# Phase 8A — EXP-061 Repository-Hosted Historical Plan Proof

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY READ-ONLY PROOF / NOT DISPATCHED  
**Decision:** DEC-283  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-282

## Purpose

DEC-283 adds a repository-hosted read-only proof for the exact DEC-282 historical-slot plan on merged `main`.

It exists only to prove the live one-slot state immediately before any separate historical executor source is considered.

## Frozen predecessor binding

DEC-283 binds:

- DEC-281 historical authorization source blob `1eab1cee2fc81441cf1c3168cc73275cd29addf5`;
- DEC-282 operator source blob `1ffef37d94b04a8206f665c375dc0b2642c4caa9`;
- DEC-282 CLI blob `4d667d05ef2a5bd672cb9d98a81f13dd2ba9370c`;
- DEC-280 reviewed-proof source blob `fbed3788ab0c1c1e00dccfe0f84a293ff04f6ccd`;
- active locked EXP-061 workflow blob `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- pinned runtime requirements blob `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## Read-only workflow

Workflow:

`.github/workflows/phase8a-exp061-historical-plan.yml`

Git blob:

`7c2d7409d1a05ce287cc36f5371a85273a6a027b`

The workflow:

- triggers only on pushes to `main` affecting the plan workflow or its frozen DEC-281/282 source surface;
- grants only `contents: read` and `actions: read`;
- has no manual dispatch, schedule, or pull-request trigger;
- checks out exact merged `main`;
- requires HEAD, `origin/main`, and `GITHUB_SHA` to match;
- verifies the frozen DEC-280/281/282 blob identities before planning;
- installs the pinned runtime without editable checkout;
- requires a clean worktree after dependency installation;
- fetches current main metadata and current exact EXP-061 manual-main run history through read-only GitHub API calls;
- invokes only the DEC-282 `plan` command;
- writes the plan under `RUNNER_TEMP`;
- validates the slot-available state and every downstream lock;
- uploads exactly one immutable plan artifact.

## Required merged-main proof

A successful DEC-283 run must prove:

- `decision = DEC-282`;
- `authorization_decision = DEC-281`;
- expected head equals the merged-main workflow head;
- exact frozen proof run id `36319888985`;
- proof run count = 1;
- historical-result attempt count = 0;
- historical-result slot consumed = false;
- stage `EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE`;
- exact planned command `gh workflow run phase8a-exp061-discovery.yml --ref main`;
- DEC-281 source-slot authorization = true.

It must also prove false:

- historical-result dispatch authorization;
- execute mode;
- historical discovery execution authorization;
- discovery-result authorization;
- rerun;
- retry;
- replacement;
- reserved robustness access;
- candidate compilation;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Prohibited actions

DEC-283 must not:

- call `gh workflow run` as an executable shell action;
- call a workflow-dispatch REST endpoint;
- invoke any execute or advance mode;
- rerun or retry EXP-061;
- create a replacement historical attempt;
- download historical feature/outcome cell artifacts;
- create cell or aggregate discovery-result artifacts;
- claim a historical discovery result.

DEC-283 consumes no historical-result slot.

## Focused tests

Focused workflow tests:

`tests/test_phase8a_exp061_historical_plan_proof.py`

Git blob:

`e25e8cbb435a106ca22e29d2e810e9c23cc25892`

They pin the main-push-only trigger, read-only permissions, frozen source identities, clean-checkout behavior, plan-only CLI use, exact slot proof assertions, lack of direct dispatch commands, and plan-only artifact persistence.

## Next gate

Only after DEC-283 merges and its merged-main workflow succeeds may a later separate one-shot historical executor source be considered.

That executor must independently bind the successful non-expired DEC-283 plan artifact, recheck the live DEC-282 plan twice immediately before any write, and still keep reserved 2023-2026 data, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked until the historical result itself is reviewed.
