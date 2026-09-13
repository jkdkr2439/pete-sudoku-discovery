# AGENTS.md

## Intent
This repository is a standalone falsifiable experiment: can an agent construct a usable world model of Sudoku from embodied interaction without pretrained weights, a puzzle corpus, or Sudoku rules in cognition?

## Boundaries
1. `substrate.py` alone owns hidden world rules, generation, validation, and ground-truth solutions.
2. Public observations never expose constraint groups, rejection reasons, candidates, or solutions.
3. Body code only senses, transduces, and commits actions.
4. Fieldmap stores evidence-weighted relations learned from interaction.
5. Imagination may consult only the public observation and Fieldmap; it must never call or import the substrate.
6. Cognition must not encode Sudoku-specific row, column, block, candidate, or solving rules.
7. All cognitive progress is online lifetime learning. No pretrained model, learned weights, LLM, or external dataset is allowed.
8. Append every physical probe and committed move to a hash-chained journal.
9. Keep runtime artifacts under `runtime/`.

## Work discipline
Update `docs/BRAINSTORM.md` and `docs/PLAN.md` before implementation. Every checkpoint must include tests, an architecture-boundary audit, and a reproducible experiment receipt.
