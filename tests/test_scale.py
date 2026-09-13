import json
import tempfile
from pathlib import Path
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
            self.assertLess(result["sandbox"]["attempts"], 5000)
            operations = [step["operation"] for step in result["sandbox"]["recent_ops"]]
            self.assertIn("SCAN", operations)
            self.assertIn("TRY", operations)
            self.assertEqual(result["sandbox"]["operation"], "COMPLETE")
            self.assertTrue(result["sandbox"]["instruction"])
            trace_path = Path(folder) / "logs" / "sandbox-trace.jsonl"
            records = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(records[0]["operation"], "BEGIN")
            self.assertEqual(records[-1]["operation"], "COMPLETE")
            self.assertTrue(any(record["operation"] == "TRY" for record in records))
            self.assertEqual(runtime.snapshot()["sandbox_log"]["steps"], len(records))


if __name__ == "__main__":
    unittest.main()
