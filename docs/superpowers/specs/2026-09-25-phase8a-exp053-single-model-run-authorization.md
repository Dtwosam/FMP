# Phase 8A — EXP-053 Single Historical Model-Run Authorization

**Date:** 2026-09-25
**Status:** AUTHORIZED SOURCE; NO EXP-053 RUN DISPATCHED BY THIS DECISION
**Decision:** DEC-179
**Experiment:** EXP-20260925-053

## 1. Preconditions

DEC-178 terminal review merged at:

`132fa1621771f9fd072ba6b3a396a70e55c6883b`

Repository Actions history was independently inspected after that merge.

The latest 100 repository runs extended back to `2026-09-25T00:16:23Z`.

The EXP-053 workflow entered `main` with DEC-177 at `2026-09-25T10:06:50Z`.

Across that complete possible workflow lifetime, zero runs matched all of:

- workflow path `.github/workflows/phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml`;
- event `workflow_dispatch`;
- branch `main`.

Therefore zero prior manual-main EXP-053 model runs existed before DEC-179 authorization source was frozen.

## 2. Frozen predecessor bindings

DEC-179 binds:

- DEC-174 fit-temporal feature-support utility protocol;
- DEC-175 deterministic in-memory training/evaluation core;
- DEC-176 artifact/evidence contract;
- DEC-177 workflow-source merge: `7faa5e765f08a47062444ebce3756bf9435ef1d4`;
- DEC-177 pre-authorization workflow blob: `0a6704f75e83b06b7555dbb9dc912cda31443bbc`;
- DEC-177 CLI blob: `dbd146100d81be6ffc492de448d8dc4e0a2f4e73`;
- DEC-177 pre-authorization execution-gate blob: `600ea84946fe908d143f3fbe2082b3505733cdf5`;
- DEC-178 review merge: `132fa1621771f9fd072ba6b3a396a70e55c6883b`;
- DEC-178 review blob: `c1586f8ddf48ad1125adaed7d8d8f0a476862beb`.

## 3. First-run rejection guard

DEC-179 hardens the authorization preflight before runtime installation or fitting.

The preflight now:

1. fetches the exact current workflow run by `GITHUB_RUN_ID`;
2. verifies the exact EXP-053 workflow name and path;
3. verifies `workflow_dispatch` and `main`;
4. lists manual-main runs for the exact workflow;
5. excludes only the current `GITHUB_RUN_ID`;
6. fails if any other prior manual-main EXP-053 run exists.

The hardened workflow Git blob is:

`4cebdc134bd4fd0edc72c4baeccee4c8185e3e1b`

The guard executes before pinned-runtime installation and before the outer execution-authorization check.

## 4. Single-attempt semantics

The first manual-main EXP-053 attempt consumes the DEC-179 slot regardless of whether it:

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

`src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_execution_gate.py`

Git blob:

`e26693a573237bae93e5cacbba2624904362be75`

It records:

`FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-179"`

and opens only the outer historical-result-producing flags:

- `FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = true`;
- `AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = true`;
- `FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = true`;
- `FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED = true`.

The underlying DEC-174 protocol, DEC-175 training core, and DEC-176 artifact-runner result/fit authorization constants remain false and are explicitly validated as frozen dependencies.

## 6. Research identity remains unchanged

DEC-179 changes none of the EXP-053 research protocol:

- three V1 pairs;
- 5m / 15m / 1h timeframes;
- 60m / 240m horizons;
- six HGB utility regressors per cell;
- six pooled excluded-regime calibration references per cell;
- 24 fit-half-year utility-support references per cell;
- 12 fit-half-year feature-support references per cell;
- unanimous positive-utility direction consensus;
- robust raw utility;
- pooled calibrated utility;
- robust fit-temporal utility support;
- robust fit-temporal feature support as the primary ranking score;
- feature-support / utility-support / pooled-calibrated / raw cutoff quadruples;
- 250 / 500 / 1000 candidate budgets;
- unchanged aggregate financial gate;
- four half-year stability windows;
- 10% candidate-share floor;
- unchanged per-window financial signs;
- validation/holdout chronology;
- no-refit forward semantics;
- accepted historical feature/outcome/readiness artifact identities;
- Python 3.12.14 numerical runtime;
- DEC-176 evidence validation;
- DEC-178 terminal-review semantics.

## 7. Mandatory terminal review

Any terminal EXP-053 run must be reviewed through DEC-178.

Success requires:

- exact attempt 1;
- exact 11-job workflow shape;
- all nine pair/timeframe cell artifacts;
- aggregate artifact;
- DEC-176 aggregate-evidence revalidation against the run head commit;
- 18 cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 fit-temporal utility-support references;
- 216 fit-temporal feature-support references;
- exact four-part cutoff evidence.

Failure, cancellation, or timeout may preserve valid partial cell evidence but cannot claim aggregate result evidence.

DEC-179 authorizes no replacement after any terminal outcome.

## 8. No dispatch by this decision

DEC-179 changes source authorization only.

It does **not** invoke the EXP-053 workflow.

A separate clean-main, one-way operator decision is required after DEC-179 merges.

## 9. Downstream authorization state

DEC-179 keeps false:

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

`4cebdc134bd4fd0edc72c4baeccee4c8185e3e1b`

Execution-gate blob:

`e26693a573237bae93e5cacbba2624904362be75`

Focused workflow tests:

`tests/test_phase8a_exp053_model_workflow.py`

Git blob:

`f7737e966592a1ae1c356d3e44b89df815fc7348`

## 11. Next gate

After DEC-179 merges, the next safe source step is a clean-main, one-way operator that:

- exposes exactly one dispatch command only while no EXP-053 run exists;
- double-plans before explicit execution;
- exposes no second dispatch after an active or terminal run appears;
- routes terminal evidence through DEC-178;
- includes no retry or rerun path.

DEC-179 itself dispatches nothing.
