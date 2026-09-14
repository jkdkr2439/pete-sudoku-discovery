"""Receipt-level context reuse and its explicit interaction-cost bound."""
from itertools import combinations
from pathlib import Path
from random import Random
import tempfile
import unittest

from pete_discovery.acquisition import Acquisition, InteractionBudgetExhausted
from pete_discovery.opaque_experiment import run_case
from pete_discovery.pairmap import PairwiseFieldmap
import test_acquisition as fixtures


class CostAwareTests(unittest.TestCase):
    def test_matches_exhaustive_models_across_densities_with_bounded_cost(self):
        cells = [f"v{i}" for i in range(12)]
        labels = len(cells) * (len(cells) - 1)
        for density in (0.0, 0.1, 0.5, 1.0):
            for seed in (3, 11):
                with self.subTest(density=density, seed=seed):
                    rng = Random(seed)
                    conflicts = {(*sorted((a, b)), equal)
                                 for a, b in combinations(cells, 2)
                                 for equal in (True, False) if rng.random() < density}
                    models = {}
                    costs = {}
                    for policy in ("exhaustive", "cost_aware"):
                        model = PairwiseFieldmap()
                        body = fixtures.PairBody(cells, conflicts)
                        receipt = Acquisition(body, model).run(policy)
                        self.assertEqual(receipt["status"], "COMPLETE")
                        models[policy] = model.snapshot()
                        costs[policy] = receipt["interactions"]
                        if policy == "cost_aware":
                            self.assertEqual(receipt["placements"], labels + receipt["queries"])
                            self.assertEqual(receipt["resets"], receipt["queries"])
                            self.assertEqual(receipt["interactions"], labels + 2 * receipt["queries"])
                    self.assertEqual(models["exhaustive"], models["cost_aware"])
                    self.assertLessEqual(costs["cost_aware"], costs["exhaustive"])
                    if density == 1.0:
                        self.assertEqual(costs["cost_aware"], 3 * labels)

    def test_rejected_member_does_not_force_a_reset(self):
        conflicts = {("a", "t", True), ("c", "t", True)}
        body = fixtures.PairBody(["a", "b", "c", "t"], conflicts)
        model = PairwiseFieldmap()
        learner = Acquisition(body, model, interaction_budget=5)
        learner._stream_group(["a", "b", "c"], "t", True)
        self.assertEqual(body.resets, 1)
        self.assertEqual(body.actions, 4)
        self.assertEqual(learner.interactions, 5)
        self.assertEqual(learner.rejected_queries, 1)
        for cell in ("a", "b", "c"):
            self.assertEqual(model.known_conflict((cell, 4), ("t", 4)), cell != "b")

    def test_partial_group_preserves_only_observed_labels(self):
        body = fixtures.PairBody(["a", "b", "c", "t"], set())
        model = PairwiseFieldmap()
        learner = Acquisition(body, model, interaction_budget=4)
        with self.assertRaises(InteractionBudgetExhausted):
            learner._stream_group(["a", "b", "c"], "t", False)
        self.assertEqual(learner.interactions, 4)
        self.assertIs(model.known_conflict(("a", 4), ("t", 7)), False)
        self.assertIs(model.known_conflict(("b", 4), ("t", 7)), False)
        self.assertIsNone(model.known_conflict(("c", 4), ("t", 7)))
        self.assertIsNone(model.known_conflict(("a", 4), ("t", 4)))

    def test_missing_or_mutating_rejection_receipt_is_rejected(self):
        for changed in (True, None):
            body = fixtures.PairBody(["a", "t"], set())
            original_act = body.act

            def act(cell, value, purpose):
                if purpose == "acquisition:member":
                    return {"receipt": {"accepted": False, "changed": changed}}
                return original_act(cell, value, purpose)

            body.act = act
            model = PairwiseFieldmap()
            learner = Acquisition(body, model)
            with self.assertRaisesRegex(ValueError, "REJECTED_ACTION_CHANGED_STATE"):
                learner._stream_group(["a"], "t", True)
            self.assertEqual(model.evidence, {})

    def test_anchor_failure_does_not_create_evidence(self):
        body = fixtures.PairBody(["a", "t"], set())
        body.act = lambda *args, **kwargs: {"receipt": {"accepted": False, "changed": False}}
        model = PairwiseFieldmap()
        with self.assertRaisesRegex(ValueError, "REJECTED_ANCHOR"):
            Acquisition(body, model)._stream_group(["a"], "t", True)
        self.assertEqual(model.evidence, {})

    def test_labels_are_not_interpreted(self):
        cells, conflicts = fixtures.synthetic_world()
        mapping = {cell: f"id-{101-i}" for i, cell in enumerate(cells)}
        mapped = {(*sorted((mapping[a], mapping[b])), equal) for a, b, equal in conflicts}
        results = []
        for names, edges in ((cells, conflicts), ([mapping[c] for c in cells], mapped)):
            learner = Acquisition(fixtures.PairBody(names, edges), PairwiseFieldmap())
            results.append(learner.run("cost_aware"))
        self.assertEqual(results[0], results[1])

    def test_real_scrambled_world_uses_new_policy_and_shared_solver(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = run_case(Path(folder) / "case", arm="pair_cost_aware", seed=5, level=0,
                               scramble_seed=17, interaction_budget=12000, search_budget=2000)
            self.assertEqual(receipt["status"], "SOLVED", receipt)
            self.assertEqual(receipt["learning"]["policy"], "cost_aware")
            self.assertEqual(receipt["prediction"]["known_pair_classes"], 6480)
            self.assertEqual(receipt["prediction"]["accuracy"], 1.0)
            self.assertLess(receipt["learning"]["interactions"], 19440)
            self.assertTrue(receipt["journal"]["verified"])


if __name__ == "__main__":
    unittest.main()
