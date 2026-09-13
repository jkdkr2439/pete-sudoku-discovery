from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from time import time

from .body import Body
from .cognition import DiscoveryAgent
from .fieldmap import DynamicFieldmap
from .journal import HashJournal
from .substrate import SudokuSubstrate


class ExperimentRuntime:
    def __init__(self, root="runtime", *, size=4, level=0, seed=1):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self.world = SudokuSubstrate(size=size, level=level, seed=seed)
        self.journal = HashJournal(self.root / "logs" / "physical-journal.jsonl")
        self.body = Body(self.world, self.journal)
        self.fieldmap = DynamicFieldmap()
        self.events = []
        self.running = False
        self.started_at = None
        self.finished_at = None
        self.last_error = None
        self.agent = DiscoveryAgent(self.body, self.fieldmap, self._event)

    def _event(self, kind, data):
        with self.lock:
            row = {"time": time(), "kind": kind, **data}
            self.events.append(row)
            self.events = self.events[-120:]

    def run(self):
        if self.running:
            return
        self.running = True
        self.started_at = time()
        self.finished_at = None
        self.last_error = None
        try:
            size = self.world.size
            if self.fieldmap.clauses:
                theory = {"version": self.fieldmap.version, "sample_count": len(self.fieldmap.samples), "clauses": list(self.fieldmap.clauses), "reused": True}
                self._event("theory_reused", {"version": self.fieldmap.version, "size": size})
            else:
                theory = self.agent.discover(size)
            verification = self.agent.evaluate(size)
            result = self.agent.solve_current()
            receipt = {
                "schema": "pete.sudoku-discovery.receipt.v1",
                "size": size,
                "level": self.world.level,
                "seed": self.world.seed,
                "theory": theory,
                "verification": verification,
                "result": result["status"],
                "imagination_attempts": (result.get("imagination") or {}).get("attempts"),
                "physical_actions": self.world.action_index,
                "life": self.body.life,
                "energy": self.body.energy,
                "journal_head": self.journal.previous,
            }
            path = self.root / "experiment-receipt.json"
            path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
            self._event("checkpoint", {"path": str(path), "result": result["status"]})
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            self.agent.phase = "FAILED"
            self._event("error", {"message": self.last_error})
        finally:
            self.finished_at = time()
            self.running = False

    def new_world(self):
        if self.running:
            return False
        previous_size = self.world.size
        self.world.next_world()
        if self.world.size != previous_size:
            self.fieldmap = DynamicFieldmap()
        self.agent = DiscoveryAgent(self.body, self.fieldmap, self._event)
        self.events = []
        return True

    def snapshot(self):
        with self.lock:
            events = list(self.events)
        sensed = self.body.sense()
        return {
            "running": self.running,
            "phase": self.agent.phase,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.last_error,
            "substrate": sensed["vision"],
            "body": sensed["interoception"],
            "fieldmap": self.fieldmap.snapshot(),
            "imagination": self.agent.imagined,
            "metrics": dict(self.agent.metrics),
            "journal": {"events": self.journal.sequence, "head": self.journal.previous},
            "events": events,
            "separation": {
                "substrate": "authoritative hidden constraints and consequences",
                "imagination": "counterfactual search over learned Fieldmap only",
                "fieldmap": "dynamic evidence-weighted internal relations",
            },
        }
