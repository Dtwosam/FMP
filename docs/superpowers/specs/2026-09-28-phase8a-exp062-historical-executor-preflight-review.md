# Phase 8A — EXP-062 Historical Executor Preflight Proof Review

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED  
**Decision:** DEC-327  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-323, DEC-324, DEC-325, DEC-326

## Purpose

DEC-327 predeclares the reviewer for a future successful DEC-326 read-only historical
executor-preflight proof.

It does not dispatch or execute historical discovery.

## Source binding

The reviewer pins:

- DEC-326 proof workflow blob:
  `8df8398508fd5e5b3d3fb2b215500d4ef93ac7bc`;
- DEC-323 runtime-freeze blob:
  `44815c9ff23fcd022346558e8c043673154ca0b3`;
- DEC-324 executor-contract blob:
  `12d514e86a2b458dd692810450e69b30f554a6bd`;
- DEC-325 preflight blob:
  `7aca87376dcbcbb4b30ea72a4da6b6f502799bd8`;
- DEC-325 preflight CLI blob:
  `a7a9ce90ab42b746fea1ef3ee5880abe2992fbf7`;
- active discovery workflow blob:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`.

## Required runtime proof shape

A valid DEC-326 proof must be:

- workflow `phase8a-exp062-historical-executor-preflight`;
- event `push`;
- branch `main`;
- exact expected merged-main head;
- workflow run #1 / attempt 1;
- terminal success;
- exactly one job:
  `read-only-historical-executor-preflight`, success;
- exactly one non-expired artifact:
  `exp062-dec326-historical-executor-preflight-<head>`;
- artifact digest formatted as SHA-256.

## Preflight-content review

The downloaded `historical-executor-preflight.json` must revalidate under DEC-325
and must prove:

- DEC-325 / DEC-324 identities;
- exact proof head;
- stage `EXP062_ONE_SHOT_EXECUTOR_PREFLIGHT_SLOT_AVAILABLE`;
- frozen gate proof remains the only discovery run;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact future discovery command as evidence only;
- executor source authorization true;
- executor availability, dispatch, execute mode, rerun/retry/replacement, reserved
  data, candidate, Phase 8B, demo/live, real-money, and trading false.

DEC-327 records both raw and canonical SHA-256 hashes of the preflight JSON.

## Safety boundary

DEC-327 adds no executor and no execute mode. A valid review only proves that the
read-only preflight is internally consistent and the one-shot slot remains available.

## Next gate

After actual DEC-326 runtime evidence passes DEC-327, a separate immutable concrete
executor-preflight proof freeze must bind its exact run, job, artifact, digest, and
preflight hashes before any one-shot executor workflow is considered.
