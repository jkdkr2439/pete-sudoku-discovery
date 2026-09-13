from __future__ import annotations


class Sandbox:
    """Small counterfactual workspace using Fieldmap predictions only."""

    def __init__(self, fieldmap):
        self.fieldmap = fieldmap
        self.attempts = 0

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

    def complete(self, public_observation, budget=2_000_000):
        board = [list(row) for row in public_observation["board"]]
        alphabet = list(public_observation["alphabet"])
        self.attempts = 0

        def choices(y, x):
            return [value for value in alphabet if self.compatible(board, (y, x), value)]

        def search():
            if self.attempts >= budget:
                return False
            open_cells = [
                (len(found), y, x, found)
                for y in range(len(board))
                for x in range(len(board))
                if board[y][x] == 0
                for found in [choices(y, x)]
            ]
            if not open_cells:
                return True
            _, y, x, found = min(open_cells)
            for value in found:
                self.attempts += 1
                board[y][x] = value
                if search():
                    return True
                board[y][x] = 0
            return False

        solved = search()
        return {
            "found": solved,
            "board": [list(row) for row in board] if solved else None,
            "attempts": self.attempts,
            "fieldmap_version": self.fieldmap.version,
        }
