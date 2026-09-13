# Brainstorm

## 2026-09-14 — G0: isolate the claim

### Parent goal
Demonstrate that a rule-governed substrate can serve as a world model from which Pete constructs usable knowledge through interaction, without offline training or Sudoku knowledge in cognition.

### Distinct layers
- **Substrate:** authoritative external state, hidden constraints, consequences, puzzle generation, difficulty progression.
- **Body:** finite sensor and actuator channels. It transports signals but does not interpret Sudoku.
- **Fieldmap:** dynamic, evidence-bearing internal relations. These are the agent's changing weights.
- **Imagination:** counterfactual workspace using only Fieldmap predictions; mistakes here do not touch substrate state.
- **Cognition:** generic experiment selection, relational description induction, goal selection, and collapse.
- **Display:** observer-only evidence surface.

### Anti-cheating criterion
Success is invalid if cognition imports the substrate, receives a hidden solution/rejection reason, contains named Sudoku constraints, or calls the real validator from imagination. A hidden substrate solver may exist solely to generate unique worlds and grade completion.

### Learning mechanism
Use controlled two-token physical experiments. Describe each pair using a generic relation vocabulary generated from observed integer coordinates and values: equality, inequality, and equal quotient buckets over possible scales. Accepted/rejected outcomes update Fieldmap weights. A greedy evidence cover may collapse recurring descriptors into a predictive constraint theory. This is generic relation induction; no descriptor is labeled as a Sudoku row, column, or block.

### Falsifiable outputs
1. Empty Fieldmap cannot predict hidden legality above chance.
2. Physical probes change Fieldmap evidence and prediction accuracy.
3. Imagination can find a completion using only the learned Fieldmap.
4. The completion survives authoritative substrate commits.
5. The same mechanism transfers across unseen 9x9 worlds and increasing clue-removal tiers without a cognition code change.

## 2026-09-14 - G1: one world scale only

The experiment is restricted to Sudoku 9x9. Smaller grids are removed so successful evidence cannot be attributed to a toy-scale curriculum. Difficulty changes only through clue removal and seeds; cognition and its empty-start condition remain unchanged.

## 2026-09-14 - G2: data as structural reaction

An external signal is not the stored data. The system transition it causes is the data: S(t) --input--> S(t+1). The gap is a measured component of that reaction, containing prediction mismatch and structural mutations. Retrieval therefore resonates against gap signatures and affected relations rather than fetching a raw input record. Identical reactions are aggregated to keep memory bounded.
