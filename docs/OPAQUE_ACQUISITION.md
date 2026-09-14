# Acquisition with scrambled cell identities

This extension tests whether useful constraints can be learned without the original row/column/square-bucket descriptors. It preserves the existing observer and adds a separate local CLI experiment.

The new substrate port exposes public cell IDs, an alphabet, current values and fixed-cell flags. A private substrate-owned permutation maps those IDs to physical cells. Neither the learner nor Sandbox receives that mapping, physical coordinates, constraint groups, a validator callback or a stored solution.

## What remains authored

The pair table assumes a deterministic, stationary world whose validity is determined by pairs of assignments, with invariance under renaming symbols. Each unordered cell pair therefore has two independently learned entries: one for equal symbols, one for unequal symbols. An unequal-symbol pair is not assumed compatible. This is a restricted compatibility model, not an arbitrary table over all 81 ordered symbol pairs, and it cannot represent general higher-order or symbol-specific rules.

Sensors, resets, the zero/empty marker, experiment policies, the pair representation, and minimum-domain-first backtracking are supplied. Unknown pair entries remain unknown in the model and are optimistically permitted by search. Completion is successful only when actual commitments receive the substrate's terminal receipt.

## Compared arms

| Arm | Learning mechanism | Spatial information used |
|---|---|---|
| `spatial` | Existing DynamicFieldmap hypotheses and collapse, using exhaustive pair probes | An authored square embedding of the public ID order; correct in the identity control, arbitrary after scrambling |
| `pair_exhaustive` | Probe every pair with equal and unequal symbols; record the two compatibility classes | None |
| `pair_adaptive` | Build compatible groups from evidence, query groups, and split rejected groups to isolate conflicting pairs | None |

The adaptive policy processes IDs in their public order. For each new ID it tests every existing compatible group twice: once with the target equal to the group's symbol, once unequal. A successful query establishes compatibility with all group members. A rejected group is recursively split until all conflicting pairs are isolated. The target then joins a group with which its equal-symbol pairs are all known compatible, or starts a new group. All groups and splits derive from observations; no geometry is used.

This policy is a first group-testing baseline. It does not implement QuAcq, learn an experiment-selection policy, use a committee of models, or optimize expected information gain. It may save resets while spending more placements. Arbitrary unknown graphs do not guarantee a query-efficiency advantage.

All three arms use `Sandbox.complete` through the same one-row public-ID projection. The solver receives only its model and public state; ordering, alphabet, attempt budget and search implementation are matched. Original square-grid behavior is preserved. The shared solver now enforces an inclusive assignment budget and propagates `BUDGET_STOP` without attempting further sibling assignments.

## Reproduce

From the repository root, using Python 3.11 or newer with no added dependencies:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/audit_boundaries.py
PYTHONPATH=src python -m pete_discovery.opaque_experiment \
  --output runtime/opaque-g9-reproduction \
  --seeds 14 --scrambles identity 17 29 \
  --interaction-budgets 8000 24000 --search-budget 2000
```

The output directory must be new and located under `runtime/`. The matrix is written before runs begin, and each receipt is retained immediately. Errors and unsuccessful solves remain in the denominator. For a smaller first run, select one mapping, one budget and one arm with `--scrambles 17 --interaction-budgets 24000 --arms pair_adaptive`.

An interaction budget counts **one reset plus every placement**. A group query reserves its complete cost before execution, so an exhausted budget cannot create partially supported inferences. The budget applies to learning; committed solution placements are reported separately. The search budget counts attempted assignments, not compatibility comparisons or wall-clock time. This CLI does not claim a strict wall-clock limit.

Each case stores its configuration, model, complete physical hash journal, complete search trace, final public board and receipt. The matrix manifest contains the Git revision and dirty status, SHA-256 hashes and a byte-for-byte snapshot of the Python source used. Each receipt includes its model/trace hashes and a verified journal head. The Linux pilot records use LF newlines; artifact hashes bind the actual saved bytes. The original archived video/trace manifests are unchanged.

## Evaluation boundary

Model evaluation occurs after search and physical commitment. It checks all 3,240 cell pairs in two held-out symbol classes `(9,9)` and `(9,8)`, using a read-only authority hook available only to the runner. Those labels never enter the model, and the runner verifies that evaluation did not mutate the saved model. This evaluates the authored symmetry assumption and learned relations; it is not an independent arbitrary-symbol benchmark. Report confusion counts and known-pair coverage alongside accuracy.

The pilot uses one generated challenge seed (14), 30 clues, three mappings (identity, 17, 29), two interaction budgets (8,000 and 24,000), and all three arms: 18 cases. The identity condition is a positive control for the spatial adapter. Different mappings are representations of the same challenge, not independent puzzle draws. A broader reliability claim needs more independently generated and external puzzles.

The tests also cover synthetic pair worlds with independently sampled equal- and unequal-symbol conflicts, opaque relabeling, budget stops, contradictory evidence, exact-limit search completion, a real opaque Sudoku solve, journal tampering and deliberate authority-import mutations. The boundary audit is a static tripwire, not a security sandbox or a proof against arbitrary Python reflection.

## Pilot results

The fixed matrix completed with all **18/18 cases retained**, no execution errors, all physical journals verified, and no learning or search budget overruns. Source snapshots bind the Python implementation evaluated at the G9 checkpoint. The full suite passed **23 tests in 41.704 seconds**, the expanded boundary audit passed, and JavaScript syntax and diff checks passed.

Artifacts: [`runtime/opaque-g9-pilot/manifest.json`](../runtime/opaque-g9-pilot/manifest.json). The ignored local output occupies about 539 MiB before bundled validation logs, primarily physical journals. The manifest also contains exact source snapshots and receipt hashes, so this uncommitted implementation is reproducible independently of the base Git revision.

| Interaction budget | Spatial control: solved representations | Exhaustive pair table | Adaptive pair table |
|---|---:|---:|---:|
| 8,000 | 1/3 (identity only) | 0/3 | 0/3 |
| 24,000 | 1/3 (identity only) | 3/3 | 3/3 |

These are three representations of **one challenge**, not three independent puzzle draws. Every unsuccessful case above reached a Sandbox completion which the substrate rejected during commitment (`COUNTEREXAMPLE`); none is hidden behind an execution-error or missing-result filter.

Full-acquisition costs at the 24,000 cap:

| Mapping | Exhaustive queries | Adaptive queries | Exhaustive placements | Adaptive placements | Exhaustive total interactions | Adaptive total interactions |
|---|---:|---:|---:|---:|---:|---:|
| Identity | 6,480 | 4,340 | 12,960 | 14,983 | 19,440 | 19,323 |
| Scramble 17 | 6,480 | 4,426 | 12,960 | 16,930 | 19,440 | 21,356 |
| Scramble 29 | 6,480 | 4,392 | 12,960 | 16,958 | 19,440 | 21,350 |

Each query incurs one reset, so the query count is also the reset count. On the scrambled mappings, adaptive acquisition reduces queries by approximately 32% but increases reset-plus-placement interactions by approximately 10%. It is **not a demonstrated interaction-efficiency improvement**. On identity ordering it saves about 0.6% of total interactions, which does not establish robustness to representation changes.

At full acquisition, both pair learners recover all 6,480 pair/equality-class entries, achieve 6,480/6,480 correct held-out-symbol predictions, and produce **byte-identical model files within each mapping**. Their shared solver consequently takes the same 51, 55 and 65 assignment attempts on identity, scramble 17 and scramble 29 respectively. This supports separation of model acquisition from search.

The original spatial control reaches full prediction accuracy with only 7,998 interactions on identity ordering, whereas neither pair learner solves at the 8,000 cap. Its structured prior is useful when aligned with the world. Under either scrambled mapping it collapses to no active clauses even after exhaustive acquisition, predicts every pair compatible (87.5% accuracy on the two-class check), and fails physical commitment.

The next empirical target is cost-aware experiment selection. Grouping alone is insufficient when its extra placements outweigh saved resets. Wall times are retained for diagnosis; initial pilot cases overlapped the unit-test process, so they should not be treated as a controlled performance benchmark. No rule-change adaptation, cross-task memory benefit, or broader Sudoku success-rate claim is established by this stage.
