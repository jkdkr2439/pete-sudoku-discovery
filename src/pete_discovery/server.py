from __future__ import annotations

import argparse
import inspect
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

from .body import Body
from .cognition import DiscoveryAgent
from .fieldmap import DynamicFieldmap
from .runtime import ExperimentRuntime
from .sandbox import Sandbox


CODE_TARGETS = {
    "scheduler": ExperimentRuntime.run_continuous,
    "physical_experiment": DiscoveryAgent.discover,
    "field_collapse": DynamicFieldmap.collapse,
    "verification": DiscoveryAgent.evaluate,
    "sandbox": Sandbox.complete,
    "physical_commit": Body.act,
    "world_advance": ExperimentRuntime._advance_world,
    "decision": DiscoveryAgent.solve_current,
}

PHASE_ROUTES = {
    "IDLE": "scheduler",
    "PHYSICAL_EXPERIMENT": "physical_experiment",
    "FIELD_COLLAPSE": "field_collapse",
    "HELD_OUT_VERIFICATION": "verification",
    "SANDBOX": "sandbox",
    "PHYSICAL_COMMIT": "physical_commit",
    "SOLVED": "world_advance",
    "INCOMPLETE": "decision",
    "GAP_UNRESOLVED": "decision",
    "COUNTEREXAMPLE": "decision",
    "FAILED": "scheduler",
}


def code_catalog():
    routes = {}
    source_root = Path(__file__).resolve().parents[2]
    for key, target in CODE_TARGETS.items():
        lines, start_line = inspect.getsourcelines(target)
        path = Path(inspect.getsourcefile(target) or "")
        try:
            display_path = path.resolve().relative_to(source_root).as_posix()
        except ValueError:
            display_path = path.name
        routes[key] = {
            "key": key,
            "file": display_path,
            "function": target.__qualname__,
            "start_line": start_line,
            "end_line": start_line + len(lines) - 1,
            "source": "".join(lines),
        }
    return routes


CODE_CATALOG = code_catalog()


class App:
    def __init__(self, root):
        self.runtime = ExperimentRuntime(root, sandbox_step_delay=0.07)

    def code_state(self):
        phase = self.runtime.agent.phase
        active_key = PHASE_ROUTES.get(phase, "decision")
        return {
            "phase": phase,
            "active_key": active_key,
            "active": CODE_CATALOG[active_key],
            "routes": CODE_CATALOG,
            "note": "Observer-only source display; it cannot mutate cognition, Fieldmap, Sandbox, or substrate.",
        }


class Handler(BaseHTTPRequestHandler):
    app = None
    static = Path(__file__).with_name("static")

    def _send(self, status, body, content_type):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/state":
            self._send(200, json.dumps(self.app.runtime.snapshot()), "application/json")
            return
        if path == "/api/code":
            self._send(200, json.dumps(self.app.code_state()), "application/json")
            return
        name = "index.html" if path == "/" else path.lstrip("/")
        target = (self.static / name).resolve()
        if self.static.resolve() not in target.parents or not target.is_file():
            self._send(404, "Not found", "text/plain")
            return
        content_type = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "application/javascript"}.get(target.suffix, "application/octet-stream")
        self._send(200, target.read_bytes(), content_type)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/start":
            accepted = not self.app.runtime.running
            if accepted:
                Thread(target=self.app.runtime.run_continuous, daemon=True).start()
            self._send(202 if accepted else 409, json.dumps({"accepted": accepted, "mode": "continuous"}), "application/json")
            return
        if path == "/api/start-once":
            accepted = not self.app.runtime.running
            if accepted:
                Thread(target=self.app.runtime.run_once, daemon=True).start()
            self._send(202 if accepted else 409, json.dumps({"accepted": accepted, "mode": "one-world"}), "application/json")
            return
        if path == "/api/pause":
            accepted = self.app.runtime.request_pause()
            self._send(202 if accepted else 409, json.dumps({"accepted": accepted, "boundary": "after-current-world"}), "application/json")
            return
        if path == "/api/new":
            changed = self.app.runtime.new_world()
            self._send(200 if changed else 409, json.dumps({"changed": changed}), "application/json")
            return
        self._send(404, "Not found", "text/plain")

    def log_message(self, format, *args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8792)
    parser.add_argument("--state", default="runtime")
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    Handler.app = App(args.state)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Pete Sudoku Discovery: http://{args.host}:{args.port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
