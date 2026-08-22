# FMP V1 — Master Specification

**Status:** APPROVED BASELINE — Phase 0 source-of-truth freeze  
**Date:** 2026-08-22  
**Repository:** `Dtwosam/FMP`  
**Project type:** Forex-only systematic trading research and execution engine  
**Development budget:** $0 until any real-money deployment is separately approved

---

## 1. Mission

Build a reproducible forex trading system that can discover, test, reject, and eventually execute strategies with positive expected value after realistic trading costs.

The objective is not to build an impressive AI model. The objective is to determine whether a repeatable trading edge exists and, only if it survives rigorous testing, use it in demo and potentially later live trading.

No profitability is assumed or guaranteed.

## 2. V1 scope

### Instruments
Only:
- EUR/USD
- GBP/USD
- USD/JPY

No indices, gold, crypto, commodities, exotic FX pairs, or additional instruments are part of V1.

### Data resolution
- Canonical research data: 1-minute bid/ask OHLC.
- Derived internally: 5m, 15m, 1h.
- Tick data: deferred to execution-quality validation for promising strategies.

### Historical target
Approximately 2015 through the latest complete usable data. Exact usable ranges are determined by acquisition and quality checks rather than forced to match.

### Time standard
Store raw/processed timestamps in UTC. Session features must use timezone-aware/DST-aware logic.

## 3. Hard constraints

1. Development cost remains $0.
2. V1 remains forex only.
3. Raw market data is immutable.
4. Bid and ask are modeled separately.
5. No look-ahead bias or data leakage.
6. Spread/slippage and relevant fees/financing are modeled.
7. No strategy advances on in-sample performance alone.
8. No real-money execution before all earlier gates and a separate explicit approval.
9. No martingale, loss-chasing, or size escalation to recover losses.
10. Complexity must earn its place through better robust out-of-sample performance.

## 4. Core principles

### Profitability over sophistication
If a simple rule/statistical method outperforms ML after costs and unseen-data tests, use the simple method.

### `NO TRADE` is valid
The system is not required to trade every hour or every day.

### Evidence before deployment
A strategy must progress through increasingly realistic evidence:

`historical research -> realistic backtest -> untouched OOS -> walk-forward -> shadow -> demo -> deployment review`

### Reproducibility
Every serious result must identify:
- code commit;
- data manifest/snapshot;
- schema/feature version;
- strategy/model configuration;
- cost model;
- split definition;
- random seed when applicable.

### Separation of concerns
Data, features, strategy, models, decision, risk, backtest, execution, and reporting remain separate modules with explicit interfaces.

## 5. Initial technology stack

### Core
- Python
- Git/GitHub

### Storage/research
- Parquet
- DuckDB
- Polars and/or Pandas
- NumPy

### Optional later statistical/ML tools
- scikit-learn
- XGBoost
- LightGBM

No ML library is mandatory.

### Visualization later
- Matplotlib and/or Plotly
- Streamlit only if monitoring needs justify it

### Execution later
Broker-adapter boundary only. Candidate later adapters include OANDA practice/live API or MetaTrader 5 Python integration. Broker choice is deliberately deferred.

## 6. Data architecture

Primary historical source candidate: Dukascopy, subject to the Phase 1 bounded acquisition verification.

The ingestion layer normalizes source-specific formats into the FMP canonical schema so the rest of the engine is not Dukascopy-specific.

Minimum canonical 1m fields:
- `timestamp_utc`
- `symbol`
- bid OHLC
- ask OHLC
- source-provided bid/ask volume/activity if available
- `source`
- `ingestion_version`
- `schema_version`

Derived midpoint/spread fields belong in processed data.

Required quality checks include duplicates, ordering, nulls, bid/ask sanity, OHLC consistency, suspicious jumps, missing intervals, market-closure gaps, and spread outliers. Questionable data is flagged and measured, never silently repaired.

Detailed contract: `docs/data-spec.md`.

## 7. Feature families

Only leakage-safe features may be used. Candidate families:
- returns;
- volatility/range;
- trend/structure;
- momentum;
- candle structure;
- session/time;
- previous/session/weekly high-low location;
- spread/quote quality;
- relative source activity where valid.

Spot-FX source volume is not total global FX volume and must not be described as such.

## 8. Strategy research layer

Before ML, establish transparent baselines such as:
- session breakout;
- trend continuation;
- mean reversion;
- previous-day high/low rejection;
- volatility breakout;
- session high/low sweep/rejection.

A strategy may work for one pair/timeframe and fail elsewhere. Nothing is assumed universal.

## 9. Backtesting requirements

The backtester must model at minimum:
- long/short entry semantics;
- bid/ask execution;
- stop loss;
- take profit;
- position size;
- spread;
- slippage;
- account/equity state;
- realized/unrealized PnL where needed;
- maximum open risk;
- drawdown;
- rejected signals/reasons.

If 1-minute OHLC cannot determine whether stop or target came first, the engine uses a conservative/predeclared ambiguity rule or later higher-resolution validation. It never chooses the profitable route after seeing the outcome.

## 10. Splits and anti-leakage

Final evaluation is chronological, not randomly shuffled.

Use:
- development/train;
- validation;
- untouched final test;
- later walk-forward windows.

Exact date boundaries are frozen only after Phase 2 data-quality inspection. Leakage-sensitive preprocessing is fit only on allowed training data.

Detailed standard: `docs/research-testing-standard.md`.

## 11. Machine learning

ML is optional and downstream of baselines.

Potential roles:
- probability target beats stop;
- conditional expected-return estimation;
- rule-signal filtering;
- regime classification.

A model is rejected if its advantage disappears after costs, unseen data, or walk-forward evaluation.

## 12. Decision engine

Output states:
- `LONG`
- `SHORT`
- `NO TRADE`

A directional signal may still be rejected for poor expected value, bad spread, invalid regime, risk limits, correlated exposure, bad data, or later economic-event risk. Rejection reasons are logged.

## 13. Risk engine

Initial research/demo defaults:
- default risk/trade: 0.25% equity;
- hard max risk/trade: 0.50%;
- maximum simultaneous open risk: 1.00%;
- maximum daily realized loss before halt: 1.50%.

Risk is based on allowed loss and stop distance, never desired profit.

Forbidden: martingale, doubling after losses, revenge logic, removing stops because a trade is losing, or increasing leverage to manufacture profitability.

Multi-position demo/live operation must account for overlapping USD exposure across the three pairs.

Detailed policy: `docs/risk-execution-policy.md`.

## 14. Evaluation metrics

Track at minimum:
- net return after costs;
- expectancy/trade;
- profit factor;
- win rate;
- average win/loss;
- reward/risk distribution;
- max drawdown;
- recovery factor;
- Sharpe/Sortino where meaningful;
- trade count;
- streaks;
- pair/timeframe/session/regime/year breakdowns;
- cost sensitivity.

Probability models also require calibration/discrimination analysis.

## 15. Promotion gates

### Research -> serious candidate
Requires positive net expectancy after realistic costs, adequate sample size, no detected leakage, no dependence on a tiny period/few trades, and acceptable drawdown.

### Candidate -> walk-forward
Untouched out-of-sample evidence must remain viable without material collapse.

### Walk-forward -> shadow
Repeated forward windows must show acceptable aggregate expectancy/stability with reproducible procedures.

### Shadow -> demo
Live quote handling, spread, timing, and hypothetical outcomes must materially resemble tested assumptions; shadow structurally cannot submit orders.

### Demo -> deployment review
Enough trades/time/regimes must exist to compare real practice execution to research assumptions and verify risk controls.

### Deployment review -> live
Never automatic. Requires a new explicit human approval and decision-log entry.

## 16. Economic/macro data

Deferred until the price-based core works.

First likely macro addition is an event-risk filter around high-impact releases, not an economic-prediction model. Only free and legally usable sources may be added under V1's $0 constraint.

## 17. System architecture

```text
Historical / Live Data
        |
        v
Data Ingestion
        |
        v
Immutable Raw Store
        |
        v
Validation + Normalization
        |
        v
Canonical 1m + Derived Timeframes
        |
        v
Feature Engine
        |
        v
Strategy Candidates
        |
        +--> Optional Statistical/ML Filter
        |
        v
Decision Engine
        |
        v
Risk Engine
        |
        v
Backtest / Shadow / Demo / Live Adapter
        |
        v
Metrics + Logs + Experiments
```

Same strategy/decision/risk interfaces should be reused across modes so deployment cannot quietly change research logic.

Detailed architecture: `docs/architecture.md`.

## 18. Repository shape

```text
FMP/
├── README.md
├── AGENTS.md
├── docs/
│   ├── master-spec.md
│   ├── architecture.md
│   ├── build-order.md
│   ├── data-spec.md
│   ├── research-testing-standard.md
│   ├── risk-execution-policy.md
│   ├── project-state.md
│   ├── decision-log.md
│   ├── experiment-log.md
│   ├── source-register.md
│   └── source-of-truth-changelog.md
├── data/                  # large data ignored by Git
├── src/forex_engine/
├── tests/
└── notebooks/
```

Code/data directories are created only as their active phase needs them.

## 19. Build phases

0. Source of truth & repository foundation
1. Historical data acquisition
2. Validation, normalization & derived bars
3. Backtesting engine
4. Baseline strategy research
5. Leakage-safe feature engine
6. Statistical/ML experiments
7. Walk-forward evaluation
8. Live shadow mode
9. Demo trading
10. Deployment review
11. Live execution, only after separate approval

Detailed acceptance criteria: `docs/build-order.md`.

## 20. Phase discipline

- Complete phases in order unless this spec is explicitly amended.
- Code existing does not mean a phase passed.
- Tests and acceptance artifacts must pass.
- Failed experiments remain recorded.
- New nonessential ideas go to backlog.
- Scope expansion requires a decision-log entry plus source-of-truth edits.

## 21. Experiment discipline

Every meaningful experiment records ID, date, hypothesis, pairs/timeframes, data version/range, features, strategy/model config, cost assumptions, risk assumptions, split definition, results, conclusion, and code commit.

Registry format: `docs/experiment-log.md`.

## 22. Definition of V1 success

V1 can succeed honestly in either form:

### A. Deployable edge
At least one system survives realistic costs, unseen data, walk-forward, shadow, and demo well enough to justify a separate real-money decision.

### B. Credible rejection
Rigorous evidence shows tested approaches do not provide a robust enough edge, with failed results preserved and understood.

A beautiful backtest alone is not success.

## 23. Explicit non-goals

Not in initial V1:
- indices;
- gold;
- crypto;
- commodities;
- exotic FX;
- social-media sentiment;
- LLM trade calls;
- copy trading;
- paid signals/data;
- automated strategy generation;
- reinforcement-learning live trading;
- high-frequency trading;
- tick-level model training by default;
- public SaaS/mobile product.

## 24. Verified external foundations

As of 2026-08-22:
- Dukascopy official historical export documents bid/ask prices and trading volumes: https://www.dukascopy.com/api/data/get/historical-data-export
- OANDA documents separate fxTrade Practice REST/streaming environments: https://developer.oanda.com/rest-live-v20/development-guide/
- MetaTrader 5 documents official Python integration for quotes/ticks/account/order/position operations: https://www.mql5.com/en/docs/python_metatrader5

These are candidates, not permanent vendor dependencies. Implementation-specific details are reverified in the relevant phase. See `docs/source-register.md`.

## 25. Current project state

The V1 baseline is approved. Phase 0 documentation is being committed through the `phase0/source-of-truth` branch. No trading code, historical acquisition, backtester, strategies, ML, shadow system, demo integration, or live integration has been implemented yet.

After the source-of-truth change is merged/frozen, the next phase is **Phase 1 — Historical Data Acquisition**.

Current live state belongs in `docs/project-state.md` rather than this stable master section.

## 26. Change control

Silent architectural drift is forbidden. A future decision that conflicts with this baseline requires an explicit decision-log entry and corresponding edits to affected source-of-truth documents before implementation proceeds.

## 27. Source-of-truth precedence

If files conflict, use this order:

1. `docs/project-state.md` for current phase/blocker/checkpoint.
2. `docs/decision-log.md` for later approved amendments.
3. `docs/master-spec.md` for stable V1 scope/architecture/constraints.
4. `docs/build-order.md` for sequence and acceptance gates.
5. Component specs.
6. README/explanatory files.

A lower-precedence file cannot silently override a higher-precedence file.

## 28. Repository identity and portable source

Canonical repo: https://github.com/Dtwosam/FMP

The repository is the live engineering record. A downloadable `FMP_PROJECT_SOURCE.md` is the portable ChatGPT Project baseline. Future sessions should read this baseline, then inspect the repository's current `project-state.md` and `decision-log.md` before continuing.
