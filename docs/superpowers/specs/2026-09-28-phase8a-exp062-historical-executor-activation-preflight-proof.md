# Phase 8A — EXP-062 Historical Executor Activation-Preflight Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY ACTIVATION PREFLIGHT PROOF / NO DISPATCH  
**Decision:** DEC-332  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-330, DEC-331

## Purpose

DEC-332 adds a repository-hosted, push-to-main, first-run/attempt-1 proof of the exact
DEC-331 historical executor activation preflight.

The proof runs only the read-only activation-preflight planner. It never submits the
historical discovery workflow.

## Trigger and permissions

The workflow:

- runs only on pushes to `main` touching the frozen activation-preflight stack;
- requires workflow run #1 / attempt 1;
- checks out exact merged main;
- uses `contents: read` and `actions: read` only;
- has no `actions: write` permission;
- has no `workflow_dispatch`, pull-request, or scheduled trigger.

## Frozen source identities

DEC-332 requires exact Git blobs for:

- DEC-330 executor activation contract:
  `35edfdfed85e52ebd723f2637060f4f102e7920b`;
- DEC-331 executor activation preflight:
  `1d88fc3ad9dfce5ee61f1a5f9bdb304b3d7f8d1a`;
- DEC-331 activation-preflight CLI:
  `e91a2a2acb0e00d9d458ed5e15ecf746411caec7`;
- active discovery workflow:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`;
- runtime requirements:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## Proof behavior

The workflow fetches current main and the exact manual-main EXP-062 discovery
inventory, then invokes only:

`python scripts/phase8a_exp062_historical_executor_activation_preflight.py plan`

A valid proof requires:

- DEC-331 / DEC-330 identities;
- exact current merged-main head;
- stage `EXP062_ONE_SHOT_EXECUTOR_ACTIVATION_PREFLIGHT_SLOT_AVAILABLE`;
- frozen proof run `36358289723` remains the only discovery run;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact future discovery command as evidence only;
- executor activation source authorization true;
- executor availability, dispatch, execute mode, rerun/retry/replacement, reserved
  data, candidate, Phase 8B, demo/live, real-money, and trading flags false.

## Artifact

A successful proof uploads only:

`historical-executor-activation-preflight.json`

under:

`exp062-dec332-historical-executor-activation-preflight-<merged-main-sha>`

No discovery result is produced.

## Next gate

After a real successful merged-main DEC-332 proof exists, its exact run, job, artifact
digest, and raw/canonical preflight hashes must be reviewed and frozen before any
one-shot executor workflow can be considered.
