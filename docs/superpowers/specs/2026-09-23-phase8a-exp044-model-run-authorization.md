# Phase 8A — EXP-044 Single Historical Model-Result Authorization

**Date:** 2026-09-23
**Status:** APPROVED — EXACTLY ONE HISTORICAL MODEL-RESULT RUN MAY BE DISPATCHED AFTER MERGE
**Decision:** DEC-093
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-088 froze the model protocol, DEC-089 bound it to verified data-preparation evidence, DEC-090 implemented the deterministic training core, DEC-091 froze exact artifact consumption/result evidence, and DEC-092 froze a fail-closed manual workflow and CLI.

DEC-093 is the first decision that authorizes a result-producing EXP-044 historical model fit.

It authorizes exactly one manual-main execution of the frozen model workflow after this decision is merged. It does not authorize promotion, shadow admission, demo orders, broker mutation, live orders, or real-money trading.

No model workflow is dispatched by this decision itself.

## 2. Pre-authorization state

Immediately before DEC-093 source work, GitHub reported zero manual `phase8a-exp044-model-training` workflow runs on `main`.

DEC-092 was merged at:

`9645bae73ec1d113383c9957569c6e05a70b2e96`

The merged DEC-092 source identities recorded before authorization are:

- workflow Git blob: `004f6c0062b6e5c1e15dcd507ea19b288b821e40`;
- CLI Git blob: `daae5b3a54a3412e799a8ec44206724859a74ba4`;
- execution-gate Git blob: `74639615946dba49e742e0d6738b9c8d34855340`;
- operator Git blob: `97a13779c7f5425697487a5a8772613e48362556`.

These values remain audit history. DEC-093 intentionally hardens the workflow and execution gate before opening the run.

## 3. Single-run invariant

The authorized workflow remains `workflow_dispatch` only, `main` only, and exposes no user inputs.

DEC-093 adds a workflow-internal first-run guard before execution authorization is checked.

The guard:

1. fetches the current GitHub Actions run and verifies its workflow name/path, manual event, and `main` branch;
2. lists all manual-main runs for `phase8a-exp044-model-training.yml`;
3. excludes only the current `GITHUB_RUN_ID`;
4. fails if any prior manual-main model run exists.

Therefore a second manual dispatch cannot produce another model result even if someone bypasses the operator.

A failed first model run also consumes the one-run slot. It may not be retried or replaced automatically.

## 4. Hardened authorized workflow identity

The DEC-093 hardened workflow Git blob is frozen as:

`491a9ab5ac688402ef71506e1207463940c8931b`

The unchanged DEC-092 CLI remains frozen as:

`daae5b3a54a3412e799a8ec44206724859a74ba4`

The execution gate recomputes Git blob identities from checked-out bytes before permitting result execution.

## 5. Numerical runtime freeze

DEC-093 does not rely on future dependency resolution.

The model workflow uses exactly Python:

`3.12.14`

and installs the exact runtime set from:

`requirements/exp044-model-run.txt`

with:

- `numpy==2.5.3`;
- `scipy==1.18.1`;
- `scikit-learn==1.9.1`;
- `joblib==1.6.0`;
- `threadpoolctl==3.7.0`;
- `cloudpickle==3.1.2`;
- `narwhals==2.26.0`;
- `polars==1.44.2`;
- `polars-runtime-32==1.44.2`.

This set matches the environment resolved by the green DEC-092 CI before authorization.

The authorization gate also binds exact Git blob identities for:

- `requirements/exp044-model-run.txt`;
- `pyproject.toml`;
- `src/fmp/models/preprocessing.py`;
- `src/fmp/features/schema.py`;
- `src/fmp/market_learning/contracts.py`;
- `src/fmp/market_learning/outcomes.py`;
- the unchanged DEC-091 artifact runner;
- the unchanged DEC-090 training core;
- the unchanged DEC-088 model protocol.

This allows unrelated repository changes to coexist without silently changing the model runtime.

## 6. Authorization flags

DEC-093 changes the execution authorization layer to:

- `MODEL_RUN_DISPATCH_AUTHORIZED=true`;
- `AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED=true`;
- `MODEL_PROTOCOL_RESULT_AUTHORIZED=true`;
- `MODEL_FIT_AUTHORIZED=true`.

These flags authorize only the one guarded historical result run.

The following remain false:

- promotion;
- shadow admission;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization;
- trading authorization.

## 7. Operator behavior

Before any model run exists, the read-only operator reports:

`MODEL_RUN_DISPATCH_REQUIRED`

with the exact command:

`gh workflow run phase8a-exp044-model-training.yml --ref main -R Dtwosam/FMP`

Only this stage is dispatchable.

Once any model run exists, the operator consumes the dispatch authorization:

- an active run reports `MODEL_RUN_IN_PROGRESS`;
- a failed run reports `MODEL_RUN_REVIEW_REQUIRED`;
- a successful verified run proceeds to aggregate result validation and reports `MODEL_RESULT_REVIEW_REQUIRED`.

No model stage other than `MODEL_RUN_DISPATCH_REQUIRED` returns a dispatch command.

## 8. Aggregate result validation

DEC-093 adds `src/fmp/market_learning/model_result_evidence.py`.

The validator recomputes the aggregate evidence SHA-256 and requires the exact DEC-088/090/091 identities, exact upstream feature/outcome/readiness evidence, the current model-run checkout SHA, and all 18 frozen model cells.

For every cell it requires one valid result fingerprint and a logically valid chronology:

- `NO_MODEL_CHALLENGER -> LOCKED_NO_SELECTION -> LOCKED_NO_SELECTION`;
- `SELECTED -> REJECT -> LOCKED_VALIDATION_REJECT`;
- `SELECTED -> PASS -> PASS|REJECT`.

Impossible or incomplete status chains fail closed even when a caller recomputes the outer evidence fingerprint.

## 9. Result-review boundary

A successful model workflow does not promote anything.

The operator verifies the exact aggregate artifact:

`exp044-model-result-evidence-<model-head-sha>-from-feature-35867307338-outcome-35876715434`

and then stops at:

`MODEL_RESULT_REVIEW_REQUIRED`

The review report may summarize counts of selected, validation-pass, and retrospective-holdout-pass cells, but it grants no promotion or trading permission.

Negative results remain first-class evidence.

## 10. Artifact and protocol boundaries remain unchanged

The authorized run still consumes only:

- feature run `35867307338`;
- outcome run `35876715434`;
- readiness artifact `10757578276`;
- the exact nine persisted feature-cell artifacts;
- the exact nine persisted outcome-cell artifacts;
- DEC-088 protocol fingerprint `1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605`.

No feature regeneration, outcome rematerialization, Dukascopy reacquisition, parameter search, target change, threshold change, or post-selection refit is authorized.

## 11. Post-run next gate

After the one authorized model run completes, its aggregate result must be independently reviewed.

A later decision may consider whether any cell is suitable for a frozen shadow-candidate design.

That later decision must not infer prospective/OOS proof from the retrospective 2025–2026 holdout and must define deterministic fitted-model reconstruction/storage rules before any shadow campaign can use a selected model.

Until such a later decision, promotion, Phase 8B admission, demo execution, broker mutation, live trading, and real-money trading remain locked.
