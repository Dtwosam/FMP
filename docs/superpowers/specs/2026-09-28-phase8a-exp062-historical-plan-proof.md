# Phase 8A — EXP-062 Repository-Hosted Historical Plan Proof

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY READ-ONLY PROOF WORKFLOW / NO HISTORICAL DISPATCH  
**Decision:** DEC-309  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-308

## Purpose

DEC-309 adds a repository-hosted proof that can run on the first merged-main push of
its own frozen workflow/source set and prove that DEC-308 still sees the single
EXP-062 historical slot as available.

The workflow is read-only. It uploads only the planner JSON. It cannot dispatch the
EXP-062 discovery workflow.

## Trigger and identity

The proof workflow is
`.github/workflows/phase8a-exp062-historical-plan.yml`.

It is triggered only by a push to `main` touching the proof workflow or its pinned
DEC-306/307/308 planning dependencies.

The workflow requires:

- repository `Dtwosam/FMP`;
- event `push`;
- ref `refs/heads/main`;
- workflow run number `1`;
- run attempt `1`;
- checked-out `main`, local HEAD, origin/main, and `GITHUB_SHA` all identical.

## Frozen source identities

Before planning, DEC-309 checks the exact Git blob identities for:

- DEC-306 runtime proof freeze;
- DEC-307 historical-slot authorization;
- DEC-308 historical operator;
- DEC-308 CLI;
- active EXP-062 discovery workflow;
- pinned runtime requirements.

Any source drift fails closed.

## Read-only plan proof

The workflow fetches:

- current GitHub `main` metadata;
- current EXP-062 manual-main discovery run inventory.

It then executes only:

`python scripts/phase8a_exp062_historical_operator.py plan ...`

The resulting JSON must prove:

- DEC-308 / DEC-307 identities;
- expected head equals the merged-main `GITHUB_SHA`;
- exact frozen proof run `36358289723`;
- one proof run and zero historical-result attempts;
- historical slot available and unconsumed;
- planned command equals
  `gh workflow run phase8a-exp062-discovery.yml --ref main`;
- historical dispatch and execute mode remain false;
- all downstream/reserved/demo/live/trading authority remains false.

The command above is inspected as JSON data only. The workflow does not execute it.

## Artifact

A successful proof uploads exactly:

`exp062-dec309-historical-plan-<merged-main-sha>`

containing only `historical-plan.json`.

No cell or aggregate discovery artifact is created.

## Safety boundary

Historical-result dispatch/execution/result production, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

The next gate after a real successful DEC-309 merged-main run is a separate immutable
review/freeze of that exact run, artifact digest, raw plan hash, and canonical plan
hash before any one-shot executor can be considered.
