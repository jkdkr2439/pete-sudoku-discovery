# Brainstorm

## 2026-09-14 — G0: isolate the claim

### Parent goal
Demonstrate that a rule-governed substrate can serve as a world model from which Pete constructs usable knowledge through interaction, without offline training or Sudoku knowledge in cognition.

### Distinct layers
- **Substrate:** authoritative external state, hidden constraints, consequences, puzzle generation, difficulty progression.
- **Body:** finite sensor and actuator channels. It transports signals but does not interpret Sudoku.
- **Fieldmap:** dynamic, evidence-bearing internal relations. These are the agent's changing weights.
- **Sandbox:** counterfactual workspace using only Fieldmap predictions; mistakes here do not touch substrate state.
- **Cognition:** generic experiment selection, relational description induction, goal selection, and collapse.
- **Display:** observer-only evidence surface.

### Anti-cheating criterion
Success is invalid if cognition imports the substrate, receives a hidden solution/rejection reason, contains named Sudoku constraints, or calls the real validator from sandbox. A hidden substrate solver may exist solely to generate unique worlds and grade completion.

### Learning mechanism
Use controlled two-token physical experiments. Describe each pair using a generic relation vocabulary generated from observed integer coordinates and values: equality, inequality, and equal quotient buckets over possible scales. Accepted/rejected outcomes update Fieldmap weights. A greedy evidence cover may collapse recurring descriptors into a predictive constraint theory. This is generic relation induction; no descriptor is labeled as a Sudoku row, column, or block.

### Falsifiable outputs
1. Empty Fieldmap cannot predict hidden legality above chance.
2. Physical probes change Fieldmap evidence and prediction accuracy.
3. Sandbox can find a completion using only the learned Fieldmap.
4. The completion survives authoritative substrate commits.
5. The same mechanism transfers across unseen 9x9 worlds and increasing clue-removal tiers without a cognition code change.

## 2026-09-14 - G1: one world scale only

The experiment is restricted to Sudoku 9x9. Smaller grids are removed so successful evidence cannot be attributed to a toy-scale curriculum. Difficulty changes only through clue removal and seeds; cognition and its empty-start condition remain unchanged.

## 2026-09-14 - G2: data as structural reaction

An external signal is not the stored data. The system transition it causes is the data: S(t) --input--> S(t+1). The gap is a measured component of that reaction, containing prediction mismatch and structural mutations. Retrieval therefore resonates against gap signatures and affected relations rather than fetching a raw input record. Identical reactions are aggregated to keep memory bounded.

## 2026-09-14 - G3: continuous world progression

The observer Start action must activate an ongoing world loop, not one episode. After an authoritative SOLVED receipt, the substrate advances to the next 9x9 world while Fieldmap persists. The first seed ramps through three clue tiers; subsequent seeds provide unlimited hardest-tier worlds. Pause requests stop at a safe world boundary.
## 2026-09-14 - G4: Sandbox is small; execution is inspectable

Sandbox names a bounded, reversible internal trial space. It is a component of Pete's broader capacity to imagine, not a synonym for all imagination. The substrate remains the authoritative world and therefore owns the dominant display area.

Event names alone do not show what executes. The observer needs a phase-to-source route with the actual repository file, callable, line interval and source body. This view is read-only display data: it observes runtime selection but cannot feed source or hidden substrate state into cognition.

## 2026-09-14 - G5: design is a measured collapse

The current interface is correct but visually diffuse. The headline consumes too much first-screen space, the three architecture cards repeat prose without showing live process state, and the strongest visual contrast belongs to static typography rather than the running system. The authoritative board is correctly dominant; Sandbox is correctly smaller; Live Code Route is useful but appears as a detached card.

Candidate collapse: turn the page into one coherent laboratory console. Use a compact identity header, a live phase rail, one large authoritative world panel and one instrument column containing Sandbox and current source. Preserve the warm paper palette while using dark navy only where source code and runtime focus require it.

## 2026-09-14 - G6: imagination capacity versus Sandbox mechanism

Imagination and Sandbox are different abstraction levels. Imagination names a general cognitive capacity: construct possibilities that are not presently committed to the external world. Sandbox names a concrete bounded mechanism: clone a public state, apply reversible transformations, compare them with the learned Fieldmap and discard failed branches.

The current system contains one Sandbox implementation and no second Imagination engine. The apparent instant solve is an observer-resolution failure: recursive search completes between 400 ms UI polls. The correction is to expose transformation events and partial structures, not to pretend a second cognitive module exists.

## G6 observer gap found during live capture

The first live screenshot captured a partial board, active-cell highlight and TRY instruction, but the source viewer scrolled below the focused assignment. The cause was a document-relative offset applied to the code panel scroll container. The offset is now normalized against the code element, keeping the actual matching source line in view.

## G6 live verification

A clean server run produced 64 observable Sandbox states for 31 tries. The snapshot reported 64 steps, exactly 64 new JSONL records were appended, and the final record was COMPLETE with instruction return True. The substrate then reported SOLVED with no runtime error.

## 2026-09-14 - G8: independent conceptual provenance and bounded claims

The paper records the author's declaration that Kevin T. N. derived the conceptual architecture through first-principles reasoning without using an existing AI architecture as a design reference. Codex is disclosed as technical assistance for implementation, organization, testing, tracing, interface construction, and documentation. This origin statement is separate from novelty claims about ordinary programming primitives.

The public claim must distinguish the mechanism available before a run from knowledge formed during a run. Pete has no pretrained neural tensor or task checkpoint. Fieldmap nevertheless acquires explicit dynamic relation weights online. The body interface, experiment scheduler, update/collapse operators, and generic Sandbox backtracking are authored mechanisms. The hidden Sudoku validator remains substrate law and is inaccessible to cognition.

## 2026-09-14 — G9: acquisition without spatial descriptors

The first extension tests coordinate dependence rather than adding architecture terminology. A substrate-owned permutation exposes opaque cell IDs and hides physical coordinates. The existing spatial hypothesis family becomes a control using an arbitrary display embedding; a new table records pairwise equal/different-symbol compatibility without spatial descriptors. Both learners retain an explicit symbol-permutation-symmetry prior; pairwise sufficiency, deterministic feedback, and resettable experiments are also assumptions. This is not arbitrary relation invention.

An adaptive learner maintains compatible groups from observed evidence. It tests a new cell against a group, infers compatible pairs from acceptance, and recursively splits rejected groups until conflicts are isolated. Both equal and unequal symbol classes are queried. Compared with exhaustive two-class pair probing, group tests can reduce resets but may increase placements. Measure both and enforce a combined reset-plus-placement budget. Unknown pairs remain explicitly unknown and are optimistically allowed in search; only substrate admission counts as success.

All arms use the existing Sandbox through a public-ID adapter, with the same value and variable order. Correct the identified attempt-limit defects so bounded failures remain comparable. Preserve the original observer/demo. No general transfer, adaptive rule-change recovery, or memory-benefit claim is included in this stage.

## G9 evidence update

Removing physical coordinates is feasible under the explicit pairwise/symbol-symmetry prior: both new learners recover complete tables and solve scrambled representations with the shared search. Adaptive grouping has a mixed cost profile. Fewer queries alone would have been misleading: the extra context placements increase total interaction cost by roughly 10% on the scrambled pilot mappings. Future selection should optimize the priced action/reset cost and preserve a direct-probe baseline. The current experiment establishes representation independence within one rule family; it does not establish representation invention, task transfer, or memory utility.

## 2026-09-14 — G10: price the actual action interface

G9's grouped rejection-and-splitting policy discards useful sequential action feedback. The substrate rejects an invalid placement without changing the board. A new policy can place a target first, then stream members of an already learned compatible group. The group's members cannot conflict with each other; consequently each member's binary receipt identifies its relation with the target, regardless of which previous members were accepted. Rejected members leave no residue. Test equal and unequal symbol classes in separate episodes.

This replaces repeated group setup/splitting with context reuse. Every tested member yields one exact pair-class label, while one reset and one anchor placement are shared across the group. Larger known-compatible groups are tested first to amortize these two overhead actions under a budget. Group construction remains learned and spatially blind. New explicit interface assumption: a rejected action leaves state unchanged. If context or anchor validity fails, abort without inventing pair evidence.

For complete acquisition from an empty model, N pair-class labels and Q episodes cost N+Q placements and Q resets, or N+2Q interactions. Since every episode tests at least one member, Q <= N, so cost is at most the exhaustive baseline's 3N under these assumptions. This is a cost bound for this supplied policy/interface, not a general active-learning lower bound or an invented representation.

## G10 evidence update

Context reuse resolves G9's measured cost weakness on the fixed new matrix: total interactions fall by 53–55% versus direct exhaustive probing, with identical complete models and search traces. The gain comes from respecting the already available sequential action interface: individual receipts label pairs while reset and anchor costs are amortized. This is an authored algorithmic improvement, not evidence of self-invented inquiry or general cognition. The next scientific boundaries remain richer rule families, changed laws and experience transfer; this stage does not test them.

## 2026-09-14 — G11: repair after hidden role changes

The next boundary is reuse after the relation network changes. Start with controlled hidden cell-role swaps: the substrate changes its private ID-to-position map and restores the challenge, retaining the same public IDs and world ID. This adds and removes incident conflict relations without introducing an unsatisfiable puzzle. It remains the Sudoku pair-rule family, not a novel higher-order domain.

Each arm first tries the retained model against the new public challenge. A failed search or physical rejection triggers either no repair (frozen), fresh G10 acquisition (relearn), or targeted repair. Repair checks pairs implicated by a rejected commitment or incompatible givens, then a fixed watchlist of previously conflicting pairs plus 128 previously compatible pairs. A directly observed contradiction causes isolated probes of both endpoints' incident pair classes. Do not recursively expand from every changed neighbor; resume the finite watchlist. Old compatible contexts cannot be trusted after a change, so repair uses isolated probes rather than G10 context reuse.

Retain revision history and replace only directly contradicted current labels under a noiseless, stable-within-phase assumption. Track which retained labels were actually revalidated. A finite watchlist cannot certify the entire new model or detect every possible change; the evaluator checks residual errors only after the controller finishes. Count initial failed attempts, all resets, probes and final commitments inside the post-change budget. Warm acquisition is a separately reported common cost, never a free pretrained model.

## G11 evidence update

Local repair has a measurable benefit in the fixed role-swap experiment: it preserves correct prior relations and repairs all 72/214 changed labels under a cap that prevents successful fresh reacquisition. The benefit shrinks as more incident neighborhoods need checking. At the three-swap lower cap all changes were repaired before the watchlist finished; the higher cap spent 1,467 more interactions checking unchanged labels. The agent lacks a justified stopping certificate, and successful task execution can leave other changed rules unobserved. Further work should keep task success, model validity and detection coverage distinct rather than treating any one as all three.

## 2026-09-14 — G12: retrieve previously learned rule models

Store immutable copies of learned pair tables, deduplicated by their predictions, with online provenance and task outcome. Do not store puzzle solutions, board fingerprints, world IDs, or authority-derived validity labels. A successful solve permits archiving a complete table but does not certify its retained labels. Archive IDs are local content hashes, not environment labels.

At each task boundary, filter archived candidates against public givens, probe pair classes on which candidates disagree, and check a fixed random sample of a surviving candidate's labels. Finite verification cannot distinguish every unfamiliar world from a remembered one. If candidates are contradicted, use current-model repair; if a selected model fails execution, repair it. Count retrieval resets/placements, verification, failures and repairs. Retain a negative test where unobserved changes survive verification and a task succeeds with a stale model.

Use a sequential A → B → A → C experiment: one online warm acquisition of A, a hidden role swap to B, the same involution back to A, then independent swaps to unfamiliar C. Controllers receive neither phase labels nor transition parameters. Compare fresh learning on each subsequent task, current-model-only repair, and archive retrieval plus repair. The public challenge repeats on returning A; memory stores only rule tables and selection uses pair predictions, not challenge identity. This tests exact recurrence in one rule family, not semantic similarity, arbitrary transfer or learned retrieval policy.

## G12 evidence update

Archive reuse cuts the return-to-A cost to 436 interactions, compared with 4,481/6,743 for latest-model repair and 8,836 for fresh learning. Including warm acquisition and all B/A/C work, savings versus repair are 14.8%/20.1%. Unfamiliar C costs 318 extra interactions: a surviving A candidate needs 105 verification probes before rejection and repair. All 18 tasks solve with fully correct final tables under the subsequent evaluator. Public givens alone narrow the archive in this pilot; disagreement probing is exercised only in synthetic tests. Three archived models plus the active table cost about 2.06–2.08 MiB of compact JSON. The evidence supports exact-rule recurrence utility, while finite validation, archive growth and repeated-challenge scope remain explicit limitations.
