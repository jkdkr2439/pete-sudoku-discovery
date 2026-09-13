# Plan

## Total goal G0
Build a portable Sudoku discovery experiment that separates substrate, body, Fieldmap, imagination, cognition, and display, then show measurable learning from interaction without training.

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

### G0.4 — Imagination and action
- Search counterfactual boards using only collapsed Fieldmap relations.
- Commit the imagined completion through the body to the authoritative substrate.
- Checkpoint: imagination has no substrate import/callback and the real world independently accepts every move.

### G0.5 — Progressive worlds and display
- Generate unlimited deterministic puzzles across increasing clue-removal tiers.
- Add Start/Pause/New controls and display the real board, Fieldmap weights, imagined board, journal, and proof metrics.
- Checkpoint: a clean run produces a machine-readable experiment receipt.

### G0.6 — Audit
- Run unit/integration tests and forbidden-dependency scans.
- Record current limits honestly: interaction count, scale cost, and any failed 9x9 run.
- Commit only after evidence passes.


## G0 result - 2026-09-14

All six checkpoints passed. The repository demonstrates an empty-to-predictive Fieldmap directly on 9x9 and transfer to harder unseen 9x9 puzzles without new samples. The boundary audit found no substrate authority import in cognition or imagination. See `docs/CHECKPOINT.json` for exact evidence and limitations.

## G1 - Restrict the experiment to 9x9

- Reject every substrate dimension except 9x9.
- Make all runtime, server and tests start directly at 9x9.
- Remove every alternate grid size and its evidence.
- Preserve progressive difficulty only within 9x9.
- Re-run boundary audit, full discovery, held-out verification, authoritative solve and transfer to the next 9x9 puzzle.

## G1 result - 2026-09-14

PASS. All public entry points now create 9x9 worlds, alternate dimensions are rejected, the clean live run solved 9x9 from an empty Fieldmap, and all architecture gates passed.
