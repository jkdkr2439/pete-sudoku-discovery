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
5. The same mechanism runs on 4x4 and 9x9 worlds without a cognition code change.
