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
