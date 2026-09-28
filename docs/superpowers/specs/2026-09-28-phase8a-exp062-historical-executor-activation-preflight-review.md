# Phase 8A — EXP-062 Historical Executor Activation-Preflight Review

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED  
**Decision:** DEC-333  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-329, DEC-330, DEC-331, DEC-332

## Purpose

DEC-333 predeclares the reviewer for a future successful DEC-332 read-only executor
activation-preflight proof.

It does not dispatch or execute historical discovery.

## Source binding

The reviewer pins:

- DEC-332 proof workflow blob:
  `d396cd27cabd2b8559d8d86121f9c59dc045c7ad`;
- DEC-329 executor-preflight runtime freeze blob:
  `f9f727ae23b88fe52ca9c41739f04ab26bec0b4e`;
- DEC-330 activation contract blob:
  `35edfdfed85e52ebd723f2637060f4f102e7920b`;
- DEC-331 activation preflight blob:
  `1d88fc3ad9dfce5ee61f1a5f9bdb304b3d7f8d1a`;
- DEC-331 activation-preflight CLI blob:
  `e91a2a2acb0e00d9d458ed5e15ecf746411caec7`;
- active discovery workflow blob:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`.

## Required runtime proof shape

A valid DEC-332 proof must be:

- workflow `phase8a-exp062-historical-executor-activation-preflight`;
- event `push`;
- branch `main`;
- exact expected merged-main head;
- workflow run #1 / attempt 1;
- terminal success;
- exactly one job:
  `read-only-historical-executor-activation-preflight`, success;
- exactly one non-expired artifact:
  `exp062-dec332-historical-executor-activation-preflight-<head>`;
- artifact digest formatted as SHA-256.

## Preflight-content review

The downloaded activation-preflight JSON must revalidate under DEC-331 and must prove:

- DEC-331 / DEC-330 identities;
- exact proof head;
- slot-available activation-preflight stage;
- gate proof remains the only discovery run;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact future discovery command;
- executor activation source authorization true;
- executor availability, dispatch, execute mode, rerun/retry/replacement, reserved
  data, candidate, Phase 8B, demo/live, real-money, and trading remain false.

DEC-333 records both raw and canonical SHA-256 hashes of the preflight.

## Safety boundary

DEC-333 adds no executor and no execute mode. A valid review only proves that the
read-only activation preflight is internally consistent and the one-shot slot is still
available.

## Next gate

After actual DEC-332 runtime evidence passes DEC-333, a separate immutable concrete
activation-preflight proof freeze must bind its exact run, job, artifact, digest, and
preflight hashes before any one-shot executor workflow is considered.
