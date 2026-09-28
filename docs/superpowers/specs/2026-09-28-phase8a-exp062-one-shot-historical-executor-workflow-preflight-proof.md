# Phase 8A — EXP-062 One-Shot Historical Executor Workflow-Preflight Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY WORKFLOW PREFLIGHT PROOF / NO DISPATCH  
**Decision:** DEC-344  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-342, DEC-343

## Purpose

DEC-344 adds a repository-hosted proof of the DEC-343 one-shot historical executor
workflow preflight.

The workflow runs only on merged main, invokes only the DEC-343 `plan` surface, and
proves that the sole EXP-062 historical-result slot remains empty with target run #2 /
attempt 1.

It never submits the historical workflow.

## Trigger and permissions

The workflow:

- runs only on pushes to `main` touching the frozen workflow-preflight stack;
- requires workflow run #1 / attempt 1;
- checks out exact merged main;
- uses only `contents: read` and `actions: read`;
- has no `actions: write` permission;
- has no `workflow_dispatch`, pull-request, or scheduled trigger.

## Frozen source identities

DEC-344 pins:

- DEC-342 workflow contract:
  `d87bf8f4fc3ad8fc081760c1250dc0f8dc9ffadc`;
- DEC-343 workflow preflight:
  `1339dd02256b9d3fc51b2a312a2272fd5d949796`;
- DEC-343 plan-only CLI:
  `8b2e190e75f378a52fa66ad61b0e1bbadacb343b`;
- active discovery workflow:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`;
- runtime requirements:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## Proof behavior

The workflow fetches current main plus the exact manual-main EXP-062 discovery run
inventory and invokes only:

`python scripts/phase8a_exp062_one_shot_historical_executor_workflow_preflight.py plan`

A valid proof requires:

- DEC-343 / DEC-342 identities;
- exact current merged-main head;
- slot-available preflight stage;
- frozen proof run `36358289723` remains the only discovery run;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact future discovery command as evidence only;
- both source authorizations true;
- executor availability, actual dispatch, execute mode, rerun/retry/replacement,
  reserved data, candidate, Phase 8B, demo/live, real-money, and trading flags false.

## Artifact

A successful proof uploads only:

`one-shot-historical-executor-workflow-preflight.json`

under:

`exp062-dec344-one-shot-historical-executor-workflow-preflight-<merged-main-sha>`

No discovery result is produced.

## Next gate

After a real successful DEC-344 proof exists, its exact run, job, artifact digest,
and raw/canonical preflight hashes must be reviewed and frozen before any
dispatch-capable executor workflow is considered.
