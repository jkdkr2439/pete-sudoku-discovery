from __future__ import annotations


class Sandbox:
    """Bounded counterfactual workspace using Fieldmap predictions only."""

    def __init__(self, fieldmap):
        self.fieldmap = fieldmap
        self.attempts = 0
        self.sequence = 0
        self.trace = []

    def compatible(self, board, position, value):
        size = len(board)
        y, x = position
        proposed = (y, x, value)
        for oy, row in enumerate(board):
            for ox, existing in enumerate(row):
                if existing and (oy, ox) != position:
                    if self.fieldmap.predicts_conflict((oy, ox, existing), proposed, size):
                        return False
        return True

    def complete(self, public_observation, budget=2_000_000, observe=None):
        board = [list(row) for row in public_observation["board"]]
        alphabet = list(public_observation["alphabet"])
        self.attempts = 0
        self.sequence = 0
        self.trace = []

        def publish(operation, *, position=None, value=None, candidates=None, instruction="", focus=""):
            self.sequence += 1
            record = {
                "sequence": self.sequence,
                "operation": operation,
                "position": list(position) if position is not None else None,
                "value": value,
                "candidate_count": len(candidates) if candidates is not None else None,
                "candidates": list(candidates) if candidates is not None else None,
                "instruction": instruction,
                "focus": focus,
                "attempts": self.attempts,
            }
            self.trace.append(record)
            self.trace = self.trace[-64:]
            state = {
                "found": operation == "COMPLETE",
                "board": [list(row) for row in board],
                "attempts": self.attempts,
                "fieldmap_version": self.fieldmap.version,
                "operation": operation,
                "active_cell": record["position"],
                "instruction": instruction,
                "focus": focus,
                "sequence": self.sequence,
                "recent_ops": list(self.trace),
            }
            if observe is not None:
                observe(state)
            return state

        def choices(y, x):
            return [value for value in alphabet if self.compatible(board, (y, x), value)]

        exhausted = False

        def search():
            nonlocal exhausted
            open_cells = [
                (len(found), y, x, found)
                for y in range(len(board))
                for x in range(len(board[y]))
                if board[y][x] == 0
                for found in [choices(y, x)]
            ]
            if not open_cells:
                publish("COMPLETE", instruction="return True", focus="return True")
                return True
            _, y, x, found = min(open_cells)
            publish(
                "SCAN",
                position=(y, x),
                candidates=found,
                instruction=f"select cell[{y}][{x}] from {found}",
                focus="_, y, x, found = min(open_cells)",
            )
            for value in found:
                if self.attempts >= budget:
                    exhausted = True
                    publish(
                        "BUDGET_STOP",
                        instruction=f"attempts >= {budget}",
                        focus="if self.attempts >= budget:",
                    )
                    return False
                self.attempts += 1
                board[y][x] = value
                publish(
                    "TRY",
                    position=(y, x),
                    value=value,
                    candidates=found,
                    instruction=f"board[{y}][{x}] = {value}",
                    focus="board[y][x] = value",
                )
                if search():
                    return True
                board[y][x] = 0
                if exhausted:
                    return False
                publish(
                    "BACKTRACK",
                    position=(y, x),
                    value=value,
                    instruction=f"board[{y}][{x}] = 0",
                    focus="board[y][x] = 0",
                )
            return False

        publish(
            "BEGIN",
            instruction="board = clone(public_observation)",
            focus='board = [list(row) for row in public_observation["board"]]',
        )
        solved = search()
        final = {
            "found": solved,
            "board": [list(row) for row in board] if solved else None,
            "attempts": self.attempts,
            "fieldmap_version": self.fieldmap.version,
            "operation": self.trace[-1]["operation"] if self.trace else "EMPTY",
            "active_cell": self.trace[-1]["position"] if self.trace else None,
            "instruction": self.trace[-1]["instruction"] if self.trace else "",
            "focus": self.trace[-1]["focus"] if self.trace else "",
            "sequence": self.sequence,
            "recent_ops": list(self.trace),
        }
        return final

    def complete_opaque(self, public_observation, budget=2_000_000, observe=None):
        """Reuse exactly the same search, with a one-row public-ID projection."""
        cells = list(public_observation["cells"])
        projected = {
            "board": [[public_observation["board"][cell] for cell in cells]],
            "alphabet": list(public_observation["alphabet"]),
        }
        worker = Sandbox(_PublicIdFieldmap(self.fieldmap, cells))
        result = worker.complete(projected, budget=budget, observe=observe)
        self.attempts, self.sequence, self.trace = worker.attempts, worker.sequence, worker.trace
        if result["board"] is not None:
            result["board"] = dict(zip(cells, result["board"][0]))
        return result


class _PublicIdFieldmap:
    """Mechanical addressing adapter with no constraint or coordinate knowledge."""

    def __init__(self, fieldmap, cells):
        self.fieldmap = fieldmap
        self.cells = cells

    @property
    def version(self):
        return self.fieldmap.version

    def predicts_conflict(self, a, b, size):
        return self.fieldmap.predicts_conflict((self.cells[a[1]], a[2]), (self.cells[b[1]], b[2]))
