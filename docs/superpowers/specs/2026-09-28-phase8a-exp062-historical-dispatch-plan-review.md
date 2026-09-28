# Phase 8A — EXP-062 Historical Dispatch Plan Proof Review

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED  
**Decision:** DEC-321  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-317, DEC-318, DEC-319, DEC-320

## Purpose

DEC-321 predeclares the reviewer for a future successful DEC-320 read-only dispatch
plan proof.

It validates runtime evidence and plan bytes only. It cannot dispatch historical
discovery.

## Source binding

The reviewer pins:

- DEC-320 proof workflow blob:
  `259900792ff7b2126b7bee4577f05ba7abdb0f25`;
- DEC-317 runtime freeze blob:
  `9626f6cd1c66a67d91dd3acf743e120ea8d2e9c0`;
- DEC-318 authorization blob:
  `b5360751459212cfabb37a3dd7758fe0cc28c4a6`;
- DEC-319 operator blob:
  `72c1cd881c004c91c2cf7c3797e00d68e3a27056`;
- DEC-319 operator CLI blob:
  `9f41465f287daccc5f7685453129bc20916bec17`;
- active discovery workflow blob:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`.

## Required runtime proof

A valid DEC-320 proof must be:

- workflow `phase8a-exp062-historical-dispatch-plan`;
- push on `main`;
- exact expected merged-main head;
- run #1 / attempt 1;
- terminal success;
- exactly one successful job:
  `read-only-historical-dispatch-plan`;
- exactly one non-expired artifact:
  `exp062-dec320-historical-dispatch-plan-<head>`;
- SHA-256 artifact digest.

## Plan review

The downloaded plan must revalidate under DEC-319 and prove:

- DEC-319 / DEC-318 identities;
- available one-shot dispatch slot;
- gate proof remains the only EXP-062 discovery run;
- zero historical-result attempts;
- target run #2 / attempt 1;
- exact command text;
- source dispatch contract true;
- actual dispatch, executor availability, execute mode, rerun/retry/replacement,
  reserved data, candidate, Phase 8B, demo/live, real-money, and trading false.

DEC-321 records raw and canonical plan SHA-256 hashes.

## Next gate

After real DEC-320 evidence passes DEC-321, a separate immutable dispatch-plan proof
freeze must bind its exact run/job/artifact/digest/plan hashes before any one-shot
executor can exist.
