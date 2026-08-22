# FMP Project State

**Updated:** 2026-08-22  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 0 — Source-of-truth freeze  
**Phase status:** READY_TO_CLOSE_AFTER_REPO_COMMIT  
**Next phase:** Phase 1 — Historical Data Acquisition

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Historical target: ~2015 to latest complete available period
- Development budget: $0
- Primary historical source candidate: Dukascopy
- Storage: Parquet + DuckDB
- Language: Python
- ML: optional, only after baselines
- Execution choice: deferred until demo/shadow needs justify it
- Real-money trading: locked

## Phase 0 checklist

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
- [ ] Source-of-truth commit merged into repository default branch
- [ ] Phase 0 checkpoint/tag recorded after merge

## Immediate next action after Phase 0 merge

Begin **Phase 1 Task 1** only: establish the minimal tested Python project foundation required by the historical-data acquisition path. Do not build strategies, indicators, ML, dashboard, or broker execution.

Before choosing a Dukascopy programmatic acquisition method, run a small bounded acquisition spike and verify exact returned fields, granularity, timestamps, limits, and licensing/usage constraints from official/free sources. Then freeze the retrieval method in a decision-log entry.

## Known open decisions (not blockers for Phase 0)

1. Exact programmatic Dukascopy retrieval mechanism for Phase 1.
2. Exact chronological train/validation/final-test date boundaries, to be set after Phase 2 data-quality inspection.
3. Exact intrabar ambiguity policy implementation details, to be frozen in Phase 3 before strategy benchmarking.
4. Exact demo broker/adapter, deferred until Phase 8/9.
5. Exact live capital/risk, explicitly outside current scope.

## Blockers

None for beginning Phase 1 after the source-of-truth commit is merged/frozen.

## Backlog — do not pull forward without need

- economic-calendar/event-risk filter
- tick-level execution validation
- dashboard
- multi-pair correlation refinement beyond conservative caps
- alternative data
- cloud hosting
- live-money execution
- indices/crypto/gold/commodities
