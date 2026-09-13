# Plan

## Total goal G0
Build a portable Sudoku discovery experiment that separates substrate, body, Fieldmap, sandbox, cognition, and display, then show measurable learning from interaction without training.

## Goal chain

### G0.1 — World boundary
- Implement deterministic 9x9-only puzzle generation inside the substrate.
- Expose only board, dimensions, immutable givens, action receipt, and reward/life signals.
- Checkpoint: public packets contain no solution, candidate list, constraint group, or reason.

### G0.2 — Embodied experiment channel
- Implement reset, place, and observe through a body port.
- Run controlled pair probes against the physical substrate.
- Checkpoint: every probe is hash-journaled and consumes experiment energy.

### G0.3 — Dynamic Fieldmap
- Convert pair outcomes into evidence-bearing descriptor nodes.
- Collapse a compact predictive theory only after repeated support and counterexample checks.
- Checkpoint: prediction accuracy improves from baseline on held-out interactions.

### G0.4 — Sandbox and action
- Search counterfactual boards using only collapsed Fieldmap relations.
- Commit the Sandbox completion through the body to the authoritative substrate.
- Checkpoint: sandbox has no substrate import/callback and the real world independently accepts every move.

### G0.5 — Progressive worlds and display
- Generate unlimited deterministic puzzles across increasing clue-removal tiers.
- Add Start/Pause/New controls and display the real board, Fieldmap weights, Sandbox board, journal, and proof metrics.
- Checkpoint: a clean run produces a machine-readable experiment receipt.

### G0.6 — Audit
- Run unit/integration tests and forbidden-dependency scans.
- Record current limits honestly: interaction count, scale cost, and any failed 9x9 run.
- Commit only after evidence passes.


## G0 result - 2026-09-14

All six checkpoints passed. The repository demonstrates an empty-to-predictive Fieldmap directly on 9x9 and transfer to harder unseen 9x9 puzzles without new samples. The boundary audit found no substrate authority import in cognition or sandbox. See `docs/CHECKPOINT.json` for exact evidence and limitations.

## G1 - Restrict the experiment to 9x9

- Reject every substrate dimension except 9x9.
- Make all runtime, server and tests start directly at 9x9.
- Remove every alternate grid size and its evidence.
- Preserve progressive difficulty only within 9x9.
- Re-run boundary audit, full discovery, held-out verification, authoritative solve and transfer to the next 9x9 puzzle.

## G1 result - 2026-09-14

PASS. All public entry points now create 9x9 worlds, alternate dimensions are rejected, the clean live run solved 9x9 from an empty Fieldmap, and all architecture gates passed.

## G2 - Structural reaction memory and proof recording

- Add pre-state, external input, structural mutation, gap signature and post-state to each Fieldmap assimilation.
- Aggregate recurring reaction shapes and expose gap-based retrieval.
- Display reaction counts, structure hash and retrieved resonance in the observer UI.
- Add tests proving the gap belongs to the reaction rather than the raw input.
- Reset all runtime evidence and record an end-to-end video from empty Fieldmap to authoritative 9x9 solution.
- Include code-boundary and no-training evidence in the recording and checkpoint.

## G2 result - 2026-09-14

PASS. Fieldmap data is now stored as aggregated structural reactions with gap-indexed retrieval. Nine tests pass. A clean-start 44-frame MP4 records zero initial samples, clauses and journal events, followed by 6,480 physical reactions, three collapsed clauses, 100% held-out accuracy and an authoritative 9x9 SOLVED result.

## G3 - One-start continuous play

- Split one-world execution from the persistent scheduler.
- Make /api/start launch the continuous scheduler and add /api/pause.
- Advance the substrate automatically after each SOLVED world.
- Preserve Fieldmap across worlds and expose completed-world history.
- Keep /api/start-once for the reproducible proof recorder.
- Add UI controls and tests for automatic progression and safe pause.

## G3 result - 2026-09-14

PASS. One Start solved two consecutive 9x9 worlds in the live server, automatically advanced the substrate, reused the same 6,480-sample three-clause Fieldmap without new samples, recorded both worlds, and honored Pause after the active world. Eleven tests pass.
## G4 - Sandbox identity and live source observer

- Rename the reversible counterfactual workspace from Imagination to Sandbox across code, API, tests and current documentation.
- Keep the authoritative substrate board visually dominant and render Sandbox as a smaller internal workspace.
- Add a read-only Live Code Route that resolves each runtime phase to the real file, function, line range and source text being executed.
- Checkpoint: source display cannot mutate runtime state; Sandbox remains unable to import or call substrate authority.
- Verify architecture tests, real 9x9 discovery/solve, boundary audit, Python compilation, JavaScript syntax and live HTTP endpoints.

## G4 result - 2026-09-14

PASS. Sandbox is now the concrete module and API name, its UI is subordinate to the substrate, and the observer exposes the real source route for scheduler, physical experiment, Fieldmap collapse, verification, Sandbox search, physical commit and world advance. Twelve tests pass, including a real 9x9 discovery/solve and a catalog-to-source assertion.
