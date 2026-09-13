from __future__ import annotations

from collections import Counter


class DynamicFieldmap:
    """Evidence-weighted relations built from experience, never from world internals."""

    def __init__(self):
        self.samples: list[dict] = []
        self.clauses: list[dict] = []
        self.version = 0

    @staticmethod
    def _facts(a, b, size):
        (ay, ax, av), (by, bx, bv) = a, b
        facts = {"value:eq"} if av == bv else {"value:ne"}
        left, right = (ay, ax), (by, bx)
        for axis, (u, v) in enumerate(zip(left, right)):
            facts.add(f"axis:{axis}:eq" if u == v else f"axis:{axis}:ne")
        for scale in range(2, size + 1):
            for axis, (u, v) in enumerate(zip(left, right)):
                if u // scale == v // scale:
                    facts.add(f"axis:{axis}:bucket:{scale}:eq")
        return facts

    @classmethod
    def descriptors(cls, a, b, size):
        facts = cls._facts(a, b, size)
        generated = set()
        if "value:eq" not in facts:
            return generated
        for axis in range(2):
            key = f"axis:{axis}:eq"
            if key in facts:
                generated.add(frozenset(("value:eq", key)))
        for scale in range(2, size + 1):
            keys = (f"axis:0:bucket:{scale}:eq", f"axis:1:bucket:{scale}:eq")
            if all(key in facts for key in keys):
                generated.add(frozenset(("value:eq", *keys)))
        return generated

    def observe_pair(self, a, b, size, accepted):
        self.samples.append({
            "a": list(a), "b": list(b), "size": size,
            "accepted": bool(accepted),
            "descriptors": [sorted(row) for row in self.descriptors(a, b, size)],
        })

    def collapse(self, size, minimum_support=3):
        relevant = [row for row in self.samples if row["size"] == size]
        candidates = Counter()
        false_positive = Counter()
        rejected_ids = set()
        for index, row in enumerate(relevant):
            if not row["accepted"]:
                rejected_ids.add(index)
            for descriptor in map(frozenset, row["descriptors"]):
                if row["accepted"]:
                    false_positive[descriptor] += 1
                else:
                    candidates[descriptor] += 1
        viable = [key for key, support in candidates.items() if support >= minimum_support and false_positive[key] == 0]
        uncovered = set(rejected_ids)
        selected = []
        while uncovered:
            ranked = []
            for key in viable:
                covered = {i for i in uncovered if key in map(frozenset, relevant[i]["descriptors"])}
                ranked.append((len(covered), -len(key), tuple(sorted(key)), key, covered))
            best = max(ranked, default=None)
            if not best or best[0] == 0:
                break
            _, _, _, key, covered = best
            selected.append({
                "terms": sorted(key),
                "support": candidates[key],
                "counterevidence": false_positive[key],
                "dynamic_weight": round(candidates[key] / max(1, candidates[key] + false_positive[key]), 6),
            })
            uncovered -= covered
            viable.remove(key)
        self.clauses = selected
        self.version += 1
        return {
            "version": self.version,
            "sample_count": len(relevant),
            "rejected_count": len(rejected_ids),
            "clauses": list(self.clauses),
            "unexplained_rejections": len(uncovered),
        }

    def predicts_conflict(self, a, b, size):
        descriptors = self.descriptors(a, b, size)
        return any(frozenset(row["terms"]) in descriptors for row in self.clauses)

    def snapshot(self):
        return {"version": self.version, "samples": len(self.samples), "clauses": list(self.clauses)}
