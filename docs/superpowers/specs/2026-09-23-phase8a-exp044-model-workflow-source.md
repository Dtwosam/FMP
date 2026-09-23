# Phase 8A — EXP-044 Frozen Model-Training Workflow Source

**Date:** 2026-09-23
**Status:** APPROVED — WORKFLOW SOURCE FROZEN; EXECUTION STILL LOCKED
**Decision:** DEC-092
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-088 froze the model protocol, DEC-089 bound that protocol to verified data-preparation evidence, DEC-090 implemented the deterministic training core, and DEC-091 froze exact artifact consumption and model-result evidence.

DEC-092 freezes the manual GitHub Actions workflow and CLI source that could execute those already-frozen components after a later authorization decision.

DEC-092 itself does not authorize a historical model fit and no EXP-044 model-training workflow is dispatched under this decision.

## 2. Frozen upstream source identities

The execution gate binds unchanged source files by exact Git blob identity:

- DEC-091 artifact runner Git blob: `27c0848d16722a22b4762f5842396c2aebc92bec`;
- DEC-090 training core Git blob: `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`;
- DEC-088 model protocol Git blob: `549b2a04f961d9d8ad83caea9c02b40ee54adec2`;
- DEC-091 merged commit: `397ef1410fe92b376431a66f5a7e3ee44d71dec6`;
- DEC-088 protocol fingerprint: `1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605`.

Git blob identity is recomputed directly from the checked-out file bytes, so a modified file cannot pass merely by preserving a version string.

## 3. Execution gate

The source gate reports:

`MODEL_RUN_WORKFLOW_SOURCE_FROZEN`

with:

- `MODEL_RUN_WORKFLOW_SOURCE_FROZEN=true`;
- `MODEL_RUN_DISPATCH_AUTHORIZED=false`;
- `AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED=false`;
- `MODEL_PROTOCOL_RESULT_AUTHORIZED=false`;
- `MODEL_FIT_AUTHORIZED=false`.

The authoritative execution guard validates the frozen upstream source identities before examining authorization flags.

Under DEC-092 it always refuses execution because dispatch authorization is false.

## 4. CLI source

`scripts/phase8a_exp044_model_run.py` freezes four commands:

- `status`: read-only source-gate report;
- `require-execution`: fail unless a later decision authorizes the model result;
- `run-cell`: exact one pair/timeframe/horizon execution path after authorization;
- `aggregate`: exact 18-cell deterministic result-evidence compilation after authorization.

Every result-producing command passes through `require_authoritative_model_execution` before loading readiness, loading historical feature/outcome artifacts, calling the DEC-090 training core, or compiling result evidence.

The CLI also requires the declared execution `code_commit` to equal the checked-out Git HEAD.

## 5. Manual workflow topology

The frozen workflow is:

`.github/workflows/phase8a-exp044-model-training.yml`

It is `workflow_dispatch` only and exposes no user inputs.

Every job requires:

- event `workflow_dispatch`;
- branch `main`;
- a checked-out repository source.

The first job is `authorization-preflight`. It inspects the frozen source and then calls `require-execution`.

The nine pair/timeframe model jobs depend on that preflight. Therefore, under DEC-092, an accidental manual dispatch fails before any feature/outcome artifact is downloaded and before any estimator is fit.

The aggregate job depends on all model-cell jobs.

## 6. Exact artifact inventory

The workflow contains exactly the nine DEC-091 feature artifact IDs/digests and nine DEC-091 outcome artifact IDs/digests.

It also uses the exact readiness artifact:

- artifact ID `10757578276`;
- ZIP SHA-256 `d35248b0690531561818ce13ec6bf371bf31eeaf120182d75eb788417a97ffa8`.

When eventually authorized, each matrix job downloads its exact feature ZIP, exact outcome ZIP, and exact readiness ZIP by artifact ID through the GitHub API, independently recomputes the downloaded ZIP SHA-256, and refuses any mismatch.

No feature generation, outcome rematerialization, Dukascopy acquisition, Phase 2 mutation, or substitute artifact discovery exists in the workflow.

## 7. Frozen model cells

The workflow has exactly nine pair/timeframe jobs:

- EURUSD 5m / 15m / 1h;
- GBPUSD 5m / 15m / 1h;
- USDJPY 5m / 15m / 1h.

Each job runs exactly two independent horizons, 60m and 240m, producing all 18 DEC-088 cells.

No pair, timeframe, horizon, model family, hyperparameter, confidence threshold, split, target, or cost scenario is a workflow input.

## 8. Result evidence

After all 18 cells succeed, the workflow downloads only the current run's exact model-cell result artifacts and invokes the DEC-091 aggregate evidence compiler.

The aggregate artifact name is bound to the execution checkout SHA and the frozen upstream feature/outcome run IDs.

This evidence is historical retrospective evidence only. It creates no promotion, shadow, demo, broker, live, or real-money authorization.

## 9. Operator behavior

DEC-092 extends the read-only EXP-044 operator to report:

`MODEL_RUN_WORKFLOW_SOURCE_FROZEN`

The stage contains no dispatch command.

DEC-087 `advance --execute` therefore remains inert and reports no submitted workflow.

## 10. Model reconstruction boundary

DEC-092 does not add a post-selection refit or fit on later data.

If a later historical result produces a surviving model, any later reconstruction for shadow use must use the exact frozen fit data, exact dependency/source identities, and reproduce the recorded preprocessor/model fingerprints before use. Such deterministic reconstruction requires a separate later decision and may not incorporate selection, validation, holdout, shadow, or newer data.

## 11. Next gate

A later separate decision must:

1. bind the exact merged DEC-092 workflow, CLI, and execution-gate source identities;
2. revalidate the frozen DEC-088/089/090/091 chain;
3. explicitly change model-run dispatch/result/fit authorization;
4. add an exact operator dispatch mapping for only the frozen model-training workflow;
5. preserve promotion and every trading authorization as false.

Only after that later decision is merged may exactly one authoritative EXP-044 model-training workflow run be dispatched.
