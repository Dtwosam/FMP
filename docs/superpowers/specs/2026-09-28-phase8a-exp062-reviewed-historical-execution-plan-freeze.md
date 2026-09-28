# Phase 8A — EXP-062 Reviewed Historical Execution Plan Freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO DISPATCH  
**Decision:** DEC-316  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-315

## Purpose

DEC-316 adds a deterministic freeze builder for a valid DEC-315 reviewed historical
execution-plan proof.

The source may merge before DEC-314 runtime evidence exists. It does not fabricate
run, job, artifact, or plan identities. Those values must come from a real DEC-315
review and are preserved unchanged in the freeze result.

## Required reviewed state

The input must be an exact DEC-315 review with:

- stage `EXP062_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE`;
- proof workflow `phase8a-exp062-historical-execution-plan`;
- proof run #1 / attempt 1 / success on the supplied merged-main head;
- positive proof run, job, and artifact IDs;
- a non-malformed SHA-256 artifact digest;
- raw and canonical plan SHA-256 values;
- DEC-313 execution-plan identity;
- frozen gate-proof run `36358289723`;
- zero historical-result attempts;
- unconsumed historical-result slot;
- target run #2 / attempt 1;
- DEC-312 execution/result authority true only inside that exact future runtime;
- dispatch/execute mode and all downstream authorities false.

The exact DEC-314/313/312/311 source-blob map emitted by DEC-315 must also match.

## Freeze output

A valid input produces:

- decision `DEC-316`;
- stage `EXP062_HISTORICAL_EXECUTION_PLAN_REVIEWED_AND_FROZEN`;
- exact proof run/job/artifact identities from the review;
- exact artifact digest and plan hashes;
- exact reviewed source-blob map;
- frozen target run #2 / attempt 1;
- frozen command text:
  `gh workflow run phase8a-exp062-discovery.yml --ref main`;
- a deterministic canonical `freeze_fingerprint_sha256`.

DEC-316 does not execute that command.

## Safety boundary

DEC-316 keeps false:

- historical-result dispatch;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 robustness access;
- candidate compilation / promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

Historical execution/result production remain true only as the already-frozen DEC-312
one-shot runtime capability for future run #2 / attempt 1. The freeze itself creates no
run.

## Next gate

After real DEC-314 evidence exists and passes DEC-315/316, a separate concrete runtime
evidence decision must bind the actual merged-main run/job/artifact/hash values before
any one-shot historical dispatcher can be considered.
