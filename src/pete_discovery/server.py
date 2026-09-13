from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

from .runtime import ExperimentRuntime


class App:
    def __init__(self, root):
        self.runtime = ExperimentRuntime(root)


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
