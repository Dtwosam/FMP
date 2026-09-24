# Phase 8A — EXP-051 Single Historical Model-Run Authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-051 RUN DISPATCHED BY THIS DECISION
**Decision:** DEC-155
**Experiment:** EXP-20260924-051

## 1. Preconditions

DEC-154 terminal review merged at:

`fce3859d8eaf9b779c539f3c49b464b4ee72c467`

After that merge, repository Actions history was independently inspected.

The latest 100 repository runs extended back to `2026-09-24T17:24:51Z`.

The EXP-051 workflow first entered `main` with DEC-153 at `2026-09-24T21:12:27Z`.

Across that entire possible workflow lifetime, zero runs matched all of:

- workflow path `.github/workflows/phase8a-exp051-temporal-calibrated-utility-model-training.yml`;
- event `workflow_dispatch`;
- branch `main`.

Therefore zero prior manual-main EXP-051 runs existed before DEC-155 authorization source was frozen.

## 2. Frozen predecessor bindings

DEC-155 binds:

- DEC-150 calibrated-utility protocol;
- DEC-151 deterministic six-regressor/six-calibration-reference training core;
- DEC-152 artifact/evidence contract;
- DEC-153 workflow-source merge: `b0fb55aca2d818e7306a15b200b1e10fcc151ad2`;
- DEC-153 pre-authorization workflow blob: `4ab7480e31e91cbfe39eb5e289eccadde428d1a4`;
- DEC-153 CLI blob: `c88b05a14bc961391ff59e29f742c1dac27272b6`;
- DEC-153 pre-authorization execution-gate blob: `37a0b7af464c464beff0976addc1464f68e916cc`;
- DEC-154 review merge: `fce3859d8eaf9b779c539f3c49b464b4ee72c467`;
- DEC-154 review blob: `bd46dfd1cb8674ab8088d858b378ca37c5d75687`.

## 3. First-run rejection guard

DEC-155 hardens the authorization preflight before runtime installation or fitting.

The preflight now:

1. fetches the exact current workflow run by `GITHUB_RUN_ID`;
2. verifies the exact EXP-051 workflow name and path;
3. verifies `workflow_dispatch` and `main`;
4. lists manual-main runs for the exact workflow;
5. excludes only the current `GITHUB_RUN_ID`;
6. fails if any other prior manual-main EXP-051 run exists.

The hardened workflow Git blob is:

`8c0f77a2585715bdc758e6a158c0c5db6cc4e8c9`

The guard executes before pinned-runtime installation and before the outer execution-authorization check.

## 4. Single-attempt semantics

The first manual-main EXP-051 attempt consumes the DEC-155 slot regardless of whether it:

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

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_execution_gate.py`

Git blob:

`cfb16316f2bf9f09e037f48b3f80867562231bf8`

It records:

`TEMPORAL_CALIBRATED_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-155"`

and opens only the outer historical-result-producing flags:

- `TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = true`;
- `AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = true`;
- `TEMPORAL_CALIBRATED_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = true`;
- `TEMPORAL_CALIBRATED_UTILITY_MODEL_FIT_AUTHORIZED = true`.

The underlying DEC-150 protocol, DEC-151 training core, and DEC-152 artifact-runner result/fit authorization constants remain false and are explicitly validated as frozen dependencies.

## 6. Research identity remains unchanged

DEC-155 changes none of the EXP-051 research protocol:

- three V1 pairs;
- 5m / 15m / 1h timeframes;
- 60m / 240m horizons;
- leakage-safe input features;
- paired 0.5-pip LONG/SHORT net-utility targets;
- three exact leave-one-regime-out fit views;
- six exact HGB regressors per cell;
- six exact excluded-regime calibration references per cell;
- positive-utility per-view voting;
- unanimous direction consensus;
- right empirical CDF calibration;
- minimum calibrated percentile across views;
- raw robust utility as secondary ranking score;
- 250 / 500 / 1000 candidate budgets;
- calibrated/raw cutoff-pair reuse;
- 250-candidate aggregate floor;
- unchanged aggregate financial gate;
- four half-year stability windows;
- 10% candidate-share floor;
- unchanged per-window financial signs;
- validation/holdout scenarios;
- accepted feature/outcome/readiness artifact identities;
- Python 3.12.14 numerical runtime;
- DEC-152 result-evidence validation;
- DEC-154 terminal-review semantics.

## 7. Mandatory terminal review

Any terminal EXP-051 run must be reviewed through DEC-154.

Success requires:

- exact attempt 1;
- exact 11-job workflow shape;
- all nine pair/timeframe cell artifacts;
- aggregate artifact;
- DEC-152 aggregate-evidence revalidation against the run head commit.

Failure, cancellation, or timeout may preserve valid partial cell evidence but cannot claim aggregate result evidence.

DEC-155 authorizes no replacement after any terminal outcome.

## 8. No dispatch by this decision

DEC-155 changes source authorization only.

It does **not** invoke the EXP-051 workflow.

A separate clean-main, one-way operator decision is required after DEC-155 merges.

## 9. Downstream authorization state

DEC-155 keeps false:

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

`8c0f77a2585715bdc758e6a158c0c5db6cc4e8c9`

Execution-gate blob:

`cfb16316f2bf9f09e037f48b3f80867562231bf8`

Focused workflow tests:

`tests/test_phase8a_exp051_model_workflow.py`

Git blob:

`2c46fe19d2875e5d3fd7625d9d685f3e5797f41e`

## 11. Next gate

After DEC-155 merges, the next safe source step is a clean-main, one-way operator that:

- exposes exactly one dispatch command only while no EXP-051 run exists;
- double-plans before explicit execution;
- exposes no second dispatch after an active or terminal run appears;
- routes terminal evidence through DEC-154;
- includes no retry or rerun path.

DEC-155 itself dispatches nothing.
