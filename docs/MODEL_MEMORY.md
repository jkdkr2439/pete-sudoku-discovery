# G12: retrieve learned rule models across recurrence

This extension adds an archive to the G11 recovery experiment. It stores learned
pair tables and retrieves them from current public evidence. The original UI and
continuous scheduler do not use this experimental controller.

## Mechanism and boundaries

`model_memory.py` contains `ModelArchive`, `MemoryController`, and the fresh-learning
control. Archive entries are independent copies, deduplicated by their pair-class
predictions. Complete coverage of the public cell universe is required for admission;
this is explicitly **not** a validity certificate. The initial entry comes from online
G10 acquisition. Later entries are admitted after an authoritative task completion.
A stale table can pass that task and enter the archive; no evaluator result is used
for admission, selection, repair, or subsequent tasks.

The archive contains rule evidence, revision history and acquisition/task provenance.
It does not contain puzzle boards, solutions, world IDs, or transition labels. Retrieval:

1. Discards entries for a different public cell universe and entries contradicted by
   the current givens.
2. Chooses pair-class probes that most evenly split candidate predictions, up to 32.
3. If one candidate survives, checks up to 128 randomly sampled remaining pair classes
   using fixed seed 0. Every probe costs one reset and two placements.
4. Treats a surviving entry as a tentative match. No match, ambiguity, or exhausted
   verification falls back to the current model. All directly observed probe labels
   update whichever model will be used.
5. Passes that model to G11 failure-triggered repair and the unchanged Sandbox.
   A failed retrieved-model attempt can therefore trigger repair before commitment.

The per-task budget includes all physical work in retrieval, verification, repair and
commitment. A reset plus the number of mutable cells is reserved during retrieval for
an attempt at completing the task. Search has a separate assignment budget per attempt.
Public sensing and CPU are unpriced in the interaction metric. Retrieval wall and process
CPU time are reported separately; both include probe handling and journal writes.
Storage is the exact compact UTF-8 JSON size of active model plus archive, excluding
transient candidate copies, interpreter object overhead and experiment artifacts.

The implementation retains the authored deterministic, pairwise, symbol-permutation
symmetry assumptions and stable rules within a task. Retrieval policy, archive admission,
sampling and fallback are authored algorithms. There is no learned router or new relation
operator. Archive size is unbounded in this pilot; there is no eviction or persistent
archive loader. Snapshots are saved for inspection, while recurrence runs in one process.

## Fixed experiment

The sequence is A → B → A → C. A common warm model is acquired online on tier 2,
puzzle seed 43 and opaque mapping seed 79. B applies one or three disjoint hidden
role swaps with seed 113. Repeating the same swaps restores A. C applies three swaps
with seed 227 to that restored A. Those operations and phase labels exist only in the
experiment harness/substrate. The public challenge repeats on return to A; the agent
stores only rule tables and probes predictions, not a challenge fingerprint.

Each of the two severities has three independent sequential arms:

- `fresh`: acquire a new table on every post-warm task, even a recurring task.
- `repair`: retain only the latest table and use G11 recovery.
- `memory`: retain the latest table and an archive; retrieve, then use G11 recovery.

Each phase has 12,000 resets-plus-placements and 2,000 search assignments per attempt.
All 18 phase outcomes are retained. The common warm cost is included once in each
arm's lifetime total. These settings were recorded in `docs/PLAN.md` before outcomes.
The two severities share one puzzle and the same A/C networks; they are not independent
replications across puzzle families.

## Reproduce

From the repository root, with Python 3.11+ and no external packages:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/audit_boundaries.py
PYTHONPATH=src python -m pete_discovery.memory_experiment \
  --output runtime/memory-g12-reproduction
```

The output must be a new directory under `runtime/`. It includes a pre-run manifest,
all Python source snapshots and hashes, a common warm journal/model, continuous
per-arm hash-chained physical journals, and per-phase model/archive snapshots,
Sandbox traces, costs, and receipts. Authority checks run only after each phase has
made all decisions and archived its model, and never feed back into the learner.
Successful completion, model accuracy and incorrect retrieval are separate fields.

## Measured result — 2026-09-14

All 18 phases solved, and every final model matched all 6,480 authority pair-class
checks. Warm acquisition cost **8,784 interactions**. The results below count every
learner reset and placement, including verification and failed commitments.

| B severity | Policy | B | Return to A | Unfamiliar C | Lifetime, including warm A |
|---|---|---:|---:|---:|---:|
| 1 swap | Fresh | 8,856 | 8,836 | 9,044 | 35,520 |
| 1 swap | Current-model repair | 4,478 | 4,481 | 7,487 | 25,230 |
| 1 swap | Archive + repair | 4,478 | **436** | 7,805 | **21,503** |
| 3 swaps | Fresh | 8,864 | 8,836 | 9,044 | 35,528 |
| 3 swaps | Current-model repair | 6,737 | 6,743 | 7,487 | 29,751 |
| 3 swaps | Archive + repair | 6,737 | **436** | 7,805 | **23,762** |

Returning A costs 384 interactions for 128 verification probes plus 52 for reset
and successful commitment. This is 90.3%/93.5% below latest-model repair and 95.1%
below fresh learning. Across the entire sequence, including initial acquisition and
unfamiliar-world overhead, memory reduces interactions by 14.8%/20.1% versus repair.

In this pilot, public givens reject B's archived model when A returns. **No
candidate-disagreement probes were needed in any real phase**; their behavior is
covered by synthetic tests. Thus the measured benefit establishes archive reuse
with given-based selection and sampled verification, not an empirical advantage
for the disagreement-probe policy.

On B, public givens reject the sole A candidate with no physical retrieval work,
so memory matches repair cost. On C, givens reject B but leave A plausible. The
105th verification probe contradicts A; memory rejects it and falls back to repair.
This costs 315 retrieval interactions plus 7,490 recovery interactions, or 318 more
than the repair-only control. Both return-to-A selections were correct under the
later full evaluator; there were no selected candidates in B or C. That is two
correct selections, not a broad false-reuse rate estimate.

Each memory arm ends with three archived models. Compact archive storage is
1,608,017 / 1,621,277 bytes; including the active model it is 2,163,763 / 2,177,023
bytes (about 2.06 / 2.08 MiB). Fresh learning retains 521,747 bytes and repair
572,208 / 598,797 bytes. Retrieval process CPU was approximately 0.024–0.159 seconds
per phase on this local run; these timings are descriptive, not a throughput benchmark.
The nested G11 `unverified_retained_pair_classes` field describes recovery probes
only; retrieval probe coverage is reported separately.

Validation: **50 tests passed in 51.892 seconds**, the expanded seven-file authority
boundary audit passed, and an independent receipt audit verified source snapshots,
model/archive/trace/receipt hashes, every continuous journal chain and phase prefix,
physical resets and placements, authoritative completions, storage sizes, and all
phase/lifetime/search bounds. The static boundary audit is a tripwire, not a formal
sandbox. See `docs/MODEL_MEMORY_CHECKPOINT.json` and
`runtime/memory-g12-pilot/manifest.json`; the receipt verifier and test/audit evidence
are bundled under `runtime/memory-g12-pilot/validation/`.

The bounded conclusion is that remembering exact prior rule networks reduces the
cost of recurrence in this one-puzzle sequence. The finite-verification negative test
still permits incorrect reuse when a changed rule is neither probed nor exercised
by the solution. Broader recurrence, noisy evidence, changed cell vocabularies,
archive eviction, and automatic task-boundary detection remain untested. All changes
are local and uncommitted.
