# Phase 8A — EXP-051 Temporal-Calibrated Utility Workflow Source

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY; EXP-051 EXECUTION AUTHORIZATION CLOSED
**Decision:** DEC-153
**Experiment:** EXP-20260924-051

## 1. Purpose

DEC-153 freezes the manual-main workflow, public CLI, pinned numerical runtime, and exact-source execution gate around the merged DEC-150 protocol, DEC-151 deterministic training core, and DEC-152 artifact/evidence contract.

This creates the source shape required for a later historical result run.

It does **not** authorize workflow dispatch, model fitting, model-protocol result production, or authoritative historical result execution.

## 2. Frozen source chain

DEC-153 binds:

- DEC-150 merge: `b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833`
- DEC-150 protocol blob: `c39309c4115cae1ea058e56f30cae4af6407e36e`
- DEC-151 merge: `68028ef37b72e3f0695b475928434ede40ad7690`
- DEC-151 training-core blob: `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`
- DEC-152 merge: `9f8fc93096fb29579924932c5c3b526598afaf28`
- DEC-152 artifact/evidence blob: `3b25ad8dee80ad2d68a421b01b3e7789b1de9f1a`
- accepted historical data-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

The execution gate also binds exact workflow, CLI, runtime requirements, pyproject, preprocessing, feature schema, market-learning contracts, and outcome-schema bytes.

Any bound-byte drift fails closed.

## 3. Workflow identity

Workflow:

`.github/workflows/phase8a-exp051-temporal-calibrated-utility-model-training.yml`

Git blob:

`4ab7480e31e91cbfe39eb5e289eccadde428d1a4`

Workflow name:

`phase8a-exp051-temporal-calibrated-utility-model-training`

The workflow is:

- manual `workflow_dispatch` only;
- input-free;
- `main` branch only;
- read-only GitHub contents/actions permissions;
- Python 3.12.14;
- no schedule;
- no pull-request trigger;
- no alternate dispatch trigger.

DEC-153 intentionally contains **no first-run guard**. That guard belongs only to a later one-run authorization decision after terminal review is frozen and zero prior manual-main EXP-051 runs are independently verified.

## 4. Frozen historical matrix

The workflow preserves the exact accepted nine pair/timeframe historical source cells:

- EURUSD 5m / 15m / 1h
- GBPUSD 5m / 15m / 1h
- USDJPY 5m / 15m / 1h

Each matrix job evaluates exactly:

- 60 minutes
- 240 minutes

The workflow reuses the accepted EXP-044 feature, outcome, and readiness artifacts with exact artifact IDs and ZIP SHA-256 values.

No new historical acquisition is performed.

## 5. Authorization preflight

The first job verifies:

- event is `workflow_dispatch`;
- branch is `main`;
- Python runtime is exactly 3.12.14;
- the frozen EXP-051 source gate validates;
- separate authoritative EXP-051 result execution is authorized.

Under DEC-153 the last condition is false.

Therefore an accidental manual dispatch cannot reach the model-cell jobs.

## 6. Partial-result preservation

If a later decision separately authorizes execution, every pair/timeframe matrix job may preserve any completed cell results even if later work fails.

Artifact namespace:

`exp051-temporal-calibrated-utility-model-cell-results-<symbol>-<timeframe>-<commit>`

Partial artifacts are evidence only. They do not form a complete aggregate result.

## 7. Aggregate evidence

The aggregate job requires the complete matrix and compiles exactly 18 cell results through DEC-152.

Aggregate artifact namespace:

`exp051-temporal-calibrated-utility-model-result-evidence-<commit>-from-feature-35867307338-outcome-35876715434`

The compiler cannot invent missing cells, calibration references, or stable variants.

## 8. CLI

CLI:

`scripts/phase8a_exp051_model_run.py`

Git blob:

`c88b05a14bc961391ff59e29f742c1dac27272b6`

Supported commands are limited to:

- `status`
- `require-execution`
- `run-cell`
- `aggregate`

The CLI contains no workflow-dispatch command.

Every result-producing command calls the DEC-153 execution requirement before readiness loading, historical artifact loading, fitting, or aggregation.

The supplied code commit must equal checkout HEAD.

## 9. Runtime lock

Requirements:

`requirements/exp051-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Pinned packages:

- numpy 2.5.3
- scipy 1.18.1
- scikit-learn 1.9.1
- joblib 1.6.0
- threadpoolctl 3.7.0
- cloudpickle 3.1.2
- narwhals 2.26.0
- polars 1.44.2
- polars-runtime-32 1.44.2

Authorized Python:

`3.12.14`

The numerical runtime is intentionally unchanged from EXP-050 so the calibrated-ranking change is not confounded by a library/runtime change.

## 10. Execution gate

Gate source:

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_execution_gate.py`

Git blob:

`37a0b7af464c464beff0976addc1464f68e916cc`

Decision:

`DEC-153`

The gate first revalidates DEC-152 and checks that all upstream DEC-150/151/152 result, execution, and fit flags remain false.

It exact-binds:

- workflow blob `4ab7480e31e91cbfe39eb5e289eccadde428d1a4`
- CLI blob `c88b05a14bc961391ff59e29f742c1dac27272b6`
- runtime requirements blob `d25ab16056b9f5df283147d67b8f401f60ae7520`
- pyproject blob `de850a1ba397fc69ba634ecf178d732b5012c378`
- preprocessing blob `fcc42f45b9588d38311bc66bc454e6ea0a563e54`
- feature schema blob `afbddc84676faadb8660b4da03c6abeb10cd2a13`
- market-learning contracts blob `4c5a75232e66715c0829e545d8659f59fb8b7724`
- outcome schema blob `c83fefd4252b2fe426af97686f86e43021760c77`

## 11. Authorization state

DEC-153 freezes:

- workflow source frozen: true
- run dispatch authorized: false
- authoritative historical result execution authorized: false
- model-protocol result authorized: false
- model fit authorized: false
- promotion authorized: false
- shadow authorized: false
- demo order authorized: false
- broker mutation authorized: false
- live order authorized: false
- real-money authorized: false
- trading authorized: false

`require-execution` therefore fails at the dispatch-authorization check.

## 12. Focused tests

Tests:

`tests/test_phase8a_exp051_model_workflow.py`

Git blob:

`572c179a3be96fd7ae23d575d206d308232da78c`

They verify:

- exact DEC-150/151/152 source identities;
- exact workflow/CLI/runtime bindings;
- all result/fit/trading authorizations remain false;
- `require-execution` fails at dispatch authorization;
- workflow is manual-main and input-free;
- no first-run guard exists yet;
- exact nine-cell matrix and both horizons;
- exact pinned Python/runtime requirements;
- partial and aggregate evidence namespaces;
- CLI gate ordering before readiness/model/aggregate actions;
- absence of a CLI dispatch bypass.

## 13. Next gate

Before any EXP-051 historical result authorization, a separate decision must predeclare the exact terminal-result review contract.

That review must define before any run exists:

- accepted workflow identity and attempt number;
- required job inventory;
- required cell/aggregate artifact inventory;
- DEC-152 aggregate-evidence revalidation rules;
- failed/cancelled/timed-out first-attempt handling;
- rerun/replacement policy;
- terminal review states.

Only after that review is frozen may another separate decision consider a single guarded historical run authorization.

DEC-153 itself dispatches nothing and produces no historical result.
