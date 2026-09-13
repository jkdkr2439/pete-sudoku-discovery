# Plan

## Total goal G0
Build a portable Sudoku discovery experiment that separates substrate, body, Fieldmap, imagination, cognition, and display, then show measurable learning from interaction without training.

## Goal chain

### G0.1 — World boundary
- Implement deterministic 4x4 and 9x9 puzzle generation inside the substrate.
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

All six checkpoints passed. The repository demonstrates an empty-to-predictive Fieldmap on 4x4, transfer to a harder new puzzle without new samples, and unchanged cognition scaling to 9x9. The boundary audit found no substrate authority import in cognition or imagination. See `docs/CHECKPOINT.json` for exact evidence and limitations.
