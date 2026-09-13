# Plan

## Total goal G0
Build a portable Sudoku discovery experiment that separates substrate, body, Fieldmap, sandbox, cognition, and display, then show measurable online structural learning without offline task optimization or preloaded Sudoku knowledge.

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
- Include code-boundary and learning-boundary evidence in the recording and checkpoint.

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

## G5 - Pete design-engine UI refinement

### Parent goal
Make the observer surface readable as a scientific instrument: the user should immediately see the authoritative world, the small Sandbox, the current cognitive route and the evidence produced by the loop.

### Fractal design loop
1. Observe the rendered UI and record hierarchy, density and legibility gaps.
2. Generate alternatives inside the design Sandbox.
3. Collapse one layout using explicit metrics: first-glance hierarchy, phase visibility, source traceability, board legibility and viewport use.
4. Render at 1600 x 1300, inspect the artifact and measure element bounds.
5. Feed the remaining gap into the next loop.

### Checkpoints
- Loop 1: hierarchy and viewport economy.
- Loop 2: phase/process observability and component identity.
- Loop 3: spacing, contrast, responsive behavior and final visual QA.
- Preserve architecture boundaries and runtime behavior.
## G5 result - 2026-09-14

PASS after three render loops. The observer now behaves as one laboratory console: compact runtime identity, live IPOD phase rail, dense evidence strip, dominant authoritative board, small Sandbox, adjacent real-source route, dynamic Fieldmap clauses and event journal. Desktop renders at 1600 x 1300 and 1280 x 900 preserve hierarchy and avoid horizontal overflow.

## G6 - Observable Sandbox execution

### Architectural distinction
- Imagination is Pete's broad capacity to construct and compare absent possibilities.
- Sandbox is the bounded executable workspace currently used to realize one form of imagination.
- There is one concrete Sandbox engine in this experiment; Imagination is not a second hidden solver.

### Goal chain
1. Convert synchronous final-only Sandbox output into observable structural steps.
2. Expose BEGIN, SCAN, TRY, BACKTRACK and COMPLETE with partial board state.
3. Pace only the observer server; keep tests and core computation unthrottled.
4. Highlight the active cell, operation, code-like instruction and matching source line.
5. Verify that trace output does not import or query substrate authority.
## G6 result - 2026-09-14

PASS. Sandbox now exposes BEGIN, SCAN, TRY, BACKTRACK and COMPLETE transformations with partial board snapshots, active cells, candidate sets, instructions and matching source focus. The observer server paces only the first 160 display steps; core tests run without delay. Every transformation is persisted to runtime/logs/sandbox-trace.jsonl. A live 9x9 run exposed 179 states and 76 tries before authoritative SOLVED.
## G7 - Repository cleanup and portability

- Pause continuous execution at a safe world boundary and stop the server before cleanup.
- Preserve one complete G6 Sandbox trace with a SHA-256 manifest.
- Remove runtime repetition, browser QA profiles, Python caches, pytest cache and locally vendored binaries.
- Declare proof-video packages as optional project dependencies instead of storing an ignored 84 MB vendor tree.
- Restart from the tracked launcher and verify the clean repository can regenerate runtime state.
## G7 result - 2026-09-14

PASS. Cleanup removed 269.5 MB of regenerated runtime, browser profiles, caches and vendored ffmpeg. A 45 KB complete Sandbox trace plus SHA-256 manifest preserves the new G6 evidence. Proof dependencies are optional package metadata, tests run without writing caches, and START_UI disables Python bytecode generation.
