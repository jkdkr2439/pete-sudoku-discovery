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

## G8 - Canonical technical paper and repository publication

- Record conceptual provenance exactly: Kevin T. N. independently derived the architecture; Codex supplied technical implementation and documentation assistance.
- Separate authored mechanisms, hidden substrate rules, acquired Fieldmap knowledge, and dynamic relational weights.
- Report only repository evidence; prohibit unsupported accuracy, SOTA, general-intelligence, zero-prior, or autonomous-search-discovery claims.
- Preserve a falsification table, limitations, reproducibility protocol, and evidence ledger.
- Run the full test suite and boundary audit before publication.

## G8 result - 2026-09-14

PASS. The canonical English manuscript and architecture figure are packaged under docs/papers. Twelve tests passed in 33.11 seconds and the architecture-boundary audit returned PASS with zero violations. Publication is scoped to the current repository state.

## G9 — Scrambled-identity acquisition experiment

1. Add an opaque-ID interface whose coordinate mapping and authority checks live only in substrate.py.
2. Add a two-symbol-class pair table and a spatial-hypothesis control over the same public IDs.
3. Implement exhaustive and adaptive grouped-probe acquisition with reset/placement accounting and a strict interaction budget.
4. Adapt opaque public state to the existing Sandbox; enforce inclusive attempt limits and retain exhaustion status.
5. Add a CLI benchmark with paired seeds/mappings, all outcomes retained, source/config hashes, physical journals, model snapshots, and authoritative completion receipts under runtime/.
6. Test hidden-interface boundaries, recovery of synthetic pair constraints (including unequal-symbol conflicts), budget exhaustion, mapping invariance, and a real opaque 9x9 solve. Extend the audit to new cognitive modules.
7. Run existing/new tests, boundary audit, and a fixed local pilot. Publish a local experiment document that reports costs and failures as observed. No commit or push is authorized.

## G9 result — 2026-09-14

Implemented and evaluated. All 23 tests and the expanded boundary audit pass. The fixed 18-case pilot retained every outcome and verified each physical journal. At 24,000 interactions both pair learners solve all three representations of seed 14; the spatial control solves only the identity mapping. At 8,000 interactions neither pair learner solves. Adaptive grouping reduces queries by about 32% but costs about 10% more total interactions on scrambled mappings, so efficiency superiority is not established. Full pair tables are identical across policies within each mapping. See `docs/OPAQUE_ACQUISITION.md` and `docs/OPAQUE_CHECKPOINT.json` for the bounded result and source-bound receipts. No commit or push performed.

## G10 — Context reuse with cost-aware grouped probing

1. Add `pair_cost_aware`, preserving the exhaustive and G9 adaptive policies as controls. Place the target first and stream learned-compatible group members, using each receipt as an exact pair label.
2. Share reset/anchor cost, prioritize larger groups, and retain valid observations when an interaction budget interrupts a group. Guard against rejected actions that mutate state and anchors that cannot be placed.
3. Add synthetic tests across equality/inequality conflict densities, budget boundaries, label renamings and dense worst cases; verify the complete-acquisition N+2Q accounting and exhaustive-cost upper bound.
4. Before evaluating real worlds, fix the comparison matrix: new challenge seed 23; new opaque mapping seeds 41 and 53; budgets 12,000 and 24,000; arms pair_exhaustive, pair_adaptive and pair_cost_aware; search budget 2,000; tier 2. Retain all 12 cases and full source-bound receipts. Do not tune against this matrix after observing outcomes.
5. Run the full tests and boundary audit. Record exact costs, model equivalence, physical completion and failures in a new G10 document/checkpoint. Preserve G9 artifacts and conclusions. No commit or push.

## G10 result — 2026-09-14

Implemented and evaluated. All 30 tests, the expanded boundary audit, JavaScript syntax and diff checks pass. All 12 fixed cases were retained. On new seed 23 with mappings 41 and 53, context reuse learns complete tables and solves using 9,056 and 8,684 interactions, reducing cost by 53.4% and 55.3% versus exhaustive probing. It alone solves at the 12,000 cap; all three policies solve at 24,000. Complete learned models and search traces are identical within each mapping. The result is bounded to the stated pairwise/symmetry/non-mutating-rejection assumptions and one new puzzle under two representations. See `docs/COST_AWARE_ACQUISITION.md` and `docs/COST_AWARE_CHECKPOINT.json`. No commit or push performed.

## G11 — Bounded repair after hidden role swaps

1. Add a substrate-only role-swap operation without exposing affected IDs or a change flag through Body.
2. Add a revisable pair table with explicit old/new evidence history; preserve existing stationary learners.
3. Add a budgeted recovery controller: retained-model attempt, contradiction probes and endpoint repair, then the unchanged Sandbox and physical commitment. Compare frozen reuse and fresh G10 relearning.
4. Fix the local matrix before outcomes: warm acquisition on challenge seed 31, mapping seed 67, tier 2; hidden swap counts 0, 1 and 3 using seed 101; post-change budgets 6,000 and 12,000; frozen, relearn and repair arms; 2,000 search attempts per solve attempt; 128 compatible watchlist pairs with controller seed 0. Retain all 18 cases. Acquire the common warm model online once, snapshot it, and give each arm an independent copy of the same post-change state and warm model.
5. Test added/removed conflict revisions, contradiction localization, budget preservation, failed commitment feedback, unchanged-world behavior and the hidden transition boundary. Run all tests and audit before the fixed matrix.
6. Record post-change and lifetime costs, detection/repair status, residual model errors, source-bound receipts and journals. Distinguish successful local repair from universal change detection. No commit or push.

## G11 result — 2026-09-14

Implemented and evaluated. All 40 tests and the expanded audit pass. All 18 fixed cases were retained. After a common 9,004-interaction warm acquisition, repair solves both changed cases at a 6,000 cap while fresh relearning fails both. At 12,000, repair uses 4,487 versus 8,890 interactions after one swap and 7,466 versus 8,878 after three. All repaired models match all 6,480 authority checks, with 72 and 214 revisions respectively. At three swaps and the lower cap, recovery solves despite `REPAIR_BUDGET_STOP`; the finite watchlist did not finish, and full correctness is a subsequent evaluator finding. No-change controls trigger no extra work. See `docs/RULE_CHANGE_RECOVERY.md` and `docs/RULE_CHANGE_CHECKPOINT.json` for source-bound receipts and scope limits. No commit or push performed.

## G12 — Archive retrieval across recurring rule networks

1. Add an immutable, prediction-deduplicated archive of online learned pair models and a controller using public-given contradictions, disagreement probes (maximum 32), and 128 sampled verification probes. Require complete pair coverage for retrieval eligibility; retain provenance without claiming global validity.
2. Reuse G11 repair and the unchanged Sandbox; enforce a shared per-phase budget for retrieval, verification, repair and commitment. Measure archive serialized bytes, selection CPU, selected-model errors after execution, and authoritative task outcomes.
3. Add a sequential experiment CLI with one common warm A model, independent arms, and continuous per-arm models/journals. Fix the pilot before results: tier 2, puzzle seed 43, initial mapping 79, B swap seed 113 with severity 1 and 3, return to A by repeating the same swaps, C three swaps with seed 227, phase budget 12,000, search budget 2,000 per attempt, retrieval seed 0. Three arms (fresh, repair, memory), two severities, three post-warm phases = 18 phase receipts. Retain all outcomes without tuning to results.
4. Test retrieval on recurrence, unfamiliar-model rejection and fallback, archive isolation/deduplication, budget exhaustion, evidence boundaries and finite-verification false reuse. Extend the static authority audit, then run full tests and audit before the pilot.
5. Save source snapshots, hash-chained journals, model/archive snapshots, traces, phase/lifetime costs and a reproducible checkpoint under runtime/. Report task success separately from full pair-table correctness. No commit or push.

## G12 result — 2026-09-14

Implemented and evaluated. All 50 tests pass in 51.892 seconds, the seven-file boundary audit passes, and independent receipt verification passes for all six sequences/18 phases. All phases solve and all final models match 6,480 authority checks. Common online warm acquisition costs 8,784 interactions. Returning A costs 436 with memory versus 4,481/6,743 with current-model repair and 8,836 with fresh learning. Full lifetime costs are 21,503/23,762 with memory versus 25,230/29,751 with repair. Unfamiliar C rejects a plausible archive entry after 105 probes and costs 318 more than repair alone. Only two archive selections occur, both subsequently verified correct; candidate-disagreement probing is not needed in the real pilot. See `docs/MODEL_MEMORY.md` and `docs/MODEL_MEMORY_CHECKPOINT.json`. No commit or push performed.
