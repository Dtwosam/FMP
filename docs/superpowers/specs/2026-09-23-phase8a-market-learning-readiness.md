# Phase 8A — EXP-044 Data-Preparation Readiness Gate

**Date:** 2026-09-23  
**Status:** APPROVED — SOURCE GATE ONLY  
**Decision:** DEC-074  
**Experiment:** EXP-20260923-044

## 1. Purpose

The direct market-learning track may not move from historical data preparation to model-protocol work merely because feature and outcome files exist.

Before model families, preprocessing, chronological splits, target selection, decision thresholds, or financial acceptance gates may be frozen, the exact persisted aggregate feature evidence and aggregate outcome evidence must be revalidated together.

## 2. Required evidence

The readiness gate requires:

- one valid persisted EXP-044 aggregate feature-evidence artifact;
- one valid persisted EXP-044 aggregate outcome-evidence artifact;
- exact nine-cell coverage for EURUSD, GBPUSD, and USDJPY on 5m, 15m, and 1h;
- the outcome evidence must bind the exact supplied feature-evidence fingerprint;
- for every cell, the outcome evidence must bind the exact feature-manifest SHA-256;
- for every cell, feature and outcome evidence must bind the same accepted Phase 2 Dukascopy processed-manifest SHA-256;
- for every cell, outcome source-feature row count must equal the feature row count;
- both evidence layers must remain retrospective and non-promoting.

## 3. Authorization semantics

A passing readiness artifact means only:

`data_preparation_complete=true`

and:

`model_protocol_source_open_authorized=true`

This permits source/design work for a separately predeclared model-training protocol.

It does **not** authorize:

- a result-producing model-training run;
- fitting any model;
- selecting a model family after seeing results;
- changing targets or thresholds after seeing results;
- promotion;
- shadow trading;
- demo orders;
- broker mutation;
- live orders;
- real-money trading.

Accordingly the readiness artifact must keep:

- `model_protocol_result_authorized=false`;
- `model_fit_authorized=false`;
- `promotion_authorized=false`;
- all shadow/demo/broker/live/real-money authorizations false.

## 4. Deterministic identity

The readiness artifact records:

- feature evidence fingerprint and code commit;
- outcome evidence fingerprint and code commit;
- exact nine cell identities;
- feature manifest SHA-256 per cell;
- outcome manifest SHA-256 per cell;
- accepted Phase 2 processed-manifest SHA-256 per cell;
- feature-row and labeled-outcome-row counts;
- one deterministic readiness fingerprint.

Any mismatch fails closed.

## 5. Workflow placement

The existing manual `phase8a-exp044-market-outcomes` workflow emits readiness only after aggregate outcome verification succeeds. It re-downloads the source aggregate feature evidence and validates both persisted evidence layers before writing readiness.

No readiness artifact exists until the authoritative feature workflow and dependent outcome workflow have actually run successfully from merged `main`.

## 6. Next gate

After a valid readiness artifact exists, a new predeclared decision must freeze the first model-training protocol before any result-producing fit. DEC-074 itself does not choose model families, splits, targets, thresholds, or financial acceptance gates.
