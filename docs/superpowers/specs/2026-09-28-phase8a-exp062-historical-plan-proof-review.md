# Phase 8A — EXP-062 Historical Plan Proof Review

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PLAN PROOF STILL REQUIRED  
**Decision:** DEC-310  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-306 through DEC-309

## Purpose

DEC-310 adds the read-only reviewer for the future successful DEC-309 repository-hosted
historical-plan proof. It does not create, dispatch, execute, or authorize a historical
discovery run.

The reviewer accepts actual GitHub run/job/artifact metadata plus the downloaded
`historical-plan.json` bytes and an exact expected merged-main head.

## Required proof shape

A valid DEC-309 proof must be:

- workflow `phase8a-exp062-historical-plan`;
- push to `main`;
- workflow run #1 / attempt 1;
- completed successfully on the exact expected head;
- exactly one successful `read-only-historical-plan` job;
- exactly one non-expired artifact named
  `exp062-dec309-historical-plan-<head>` with a valid SHA-256 artifact digest.

The downloaded plan must validate as the exact DEC-308 slot-available plan:

- DEC-307 source authorization intact;
- frozen gate proof run `36358289723` still the only EXP-062 manual-main run;
- zero historical-result attempts;
- slot unconsumed;
- future dispatch command present as plan data only;
- dispatch/execute/result/rerun/retry/replacement authority false;
- reserved 2023-2026 data, candidates, Phase 8B, demo/live, real-money, and trading
  authority false.

DEC-310 records both raw and canonical SHA-256 hashes of the downloaded plan bytes.

## Source binding

The reviewer pins the exact DEC-309 plan-proof workflow, DEC-308 operator and CLI,
DEC-307 historical authorization, and DEC-306 runtime proof freeze Git blobs.

## Safety boundary

DEC-310 remains source-only until actual DEC-309 runtime evidence exists. It grants no
historical-result dispatch or execution authority.

The next gate after a real reviewed DEC-309 proof is an immutable concrete plan-proof
freeze before any historical execution authorization is considered.
