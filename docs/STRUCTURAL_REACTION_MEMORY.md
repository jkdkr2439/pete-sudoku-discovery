# Dynamic Data as Structural Reaction

## Definition

Let the current internal organization be:

```text
S(t) = nodes + relations + dynamic weights + active invariants
```

An external signal `u(t)` is admitted through the body. Data is not identified with that signal. Data is the transformation caused by the signal:

```text
R(t) = < hash(S(t)), ref(u(t)), Delta(t), gap(t), hash(S(t+1)) >
```

- `ref(u(t))` identifies the external cause without retaining a second raw copy.
- `Delta(t)` contains nodes, counters, relations or weights that changed.
- `gap(t)` is the measured effect: prediction mismatch, observed consequence and affected relation signature.
- `S(t+1)` becomes the starting structure for the next interaction.

Therefore a sequence `A -> B -> C` receiving a new variable does not merely append that variable. Its organization becomes `A' -> B' -> C'`. Every later signal interacts with this changed organization.

## Storage

The Fieldmap retains:

1. explicit relation evidence;
2. dynamic weights produced by support and counterevidence;
3. aggregated reaction shapes;
4. the before/after structure hashes;
5. the gap signature and structural mutations;
6. bounded input references rather than raw duplicate input records.

Five identical reaction shapes increase the count of one structure instead of creating five unrelated memories.

## Retrieval

Retrieval begins from a current gap. The Fieldmap encodes the relations affected by that gap and compares them with stored reaction signatures. Resonance is ranked by:

- overlap of affected relations;
- match between observed consequences;
- recurrence count.

The result is not a literal replay of an old input. It is reactivation of a prior transformation shape that can influence the next prediction or action.

## Relation to the three layers

- **Substrate:** produces the external consequence.
- **Fieldmap:** is changed by that consequence and stores the reaction topology.
- **Imagination:** operates on the resulting changed Fieldmap without touching substrate authority.

## Present implementation boundary

The representation language for coordinate equality and quotient buckets remains authored. What changes dynamically is which relations acquire evidence, their weights, which gap shapes recur and which clauses collapse. This is a testable structural-learning mechanism, not a claim of learning without any prior machinery.
