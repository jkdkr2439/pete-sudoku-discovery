from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COGNITION_FILES = [
    ROOT / "src/pete_discovery/cognition.py",
    ROOT / "src/pete_discovery/fieldmap.py",
    ROOT / "src/pete_discovery/imagination.py",
]


def imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    output = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            output.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            output.append(node.module or "")
    return output


def main():
    violations = []
    for path in COGNITION_FILES:
        for name in imports(path):
            if "substrate" in name:
                violations.append(f"{path.name}: forbidden import {name}")
        source = path.read_text(encoding="utf-8")
        for token in ("hidden_grade", "_valid(", "_solution"):
            if token in source:
                violations.append(f"{path.name}: forbidden authority token {token}")
    result = {"status": "PASS" if not violations else "FAIL", "files": [str(p) for p in COGNITION_FILES], "violations": violations}
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(violations))


if __name__ == "__main__":
    main()
