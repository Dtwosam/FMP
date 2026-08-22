# FMP Decision Log

Later approved decisions override older assumptions only when this log says so and affected source-of-truth files are updated in the same change.

## DEC-001 — Forex-only V1

**Date:** 2026-08-22  
**Status:** APPROVED

V1 will focus only on forex. Indices were considered and explicitly removed to prevent unnecessary complexity and market-behavior mixups.

**V1 instruments:** EUR/USD, GBP/USD, USD/JPY.

## DEC-002 — $0 development constraint

**Date:** 2026-08-22  
**Status:** APPROVED

Research, backtesting, shadow-mode development, and demo-system development should require no paid data, AI API, database, VPS, or subscription. A paid dependency cannot become required without a new explicit decision.

## DEC-003 — Python-owned trading engine

**Date:** 2026-08-22  
**Status:** APPROVED

Core intelligence lives in a Python codebase. MT5/OANDA or another broker environment, if later used, is an adapter/execution boundary rather than the location of the system's core research logic.

## DEC-004 — Canonical 1-minute bid/ask data

**Date:** 2026-08-22  
**Status:** APPROVED

Use 1-minute bid/ask data as the canonical research dataset. Generate 5m/15m/1h internally. Tick data is deferred until a promising strategy needs execution-quality validation.

## DEC-005 — Initial historical data source candidate

**Date:** 2026-08-22  
**Status:** APPROVED WITH PHASE-1 VERIFICATION

Dukascopy is the primary free historical source candidate because official historical export documentation confirms bid/ask price data and trading volume availability. The exact programmatic retrieval method is not yet frozen; Phase 1 must verify it with a bounded spike before full acquisition.

## DEC-006 — Simpler model wins ties

**Date:** 2026-08-22  
**Status:** APPROVED

Machine learning is optional. If a simple rule/statistical method is as good as or better than a complex model after costs and out-of-sample tests, use the simpler method.

## DEC-007 — Backtester before strategy benchmarking

**Date:** 2026-08-22  
**Status:** APPROVED

Build and validate the realistic backtesting engine before trusting baseline strategy results. This avoids benchmarking strategies on a simulator whose execution/cost semantics are not yet proven.

## DEC-008 — Real-money lock

**Date:** 2026-08-22  
**Status:** APPROVED

No automatic transition to live capital. Phase 10 may only declare eligibility for a separate explicit live-trading approval. Until that approval exists, live execution remains disabled.
