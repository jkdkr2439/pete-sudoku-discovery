# Pete Sudoku Discovery

A standalone experiment testing one claim: **a rule-governed substrate can be the authoritative world from which an agent constructs a usable internal model through interaction.**

The repository contains no LLM, pretrained weights, training corpus, or Sudoku rule in cognition. The substrate privately generates and enforces its world. Pete receives only board-shaped sensor packets and binary action consequences. Generic relational induction turns repeated gaps into a dynamic Fieldmap. Sandbox then searches the Fieldmap without access to the real validator, and every proposed completion must survive physical commitment back into the substrate.

## Three different things

- **Substrate** is the external rule world: hidden constraints, state transitions, life consequences, puzzle generation and independent grading.
- **Fieldmap** is Pete's dynamic internal model: evidence-weighted relation nodes collapsed from experience. It is analogous to changing weights, but remains explicit and inspectable.
- **Sandbox** is a bounded executable workspace: it uses the current Fieldmap to try possible states. It cannot ask the substrate whether a Sandbox move is correct.
- **Imagination** is the broader capacity to construct absent possibilities. In this repository it is realized by Sandbox; it is not a second solver.

## Run

```powershell
cd D:\Projects\01_Active\pete-sudoku-discovery
$env:PYTHONPATH = "src"
python -m pete_discovery.server --port 8792
```

Open http://127.0.0.1:8792/ and press **Start continuous**.

## Learning boundary

Learning is mandatory: embodied experiments continuously alter explicit Fieldmap structure and weights. Knowledge is formed and updated during Pete's lifetime. The bounded claim is **no offline task optimization, no pretrained parameter file, and no encoded Sudoku knowledge in cognition**.

## Reproduce

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python tools/audit_boundaries.py
# Optional proof-video dependencies: pip install -e ".[proof]"
```

## Evidence artifacts

- `docs/STRUCTURAL_REACTION_MEMORY.md`: formal dynamic-data definition.
- `docs/VIDEO_PROOF_PROTOCOL.md`: clean-start recording protocol.
- `artifacts/proof/PETE_9X9_EMPTY_TO_SOLVED_20260914.mp4`: recorded run.
- `artifacts/proof/PETE_9X9_EMPTY_TO_SOLVED_20260914.manifest.json`: machine-readable provenance and timeline.
- `artifacts/proof/PETE_SANDBOX_TRACE_G6_20260914.jsonl`: one complete BEGIN-to-COMPLETE Sandbox trace.
- `artifacts/proof/PETE_SANDBOX_TRACE_G6_20260914.manifest.json`: trace count, result and SHA-256.

## Continuous play

One Start keeps the scheduler active. After each authoritative SOLVED receipt, the substrate creates the next 9x9 puzzle and Fieldmap is retained. Three clue tiers are followed by unlimited hardest-tier worlds across new seeds. Pause stops after the current world reaches a safe boundary.

## Scrambled-identity acquisition experiment

A separate CLI compares the original spatial hypotheses with exhaustive and adaptive
pairwise learners behind a substrate-owned cell permutation. All arms use the same
Sandbox search. The pairwise learners assume pairwise constraints and symbol-renaming
symmetry, but receive no physical coordinates. See
[`docs/OPAQUE_ACQUISITION.md`](docs/OPAQUE_ACQUISITION.md) for assumptions, budgets,
reproduction commands and measured results.

The follow-up [`docs/COST_AWARE_ACQUISITION.md`](docs/COST_AWARE_ACQUISITION.md)
adds `pair_cost_aware`, which reuses compatible contexts and learns from each
placement receipt. It compares actual reset-plus-placement cost with the G9 controls.

[`docs/RULE_CHANGE_RECOVERY.md`](docs/RULE_CHANGE_RECOVERY.md) tests failure-triggered
repair after hidden cell-role changes, comparing retained-model reuse, fresh
relearning and targeted revision with full post-transition cost accounting.

[`docs/MODEL_MEMORY.md`](docs/MODEL_MEMORY.md) adds an archive of online-learned rule
models and tests A → B → A → C recurrence against fresh learning and current-model
repair, including retrieval costs, unfamiliar-world fallback and storage.
