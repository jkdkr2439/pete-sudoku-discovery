import inspect
import json
import unittest

import pete_discovery.cognition as cognition_module
import pete_discovery.sandbox as sandbox_module
from pete_discovery.runtime import ExperimentRuntime
from pete_discovery.substrate import SudokuSubstrate
from pete_discovery.server import code_catalog


class ArchitectureBoundaryTests(unittest.TestCase):
    def test_public_packet_hides_world_internals(self):
        world = SudokuSubstrate(seed=7)
        self.assertEqual(world.observe()["shape"], [9, 9])
        text = json.dumps(world.observe()).lower()
        for forbidden in ("solution", "candidate", "constraint", "group", "reason"):
            self.assertNotIn(forbidden, text)

    def test_cognition_and_sandbox_do_not_import_substrate(self):
        source = inspect.getsource(cognition_module) + inspect.getsource(sandbox_module)
        self.assertNotIn("import substrate", source)
        self.assertNotIn("from .substrate", source)
        self.assertNotIn("_valid(", source)
        self.assertNotIn("hidden_grade", source)

    def test_live_code_catalog_points_to_real_runtime_functions(self):
        routes = code_catalog()
        self.assertIn("sandbox", routes)
        self.assertTrue(routes["sandbox"]["file"].endswith("sandbox.py"))
        self.assertIn("def complete", routes["sandbox"]["source"])
        self.assertGreater(routes["sandbox"]["start_line"], 0)
    def test_every_other_dimension_is_rejected(self):
        for size in (1, 4, 16):
            with self.assertRaisesRegex(ValueError, "ONLY_9X9"):
                SudokuSubstrate(size=size)


class NineByNineWorldTests(unittest.TestCase):
    def test_default_runtime_is_9x9(self):
        runtime = ExperimentRuntime.__new__(ExperimentRuntime)
        self.assertEqual(9, SudokuSubstrate.SIZE)

    def test_progression_stays_9x9_and_changes_seed_at_last_tier(self):
        world = SudokuSubstrate(level=2, seed=9)
        observation = world.next_world()
        self.assertEqual(observation["shape"], [9, 9])
        self.assertEqual(observation["difficulty_index"], 2)
        self.assertEqual(world.seed, 10)


if __name__ == "__main__":
    unittest.main()
