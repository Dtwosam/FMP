# Phase 8A — EXP-044 Outcome Identity Projection

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-079  
**Experiment:** EXP-20260923-044

## 1. Purpose

EXP-044 feature artifacts contain 55 columns: seven identity/provenance columns and 48 market feature values.

Direct future-outcome labeling does not use the 48 feature values. It needs only:

- symbol;
- timeframe;
- bar start;
- feature availability time;
- feature-set identity;
- Phase 2 processed-manifest identity.

DEC-079 reduces pair-outcome runner memory by retaining only those six columns after each full feature artifact has been integrity-validated.

## 2. Full-file validation remains mandatory

Projection is not a shortcut around artifact validation.

Before a monthly feature parquet contributes any projected rows, the materializer still requires:

- exact manifest-bound file path;
- exact byte size;
- exact file SHA-256;
- exact full 55-column parquet schema;
- exact row count.

Only after those checks does the pair path read/retain the six outcome-identity columns.

The existing single-cell/full-frame loader remains available unchanged by default.

## 3. Outcome identity contract

The frozen projected columns are:

- `symbol`;
- `timeframe`;
- `bar_start_utc`;
- `available_at_utc`;
- `feature_set_version`;
- `processed_manifest_sha256`.

A dedicated outcome builder accepts this projected identity frame.

The original full-feature outcome builder remains strict: callers using it must still provide the full feature schema.

## 4. Equivalence requirement

Tests require the projected-identity outcome builder to produce exactly the same:

- output rows;
- net-pip labels;
- best-direction labels;
- source-row counts;
- missing-entry counts;
- missing-exit counts

as the original full 55-column builder for the same observations and one-minute quotes.

Pair-level materialization must also remain manifest-identical to independent full-frame single-cell materializations.

## 5. Frozen semantics unchanged

DEC-079 changes no:

- feature artifact bytes or schema;
- feature values;
- Dukascopy/Phase 2 identities;
- quote data;
- 60m / 240m horizons;
- spread/slippage economics;
- exact-timestamp rules;
- outcome schema or artifact identity;
- aggregate evidence/readiness rules;
- authorization state.

## 6. Safety boundary

This is an execution-memory optimization only.

No model fit, model selection, promotion, shadow/demo action, broker mutation, live order, or real-money action is authorized.

## 7. Next gate

The next hard gate remains authoritative dispatch of `phase8a-exp044-market-features` from merged `main`, followed by the exact feature-bound outcome workflow.
