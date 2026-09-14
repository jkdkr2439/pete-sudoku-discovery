# Pete Sudoku Discovery

A standalone experiment testing one claim: **a rule-governed substrate can be the authoritative world from which an agent constructs a usable internal model through interaction.**

The repository contains no LLM, pretrained weights, or training corpus. The substrate privately generates and enforces Sudoku rules. The original demo learns which authored spatial hypotheses explain action feedback; the newer experiments learn pair relations over opaque cell IDs, repair changed relations, and retrieve previously learned models. All use a supplied bounded backtracking Sandbox without access to the real validator. Every proposed completion must survive physical commitment back into the substrate.

## Latest findings — 2026-09-14

The acquisition, recovery and memory extensions are available through separate
experimental CLIs. The continuous-play UI still uses the original learner.
An **interaction** is one reset or one attempted placement, including rejected moves.

| Stage | Measured finding in its fixed pilot |
|---|---|
| [Opaque-ID acquisition (G9)](docs/OPAQUE_ACQUISITION.md) | At a 24,000-interaction cap, pair learners solve all three mappings; the original spatial control solves only the identity mapping. Grouped probing reduces queries but increases total cost by about 10% on scrambled mappings. |
| [Cost-aware acquisition (G10)](docs/COST_AWARE_ACQUISITION.md) | Reusing compatible contexts learns the same complete models with **53.4–55.3% fewer interactions** than exhaustive probing. |
| [Rule-change recovery (G11)](docs/RULE_CHANGE_RECOVERY.md) | Targeted repair solves both changed cases within 6,000 interactions, where fresh relearning fails both. At the higher cap, repair saves **15.9–49.5%** of post-change interactions. |
| [Model memory (G12)](docs/MODEL_MEMORY.md) | In **A → B → A → C**, returning to A costs **436 interactions**, versus 4,481–6,743 for current-model repair and 8,836 for fresh learning. Including initial acquisition and every phase, memory saves **14.8–20.1%** versus repair. |

Memory has a measured cost on unfamiliar rules: C requires **318 more interactions**
than repair alone to check and reject a plausible archived model before recovery.
The memory pilot completed **18/18 phases**, with every final model matching all
**6,480 pair-class checks**. Each memory arm ends with three archived models; archive
plus active model occupies about **2.06–2.08 MiB** of compact JSON.

These are bounded pilots within one rule family. The pair learners assume deterministic
pairwise constraints and symbol-renaming symmetry; model structure, probe policies,
retrieval and search algorithms are authored. In G12, public givens narrowed the
archive without needing disagreement probes. Sampled verification and a successful
solve can still miss changed rules, as a negative test demonstrates. This establishes
utility for exact rule recurrence, not general transfer or autonomous algorithm invention.

The latest implementation passed **50 tests**, the architecture-boundary audit and
an independent receipt audit. Reports linked above include configurations, failures,
limitations and reproduction commands. [The G12 checkpoint](docs/MODEL_MEMORY_CHECKPOINT.json)
binds results to source and artifact hashes. Full journals and source snapshots remain
in ignored local `runtime/` directories; the reports and checkpoints are committed.

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

## Run the memory experiment

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m pete_discovery.memory_experiment --output runtime/memory-reproduction
```

Or in Bash:

```bash
PYTHONPATH=src python -m pete_discovery.memory_experiment --output runtime/memory-reproduction
```

The output must be a new directory under `runtime/`. Defaults reproduce the fixed
six-sequence, 18-phase comparison. See the [memory report](docs/MODEL_MEMORY.md)
for the mechanism, budgets and artifact layout, and the other reports above for
acquisition and recovery commands.
