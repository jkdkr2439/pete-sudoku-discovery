import inspect
import json
import tempfile
import unittest

import pete_discovery.cognition as cognition_module
import pete_discovery.imagination as imagination_module
from pete_discovery.runtime import ExperimentRuntime
from pete_discovery.substrate import SudokuSubstrate


class ArchitectureBoundaryTests(unittest.TestCase):
    def test_public_packet_hides_world_internals(self):
        world = SudokuSubstrate(size=4, level=0, seed=7)
        text = json.dumps(world.observe()).lower()
        for forbidden in ("solution", "candidate", "constraint", "group", "reason"):
            self.assertNotIn(forbidden, text)

    def test_cognition_and_imagination_do_not_import_substrate(self):
        source = inspect.getsource(cognition_module) + inspect.getsource(imagination_module)
        self.assertNotIn("import substrate", source)
        self.assertNotIn("from .substrate", source)
        self.assertNotIn("_valid(", source)
        self.assertNotIn("hidden_grade", source)


class DiscoveryTests(unittest.TestCase):
    def test_empty_field_becomes_predictive_and_solves_4x4(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = ExperimentRuntime(folder, size=4, level=1, seed=3)
            self.assertEqual(runtime.fieldmap.snapshot()["clauses"], [])
            theory = runtime.agent.discover(4)
            self.assertEqual(theory["unexplained_rejections"], 0)
            self.assertGreaterEqual(len(theory["clauses"]), 3)
            report = runtime.agent.evaluate(4)
            self.assertGreater(report["accuracy"], report["empty_model_baseline"])
            self.assertEqual(report["accuracy"], 1.0)
            result = runtime.agent.solve_current()
            self.assertEqual(result["status"], "SOLVED")
            board = tuple(tuple(row) for row in result["observation"]["board"])
            self.assertTrue(runtime.world.hidden_grade(board))
            self.assertGreater(runtime.journal.sequence, 0)

    def test_progression_reaches_9x9(self):
        world = SudokuSubstrate(size=4, level=2, seed=9)
        observation = world.next_world()
        self.assertEqual(observation["shape"], [9, 9])
        self.assertEqual(observation["difficulty_index"], 0)


if __name__ == "__main__":
    unittest.main()
