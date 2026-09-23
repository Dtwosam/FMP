# Phase 8A — EXP-044 Pair-Batched Workflow Execution

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-076  
**Experiment:** EXP-20260923-044

## 1. Purpose

The frozen EXP-044 feature and outcome workflows were initially arranged as a 3-symbol × 3-timeframe matrix.

That topology caused the same accepted Phase 2 Dukascopy ZIP for a symbol to be downloaded and verified independently for each of its three timeframes.

DEC-076 changes only the workflow execution topology so each symbol job downloads its accepted Phase 2 artifact once and processes 5m, 15m, and 1h sequentially from that same verified local copy.

## 2. Feature workflow topology

The feature workflow now has three matrix jobs:

- EURUSD
- GBPUSD
- USDJPY

Each pair job:

1. downloads its exact frozen Phase 2 artifact once;
2. verifies the same ZIP SHA-256 and processed-manifest SHA-256 already frozen by EXP-044;
3. generates 5m, 15m, and 1h feature cells;
4. performs the unchanged double-generation determinism check for all three timeframes;
5. uploads the same three per-timeframe artifact names used by the prior topology.

The aggregate verifier still requires and verifies exactly nine cell artifacts.

## 3. Outcome workflow topology

The outcome materialization workflow likewise runs one matrix job per symbol.

Each pair job:

1. downloads the aggregate feature evidence;
2. downloads the exact three feature-cell artifacts for that symbol;
3. downloads and verifies that symbol's accepted Phase 2 Dukascopy artifact once;
4. materializes 5m, 15m, and 1h outcome cells sequentially;
5. uploads the same three per-timeframe outcome artifact names used by the prior topology.

The aggregate outcome verifier still requires exactly nine outcome cells and emits the same form of outcome evidence and DEC-074 readiness artifact.

## 4. Frozen semantics unchanged

DEC-076 changes none of the following:

- EURUSD / GBPUSD / USDJPY universe;
- 5m / 15m / 1h timeframes;
- accepted Phase 2 source artifact IDs or SHA-256 identities;
- historical range;
- feature definitions or feature-set version;
- 60m / 240m outcome horizons;
- slippage assumptions;
- missing-horizon handling;
- artifact naming identities;
- aggregate feature/outcome evidence requirements;
- DEC-074 readiness requirements;
- DEC-075 execution-observability states;
- model-training authorization;
- promotion or trading authorization.

## 5. Execution effect

For each workflow, accepted Phase 2 pair-history downloads are reduced from nine total downloads to three total downloads.

The logical evidence remains nine pair/timeframe cells.

This amendment is permitted because no EXP-044 feature or outcome workflow had been dispatched before the topology change.

## 6. Safety boundary

Both workflows remain manual `workflow_dispatch` workflows and require merged `main`.

DEC-076 does not authorize model fitting, strategy/model promotion, shadow trading, demo orders, broker mutation, live orders, or real-money trading.

## 7. Next gate

The next hard gate remains the first authoritative dispatch of `phase8a-exp044-market-features` from merged `main`, followed by `phase8a-exp044-market-outcomes` using the exact successful feature-run ID.
