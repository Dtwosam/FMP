# Phase 8A — EXP-049 Single Historical Model-Run Authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-049 RUN DISPATCHED BY THIS DECISION
**Decision:** DEC-137
**Experiment:** EXP-20260924-049

## 1. Preconditions

Before DEC-137 source work, DEC-136 terminal review was merged at:

`3f7f6e00ecd8580266d5728a516bff3b700ade0a`

The repository Actions history was independently inspected after that merge.

The latest 30 repository runs extended back to 2026-09-24T15:41:59Z. The EXP-049 workflow first entered `main` with DEC-135 at 2026-09-24T16:06:45Z. Across that complete workflow lifetime, zero runs matched the exact workflow name/path:

`phase8a-exp049-regime-utility-model-training`

Therefore zero prior manual-main EXP-049 model runs existed before DEC-137 authorization source was frozen.

## 2. Frozen predecessor bindings

DEC-137 binds:

- DEC-132 regime-utility protocol;
- DEC-133 deterministic six-regressor training core;
- DEC-134 artifact/evidence contract;
- DEC-135 locked workflow source merge: `0fe11d26fd74355e39f7379f3eeba869d848271c`;
- DEC-135 pre-authorization workflow blob: `955152835ec1cedf39d6d31e54d6028a7953fab5`;
- DEC-135 CLI blob: `cba5ece4eda8e02a7ca07a780d8caa69a239e094`;
- DEC-135 pre-authorization gate blob: `9d2ffc670a1572febb0e4a29bfda426f8252e5ee`;
- DEC-136 review merge: `3f7f6e00ecd8580266d5728a516bff3b700ade0a`;
- DEC-136 review blob: `1c48405fa8b754ee8d6756dac701332ac72816bd`.

## 3. First-run rejection guard

DEC-137 hardens the workflow before runtime installation or model fitting.

The authorization-preflight now:

1. fetches the exact current workflow run by `GITHUB_RUN_ID`;
2. verifies the exact EXP-049 workflow name and path;
3. verifies `workflow_dispatch` and `main`;
4. lists manual-main runs for the exact EXP-049 workflow;
5. excludes only the current `GITHUB_RUN_ID`;
6. fails if any other prior manual-main EXP-049 run exists.

The hardened workflow Git blob is:

`2d012acdea55f363938156844ae7a74899a2bd40`

This guard runs before pinned-runtime installation and before the outer authorization check.

## 4. Single-attempt semantics

The first manual-main EXP-049 workflow attempt consumes the DEC-137 run slot regardless of whether it:

- succeeds;
- fails;
- is cancelled;
- times out.

No automatic retry is authorized.

GitHub rerun actions are not authorized by DEC-137.

A replacement run is not authorized by DEC-137.

Any later replacement decision would require a separate source-of-truth change after terminal evidence review.

## 5. Outer authorization layer

Authorized execution-gate source:

`src/fmp/market_learning/model_successor_regime_utility_execution_gate.py`

Git blob:

`8ceed495e4501244d610b37bfe965de657a5dc0a`

It records:

`REGIME_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-137"`

and opens only the outer historical result-producing flags:

- `REGIME_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = true`
- `AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = true`
- `REGIME_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = true`
- `REGIME_UTILITY_MODEL_FIT_AUTHORIZED = true`

The underlying DEC-132 protocol, DEC-133 training core, and DEC-134 artifact-runner source-level result/fit authorization constants remain false and are explicitly checked as frozen dependencies.

## 6. What remains unchanged

DEC-137 changes none of the research protocol:

- three V1 pairs;
- 5m/15m/1h timeframes;
- 60m/240m horizons;
- 48 input features;
- paired 0.5-pip LONG/SHORT net-utility targets;
- three exact fit regimes;
- six exact HGB regressors per cell;
- positive-utility per-regime voting;
- unanimous direction consensus;
- minimum agreed-direction utility score;
- 250/500/1000 candidate budgets;
- 250-candidate aggregate floor;
- aggregate financial gate;
- four half-year stability windows;
- 10% candidate-share floor;
- per-window financial signs;
- validation/holdout scenarios;
- exact selection-cutoff reuse;
- accepted feature/outcome/readiness artifact identities;
- Python 3.12.14 numerical runtime;
- DEC-134 result-evidence validation;
- DEC-136 terminal-review semantics.

## 7. Mandatory terminal review

Any terminal EXP-049 run must be reviewed through DEC-136.

Success requires:

- exact attempt 1;
- exact 11-job workflow shape;
- all nine pair/timeframe cell artifacts;
- aggregate artifact;
- DEC-134 aggregate-evidence revalidation against the run head commit.

Failure, cancellation, or timeout may preserve valid partial cell evidence but cannot claim aggregate result evidence.

DEC-137 does not authorize a replacement after any terminal outcome.

## 8. No dispatch by this decision

DEC-137 changes source authorization only.

It does **not** invoke:

`gh workflow run phase8a-exp049-regime-utility-model-training.yml --ref main -R Dtwosam/FMP`

A separate clean-main, one-way operator step is required after DEC-137 merges.

## 9. Downstream authorization state

DEC-137 keeps false:

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

Workflow:

`.github/workflows/phase8a-exp049-regime-utility-model-training.yml`

Hardened workflow blob:

`2d012acdea55f363938156844ae7a74899a2bd40`

Execution gate blob:

`8ceed495e4501244d610b37bfe965de657a5dc0a`

Focused workflow tests:

`tests/test_phase8a_exp049_model_workflow.py`

Git blob:

`ffb9992c83e54cd78858907c7482a07c4be5641c`

## 11. Next gate

After DEC-137 merges, the next safe source step is a clean-main, one-way operator that:

- exposes exactly one dispatch only while no EXP-049 run exists;
- double-plans before explicit execution;
- cannot expose a second dispatch after an active or terminal run appears;
- routes terminal evidence through DEC-136.

DEC-137 itself dispatches nothing.
