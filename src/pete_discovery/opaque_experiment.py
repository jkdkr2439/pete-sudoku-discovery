"""Local benchmark orchestration; authority hooks stay outside learner/search code."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import platform
import subprocess
from time import perf_counter
import traceback

from .acquisition import Acquisition
from .body import Body
from .journal import HashJournal
from .pairmap import PairwiseFieldmap, SpatialControl
from .sandbox import Sandbox
from .substrate import OpaqueSudokuSubstrate

ARMS = ("spatial", "pair_exhaustive", "pair_adaptive", "pair_cost_aware")


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_journal(path):
    previous, count = "GENESIS", 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            claimed = row.pop("hash")
            payload = json.dumps(row, sort_keys=True, separators=(",", ":"))
            if row["previous"] != previous or row["sequence"] != count + 1:
                raise ValueError("JOURNAL_CHAIN_MISMATCH")
            if hashlib.sha256(payload.encode()).hexdigest() != claimed:
                raise ValueError("JOURNAL_HASH_MISMATCH")
            previous, count = claimed, count + 1
    return {"verified": True, "events": count, "head": previous}


def run_case(root, *, arm, seed, level, scramble_seed, interaction_budget, search_budget):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    config = dict(arm=arm, seed=seed, level=level, scramble_seed=scramble_seed,
                  interaction_budget=interaction_budget, search_budget=search_budget)
    write_json(root / "config.json", config)
    receipt = {"schema": "pete.opaque-acquisition.case.v1", "config": config, "status": "ERROR"}
    started = perf_counter()
    try:
        if arm not in ARMS:
            raise ValueError("UNKNOWN_ARM")
        world = OpaqueSudokuSubstrate(seed=seed, level=level, scramble_seed=scramble_seed)
        receipt["generation_seconds"] = perf_counter() - started
        public = world.observe()
        receipt["clues"] = sum(bool(value) for value in public["board"].values())
        journal = HashJournal(root / "physical-journal.jsonl")
        journal.append("experiment.initial", public)
        body = Body(world, journal)
        model = SpatialControl(public["cells"]) if arm == "spatial" else PairwiseFieldmap()
        acquisition = Acquisition(body, model, interaction_budget=interaction_budget)
        tick = perf_counter()
        policy = {"pair_adaptive": "adaptive", "pair_cost_aware": "cost_aware"}.get(arm, "exhaustive")
        receipt["learning"] = acquisition.run(policy)
        receipt["learning_seconds"] = perf_counter() - tick
        write_json(root / "model.json", model.snapshot())
        receipt["model_sha256"] = sha256(root / "model.json")
        # Search and commitment precede authority-side model evaluation.
        public = body.reset_challenge()["vision"]
        journal.append("experiment.challenge_restored", public)
        operations = Counter()
        trace_path = root / "sandbox-trace.jsonl"
        tick = perf_counter()
        with trace_path.open("w", encoding="utf-8", newline="\n") as trace:
            def observe(state):
                operations[state["operation"]] += 1
                trace.write(json.dumps(state, separators=(",", ":")) + "\n")
            result = Sandbox(model).complete_opaque(public, budget=search_budget, observe=observe)
        receipt["search_seconds"] = perf_counter() - tick
        receipt["search"] = {"found": result["found"], "attempts": result["attempts"],
                             "operation": result["operation"], "operations": dict(operations)}
        receipt["commit_placements"] = 0
        receipt["status"] = "SEARCH_BUDGET_STOP" if result["operation"] == "BUDGET_STOP" else "NO_COMPLETION"
        if result["found"]:
            receipt["status"] = "INCOMPLETE"
            for cell in public["cells"]:
                if public["fixed"][cell]:
                    continue
                response = body.act(cell, result["board"][cell], purpose="challenge-commit")
                receipt["commit_placements"] += 1
                receipt["last_commit_receipt"] = response["receipt"]
                if not response["receipt"]["accepted"]:
                    receipt["status"] = "COUNTEREXAMPLE"
                    break
                if response["receipt"]["complete"]:
                    receipt["status"] = "SOLVED"
        write_json(root / "final-observation.json", body.sense()["vision"])
        # The evaluator never supplies labels back to the frozen learner.
        tick = perf_counter()
        confusion = Counter()
        known = 0
        value_pairs = ((public["alphabet"][-1], public["alphabet"][-1]),
                       (public["alphabet"][-1], public["alphabet"][-2]))
        for a, b in combinations(public["cells"], 2):
            for av, bv in value_pairs:
                predicted = model.predicts_conflict((a, av), (b, bv))
                actual = world.hidden_pair_conflict(a, av, b, bv)
                confusion[("true" if predicted == actual else "false") + ("_positive" if predicted else "_negative")] += 1
                if isinstance(model, PairwiseFieldmap):
                    known += model.known_conflict((a, av), (b, bv)) is not None
        receipt["evaluation_seconds"] = perf_counter() - tick
        cases = sum(confusion.values())
        receipt["prediction"] = {"cases": cases, "confusion": dict(confusion),
                                 "accuracy": (confusion["true_positive"] + confusion["true_negative"]) / cases,
                                 "known_pair_classes": known if isinstance(model, PairwiseFieldmap) else None}
        if model.snapshot() != json.loads((root / "model.json").read_text(encoding="utf-8")):
            raise ValueError("EVALUATOR_MUTATED_MODEL")
        receipt["physical_actions"] = world.action_index
        receipt["journal"] = verify_journal(journal.path)
        receipt["sandbox_trace_sha256"] = sha256(trace_path)
    except Exception as exc:
        receipt["status"] = "ERROR"
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        (root / "error.txt").write_text(traceback.format_exc(), encoding="utf-8")
    receipt["total_seconds"] = perf_counter() - started
    write_json(root / "receipt.json", receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory under runtime/")
    parser.add_argument("--seeds", nargs="+", type=int, default=[14])
    parser.add_argument("--scrambles", nargs="+", default=["identity", "17", "29"])
    parser.add_argument("--arms", nargs="+", choices=ARMS, default=list(ARMS[:3]))
    parser.add_argument("--interaction-budgets", nargs="+", type=int, default=[24_000])
    parser.add_argument("--search-budget", type=int, default=2_000)
    parser.add_argument("--level", type=int, choices=(0, 1, 2), default=2)
    args = parser.parse_args(argv)
    if not args.output.resolve().is_relative_to(Path("runtime").resolve()):
        parser.error("--output must be under runtime/")
    if args.output.exists():
        parser.error("--output must be new; existing evidence is never appended or overwritten")
    if args.search_budget < 0 or any(budget < 0 for budget in args.interaction_budgets):
        parser.error("budgets must be nonnegative")
    try:
        scrambles = [None if value == "identity" else int(value) for value in args.scrambles]
    except ValueError:
        parser.error("scrambles must be integer seeds or identity")
    configurations = list(product(args.seeds, scrambles, args.interaction_budgets, args.arms))
    if len(set(configurations)) != len(configurations):
        parser.error("duplicate case configurations")
    args.output.mkdir(parents=True)
    source_root = Path(__file__).resolve().parents[2]
    source_files = sorted((source_root / "src").rglob("*.py"))
    source_hashes = {path.relative_to(source_root).as_posix(): sha256(path) for path in source_files}
    for path in source_files:
        destination = args.output / "source" / path.relative_to(source_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
    manifest = {
        "schema": "pete.opaque-acquisition.matrix.v1",
        "python": platform.python_version(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, text=True).strip(),
        "git_status": subprocess.check_output(["git", "status", "--short"], cwd=source_root, text=True),
        "source_sha256": source_hashes,
        "source_snapshot": "source/",
        "config": {**vars(args), "output": str(args.output)},
        "planned_cases": len(configurations),
        "complete": False,
        "results": [],
    }
    write_json(args.output / "manifest.json", manifest)
    for seed, scramble, budget, arm in configurations:
        name = f"seed-{seed}_map-{scramble}_budget-{budget}_{arm}"
        receipt = run_case(args.output / name, arm=arm, seed=seed, level=args.level,
                           scramble_seed=scramble, interaction_budget=budget, search_budget=args.search_budget)
        manifest["results"].append({"directory": name,
                                    "receipt_sha256": sha256(args.output / name / "receipt.json"), **receipt})
        write_json(args.output / "manifest.json", manifest)
        print(json.dumps({"case": name, "status": receipt["status"],
                          "learning": receipt.get("learning"), "search": receipt.get("search")}), flush=True)
    manifest["complete"] = True
    write_json(args.output / "manifest.json", manifest)
    return int(any(row["status"] == "ERROR" for row in manifest["results"]))


if __name__ == "__main__":
    raise SystemExit(main())
