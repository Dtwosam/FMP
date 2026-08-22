# FMP Project State

**Updated:** 2026-08-22  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 1 — Historical Data Acquisition  
**Phase status:** CODE_READY_FOR_BOUNDED_NETWORK_SMOKE  
**Next phase:** Phase 2 — Validation, Normalization & Derived Bars (LOCKED until Phase 1 PASS)

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Historical target: ~2015 to latest complete available period
- Development budget: $0
- Primary historical source candidate: Dukascopy
- Storage: raw source files + manifests in Phase 1; Parquet + DuckDB begins downstream
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

The connected GitHub write surface used for this build does not expose native tag creation, so the immutable checkpoint commit and same-name checkpoint branch are recorded instead. Do not move that checkpoint ref.

## Phase 1 checklist

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
- [x] One-pair and all-pair date-range CLI implemented
- [x] Acquisition coverage report implemented
- [x] Unit tests and compile check pass locally
- [x] Bounded live-network smoke workflow defined
- [ ] Bounded live-network smoke PASS on GitHub runner
- [ ] Retrieval method frozen in `decision-log.md` after live smoke
- [ ] Golden sample acquired and manifests/checksums inspected
- [ ] Full target history acquired for all three pairs and both sides
- [ ] Full acquisition coverage/manifests produced
- [ ] Phase 1 acceptance gate recorded PASS
- [ ] Phase 1 checkpoint recorded

## Current verification evidence

Local isolated implementation verification on 2026-08-22:

- `PYTHONPATH=src python -m unittest discover -s tests -v` → 10 tests PASS
- `python -m compileall -q src tests` → PASS

These tests use deterministic fake HTTP responses. They prove acquisition semantics, not current external network availability.

## Immediate next action

Run the bounded GitHub Actions network smoke against one complete historical EUR/USD UTC weekday (2024-01-02), requiring both BID and ASK chunks, valid LZMA structure, manifests, record counts, and matching SHA-256 checksums.

Only if that passes may the exact retrieval method be frozen. Then proceed to the golden sample and full-history acquisition.

## Known open decisions

1. Exact chronological train/validation/final-test boundaries — Phase 2 data-quality dependent.
2. Exact intrabar ambiguity policy implementation details — Phase 3.
3. Exact demo broker/adapter — Phase 8/9.
4. Exact live capital/risk — explicitly outside current scope until Phase 10 review + Phase 11 approval.

## Blockers

- No code blocker for the bounded Phase 1 network smoke.
- Full raw history must live outside Git by design. A persistent local/free runtime with enough storage is required for the full acquisition artifact; the repository must never absorb large market-data files.

## Backlog — do not pull forward without need

- economic-calendar/event-risk filter
- tick-level execution validation
- dashboard
- multi-pair correlation refinement beyond conservative caps
- alternative data
- cloud hosting
- live-money execution
- indices/crypto/gold/commodities
