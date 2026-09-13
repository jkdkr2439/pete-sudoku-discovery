from __future__ import annotations

from dataclasses import dataclass
from random import Random

Board = tuple[tuple[int, ...], ...]


def _groups(board: Board):
    size = len(board)
    root = int(size ** 0.5)
    yield from board
    for x in range(size):
        yield tuple(board[y][x] for y in range(size))
    for y0 in range(0, size, root):
        for x0 in range(0, size, root):
            yield tuple(board[y][x] for y in range(y0, y0 + root) for x in range(x0, x0 + root))


def _valid(board: Board) -> bool:
    size = len(board)
    for group in _groups(board):
        occupied = [value for value in group if value]
        if any(value < 1 or value > size for value in occupied):
            return False
        if len(occupied) != len(set(occupied)):
            return False
    return True


def _solutions(board: Board, limit: int = 2) -> list[Board]:
    size = len(board)
    work = [list(row) for row in board]
    output: list[Board] = []

    def options(y: int, x: int):
        values = []
        for value in range(1, size + 1):
            work[y][x] = value
            if _valid(tuple(tuple(row) for row in work)):
                values.append(value)
        work[y][x] = 0
        return values

    def visit():
        if len(output) >= limit:
            return
        open_cells = [
            (len(found), y, x, found)
            for y in range(size)
            for x in range(size)
            if work[y][x] == 0
            for found in [options(y, x)]
        ]
        if not open_cells:
            output.append(tuple(tuple(row) for row in work))
            return
        _, y, x, found = min(open_cells)
        for value in found:
            work[y][x] = value
            visit()
            work[y][x] = 0

    visit()
    return output


def generate(size: int, clues: int, seed: int) -> tuple[Board, Board]:
    root = int(size ** 0.5)
    if root * root != size:
        raise ValueError("WORLD_REQUIRES_SQUARE_DIMENSION")
    rng = Random(seed)
    symbols = list(range(1, size + 1))
    rng.shuffle(symbols)
    pattern = lambda y, x: (root * (y % root) + y // root + x) % size
    bands = rng.sample(range(root), root)
    stacks = rng.sample(range(root), root)
    ys = [band * root + y for band in bands for y in rng.sample(range(root), root)]
    xs = [stack * root + x for stack in stacks for x in rng.sample(range(root), root)]
    solution = tuple(tuple(symbols[pattern(y, x)] for x in xs) for y in ys)
    board = [list(row) for row in solution]
    cells = list(range(size * size))
    rng.shuffle(cells)
    for index in cells:
        if sum(bool(v) for row in board for v in row) <= clues:
            break
        y, x = divmod(index, size)
        old = board[y][x]
        board[y][x] = 0
        if len(_solutions(tuple(tuple(row) for row in board), 2)) != 1:
            board[y][x] = old
    return tuple(tuple(row) for row in board), solution


@dataclass(frozen=True)
class WorldReceipt:
    accepted: bool
    complete: bool
    changed: bool
    life_delta: int
    action_index: int

    def public(self):
        return {
            "accepted": self.accepted,
            "complete": self.complete,
            "changed": self.changed,
            "life_delta": self.life_delta,
            "action_index": self.action_index,
        }


class SudokuSubstrate:
    """Authoritative world. Its internals are deliberately hidden from cognition."""

    SIZE = 9
    TIERS = (50, 40, 30)

    def __init__(self, size=9, level=0, seed=1):
        self.size = int(size)
        if self.size != self.SIZE:
            raise ValueError("ONLY_9X9_WORLD_IS_AVAILABLE")
        self.level = int(level)
        self.seed = int(seed)
        self.action_index = 0
        self.mode = "challenge"
        self._load_challenge()

    def _load_challenge(self):
        tiers = self.TIERS
        clues = tiers[min(self.level, len(tiers) - 1)]
        self._initial, self._solution = generate(self.size, clues, self.seed)
        self._board = self._initial
        self._initial_givens = tuple(tuple(bool(v) for v in row) for row in self._initial)
        self._givens = self._initial_givens
        self.mode = "challenge"

    def next_world(self):
        tiers = self.TIERS
        self.level += 1
        if self.level >= len(tiers):
            self.level = len(tiers) - 1
            self.seed += 1
        self._load_challenge()
        return self.observe()

    def reset_challenge(self):
        self._board = self._initial
        self._givens = self._initial_givens
        self.mode = "challenge"

    def begin_experiment(self):
        self._board = tuple(tuple(0 for _ in range(self.size)) for _ in range(self.size))
        self._givens = tuple(tuple(False for _ in range(self.size)) for _ in range(self.size))
        self.mode = "experiment"
        return self.observe()

    def observe(self):
        return {
            "world_id": f"opaque-grid-{self.size}-{self.seed}-{self.level}",
            "shape": [self.size, self.size],
            "alphabet": list(range(1, self.size + 1)),
            "board": [list(row) for row in self._board],
            "fixed": [list(row) for row in self._givens],
            "mode": self.mode,
            "difficulty_index": self.level,
            "action_index": self.action_index,
        }

    def place(self, position: tuple[int, int], value: int) -> WorldReceipt:
        y, x = map(int, position)
        value = int(value)
        self.action_index += 1
        before = self._board
        accepted = 0 <= y < self.size and 0 <= x < self.size
        accepted = accepted and not self._givens[y][x] and before[y][x] == 0
        if accepted:
            work = [list(row) for row in before]
            work[y][x] = value
            candidate = tuple(tuple(row) for row in work)
            accepted = _valid(candidate)
            if accepted:
                self._board = candidate
        complete = self.mode == "challenge" and self._board == self._solution
        return WorldReceipt(accepted, complete, before != self._board, 0 if accepted else -1, self.action_index)

    def hidden_grade(self, board: Board) -> bool:
        """Test/authority hook. Never exposed through a body port."""
        return board == self._solution and _valid(board)
