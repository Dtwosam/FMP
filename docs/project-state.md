# FMP Project State

**Updated:** 2026-09-13  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 2 — Validation, Normalization & Derived Bars  
**Phase status:** CANONICAL_FOUNDATION_ACTIVE  
**Next milestone:** authenticated cloud raw reader, accepted golden-chunk validation, and bounded cloud materialization

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

Phase 2 — Validation, Normalization & Derived Bars — is now active. This Phase 1 PASS does not authorize any real-money trading or change DEC-008.

Historical Phase 1 recovery chronology remains preserved in Git history through pre-PASS main commit `0ff45220cd930839059afcfba631e1e120cb38aa`.

## Phase 2 — CANONICAL_FOUNDATION_ACTIVE

The `phase2-canonical-data-foundation` branch implements only the local, bounded canonical-data foundation defined by the approved Phase 2 design and implementation plan. It does **not** mark Phase 2 PASS.

Implemented foundation scope:

- typed Dukascopy BI5 decoding with frozen V1 price scaling and fail-closed structural validation;
- `RawChunkReader` protocol plus manifest/SHA/size-verifying `LocalRawChunkReader`;
- canonical BID/ASK normalization with one-sided-row preservation and duplicate-side rejection;
- deterministic quote-quality, spread/jump outlier, market-week, gap, and DST analysis;
- deterministic 5m/15m/1h resampling with explicit completeness;
- deterministic Zstd Parquet artifacts, quality JSON, processed manifests, and artifact digests;
- bounded local CLI commands: `decode-day`, `normalize`, `quality`, `resample`, and `process-phase2`.

Still outside this local foundation and required before Phase 2 can close:

- authenticated `CloudRawChunkReader` / read-only `fmp-raw-read` path;
- accepted real Phase 1 golden-chunk decoder validation;
- bounded cloud materialization, then exhaustive full-history processing;
- quantified quality evidence for all three V1 pairs;
- reproducible full-history 1m/5m/15m/1h artifacts and processed manifests;
- Phase 2 checkpoint `fmp-v1-phase2-normalized-data`.
