import tempfile
import unittest

from pete_discovery.runtime import ExperimentRuntime


class ScaleEvidenceTests(unittest.TestCase):
    def test_same_cognition_discovers_and_solves_9x9(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = ExperimentRuntime(folder, size=9, level=2, seed=5)
            theory = runtime.agent.discover(9)
            self.assertEqual(theory["unexplained_rejections"], 0)
            self.assertEqual(len(theory["clauses"]), 3)
            verification = runtime.agent.evaluate(9)
            self.assertEqual(verification["accuracy"], 1.0)
            result = runtime.agent.solve_current()
            self.assertEqual(result["status"], "SOLVED")
            self.assertLess(result["imagination"]["attempts"], 5000)


if __name__ == "__main__":
    unittest.main()
