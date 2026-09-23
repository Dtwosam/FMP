# Phase 8A — EXP-046 Single Historical Model-Run Authorization

**Date:** 2026-09-23
**Status:** AUTHORIZED SOURCE; NO EXP-046 RUN DISPATCHED BY THIS DECISION
**Decision:** DEC-109
**Experiment:** EXP-20260923-046

## 1. Purpose

DEC-109 separately authorizes at most one guarded historical EXP-046 result-producing workflow run after merge.

It follows the source-only protocol/core/artifact/workflow chain through DEC-107 and the predeclared terminal review in DEC-108.

DEC-109 does not itself dispatch the workflow and does not create a model result.

## 2. Zero-run precondition

Immediately before DEC-109 source work, GitHub reported zero manual-main runs of:

`phase8a-exp046-stability-model-training`

The authorization is valid only for the first manual-main run after merge.

## 3. Bound predecessor state

DEC-109 binds:

- DEC-104 protocol merge: `bb2ee82a7d081138e1c0847e8c406d6c3ac68589`
- DEC-105 training-core merge: `7aa3d86f6c1fce61dd7e35d9ba9830b1fa7355b5`
- DEC-106 artifact-runner merge: `f1316addb56741fcd9b6b12f57e66b677c515188`
- DEC-107 locked workflow-source merge: `0ac50f49ed677ee767c02ca8c964fab569315127`
- DEC-108 predeclared terminal-review merge: `16ef2773a6f1bf6eae54d981ebd6f843e25d4e2a`

Pre-authorization DEC-107 source identities:

- workflow blob: `eb4690091a92021bb0c60f153800dc6cd9111cd5`
- CLI blob: `525be24ec365d50f6f7a390f7eb4f6ac370440b9`
- execution-gate blob: `d20ab76ec7ce112f6a1ca5485e78a395bacdf49b`

DEC-108 review source blob:

`e5ff3c6a0cb65ba14bb3bd43d5dd1d4a5a491cf6`

## 4. First-run workflow guard

DEC-109 hardens:

`.github/workflows/phase8a-exp046-stability-model-training.yml`

to Git blob:

`3fc199f72665fad2a5d66c346645e9362b1e48e3`

Before dependency installation or model execution, the authorization-preflight job:

1. fetches the current GitHub Actions run by `GITHUB_RUN_ID`;
2. verifies exact current run id;
3. verifies exact workflow name;
4. verifies exact workflow path;
5. verifies `workflow_dispatch`;
6. verifies head branch `main`;
7. lists manual-main runs for the exact EXP-046 workflow;
8. excludes only the current run id;
9. fails if any prior manual-main EXP-046 run exists.

The guard is independent of the Python execution gate.

## 5. One-shot semantics

DEC-109 authorizes **at most one** first historical run.

The first manual-main workflow attempt consumes the slot regardless of whether its terminal outcome is:

- success;
- failure;
- cancellation;
- timeout.

No rerun or replacement is automatically authorized.

A later result/failure review must use DEC-108.

## 6. Outer authorization layer

DEC-109 sets the separate outer execution-gate flags true:

- `STABILITY_MODEL_RUN_DISPATCH_AUTHORIZED`
- `AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED`
- `STABILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED`
- `STABILITY_MODEL_FIT_AUTHORIZED`

The underlying DEC-104 protocol, DEC-105 training core, and DEC-106 artifact runner remain individually non-executable in their own source modules.

The DEC-109 authorized execution-gate source is:

`src/fmp/market_learning/model_successor_stability_execution_gate.py`

with Git blob:

`535a321967e6e9bff9c6a4d36b316ccaa0f79d4d`

This layered structure preserves the distinction between frozen research source and later explicit execution authorization.

## 7. Authorized historical scope

The authorized first run remains exactly:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- 60m and 240m horizons;
- the exact DEC-104 temporal-stability protocol;
- the exact DEC-105 deterministic core;
- the exact DEC-106 artifact/evidence contract;
- the exact previously verified EXP-044 feature, outcome, and readiness artifacts;
- Python 3.12.14 and the frozen numerical runtime.

No feature, target, model family, parameter, threshold, candidate-count floor, chronology, stability window, artifact identity, or runtime change is authorized.

## 8. Post-result interpretation

Any produced EXP-046 evidence remains:

- post-result-informed;
- retrospective;
- `untouched_oos = false`.

A successful workflow result is not promotion authorization.

DEC-108 remains the required terminal review contract.

## 9. Locks

DEC-109 keeps false:

- replacement-run authorization;
- promotion;
- prospective shadow;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization;
- trading authorization.

## 10. Dispatch boundary

DEC-109 does **not** dispatch the workflow.

After DEC-109 merges, a separate guarded operator step may:

1. verify current merged `main`;
2. verify zero prior manual-main EXP-046 runs;
3. verify exact authorized source identities;
4. submit exactly one manual-main workflow dispatch.

No second dispatch is permitted after the first attempt exists.
