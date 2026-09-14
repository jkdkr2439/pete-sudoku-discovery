# Context reuse and interaction cost

G10 extends the scrambled-ID experiment with `pair_cost_aware`. G9's `pair_adaptive` reduced reset episodes but paid for repeated context placements and split queries. The new arm uses the information in every sequential action receipt and reuses a known-compatible context.

## Mechanism and assumptions

Suppose `a`, `b` and `c` are already known to be mutually compatible when holding the same symbol. To learn their relations with a new target:

1. Reset and place the target first.
2. Place `a`. Its receipt identifies the target–a pair's compatibility.
3. Place `b` in the same experiment. Any previously accepted group member is known compatible with b, so the new receipt identifies the target–b pair.
4. Continue with c, including after rejections, which leave the board unchanged.

Repeat with the other equality class in a fresh context. Both compatible and conflicting relations are learned; neither class is assigned a fixed truth value. The group members share a symbol; the target uses either that symbol or a different one. Symbol-renaming symmetry makes these representatives applicable to other symbols, as in G9.

Groups are constructed from prior pair observations. Larger groups are visited first so the reset and anchor placement are amortized over more labels. Group selection and context reuse are authored policies. No physical coordinates, hidden grouping, validator or solution is supplied to acquisition or Sandbox.

The model still assumes stationary deterministic pair constraints and symbol-renaming symmetry. This arm additionally requires that rejected actions leave the board unchanged. It stops if an anchor is rejected or a rejected member reports a changed/missing state-change flag. It does not implement adaptation to changing rules or infer higher-order relationships.

## Costs and budget handling

A query/episode means one reset plus its sequence of placements; the meaning of a query therefore differs from a single binary pair query. The primary metric is the sum of all resets and placements, which does not hide this distinction.

For complete learning from an empty model, let N be the number of pair/equality-class labels and Q the number of episodes. Each member placement identifies exactly one label; each episode adds one anchor placement and one reset:

- Member placements: N.
- All placements: N + Q.
- Total interactions: N + 2Q.

Every episode processes at least one member, so Q <= N. Under the stated assumptions, complete learning costs at most 3N, the exhaustive policy's cost. The bound does not imply that every fixed-budget partial model solves a puzzle, nor that every world provides useful groups. When all equal-symbol pairs conflict, groups are singletons and the new policy can tie exhaustive probing.

For 81 IDs and two symbol classes, N = 6,480 and exhaustive learning costs 19,440 interactions. The policy budgets every action. It starts a context only if its overhead plus at least one member fits. If the budget ends partway through a group, observed labels are retained and untested pairs stay unknown. This differs from G9's upfront reservation of a complete grouped query.

The unchanged Sandbox search is shared by all arms. Unknown pairs are optimistically permitted; substrate commitment determines success. Read-only authority evaluation occurs only after search and commitment, never supplies labels to learners, and is checked against a frozen model snapshot.

## Fixed comparison and reproduction

The matrix was fixed in `docs/PLAN.md` before observing its outcomes:

- Challenge seed 23 (new relative to G9), tier 2.
- Scramble seeds 41 and 53 (new relative to G9).
- Interaction caps 12,000 and 24,000.
- Arms `pair_exhaustive`, `pair_adaptive`, and `pair_cost_aware`.
- Shared search budget 2,000 assignments.
- Twelve cases, all outcomes retained.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/audit_boundaries.py
PYTHONPATH=src python -m pete_discovery.opaque_experiment \
  --output runtime/opaque-g10-reproduction \
  --seeds 23 --scrambles 41 53 \
  --interaction-budgets 12000 24000 \
  --arms pair_exhaustive pair_adaptive pair_cost_aware \
  --search-budget 2000
```

Use a new directory under `runtime/`. Existing evidence is not overwritten. Default arms remain the original three G9 arms so the previous reproduction command retains its scope; the new arm is explicitly selected above.

Receipts contain separate learning, generation, search and evaluation times, physical counts, confusion matrices and known-pair coverage. Each run retains its model, all physical actions in a verified hash journal, search trace, source snapshot and configuration. No prior learned model is loaded. G9's existing artifacts and checkpoint remain historical records of their own source snapshot.

## Results

All **12/12 planned cases** completed and were retained, with no execution errors. The full suite passed **30 tests in 42.830 seconds**, the boundary audit passed, and JavaScript syntax and diff checks passed. Tests finished before the comparison started. The G9 control policies, pair model, substrate and shared solver remain unchanged; the new acquisition policy and its dispatch are the experimental change.

Full-acquisition costs, measured in the 24,000-cap cases:

| Mapping | Policy | Reset episodes | Placements | Total interactions |
|---|---|---:|---:|---:|
| 41 | Exhaustive | 6,480 | 12,960 | 19,440 |
| 41 | G9 grouped | 4,416 | 16,630 | 21,046 |
| 41 | Context reuse | 1,288 | 7,768 | **9,056** |
| 53 | Exhaustive | 6,480 | 12,960 | 19,440 |
| 53 | G9 grouped | 4,356 | 17,088 | 21,444 |
| 53 | Context reuse | 1,102 | 7,582 | **8,684** |

Context reuse saves **53.4% and 55.3%** of total interactions versus exhaustive probing, and **57.0% and 59.5%** versus G9 grouped probing on mappings 41 and 53 respectively. Unlike G9's query-count improvement, these reductions include the full reset and placement cost.

| Interaction cap | Exhaustive: solved mappings | G9 grouped | Context reuse |
|---|---:|---:|---:|
| 12,000 | 0/2 | 0/2 | **2/2** |
| 24,000 | 2/2 | 2/2 | **2/2** |

At 12,000, the controls produced incomplete learned models and their proposed completions were rejected during physical commitment (`COUNTEREXAMPLE`). Context reuse completed learning before reaching that cap, using the same 9,056 and 8,684 interactions as at the higher cap. Learning and commitment budgets are accounted separately; each successful solution required 51 physical commitment placements.

Every complete model has all 6,480 pair/equality-class entries and predicts all 6,480 held-out-symbol pair cases correctly. Within each mapping, **complete model files and complete Sandbox trace files are byte-identical across policies and across the completed-learning budget conditions**. The solver used 81 assignments with 30 backtracks on mapping 41 and 51 assignments without backtracking on mapping 53. This isolates the measured cost change to acquisition rather than a change in knowledge or search.

The accounting identity N + 2Q holds in all new-policy cases. Every physical journal verifies, all receipts and saved source snapshots are hash-bound, and no interaction or search budget was exceeded. The matrix and raw receipts are at [`runtime/opaque-g10-pilot/manifest.json`](../runtime/opaque-g10-pilot/manifest.json); the durable checkpoint is [`COST_AWARE_CHECKPOINT.json`](COST_AWARE_CHECKPOINT.json).

These results concern **one new generated puzzle under two new representations**, not an independent puzzle success-rate estimate. Acquisition costs depend on the hidden relation network and ID ordering; changing a Sudoku puzzle seed alone does not change its rule family. The unit tests cover other synthetic pair networks, but no higher-order rule family or cross-task transfer was evaluated. The cost bound and gains depend on pairwise sufficiency, learned-compatible contexts, symbol symmetry, and rejection without state change. The supplied policy is now more efficient on this interface; it has not learned its own representation, query strategy, or search algorithm.
