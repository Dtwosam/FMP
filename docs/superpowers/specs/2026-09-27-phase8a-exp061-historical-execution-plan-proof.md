# Phase 8A — EXP-061 Repository-Hosted Historical Execution Plan Proof

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY READ-ONLY PROOF / NOT DISPATCHED  
**Decision:** DEC-287  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-286

## Purpose

DEC-287 adds a repository-hosted read-only proof for the exact DEC-286 historical execution plan on merged `main`.

It exists only to prove that the live EXP-061 workflow inventory still contains the frozen proof as run number 1, that no historical-result attempt exists yet, and that the only future target remains workflow run number 2 / attempt 1.

It does not dispatch EXP-061.

## Frozen predecessor binding

DEC-287 pins:

- DEC-284 reviewed-plan source blob `14d9c559eaa33e5cb217baaf3ed2597091735b18`;
- DEC-285 historical execution authorization blob `30258e076f6a786c977fac8c588ac2b22aeed66e`;
- activated EXP-061 CLI blob `477aa9e8de4452e6444d1ee4361218aca445180d`;
- DEC-286 historical execution operator blob `a711b14fb613f1c9952f5b2a6bf85d892bd2c4a5`;
- DEC-286 operator CLI blob `1f43e1218072918d2ebb33b2c312ba8e950881f9`;
- active EXP-061 discovery workflow blob `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- pinned runtime requirements blob `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## Read-only proof workflow

Workflow:

`.github/workflows/phase8a-exp061-historical-execution-plan.yml`

Git blob:

`6f4b6a04291465f0f32f1f8e9276ff4a62417ec2`

The workflow:

- triggers only on pushes to `main` affecting the proof workflow or its DEC-285/286 source surface;
- grants only `contents: read` and `actions: read`;
- has no manual dispatch, schedule, or pull-request trigger;
- checks out exact merged `main`;
- requires HEAD, `origin/main`, and `GITHUB_SHA` to match;
- verifies the frozen DEC-284/285/286 source identities;
- installs the pinned runtime without editable checkout;
- requires a clean worktree;
- fetches current main metadata and current workflow-dispatch run inventory through read-only GitHub API calls;
- invokes only the DEC-286 `plan` command;
- validates the slot-available state, proof run number, target run number, and all downstream locks;
- uploads exactly one immutable execution-plan artifact.

## Required merged-main proof

A successful DEC-287 proof must show:

- operator decision `DEC-286`;
- authorization decision `DEC-285`;
- expected head equals merged main;
- frozen proof run id `36319888985`;
- proof run count `1`;
- proof workflow run number `1`;
- historical-result attempt count `0`;
- historical-result slot consumed `false`;
- target workflow run number `2`;
- target run attempt `1`;
- exact future command `gh workflow run phase8a-exp061-discovery.yml --ref main`;
- historical execution source authorization `true`;
- historical discovery execution authorization `true`;
- discovery-result authorization `true`.

It must also prove false:

- historical-result dispatch authorization;
- execute mode;
- rerun;
- retry;
- replacement;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Prohibited actions

DEC-287 must not:

- invoke `gh workflow run` as a shell action;
- call a workflow-dispatch REST endpoint;
- invoke any execute or advance mode;
- rerun or retry EXP-061;
- create a replacement historical attempt;
- download historical feature/outcome result inputs for discovery execution;
- create cell or aggregate discovery-result artifacts;
- claim a historical discovery result.

DEC-287 consumes no historical-result slot.

## Focused tests

Focused proof workflow tests:

`tests/test_phase8a_exp061_historical_execution_plan_proof.py`

Git blob:

`95a4bb6dbcab6cef3fdec3cbac7bef09bb952311`

They pin main-push-only scope, read-only permissions, exact DEC-284/285/286 source identities, clean-checkout behavior, plan-only invocation, run-#1 proof identity, run-#2 target identity, absence of direct dispatch commands, and plan-only artifact persistence.

## Next gate

Only after DEC-287 merges and its merged-main proof succeeds may the exact non-expired plan artifact be frozen by a later reviewed-proof decision.

A one-shot historical executor may be considered only after that reviewed proof is merged.
