# Phase 8A — EXP-062 Historical Executor Preflight Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY PREFLIGHT PROOF / NO DISPATCH  
**Decision:** DEC-326  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-323, DEC-324, DEC-325

## Purpose

DEC-326 adds a repository-hosted, push-to-main, first-run/attempt-1 proof of the exact
DEC-325 historical executor preflight.

The proof runs only the read-only preflight planner. It never submits the historical
discovery workflow.

## Trigger and permissions

The workflow:

- runs only on pushes to `main` touching the frozen preflight stack;
- requires workflow run #1 / attempt 1;
- checks out exact merged main;
- uses `contents: read` and `actions: read` only;
- has no `actions: write` permission;
- has no `workflow_dispatch`, pull-request, or scheduled trigger.

## Frozen source identities

DEC-326 requires exact Git blobs for:

- DEC-323 dispatch runtime freeze:
  `44815c9ff23fcd022346558e8c043673154ca0b3`;
- DEC-324 executor contract:
  `12d514e86a2b458dd692810450e69b30f554a6bd`;
- DEC-325 executor preflight:
  `7aca87376dcbcbb4b30ea72a4da6b6f502799bd8`;
- DEC-325 preflight CLI:
  `a7a9ce90ab42b746fea1ef3ee5880abe2992fbf7`;
- active discovery workflow:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`;
- runtime requirements:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## Proof behavior

The workflow fetches current main and the exact manual-main EXP-062 discovery
inventory, then invokes only:

`python scripts/phase8a_exp062_historical_executor_preflight.py plan`

A valid proof requires:

- DEC-325 / DEC-324 identities;
- exact current merged-main head;
- stage `EXP062_ONE_SHOT_EXECUTOR_PREFLIGHT_SLOT_AVAILABLE`;
- frozen proof run `36358289723` remains the only discovery run;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact future discovery command as evidence only;
- executor source authorization true;
- executor availability, dispatch, execute mode, rerun/retry/replacement, reserved
  data, candidate, Phase 8B, demo/live, real-money, and trading flags false.

## Artifact

A successful proof uploads only:

`historical-executor-preflight.json`

under:

`exp062-dec326-historical-executor-preflight-<merged-main-sha>`

No discovery result is produced.

## Next gate

After a real successful merged-main DEC-326 proof exists, its exact run, job, artifact
digest, and raw/canonical preflight hashes must be reviewed and frozen before any
one-shot executor workflow can be considered.
