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
- HTTP 404 is recorded as `not_found`; delayed files can be explicitly retried locally with `--recheck-not-found`, subject to DEC-013's prohibition on cloud-mirrored in-place promotion.
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
**Status:** APPROVED

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


## DEC-012 — Sparse exact-gap Phase 1 cleanup

**Date:** 2026-09-09  
**Status:** APPROVED

Once Phase 1 recovery gaps are sparse, repair will move from month-level replay to exact missing pair/date/side chunks.

Rules:

- the frozen target remains exactly **25,500** Dukascopy V1 manifests;
- exact-gap plans are generated from the live Supabase cloud ledger after the preceding repair sweep stops;
- each plan carries its UTC audit timestamp, present/missing counts, and explicit chunk list;
- present + missing must equal 25,500 and missing must equal the exact chunk count;
- plans reject duplicate, unknown, unsupported, out-of-range, or non-canonical chunks;
- sparse acquisition uses the existing DEC-011 one-runner, 8-attempt, 5-second pacing policy;
- the dedicated trigger is `[phase1-exact-gap-batch]`;
- the same exact-gap workflow run must not be rerun after partial success/failure; a fresh Supabase audit and smaller fresh plan are required;
- before sparse source access, the runner must reject a plan if any other source-capable `phase1-full-acquisition` run was updated after the plan's `audited_at_utc`; because GitHub workflow timestamps are only second-granularity, any source-capable run reported in the same UTC second as the audit is also treated as intervening/fail-closed; the current exact-gap run and push-triggered `[phase1-no-source]` runs are excluded from that check; manual `workflow_dispatch` runs remain source-capable regardless of the underlying head-commit message;
- cloud/OIDC/Supabase failures remain fail-fast and local exact-plan provenance verification remains fail-closed;
- raw cloud objects remain immutable and are never deleted merely to repair accounting;
- every cloud-mirrored Phase 1 acquisition run from current `main` must complete an authenticated ingest protocol preflight before any source request and require exactly `fmp-raw-ingest-v2`; an older/misdeployed endpoint fails before Dukascopy access;
- the ingest endpoint must reject malformed, extra-field, missing-field, path/body-identity-mismatched, or unknown-status manifest JSON before immutable storage;
- manifest identity fields must match the canonical object path, source URL, pair, side, UTC date, retrieval method, 1m granularity, BI5 format, 24-byte record size, and zero-based source-month semantics;
- `retrieved_at_utc` must use UTC (zero offset) and status-specific metadata must satisfy the frozen `complete` / `not_found` schema;
- a `not_found` manifest is accepted only when the matching immutable raw object is verified absent;
- a `complete` manifest is accepted only when the matching immutable raw object already exists and its server-side SHA-256 and byte size match the manifest;
- Storage lookup errors other than a verified missing-key result fail closed;
- canonical ingest object paths must resolve to a real Gregorian date inside the frozen Phase 1 interval 2015-01-01 through 2026-08-20 inclusive; regex-shaped but impossible/out-of-range paths are rejected before storage;
- final Phase 1 structural/accounting audit clocks and the provenance acquisition-baseline completion clock must use UTC-zero offsets and must not be future-dated at acceptance time;
- `[phase1-no-source]` is the code/docs-only operational tag: it suppresses push-triggered Phase 1 acquisition and PR Dukascopy golden/network jobs;
- final cloud provenance must record its guard start before checking acquisition idleness and, after provenance reads finish, scan the complete acquisition workflow history; any source-capable run updated at or after that observable UTC-second boundary invalidates the audit, including GitHub reruns that reuse an old workflow run ID; only push-triggered `[phase1-no-source]` runs are exempt;
- final provenance baseline identity is the most recently updated source-capable acquisition run, not merely the newest workflow-run ID; the same run ID and activity/completion timestamp must be selected before and after provenance verification;
- Phase 2 remains locked until the final 25,500/25,500 coverage and integrity gates pass.

Implementation evidence: PR #12, merge commit `a6bf7e2ecf215cf65e99cc9653267abe9ddb4eb1`.


## DEC-013 — No in-place cloud promotion of canonical `not_found` manifests

**Date:** 2026-09-09  
**Status:** APPROVED

The canonical Phase 1 cloud manifest path is first-write stable. A cloud manifest whose first accepted status is `not_found` is not mutated or replaced later with a `complete` manifest in V1.

Rules:

- `--recheck-not-found` remains supported for local acquisition/revalidation when `--mirror-url` is not configured;
- combining `--recheck-not-found` with cloud mirroring is rejected before GitHub OIDC setup and before any source request;
- this avoids the unsafe sequence where a later HTTP 200 uploads a new raw object first, then the immutable earlier `not_found` manifest rejects the substantive `complete` replacement and leaves raw + stale `not_found` provenance;
- existing canonical manifests and raw objects are not deleted or overwritten to implement a status transition;
- any future cloud 404→200 promotion requires a separately approved versioned-provenance design rather than in-place mutation;
- legitimate `not_found` manifests remain valid Phase 1 accounting/provenance evidence and Phase 2 still determines whether observed gaps are expected market closures or data-quality concerns.

This decision reconciles DEC-009's explicit source recheck capability with DEC-010's first-cloud-manifest immutability.
