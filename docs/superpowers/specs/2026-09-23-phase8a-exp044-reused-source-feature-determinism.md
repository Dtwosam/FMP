# Phase 8A — EXP-044 Reused-Source Feature Determinism

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-080  
**Experiment:** EXP-20260923-044

## 1. Purpose

The EXP-044 feature workflow previously generated its deterministic A/B copies in two separate passes.

For each pair/timeframe cell, both passes independently checksum-verified and read the same Phase 2 derived-bar partitions even though the accepted source bytes were unchanged.

DEC-080 keeps two independent feature computations and output trees, but reuses one already-verified in-memory source frame for those two computations.

## 2. Pair-level execution

For each symbol job and each frozen timeframe (5m, 15m, 1h):

1. the Phase 2 processed manifest is validated;
2. the exact overlapping monthly derived-bar files are size- and SHA-256-verified;
3. those bars are loaded once;
4. the EXP-044 feature frame is built and written to the primary A tree;
5. the feature frame is discarded;
6. the EXP-044 feature frame is rebuilt from the same verified source frame and written to the verification B tree;
7. the two manifests must match exactly;
8. the existing workflow byte-for-byte manifest and parquet comparison remains mandatory.

The next timeframe is then processed.

## 3. Equivalence requirement

Tests require the new pair-level path to:

- invoke the Phase 2 feature-source loader exactly once per timeframe;
- produce primary and verification manifests that are identical;
- produce primary manifests identical to the existing single-cell generator;
- produce primary parquet bytes identical to the existing single-cell generator.

The existing single-cell feature-generation API remains available unchanged.

## 4. Frozen semantics unchanged

DEC-080 changes none of the following:

- accepted Dukascopy / Phase 2 data identities;
- 5m / 15m / 1h bar contents;
- feature formulas;
- feature-set version;
- 55-column feature schema;
- retrospective evidence label;
- historical date range;
- per-timeframe artifact names;
- aggregate feature evidence;
- outcome labels;
- DEC-074 readiness;
- DEC-075 execution status;
- DEC-078 source preflight;
- model/trading authorization.

## 5. Execution effect

For the feature workflow, each pair/timeframe Phase 2 derived-bar history is verified/read once instead of twice.

The feature computation itself still runs twice so deterministic regeneration remains directly tested.

No EXP-044 feature or outcome workflow had been dispatched before DEC-080.

## 6. Safety boundary

DEC-080 creates no model result and no trading authorization.

Model fitting, promotion, shadow trading, demo orders, broker mutation, live orders, and real-money trading remain locked.

## 7. Next gate

The next hard gate remains the first authoritative dispatch of `phase8a-exp044-market-features` from merged `main`.
