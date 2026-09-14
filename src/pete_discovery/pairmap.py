"""Spatially blind pair evidence, with an explicit symbol-symmetry prior."""
from __future__ import annotations

from math import isqrt

from .fieldmap import DynamicFieldmap


class PairwiseFieldmap:
    """Unknown, compatible, or conflicting for each cell pair and equality class.

    Authored assumptions: stationary deterministic pair constraints and invariance
    under symbol permutations. Neither equality nor inequality implies conflict.
    """

    def __init__(self):
        self.evidence = {}
        self.version = 0

    @staticmethod
    def key(a, b):
        left, right = sorted((a[0], b[0]))
        if left == right:
            raise ValueError("PAIR_REQUIRES_DISTINCT_CELLS")
        return left, right, a[1] == b[1]

    def observe_pair(self, a, b, accepted):
        key = self.key(a, b)
        conflict = not bool(accepted)
        row = self.evidence.setdefault(key, {"compatible": 0, "conflict": 0})
        row["conflict" if conflict else "compatible"] += 1
        self.version += 1
        if row["compatible"] and row["conflict"]:
            raise ValueError("CONTRADICTORY_PAIR_EVIDENCE")

    def known_conflict(self, a, b):
        row = self.evidence.get(self.key(a, b))
        if row is None:
            return None
        return bool(row["conflict"])

    def predicts_conflict(self, a, b):
        # Optimism is a search policy, not a claim that an unknown pair is valid.
        return self.known_conflict(a, b) is True

    def finalize(self):
        pass

    def snapshot(self):
        return {
            "model": "pairwise-equality-classes",
            "version": self.version,
            "known_pair_classes": len(self.evidence),
            "relations": [
                {"left": a, "right": b, "equal": equal, **counts}
                for (a, b, equal), counts in sorted(self.evidence.items())
            ],
        }


class RevisablePairwiseFieldmap(PairwiseFieldmap):
    """Latest directly observed label wins; contradicted evidence stays in history.

    Assumes noiseless feedback and rules stable during each repair phase. This is
    explicit belief revision, not a noise estimator or autonomous drift detector.
    """

    def __init__(self):
        super().__init__()
        self.revisions = []

    def revise_pair(self, a, b, accepted):
        key = self.key(a, b)
        previous = self.known_conflict(a, b)
        current = not bool(accepted)
        changed = previous is not None and previous != current
        if changed:
            self.revisions.append({
                "left": key[0], "right": key[1], "equal": key[2],
                "previous_conflict": previous, "current_conflict": current,
                "previous_evidence": dict(self.evidence[key]),
                "at_version": self.version + 1,
            })
            self.evidence[key] = {"compatible": 0, "conflict": 0}
        self.observe_pair(a, b, accepted)
        return changed

    def snapshot(self):
        return {**super().snapshot(), "revisions": list(self.revisions)}


class SpatialControl:
    """Original hypotheses over an arbitrary public ordering, without its mapping.

    Identity ordering recovers the original interface. Scrambled ordering tests
    whether those spatial hypotheses can represent the hidden relation network.
    """

    def __init__(self, cells):
        self.width = isqrt(len(cells))
        if self.width * self.width != len(cells):
            raise ValueError("SPATIAL_CONTROL_REQUIRES_SQUARE_CELL_COUNT")
        self.embedding = {cell: divmod(i, self.width) for i, cell in enumerate(cells)}
        self.fieldmap = DynamicFieldmap()

    @property
    def version(self):
        return self.fieldmap.version

    def _encode(self, assignment):
        cell, value = assignment
        return (*self.embedding[cell], value)

    def observe_pair(self, a, b, accepted):
        self.fieldmap.observe_pair(self._encode(a), self._encode(b), self.width, accepted)

    def predicts_conflict(self, a, b):
        return self.fieldmap.predicts_conflict(self._encode(a), self._encode(b), self.width)

    def finalize(self):
        self.fieldmap.collapse(self.width)

    def snapshot(self):
        return {"model": "original-spatial-hypotheses", **self.fieldmap.snapshot()}
