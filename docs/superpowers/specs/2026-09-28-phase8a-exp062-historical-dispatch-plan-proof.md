# Phase 8A — EXP-062 Historical Dispatch Plan Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / NO DISPATCH  
**Decision:** DEC-320  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-317, DEC-318, DEC-319

## Purpose

DEC-320 adds a repository-hosted proof of the DEC-319 current-main dispatch plan.

It runs only on a push to merged main, has read-only permissions, and never submits
the EXP-062 discovery workflow.

## Frozen source stack

The workflow pins:

- DEC-317 runtime freeze blob:
  `9626f6cd1c66a67d91dd3acf743e120ea8d2e9c0`;
- DEC-318 dispatch authorization blob:
  `b5360751459212cfabb37a3dd7758fe0cc28c4a6`;
- DEC-319 dispatch operator blob:
  `72c1cd881c004c91c2cf7c3797e00d68e3a27056`;
- DEC-319 operator CLI blob:
  `9f41465f287daccc5f7685453129bc20916bec17`;
- active discovery workflow blob:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`;
- runtime requirements blob:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## Proof behavior

The workflow requires:

- first workflow run / attempt `1 / 1`;
- exact push to `main`;
- exact merged-main checkout and origin/main identity;
- clean checkout;
- read-only GitHub API fetch of current main and EXP-062 discovery inventory.

It invokes only:

`python scripts/phase8a_exp062_historical_dispatch_operator.py plan`

A valid proof must show:

- DEC-319 / DEC-318 identities;
- stage `EXP062_ONE_SHOT_DISPATCH_SLOT_AVAILABLE`;
- frozen proof run `36358289723` remains the only discovery run;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact command text:
  `gh workflow run phase8a-exp062-discovery.yml --ref main`;
- source dispatch contract true;
- actual dispatch, executor availability, execute mode, rerun/retry/replacement,
  reserved data, candidate, Phase 8B, demo/live, real-money, and trading all false.

The command is validated only as JSON data.

## Artifact

A successful proof uploads only:

`historical-dispatch-plan.json`

as:

`exp062-dec320-historical-dispatch-plan-<merged-main-sha>`.

No historical discovery, cell result, or aggregate result is executed or produced.

## Next gate

After a real successful DEC-320 proof exists, its run/job/artifact/plan hashes must be
reviewed and frozen before any one-shot dispatcher can be implemented.
