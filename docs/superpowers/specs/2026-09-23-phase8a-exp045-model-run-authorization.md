# Phase 8A — EXP-045 Single Historical Model-Result Authorization

**Date:** 2026-09-23
**Status:** APPROVED — AT MOST ONE GUARDED HISTORICAL EXP-045 MODEL-RESULT RUN MAY BE DISPATCHED AFTER MERGE
**Decision:** DEC-099
**Experiment:** EXP-20260923-045

## 1. Purpose

DEC-095 froze the post-result-informed successor protocol.

DEC-096 implemented the deterministic successor training core.

DEC-097 froze verified historical artifact consumption and deterministic all-18-cell aggregate evidence.

DEC-098 froze the manual workflow, fail-closed CLI, pinned runtime, and execution-gate source while keeping result execution disabled.

DEC-099 is the separate authorization gate required by DEC-098. It authorizes at most one guarded historical EXP-045 model-result run after this decision is merged.

DEC-099 does not dispatch that run itself. It does not authorize promotion, prospective shadow admission, demo orders, broker mutation, live orders, real-money trading, or any claim of untouched OOS evidence.

## 2. Pre-authorization state

DEC-098 merged to `main` at:

`292a86fa2aa497b31c0dd4e0284115b185f31ed4`

The merged DEC-098 source identities are:

- workflow Git blob:
  `d3e4d11a8e8270417d6bbced27e756b7cc23c324`;
- CLI Git blob:
  `ff0ed231e22589c3597672bb8bab1f62b321647d`;
- execution-gate Git blob:
  `6bdb3dfe3d8b548610259cbdfc6245398f9fc199`.

Before DEC-099 source work, GitHub reported zero manual-main runs of `phase8a-exp045-model-training`.

Those identities and the zero-run observation are prerequisites for this authorization.

## 3. One-run invariant

The workflow remains:

- `workflow_dispatch` only;
- `main` only;
- no user inputs;
- read-only repository/actions permissions.

DEC-099 adds a workflow-internal prior-run guard before execution authorization.

The guard:

1. loads the current GitHub Actions run and verifies exact workflow name/path, manual event, and `main` branch;
2. lists manual-main runs for `phase8a-exp045-model-training.yml`;
3. excludes only the current `GITHUB_RUN_ID`;
4. fails if any prior manual-main run exists.

A failed or cancelled first manual-main run consumes the one-run slot. No automatic retry or replacement is authorized.

## 4. Authorized workflow identity

The DEC-099 hardened workflow Git blob is:

`3c7fc17d747bca474bd91e44cb753c5cf4cc153b`

The unchanged DEC-098 CLI remains:

`ff0ed231e22589c3597672bb8bab1f62b321647d`

The DEC-099 authorization-gate source blob is:

`e1862169c71c77d85d37b8694dc29fc9d82dc30a`

The authorization layer also records the merged DEC-098 commit and prior workflow/CLI/gate identities for audit.

## 5. Frozen research inputs

The authorization does not change any research input.

The run remains constrained to:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h derived bars;
- exact 60m and 240m model horizons;
- the exact nine persisted feature artifacts frozen under DEC-091/097;
- the exact nine persisted outcome artifacts frozen under DEC-091/097;
- readiness artifact `10757578276` with its frozen ZIP SHA-256;
- DEC-095 protocol identity;
- DEC-096 successor core identity;
- DEC-097 artifact/evidence contract.

No market-data reacquisition, feature regeneration, outcome rematerialization, target change, threshold change, estimator rescue, hyperparameter search, post-selection refit, or replacement experiment is authorized.

## 6. Runtime freeze

Execution remains pinned to Python `3.12.14` and `requirements/exp045-model-run.txt`.

The exact runtime is:

- `numpy==2.5.3`;
- `scipy==1.18.1`;
- `scikit-learn==1.9.1`;
- `joblib==1.6.0`;
- `threadpoolctl==3.7.0`;
- `cloudpickle==3.1.2`;
- `narwhals==2.26.0`;
- `polars==1.44.2`;
- `polars-runtime-32==1.44.2`.

Source validation continues to recompute the exact frozen Git blobs for the runner, core, protocol, failure review, historical loader, workflow, CLI, requirements, pyproject, preprocessing, feature schema, contracts, and outcomes.

## 7. Authorization flags

DEC-099 sets only the outer historical execution layer to:

- `SUCCESSOR_MODEL_RUN_DISPATCH_AUTHORIZED=true`;
- `AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED=true`;
- `SUCCESSOR_MODEL_PROTOCOL_RESULT_AUTHORIZED=true`;
- `SUCCESSOR_MODEL_FIT_AUTHORIZED=true`.

The underlying DEC-095 protocol and DEC-096 training-core source locks remain false. Their source bytes are unchanged; DEC-099 is the separate execution authorization around them.

The following remain false:

- promotion;
- shadow admission;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization;
- trading authorization.

## 8. Evidence persistence and result boundary

DEC-095/098 persistence behavior remains unchanged.

Pair/timeframe result upload runs with `if: always()`, includes hidden files, and warns if no result exists.

Aggregate evidence still requires all 18 exact cells and is revalidated by the DEC-097 successor evidence contract.

Any partial evidence is review evidence only and cannot substitute for the complete aggregate.

A successful result remains explicitly post-result-informed and retrospective. It must not be described as untouched OOS or prospective evidence.

## 9. Dispatch boundary

DEC-099 does not submit a GitHub Actions run.

After merge, a separate operator/action step must first re-check:

- clean current `main`;
- the merged DEC-099 source identity;
- zero prior manual-main EXP-045 model runs.

Only then may the single guarded workflow be dispatched.

No second run is authorized.

## 10. Post-run gate

After the one authorized run reaches a terminal state, its persisted evidence must be reviewed as a separate decision.

A successful historical result still cannot authorize promotion or Phase 8B prospective shadow activity by itself.

Any later shadow-candidate decision must preserve the post-result-informed label and define deterministic fitted-model reconstruction/storage before prospective use.

Until such a later decision, demo execution, broker mutation, live orders, real-money trading, and trading authorization remain locked.
