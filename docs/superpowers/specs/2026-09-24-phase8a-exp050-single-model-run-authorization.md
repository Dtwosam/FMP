# Phase 8A — EXP-050 Single Historical Model-Run Authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-050 RUN DISPATCHED BY THIS DECISION
**Decision:** DEC-146
**Experiment:** EXP-20260924-050

## 1. Preconditions

DEC-145 terminal review merged at:

`b2907cced930afa4d877596a8268ec3bc49ceb9c`

After that merge, repository Actions history was independently inspected.

The latest 100 repository runs extended back to `2026-09-24T15:43:22Z`.

The EXP-050 workflow first entered `main` with DEC-144 at:

`2026-09-24T18:13:58Z`

Across that entire possible workflow lifetime, zero runs matched all of:

- workflow path `.github/workflows/phase8a-exp050-temporal-jackknife-utility-model-training.yml`;
- event `workflow_dispatch`;
- branch `main`.

Therefore zero prior manual-main EXP-050 runs existed before DEC-146 authorization source was frozen.

## 2. Frozen predecessor bindings

DEC-146 binds:

- DEC-141 temporal-jackknife utility protocol;
- DEC-142 deterministic six-regressor training core;
- DEC-143 artifact/evidence contract;
- DEC-144 locked workflow-source merge: `9f2986c783823cf7d9647ed4b0a50c66470bea21`;
- DEC-144 pre-authorization workflow blob: `ec8ed4ab3f0b8a18ffc735af92172e059ed29955`;
- DEC-144 CLI blob: `70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09`;
- DEC-144 pre-authorization gate blob: `4814f0db86bec943d7282ab13586559b1eb8caa7`;
- DEC-145 review merge: `b2907cced930afa4d877596a8268ec3bc49ceb9c`;
- DEC-145 review blob: `e93f7f26e6f0cf8541c9dffd0d359acf0a7ec64e`.

## 3. First-run rejection guard

DEC-146 hardens the authorization preflight before runtime installation or fitting.

The preflight now:

1. fetches the exact current workflow run by `GITHUB_RUN_ID`;
2. verifies the exact EXP-050 workflow name and path;
3. verifies `workflow_dispatch` and `main`;
4. lists manual-main runs for the exact workflow;
5. excludes only the current `GITHUB_RUN_ID`;
6. fails if any other prior manual-main EXP-050 run exists.

The hardened workflow Git blob is:

`7a5875c69d8cdf33e9aaae58fc321dba0537ce0b`

The guard executes before pinned-runtime installation and before the outer execution-authorization check.

## 4. Single-attempt semantics

The first manual-main EXP-050 attempt consumes the DEC-146 slot regardless of whether it:

- succeeds;
- fails;
- is cancelled;
- times out.

No automatic retry is authorized.

GitHub rerun actions are not authorized.

A replacement run is not authorized.

Any later replacement would require a separate source-of-truth decision after terminal evidence review.

## 5. Outer authorization layer

Authorized execution gate:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_execution_gate.py`

Git blob:

`4b1e6723928f122fc2eaa3ba7564283088664296`

It records:

`TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-146"`

and opens only the outer historical-result-producing flags:

- `TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = true`;
- `AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = true`;
- `TEMPORAL_JACKKNIFE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = true`;
- `TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED = true`.

The underlying DEC-141 protocol, DEC-142 training core, and DEC-143 artifact-runner result/fit authorization constants remain false and are explicitly validated as frozen dependencies.

## 6. Research identity remains unchanged

DEC-146 changes none of the EXP-050 research protocol:

- three V1 pairs;
- 5m / 15m / 1h timeframes;
- 60m / 240m horizons;
- leakage-safe input features;
- paired 0.5-pip LONG/SHORT net-utility targets;
- three exact four-year leave-one-regime-out fit views;
- six exact HGB regressors per cell;
- positive-utility per-view voting;
- unanimous direction consensus;
- minimum agreed-direction utility score;
- 250 / 500 / 1000 candidate budgets;
- 250-candidate aggregate floor;
- aggregate financial gate;
- four half-year stability windows;
- 10% candidate-share floor;
- per-window financial signs;
- validation/holdout scenarios;
- exact selection-cutoff reuse;
- accepted feature/outcome/readiness artifact identities;
- Python 3.12.14 numerical runtime;
- DEC-143 result-evidence validation;
- DEC-145 terminal-review semantics.

## 7. Mandatory terminal review

Any terminal EXP-050 run must be reviewed through DEC-145.

Success requires:

- exact attempt 1;
- exact 11-job workflow shape;
- all nine pair/timeframe cell artifacts;
- aggregate artifact;
- DEC-143 aggregate-evidence revalidation against the run head commit.

Failure, cancellation, or timeout may preserve valid partial cell evidence but cannot claim aggregate result evidence.

DEC-146 authorizes no replacement after any terminal outcome.

## 8. No dispatch by this decision

DEC-146 changes source authorization only.

It does **not** invoke:

`gh workflow run phase8a-exp050-temporal-jackknife-utility-model-training.yml --ref main -R Dtwosam/FMP`

A separate clean-main, one-way operator decision is required after DEC-146 merges.

## 9. Downstream authorization state

DEC-146 keeps false:

- replacement model-run authorization;
- promotion;
- prospective shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

One historical run authorization does not imply an accepted model challenger.

## 10. Focused regression identity

Hardened workflow blob:

`7a5875c69d8cdf33e9aaae58fc321dba0537ce0b`

Execution-gate blob:

`4b1e6723928f122fc2eaa3ba7564283088664296`

Focused workflow tests:

`tests/test_phase8a_exp050_model_workflow.py`

Git blob:

`c5893e6a18fd9d0330001d4b35f5e34bbb8c33c1`

## 11. Next gate

After DEC-146 merges, the next safe source step is a clean-main, one-way operator that:

- exposes exactly one dispatch command only while no EXP-050 run exists;
- double-plans before explicit execution;
- exposes no second dispatch after an active or terminal run appears;
- routes terminal evidence through DEC-145;
- includes no retry or rerun path.

DEC-146 itself dispatches nothing.
