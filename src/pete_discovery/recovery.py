"""Failure-triggered, finite-watchlist repair through public observations only."""
from __future__ import annotations

from itertools import combinations
from random import Random

from .acquisition import Acquisition, InteractionBudgetExhausted
from .pairmap import RevisablePairwiseFieldmap
from .sandbox import Sandbox


class BudgetedBody:
    """Count all post-transition resets and placements, including failed commits."""

    def __init__(self, body, budget):
        if budget < 0:
            raise ValueError("NEGATIVE_INTERACTION_BUDGET")
        self.body = body
        self.budget = budget
        self.resets = 0
        self.placements = 0

    @property
    def interactions(self):
        return self.resets + self.placements

    @property
    def remaining(self):
        return self.budget - self.interactions

    def _spend(self, kind):
        if self.remaining <= 0:
            raise InteractionBudgetExhausted
        if kind == "reset":
            self.resets += 1
        else:
            self.placements += 1

    def sense(self):
        return self.body.sense()

    def reset_experiment(self):
        self._spend("reset")
        return self.body.reset_experiment()

    def reset_challenge(self):
        self._spend("reset")
        packet = self.body.reset_challenge()
        journal = getattr(self.body, "journal", None)
        if journal is not None:
            journal.append("body.reset_challenge", packet["vision"])
        return packet

    def act(self, position, value, purpose="commit"):
        self._spend("placement")
        return self.body.act(position, value, purpose=purpose)

    def snapshot(self):
        return {"budget": self.budget, "interactions": self.interactions,
                "resets": self.resets, "placements": self.placements}


def attempt_completion(body, model, search_budget, observe=None):
    report = {"status": "BUDGET_STOP", "commit_placements": 0}
    try:
        public = body.reset_challenge()["vision"]
        result = Sandbox(model).complete_opaque(public, budget=search_budget, observe=observe)
        report["search"] = {"found": result["found"], "attempts": result["attempts"],
                            "operation": result["operation"]}
        if not result["found"]:
            report["status"] = "SEARCH_BUDGET_STOP" if result["operation"] == "BUDGET_STOP" else "NO_COMPLETION"
            return report
        current = dict(public["board"])
        report["status"] = "INCOMPLETE"
        for cell in public["cells"]:
            if public["fixed"][cell]:
                continue
            value = result["board"][cell]
            response = body.act(cell, value, purpose="recovery:commit")
            report["commit_placements"] += 1
            report["last_receipt"] = response["receipt"]
            if not response["receipt"]["accepted"]:
                report["status"] = "COUNTEREXAMPLE"
                report["counterexample"] = {
                    "assignment": [cell, value],
                    "context": [[other, existing] for other, existing in current.items() if existing],
                }
                return report
            current[cell] = value
            if response["receipt"]["complete"]:
                report["status"] = "SOLVED"
        return report
    except InteractionBudgetExhausted:
        report["status"] = "BUDGET_STOP"
        return report


class RecoveryController:
    def __init__(self, body, model, *, interaction_budget, search_budget=2000,
                 compatible_checks=128, watch_seed=0, observer=None):
        self.body = BudgetedBody(body, interaction_budget)
        self.model = model
        self.public = body.sense()["vision"]
        self.search_budget = search_budget
        self.compatible_checks = compatible_checks
        self.watch_seed = watch_seed
        self.observer = observer
        self.verified = set()
        self.triggers = 0
        self.probes = 0
        self.watchlist_size = 0
        self.commit_reserve = 1 + sum(not fixed for fixed in self.public["fixed"].values())

    def _probe(self, key):
        if key in self.verified:
            return False
        if self.body.remaining < self.commit_reserve + 3:
            raise InteractionBudgetExhausted
        a, b, equal = key
        first, other = self.public["alphabet"][:2]
        self.body.reset_experiment()
        anchor = self.body.act(a, first, purpose="repair:anchor")
        if not anchor["receipt"]["accepted"]:
            raise ValueError("EMPTY_CONTEXT_REJECTED_ANCHOR")
        result = self.body.act(b, first if equal else other, purpose="repair:probe")
        accepted = result["receipt"]["accepted"]
        if not accepted and result["receipt"].get("changed") is not False:
            raise ValueError("REJECTED_ACTION_CHANGED_STATE")
        changed = self.model.revise_pair((a, first), (b, first if equal else other), accepted)
        self.probes += 1
        self.verified.add(key)
        return changed

    def _watchlist(self, initial):
        keys = []
        counterexample = initial.get("counterexample")
        if counterexample:
            target = tuple(counterexample["assignment"])
            keys.extend(self.model.key(target, tuple(context)) for context in counterexample["context"])
        givens = [(cell, value) for cell, value in self.public["board"].items() if value]
        keys.extend(self.model.key(a, b) for a, b in combinations(givens, 2)
                    if self.model.predicts_conflict(a, b))
        conflicting, compatible = [], []
        for key, evidence in sorted(self.model.evidence.items()):
            (conflicting if evidence["conflict"] else compatible).append(key)
        rng = Random(self.watch_seed)
        rng.shuffle(conflicting)
        keys.extend(conflicting)
        keys.extend(rng.sample(compatible, min(self.compatible_checks, len(compatible))))
        return list(dict.fromkeys(keys))

    def repair(self, initial):
        watchlist = self._watchlist(initial)
        self.watchlist_size = len(watchlist)
        try:
            for key in watchlist:
                if self._probe(key):
                    self.triggers += 1
                    # Only outer watchlist contradictions trigger an endpoint scan.
                    # Scanning every changed neighbor recursively would erase locality.
                    for endpoint in key[:2]:
                        for other in self.public["cells"]:
                            if other != endpoint:
                                for equal in (True, False):
                                    pair = (*sorted((endpoint, other)), equal)
                                    self._probe(pair)
            return "WATCHLIST_COMPLETE"
        except InteractionBudgetExhausted:
            return "REPAIR_BUDGET_STOP"

    def run(self, policy):
        if policy not in ("frozen", "relearn", "repair"):
            raise ValueError("UNKNOWN_RECOVERY_POLICY")
        initial = attempt_completion(self.body, self.model, self.search_budget, self.observer)
        report = {"policy": policy, "initial_attempt": initial,
                  "status": initial["status"], "repair_status": "NOT_TRIGGERED"}
        if initial["status"] not in ("SOLVED", "BUDGET_STOP") and policy != "frozen":
            if policy == "relearn":
                self.model = RevisablePairwiseFieldmap()
                learner = Acquisition(self.body, self.model,
                                      interaction_budget=max(0, self.body.remaining - self.commit_reserve))
                report["learning"] = learner.run("cost_aware")
                report["repair_status"] = report["learning"]["status"]
            else:
                report["repair_status"] = self.repair(initial)
            final = attempt_completion(self.body, self.model, self.search_budget, self.observer)
            report["final_attempt"] = final
            report["status"] = final["status"]
        report["cost"] = self.body.snapshot()
        report["repair"] = {"probes": self.probes, "triggers": self.triggers,
                            "revalidated_pair_classes": len(self.verified),
                            "unverified_retained_pair_classes": len(self.model.evidence) - len(self.verified)
                            if policy == "repair" else None,
                            "watchlist_size": self.watchlist_size,
                            "revisions": len(self.model.revisions)}
        return report
