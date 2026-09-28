# Phase 8A — EXP-062 Historical Execution Plan Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / NO DISPATCH  
**Decision:** DEC-314  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-311, DEC-312, DEC-313

## Purpose

DEC-314 adds a repository-hosted, push-to-main proof of the exact DEC-313 historical
execution plan.

The proof runs only the planner. It never executes the future discovery dispatch
command.

## Trigger and permissions

The workflow:

- runs only on pushes to `main` touching the frozen proof/runtime/operator stack;
- requires workflow run #1 / attempt 1;
- checks out exact merged main;
- uses `contents: read` and `actions: read` only;
- has no `actions: write` permission;
- has no `workflow_dispatch`, pull-request, or scheduled trigger.

## Frozen source identities

DEC-314 requires exact Git blobs for:

- DEC-311 plan freeze:
  `e3274118b37066efe2869d554e78e6b68e64b32a`;
- DEC-312 execution authorization:
  `aa8cfb25e3d78c0c72da4b22898c1263a42548ba`;
- activated EXP-062 CLI:
  `773784d0770d54b1d3e41fba2057b9314a090034`;
- DEC-313 execution operator:
  `7f21ccf59de9605c7fab45b4506f947ffae69cab`;
- DEC-313 operator CLI:
  `9ecb3f47d7e68461e4a7d893ad5862d7e78a1fc8`;
- active discovery workflow:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`;
- runtime requirements:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## Proof behavior

The workflow fetches current main and the exact manual-main EXP-062 discovery
inventory, then invokes only:

`python scripts/phase8a_exp062_historical_execution_operator.py plan`

A valid proof requires:

- DEC-313 / DEC-312 identities;
- exact current merged-main head;
- stage `EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE`;
- frozen proof run `36358289723` remains workflow run #1;
- zero historical-result attempts;
- unconsumed slot;
- target workflow run #2 / attempt 1;
- exact future plan command:
  `gh workflow run phase8a-exp062-discovery.yml --ref main`;
- execution source/runtime/result flags true only as defined by DEC-312;
- dispatch, execute mode, rerun/retry/replacement, reserved-data, candidate,
  Phase 8B, demo/live, real-money, and trading flags false.

The command is validated only as JSON data.

## Artifact

A successful proof uploads only:

`historical-execution-plan.json`

under:

`exp062-dec314-historical-execution-plan-<merged-main-sha>`

No cell or aggregate discovery result is produced.

## Next gate

After a real successful merged-main DEC-314 proof exists, its exact run, job, artifact
digest, and raw/canonical plan hashes must be reviewed and frozen before any one-shot
dispatcher can be considered.
