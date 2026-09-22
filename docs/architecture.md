# FMP V1 Architecture

**Status:** Approved baseline  
**Scope:** Forex only  
**Repository:** `Dtwosam/FMP`

## Architectural objective

Separate research logic from data-source and broker-specific details so the same strategy, decision, and risk behavior can be exercised consistently in historical backtests, shadow mode, demo trading, and—only if later approved—live execution.

## Logical flow

```text
Historical / Live Quote Source
            |
            v
      Ingestion Adapter
            |
            v
   Immutable Raw Data Store
            |
            v
 Validation + Normalization
            |
            v
 Canonical 1m Bid/Ask Dataset
            |
            +------> Derived 5m / 15m / 1h Bars
            |
            v
       Feature Engine
            |
            v
  Versioned Strategy Library
            |
            +------> Optional Statistical/ML / Regime Filter
            |
            v
 Champion/Challenger Registry
            |
            v
 Portfolio / Applicability Router
            |
            v
      Decision Engine
     LONG / SHORT / NO TRADE
            |
            v
 Portfolio-Aware Risk Engine
            |
            v
 Mode Adapter: Backtest | Shadow | Demo | Live
            |
            v
    Logs + Metrics + Experiments
```

## Module boundaries

### `data`
Owns source adapters, ingestion manifests, raw-file provenance, validation, normalization, and deterministic timeframe generation. It does not know trading strategy rules.

### `features`
Transforms validated historical information into leakage-safe features. It never mutates raw data and never decides trades.

### `strategies`
Produces transparent candidate signals/setup metadata. Strategy code must not size positions or send broker orders.

### `models`
Optional statistical/ML filtering or probability estimation. It is downstream of leakage-safe features and must be benchmarked against simpler baselines.

### `portfolio`
Owns versioned strategy-registration metadata, champion/challenger eligibility, deterministic candidate aggregation, applicability/regime routing metadata, conflict handling, and exposure summaries. It does not size positions and cannot promote a challenger by itself.

### `decision`
Combines eligible portfolio-routed signal/model evidence with market/execution conditions and emits `LONG`, `SHORT`, or `NO TRADE`, plus reason codes.

### `risk`
Owns position sizing, risk caps, daily halts, simultaneous-risk limits, and correlation/exposure constraints. It is independent of alpha logic.

### `backtest`
Simulates execution against historical bid/ask data with explicit cost and ambiguity policies. It consumes the same decision/risk interfaces intended for later modes.

### `execution`
Broker adapters only. It translates an approved order intent into practice/live broker calls and reports actual execution results back to the engine.

### `reporting`
Produces metrics, diagnostics, run summaries, and auditable artifacts. It does not change trading decisions.

## Core interface philosophy

The engine should pass structured records between modules rather than hiding state in notebooks or global variables. Exact Python types will be frozen during the relevant implementation phase, but these conceptual interfaces are stable:

- `QuoteBar` / canonical market row
- `FeatureRow`
- `SignalCandidate`
- `StrategyVersion`
- `ChampionSet`
- `PortfolioCandidateSet`
- `Decision`
- `RiskAssessment`
- `OrderIntent`
- `ExecutionResult`
- `TradeRecord`
- `BacktestRun`
- `ExperimentRecord`

## Mode parity

A major architectural requirement is **logic parity**:

- Backtest mode may simulate execution, but it must not use a different strategy/risk rule set from shadow/demo.
- Shadow mode produces the same decisions but prevents order submission.
- A registered shadow/demo/live campaign freezes its champion strategy set; the continuous-research path may create challengers but cannot hot-swap them into the active campaign.
- Demo mode sends orders only to a practice account.
- Live mode remains disabled until Phase 11 is explicitly approved.

## Storage architecture

### Raw layer
Source-faithful, immutable files plus ingestion manifests/checksums. Large raw data stays outside Git.

### Processed layer
Normalized canonical 1m Parquet data and deterministic derived timeframes.

### Feature layer
Versioned reproducible feature tables created from processed data.

### Analytical query layer
DuckDB may query local Parquet without requiring a paid server database.

## Reproducibility identity

Every serious result should be recoverable from:

```text
code commit
+ data snapshot/manifest
+ schema version
+ strategy/model config
+ cost model
+ split definition
+ random seed (if any)
= reproducible run
```

## Deferred architecture

Do not prematurely build:

- dashboard infrastructure
- paid cloud deployment
- distributed training
- microservices
- tick-level full-history research pipeline
- LLM-based trading decisions
- live broker failover
- multi-asset portfolio engine outside the three approved V1 FX pairs

These are outside V1 unless evidence creates a real requirement.


## Continuous research and promotion loop

DEC-039 adds a controlled research loop alongside, not inside, the active trading path:

```text
New historical / shadow / demo observations
            |
            v
     Research evidence store
            |
            v
 Challenger discovery / revision
            |
            v
 Frozen historical evaluation
            |
            v
 Explicit promotion gate
            |
            +----> reject / retire
            |
            v
 Future champion-set version
```

The active campaign never reads an unapproved challenger as executable strategy logic. A learner may recommend or materialize a new challenger configuration, but promotion is a versioned evidence event.

## Multi-pair portfolio boundary

The Phase 8A portfolio is still forex-only and limited to EURUSD, GBPUSD, and USDJPY. It is not a general multi-asset engine. The router may combine approved strategy candidates across those pairs, while the risk module remains responsible for total risk, overlapping USD exposure, and correlated-position constraints.
