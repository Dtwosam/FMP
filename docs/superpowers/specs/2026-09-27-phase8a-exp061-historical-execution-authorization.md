# Phase 8A — EXP-061 Historical Execution Authorization

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY RUNTIME AUTHORIZATION / DISPATCH STILL LOCKED  
**Decision:** DEC-285  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-284

## Purpose

DEC-285 is the first transition that allows the already-frozen EXP-061 historical workflow runtime to pass its execution gate for exactly one future historical-result attempt.

It does **not** dispatch the workflow.

It does **not** authorize any rerun, retry, replacement, 2023-2026 robustness access, candidate compilation, promotion, Phase 8B, demo order, broker mutation, live order, real-money action, or trading.

## Reviewed-proof prerequisite

DEC-285 binds the reviewed DEC-284 proof source:

- decision: `DEC-284`;
- reviewed-proof source blob: `14d9c559eaa33e5cb217baaf3ed2597091735b18`;
- DEC-283 proof run: `36323674455`;
- DEC-283 proof head: `7fd3a9e878bf2760850037548e93dc1e8173c0c1`;
- reviewed plan proves zero historical-result attempts and an unconsumed slot.

The frozen DEC-275 execution flag remains false. DEC-285 supersedes that runtime gate without rewriting DEC-275.

## Exact source stack

DEC-285 requires the unchanged historical research stack:

- active discovery workflow blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- pattern protocol blob: `63b3f0121d6a50eb9e8e62ab666d70eb91791621`;
- pattern miner blob: `495a67699eb5014e52129f0238a2737049fe38e6`;
- market-learning adapter blob: `978a33554fad7e9d78b002778c4896be0af3333a`;
- range-limited loader blob: `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- run-contract blob: `260eb6930673427266463517546969635188b143`;
- legacy DEC-275 workflow-source blob: `68566fc86ff3470cc8b6ebef606becaff9f3450b`;
- runtime requirements blob: `1ff32214dee10d877a067e750cd69ffad96d5fe5`;
- activated public CLI blob: `477aa9e8de4452e6444d1ee4361218aca445180d`.

The active workflow itself is unchanged. Only the public CLI runtime gate changes.

## One-shot runtime identity

The prior fail-closed proof run is confirmed as:

- workflow run number: `1`;
- run attempt: `1`;
- run id: `36319888985`.

Therefore DEC-285 authorizes runtime execution only when the future run has all of these values:

- `GITHUB_ACTIONS=true`;
- repository `Dtwosam/FMP`;
- workflow name `phase8a-exp061-discovery`;
- event `workflow_dispatch`;
- ref `refs/heads/main`;
- workflow run number `2`;
- workflow run attempt `1`;
- runtime `GITHUB_SHA` exactly equals the CLI `--code-commit`;
- runtime run id is positive and is not proof run `36319888985`;
- runtime code commit is not the old proof head.

Run number 1 is the completed proof.

Run number 3 or later is rejected.

Any rerun of run number 2 has `run_attempt > 1` and is rejected.

This makes the historical runtime intrinsically one-shot even though the active workflow source itself remains unchanged.

## Source-vs-dispatch split

DEC-285 records:

- historical execution source authorized: **true**;
- historical-result slot source authorized: **true**;
- historical discovery execution authorized at the exact runtime identity: **true**;
- discovery-result production authorized inside that exact runtime: **true**;
- historical-result dispatch authorized: **false**;
- rerun: **false**;
- retry: **false**;
- replacement: **false**.

No repository-hosted executor is added by DEC-285.

## Data boundary

The runtime remains limited to the already-frozen EXP-061 historical range:

- 2015-01-01 inclusive;
- 2023-01-01 exclusive.

The reserved robustness block remains closed:

- 2023-01-01 inclusive;
- 2026-08-21 exclusive.

The unchanged range-limited loader continues to reject rows or targets outside the frozen historical boundary.

## Public CLI transition

`scripts/phase8a_exp061.py` now imports the DEC-285 gate from:

`src/fmp/discovery/historical_execution_authorization.py`

The gate remains before:

- any historical feature/outcome loader call in a cell job;
- any historical cell-evidence read in the aggregate job.

Preflight evidence also records the DEC-285 execution-authorization payload.

The former DEC-281 exact-source validator intentionally detects the activated CLI as a source supersession. DEC-281 run inventory semantics remain valid; its old current-source builder is no longer the active authorization layer.

## Frozen implementation

Authorization source:

`src/fmp/discovery/historical_execution_authorization.py`

Git blob:

`30258e076f6a786c977fac8c588ac2b22aeed66e`

Activated CLI:

`scripts/phase8a_exp061.py`

Git blob:

`477aa9e8de4452e6444d1ee4361218aca445180d`

Focused authorization tests:

`tests/test_phase8a_exp061_historical_execution_authorization.py`

Git blob:

`2636ae1daa6e90607bc86fde454bfb5b32b53f34`

DEC-281 supersession tests:

`tests/test_phase8a_exp061_historical_run_authorization.py`

Git blob:

`08ffe0a1bace03ec8d934109bf5e0157ad424653`

## Downstream locks

DEC-285 keeps false:

- historical-result dispatch;
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

A historical discovery result, if later produced by the exact one-shot run, remains a retrospective pattern-hypothesis result and is not an executable strategy.

## Next gate

Only after DEC-285 merges green may a separate read-only execution operator be added.

That operator must prove the live workflow inventory still contains only run number 1 / proof run `36319888985`, expose the single future dispatch command as plan evidence, and provide no execute mode.

A one-shot executor may be considered only after that new operator is itself reviewed.
