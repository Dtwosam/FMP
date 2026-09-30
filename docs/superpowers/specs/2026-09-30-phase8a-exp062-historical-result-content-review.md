# Phase 8A — EXP-062 Historical Result Content Review

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY ACTUAL RESULT REVIEW / NO DOWNSTREAM AUTHORIZATION  
**Decision:** DEC-440  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-439

## Purpose

DEC-440 reviews the sole successful EXP-062 historical result after the DEC-439
recovery-v2 path produced historical workflow run #2 / attempt 1.

This decision is read-only and source-only. It does not dispatch or rerun EXP-062,
compile candidates, open reserved robustness data, promote any result, enter Phase
8B, or authorize any trading surface.

## Bound historical result

DEC-440 pins the actual historical result:

- workflow `phase8a-exp062-discovery`;
- run `36714210992`;
- run #2 / attempt 1;
- head `013395092804de6b0ef51537081ab8443b8b91be`;
- terminal conclusion `success`;
- exact DEC-334 success shape: 20 successful jobs and 20 non-expired artifacts;
- historical-result slot consumed permanently.

The terminal shape must classify through DEC-334 as:

`EXP062_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED`

before content review is allowed.

## Bound aggregate artifact

The exact aggregate artifact is:

- artifact id `11096592737`;
- name `phase8a-exp062-aggregate-013395092804de6b0ef51537081ab8443b8b91be`;
- artifact digest `sha256:077535bc6e9d9a1d6e8693f873b7552cf8028d793ef79eab175dbbd9970430bc`;
- exact `aggregate-evidence.json` SHA-256
  `bfdf9787e9ee32c30ff29aa70594d7404bc7fc2cb573a60068802d2aacbaa6f3`;
- aggregate evidence fingerprint
  `b8019226fb7fce14c6711834fe16cdbb52795d9ca8996b1ed98ede7ecfba9506`.

The aggregate must also validate through the frozen DEC-298 EXP-062 aggregate
evidence validator.

## Reviewed result

The exact aggregate content is frozen for review as:

- 18 expected cells;
- 18 verified cells;
- 67 discovery-shortlist entries;
- 11 confirmation-frozen candidates;
- 0 validation-accepted candidates;
- evidence label `RETROSPECTIVE_ALREADY_SEEN`;
- `untouched_oos=false`;
- reserved robustness data not opened.

DEC-440 therefore classifies the reviewed result as:

`EXP062_HISTORICAL_RESULT_CONTENT_REVIEWED_NO_VALIDATION_ACCEPTED`

This is an evidence statement, not an authorization to alter thresholds, rerun the
experiment, reuse the consumed historical slot, or promote confirmation-frozen
patterns as validated candidates.

## Locks preserved

DEC-440 keeps false:

- rerun;
- retry;
- replacement run;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Frozen implementation

Reviewer:

`src/fmp/discovery/exp062_historical_result_content_review.py`

Focused tests:

`tests/test_phase8a_exp062_historical_result_content_review.py`

## Next gate

The next safe gate is a deterministic immutable DEC-441 freeze of the reviewed
historical-result identity, aggregate artifact identity/digest, exact aggregate JSON
hash, aggregate evidence fingerprint, and the reviewed 67 / 11 / 0 result counts.

DEC-441 must remain non-authorizing. Any later research direction requires a separate
explicit decision after the immutable result freeze exists.
