# Phase 8A — EXP-062 Reviewed Historical Executor Preflight Freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO EXECUTOR  
**Decision:** DEC-328  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-327

## Purpose

DEC-328 adds a deterministic freeze builder for a valid DEC-327 reviewed historical
executor-preflight proof.

The source may merge before DEC-326 runtime evidence exists. It does not fabricate
run, job, artifact, or preflight identities. Those values must come from a real
DEC-327 review and are preserved unchanged in the freeze result.

## Required reviewed state

The input must be an exact DEC-327 review with:

- stage `EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_PROOF_REVIEWED_SLOT_AVAILABLE`;
- proof workflow `phase8a-exp062-historical-executor-preflight`;
- proof run #1 / attempt 1 / success on the supplied merged-main head;
- positive proof run, job, and artifact IDs;
- a valid SHA-256 artifact digest;
- raw and canonical preflight SHA-256 values;
- DEC-325 preflight identity;
- frozen gate-proof run `36358289723`;
- zero historical-result attempts;
- unconsumed historical-result slot;
- target run #2 / attempt 1;
- executor source contract true;
- executor availability, dispatch, execute mode, and all downstream authorities false.

The exact DEC-323/324/325/326 source-blob map emitted by DEC-327 must also match.

## Freeze output

A valid input produces:

- decision `DEC-328`;
- stage `EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_REVIEWED_AND_FROZEN`;
- exact proof run/job/artifact identities from the review;
- exact artifact digest and preflight hashes;
- exact reviewed source-blob map;
- frozen target run #2 / attempt 1;
- frozen command text:
  `gh workflow run phase8a-exp062-discovery.yml --ref main`;
- a deterministic canonical `freeze_fingerprint_sha256`.

DEC-328 does not execute that command.

## Safety boundary

DEC-328 keeps false:

- historical executor availability;
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

## Next gate

After real DEC-326 evidence exists and passes DEC-327/328, a separate concrete runtime
evidence decision must bind the actual merged-main run/job/artifact/hash values before
any one-shot executor workflow can be considered.
