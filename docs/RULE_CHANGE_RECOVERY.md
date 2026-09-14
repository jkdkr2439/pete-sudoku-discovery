# Recovery after hidden cell-role changes

G11 tests one bounded form of adaptation: can an online-acquired pair model remain useful after its environment changes some relationships? It adds a separate recovery CLI. The original demo and the G9/G10 experiments remain available.

## Transition and information boundary

The authority swaps private ID-to-position assignments, then restores the challenge. Public IDs, alphabet, observation schema and world ID remain unchanged; current values and fixed-cell flags reflect the restored challenge under the new mapping. The controller receives no swapped IDs, swap count, transition seed or change flag. A swap alters the pair constraints associated with public IDs while preserving a solvable 9x9 problem.

This is a change of variable roles within the same Sudoku pair-rule family. It is not discovery of new rule operators or transfer to a higher-order domain. The three-swap condition applies three disjoint swaps simultaneously; branches start from the same warm state, rather than forming a long sequence of independent life episodes.

A common warm model is acquired online using G10 context reuse, verified, and saved. Each case receives an independent copy of that model and environment state. Warm learning is reported as a common upfront cost; lifetime cost includes it. No external training data or pretrained model is loaded.

## Recovery policies

All arms first try the retained model with the same Sandbox and physical commitment. If that attempt succeeds, no recovery runs. A failed search or rejected commitment triggers the chosen policy:

| Policy | Response to failure |
|---|---|
| `frozen` | Retain the failure and perform no adaptation |
| `relearn` | Discard the active model, run fresh G10 cost-aware acquisition, then retry |
| `repair` | Probe contradiction candidates, revise directly contradicted labels and check incident relationships, then retry |

Failure is a trigger for investigation, not proof that the rules changed: an inadequate search budget can also cause failure.

The repair watchlist starts with pairs implicated by a rejected placement and pairs of current givens that the old model regards as incompatible. It then visits all previously conflicting pair classes and a deterministic sample of 128 previously compatible pair classes. The controller uses seed 0 for ordering and sampling, unrelated to the hidden transition seed.

Each watchlist probe is a fresh, isolated two-assignment experiment. If it contradicts the current model, the controller probes both endpoints' incident pairs in both equality classes. It does not recursively expand from every neighbor whose label changes. Already verified pairs are skipped. This targets local changes while keeping the work bounded.

Old compatible groups are not trusted after a transition, so repair intentionally uses direct probes rather than streaming assignments through stale G10 contexts. Relearning can safely rebuild and reuse groups from fresh observations.

## Revision and certification limits

`RevisablePairwiseFieldmap` keeps the previous label, its evidence counts and the version of each revision. Under the assumption of noiseless feedback and rules stable during repair, the latest directly observed label becomes active. The original stationary pair table still raises on contradictory evidence.

Only tested relationships are revalidated; untested retained labels remain explicitly counted. `WATCHLIST_COMPLETE` means the chosen checks finished, not that all possible changes were found. After the controller stops, a read-only evaluator checks all 6,480 pair/equality-class cases and reports residual errors without updating the model.

The tests exhibit two important limitations: a changed constraint can go unnoticed when the current solution still succeeds, and an empty/uninformative watchlist can finish despite a wrong retained model. Therefore authoritative puzzle success, watchlist completion and full model correctness are reported separately.

## Budgets and evidence

The post-transition cap includes the initial retained-model attempt, every experimental reset and placement, every challenge reset, and all failed/successful physical commitments. Sense calls and model computation are unpriced. The search limit is 2,000 assignments **per solve attempt**, with at most an initial and a final attempt. Search work is reported separately from physical interactions.

Repair and relearning reserve enough interactions for one final challenge reset and all mutable-cell commitments. Repair stops before a probe that would consume that reserve; directly observed revisions survive the stop. Each arm records its actual post-transition cost and the common warm cost plus that cost.

Physical journals reference the warm journal head and model hash. Source snapshots, model snapshots, search traces, configurations and receipts are retained under the output directory. The evaluator runs after search/commitment and checks that it did not mutate the saved model.

## Fixed matrix and reproduction

The matrix was fixed in `docs/PLAN.md` before outcomes were observed: challenge seed 31, initial mapping seed 67, tier 2, swap seed 101, swap counts 0/1/3, budgets 6,000/12,000, and all three policies. It contains 18 cases, including the unchanged-world control. All failures are retained. The warm-acquisition cap is 24,000 interactions.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/audit_boundaries.py
PYTHONPATH=src python -m pete_discovery.recovery_experiment \
  --output runtime/recovery-g11-reproduction \
  --seed 31 --mapping 67 --swap-seed 101 --swaps 0 1 3 \
  --budgets 6000 12000 --policies frozen relearn repair \
  --search-budget 2000 --compatible-checks 128 --watch-seed 0
```

The output directory must be new and under `runtime/`. Previous G9/G10 receipts remain bound to their own source snapshots.

## Results

All **18/18 planned cases** completed and were retained with no execution errors. The full suite passed **40 tests in 44.527 seconds**, the expanded boundary audit passed, and JavaScript syntax and diff checks passed. Tests finished before the matrix started.

The common warm acquisition cost **9,004 interactions** and produced all 6,480 correct pair/equality-class entries. The role transitions changed **72** entries after one swap and **214** after three swaps. The zero-swap control changed none.

At the **6,000 post-transition interaction cap**:

| Change | Frozen reuse | Fresh relearning | Targeted repair | Repair model errors |
|---|---|---|---|---:|
| No swaps | SOLVED, 52 | SOLVED, 52 | SOLVED, 52 | 0 |
| One swap | Rejected, 10 | Rejected, 5,956 | **SOLVED, 4,487** | **0/6,480** |
| Three swaps | Rejected, 10 | Rejected, 5,958 | **SOLVED, 5,999** | **0/6,480** |

At the **12,000 cap**, where both recovery methods finished their planned learning/checks:

| Change | Fresh relearning: post-transition interactions | Targeted repair | Repair saving |
|---|---:|---:|---:|
| One swap | 8,890 | **4,487** | **49.5%** |
| Three swaps | 8,878 | **7,466** | **15.9%** |

Both methods solved and had zero model errors in those higher-budget changed cases. Frozen reuse still failed with 72 or 214 stale labels. The unchanged-world control solved immediately in every arm and budget, with no probes or revisions.

Costs include the failed initial attempt (10 interactions in each changed case), all probes/resets, and the successful final commitment (52 interactions). They are **post-transition** figures, not costs from an empty lifetime. Adding the shared 9,004-interaction warm-up gives 13,491 versus 17,894 lifetime interactions for repair versus relearning after one swap at the higher cap, and 16,470 versus 17,882 after three swaps.

Repair revalidated 1,475 pair classes and recorded 72 revisions after one swap. At three swaps it recorded all 214 revisions within 1,979 probes at the lower cap; at the higher cap it performed 2,468 probes. Untested retained labels are counted separately in each receipt. All repaired models matched the authority on all 6,480 pair cases after the controller had stopped; those evaluation labels never influenced repair.

The three-swap lower-budget case is instructive: its status is **SOLVED with REPAIR_BUDGET_STOP**, not `WATCHLIST_COMPLETE`. The evaluator subsequently found zero errors. With more budget, the fixed policy continued checking unchanged relationships, spending an additional 1,467 interactions without additional revisions. The controller did not know that all changes had already been repaired. This reveals a remaining stopping-policy cost rather than a budget violation or a certified early-stop rule.

Every physical journal verified. Source snapshots, per-case receipts, model/trace hashes and complete budget accounting are preserved at [`runtime/recovery-g11-pilot/manifest.json`](../runtime/recovery-g11-pilot/manifest.json). The durable checkpoint is [`RULE_CHANGE_CHECKPOINT.json`](RULE_CHANGE_CHECKPOINT.json).

This supports local, failure-triggered repair within **one generated puzzle, one initial mapping, and two related perturbation severities**. The three-swap condition shares the first swap with the one-swap condition under the fixed seed; these are not independent population samples. It does not establish universal change detection, long-horizon stability, robustness to noisy feedback, or transfer to new rule families. The authored repair policy relies on sparse/local changes being discoverable through its available failure evidence and watchlist.
