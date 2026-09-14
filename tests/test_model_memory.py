"""Memory utility, immutable snapshots, failure fallback and verification limits."""
from copy import deepcopy
import unittest

from pete_discovery.model_memory import ModelArchive, MemoryController, fresh_completion
from pete_discovery.substrate import OpaqueSudokuSubstrate
from test_recovery import PairChallengeBody, learned_model


class MemoryTests(unittest.TestCase):
    cells = ["a", "b", "c"]
    old = {("a", "b", True)}
    new = {("a", "c", True)}

    def archive(self, *models):
        archive = ModelArchive()
        for model in models:
            archive.remember(model, self.cells, source={"method": "test_observations"})
        return archive

    def test_archive_deduplicates_predictions_and_isolates_mutations(self):
        model = learned_model(self.cells, self.old)
        archive = self.archive(model)
        before = deepcopy(archive.snapshot())
        model.revise_pair(("a", 1), ("b", 1), True)
        self.assertEqual(archive.snapshot(), before)
        candidate = next(iter(archive.candidates().values()))
        candidate.revise_pair(("a", 1), ("b", 1), True)
        self.assertEqual(archive.snapshot(), before)
        original = learned_model(self.cells, self.old)
        original.observe_pair(("a", 1), ("b", 1), False)
        archive.remember(original, self.cells, source={"method": "reobserved"})
        self.assertEqual(len(archive.candidates()), 1)
        self.assertGreater(archive.storage_bytes(), 0)

    def test_incomplete_model_cannot_enter_retrieval(self):
        model = learned_model(self.cells, self.old)
        model.evidence.pop(next(iter(model.evidence)))
        self.assertIsNone(ModelArchive().remember(model, self.cells, source={}))

    def test_recurrence_selects_old_model_from_observed_disagreement(self):
        old = learned_model(self.cells, self.old)
        current = learned_model(self.cells, self.new)
        archive = self.archive(old, current)
        old_id = next(iter(archive.candidates()))
        body = PairChallengeBody(self.cells, self.old)
        controller = MemoryController(body, current, archive, interaction_budget=100,
                                      verification_checks=128)
        result = controller.run()
        self.assertEqual(result["status"], "SOLVED")
        self.assertEqual(result["retrieval"]["selected_id"], old_id)
        self.assertEqual(result["retrieval"]["discrimination_probes"], 1)
        self.assertEqual(result["recovery"]["repair_status"], "NOT_TRIGGERED")
        self.assertEqual(result["cost"]["interactions"], body.actions + body.resets)
        self.assertEqual(len(archive.candidates()), 2)

    def test_unfamiliar_world_rejects_archive_and_repairs(self):
        current = learned_model(self.cells, self.old)
        controller = MemoryController(PairChallengeBody(self.cells, self.new), current,
                                      self.archive(current), interaction_budget=100)
        result = controller.run()
        self.assertIsNone(result["retrieval"]["selected_id"])
        self.assertEqual(result["retrieval"]["status"], "NO_MATCH")
        self.assertEqual(result["status"], "SOLVED")
        self.assertTrue(controller.model.predicts_conflict(("a", 1), ("c", 1)))

    def test_wrong_reuse_can_fail_execution_then_repair(self):
        current = learned_model(self.cells, self.old)
        controller = MemoryController(PairChallengeBody(self.cells, self.new), current,
                                      self.archive(current), interaction_budget=100, verification_checks=0)
        result = controller.run()
        self.assertIsNotNone(result["retrieval"]["selected_id"])
        self.assertEqual(result["recovery"]["initial_attempt"]["status"], "COUNTEREXAMPLE")
        self.assertEqual(result["status"], "SOLVED")
        self.assertGreater(result["recovery"]["repair"]["probes"], 0)

    def test_finite_verification_and_success_do_not_certify_memory(self):
        # Unchecked unequal-symbol change leaves an all-equal completion valid.
        current = learned_model(self.cells, set())
        controller = MemoryController(PairChallengeBody(self.cells, {("a", "b", False)}), current,
                                      self.archive(current), interaction_budget=100, verification_checks=0)
        result = controller.run()
        self.assertEqual(result["status"], "SOLVED")
        self.assertEqual(result["retrieval"]["status"], "TENTATIVE_MATCH")
        self.assertFalse(controller.model.predicts_conflict(("a", 1), ("b", 2)))
        self.assertEqual(controller.archive.snapshot()["entries"][0]["validity"],
                         "UNCERTIFIED_COMPLETE_COVERAGE")

    def test_all_stages_share_budget_and_exhaustion_is_not_match(self):
        for budget in (0, 2, 4, 6, 10, 20, 100):
            model = learned_model(self.cells, self.old)
            body = PairChallengeBody(self.cells, self.new)
            controller = MemoryController(body, model, self.archive(model), interaction_budget=budget)
            result = controller.run()
            self.assertLessEqual(result["cost"]["interactions"], budget)
            self.assertEqual(result["cost"]["interactions"], body.actions + body.resets)
            if result["retrieval"]["status"] == "RETRIEVAL_BUDGET_STOP":
                self.assertIsNone(result["retrieval"]["selected_id"])

    def test_fresh_relearns_even_when_task_repeats(self):
        for budget in (0, 2, 10, 100):
            body = PairChallengeBody(self.cells, self.old)
            _, result = fresh_completion(body, interaction_budget=budget)
            self.assertEqual(result["cost"]["interactions"], body.actions + body.resets)
            self.assertLessEqual(result["cost"]["interactions"], budget)
            if budget == 100:
                self.assertEqual(result["status"], "SOLVED")
                self.assertEqual(result["learning"]["status"], "COMPLETE")

    def test_world_metadata_does_not_select_memory(self):
        class MisleadingBody(PairChallengeBody):
            def sense(self):
                public = super().sense()
                public["vision"]["world_id"] = "wrong-archive-label"
                public["vision"]["action_index"] = 987654
                return public
        reports = []
        for cls in (PairChallengeBody, MisleadingBody):
            model = learned_model(self.cells, self.new)
            controller = MemoryController(cls(self.cells, self.old), model,
                                          self.archive(learned_model(self.cells, self.old), model),
                                          interaction_budget=100)
            report = controller.run()["retrieval"]
            report.pop("seconds")
            report.pop("cpu_seconds")
            reports.append(report)
        self.assertEqual(*reports)

    def test_same_hidden_swap_restores_network_and_public_challenge(self):
        world = OpaqueSudokuSubstrate(seed=7, scramble_seed=79)
        before = world.observe()
        world.change_roles(swaps=3, seed=113)
        self.assertNotEqual(before["board"], world.observe()["board"])
        world.change_roles(swaps=3, seed=113)
        self.assertEqual(before, world.observe())


if __name__ == "__main__":
    unittest.main()
