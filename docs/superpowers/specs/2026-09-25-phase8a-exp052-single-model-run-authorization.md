# Phase 8A — EXP-052 Single Historical Model-Run Authorization

**Date:** 2026-09-25
**Status:** AUTHORIZED SOURCE; NO EXP-052 RUN DISPATCHED BY THIS DECISION
**Decision:** DEC-168
**Experiment:** EXP-20260925-052

## 1. Preconditions

DEC-167 terminal review merged at:

`32af27a80cdb50a8be069b21ffe1757f0b6aaa10`

Repository Actions history was independently inspected after that merge.

The latest 100 repository runs extended back to `2026-09-24T21:06:09Z`.

The EXP-052 workflow first entered `main` with DEC-166 at `2026-09-25T00:39:05Z`.

Across that complete possible workflow lifetime, zero runs matched all of:

- workflow path `.github/workflows/phase8a-exp052-fit-temporal-support-utility-model-training.yml`;
- event `workflow_dispatch`;
- branch `main`.

Therefore zero prior manual-main EXP-052 model runs existed before DEC-168 authorization source was frozen.

## 2. Frozen predecessor bindings

DEC-168 binds:

- DEC-163 fit-temporal-support protocol;
- DEC-164 deterministic in-memory training/evaluation core;
- DEC-165 artifact/evidence contract;
- DEC-166 workflow-source merge: `2883cc46c65ff7c672c9f8d7192fc7fb240a9835`;
- DEC-166 pre-authorization workflow blob: `a49af5daeb14177a44154ef96b135f64a98a85bf`;
- DEC-166 CLI blob: `728691476a2285ec4cdec594a020aa5c84b04c5e`;
- DEC-166 pre-authorization execution-gate blob: `139028be1c354a99599a3ed6505a1a4725889c02`;
- DEC-167 review merge: `32af27a80cdb50a8be069b21ffe1757f0b6aaa10`;
- DEC-167 review blob: `dbccea23117adbc50fa54345ec418fde54f254a3`.

## 3. First-run rejection guard

DEC-168 hardens the authorization preflight before runtime installation or fitting.

The preflight now:

1. fetches the exact current workflow run by `GITHUB_RUN_ID`;
2. verifies the exact EXP-052 workflow name and path;
3. verifies `workflow_dispatch` and `main`;
4. lists manual-main runs for the exact workflow;
5. excludes only the current `GITHUB_RUN_ID`;
6. fails if any other prior manual-main EXP-052 run exists.

The hardened workflow Git blob is:

`c4310d4d4a58436eca75afaf147fa570ac725088`

The guard executes before pinned-runtime installation and before the outer execution-authorization check.

## 4. Single-attempt semantics

The first manual-main EXP-052 attempt consumes the DEC-168 slot regardless of whether it:

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

`src/fmp/market_learning/model_successor_fit_temporal_support_utility_execution_gate.py`

Git blob:

`7d5fb31ee5e31d042f06426a699b06fb84237338`

It records:

`FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-168"`

and opens only the outer historical-result-producing flags:

- `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = true`;
- `AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = true`;
- `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = true`;
- `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED = true`.

The underlying DEC-163 protocol, DEC-164 training core, and DEC-165 artifact-runner result/fit authorization constants remain false and are explicitly validated as frozen dependencies.

## 6. Research identity remains unchanged

DEC-168 changes none of the EXP-052 research protocol:

- three V1 pairs;
- 5m / 15m / 1h timeframes;
- 60m / 240m horizons;
- six HGB utility regressors per cell;
- six pooled EXP-051 excluded-regime calibration references per cell;
- 24 fit-half-year temporal-support references per cell;
- unanimous positive-utility direction consensus;
- robust raw utility;
- pooled calibrated utility as the secondary score;
- robust fit-temporal support as the primary score;
- support / pooled-calibrated / raw cutoff triples;
- 250 / 500 / 1000 candidate budgets;
- unchanged aggregate financial gate;
- four half-year stability windows;
- 10% candidate-share floor;
- unchanged per-window financial signs;
- validation/holdout chronology;
- no-refit forward semantics;
- accepted historical feature/outcome/readiness artifact identities;
- Python 3.12.14 numerical runtime;
- DEC-165 evidence validation;
- DEC-167 terminal-review semantics.

## 7. Mandatory terminal review

Any terminal EXP-052 run must be reviewed through DEC-167.

Success requires:

- exact attempt 1;
- exact 11-job workflow shape;
- all nine pair/timeframe cell artifacts;
- aggregate artifact;
- DEC-165 aggregate-evidence revalidation against the run head commit;
- 18 cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 fit-temporal-support references.

Failure, cancellation, or timeout may preserve valid partial cell evidence but cannot claim aggregate result evidence.

DEC-168 authorizes no replacement after any terminal outcome.

## 8. No dispatch by this decision

DEC-168 changes source authorization only.

It does **not** invoke the EXP-052 workflow.

A separate clean-main, one-way operator decision is required after DEC-168 merges.

## 9. Downstream authorization state

DEC-168 keeps false:

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

`c4310d4d4a58436eca75afaf147fa570ac725088`

Execution-gate blob:

`7d5fb31ee5e31d042f06426a699b06fb84237338`

Focused workflow tests:

`tests/test_phase8a_exp052_model_workflow.py`

Git blob:

`80e185f9420ed060dfa6d2586e8c3922a7c04d33`

## 11. Next gate

After DEC-168 merges, the next safe source step is a clean-main, one-way operator that:

- exposes exactly one dispatch command only while no EXP-052 run exists;
- double-plans before explicit execution;
- exposes no second dispatch after an active or terminal run appears;
- routes terminal evidence through DEC-167;
- includes no retry or rerun path.

DEC-168 itself dispatches nothing.
