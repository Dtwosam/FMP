# Phase 8A — EXP-044 Single-Step Operator Advance

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-087  
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-086 determines exactly one legitimate next action but intentionally never dispatches it.

DEC-087 adds a separate `advance` mode that reuses the public DEC-086 planner and may execute at most one currently authorized workflow dispatch after an explicit operator request.

## 2. Interface

The command is:

`python scripts/phase8a_exp044_operator.py advance`

It is dry-run by default.

Actual dispatch requires:

`python scripts/phase8a_exp044_operator.py advance --execute`

## 3. Planner reuse

`advance` does not implement an independent gate sequence.

It invokes the existing public `next` mode and consumes its JSON report.

The report must remain explicitly read-only and keep model-protocol-result, model-fit, promotion, and trading authorizations false.

## 4. Executable planner states

Only three DEC-086 states may map to a workflow command:

- `PRESERVATION_DISPATCH_REQUIRED`;
- `FEATURE_DISPATCH_REQUIRED`;
- `OUTCOME_DISPATCH_REQUIRED`.

The mapped command must exactly match the command already embedded in the DEC-086 report.

Outcome dispatch additionally requires the exact positive verified feature-run ID from that report.

## 5. Non-executable states

No command may be executed for:

- preservation/feature/outcome in-progress states;
- preservation/feature/outcome review-required states;
- duplicate-run failures;
- readiness or `MODEL_PROTOCOL_SOURCE_OPEN`;
- any unrecognized state.

Failed workflows are never automatically retried.

## 6. Stale-plan protection

With `--execute`, `advance` obtains the DEC-086 plan, then immediately invokes the public planner a second time before mutation.

The second report must be exactly equal to the first.

If live workflow/evidence state changed, execution aborts and the operator must rerun `advance`.

## 7. Single mutation boundary

A successful execution submits exactly one `gh workflow run` command.

Submission means only that the dispatch request was submitted.

DEC-087 does not claim that the workflow started, completed, succeeded, or produced valid evidence.

## 8. Safety boundary

DEC-087 does not authorize:

- automatic retry;
- multi-stage chaining;
- model fitting;
- model selection or promotion;
- shadow/demo trading;
- broker mutation;
- live orders;
- real-money trading.

## 9. Next gate

Before any EXP-044 run exists, `advance --execute` may submit only the DEC-084 preservation workflow because DEC-086 must first resolve `PRESERVATION_DISPATCH_REQUIRED`.

The operator must run `advance` again after each authoritative state transition.
