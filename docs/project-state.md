# FMP Project State

**Updated:** 2026-08-22  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 1 — Historical Data Acquisition  
**Phase status:** READY_FOR_FULL_HISTORY_ACQUISITION  
**Next phase:** Phase 2 — Validation, Normalization & Derived Bars (LOCKED until Phase 1 PASS)

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Historical target: ~2015 to latest complete available period
- Development budget: $0
- Historical source: Dukascopy daily M1 BID/ASK `.bi5`, frozen by DEC-009
- Storage: immutable raw source files + manifests in Phase 1; Parquet + DuckDB begins downstream
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
- [x] Explicit recheck path for delayed `not_found` chunks implemented
- [x] Transient 5xx retry hardening implemented and tested
- [x] One-pair and all-pair date-range CLI implemented
- [x] Acquisition coverage report implemented
- [x] Full snapshot provenance verifier implemented
- [x] Unit tests and compile check pass locally
- [x] Standard GitHub CI PASS
- [x] Bounded live-network smoke PASS on GitHub runner
- [x] Retrieval method frozen in `decision-log.md` as DEC-009
- [x] Golden sample acquired and manifests/checksums inspected for all V1 pairs
- [ ] Full target history acquired for all three pairs and both sides
- [ ] Full snapshot verifier returns `ready: true`
- [ ] Full acquisition coverage/manifests archived with the research snapshot
- [ ] Phase 1 acceptance gate recorded PASS
- [ ] Phase 1 checkpoint recorded

## Verification evidence

### Local deterministic verification

Latest isolated local verification after snapshot-verifier implementation:

- `PYTHONPATH=src python -m unittest discover -s tests -v` → 13 tests PASS
- `python -m compileall -q src tests` → PASS

### GitHub clean-run verification

Hardened branch verification at commit lineage ending in `7aa0ee23357a0ccd0cb7af6f1650dd09a4df2ea8`:

- unit-test workflow run `32541626130` → PASS
- bounded network smoke run `32541626110` → PASS
- all-pair golden sample run `32541626104`, job `96952617097` → PASS

The golden sample verified 6/6 pair-side chunks on 2024-01-02 UTC, all with 1,440 records and matching SHA-256 manifests. Detailed hashes and the earlier transient-503 investigation are preserved in `docs/phase1-golden-sample.md`.

The newer full-snapshot verifier code must also pass the current PR CI before the acquisition tooling is merged.

## Immediate next action

Acquire the full Phase 1 historical snapshot in persistent storage outside Git, then run:

```bash
PYTHONPATH=src python -m fmp.data.cli verify \
  --pair ALL \
  --start 2015-01-01 \
  --end <EXCLUSIVE_LATEST_COMPLETE_DATE> \
  --out data
```

The verifier must return `"ready": true`. This proves acquisition/provenance completeness only. It does not declare the market data clean; Phase 2 owns that judgment.

## Known open decisions

1. Exact exclusive end date for the first frozen full snapshot — set immediately before the persistent acquisition run to a safely complete historical date.
2. Exact chronological train/validation/final-test boundaries — Phase 2 data-quality dependent.
3. Exact intrabar ambiguity policy implementation details — Phase 3.
4. Exact demo broker/adapter — Phase 8/9.
5. Exact live capital/risk — explicitly outside current scope until Phase 10 review + Phase 11 approval.

## Blockers

- Full raw history must live outside Git by design.
- The current ChatGPT execution container does not provide reliable outbound access to Dukascopy for the long-lived raw snapshot, while GitHub Actions runners are ephemeral. A persistent $0 storage/runtime must hold the full acquisition artifact before Phase 1 can honestly pass.
- This blocker does not justify skipping Phase 1 or starting Phase 2 from a partial/golden dataset.

## Backlog — do not pull forward without need

- economic-calendar/event-risk filter
- tick-level execution validation
- dashboard
- multi-pair correlation refinement beyond conservative caps
- alternative data
- cloud hosting
- live-money execution
- indices/crypto/gold/commodities
