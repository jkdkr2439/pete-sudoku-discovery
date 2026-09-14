"""Finite acquisition policies using only public body feedback and pair evidence."""
from __future__ import annotations

from itertools import combinations


class InteractionBudgetExhausted(Exception):
    pass


class Acquisition:
    def __init__(self, body, model, *, interaction_budget=24_000):
        if interaction_budget < 0:
            raise ValueError("NEGATIVE_INTERACTION_BUDGET")
        self.body = body
        self.model = model
        observation = body.sense()["vision"]
        self.cells = list(observation["cells"])
        self.alphabet = list(observation["alphabet"])
        if len(self.alphabet) < 2:
            raise ValueError("TWO_SYMBOL_CLASSES_REQUIRE_TWO_SYMBOLS")
        self.budget = interaction_budget
        self.queries = 0
        self.placements = 0
        self.resets = 0
        self.rejected_queries = 0

    @property
    def interactions(self):
        return self.placements + self.resets

    def _query(self, group, target, equal):
        # Reserve the entire query, so budget stops never yield partial inference.
        if self.interactions + len(group) + 2 > self.budget:
            raise InteractionBudgetExhausted
        first, other = self.alphabet[:2]
        self.body.reset_experiment()
        self.resets += 1
        self.queries += 1
        for cell in group:
            response = self.body.act(cell, first, purpose="acquisition:context")
            self.placements += 1
            if not response["receipt"]["accepted"]:
                raise ValueError("CONTEXT_REJECTED_PAIRWISE_ASSUMPTION_FAILED")
        response = self.body.act(target, first if equal else other, purpose="acquisition:target")
        self.placements += 1
        accepted = response["receipt"]["accepted"]
        self.rejected_queries += not accepted
        return accepted

    def _record(self, left, right, equal, accepted):
        first, other = self.alphabet[:2]
        self.model.observe_pair((left, first), (right, first if equal else other), accepted)

    def exhaustive(self):
        for left, right in combinations(self.cells, 2):
            for equal in (True, False):
                accepted = self._query([left], right, equal)
                self._record(left, right, equal, accepted)

    def _learn_group(self, group, target, equal):
        if not group:
            return
        accepted = self._query(group, target, equal)
        if accepted or len(group) == 1:
            for cell in group:
                self._record(cell, target, equal, accepted)
        else:
            midpoint = len(group) // 2
            self._learn_group(group[:midpoint], target, equal)
            self._learn_group(group[midpoint:], target, equal)

    def adaptive(self):
        # Groups are constructed from learned compatibility, never from geometry.
        groups = []
        first = self.alphabet[0]
        for target in self.cells:
            for group in groups:
                for equal in (True, False):
                    self._learn_group(group, target, equal)
            destination = next((group for group in groups if all(
                self.model.known_conflict((cell, first), (target, first)) is False
                for cell in group
            )), None)
            if destination is None:
                groups.append([target])
            else:
                destination.append(target)

    def _stream_group(self, group, target, equal):
        """Amortize reset/anchor cost; every member action identifies one pair.

        Members must be mutually compatible with the common context symbol.
        Failed actions must leave state unchanged, so later tests remain valid.
        """
        if not group:
            return
        # At least one pair label must fit before spending context overhead.
        if self.interactions + 3 > self.budget:
            raise InteractionBudgetExhausted
        first, other = self.alphabet[:2]
        self.body.reset_experiment()
        self.resets += 1
        self.queries += 1
        response = self.body.act(target, first if equal else other, purpose="acquisition:anchor")
        self.placements += 1
        if not response["receipt"]["accepted"]:
            raise ValueError("EMPTY_CONTEXT_REJECTED_ANCHOR")
        any_rejected = False
        for cell in group:
            if self.interactions >= self.budget:
                raise InteractionBudgetExhausted
            response = self.body.act(cell, first, purpose="acquisition:member")
            self.placements += 1
            accepted = response["receipt"]["accepted"]
            if not accepted and response["receipt"].get("changed") is not False:
                raise ValueError("REJECTED_ACTION_CHANGED_STATE")
            if not accepted and not any_rejected:
                self.rejected_queries += 1
                any_rejected = True
            self._record(cell, target, equal, accepted)

    def cost_aware(self):
        groups = []
        first = self.alphabet[0]
        for target in self.cells:
            # Stable order breaks ties; IDs are never interpreted as geometry.
            for group in sorted(groups, key=len, reverse=True):
                for equal in (True, False):
                    self._stream_group(group, target, equal)
            destination = next((group for group in groups if all(
                self.model.known_conflict((cell, first), (target, first)) is False
                for cell in group
            )), None)
            if destination is None:
                groups.append([target])
            else:
                destination.append(target)

    def run(self, policy):
        if policy not in ("exhaustive", "adaptive", "cost_aware"):
            raise ValueError("UNKNOWN_ACQUISITION_POLICY")
        status = "COMPLETE"
        try:
            getattr(self, policy)()
        except InteractionBudgetExhausted:
            status = "INTERACTION_BUDGET_STOP"
        self.model.finalize()
        return {
            "status": status,
            "policy": policy,
            "queries": self.queries,
            "resets": self.resets,
            "placements": self.placements,
            "interactions": self.interactions,
            "interaction_budget": self.budget,
            "rejected_queries": self.rejected_queries,
        }
