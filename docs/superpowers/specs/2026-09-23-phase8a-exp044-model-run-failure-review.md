# Phase 8A — EXP-044 Model-Run Failure Review and V1 Closure

**Date:** 2026-09-23
**Status:** APPROVED — FAILED RUN REVIEWED; EXP-044 V1 MODEL EXECUTION CLOSED
**Decision:** DEC-094
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-093 authorized exactly one guarded historical EXP-044 model-result workflow.

That workflow executed once as run `35891605645` from merged `main` SHA `e97fa03d0e94fd505d0f926eb730e01a41947880`, attempt 1.

The run completed with conclusion `failure`.

DEC-094 freezes the exact failure inventory, closes all EXP-044 V1 model execution authorization, repairs only the source-side artifact-persistence defect, and preserves the failed run as immutable audit evidence.

DEC-094 does not authorize a rerun, retry, replacement run, model-parameter rescue, promotion, shadow activity, demo orders, broker mutation, live orders, or real-money trading.

## 2. Terminal run identity

The reviewed workflow identity is exactly:

- workflow: `phase8a-exp044-model-training`;
- run ID: `35891605645`;
- event: `workflow_dispatch`;
- branch: `main`;
- head SHA: `e97fa03d0e94fd505d0f926eb730e01a41947880`;
- attempt: `1`;
- status: `completed`;
- conclusion: `failure`.

Authorization preflight job `107285171765` completed successfully.

Aggregate evidence job `107292746560` was skipped because matrix jobs failed.

GitHub reports zero persisted artifacts for the run.

The run must not be deleted, rerun, or replaced under DEC-094.

## 3. Successful computations whose evidence was not persisted

Five pair/timeframe matrix jobs completed the full `Run exact 60m and 240m model cells` step successfully and failed only afterward while uploading the hidden `.results` directory:

- EURUSD 5m — job `107285328769`;
- EURUSD 1h — job `107285328904`;
- GBPUSD 15m — job `107285328635`;
- GBPUSD 1h — job `107285328632`;
- USDJPY 1h — job `107285329110`.

The failure was caused by `actions/upload-artifact@v6` defaulting to `include-hidden-files: false` while the workflow supplied `path: .results`.

The action therefore reported that no files were found.

The ephemeral result JSON from those runners was not persisted. DEC-094 does not reconstruct, infer, or claim those five computation results.

They are recorded only as successful computation steps followed by evidence-persistence failure.

## 4. Logistic-regression non-convergence

Four pair/timeframe jobs failed inside the model-cell calculation:

- EURUSD 15m — job `107285328653`;
- GBPUSD 5m — job `107285328704`;
- USDJPY 5m — job `107285328835`;
- USDJPY 15m — job `107285328648`.

Each failure has the same frozen-model signature:

`lbfgs failed to converge after 2000 iteration(s)`

followed by:

`RuntimeError: EXP-044 logistic regression failed to converge`

DEC-090 intentionally converts `ConvergenceWarning` into a hard failure.

These failures are therefore negative EXP-044 V1 evidence.

## 5. No post-result rescue of DEC-088

DEC-088 froze exactly two model families, fixed estimator configurations, and six family/threshold variants per model cell before results existed.

DEC-094 does not change:

- logistic-regression `max_iter=2000`;
- logistic solver `lbfgs`;
- logistic tolerance or regularization;
- histogram-gradient-boosting configuration;
- target `best_direction_0p5`;
- the 48 feature inputs;
- chronological splits;
- confidence thresholds 0.50/0.60/0.70;
- financial selection, validation, or holdout gates;
- family universe.

Increasing iterations, swapping solvers, changing preprocessing, dropping the logistic family, or otherwise rescuing the failed fits now would be post-result protocol adaptation and is not permitted inside EXP-044 V1.

## 6. Source-only evidence-persistence repair

DEC-094 repairs the workflow source so a future separately authorized experiment can preserve hidden result files.

The pair/timeframe upload step now:

- runs with `if: always()`;
- uses `include-hidden-files: true`;
- uses `if-no-files-found: warn`.

This permits a job that produced one or more result JSON files before a later failure to preserve those files for review.

The aggregate evidence upload also uses `include-hidden-files: true`.

This repair does not authorize EXP-044 V1 to run again.

## 7. Machine-readable failure review

`src/fmp/market_learning/model_run_failure_review.py` freezes:

- the reviewed run identity;
- authorization-preflight job identity;
- all nine matrix job identities;
- the five upload-failure classifications;
- the four logistic-nonconvergence classifications;
- the skipped aggregate job;
- zero persisted artifacts.

Any drift in the run ID, head SHA, run attempt, job inventory, failure-step identity, or artifact inventory fails closed.

## 8. Execution closure

DEC-094 sets:

- `MODEL_RUN_DISPATCH_AUTHORIZED=false`;
- `AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED=false`;
- `MODEL_PROTOCOL_RESULT_AUTHORIZED=false`;
- `MODEL_FIT_AUTHORIZED=false`.

Promotion, shadow, demo-order, broker-mutation, live-order, real-money, and trading authorization remain false.

The read-only operator validates the exact failed run and reports:

`MODEL_RUN_FAILURE_REVIEWED`

with no dispatch command.

## 9. EXP-044 V1 disposition

EXP-044 V1 produced no authoritative aggregate model-result artifact.

It is closed after one authorized failed workflow run.

The five ephemeral successful computations are not accepted model evidence because they were not persisted.

The four non-converged logistic jobs remain explicit negative evidence.

No historical qualification, shadow-candidate identity, promotion, portfolio admission, demo eligibility, or trading authority results from this run.

## 10. Any successor must be a new predeclared protocol

Continued direct-market model research, if pursued, requires a separately identified successor experiment/protocol.

Such a successor must explicitly acknowledge that EXP-044 V1 results and failure modes have now been observed.

It must freeze any changed convergence policy, estimator configuration, family-failure handling, evidence-persistence behavior, and execution gate before producing another result.

Because the same historical data is already retrospective and now additionally informed the V1 failure review, no successor may characterize that history as untouched out-of-sample evidence.

A successor decision is not created or authorized by DEC-094.
