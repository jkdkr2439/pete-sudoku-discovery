from __future__ import annotations

from itertools import combinations

from .sandbox import Sandbox


class DiscoveryAgent:
    """Generic experiment -> relation induction -> counterfactual -> action loop."""

    def __init__(self, body, fieldmap, event=None, sandbox_observer=None):
        self.body = body
        self.fieldmap = fieldmap
        self.sandbox = Sandbox(fieldmap)
        self.event = event or (lambda kind, data: None)
        self.sandbox_observer = sandbox_observer
        self.phase = "IDLE"
        self.metrics = {}
        self.sandbox_state = None

    def _emit(self, kind, **data):
        self.event(kind, data)

    def _observe_sandbox(self, state):
        self.sandbox_state = state
        self._emit(
            "sandbox_step",
            operation=state["operation"],
            sequence=state["sequence"],
            attempts=state["attempts"],
            position=state["active_cell"],
            instruction=state["instruction"],
        )
        if self.sandbox_observer is not None:
            self.sandbox_observer(state)
    def discover(self, size):
        self.phase = "PHYSICAL_EXPERIMENT"
        cells = list(range(size * size))
        total = 2 * (len(cells) * (len(cells) - 1) // 2)
        completed = 0
        for left, right in combinations(cells, 2):
            a = divmod(left, size)
            b = divmod(right, size)
            for values in ((1, 1), (1, 2)):
                self.body.reset_experiment()
                first = self.body.act(a, values[0], purpose="controlled-probe:first")
                if not first["receipt"]["accepted"]:
                    raise RuntimeError("EMPTY_WORLD_REJECTED_FIRST_PROBE")
                second = self.body.act(b, values[1], purpose="controlled-probe:second")
                accepted = second["receipt"]["accepted"]
                self.fieldmap.retrieve_by_gap((*a, values[0]), (*b, values[1]), size, observed_conflict=not accepted)
                self.fieldmap.observe_pair((*a, values[0]), (*b, values[1]), size, accepted)
                completed += 1
                if completed % max(1, total // 20) == 0:
                    self._emit("progress", phase=self.phase, completed=completed, total=total)
        self.phase = "FIELD_COLLAPSE"
        theory = self.fieldmap.collapse(size)
        self._emit("theory", **theory)
        return theory

    def evaluate(self, size, limit=240):
        self.phase = "HELD_OUT_VERIFICATION"
        cells = list(range(size * size))
        cases = []
        for value_pair in ((size, size), (size, max(1, size - 1))):
            for left, right in combinations(cells, 2):
                cases.append((left, right, value_pair))
        stride = max(1, len(cases) // limit)
        chosen = cases[::stride][:limit]
        correct = 0
        baseline_correct = 0
        for left, right, values in chosen:
            a, b = divmod(left, size), divmod(right, size)
            predicted_reject = self.fieldmap.predicts_conflict((*a, values[0]), (*b, values[1]), size)
            self.body.reset_experiment()
            self.body.act(a, values[0], purpose="heldout:first")
            result = self.body.act(b, values[1], purpose="heldout:second")
            actual_reject = not result["receipt"]["accepted"]
            self.fieldmap.retrieve_by_gap((*a, values[0]), (*b, values[1]), size, observed_conflict=actual_reject)
            correct += predicted_reject == actual_reject
            baseline_correct += actual_reject is False
        report = {"cases": len(chosen), "accuracy": round(correct / max(1, len(chosen)), 6), "empty_model_baseline": round(baseline_correct / max(1, len(chosen)), 6)}
        self.metrics["verification"] = report
        self._emit("verification", **report)
        return report

    def solve_current(self):
        self.phase = "SANDBOX"
        packet = self.body.reset_challenge()
        public = packet["vision"]
        sandbox = self.sandbox.complete(public, observe=self._observe_sandbox)
        self.sandbox_state = sandbox
        self._emit("sandbox", found=sandbox["found"], attempts=sandbox["attempts"])
        if not sandbox["found"]:
            self.phase = "GAP_UNRESOLVED"
            return {"status": self.phase, "sandbox": sandbox}
        self.phase = "PHYSICAL_COMMIT"
        last = None
        for y in range(public["shape"][0]):
            for x in range(public["shape"][1]):
                if public["fixed"][y][x]:
                    continue
                last = self.body.act((y, x), sandbox["board"][y][x], purpose="challenge-commit")
                if not last["receipt"]["accepted"]:
                    self.phase = "COUNTEREXAMPLE"
                    self._emit("counterexample", position=[y, x], value=sandbox["board"][y][x])
                    return {"status": self.phase, "sandbox": sandbox, "receipt": last["receipt"]}
        observation = self.body.sense()["vision"]
        self.phase = "SOLVED" if last and last["receipt"]["complete"] else "INCOMPLETE"
        self._emit("result", status=self.phase, actions=observation["action_index"])
        return {"status": self.phase, "sandbox": sandbox, "observation": observation}
