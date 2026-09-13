import tempfile
import unittest

from pete_discovery.runtime import ExperimentRuntime


class ContinuousSchedulerTests(unittest.TestCase):
    def test_one_start_advances_repeatedly_until_pause_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = ExperimentRuntime(folder)
            advances = []

            def execute():
                runtime.worlds_completed += 1
                if runtime.worlds_completed == 3:
                    runtime.stop_requested = True
                return {"result": "SOLVED"}

            def advance(clear_events=False):
                advances.append(runtime.worlds_completed)
                return {"world_id": f"test-{len(advances)}"}

            runtime._execute_current = execute
            runtime._advance_world = advance
            self.assertTrue(runtime.run_continuous())
            self.assertEqual(runtime.worlds_completed, 3)
            self.assertEqual(advances, [1, 2])
            self.assertFalse(runtime.running)
            self.assertFalse(runtime.continuous)

    def test_pause_is_rejected_when_scheduler_is_not_running(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = ExperimentRuntime(folder)
            self.assertFalse(runtime.request_pause())


if __name__ == "__main__":
    unittest.main()
