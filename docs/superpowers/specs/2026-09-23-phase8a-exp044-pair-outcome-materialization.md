# Phase 8A — EXP-044 Pair Outcome Materialization

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-077  
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-076 reduced accepted Phase 2 ZIP downloads to one per pair job, but the outcome workflow still invoked the single-cell materializer three times.

Each invocation independently checksum-verified and read the same 140 monthly one-minute Phase 2 parquet partitions.

DEC-077 removes that repeated local read while preserving the exact outcome semantics.

## 2. Pair-level materialization

A new pair-level materializer receives the verified 5m, 15m, and 1h feature roots for one symbol.

It:

1. verifies all three feature cells against the same aggregate feature evidence;
2. requires the three cells to bind one common Phase 2 processed-manifest SHA-256;
3. determines the combined quote window needed by all three feature cells;
4. checksum-verifies and loads the accepted one-minute Phase 2 history once;
5. builds the 5m, 15m, and 1h outcome grids sequentially from that same verified quote frame;
6. writes the same per-timeframe outcome directories and manifests used before DEC-077.

## 3. Equivalence requirement

The pair-level materializer is required by tests to produce manifests identical to three independent calls of the existing single-cell materializer for the same inputs and code commit.

The existing single-cell API remains available and unchanged for compatibility and independent verification.

## 4. Frozen semantics unchanged

DEC-077 changes none of the following:

- accepted Dukascopy/Phase 2 identities;
- feature artifacts or feature evidence;
- pair/timeframe universe;
- 60m / 240m horizons;
- exact-timestamp entry/exit rules;
- 0.2 / 0.5 / 1.0-pip adverse-slippage scenarios;
- outcome schema or outcome-set version;
- per-timeframe outcome artifact names;
- aggregate outcome evidence;
- DEC-074 readiness;
- DEC-075 status semantics;
- model/trading authorization.

## 5. Execution effect

Within each pair outcome job, the full one-minute Phase 2 history is verified/read once instead of three times.

The logical evidence remains nine outcome cells.

No EXP-044 feature or outcome workflow had been dispatched before DEC-077.

## 6. Safety boundary

DEC-077 creates no model result and no authorization.

Model fitting, promotion, shadow trading, demo orders, broker mutation, live orders, and real-money trading remain locked.

## 7. Next gate

The next hard gate remains the first authoritative dispatch of the pair-batched `phase8a-exp044-market-features` workflow from merged `main`, followed by the pair-batched `phase8a-exp044-market-outcomes` workflow using the exact successful feature-run ID.
