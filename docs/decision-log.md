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
- no undocumented rate allowance is assumed.

**Verification evidence:** GitHub Actions run `32541224812`, job `96951495249`, on a clean Ubuntu runner. EUR/USD 2024-01-02 returned HTTP 200 for both sides with 1,440 records each. BID SHA-256: `9b2d2b718f9ca123b58dce4b4512d4e1bd35c692e23e1beafebdd700072cf546`. ASK SHA-256: `a7dd327f5c59ad016c0e7e480d33fd7abd38da3e9c51dfe614f5e95f677386b3`.

## DEC-010 — Dedicated Supabase raw snapshot persistence

**Date:** 2026-08-22  
**Status:** APPROVED

Use a dedicated Supabase project named `FMP` as the persistent cloud copy of Phase 1 immutable Dukascopy raw chunks and acquisition manifests only.

- Supabase project ref: `htjqqzlezyguveuajuat`
- region: `eu-central-1`
- private Storage bucket: `fmp-raw`
- creation cost verified by Supabase management API: `$0/month`
- free-plan Storage is used for Phase 1 raw/manifests only; Phase 2+ normalized/feature datasets remain Parquet/DuckDB outside this bucket unless a later decision changes the architecture.
- the unrelated `frnd-staging` project is not used by FMP.
- the bucket is private and is not given public write policies.
- GitHub never receives a Supabase service-role/secret key.
- uploads go through the `fmp-raw-ingest` Edge Function, which validates GitHub Actions OIDC identity and canonical repository/workflow claims.
- uploaded bytes must match a caller-supplied SHA-256 before storage.
- object paths are restricted to canonical V1 raw/manifest paths.
- cloud raw objects are immutable; semantically identical retry manifests may differ only in `retrieved_at_utc` and never overwrite the first stored manifest.

This storage layer solves persistence for ephemeral GitHub acquisition runners without changing Dukascopy source semantics or making Supabase part of downstream trading intelligence.

## DEC-011 — Serialize and monthly-isolate Dukascopy acquisition

**Date:** 2026-08-22  
**Status:** APPROVED, pending final hardened network-smoke gate before merge

The first full-history run used 36 pair/year jobs with up to three concurrent source runners. It stopped with only 1,055 of 25,500 planned manifests persisted.

Root-cause diagnostics reproduced Dukascopy source instability directly:

- diagnostic run `32561119936`, USDJPY job `97002685840`, exhausted all six retries on HTTP 503 for `USDJPY/2024/00/04/ASK_candles_min_1.bi5`;
- the same run, GBPUSD job `97002685900`, exhausted all six retries on HTTP 503 for `GBPUSD/2022/00/04/ASK_candles_min_1.bi5`;
- diagnostic run `32561495430` then requested those exact URLs serially with a 10-second gap and both returned HTTP 200;
- the same serial diagnostic later received `Connection reset by peer` on a EURUSD request, proving intermittent instability remains even without concurrency.

Therefore Phase 1 acquisition is changed as follows:

- at most **one GitHub source runner** may access Dukascopy at a time;
- full-history work is isolated by **calendar month** rather than pair/year, reducing failure blast radius;
- each monthly runner processes all three V1 pairs sequentially;
- production source requests use a configured delay between consecutive chunks;
- the hardened recovery workflow currently uses a **5-second inter-chunk delay** and **8-attempt** retry budget, subject to the final live regression smoke before merge;
- successful objects already in Supabase remain reusable through immutable/idempotent cloud semantics;
- a failed month is a recoverable Phase 1 acquisition failure and does not unlock Phase 2.

This decision supersedes the concurrency and year-shard operational assumptions of the initial full-history workflow. It does **not** change DEC-009 source format, canonical data, or Phase 1 acceptance criteria.
