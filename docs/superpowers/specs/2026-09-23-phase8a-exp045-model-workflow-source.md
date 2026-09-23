# Phase 8A — EXP-045 Frozen Model-Workflow Source

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT
**Decision:** DEC-098
**Experiment:** EXP-20260923-045

## 1. Purpose

DEC-095 froze the post-result-informed EXP-045 successor protocol.

DEC-096 implemented the deterministic successor training core.

DEC-097 froze verified historical artifact consumption and deterministic aggregate-result evidence.

DEC-098 freezes the manual workflow, CLI, pinned numerical runtime, and fail-closed execution-gate source that may later execute those already-frozen components.

DEC-098 is source-only.

It does not authorize or dispatch a historical model fit, create a model result, promote a candidate, open shadow/demo activity, mutate a broker, place a live order, or permit real-money trading.

## 2. Frozen source chain

DEC-098 binds:

- merged DEC-097 commit:
  `f6c1090064cd3d85c7c3503dec1ef461eeba5da2`;
- DEC-097 successor artifact-runner blob:
  `adebcc48130e8800741810c239528ef6c21eea6e`;
- DEC-096 successor training-core blob:
  `3f0bc1bfa9640d08175e72cdf131bb97c94d562c`;
- DEC-095 successor protocol blob:
  `44129fc5337fb55b9c7d81f5ba0561ea788bd264`;
- DEC-094 failed-run review blob:
  `2260ad4ad08a7e9874bd28030be977a3e71436f9`;
- DEC-091 verified data-loader blob:
  `27c0848d16722a22b4762f5842396c2aebc92bec`.

The DEC-098 workflow source blob is:

`d3e4d11a8e8270417d6bbced27e756b7cc23c324`

The DEC-098 CLI source blob is:

`ff0ed231e22589c3597672bb8bab1f62b321647d`

The DEC-098 execution-gate source blob is:

`6bdb3dfe3d8b548610259cbdfc6245398f9fc199`

A later authorization decision must bind the exact merged DEC-098 gate/source identity before result execution can open.

## 3. Numerical runtime freeze

The workflow uses exactly Python:

`3.12.14`

and installs:

`requirements/exp045-model-run.txt`

whose Git blob is:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

The pinned runtime is:

- `numpy==2.5.3`;
- `scipy==1.18.1`;
- `scikit-learn==1.9.1`;
- `joblib==1.6.0`;
- `threadpoolctl==3.7.0`;
- `cloudpickle==3.1.2`;
- `narwhals==2.26.0`;
- `polars==1.44.2`;
- `polars-runtime-32==1.44.2`.

The execution gate additionally binds exact blobs for `pyproject.toml`, preprocessing, the 48-feature schema, market-learning contracts, and outcome schema/source.

## 4. Workflow surface

The workflow is:

`.github/workflows/phase8a-exp045-model-training.yml`

It is:

- `workflow_dispatch` only;
- `main` only;
- no user inputs;
- read-only GitHub permissions;
- exact pinned Python/runtime installation;
- authorization-preflight first.

No target, estimator, threshold, horizon, artifact, pair, timeframe, or hyperparameter can be supplied at dispatch time.

## 5. Fail-closed authorization preflight

Every result-producing job depends on `authorization-preflight`.

Preflight:

1. verifies manual dispatch;
2. verifies `refs/heads/main`;
3. installs the pinned runtime;
4. reports the frozen DEC-098 gate;
5. calls the authoritative EXP-045 execution requirement.

Under DEC-098:

- `SUCCESSOR_MODEL_RUN_DISPATCH_AUTHORIZED=false`;
- `AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED=false`;
- `SUCCESSOR_MODEL_PROTOCOL_RESULT_AUTHORIZED=false`;
- `SUCCESSOR_MODEL_FIT_AUTHORIZED=false`.

Therefore the workflow cannot reach artifact download or fitting under DEC-098.

## 6. Exact historical artifact inventory

If a later separate decision opens execution, the nine matrix rows remain fixed to the already-persisted historical feature and outcome artifacts used by EXP-044 data preparation.

Each row binds exact GitHub artifact ID and ZIP SHA-256.

The readiness artifact remains exactly:

`10757578276`

with exact ZIP SHA-256:

`d35248b0690531561818ce13ec6bf371bf31eeaf120182d75eb788417a97ffa8`

The DEC-097 loader then revalidates readiness, manifests, partition bytes, row counts, schemas, and source cross-bindings.

No market-data reacquisition, feature regeneration, or outcome rematerialization is present.

## 7. Frozen model cells

The matrix remains exactly nine pair/timeframe datasets:

- EURUSD 5m/15m/1h;
- GBPUSD 5m/15m/1h;
- USDJPY 5m/15m/1h.

Each dataset runs exactly:

- 60m;
- 240m.

The result object remains EXP-045 / DEC-095 / DEC-096 identity and explicitly post-result-informed.

## 8. Persistence policy

DEC-098 implements the already-predeclared DEC-095 evidence-persistence behavior.

Pair/timeframe upload:

- runs with `if: always()`;
- includes hidden files;
- uploads `.results`;
- uses `if-no-files-found: warn`.

Therefore a completed cell result may survive even if another cell in the same job later fails.

Aggregate execution still requires the matrix to succeed completely.

Aggregate upload includes the hidden `.model-evidence` path and fails if aggregate evidence is absent.

Partial cell artifacts remain review evidence only and can never substitute for the required all-18-cell aggregate.

## 9. CLI boundary

`scripts/phase8a_exp045_model_run.py` exposes:

- `status`;
- `require-execution`;
- `run-cell`;
- `aggregate`.

Every command except read-only `status` calls the execution gate first.

The CLI also requires the supplied execution code commit to equal checked-out `git rev-parse HEAD`.

Only after a future authorization can `run-cell` load verified artifacts and call the DEC-096 successor core.

Only after a future authorization can `aggregate` invoke the DEC-097 all-18-cell evidence compiler.

## 10. Execution-gate source validation

`model_successor_execution_gate.py` revalidates the DEC-097 source chain and exact checked-out bytes for:

- successor runner;
- successor core;
- successor protocol;
- failed-run review;
- legacy historical loader;
- workflow;
- CLI;
- runtime requirements;
- pyproject;
- preprocessing;
- feature schema;
- market contracts;
- outcome source/schema.

Any drift fails closed.

## 11. No dispatch mapping

DEC-098 adds no operator dispatch command and submits no GitHub Actions run.

No EXP-045 manual model-training run exists at DEC-098 source freeze.

A manual dispatch attempted before a later authorization would fail in authorization preflight and would not produce model evidence.

## 12. Authorization locks

DEC-098 keeps:

- model-run dispatch false;
- authoritative model-result execution false;
- model-protocol result false;
- model fit false;
- promotion false;
- shadow false;
- demo-order false;
- broker mutation false;
- live-order false;
- real-money false;
- trading false.

## 13. Next gate

A later separate decision may bind the exact merged DEC-098 workflow/CLI/execution-gate identities and authorize at most one guarded historical EXP-045 result run.

That later decision must first verify no prior EXP-045 result-producing run exists and must preserve the post-result-informed / non-OOS identity.

Even a successful historical EXP-045 result cannot authorize promotion or prospective shadow activity without another explicit review.
