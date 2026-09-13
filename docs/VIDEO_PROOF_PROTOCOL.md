# Reproducible Video Proof Protocol

The recording is an evidence artifact, not a hand-edited animation.

## Preconditions

1. Source code is committed.
2. The server is stopped.
3. `runtime/` is deleted and recreated empty.
4. A fresh server process starts from that directory.
5. Initial API state must report zero Fieldmap samples, zero clauses and zero journal events. The recorder aborts if any condition fails.

## Recorded causal sequence

1. Show the empty-start contract.
2. Show the live observer UI before Start.
3. Trigger `POST /api/start-once` so the proof has one bounded world.
4. Capture the actual UI throughout physical experimentation, Fieldmap collapse, held-out verification, imagination and physical commitment.
5. Require final phase `SOLVED`; otherwise abort without claiming success.
6. Encode captured frames to MP4 and write a JSON manifest containing source commit, initial state, timeline, final Fieldmap, verification metrics and journal head.

## Code evidence

- Hidden world physics: `src/pete_discovery/substrate.py`
- Dynamic structural reactions: `src/pete_discovery/fieldmap.py`
- Cognition: `src/pete_discovery/cognition.py`
- Validator-free imagination: `src/pete_discovery/imagination.py`
- Boundary scanner: `tools/audit_boundaries.py`
- Recorder: `tools/record_proof.py`

The boundary audit parses imports in cognition, Fieldmap and imagination and fails if substrate authority is referenced. The public-packet test fails if a solution, candidate, constraint, group or rejection reason crosses the sensor boundary.

## Interpretation

"No training" means there is no corpus, offline optimization, pretrained parameter file or Sudoku knowledge installed in cognition. The live Fieldmap still changes from experience. That is online structural learning, which is the phenomenon this experiment measures.
