"""Sequential A-B-A-C model-memory comparison; phase labels stay in this harness."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import platform
import subprocess
from time import perf_counter

from .acquisition import Acquisition
from .body import Body
from .journal import HashJournal
from .model_memory import ModelArchive, MemoryController, fresh_completion
from .opaque_experiment import sha256, verify_journal, write_json
from .pairmap import RevisablePairwiseFieldmap
from .recovery import RecoveryController
from .recovery_experiment import evaluate
from .substrate import OpaqueSudokuSubstrate


def run_sequence(root, base_world, warm_model, warm, *, policy, swaps, args):
    root.mkdir(parents=True, exist_ok=False)
    world = deepcopy(base_world)
    model = deepcopy(warm_model)
    archive = ModelArchive()
    if policy == "memory":
        archive.remember(model, world.observe()["cells"], source={"method": "online_cost_aware", "status": "COMPLETE"})
    journal = HashJournal(root / "physical-journal.jsonl")
    journal.append("experiment.parent", {"warm_model_sha256": warm["model_sha256"],
                                         "warm_journal_head": warm["journal"]["head"]})
    body = Body(world, journal)
    lifetime = warm["learning"]["interactions"]
    results = []
    # Repeating a set of disjoint swaps is an involution. No state labels enter cognition.
    for index, (label, count, seed) in enumerate((
            ("B", swaps, args.swap_seed), ("A_return", swaps, args.swap_seed),
            ("C", 3, args.novel_seed)), start=1):
        world.change_roles(swaps=count, seed=seed)
        phase_root = root / f"{index}-{label}"
        phase_root.mkdir()
        public = world.observe()
        journal.append("experiment.initial", public)
        start_actions = public["action_index"]
        tick = perf_counter()
        selected = None
        trace_path = phase_root / "sandbox-trace.jsonl"
        with trace_path.open("w", encoding="utf-8", newline="\n") as trace:
            attempt = 0
            def observe(state):
                nonlocal attempt
                if state["operation"] == "BEGIN":
                    attempt += 1
                trace.write(json.dumps({"attempt": attempt, **state}, separators=(",", ":")) + "\n")
            if policy == "fresh":
                model, report = fresh_completion(body, interaction_budget=args.budget,
                                                  search_budget=args.search_budget, observer=observe)
            elif policy == "repair":
                controller = RecoveryController(body, model, interaction_budget=args.budget,
                                                search_budget=args.search_budget, observer=observe)
                report = controller.run("repair")
                model = controller.model
            else:
                controller = MemoryController(body, model, archive, interaction_budget=args.budget,
                                              search_budget=args.search_budget, observer=observe,
                                              discrimination_limit=args.discrimination_limit,
                                              verification_checks=args.verification_checks,
                                              retrieval_seed=args.retrieval_seed)
                report = controller.run()
                model = controller.model
                selected = controller.selected_model
        report["control_seconds"] = perf_counter() - tick
        report["phase"] = label
        report["index"] = index
        report["phase_placements"] = world.action_index - start_actions
        if report["phase_placements"] != report["cost"]["placements"]:
            raise ValueError("PHYSICAL_ACCOUNTING_MISMATCH")
        lifetime += report["cost"]["interactions"]
        report["lifetime_interactions"] = lifetime
        write_json(phase_root / "model.json", model.snapshot())
        write_json(phase_root / "final-observation.json", body.sense()["vision"])
        report["model_sha256"] = sha256(phase_root / "model.json")
        report["active_model_bytes"] = len(json.dumps(model.snapshot(), sort_keys=True, separators=(",", ":")).encode())
        report["total_model_storage_bytes"] = report["active_model_bytes"] + report.get("archive_bytes", 0)
        if policy == "memory":
            # Exact compact serialization is the declared logical storage metric.
            archive_path = phase_root / "archive.json"
            archive_path.write_text(json.dumps(archive.snapshot(), sort_keys=True, separators=(",", ":")), encoding="utf-8")
            if archive_path.stat().st_size != report["archive_bytes"]:
                raise ValueError("ARCHIVE_STORAGE_ACCOUNTING_MISMATCH")
            report["archive_sha256"] = sha256(archive_path)
        if selected is not None:
            write_json(phase_root / "selected-model.json", selected.snapshot())
            report["selected_model_sha256"] = sha256(phase_root / "selected-model.json")
        # Evaluation happens after all decisions and archive admissions, with no feedback.
        before = model.snapshot(), archive.snapshot()
        report["prediction"] = evaluate(world, model)
        report["selected_prediction"] = evaluate(world, selected) if selected is not None else None
        report["incorrect_reuse"] = (report["selected_prediction"]["mismatches"] > 0
                                      if selected is not None else None)
        if before != (model.snapshot(), archive.snapshot()):
            raise ValueError("EVALUATOR_MUTATED_LEARNER")
        report["journal_prefix"] = {"head": journal.previous, "records": journal.sequence}
        report["sandbox_trace_sha256"] = sha256(trace_path)
        write_json(phase_root / "receipt.json", report)
        results.append({"directory": phase_root.name, "receipt_sha256": sha256(phase_root / "receipt.json"), **report})
        print(json.dumps({"policy": policy, "swaps": swaps, "phase": label, "status": report["status"],
                          "cost": report["cost"]["interactions"], "retrieval": report.get("retrieval"),
                          "errors": report["prediction"]["mismatches"]}), flush=True)
    receipt = {"policy": policy, "swaps": swaps, "phases": results,
               "lifetime_interactions": lifetime, "journal": verify_journal(journal.path)}
    write_json(root / "receipt.json", receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=43)
    parser.add_argument("--mapping", type=int, default=79)
    parser.add_argument("--swap-seed", type=int, default=113)
    parser.add_argument("--novel-seed", type=int, default=227)
    parser.add_argument("--swaps", nargs="+", type=int, default=[1, 3])
    parser.add_argument("--budget", type=int, default=12000)
    parser.add_argument("--search-budget", type=int, default=2000)
    parser.add_argument("--discrimination-limit", type=int, default=32)
    parser.add_argument("--verification-checks", type=int, default=128)
    parser.add_argument("--retrieval-seed", type=int, default=0)
    parser.add_argument("--policies", nargs="+", choices=("fresh", "repair", "memory"), default=["fresh", "repair", "memory"])
    args = parser.parse_args(argv)
    if not args.output.resolve().is_relative_to(Path("runtime").resolve()) or args.output.exists():
        parser.error("output must be a new directory under runtime/")
    if min(args.budget, args.search_budget, args.discrimination_limit, args.verification_checks) < 0:
        parser.error("negative budget or probe limit")
    if any(n < 1 or n > 40 for n in args.swaps):
        parser.error("swap counts must be 1..40")
    if len(set(args.swaps)) != len(args.swaps) or len(set(args.policies)) != len(args.policies):
        parser.error("duplicate configurations")
    args.output.mkdir(parents=True)
    source_root = Path(__file__).resolve().parents[2]
    hashes = {}
    for path in sorted((source_root / "src").rglob("*.py")):
        relative = path.relative_to(source_root)
        hashes[relative.as_posix()] = sha256(path)
        destination = args.output / "source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
    manifest = {"schema": "pete.memory.matrix.v1", "python": platform.python_version(),
                "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, text=True).strip(),
                "git_status": subprocess.check_output(["git", "status", "--short"], cwd=source_root, text=True),
                "source_sha256": hashes, "source_snapshot": "source/",
                "config": {**vars(args), "output": str(args.output)},
                "planned_phases": len(args.swaps) * len(args.policies) * 3,
                "complete": False, "results": []}
    write_json(args.output / "manifest.json", manifest)
    warm_root = args.output / "warm"
    warm_root.mkdir()
    world = OpaqueSudokuSubstrate(seed=args.seed, level=2, scramble_seed=args.mapping)
    journal = HashJournal(warm_root / "physical-journal.jsonl")
    journal.append("experiment.initial", world.observe())
    model = RevisablePairwiseFieldmap()
    learning = Acquisition(Body(world, journal), model, interaction_budget=24000).run("cost_aware")
    write_json(warm_root / "model.json", model.snapshot())
    warm = {"learning": learning, "model_sha256": sha256(warm_root / "model.json"),
            "journal": verify_journal(journal.path)}
    # Only observable completion of acquisition gates the experiment, never authority accuracy.
    if learning["status"] != "COMPLETE":
        raise RuntimeError("WARM_ACQUISITION_INCOMPLETE")
    warm["prediction"] = evaluate(world, model)
    write_json(warm_root / "receipt.json", warm)
    manifest["warm"] = warm
    write_json(args.output / "manifest.json", manifest)
    for swaps in args.swaps:
        for policy in args.policies:
            name = f"swaps-{swaps}_{policy}"
            receipt = run_sequence(args.output / name, world, model, warm, policy=policy, swaps=swaps, args=args)
            manifest["results"].append({"directory": name, "receipt_sha256": sha256(args.output / name / "receipt.json"), **receipt})
            write_json(args.output / "manifest.json", manifest)
    manifest["complete"] = True
    write_json(args.output / "manifest.json", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
