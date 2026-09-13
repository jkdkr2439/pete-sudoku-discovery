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

## What "no training" means here

There is no offline optimization stage and no fixed learned parameter file. Pete still learns during its lifetime: embodied experiments alter explicit Fieldmap weights. Calling that process "no learning" would be false; the claim is **no prior task training and no encoded Sudoku knowledge in cognition**.

## Reproduce

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python tools/audit_boundaries.py
```

## Evidence artifacts

- `docs/STRUCTURAL_REACTION_MEMORY.md`: formal dynamic-data definition.
- `docs/VIDEO_PROOF_PROTOCOL.md`: clean-start recording protocol.
- `artifacts/proof/PETE_9X9_EMPTY_TO_SOLVED_20260914.mp4`: recorded run.
- `artifacts/proof/PETE_9X9_EMPTY_TO_SOLVED_20260914.manifest.json`: machine-readable provenance and timeline.

## Continuous play

One Start keeps the scheduler active. After each authoritative SOLVED receipt, the substrate creates the next 9x9 puzzle and Fieldmap is retained. Three clue tiers are followed by unlimited hardest-tier worlds across new seeds. Pause stops after the current world reaches a safe boundary.
