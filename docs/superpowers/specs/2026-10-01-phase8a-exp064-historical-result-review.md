# Phase 8A — EXP-064 Historical Result Review

**Date:** 2026-10-01  
**Status:** HISTORICAL RESULT REVIEWED AND FROZEN / NO CONTINUOUS-STABILITY HYPOTHESES  
**Decision:** DEC-458  
**Experiment:** EXP-20261001-064  
**Predecessor:** DEC-457

## Purpose

DEC-458 freezes the terminal historical result of the one-shot EXP-064 run.

No transform, estimator, annual-stability threshold, cost rule, ranking rule,
search bound, or freeze cap is changed.

No rerun, retry, replacement, reserved-data opening, candidate compilation, Phase
8B, promotion, or trading action is authorized.

## Frozen run identity

The only EXP-064 historical run is:

- run id: `36853290904`;
- workflow: `phase8a-exp064-continuous-stability`;
- path: `.github/workflows/phase8a-exp064-continuous-stability.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head:
  `b13f89f4d6bef8b1ab4a2fa12c6b01d0e5067506`;
- run number: `1`;
- attempt: `1`;
- terminal status: `completed`;
- terminal conclusion: `success`.

This run consumed the one-shot slot permanently.

## Terminal run shape

Exactly 20 jobs completed successfully:

- one preflight;
- 18 continuous-stability cells;
- one aggregate.

Exactly 20 artifacts exist and are non-expired.

Aggregate artifact:

- id: `11158816828`;
- name:
  `phase8a-exp064-aggregate-b13f89f4d6bef8b1ab4a2fa12c6b01d0e5067506`;
- artifact digest:
  `sha256:a404c053a5dd6989cf0efb2adba2cb276fec9a66a448a8617e7dac7da50c577f`.

The downloaded aggregate JSON has SHA-256:

`b971340204ec2a6136559dc467f84f1e6b69f1c58fe3c5cca01e437ba6c80284`

and canonical evidence fingerprint:

`832e8c814ac578b614764d37cba15e64569e2f841dfa6f72f2c9cd9a8fdbcbb1`.

The canonical fingerprint was independently recomputed from the unsigned aggregate
object and matched exactly.

## Cell-level result

All 18 cell evidence artifacts were inspected.

Each exact EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m cell reports:

- 80 frozen hypotheses;
- 80 evaluable hypotheses;
- 0 qualifying hypotheses;
- 0 deduplicated hypotheses;
- empty continuous-stability shortlist;
- empty frozen fingerprint inventory.

Across all 18 cells:

- hypotheses: `1,440`;
- evaluable hypotheses: `1,440`;
- qualifying hypotheses: `0`;
- deduplicated hypotheses: `0`;
- continuous-stability shortlist count: `0`;
- frozen continuous-stability count: `0`.

Every inspected cell evidence canonical fingerprint recomputed successfully and
matched its aggregate cell fingerprint.

## Classification

DEC-458 classifies the result as:

`NO_CONTINUOUS_STABILITY_HYPOTHESIS_PASSED_FROZEN_GATE`

This is stronger than a ranking or deduplication failure. No hypothesis entered the
qualifying set at all.

The classification applies only to the exact frozen EXP-064 universe and protocol:

- EURUSD / GBPUSD / USDJPY;
- 5m / 15m / 1h;
- 60m / 240m;
- the same 20 leakage-safe continuous features;
- frozen empirical midrank transform;
- one-feature × direction × polarity hypotheses;
- frozen DEC-452 continuous-stability thresholds and ranking;
- already-seen 2015-2022 design evidence.

It does not establish that no market edge can exist outside that frozen research
universe.

## Evidence semantics

The aggregate remains labeled:

`RETROSPECTIVE_ALREADY_SEEN`

with:

`untouched_oos = false`

and output kind:

`RETROSPECTIVE_CONTINUOUS_STABILITY_HYPOTHESIS_NOT_VALIDATED`.

Because the continuous-stability shortlist is empty, there are no frozen
hypotheses to carry forward.

The frozen aggregate also records:

- protocol fingerprint:
  `0fe6f992f0d6c27b1d7998561005f37b07f89c8715edd874ee8eb8f8d79ca7e0`;
- feature evidence fingerprint:
  `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`;
- outcome evidence fingerprint:
  `b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117`.

## Reserved robustness

The reserved block remains unopened:

2023-01-01 through 2026-08-20.

DEC-458 does not authorize opening it.

With zero frozen continuous-stability hypotheses, there is also no EXP-064
hypothesis set available for robustness testing under the current protocol.

## Locks preserved

DEC-458 keeps false:

- rerun;
- retry;
- replacement run;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

The reviewed evidence itself also preserves
`source_access_authorized=false`,
`historical_execution_authorized=false`, and
`historical_result_authorized=false`; those evidence-contract fields do not
retroactively alter the fact that the single DEC-457 runtime completed.

## Frozen review source

Review source:

`src/fmp/discovery/exp064_historical_result_review.py`

blob:

`c5878685950e14a632b4eb8d2616d9540afb12d2`.

Focused tests:

`tests/test_phase8a_exp064_historical_result_review.py`

blob:

`258aa9fbe71fae63b805d08a0112aef229cb205f`.

## Next gate

The next gate is:

`EXPLICIT_POST_EXP064_RESEARCH_DIRECTION_DECISION`

Any successor research decision must treat the EXP-064 result as already-seen
evidence. It may not weaken or redefine DEC-452 retroactively, rescue failed
hypotheses, rerun EXP-064, or claim fresh validation from 2015-2022.
