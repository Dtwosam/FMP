# Phase 8A — EXP-044 Execution Observability

**Date:** 2026-09-23  
**Status:** APPROVED — SOURCE OBSERVABILITY ONLY  
**Decision:** DEC-075  
**Experiment:** EXP-20260923-044

## 1. Purpose

EXP-044 now has separate source layers for feature generation, aggregate feature evidence, outcome materialization, aggregate outcome evidence, and DEC-074 data-preparation readiness.

DEC-075 adds one read-only execution-status layer so an operator can determine exactly which evidence step is still missing without inferring progress from source code, workflow presence, or partial artifacts.

## 2. Status states

The deterministic status machine may report only these execution states:

- `FEATURE_DISPATCH_REQUIRED`
- `FEATURE_RUN_NOT_SUCCESSFUL`
- `FEATURE_EVIDENCE_REQUIRED`
- `OUTCOME_DISPATCH_REQUIRED`
- `OUTCOME_RUN_NOT_SUCCESSFUL`
- `OUTCOME_EVIDENCE_REQUIRED`
- `READINESS_REQUIRED`
- `MODEL_PROTOCOL_SOURCE_OPEN`

A later state requires all prior supplied evidence to validate and cross-bind exactly.

## 3. Workflow identity validation

When workflow-run metadata is supplied, the status layer validates:

- exact workflow name and path;
- `workflow_dispatch` event;
- `main` head branch;
- positive run ID;
- valid 40-character Git head SHA;
- status and conclusion shape.

A successful feature run must bind the supplied aggregate feature evidence through the exact head SHA. A successful outcome run must bind the aggregate outcome evidence through the exact outcome head SHA, and that outcome evidence must bind the exact feature-evidence fingerprint.

## 4. Readiness validation

Persisted DEC-074 readiness is fingerprint-verified before use.

A valid readiness artifact must retain:

- exact EXP-044 identities;
- exact nine pair/timeframe cells;
- `data_preparation_complete=true`;
- `model_protocol_source_open_authorized=true`;
- `model_protocol_result_authorized=false`;
- `model_fit_authorized=false`;
- `promotion_authorized=false`;
- all shadow/demo/broker/live/real-money authorizations false.

The readiness artifact must bind the supplied feature and outcome evidence fingerprints and code commits.

## 5. Authorization boundary

DEC-075 creates no new authorization.

The execution-status tool may report `MODEL_PROTOCOL_SOURCE_OPEN` only when a valid persisted DEC-074 readiness artifact is supplied and revalidated together with its feature/outcome evidence chain.

Even in that state:

- no model fit is authorized;
- no result-producing model workflow is authorized;
- no model family, split, preprocessing rule, target, threshold, or financial gate is selected;
- no strategy/model promotion is authorized;
- no shadow/demo/live/broker/real-money action is authorized.

## 6. Interface

The source-only CLI is:

`python scripts/phase8a_market_learning_status.py`

It accepts optional local copies of:

- feature workflow-run JSON;
- aggregate feature evidence;
- outcome workflow-run JSON;
- aggregate outcome evidence;
- DEC-074 readiness.

Missing inputs produce the earliest unresolved stage. Supplied malformed or contradictory inputs fail closed.

## 7. Next gate

The real project gate remains unchanged:

1. dispatch `phase8a-exp044-market-features` from merged `main`;
2. preserve and validate its aggregate feature evidence;
3. dispatch `phase8a-exp044-market-outcomes` using that successful feature-run ID;
4. preserve aggregate outcome evidence and DEC-074 readiness;
5. only then may source work begin on a separately frozen model-training protocol.

DEC-075 does not bypass or weaken DEC-074.
