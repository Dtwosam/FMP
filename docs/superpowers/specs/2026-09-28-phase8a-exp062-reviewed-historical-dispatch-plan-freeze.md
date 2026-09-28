# Phase 8A — EXP-062 Reviewed Historical Dispatch Plan Freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO DISPATCH  
**Decision:** DEC-322  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-321

## Purpose

DEC-322 adds a deterministic freeze builder for a valid future DEC-321 reviewed
dispatch-plan proof.

It does not create runtime evidence, does not authorize runtime dispatch, and does not
provide an executor.

## Required review

The DEC-321 input must prove:

- successful DEC-320 run #1 / attempt 1;
- one proof job and one non-expired artifact;
- exact DEC-319 / DEC-318 identities;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- source dispatch contract true;
- actual dispatch, executor availability, execute mode, rerun/retry/replacement,
  reserved data, candidate, Phase 8B, demo/live, real-money, and trading false;
- exact DEC-320/319/318/317 source-blob map.

Run/job/artifact IDs and plan hashes are preserved from the real review; they are not
invented by DEC-322.

## Output

A valid review produces:

- decision `DEC-322`;
- stage `EXP062_HISTORICAL_DISPATCH_PLAN_REVIEWED_AND_FROZEN`;
- exact review runtime identities and plan hashes;
- frozen future command;
- deterministic `freeze_fingerprint_sha256`.

Actual dispatch and executor availability remain false.

## Next gate

After real DEC-320 evidence exists and passes DEC-321/322, a separate concrete
dispatch-plan runtime evidence binding must occur before any one-shot executor is
implemented.
