from __future__ import annotations

from collections import Counter
import hashlib
import json


def _hash(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


class DynamicFieldmap:
    """A changing structure whose durable data is the reaction caused by input."""

    def __init__(self):
        self.samples: list[dict] = []
        self.clauses: list[dict] = []
        self.relation_evidence: dict[str, dict] = {}
        self.outcome_counts = {"accepted": 0, "rejected": 0}
        self.reactions: dict[str, dict] = {}
        self.reaction_sequence = 0
        self.last_retrieval: list[dict] = []
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

    def _structure_payload(self):
        return {
            "relations": self.relation_evidence,
            "outcomes": self.outcome_counts,
            "clauses": self.clauses,
            "version": self.version,
        }

    @property
    def structure_hash(self):
        return _hash(self._structure_payload())

    def observe_pair(self, a, b, size, accepted):
        before_hash = self.structure_hash
        predicted_conflict = self.predicts_conflict(a, b, size)
        actual_conflict = not bool(accepted)
        descriptors = self.descriptors(a, b, size)
        encoded = [sorted(row) for row in descriptors]
        outcome = "accepted" if accepted else "rejected"
        mutations = []
        self.outcome_counts[outcome] += 1
        mutations.append({"target": f"outcome:{outcome}", "delta": 1})
        for descriptor in sorted(descriptors, key=lambda row: tuple(sorted(row))):
            relation_id = "relation:" + _hash(sorted(descriptor))[:16]
            row = self.relation_evidence.setdefault(relation_id, {
                "terms": sorted(descriptor), "support": 0, "counterevidence": 0,
                "dynamic_weight": 0.5, "activation": 0.0, "last_sequence": 0,
            })
            key = "support" if actual_conflict else "counterevidence"
            old_weight = row["dynamic_weight"]
            row[key] += 1
            row["dynamic_weight"] = round(row["support"] / max(1, row["support"] + row["counterevidence"]), 6)
            row["activation"] = 1.0
            row["last_sequence"] = self.reaction_sequence + 1
            mutations.append({
                "target": relation_id,
                "counter": key,
                "delta": 1,
                "weight_before": old_weight,
                "weight_after": row["dynamic_weight"],
            })
        self.samples.append({"size": size, "accepted": bool(accepted), "descriptors": encoded})
        self.reaction_sequence += 1
        after_hash = self.structure_hash
        gap = {
            "prediction": "conflict" if predicted_conflict else "compatible",
            "observation": "conflict" if actual_conflict else "compatible",
            "prediction_mismatch": predicted_conflict != actual_conflict,
            "affected_relations": sorted(_hash(row)[:16] for row in encoded),
            "mutation_count": len(mutations),
        }
        input_encoding = {"left": list(a), "right": list(b), "size": size}
        signature = _hash({
            "mismatch": gap["prediction_mismatch"],
            "observation": gap["observation"],
            "affected": gap["affected_relations"],
        })
        aggregate = self.reactions.setdefault(signature, {
            "id": "reaction:" + signature[:16],
            "count": 0,
            "gap_signature": gap,
            "affected_relations": gap["affected_relations"],
            "first_sequence": self.reaction_sequence,
        })
        aggregate.update({
            "count": aggregate["count"] + 1,
            "last_sequence": self.reaction_sequence,
            "input_reference": _hash(input_encoding)[:16],
            "transition": {"before": before_hash, "after": after_hash},
            "mutations": mutations,
        })
        return aggregate

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
            "structure_hash": self.structure_hash,
            "reaction_shapes": len(self.reactions),
        }

    def predicts_conflict(self, a, b, size):
        descriptors = self.descriptors(a, b, size)
        return any(frozenset(row["terms"]) in descriptors for row in self.clauses)

    def retrieve_by_gap(self, a, b, size, observed_conflict=None, limit=5):
        query_relations = sorted(_hash(sorted(row))[:16] for row in self.descriptors(a, b, size))
        query = set(query_relations)
        ranked = []
        for reaction in self.reactions.values():
            stored = set(reaction["affected_relations"])
            overlap = len(query & stored) / max(1, len(query | stored))
            outcome_match = 0.0
            if observed_conflict is not None:
                expected = "conflict" if observed_conflict else "compatible"
                outcome_match = 1.0 if reaction["gap_signature"]["observation"] == expected else 0.0
            score = round(0.75 * overlap + 0.25 * outcome_match, 6)
            if score:
                ranked.append({
                    "reaction_id": reaction["id"],
                    "score": score,
                    "count": reaction["count"],
                    "gap_signature": reaction["gap_signature"],
                })
        self.last_retrieval = sorted(ranked, key=lambda row: (-row["score"], -row["count"], row["reaction_id"]))[:limit]
        return list(self.last_retrieval)

    def snapshot(self):
        recent = sorted(self.reactions.values(), key=lambda row: row["last_sequence"], reverse=True)[:5]
        return {
            "version": self.version,
            "samples": len(self.samples),
            "clauses": list(self.clauses),
            "structure_hash": self.structure_hash,
            "relation_nodes": len(self.relation_evidence),
            "reaction_shapes": len(self.reactions),
            "reaction_events": self.reaction_sequence,
            "recent_reactions": recent,
            "last_gap_retrieval": list(self.last_retrieval),
        }
