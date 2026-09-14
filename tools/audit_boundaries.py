from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COGNITION_FILES = [
    ROOT / "src/pete_discovery/cognition.py",
    ROOT / "src/pete_discovery/fieldmap.py",
    ROOT / "src/pete_discovery/sandbox.py",
    ROOT / "src/pete_discovery/pairmap.py",
    ROOT / "src/pete_discovery/acquisition.py",
    ROOT / "src/pete_discovery/recovery.py",
    ROOT / "src/pete_discovery/model_memory.py",
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


def audit_source(source, filename):
    violations = []
    for node in ast.walk(ast.parse(source)):
        names = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
            names.extend(alias.name for alias in node.names)
        for name in names:
            if any(part in {"substrate", "runtime", "opaque_experiment", "recovery_experiment", "memory_experiment", "server", "body"}
                   for part in name.split(".")):
                violations.append(f"{filename}: forbidden authority import {name}")
        if isinstance(node, ast.Attribute) and (
            node.attr.startswith("hidden_") or "__world" in node.attr or node.attr in {"_solution", "change_roles"}
        ):
            violations.append(f"{filename}: forbidden authority attribute {node.attr}")
    for token in ("hidden_grade", "hidden_pair_conflict", "_valid(", "_solution"):
        if token in source:
            violations.append(f"{filename}: forbidden authority token {token}")
    return violations


def main():
    violations = []
    for path in COGNITION_FILES:
        source = path.read_text(encoding="utf-8")
        violations.extend(audit_source(source, path.name))
    result = {"status": "PASS" if not violations else "FAIL", "files": [str(p) for p in COGNITION_FILES], "violations": violations}
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(violations))


if __name__ == "__main__":
    main()
