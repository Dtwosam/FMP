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
**Status:** SUPERSEDED BY DEC-009

Dukascopy was selected as the primary free historical source candidate because official historical export documentation confirms bid/ask price data and trading volume availability. Phase 1 was required to verify the exact programmatic retrieval method before full acquisition.

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

## DEC-009 — Phase 1 Dukascopy retrieval method

**Date:** 2026-08-22  
**Status:** APPROVED

Freeze the Phase 1 historical acquisition adapter to Dukascopy's public daily M1 `.bi5` candle files using separate BID and ASK resources:

```text
https://datafeed.dukascopy.com/datafeed/{PAIR}/{YYYY}/{MM_ZERO_BASED}/{DD}/{SIDE}_candles_min_1.bi5
```

Rules:

- V1 pairs remain `EURUSD`, `GBPUSD`, `USDJPY` only.
- `SIDE` is acquired separately as `BID` and `ASK`.
- source URL month folders are zero-based (`00` = January).
- successful compressed source bytes are preserved unchanged in the raw layer.
- Phase 1 performs only structural validation sufficient to reject empty/corrupt/obviously partial payloads; full price decoding and quote-quality validation remain Phase 2.
- every successful chunk gets a SHA-256 manifest and deterministic provenance path.
- existing verified chunks are never silently overwritten.
- HTTP 404 is recorded as `not_found`; delayed files can be explicitly retried with `--recheck-not-found`.
- acquisition remains sequential/resumable initially; no undocumented rate allowance is assumed.

**Verification evidence:** GitHub Actions run `32541224812`, job `96951495249`, on a clean Ubuntu runner. EUR/USD 2024-01-02 returned HTTP 200 for both sides with 1,440 records each. BID SHA-256: `9b2d2b718f9ca123b58dce4b4512d4e1bd35c692e23e1beafebdd700072cf546`. ASK SHA-256: `a7dd327f5c59ad016c0e7e480d33fd7abd38da3e9c51dfe614f5e95f677386b3`. The workflow independently recomputed checksums and passed coverage assertions.
