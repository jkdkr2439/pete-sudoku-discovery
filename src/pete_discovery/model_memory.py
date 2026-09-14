"""Online rule-model archive and bounded retrieval, without environment labels."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import combinations
import json
from random import Random
from time import perf_counter, process_time

from .acquisition import Acquisition, InteractionBudgetExhausted
from .pairmap import RevisablePairwiseFieldmap
from .recovery import BudgetedBody, RecoveryController, attempt_completion


class ModelArchive:
    """Independent snapshots; complete coverage is eligibility, not certification."""

    def __init__(self):
        self._entries = {}

    def remember(self, model, cells, *, source):
        expected = {(*sorted((a, b)), equal) for a, b in combinations(cells, 2)
                    for equal in (True, False)}
        if set(model.evidence) != expected:
            return None
        labels = [[*key, bool(counts["conflict"])] for key, counts in sorted(model.evidence.items())]
        identity = sha256(json.dumps(labels, separators=(",", ":")).encode()).hexdigest()
        if identity not in self._entries:
            self._entries[identity] = {"model": deepcopy(model), "source": deepcopy(source),
                                       "validity": "UNCERTIFIED_COMPLETE_COVERAGE"}
        return identity

    def candidates(self):
        return {key: deepcopy(entry["model"]) for key, entry in self._entries.items()}

    def snapshot(self):
        return {"schema": "pete.model-archive.v1", "entries": [
            {"id": key, "source": deepcopy(entry["source"]), "validity": entry["validity"],
             "model": entry["model"].snapshot()} for key, entry in self._entries.items()]}

    def storage_bytes(self):
        return len(json.dumps(self.snapshot(), sort_keys=True, separators=(",", ":")).encode())


class MemoryController:
    def __init__(self, body, model, archive, *, interaction_budget, search_budget=2000,
                 discrimination_limit=32, verification_checks=128, retrieval_seed=0,
                 compatible_checks=128, observer=None):
        if min(discrimination_limit, verification_checks, compatible_checks) < 0:
            raise ValueError("NEGATIVE_PROBE_COUNT")
        self.body = BudgetedBody(body, interaction_budget)
        self.model = model
        self.archive = archive
        self.public = body.sense()["vision"]
        self.search_budget = search_budget
        self.discrimination_limit = discrimination_limit
        self.verification_checks = verification_checks
        self.retrieval_seed = retrieval_seed
        self.compatible_checks = compatible_checks
        self.observer = observer
        self.selected_model = None  # Evaluator may inspect only after run returns.
        self.observations = {}
        self.reserve = 1 + sum(not fixed for fixed in self.public["fixed"].values())

    def _probe(self, key):
        if key in self.observations:
            return self.observations[key]
        if self.body.remaining < self.reserve + 3:
            raise InteractionBudgetExhausted
        a, b, equal = key
        first, second = self.public["alphabet"][:2]
        self.body.reset_experiment()
        anchor = self.body.act(a, first, purpose="memory:anchor")
        if not anchor["receipt"]["accepted"]:
            raise ValueError("EMPTY_CONTEXT_REJECTED_ANCHOR")
        result = self.body.act(b, first if equal else second, purpose="memory:probe")
        if not result["receipt"]["accepted"] and result["receipt"].get("changed") is not False:
            raise ValueError("REJECTED_ACTION_CHANGED_STATE")
        self.observations[key] = not result["receipt"]["accepted"]
        return self.observations[key]

    def retrieve(self):
        candidates = self.archive.candidates()
        initial_count = len(candidates)
        expected = {(*sorted((a, b)), equal) for a, b in combinations(self.public["cells"], 2)
                    for equal in (True, False)}
        candidates = {key: model for key, model in candidates.items() if set(model.evidence) == expected}
        universe_rejections = initial_count - len(candidates)
        givens = [(cell, value) for cell, value in self.public["board"].items() if value]
        candidates = {key: model for key, model in candidates.items()
                      if not any(model.predicts_conflict(a, b) for a, b in combinations(givens, 2))}
        given_rejections = initial_count - universe_rejections - len(candidates)
        discrimination = verification = 0
        status = "NO_MATCH"
        selected = None
        try:
            while len(candidates) > 1 and discrimination < self.discrimination_limit:
                models = list(candidates.values())
                # All entries cover the same public universe. Most balanced split first.
                splits = []
                for key in sorted(models[0].evidence):
                    votes = sum(bool(model.evidence[key]["conflict"]) for model in models)
                    if 0 < votes < len(models):
                        splits.append((abs(2 * votes - len(models)), key))
                if not splits:
                    break
                key = min(splits)[1]
                actual = self._probe(key)
                discrimination += 1
                candidates = {identity: model for identity, model in candidates.items()
                              if bool(model.evidence[key]["conflict"]) == actual}
            if len(candidates) == 1:
                identity, candidate = next(iter(candidates.items()))
                remaining = sorted(set(candidate.evidence) - set(self.observations))
                keys = Random(self.retrieval_seed).sample(remaining, min(self.verification_checks, len(remaining)))
                for key in keys:
                    actual = self._probe(key)
                    verification += 1
                    if bool(candidate.evidence[key]["conflict"]) != actual:
                        candidates = {}
                        break
                if candidates:
                    selected = identity
                    self.model = candidate
                    self.selected_model = deepcopy(candidate)
                    status = "TENTATIVE_MATCH"
            elif candidates:
                status = "AMBIGUOUS"
        except InteractionBudgetExhausted:
            status = "RETRIEVAL_BUDGET_STOP"
        # Preserve every direct observation even when no archive entry survives.
        first, second = self.public["alphabet"][:2]
        for (a, b, equal), conflict in self.observations.items():
            self.model.revise_pair((a, first), (b, first if equal else second), not conflict)
        return {"status": status, "selected_id": selected, "initial_candidates": initial_count,
                "given_rejections": given_rejections, "universe_rejections": universe_rejections, "remaining_candidates": len(candidates),
                "discrimination_probes": discrimination, "verification_probes": verification,
                "probes": len(self.observations)}

    def run(self):
        tick = perf_counter()
        cpu_tick = process_time()
        retrieval = self.retrieve()
        retrieval["seconds"] = perf_counter() - tick
        retrieval["cpu_seconds"] = process_time() - cpu_tick
        retrieval["interactions"] = self.body.interactions
        recovery = RecoveryController(self.body, self.model, interaction_budget=self.body.remaining,
                                      search_budget=self.search_budget, compatible_checks=self.compatible_checks,
                                      observer=self.observer)
        result = recovery.run("repair")
        self.model = recovery.model
        archived = None
        if result["status"] == "SOLVED":
            archived = self.archive.remember(self.model, self.public["cells"],
                                             source={"method": "retrieval_then_repair", "task_status": "SOLVED"})
        return {"policy": "memory", "status": result["status"], "retrieval": retrieval,
                "recovery": result, "cost": self.body.snapshot(), "archived_id": archived,
                "archive_entries": len(self.archive.candidates()), "archive_bytes": self.archive.storage_bytes()}


def fresh_completion(body, *, interaction_budget, search_budget=2000, observer=None):
    """Fresh acquisition on every task, including recurring tasks."""
    metered = BudgetedBody(body, interaction_budget)
    public = metered.sense()["vision"]
    reserve = 1 + sum(not fixed for fixed in public["fixed"].values())
    model = RevisablePairwiseFieldmap()
    learning = Acquisition(metered, model, interaction_budget=max(0, metered.remaining - reserve)).run("cost_aware")
    completion = attempt_completion(metered, model, search_budget, observer)
    return model, {"policy": "fresh", "status": completion["status"], "learning": learning,
                   "completion": completion, "cost": metered.snapshot()}
