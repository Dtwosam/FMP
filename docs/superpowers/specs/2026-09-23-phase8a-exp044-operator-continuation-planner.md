# Phase 8A — EXP-044 Operator Continuation Planner

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-086  
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-081 through DEC-085 provide safe manual dispatch, live source/evidence preflight, readiness inspection, preservation, and exact preserved-source fallback.

The remaining operator risk is procedural: an authorized machine must still know which command is appropriate next and must not accidentally duplicate a result-producing workflow.

DEC-086 adds one read-only `next` mode that inspects the live authoritative chain and reports exactly one next state/action.

## 2. Interface

The command is:

`python scripts/phase8a_exp044_operator.py next`

It has no `--execute` argument.

It never calls `gh workflow run` and never submits a workflow dispatch.

When a dispatch is the next legitimate step, it prints the exact command as data only.

## 3. Preservation gate

The planner first validates the published DEC-084 preservation release when it exists.

If no valid preservation release exists, it inspects the preservation workflow's manual-main run history.

Allowed states include:

- `PRESERVATION_DISPATCH_REQUIRED`;
- `PRESERVATION_RUN_IN_PROGRESS`;
- `PRESERVATION_REVIEW_REQUIRED`.

A successful preservation workflow with no exact published release fails closed.

The planner never automatically retries a failed preservation run.

## 4. Exact run uniqueness

For preservation, feature, and outcome workflows, the planner requires at most one manual `main` run.

It does not select a latest or preferred run when duplicates exist.

Multiple manual-main runs fail closed for operator review.

Push runs and non-main manual runs are ignored for this progression.

## 5. Feature gate

After a valid preservation release exists, the planner inspects the feature workflow.

Allowed states include:

- `FEATURE_DISPATCH_REQUIRED`;
- `FEATURE_RUN_IN_PROGRESS`;
- `FEATURE_REVIEW_REQUIRED`.

A successful feature run is fetched by exact run ID and must pass the existing DEC-081/082 workflow/run checks.

The exact aggregate feature-evidence artifact is then downloaded and fingerprint/cross-binding validation remains mandatory before the planner can advance to outcomes.

## 6. Outcome gate

After exact feature evidence is valid, the planner inspects the outcome workflow.

Allowed states include:

- `OUTCOME_DISPATCH_REQUIRED`;
- `OUTCOME_RUN_IN_PROGRESS`;
- `OUTCOME_REVIEW_REQUIRED`.

When outcome dispatch is required, the printed command is bound to the exact verified successful feature-run ID.

A successful outcome run is fetched by exact run ID and must pass the existing workflow identity checks.

## 7. Readiness gate

After exact outcome success, the planner downloads:

- aggregate feature evidence;
- aggregate outcome evidence;
- DEC-074 readiness.

It then passes the exact chain to the existing DEC-075 execution-status implementation.

The planner may report `MODEL_PROTOCOL_SOURCE_OPEN` only if DEC-075 independently rebuilds and verifies that state.

The planner does not create or alter readiness.

## 8. Source availability

When a feature or outcome dispatch is the next legitimate step, the planner uses the DEC-085 source resolver.

The report records whether the authoritative source mode would be:

- `actions`; or
- `release`.

DEC-086 does not alter source selection rules.

## 9. Safety boundary

Every `next` report is explicitly read-only and keeps:

- `model_protocol_result_authorized=false`;
- `model_fit_authorized=false`;
- `promotion_authorized=false`;
- `trading_authorized=false`.

DEC-086 performs no workflow dispatch, model fit, strategy/model promotion, shadow/demo action, broker mutation, live order, or real-money action.

## 10. Next gate

Before any EXP-044 result exists, the expected first planner state is `PRESERVATION_DISPATCH_REQUIRED` while the exact preservation release is absent.

After preservation is complete, the planner advances the operator through feature dispatch, feature evidence, outcome dispatch, outcome/readiness evidence, and finally the existing `MODEL_PROTOCOL_SOURCE_OPEN` gate without skipping or inventing a result.
