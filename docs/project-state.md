# FMP Project State

**Updated:** 2026-08-22  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 1 — Historical Data Acquisition  
**Phase status:** RECOVERING_INCOMPLETE_FULL_HISTORY_ACQUISITION  
**Next phase:** Phase 2 — Validation, Normalization & Derived Bars (LOCKED until Phase 1 PASS)

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Frozen first snapshot target: 2015-01-01 through 2026-08-20 inclusive
- Planned pair/side/date manifests: **25,500**
- Development budget: $0
- Historical source: Dukascopy daily M1 BID/ASK `.bi5`, frozen by DEC-009
- Phase 1 persistent cloud copy: dedicated Supabase `FMP` project, private `fmp-raw` bucket, frozen by DEC-010
- Phase 2+ research storage: Parquet + DuckDB outside the Phase 1 raw bucket
- Language: Python
- ML: optional, only after baselines
- Execution choice: deferred until demo/shadow needs justify it
- Real-money trading: locked

## Phase 0 — PASS

**Merge commit:** `31cd8decca5dcb90f9d123ff33f71ac20413e269`  
**Checkpoint ref:** `fmp-v1-phase0-source-of-truth`

All Phase 0 source-of-truth, architecture, data, research, risk, build-order, experiment-log and continuation-rule gates are complete.

## Phase 1 — completed gates

### Source/acquisition
- [x] deterministic Dukascopy daily M1 BID/ASK source adapter
- [x] resumable local acquisition semantics
- [x] atomic raw/manifest writes
- [x] SHA-256 provenance
- [x] fail-closed tamper handling
- [x] structural LZMA/record validation
- [x] explicit 404 `not_found` provenance
- [x] delayed-404 recheck path
- [x] transient 5xx retry handling
- [x] acquisition coverage report
- [x] snapshot provenance verifier
- [x] bounded live-network smoke previously PASS
- [x] all-pair golden sample PASS
- [x] retrieval method frozen as DEC-009

### Persistent cloud snapshot
- [x] dedicated Supabase `FMP` project created at verified `$0/month`
- [x] private `fmp-raw` bucket created
- [x] GitHub OIDC trust boundary implemented/tested
- [x] Supabase `fmp-raw-ingest` Edge Function deployed
- [x] canonical V1 object-path validation
- [x] SHA-256 required before storage
- [x] Python GitHub-OIDC mirror client
- [x] immediate per-result cloud mirroring
- [x] main-branch end-to-end cloud smoke PASS
- [x] retry-manifest idempotency defect regression-tested, fixed, deployed as Edge Function v3 and merged via PR #5

## First full-history run — INCOMPLETE

Original trigger:

- `496ef145daf694902d09d17e5f969cc62a93fefd` — `chore: start Phase 1 full acquisition [phase1-full]`

Original workflow shape:

- 36 pair/year jobs
- maximum 3 concurrent source runners
- whole-year failure blast radius
- 6-attempt source retry budget
- no explicit inter-chunk source pacing

Independent Supabase audit after writes stopped:

- expected manifests: **25,500**
- present manifests: **1,055**
- missing manifests: **24,445**
- raw objects: **1,055**
- manifest objects: **1,055**
- total objects: **2,110**
- latest object observed from the stopped run: `2026-08-22 03:59:46.247262+00`

The partial cloud snapshot is valid persisted progress but is **not** Phase 1 completion evidence.

## Root cause — DUKASCOPY THROTTLING / SOURCE INSTABILITY

A diagnostic-only PR reproduced the stopped-run behavior without writing to Supabase.

### Concurrent reproduction

GitHub Actions run `32561119936` used three simultaneous one-month source probes with the same six-attempt production retry budget.

- USDJPY job `97002685840` exhausted all six retries on HTTP **503** for `USDJPY/2024/00/04/ASK_candles_min_1.bi5`.
- GBPUSD job `97002685900` exhausted all six retries on HTTP **503** for `GBPUSD/2022/00/04/ASK_candles_min_1.bi5`.

### Serial hypothesis test

GitHub Actions run `32561495430` requested the exact previously failing URLs serially with a 10-second gap:

- USDJPY 2024-01-04 ASK → HTTP **200**, 12,699 bytes.
- GBPUSD 2022-01-04 ASK → HTTP **200**, 11,426 bytes.
- a later EURUSD request received `Connection reset by peer`.

Conclusion: Dukascopy is load-sensitive under our earlier concurrency and remains intermittently unstable even with serial access. Supabase was not the primary cause of the stopped historical run.

## Recovery implementation — PR #7

PR #7: `Phase 1: harden Dukascopy throttling recovery`

### TDD evidence

Red commit `b26306ceebcad10641ae4658a6d9179f21057aa1` added tests requiring:

- configurable delay between consecutive source chunks;
- CLI `--source-delay` support.

CI run `32561686275` failed exactly on those two missing behaviors while existing tests remained green.

Green implementation commit `619e8e5cb9dfec83e3e4d5b8d604799493be3072` added the minimal pacing support. Subsequent Python CI passed all **20 tests**.

### Recovery workflow shape

The proposed full-history workflow now:

- runs at **max-parallel: 1**;
- uses calendar-month shards instead of pair/year shards;
- processes all three V1 pairs sequentially inside each active month;
- uses immediate Supabase mirroring for every result;
- uses `--attempts 8`;
- uses `--source-delay 5` seconds;
- verifies each month locally after acquisition;
- caps the first snapshot at exclusive `2026-08-21`;
- keeps failed months isolated and retryable.

The proposed live regression smoke now covers EUR/USD 2024-01-02 through 2024-01-07 inclusive (both sides), with the same 8-attempt / 5-second pacing policy. Python tests and the all-pair golden sample are green. The strengthened multi-day source smoke is the remaining pre-merge gate.

DEC-011 records the throttling recovery decision.

## Manifest retry incident — FIXED

A prior duplicate cloud smoke found regenerated manifests differ by `retrieved_at_utc` even when raw market data is identical.

Current v3 rule:

- raw `.bi5` objects remain strictly byte-for-byte immutable;
- duplicate manifest bytes are accepted directly when SHA-256 matches;
- when manifest bytes differ, semantic comparison ignores **only** top-level `retrieved_at_utc`;
- every other manifest field must match;
- first cloud manifest remains stored; retry attempts do not overwrite it;
- substantive conflicts still return HTTP 409.

Merged via PR #5 at commit `a2906a37f380dc6c4d27e90d46f15c2c2731d417`.

## Remaining Phase 1 gates

- [ ] hardened multi-day source smoke PASS
- [ ] PR #7 merged and main-branch cloud smoke PASS
- [ ] serialized monthly full-history recovery triggered
- [ ] every planned pair/side/date manifest accounted for
- [ ] expected source-404/market-closure manifests accounted for
- [ ] no unexplained missing planned chunks
- [ ] final cloud provenance/coverage evidence recorded
- [ ] Phase 1 acceptance gate recorded PASS
- [ ] Phase 1 checkpoint recorded

## Immediate next action

1. Wait for the hardened multi-day source smoke on PR #7 to pass or produce a concrete failure.
2. Do not merge on a pending/failed network gate.
3. If green, merge PR #7 and verify the merge-triggered main-branch cloud smoke against Supabase.
4. Only after that, issue a fresh `[phase1-full]` recovery trigger using the serialized monthly workflow.
5. Independently audit the private bucket against all 25,500 planned manifests before Phase 1 can PASS.
6. Keep Phase 2 locked throughout recovery.

## Known open decisions

1. Exact chronological train/validation/final-test boundaries — Phase 2 data-quality dependent.
2. Exact intrabar ambiguity policy implementation details — Phase 3.
3. Exact demo broker/adapter — Phase 8/9.
4. Exact live capital/risk — outside current scope until Phase 10 review + Phase 11 approval.

## Backlog — do not pull forward

- economic-calendar/event-risk filter
- tick-level execution validation
- dashboard
- advanced multi-pair correlation controls
- alternative data
- broader cloud hosting beyond Phase 1 raw persistence
- live-money execution
- indices/crypto/gold/commodities
