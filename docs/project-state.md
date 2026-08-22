# FMP Project State

**Updated:** 2026-08-22  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 1 — Historical Data Acquisition  
**Phase status:** READY_FOR_FULL_HISTORY_CLOUD_ACQUISITION  
**Next phase:** Phase 2 — Validation, Normalization & Derived Bars (LOCKED until Phase 1 PASS)

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Historical target: 2015-01-01 through 2026-08-20 inclusive for the first frozen snapshot
- Development budget: $0
- Historical source: Dukascopy daily M1 BID/ASK `.bi5`, frozen by DEC-009
- Phase 1 persistent cloud copy: dedicated Supabase `FMP` project, private `fmp-raw` bucket, frozen by DEC-010
- Phase 2+ storage/research: Parquet + DuckDB outside the Phase 1 raw bucket
- Language: Python
- ML: optional, only after baselines
- Execution choice: deferred until demo/shadow needs justify it
- Real-money trading: locked

## Phase 0 — PASS

- [x] Mission and V1 scope frozen
- [x] $0 constraint frozen
- [x] Architecture defined
- [x] Data contract defined
- [x] Research/testing standard defined
- [x] Risk/execution policy defined
- [x] Build order defined
- [x] Experiment record format defined
- [x] Decision log initialized
- [x] External source register initialized
- [x] Agent continuation rules defined
- [x] Portable single-file project source generated
- [x] Source-of-truth merged into repository default branch
- [x] Phase 0 checkpoint recorded

**Phase 0 merge commit:** `31cd8decca5dcb90f9d123ff33f71ac20413e269`  
**Checkpoint ref:** `fmp-v1-phase0-source-of-truth`

## Phase 1 checklist

### Source/acquisition
- [x] Minimal Python package and standard-library test harness created
- [x] V1 pair/side source types defined
- [x] Deterministic Dukascopy daily M1 BID/ASK source path defined
- [x] Resumable per-chunk acquisition implemented
- [x] Atomic raw-file and manifest writes implemented
- [x] SHA-256 verification implemented
- [x] Existing-good-file resume behavior implemented
- [x] Inconsistent/tampered existing state fails closed
- [x] Corrupt/partial LZMA response rejection implemented
- [x] HTTP 404 acquisition outcome recorded without claiming data cleanliness
- [x] Explicit recheck path for delayed `not_found` chunks implemented
- [x] Transient 5xx retry hardening implemented and tested
- [x] Acquisition coverage report implemented
- [x] Full snapshot provenance verifier implemented
- [x] Bounded live-network smoke PASS
- [x] All-pair golden sample PASS
- [x] Retrieval method frozen as DEC-009

### Persistent cloud snapshot
- [x] Dedicated Supabase `FMP` project created at verified `$0/month`
- [x] Private `fmp-raw` bucket created
- [x] GitHub OIDC trust boundary defined and tested
- [x] Supabase `fmp-raw-ingest` Edge Function deployed and ACTIVE
- [x] Edge Function validates SHA-256 and canonical V1 object paths
- [x] Immutable cloud-object conflict behavior implemented
- [x] Python GitHub-OIDC raw mirror client implemented and tested
- [x] Acquisition CLI mirrors each result immediately when `--mirror-url` is supplied
- [x] Sharded GitHub full-acquisition workflow defined
- [x] Main-branch end-to-end OIDC cloud smoke PASS
- [x] Supabase cloud smoke objects independently observed in private bucket
- [ ] `[phase1-full]` full-history run triggered
- [ ] All pair/year shards PASS
- [ ] Full target history accounted for in private bucket
- [ ] Full acquisition coverage/provenance evidence recorded
- [ ] Phase 1 acceptance gate recorded PASS
- [ ] Phase 1 checkpoint recorded

## Current verification evidence

### Existing source-acquisition evidence

- Existing acquisition semantics: 13-test Python suite + live source smoke/golden sample previously PASS.
- Cloud mirror contract adds tests for GitHub OIDC audience/auth request, object SHA-256 headers, idempotent `already_verified`, manifest-only mirroring for source 404, and immediate mirror-before-advance semantics.
- Edge validation tests cover pinned repository/workflow identity, allowed event types, and canonical storage paths.
- Edge Function entrypoint is type-checked with Deno in CI.
- Supabase Edge Function `fmp-raw-ingest` version 2 is ACTIVE.

### Main-branch cloud smoke — PASS

Triggered from `main` by commit `e3f0d3e5977be4b1066764dfb0d9eafd43e190ad` on 2026-08-22.

Supabase Edge Function logs recorded four HTTP 201 `PUT` responses through deployment version 2. Independent SQL inspection of private bucket `fmp-raw` confirmed exactly the expected EUR/USD 2024-01-02 objects:

- `raw/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.bi5` — 11,714 bytes
- `raw/dukascopy/v1/EURUSD/2024/00/02/ASK_candles_min_1.bi5` — 12,015 bytes
- `manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json` — 655 bytes
- `manifests/dukascopy/v1/EURUSD/2024/00/02/ASK_candles_min_1.json` — 655 bytes

The raw byte sizes match the earlier independently verified Dukascopy golden sample. The ingestion function computed and required SHA-256 equality before accepting each object.

Detailed cloud architecture: `docs/supabase-storage.md`.

## Immediate next action

1. Issue a controlled `main` commit containing `[phase1-full]` and touching `docs/phase1-full-acquisition-trigger.md`.
2. This starts the 36-shard matrix: three pairs × years 2015–2026, max three concurrent jobs.
3. Each shard must acquire BID/ASK source chunks, immediately mirror every result to private Supabase Storage, and pass its local provenance verifier.
4. After the run, independently account for the full private-bucket snapshot and record coverage evidence.
5. Keep Phase 2 locked until the full cloud snapshot is accounted for and Phase 1 is formally frozen.

## Known open decisions

1. Exact chronological train/validation/final-test boundaries — Phase 2 data-quality dependent.
2. Exact intrabar ambiguity policy implementation details — Phase 3.
3. Exact demo broker/adapter — Phase 8/9.
4. Exact live capital/risk — explicitly outside current scope until Phase 10 review + Phase 11 approval.

## Blockers

- No architecture blocker remains for persistent Phase 1 acquisition.
- Remaining gates are evidence gates only: full-history acquisition, full cloud accounting, Phase 1 PASS record, and checkpoint.
- These gates do not justify starting Phase 2 early.

## Backlog — do not pull forward without need

- economic-calendar/event-risk filter
- tick-level execution validation
- dashboard
- multi-pair correlation refinement beyond conservative caps
- alternative data
- broader cloud hosting beyond Phase 1 raw persistence
- live-money execution
- indices/crypto/gold/commodities
