from __future__ import annotations

import hashlib
import json
from pathlib import Path
from threading import Lock
from time import time


class HashJournal:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self.sequence = 0
        self.previous = "GENESIS"
        if self.path.exists():
            rows = [line for line in self.path.read_text(encoding="utf-8").splitlines() if line]
            if rows:
                last = json.loads(rows[-1])
                self.sequence = int(last["sequence"])
                self.previous = last["hash"]

    def append(self, kind: str, data: dict) -> dict:
        with self.lock:
            row = {
                "sequence": self.sequence + 1,
                "previous": self.previous,
                "time": time(),
                "kind": kind,
                "data": data,
            }
            payload = json.dumps(row, sort_keys=True, separators=(",", ":"))
            row["hash"] = hashlib.sha256(payload.encode()).hexdigest()
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
            self.sequence = row["sequence"]
            self.previous = row["hash"]
            return row
