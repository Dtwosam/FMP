# Phase 3 Backtesting Engine Design

**Date:** 2026-09-14  
**Status:** Approved design, implementation not started  
**Phase:** 3 — Backtesting Engine  
**Repository baseline:** `4f6c40dcb127e466616af6fbd3a51aa0a2ecfe87`  
**Phase 2 checkpoint:** `fmp-v1-phase2-normalized-data`

## 1. Purpose

Build a deterministic, auditable historical execution simulator before any Phase 4 strategy family is judged. The backtester must enforce realistic bid/ask execution, explicit costs, conservative intrabar ambiguity handling, account/risk state, rejected-signal logging, and reproducible run artifacts.

This phase does not implement strategy research, feature engineering, ML, broker connectivity, shadow execution, demo execution, or live trading.

## 2. Architectural choice

Use a deterministic event-driven execution kernel fed by chronological canonical/derived bars. Polars remains the data-frame/storage layer, but trade/account/risk transitions are explicit state-machine events rather than vectorized PnL formulas.

This is preferred over a fully vectorized backtester because stops, targets, daily halts, simultaneous-risk caps, rejected decisions, next-bar execution, and conservative intrabar ambiguity are stateful and must remain easy to audit. A hybrid/vectorized optimization may be introduced later only if profiling demonstrates a real need and behavior remains identical under golden tests.

## 3. Module boundaries

Phase 3 introduces these logical boundaries under `src/fmp/`:

- `contracts`: stable broker-independent records and enums shared by decision, risk, backtest, and later shadow/demo modes.
- `risk`: risk assessment, position sizing, risk reservation, daily halt, and simultaneous-risk enforcement.
- `backtest.execution`: bid/ask fill semantics, stop/target handling, gap handling, slippage, commission, and intrabar ambiguity policy.
- `backtest.engine`: chronological account/position state machine and orchestration.
- `backtest.costs`: explicit cost-model interfaces and deterministic implementations.
- `reporting`: deterministic run/trade/rejection artifacts and core metrics.

Strategy logic is not introduced in Phase 3. Tests and acceptance fixtures use scripted decisions/order intents so the simulator is proven independently of alpha logic.

## 4. Core contracts

Exact Python names may be adjusted for clarity during implementation, but the semantic records are frozen:

### `Decision`

Represents an already-known directional or no-trade decision. It contains at minimum:

- symbol;
- decision timestamp;
- direction: `LONG`, `SHORT`, or `NO_TRADE`;
- earliest executable timestamp;
- requested risk fraction;
- stop price when directional;
- target price when directional/used;
- stable decision/reason metadata.

A decision never contains a broker-specific order payload.

### `RiskAssessment`

Contains approval/rejection, approved monetary risk, approved units if applicable, stable machine-readable reason code, and human-readable explanation.

### `OrderIntent`

Created only after a directional decision passes risk. It is broker-independent and includes symbol, side, units, stop, target, decision timestamp, and earliest executable timestamp.

### `TradeRecord`

Contains deterministic entry/exit timestamps and prices, side, units, stop/target definitions, exit reason, gross PnL, cost components, net PnL, and pre/post account state needed for audit.

### `BacktestRun`

Identifies the code/data/config inputs and summarizes deterministic outputs including trades, rejections, account/equity series or checkpoints, metrics, and artifact hashes.

## 5. Signal timing and anti-look-ahead contract

A strategy decision based on bar `T` becomes actionable only after that bar is closed. Its earliest executable timestamp is the next chronological bar for that symbol.

The engine must reject or fail closed on any order intent whose earliest executable timestamp is earlier than the first bar after the decision timestamp.

Golden tests must prove that a signal derived from bar `T` cannot fill on bar `T`.

Phase 3 does not choose research split dates or strategy observation rules. It only enforces the declared timing contract supplied to it.

## 6. Bid/ask execution semantics

Entry and exit prices use executable sides rather than midpoint prices:

- LONG entry: ASK side.
- LONG exit: BID side.
- SHORT entry: BID side.
- SHORT exit/cover: ASK side.

At next-bar entry, the relevant bar open is the reference execution price before configured adverse slippage/cost treatment.

Stop/target reachability is evaluated on the executable exit side:

- LONG stop/target checks use BID OHLC.
- SHORT stop/target checks use ASK OHLC.

Spread therefore enters naturally through separate bid/ask observations and must not be added again as a synthetic spread cost.

## 7. Slippage, commission, and financing

Slippage is explicit and adverse:

- buy fills move upward by configured slippage;
- sell fills move downward by configured slippage.

Slippage configuration is expressed in pips and converted by symbol pip convention. Golden tests cover both JPY and non-JPY pairs.

Commission is an explicit deterministic cost model. The default research fixture may use zero commission, but every run identity records the configured commission model/value.

Financing/rollover is represented by a cost-model interface. A zero-financing implementation is valid only when the run explicitly declares zero financing or the holding-period experiment makes financing irrelevant. The engine must not invent a venue-specific financing assumption before a venue/experiment defines one.

## 8. Stop, target, gap, and ambiguity policy

Stop and target become active immediately after entry unless a future strategy contract explicitly declares a later activation rule; Phase 3 fixtures use immediate activation.

### Stop fill

If the executable side opens beyond the stop in an adverse direction, fill at the worse executable bar-open price plus adverse slippage. Otherwise, if the stop is touched intrabar, fill at the stop price plus adverse slippage.

### Target fill

If the executable side reaches the target, fill at the declared target price minus adverse slippage as applicable. Favorable gap-through-target price improvement is not granted; the simulator does not create optimistic execution from OHLC uncertainty.

### Both stop and target reachable in one bar

When 1-minute OHLC indicates both thresholds were reachable and ordering cannot be known, the conservative rule is frozen:

**the stop outcome wins.**

The engine records that the exit was intrabar-ambiguous and resolved conservatively.

### End of data

Any open position at the end of the supplied backtest data closes deterministically on the final executable side and records exit reason `END_OF_DATA`.

## 9. Account state

The initial implementation models one USD-denominated research account with deterministic realized cash/equity accounting.

The engine records at minimum:

- starting equity;
- realized PnL;
- current equity used for new-risk calculations;
- reserved open risk;
- start-of-day risk basis;
- day realized PnL;
- open positions;
- daily halt state.

Unrealized mark-to-market may be tracked for reporting/drawdown where needed, but position sizing and daily realized-loss halt use the explicitly defined bases below rather than an implicit mark convention.

## 10. Risk policy

Existing approved limits are unchanged:

- default risk per trade: 0.25% of current equity;
- hard maximum requested risk per trade: 0.50% of current equity;
- maximum simultaneous open risk: 1.00% of current equity;
- maximum daily realized loss before halt: 1.50%.

A request above the hard per-trade maximum is rejected. It is not silently clamped.

Open positions reserve their approved monetary risk until close. A new entry is rejected if existing reserved risk plus proposed approved risk would exceed the simultaneous-risk limit.

Every rejection receives a stable machine-readable reason code plus human-readable explanation.

## 11. Daily-loss basis and reset

Phase 3 freezes the previously unresolved daily-loss interpretation:

**Daily-loss basis is the account equity snapshot at the start of each UTC calendar day, before that day's realized PnL.**

When cumulative realized PnL for that UTC day is less than or equal to negative 1.50% of that day-start equity basis:

- new entries are blocked for the remainder of that UTC day;
- existing positions are not automatically closed solely because of the halt;
- the halt reason/time is recorded;
- the halt resets deterministically on the next UTC date, whose new day-start equity snapshot becomes the next basis.

## 12. Position sizing

Position size is derived from allowed USD risk divided by USD loss per unit at the stop. Desired profit never affects size.

### EURUSD and GBPUSD

For USD-quoted pairs:

`loss_usd_per_unit = abs(entry_price - stop_price)`

`units = floor(allowed_risk_usd / loss_usd_per_unit)`

### USDJPY

For USD base / JPY quote:

`loss_jpy_per_unit = abs(entry_price - stop_price)`

Convert the stop loss to USD using the adverse stop/fill conversion basis defined by the execution fixture. For the Phase 3 deterministic sizing contract, the stop price is used as the USDJPY conversion denominator:

`loss_usd_per_unit = abs(entry_price - stop_price) / stop_price`

`units = floor(allowed_risk_usd / loss_usd_per_unit)`

Sizing rejects invalid/non-positive stop distance, non-positive equity/risk allowance, unsupported symbols, or zero/invalid conversion values.

## 13. Position concurrency

The engine supports multiple simultaneously open positions because the approved risk policy has a simultaneous-risk cap.

Phase 3 enforces aggregate reserved monetary risk only. Cross-pair USD exposure/correlation logic is explicitly deferred until the policy requires it before multi-position demo/live operation. No rolling-correlation model is invented in Phase 3.

The deterministic event order for simultaneous timestamps must be frozen in tests. The implementation must process exits before evaluating new entries at the same timestamp so legitimately released risk is available for that timestamp's new decisions; within each category, ordering must be stable and documented.

## 14. Rejections and `NO_TRADE`

The engine preserves decisions that do not become trades.

At minimum it distinguishes:

- `NO_TRADE` strategy/decision output;
- timing-contract violation;
- invalid quote/data state;
- invalid stop/target definition;
- per-trade risk cap exceeded;
- simultaneous-risk cap exceeded;
- daily loss halt active;
- position-size calculation invalid.

Reason-code strings are stable contract values and are covered by tests.

## 15. Deterministic reporting

A Phase 3 run produces deterministic machine-readable artifacts for the same inputs/configuration.

Minimum outputs:

- run summary JSON;
- trade records JSON/JSONL or equivalent deterministic representation;
- rejection/decision records;
- metrics JSON;
- manifest containing SHA-256 and byte size for persisted artifacts.

Artifact serialization uses stable key ordering and deterministic formatting so repeated equivalent runs have identical output bytes/digests where timestamps or environment metadata would otherwise create noise.

Run identity includes at minimum:

- code commit;
- processed data manifest/snapshot identity;
- canonical/derived schema version;
- backtest-engine version;
- cost-model configuration;
- risk configuration;
- decision fixture/strategy configuration;
- requested time range/timeframe;
- random seed when any future stochastic component exists.

Phase 3 itself remains deterministic and does not require randomness.

## 16. Core metrics

The Phase 3 reporting layer computes deterministic whole-run metrics sufficient to validate simulator/account correctness:

- net PnL and net return after costs;
- expectancy per closed trade;
- profit factor;
- win rate;
- average win;
- average loss;
- trade count;
- maximum drawdown;
- recovery factor where denominator is meaningful;
- longest winning streak;
- longest losing streak;
- total explicit costs by component.

Sharpe/Sortino and strategy/pair/timeframe/session/year breakdowns are not required for the first Phase 3 kernel unless needed to satisfy the Phase 3 acceptance gate. Those richer research breakdowns belong with actual Phase 4 strategy experiments.

## 17. Failure behavior

The engine fails closed on malformed or unsupported inputs rather than guessing:

- unsupported symbols;
- non-UTC or non-monotonic input where chronological semantics are required;
- missing executable quote side;
- non-finite/non-positive executable prices;
- invalid stop direction;
- invalid units/risk values;
- duplicate executable identities that make event ordering ambiguous.

No input defect is silently repaired by the backtester.

## 18. Required golden tests

The Phase 3 acceptance suite must include hand-calculable cases for:

1. LONG buy at ASK, exit at BID.
2. SHORT sell at BID, cover at ASK.
3. LONG stop hit.
4. SHORT stop hit.
5. LONG target hit.
6. SHORT target hit.
7. Stop and target both reachable in one bar -> conservative stop outcome.
8. Gap through stop -> worse executable bar-open fill.
9. Target gap does not receive favorable price improvement.
10. Signal on bar `T` cannot execute on bar `T`; earliest fill is the next bar.
11. EURUSD/GBPUSD USD-risk sizing.
12. USDJPY sizing and pip/slippage convention.
13. Adverse slippage direction for buys/sells.
14. Commission application.
15. Per-trade hard-risk rejection.
16. Simultaneous open-risk rejection.
17. Exit-before-entry event ordering releases risk deterministically.
18. Daily realized-loss halt.
19. Deterministic UTC next-day halt reset.
20. `NO_TRADE` and rejected decisions are recorded.
21. End-of-data forced close semantics.
22. Repeated identical runs produce identical trade/metric/artifact digests.
23. Hand-calculated account/equity/PnL scenario agrees exactly with engine output.

The full repository regression suite must also remain green.

## 19. Phase 3 acceptance gate

Phase 3 is not PASS merely because the engine exists. It can close only when:

- the stable contracts needed for backtest/risk execution are frozen and tested;
- bid/ask entry/exit semantics are proven by golden tests;
- stops, targets, conservative intrabar ambiguity, and gap handling are proven;
- risk sizing for JPY and non-JPY pip conventions is proven;
- per-trade, simultaneous-risk, and daily-halt controls are proven;
- explicit cost modeling and deterministic accounting are proven;
- rejected decisions/reason codes are retained;
- repeated runs are deterministic;
- hand-calculated golden scenarios agree with the engine;
- deterministic run/trade/metrics/manifests are produced and inspected;
- full regression CI is green;
- a Phase 3 acceptance record is reviewed before checkpoint `fmp-v1-phase3-backtester` is created.

## 20. Non-goals

Not part of this Phase 3 design:

- strategy families or parameter research;
- leakage-safe feature-engine implementation;
- ML/statistical models;
- walk-forward evaluation;
- live quote ingestion;
- shadow/demo/live broker adapters;
- broker-specific financing tables;
- tick-level sequencing of ambiguous bars;
- portfolio correlation models;
- dashboards;
- distributed backtesting;
- any real-money path.

## 21. Safety and source boundaries

All Phase 3 commits and PR titles use `[phase1-no-source]`.

Phase 3 must not:

- invoke Dukascopy/source acquisition;
- mutate `fmp-raw`;
- modify `docs/phase1-exact-gap-queue.json`;
- reopen Phase 1 or Phase 2 acceptance without new integrity evidence;
- enable broker/live execution;
- start Phase 4 before Phase 3 is formally accepted.
