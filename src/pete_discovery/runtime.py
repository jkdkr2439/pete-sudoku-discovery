from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from time import sleep, time

from .body import Body
from .cognition import DiscoveryAgent
from .fieldmap import DynamicFieldmap
from .journal import HashJournal
from .substrate import SudokuSubstrate


class ExperimentRuntime:
    def __init__(self, root="runtime", *, size=9, level=0, seed=1):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self.world = SudokuSubstrate(size=size, level=level, seed=seed)
        self.journal = HashJournal(self.root / "logs" / "physical-journal.jsonl")
        self.body = Body(self.world, self.journal)
        self.fieldmap = DynamicFieldmap()
        self.events = []
        self.running = False
        self.continuous = False
        self.stop_requested = False
        self.started_at = None
        self.finished_at = None
        self.last_error = None
        self.last_receipt = None
        self.worlds_completed = 0
        self.history = []
        self.agent = DiscoveryAgent(self.body, self.fieldmap, self._event)

    def _event(self, kind, data):
        with self.lock:
            row = {"time": time(), "kind": kind, **data}
            self.events.append(row)
            self.events = self.events[-120:]

    def _begin(self, continuous):
        if self.running:
            return False
        self.running = True
        self.continuous = bool(continuous)
        self.stop_requested = False
        self.started_at = time()
        self.finished_at = None
        self.last_error = None
        return True

    def _execute_current(self):
        size = self.world.size
        world_identity = {
            "world_id": self.world.observe()["world_id"],
            "size": size,
            "level": self.world.level,
            "seed": self.world.seed,
        }
        if self.fieldmap.clauses:
            theory = {
                "version": self.fieldmap.version,
                "sample_count": len(self.fieldmap.samples),
                "clauses": list(self.fieldmap.clauses),
                "reused": True,
            }
            self._event("theory_reused", {"version": self.fieldmap.version, "size": size})
        else:
            theory = self.agent.discover(size)
        verification = self.agent.evaluate(size)
        result = self.agent.solve_current()
        receipt = {
            "schema": "pete.sudoku-discovery.receipt.v2",
            **world_identity,
            "theory": theory,
            "verification": verification,
            "result": result["status"],
            "sandbox_attempts": (result.get("sandbox") or {}).get("attempts"),
            "physical_actions": self.world.action_index,
            "life": self.body.life,
            "energy": self.body.energy,
            "journal_head": self.journal.previous,
        }
        self.last_receipt = receipt
        (self.root / "experiment-receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        self._event("checkpoint", {"world_id": world_identity["world_id"], "result": result["status"]})
        if result["status"] == "SOLVED":
            self.worlds_completed += 1
            summary = {
                "ordinal": self.worlds_completed,
                "world_id": world_identity["world_id"],
                "seed": world_identity["seed"],
                "level": world_identity["level"],
                "result": result["status"],
                "sandbox_attempts": receipt["sandbox_attempts"],
                "fieldmap_version": self.fieldmap.version,
                "journal_head": self.journal.previous,
            }
            self.history.append(summary)
            self.history = self.history[-100:]
            (self.root / "world-history.json").write_text(json.dumps(self.history, indent=2), encoding="utf-8")
        return receipt

    def _advance_world(self, clear_events=False):
        previous = self.world.observe()["world_id"]
        observation = self.world.next_world()
        self.agent = DiscoveryAgent(self.body, self.fieldmap, self._event)
        if clear_events:
            self.events = []
        self._event("world_advanced", {
            "previous_world": previous,
            "next_world": observation["world_id"],
            "seed": self.world.seed,
            "level": self.world.level,
            "fieldmap_version": self.fieldmap.version,
        })
        return observation

    def run_once(self):
        if not self._begin(False):
            return False
        try:
            self._execute_current()
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            self.agent.phase = "FAILED"
            self._event("error", {"message": self.last_error})
        finally:
            self.finished_at = time()
            self.running = False
            self.continuous = False
        return True

    def run_continuous(self):
        if not self._begin(True):
            return False
        try:
            if self.agent.phase == "SOLVED":
                self._advance_world()
            while not self.stop_requested:
                receipt = self._execute_current()
                if receipt["result"] != "SOLVED" or self.stop_requested:
                    break
                sleep(0.75)
                if not self.stop_requested:
                    self._advance_world()
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            self.agent.phase = "FAILED"
            self._event("error", {"message": self.last_error})
        finally:
            self.finished_at = time()
            self.running = False
            self.continuous = False
            self._event("scheduler_stopped", {"pause_requested": self.stop_requested})
        return True

    def run(self):
        return self.run_once()

    def request_pause(self):
        if not self.running:
            return False
        self.stop_requested = True
        self._event("pause_requested", {"boundary": "after-current-world"})
        return True

    def new_world(self):
        if self.running:
            return False
        self._advance_world(clear_events=True)
        return True

    def snapshot(self):
        with self.lock:
            events = list(self.events)
        sensed = self.body.sense()
        return {
            "running": self.running,
            "continuous": self.continuous,
            "pause_requested": self.stop_requested,
            "phase": self.agent.phase,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.last_error,
            "worlds_completed": self.worlds_completed,
            "history": list(self.history),
            "last_receipt": self.last_receipt,
            "substrate": sensed["vision"],
            "body": sensed["interoception"],
            "fieldmap": self.fieldmap.snapshot(),
            "sandbox": self.agent.sandbox_state,
            "metrics": dict(self.agent.metrics),
            "journal": {"events": self.journal.sequence, "head": self.journal.previous},
            "events": events,
            "separation": {
                "substrate": "authoritative hidden constraints and consequences",
                "sandbox": "small counterfactual workspace over learned Fieldmap only",
                "fieldmap": "dynamic evidence-weighted internal relations",
            },
        }
