# Paper construction plan — 2026-09-14

## Parent goal

Provide a repository-backed, falsifiable technical account of Pete's structural Sudoku experiment without inflating the evidence.

## Claim boundary

The paper may claim only what the repository, tests, journals, and archived traces demonstrate.

- Pete uses no language model, pretrained parameter checkpoint, or offline task-training dataset.
- Sudoku constraints are hidden in the substrate and are not encoded in cognition.
- Interaction updates explicit relation evidence and dynamic Fieldmap weights during the run.
- A generic bounded Sandbox search uses the learned Fieldmap and is therefore an architectural prior, not discovered Sudoku knowledge.
- The present artifact demonstrates one 9 x 9 task family. It does not establish task-agnostic intelligence, neural-model superiority, or state-of-the-art accuracy.

## Work chain

1. Inventory the executable boundary and name every authored prior.
2. Separate substrate, body, Fieldmap, memory, Sandbox, controller, display, and journal.
3. State the mechanism with implementation-linked definitions.
4. Report only archived observations and reproducible tests.
5. List falsifiers, limitations, and ablations required for stronger claims.
6. Package the manuscript and architecture figure in the repository.

## Acceptance checkpoint

- Every strong claim has a repository path or recorded artifact.
- "No training" is replaced by the precise phrase "no offline parameter optimization"; online learning is explicit.
- Hard-coded mechanisms, learned knowledge, hidden world rules, and display-only code are distinguished.
- Results include run identity and raw counts, not selected accuracy percentages.
- The manuscript contains reproducibility steps and threats to validity.

