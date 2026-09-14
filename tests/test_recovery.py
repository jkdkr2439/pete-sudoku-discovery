"""Belief revision, failure feedback, and explicit change-detection limits."""
from itertools import combinations
import unittest

from pete_discovery.pairmap import PairwiseFieldmap, RevisablePairwiseFieldmap
from pete_discovery.recovery import RecoveryController
from pete_discovery.substrate import OpaqueSudokuSubstrate


class PairChallengeBody:
    """Synthetic test-only body; rule changes are never passed to the controller."""

    def __init__(self, cells, conflicts):
        self.cells = cells
        self.conflicts = conflicts
        self.board = {}
        self.mode = "challenge"
        self.actions = 0
        self.resets = 0

    def sense(self):
        return {"vision": {"cells": list(self.cells), "alphabet": [1, 2, 3],
                           "board": {cell: self.board.get(cell, 0) for cell in self.cells},
                           "fixed": {cell: False for cell in self.cells}, "mode": self.mode}}

    def reset_experiment(self):
        self.board = {}
        self.mode = "experiment"
        self.resets += 1
        return self.sense()["vision"]

    def reset_challenge(self):
        self.board = {}
        self.mode = "challenge"
        self.resets += 1
        return self.sense()

    def act(self, cell, value, purpose):
        self.actions += 1
        accepted = cell not in self.board and not any(
            PairwiseFieldmap.key((cell, value), (other, old)) in self.conflicts
            for other, old in self.board.items())
        if accepted:
            self.board[cell] = value
        return {"receipt": {"accepted": accepted, "changed": accepted,
                            "complete": self.mode == "challenge" and len(self.board) == len(self.cells)}}


def learned_model(cells, conflicts):
    model = RevisablePairwiseFieldmap()
    for a, b in combinations(cells, 2):
        for equal in (True, False):
            key = (*sorted((a, b)), equal)
            model.observe_pair((a, 1), (b, 1 if equal else 2), key not in conflicts)
    return model


class RevisionTests(unittest.TestCase):
    def test_both_revision_directions_preserve_old_evidence(self):
        model = RevisablePairwiseFieldmap()
        a, b = ("a", 1), ("b", 1)
        model.observe_pair(a, b, True)
        self.assertTrue(model.revise_pair(a, b, False))
        self.assertTrue(model.predicts_conflict(a, b))
        self.assertTrue(model.revise_pair(a, b, True))
        self.assertFalse(model.predicts_conflict(a, b))
        self.assertEqual(len(model.revisions), 2)
        self.assertEqual(model.revisions[0]["previous_evidence"], {"compatible": 1, "conflict": 0})
        self.assertEqual(model.revisions[1]["previous_evidence"], {"compatible": 0, "conflict": 1})
        self.assertFalse(model.revise_pair(a, b, True))
        self.assertEqual(len(model.revisions), 2)

    def test_stationary_model_still_rejects_contradictions(self):
        model = PairwiseFieldmap()
        model.observe_pair(("a", 1), ("b", 1), True)
        with self.assertRaisesRegex(ValueError, "CONTRADICTORY"):
            model.observe_pair(("a", 1), ("b", 1), False)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.cells = ["a", "b", "c"]
        self.old = {("a", "b", True)}
        self.new = {("a", "c", True)}

    def test_commit_rejection_drives_both_added_and_removed_edge_repairs(self):
        body = PairChallengeBody(self.cells, self.new)
        controller = RecoveryController(body, learned_model(self.cells, self.old), interaction_budget=100)
        result = controller.run("repair")
        self.assertEqual(result["initial_attempt"]["status"], "COUNTEREXAMPLE")
        self.assertEqual(result["initial_attempt"]["counterexample"]["assignment"], ["c", 1])
        self.assertEqual(result["status"], "SOLVED")
        self.assertEqual(result["repair_status"], "WATCHLIST_COMPLETE")
        self.assertEqual(result["repair"]["revisions"], 2)
        self.assertEqual(result["repair"]["revalidated_pair_classes"], 6)
        self.assertEqual(result["cost"]["interactions"], body.actions + body.resets)
        first_revision = controller.model.revisions[0]
        self.assertEqual((first_revision["left"], first_revision["right"]), ("a", "c"))
        for a, b in combinations(self.cells, 2):
            for equal in (True, False):
                self.assertEqual(controller.model.predicts_conflict((a, 1), (b, 1 if equal else 2)),
                                 (a, b, equal) in self.new)

    def test_frozen_and_relearn_controls(self):
        for policy, status in (("frozen", "COUNTEREXAMPLE"), ("relearn", "SOLVED")):
            controller = RecoveryController(PairChallengeBody(self.cells, self.new),
                                            learned_model(self.cells, self.old), interaction_budget=100)
            result = controller.run(policy)
            self.assertEqual(result["status"], status)
            if policy == "relearn":
                self.assertEqual(result["learning"]["policy"], "cost_aware")
                self.assertEqual(controller.model.revisions, [])

    def test_unchanged_world_does_not_trigger_work(self):
        for policy in ("frozen", "relearn", "repair"):
            controller = RecoveryController(PairChallengeBody(self.cells, self.old),
                                            learned_model(self.cells, self.old), interaction_budget=100)
            result = controller.run(policy)
            self.assertEqual(result["status"], "SOLVED")
            self.assertEqual(result["repair_status"], "NOT_TRIGGERED")
            self.assertEqual(result["repair"]["probes"], 0)
            self.assertEqual(result["cost"]["interactions"], 4)

    def test_all_physical_work_is_budgeted(self):
        for budget in (0, 2, 4, 6, 10, 20):
            for policy in ("frozen", "relearn", "repair"):
                body = PairChallengeBody(self.cells, self.new)
                controller = RecoveryController(body, learned_model(self.cells, self.old), interaction_budget=budget)
                result = controller.run(policy)
                self.assertLessEqual(result["cost"]["interactions"], budget)
                self.assertEqual(result["cost"]["interactions"], body.actions + body.resets)

    def test_successful_solution_can_miss_an_unexercised_changed_rule(self):
        # The new unequal-symbol prohibition does not affect the all-equal solution.
        body = PairChallengeBody(["a", "b"], {("a", "b", False)})
        model = learned_model(["a", "b"], set())
        result = RecoveryController(body, model, interaction_budget=100).run("repair")
        self.assertEqual(result["status"], "SOLVED")
        self.assertEqual(result["repair"]["probes"], 0)
        self.assertFalse(model.predicts_conflict(("a", 1), ("b", 2)))
        self.assertIn(("a", "b", False), body.conflicts)

    def test_watchlist_completion_is_not_global_model_certification(self):
        body = PairChallengeBody(["a", "b"], {("a", "b", True)})
        controller = RecoveryController(body, learned_model(["a", "b"], set()),
                                        interaction_budget=100, compatible_checks=0)
        self.assertEqual(controller.repair({"status": "NO_COMPLETION"}), "WATCHLIST_COMPLETE")
        self.assertEqual(controller.probes, 0)
        self.assertFalse(controller.model.predicts_conflict(("a", 1), ("b", 1)))

    def test_prior_incompatible_givens_supply_probe_candidates(self):
        model = learned_model(self.cells, self.old)
        controller = RecoveryController(PairChallengeBody(self.cells, self.new), model, interaction_budget=100)
        controller.public["board"] = {"a": 1, "b": 1, "c": 0}
        self.assertEqual(controller._watchlist({"status": "NO_COMPLETION"})[0], ("a", "b", True))


class TransitionBoundaryTests(unittest.TestCase):
    def test_role_swap_changes_relations_without_exposing_change_metadata(self):
        world = OpaqueSudokuSubstrate(seed=5, level=0, scramble_seed=17)
        before = world.observe()
        pairs = list(combinations(before["cells"], 2))
        old = [world.hidden_pair_conflict(a, 1, b, 1) for a, b in pairs]
        world.change_roles(swaps=1, seed=101)
        after = world.observe()
        new = [world.hidden_pair_conflict(a, 1, b, 1) for a, b in pairs]
        self.assertEqual(set(before), set(after))
        self.assertEqual(before["cells"], after["cells"])
        self.assertEqual(before["world_id"], after["world_id"])
        self.assertEqual(before["action_index"], after["action_index"])
        self.assertNotEqual(old, new)
        self.assertEqual(sum(old), sum(new))


if __name__ == "__main__":
    unittest.main()
