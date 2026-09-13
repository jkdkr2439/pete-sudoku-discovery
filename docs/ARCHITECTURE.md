# Architecture

## Causal route

```text
SUBSTRATE (hidden authority)
    -> public sensor packet
BODY (encode / transport)
    -> observations + interoception
COGNITION (choose generic controlled experiments)
    -> physical actions through Body
SUBSTRATE (accept or reject; no explanation)
    -> observed gap
FIELDMAP (evidence-weighted explicit relations)
    -> collapsed predictive clauses
IMAGINATION (counterfactual search against Fieldmap only)
    -> intended board
BODY -> SUBSTRATE (authoritative commitment)
    -> completion or counterexample
```

## Hard world versus learned model

`substrate.py` contains puzzle generation, private validation and the hidden target. Those are world physics, comparable to collision rules in a game engine. They are not available through the sensor channel.

`fieldmap.py` starts empty. It receives pairs of opaque coordinate/value bindings plus accepted/rejected consequences. It generates a general arithmetic relation vocabulary from the public integers: equality and equal quotient buckets at possible scales. Evidence collapse selects the smallest zero-counterexample cover of rejected events. The resulting clauses have no Sudoku labels.

`sandbox.py` performs generic finite-domain state search. Compatibility comes exclusively from Fieldmap predictions. It imports no substrate module and receives no validator callback.

`cognition.py` chooses controlled two-binding experiments, requests Fieldmap collapse, verifies predictions on held-out values, asks Sandbox for a state, and commits that state through the body.

## Why the substrate is a world model

It is executable rather than descriptive. The same proposed action always meets authoritative state-transition conditions and produces a consequence. The agent can be wrong about it; therefore Fieldmap and substrate are not the same object. A learned theory becomes knowledge only after it predicts new substrate interactions and a complete sandbox state survives real commitment.

## Progressive worlds

The substrate generates deterministic, unique 9x9 boards only. Difficulty increases by clue removal across three tiers. Puzzles are unlimited through seeds, and a Fieldmap is reused across new 9x9 puzzles so transfer remains visible.

## Current scope

The experiment discovers binary incompatibility relations in finite grids. The relation vocabulary and controlled probe schedule are authored general cognitive primitives. They reduce the search space and are therefore real inductive biases. The experiment does not yet prove open-ended discovery, optimal experiment selection, or learning without any prior representational primitives.
## Imagination and Sandbox

Imagination is a system-level capacity to construct and compare possibilities absent from the authoritative world. Sandbox is the concrete finite workspace that currently implements counterfactual Sudoku completion. They are therefore two conceptual levels but one executable search engine in this repository. Sandbox receives only a public observation plus Fieldmap predictions; it never imports or calls substrate authority.
