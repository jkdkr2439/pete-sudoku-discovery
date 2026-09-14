"""Paired recovery experiment with one common, online-acquired warm model."""
from __future__ import annotations

import argparse
from copy import deepcopy
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
from .opaque_experiment import sha256, verify_journal, write_json
from .pairmap import RevisablePairwiseFieldmap
from .recovery import RecoveryController
from .substrate import OpaqueSudokuSubstrate


def evaluate(world, model, previous=None):
    public = world.observe()
    correct = 0
    changed = 0
    residual_changed = 0
    missing = 0
    for a, b in combinations(public["cells"], 2):
        for av, bv in ((9, 9), (9, 8)):
            actual = world.hidden_pair_conflict(a, av, b, bv)
            predicted = model.predicts_conflict((a, av), (b, bv))
            correct += predicted == actual
            missing += model.known_conflict((a, av), (b, bv)) is None
            if previous is not None and previous.predicts_conflict((a, av), (b, bv)) != actual:
                changed += 1
                residual_changed += predicted != actual
    cases = len(public["cells"]) * (len(public["cells"]) - 1)
    return {"cases": cases, "correct": correct, "mismatches": cases - correct,
            "unknown_pair_classes": missing, "changed_pair_classes": changed if previous is not None else None,
            "residual_changed_pair_errors": residual_changed if previous is not None else None}


def run_branch(root, base_world, warm_model, warm_receipt, *, policy, swaps, swap_seed,
               budget, search_budget, compatible_checks, watch_seed):
    root.mkdir(parents=True, exist_ok=False)
    config = {"policy": policy, "swaps": swaps, "swap_seed": swap_seed, "budget": budget,
              "search_budget": search_budget, "compatible_checks": compatible_checks, "watch_seed": watch_seed}
    write_json(root / "config.json", config)
    receipt = {"config": config, "status": "ERROR"}
    started = perf_counter()
    controller = None
    world = None
    journal = None
    try:
        world = deepcopy(base_world)
        world.change_roles(swaps=swaps, seed=swap_seed)
        start_actions = world.action_index
        model = deepcopy(warm_model)
        journal = HashJournal(root / "physical-journal.jsonl")
        journal.append("experiment.parent", {"warm_model_sha256": warm_receipt["model_sha256"],
                                             "warm_journal_head": warm_receipt["journal"]["head"]})
        journal.append("experiment.initial", world.observe())
        body = Body(world, journal)
        trace_path = root / "sandbox-trace.jsonl"
        with trace_path.open("w", encoding="utf-8", newline="\n") as trace:
            attempt = 0
            def observe(state):
                nonlocal attempt
                if state["operation"] == "BEGIN":
                    attempt += 1
                trace.write(json.dumps({"attempt": attempt, **state}, separators=(",", ":")) + "\n")
            controller = RecoveryController(body, model, interaction_budget=budget,
                                            search_budget=search_budget, compatible_checks=compatible_checks,
                                            watch_seed=watch_seed, observer=observe)
            receipt.update(controller.run(policy))
        receipt["control_seconds"] = perf_counter() - started
        model = controller.model
        write_json(root / "model.json", model.snapshot())
        write_json(root / "final-observation.json", body.sense()["vision"])
        receipt["model_sha256"] = sha256(root / "model.json")
        receipt["prediction"] = evaluate(world, model, warm_model)
        if model.snapshot() != json.loads((root / "model.json").read_text(encoding="utf-8")):
            raise ValueError("EVALUATOR_MUTATED_MODEL")
        receipt["phase_placements"] = world.action_index - start_actions
        if receipt["phase_placements"] != receipt["cost"]["placements"]:
            raise ValueError("PHYSICAL_ACCOUNTING_MISMATCH")
        receipt["lifetime_interactions"] = warm_receipt["learning"]["interactions"] + receipt["cost"]["interactions"]
        receipt["journal"] = verify_journal(journal.path)
        receipt["sandbox_trace_sha256"] = sha256(trace_path)
    except Exception as exc:
        receipt["status"] = "ERROR"
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        if controller is not None:
            receipt["cost"] = controller.body.snapshot()
        (root / "error.txt").write_text(traceback.format_exc(), encoding="utf-8")
    receipt["total_seconds"] = perf_counter() - started
    write_json(root / "receipt.json", receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=31)
    parser.add_argument("--mapping", type=int, default=67)
    parser.add_argument("--swap-seed", type=int, default=101)
    parser.add_argument("--swaps", nargs="+", type=int, default=[0, 1, 3])
    parser.add_argument("--budgets", nargs="+", type=int, default=[6000, 12000])
    parser.add_argument("--policies", nargs="+", choices=("frozen", "relearn", "repair"), default=["frozen", "relearn", "repair"])
    parser.add_argument("--search-budget", type=int, default=2000)
    parser.add_argument("--compatible-checks", type=int, default=128)
    parser.add_argument("--watch-seed", type=int, default=0)
    args = parser.parse_args(argv)
    if not args.output.resolve().is_relative_to(Path("runtime").resolve()) or args.output.exists():
        parser.error("output must be a new directory under runtime/")
    if any(n < 0 or n > 40 for n in args.swaps) or any(n < 0 for n in args.budgets):
        parser.error("invalid swap count or budget")
    if args.search_budget < 0 or args.compatible_checks < 0:
        parser.error("negative search budget or compatible-check count")
    configurations = list(product(args.swaps, args.budgets, args.policies))
    if len(set(configurations)) != len(configurations):
        parser.error("duplicate configurations")
    args.output.mkdir(parents=True)
    source_root = Path(__file__).resolve().parents[2]
    source_hashes = {}
    for path in sorted((source_root / "src").rglob("*.py")):
        relative = path.relative_to(source_root)
        source_hashes[relative.as_posix()] = sha256(path)
        destination = args.output / "source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
    manifest = {"schema": "pete.recovery.matrix.v1", "python": platform.python_version(),
                "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, text=True).strip(),
                "git_status": subprocess.check_output(["git", "status", "--short"], cwd=source_root, text=True),
                "source_sha256": source_hashes, "source_snapshot": "source/",
                "config": {**vars(args), "output": str(args.output)}, "planned_cases": len(configurations),
                "complete": False, "results": []}
    write_json(args.output / "manifest.json", manifest)
    warm_root = args.output / "warm"
    warm_root.mkdir()
    world = OpaqueSudokuSubstrate(seed=args.seed, level=2, scramble_seed=args.mapping)
    journal = HashJournal(warm_root / "physical-journal.jsonl")
    journal.append("experiment.initial", world.observe())
    model = RevisablePairwiseFieldmap()
    tick = perf_counter()
    warm_learning = Acquisition(Body(world, journal), model, interaction_budget=24000).run("cost_aware")
    warm_seconds = perf_counter() - tick
    write_json(warm_root / "model.json", model.snapshot())
    warm = {"learning": warm_learning, "seconds": warm_seconds, "prediction": evaluate(world, model),
            "model_sha256": sha256(warm_root / "model.json"), "journal": verify_journal(journal.path)}
    write_json(warm_root / "receipt.json", warm)
    manifest["warm"] = warm
    write_json(args.output / "manifest.json", manifest)
    if warm_learning["status"] != "COMPLETE" or warm["prediction"]["mismatches"]:
        raise RuntimeError("WARM_MODEL_NOT_VERIFIED")
    for swaps, budget, policy in configurations:
        name = f"swaps-{swaps}_budget-{budget}_{policy}"
        receipt = run_branch(args.output / name, world, model, warm, policy=policy, swaps=swaps,
                             swap_seed=args.swap_seed, budget=budget, search_budget=args.search_budget,
                             compatible_checks=args.compatible_checks, watch_seed=args.watch_seed)
        manifest["results"].append({"directory": name, "receipt_sha256": sha256(args.output / name / "receipt.json"), **receipt})
        write_json(args.output / "manifest.json", manifest)
        print(json.dumps({"case": name, "status": receipt["status"], "cost": receipt.get("cost"),
                          "repair": receipt.get("repair"), "prediction": receipt.get("prediction")}), flush=True)
    manifest["complete"] = True
    write_json(args.output / "manifest.json", manifest)
    return int(any(r["status"] == "ERROR" for r in manifest["results"]))


if __name__ == "__main__":
    raise SystemExit(main())
