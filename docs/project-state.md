# FMP Project State

**Updated:** 2026-09-13  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 2 — Validation, Normalization & Derived Bars  
**Phase status:** FULL_HISTORY_MATERIALIZATION_ACTIVE  
**Next milestone:** exhaustive source-free full-history materialization and Phase 2 acceptance evidence review

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars planned for Phase 2: 5m, 15m, 1h
- Frozen Phase 1 snapshot: 2015-01-01 through 2026-08-20 inclusive
- Planned pair/side/date manifests: **25,500**
- Historical source: Dukascopy daily M1 BID/ASK `.bi5` (DEC-009)
- Persistent raw snapshot: Supabase project `FMP`, private bucket `fmp-raw` (DEC-010)
- Real-money trading: locked

## Phase 0 — PASS

- Merge commit: `31cd8decca5dcb90f9d123ff33f71ac20413e269`
- Checkpoint: `fmp-v1-phase0-source-of-truth`

## Phase 1 — PASS

Phase 1 acceptance proves acquisition completeness and immutable cloud provenance for the frozen 25,500-key Dukascopy V1 snapshot. It does **not** prove quote cleanliness, market-session correctness, gap acceptability, normalization correctness, or derived-bar correctness; those remain Phase 2 responsibilities.

### Final structural evidence

Audit timestamp: `2026-09-13T12:54:55.900Z`

- expected manifests: **25,500**
- present manifests: **25,500**
- missing manifests: **0**
- raw objects: **25,500**
- unexpected manifest paths: **0**
- raw without manifest: **0**
- unexpected raw paths: **0**
- structural gate: **PASS**

### Final recovery/accounting evidence

Audit timestamp: `2026-09-13T12:55:12.135Z`

- expected/present manifests: **25,500 / 25,500**
- missing manifests: **0**
- raw-backed manifests: **25,500**
- inferred `not_found`: **0**
- raw without manifest: **0**
- unexpected manifest paths: **0**
- unexpected raw paths: **0**
- EURUSD/GBPUSD/USDJPY × BID/ASK: each **4,250 / 4,250**
- accounting gate: **PASS**

### Final full cloud provenance

- workflow: `phase1-final-cloud-audit`
- run: **#4**
- run ID: `34758527971`
- head SHA: `0ff45220cd930839059afcfba631e1e120cb38aa`
- result: **SUCCESS**
- artifact: `phase1-cloud-provenance-34758527971`
- artifact ID: `10318323714`
- artifact SHA-256: `53dbc184677393642e07c78fb6f2229a2c9bf5d8a38c2169935c23297003244b`
- plan SHA-256: `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`
- planned chunks: **25,500**
- complete: **25,500**
- not_found: **0**
- invalid manifests: **0**
- invalid raw audits: **0**
- raw checksum mismatches: **0**
- raw size mismatches: **0**
- total issues: **0**
- provenance ready: **true**

### Acquisition-stability evidence

- final source-capable baseline run: `34718347187`
- baseline completion: `2026-09-12T21:23:53Z`
- provenance history guard version: **1**
- guard start: `2026-09-13T12:58:28.353525Z`
- acquisition unchanged during verification: **true**
- source-capable runs checked: **18**
- no-source runs ignored: **25**
- latest checked source run remained `34718347187`

Evidence ordering satisfied:

`2026-09-12T21:23:53Z` baseline completion ≤ `2026-09-13T12:54:55.900Z` structural audit ≤ `2026-09-13T12:55:12.135Z` accounting audit ≤ `2026-09-13T12:58:28.353525Z` provenance guard start.

### Cross-report acceptance

- Phase 1 evidence checks: **55**
- failed evidence checks: **0**
- final acceptance: **PASS**

## Phase boundary

Phase 1 is closed. No further acquisition or repair workflow is required for the frozen V1 snapshot unless later evidence demonstrates an integrity defect.

Phase 2 — Validation, Normalization & Derived Bars — is active. This Phase 1 PASS does not authorize any real-money trading or change DEC-008.

Historical Phase 1 recovery chronology remains preserved in Git history through pre-PASS main commit `0ff45220cd930839059afcfba631e1e120cb38aa`.

## Phase 2 — FULL_HISTORY_MATERIALIZATION_ACTIVE

Phase 2 has a proven local canonical-data foundation and a proven authenticated bounded cloud-read path. Phase 2 is **not PASS** until exhaustive processing of the frozen three-pair snapshot is complete and the resulting quality/manifests are reviewed against the Phase 2 exit gate.

### Canonical foundation implemented

- typed Dukascopy BI5 decoding with frozen V1 price scaling and fail-closed structural validation;
- `RawChunkReader` protocol plus manifest/SHA/size-verifying local and cloud readers;
- canonical BID/ASK normalization with one-sided-row preservation and duplicate-side rejection;
- deterministic quote-quality, spread/jump outlier, market-week, gap, and DST analysis;
- deterministic 5m/15m/1h resampling with explicit completeness;
- deterministic Zstd Parquet artifacts, quality JSON, processed manifests, and artifact digests;
- bounded local CLI commands for decode, normalize, quality, resample, and processing.

### Authenticated bounded cloud proof — PROVEN

The read-only `fmp-raw-read` Edge Function and `CloudRawChunkReader` were exercised against the real frozen Phase 1 cloud snapshot through GitHub OIDC.

- workflow: `phase2-cloud-golden`
- run: **#2**
- run ID: `34780748485`
- head SHA: `c2aa08e36157544d891375ea5aba44915d702d76`
- result: **SUCCESS**
- artifact: `phase2-cloud-golden-evidence`
- artifact ID: `10325445851`
- artifact ZIP SHA-256: `458f827676be8985cd684549aa68574cbcb772531401dca4e9c7404c9a53d1cc`
- artifact files: **11**

Verified raw chunks for `2024-01-02`:

- EURUSD BID: 11,714 bytes, SHA-256 `9b2d2b718f9ca123b58dce4b4512d4e1bd35c692e23e1beafebdd700072cf546`
- EURUSD ASK: 12,015 bytes, SHA-256 `a7dd327f5c59ad016c0e7e480d33fd7abd38da3e9c51dfe614f5e95f677386b3`
- USDJPY BID: 12,522 bytes, SHA-256 `c090db5407da5b5733b2bba5fbd52b39d8ea5afdd43dd2f4741f8acbbca86915`
- USDJPY ASK: 12,514 bytes, SHA-256 `f08b20f1fe78ae48bdb99f2080d93432f6ee5ab8b3b3063c3f8f62dfdc504242`

For both pairs the proof produced and verified:

- 1m rows: **1,440**
- 5m rows: **288**
- 15m rows: **96**
- 1h rows: **24**
- pair quality JSON with zero missing BID/ASK rows, zero required nulls, zero duplicate rows, zero missing open-market minutes, and zero suspicious gaps for the bounded day.

Spread-outlier warnings (EURUSD 44, USDJPY 50) were retained as quality telemetry and did not mutate source or canonical observations.

### Active milestone

The active Phase 2 slice is exhaustive source-free materialization of the complete frozen snapshot:

- EURUSD, GBPUSD, USDJPY;
- 2015-01-01 through 2026-08-20 inclusive;
- **4,250** days and **8,500** verified BID/ASK reads per pair;
- monthly deterministic 1m/5m/15m/1h Parquet partitions;
- full-pair quality reports;
- exact raw-read ledgers;
- versioned processed manifests and reproducibility digests.

Still required before Phase 2 can close:

- successful exhaustive materialization for all three pairs through the authenticated cloud-read path;
- inspection of all three raw ledgers, quality reports, row counts, partition digests, and processed manifests;
- explicit Phase 2 acceptance review against `docs/data-spec.md` and `docs/build-order.md`;
- only after that review, checkpoint `fmp-v1-phase2-normalized-data` and a Phase 2 PASS decision.

Phase 3 has not started.
