# Phase 8A — EXP-062 Historical Execution Plan Proof Review

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED  
**Decision:** DEC-315  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-311, DEC-312, DEC-313, DEC-314

## Purpose

DEC-315 predeclares the reviewer for a future successful DEC-314 read-only historical
execution-plan proof.

It does not dispatch or execute historical discovery.

## Source binding

The reviewer pins:

- DEC-314 proof workflow blob:
  `d2b2e4fcc2a39e614dda98c890ec13b6387725e8`;
- DEC-313 execution operator blob:
  `7f21ccf59de9605c7fab45b4506f947ffae69cab`;
- DEC-313 operator CLI blob:
  `9ecb3f47d7e68461e4a7d893ad5862d7e78a1fc8`;
- DEC-312 execution authorization blob:
  `aa8cfb25e3d78c0c72da4b22898c1263a42548ba`;
- activated EXP-062 CLI blob:
  `773784d0770d54b1d3e41fba2057b9314a090034`;
- active discovery workflow blob:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`;
- DEC-311 historical-plan freeze blob:
  `e3274118b37066efe2869d554e78e6b68e64b32a`.

## Required runtime proof shape

A valid DEC-314 proof must be:

- workflow `phase8a-exp062-historical-execution-plan`;
- event `push`;
- branch `main`;
- exact expected merged-main head;
- workflow run #1 / attempt 1;
- terminal success;
- exactly one job:
  `read-only-historical-execution-plan`, success;
- exactly one non-expired artifact:
  `exp062-dec314-historical-execution-plan-<head>`;
- artifact digest formatted as SHA-256.

## Plan-content review

The downloaded `historical-execution-plan.json` must revalidate under DEC-313 and
must prove:

- DEC-313 / DEC-312 identities;
- exact proof head;
- stage `EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE`;
- gate proof remains the only discovery run;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact future discovery command;
- historical execution source/runtime/result authorization true only as frozen by
  DEC-312;
- dispatch, execute mode, rerun/retry/replacement, reserved data, candidate,
  Phase 8B, demo/live, real-money, and trading remain false.

DEC-315 records both raw and canonical SHA-256 hashes of the plan.

## Safety boundary

DEC-315 adds no dispatcher and no execute mode. A valid review only proves that the
read-only execution plan is internally consistent and the one-shot slot is still
available.

## Next gate

After actual DEC-314 runtime evidence passes DEC-315, a separate immutable concrete
execution-plan proof freeze must bind its exact run, job, artifact, digest, and plan
hashes before any one-shot dispatcher is considered.
