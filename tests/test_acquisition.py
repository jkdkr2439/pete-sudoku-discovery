"""Synthetic finite pair worlds test acquisition, not alternative Sudoku sizes."""
import importlib.util
from itertools import combinations
from pathlib import Path
from random import Random
import tempfile
import unittest

from pete_discovery.acquisition import Acquisition
from pete_discovery.opaque_experiment import run_case, verify_journal
from pete_discovery.pairmap import PairwiseFieldmap
from pete_discovery.sandbox import Sandbox
from pete_discovery.substrate import OpaqueSudokuSubstrate


class PairBody:
    """Test-only binary oracle, supporting both equality classes independently."""

    def __init__(self, cells, conflicts):
        self.cells = cells
        self.conflicts = conflicts
        self.board = {}
        self.actions = 0
        self.resets = 0

    def sense(self):
        return {"vision": {"cells": self.cells, "alphabet": [4, 7, 8]}}

    def reset_experiment(self):
        self.board = {}
        self.resets += 1

    def act(self, cell, value, purpose):
        self.actions += 1
        accepted = cell not in self.board and not any(
            PairwiseFieldmap.key((cell, value), (other, existing)) in self.conflicts
            for other, existing in self.board.items()
        )
        if accepted:
            self.board[cell] = value
        return {"receipt": {"accepted": accepted, "changed": accepted}}


def synthetic_world(seed=0):
    cells = [f"token-{i}" for i in range(12)]
    rng = Random(seed)
    conflicts = {
        (*sorted((a, b)), equal)
        for a, b in combinations(cells, 2)
        for equal in (True, False)
        if rng.random() < 0.3
    }
    return cells, conflicts


class AcquisitionTests(unittest.TestCase):
    def test_both_policies_recover_both_symbol_classes(self):
        for seed in range(4):
            for policy in ("exhaustive", "adaptive", "cost_aware"):
                with self.subTest(seed=seed, policy=policy):
                    cells, conflicts = synthetic_world(seed)
                    body = PairBody(cells, conflicts)
                    model = PairwiseFieldmap()
                    result = Acquisition(body, model).run(policy)
                    self.assertEqual(result["status"], "COMPLETE")
                    self.assertEqual(result["placements"], body.actions)
                    self.assertEqual(result["resets"], body.resets)
                    self.assertEqual(len(model.evidence), len(cells) * (len(cells) - 1))
                    for a, b in combinations(cells, 2):
                        for values in ((8, 8), (8, 7)):
                            key = model.key((a, values[0]), (b, values[1]))
                            self.assertEqual(model.known_conflict((a, values[0]), (b, values[1])), key in conflicts)

    def test_budget_stop_does_not_invent_unobserved_relations(self):
        cells, conflicts = synthetic_world()
        for policy in ("exhaustive", "adaptive", "cost_aware"):
            for budget in (0, 2, 3, 7, 20):
                body, model = PairBody(cells, conflicts), PairwiseFieldmap()
                result = Acquisition(body, model, interaction_budget=budget).run(policy)
                self.assertEqual(result["status"], "INTERACTION_BUDGET_STOP")
                self.assertLessEqual(body.actions + body.resets, budget)
                for key, row in model.evidence.items():
                    self.assertEqual(bool(row["conflict"]), key in conflicts)

    def test_relabeling_does_not_change_acquisition(self):
        cells, conflicts = synthetic_world()
        mapping = {cell: f"opaque-{len(cells)-i}" for i, cell in enumerate(cells)}
        mapped_conflicts = {(*sorted((mapping[a], mapping[b])), equal) for a, b, equal in conflicts}
        totals = []
        for ids, edges in ((cells, conflicts), ([mapping[cell] for cell in cells], mapped_conflicts)):
            body, model = PairBody(ids, edges), PairwiseFieldmap()
            result = Acquisition(body, model).run("adaptive")
            totals.append((result["interactions"], result["queries"], len(model.evidence)))
        self.assertEqual(totals[0], totals[1])

    def test_unknown_and_conflicting_evidence_are_explicit(self):
        model = PairwiseFieldmap()
        a, b = ("x", 1), ("y", 1)
        self.assertIsNone(model.known_conflict(a, b))
        self.assertFalse(model.predicts_conflict(a, b))
        self.assertEqual(model.evidence, {})
        model.observe_pair(a, b, accepted=False)
        with self.assertRaisesRegex(ValueError, "CONTRADICTORY"):
            model.observe_pair(a, b, accepted=True)

    def test_adaptive_groups_reduce_cost_on_compatible_world(self):
        cells = [f"x{i}" for i in range(12)]
        costs = {}
        for policy in ("exhaustive", "adaptive"):
            costs[policy] = Acquisition(PairBody(cells, set()), PairwiseFieldmap()).run(policy)["interactions"]
        self.assertLess(costs["adaptive"], costs["exhaustive"])


class SandboxBudgetTests(unittest.TestCase):
    def test_completion_at_exact_budget_is_accepted(self):
        result = Sandbox(PairwiseFieldmap()).complete_opaque(
            {"cells": ["a"], "board": {"a": 0}, "alphabet": [1]}, budget=1)
        self.assertTrue(result["found"])
        self.assertEqual(result["attempts"], 1)

    def test_exhaustion_bounds_attempts_and_retains_stop_operation(self):
        result = Sandbox(PairwiseFieldmap()).complete_opaque(
            {"cells": ["a", "b"], "board": {"a": 0, "b": 0}, "alphabet": [1, 2]}, budget=1)
        self.assertFalse(result["found"])
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(result["operation"], "BUDGET_STOP")

    def test_completed_input_needs_zero_assignments(self):
        result = Sandbox(PairwiseFieldmap()).complete_opaque(
            {"cells": ["a"], "board": {"a": 1}, "alphabet": [1]}, budget=0)
        self.assertTrue(result["found"])
        self.assertEqual(result["attempts"], 0)


class OpaqueIntegrationTests(unittest.TestCase):
    def test_packet_omits_coordinates_and_authority_data(self):
        world = OpaqueSudokuSubstrate(seed=5, level=0, scramble_seed=17)
        packet = world.observe()
        self.assertEqual(set(packet), {"world_id", "cells", "alphabet", "board", "fixed", "mode", "action_index"})
        self.assertEqual(set(packet["cells"]), set(packet["board"]))
        self.assertEqual(len(packet["cells"]), 81)
        self.assertTrue(all(isinstance(cell, str) for cell in packet["cells"]))
        self.assertEqual(len(packet["alphabet"]), 9)

    def test_real_scrambled_world_and_provenance(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "case"
            receipt = run_case(root, arm="pair_adaptive", seed=5, level=0, scramble_seed=17,
                               interaction_budget=30_000, search_budget=2000)
            self.assertEqual(receipt["status"], "SOLVED", receipt)
            self.assertTrue(receipt["last_commit_receipt"]["complete"])
            self.assertEqual(receipt["prediction"]["accuracy"], 1.0)
            self.assertEqual(receipt["prediction"]["known_pair_classes"], 6480)
            self.assertEqual(receipt["journal"], verify_journal(root / "physical-journal.jsonl"))
            self.assertEqual(receipt["physical_actions"], receipt["learning"]["placements"] + receipt["commit_placements"])
            with self.assertRaises(FileExistsError):
                run_case(root, arm="pair_adaptive", seed=5, level=0, scramble_seed=17,
                         interaction_budget=30_000, search_budget=2000)
            with (root / "physical-journal.jsonl").open("a") as handle:
                handle.write('{"hash":"invalid"}\n')
            with self.assertRaises((ValueError, KeyError)):
                verify_journal(root / "physical-journal.jsonl")

    def test_audit_detects_deliberate_direct_and_indirect_authority_imports(self):
        path = Path(__file__).resolve().parents[1] / "tools" / "audit_boundaries.py"
        spec = importlib.util.spec_from_file_location("audit", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for source in ("from .substrate import SudokuSubstrate", "from . import substrate",
                       "from .opaque_experiment import run_case", "body._Body__world.place(1, 2)",
                       "world.hidden_pair_conflict(a, 1, b, 1)",
                       "from .recovery_experiment import run_branch", "from .memory_experiment import run_sequence", "world.change_roles(swaps=1, seed=2)"):
            self.assertTrue(module.audit_source(source, "mutated.py"), source)
        self.assertEqual(module.audit_source("from .pairmap import PairwiseFieldmap", "safe.py"), [])


if __name__ == "__main__":
    unittest.main()
