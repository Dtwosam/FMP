# Phase 4 Baseline Strategy Research Design

**Date:** 2026-09-14  
**Status:** APPROVED DESIGN — implementation not started  
**Repository:** `Dtwosam/FMP`  
**Base:** Phase 3 formally PASS at checkpoint `fmp-v1-phase3-backtester`  
**Scope:** Phase 4 — Baseline Strategy Research

## 1. Objective

Phase 4 establishes transparent, reproducible non-ML strategy benchmarks on top of the accepted Phase 2 data and Phase 3 backtester. The purpose is to determine whether simple baseline families show robust evidence of edge after realistic execution costs, not to maximize in-sample profitability.

The project succeeds in Phase 4 either by identifying one or more serious baseline candidates or by producing credible evidence that the tested baselines do not show robust edge, with failed experiments preserved and the next research question justified.

Phase 4 does not add machine learning, a general Phase 5 feature engine, broker integration, live execution, or real-money permission.

## 2. Research principles

All Phase 4 work follows these rules:

- assume no edge until evidence supports one;
- implement one strategy family at a time behind a common strategy/research interface;
- predeclare hypotheses and bounded parameter ranges before results are inspected;
- evaluate chronologically;
- keep the final test untouched until candidate selection is materially complete;
- preserve realistic bid/ask execution, slippage, commission, risk sizing, ambiguity rules, and rejection logging through the accepted Phase 3 engine;
- retain failed experiments permanently;
- prefer broad, stable parameter behavior over a single best point;
- never promote on development performance alone;
- never use Phase 4 strategy logic to size positions or simulate fills.

## 3. Phase 4 decomposition

Phase 4 is executed as sequential family slices rather than one large six-family implementation.

Approved family order:

1. session breakout;
2. trend continuation;
3. mean reversion;
4. previous-day high/low rejection;
5. volatility breakout;
6. session high/low sweep/rejection.

The first implementation slice establishes the reusable research harness and the session-breakout family only. Later family slices reuse the same contracts and evidence format.

Phase 4 remains ACTIVE until the baseline program satisfies the Phase 4 acceptance gate.

## 4. Module boundaries

New Phase 4 code will live under focused packages rather than notebooks or one-off scripts.

### `fmp.strategies`

Owns deterministic alpha/setup logic. Strategy code:

- consumes only information available from fully closed supplied bars;
- emits structured signal candidates and optional strategy exit schedules;
- does not size positions;
- does not calculate broker fills;
- does not mutate risk state;
- does not write experiment conclusions.

### `fmp.research`

Owns research-only orchestration:

- chronological split definitions;
- processed-Parquet loading;
- experiment specifications and identities;
- parameter-grid expansion;
- strategy-candidate to Phase 3 `Decision` conversion;
- execution of deterministic backtests through `run_backtest`;
- cost-sensitivity runs;
- pair/timeframe/subperiod aggregation;
- benchmark artifacts and experiment evidence.

### Existing Phase 3 modules

`fmp.backtest`, `fmp.risk`, and `fmp.reporting` remain the single source of truth for fills, costs, risk, PnL, and base backtest metrics. Phase 4 must not duplicate those semantics.

## 5. Common strategy contracts

Phase 4 introduces immutable research records with stable serialization.

### `StrategyConfig`

Contains at minimum:

- family ID;
- strategy version;
- parameter mapping;
- eligible timeframe;
- session/timezone identity where relevant.

### `SignalCandidate`

Contains at minimum:

- stable candidate ID;
- symbol;
- observation-bar timestamp label;
- direction (`LONG`, `SHORT`, or `NO_TRADE` where useful);
- stop price;
- target price;
- optional latest-exit timestamp;
- reason/setup code;
- deterministic metadata needed to audit the setup.

The candidate contains no approved units and no risk amount.

### `StrategyProtocol`

A deterministic strategy consumes an ordered sequence of `QuoteBar` values plus `StrategyConfig` and returns ordered `SignalCandidate` values. Re-running the same bars/configuration must return byte-equivalent serialized candidates.

### Candidate-to-decision adapter

The research layer converts directional candidates into the accepted Phase 3 `Decision` type.

Phase 2 derived bars are left-labelled buckets. Therefore a bar labelled `T` represents the interval beginning at `T`; the strategy may use that bar only after it is fully closed. To preserve the accepted Phase 3 timing contract, the `Decision.decision_timestamp_utc` uses the closed observation bar's label `T`, while `earliest_executable_timestamp_utc` is the immediately following supplied bar label. Strategy tests must prove that no candidate can execute on its own observation bar.

## 6. Narrow scheduled-exit extension

A session strategy requires a deterministic intraday flat time. The accepted Phase 3 engine currently supports stop, target, and end-of-data exits but has no explicit strategy-timed exit. Letting unmatched trades remain open overnight would make financing materially relevant and would change the intended session-breakout hypothesis.

Phase 4 therefore includes one backward-compatible execution extension:

- add a structured scheduled-exit instruction keyed to the originating decision/position;
- a scheduled exit executes at the first supplied bar whose timestamp equals the declared exit timestamp;
- the exit fills at the executable side **open** of that bar, with the existing adverse slippage, commission, and PnL rules;
- LONG scheduled exits sell on BID; SHORT scheduled exits buy on ASK;
- stop/target handling on earlier bars remains unchanged;
- at a timestamp where an existing position has a scheduled exit, that exit is processed before new entries, consistent with the Phase 3 exit-before-entry rule;
- if the position has already closed by stop/target, the scheduled exit is a deterministic no-op;
- supplying no scheduled exits preserves existing Phase 3 behavior and artifacts.

This is an execution capability, not alpha logic. The strategy may declare **when** a position must be flat; the backtester remains solely responsible for **how** the fill is executed and accounted.

A new exit reason such as `TIME_EXIT` is required so a strategy session close is not mislabeled as `END_OF_DATA`.

All existing Phase 3 golden tests must remain green, and new golden tests must cover LONG and SHORT scheduled exits, ordering, slippage/cost application, and no-op behavior after an earlier stop/target.

## 7. Frozen chronological split

The first serious Phase 4 experiment uses the complete accepted Phase 2 date coverage while keeping a recent final period untouched.

Frozen split:

- **Development:** 2015-01-01 through 2020-12-31 inclusive.
- **Validation:** 2021-01-01 through 2023-12-31 inclusive.
- **Final untouched test:** 2024-01-01 through 2026-08-20 inclusive.

These boundaries are fixed before strategy results are inspected and must be recorded in the decision log before the first serious experiment is run.

Rules:

- parameter exploration occurs on development only;
- the predeclared bounded grid may be evaluated once on validation for stability/selection;
- validation results may cause rejection or a frozen candidate choice;
- final-test data is not loaded by the development/validation runner;
- access to final-test results requires a separate explicit research promotion step after candidate selection is materially complete;
- a final-test result may confirm or reject a candidate but may not trigger another round of parameter tuning against that same final period.

## 8. Experiment identity and evidence

Every serious run uses the existing `EXP-YYYYMMDD-NNN` identity.

An `ExperimentSpec` must include:

- experiment ID and pre-result hypothesis;
- code commit;
- processed-data manifest/version identity;
- schema version;
- strategy family/version/config;
- pair(s);
- timeframe(s);
- development/validation/final split identity;
- cost model;
- slippage scenario;
- commission/financing assumptions;
- risk configuration;
- random seed if ever relevant.

An `ExperimentResult` must preserve:

- deterministic run identities;
- trade/rejection evidence;
- required headline metrics;
- pair/timeframe breakdown;
- session breakdown where applicable;
- calendar-year/subperiod breakdown;
- cost-sensitivity breakdown;
- robustness summaries;
- conclusion (`PROMOTE`, `REJECT`, `REVISE`, or `NEED_MORE_DATA`);
- reason and follow-up.

Machine-readable artifacts are the reproducible evidence source. `docs/experiment-log.md` remains the human-readable experiment registry and must include failures.

## 9. Processed-data loading

The Phase 4 loader reads only Phase 2 processed Parquet plus its processed-data manifest. It has no Dukascopy/source acquisition code and no write access to `fmp-raw`.

Requirements:

- require explicit dataset root and processed-manifest identity;
- require requested pair/timeframe to exist in the manifest;
- load only the requested chronological split;
- preserve sorted UTC bars;
- reject incomplete/duplicate identities rather than silently fixing them;
- convert stored Phase 2 rows deterministically to Phase 3 `QuoteBar` values;
- never fetch or regenerate source data implicitly.

The research code remains portable: CI/local runners may provide the accepted Phase 2 materialization by any documented read-only mechanism, but strategy code itself is storage-agnostic.

## 10. Session-breakout baseline

### 10.1 Hypothesis

After a completed pre-London range, a confirmed break during the early London session may exhibit enough short-horizon continuation on some V1 pair/timeframe combinations to overcome bid/ask spread, adverse slippage, and fixed-risk execution.

No profitability is assumed.

### 10.2 Eligible universe

Pairs:

- EURUSD;
- GBPUSD;
- USDJPY.

Timeframes:

- 5m;
- 15m;
- 1h.

Canonical 1m remains the source of derived bars but is not an eligible signal timeframe for this initial family.

### 10.3 Session definition

Named timezone: `Europe/London`.

For each London-local trading date:

- range window: **00:00 inclusive to 08:00 exclusive**;
- breakout-observation window: **08:00 inclusive to 12:00 exclusive**;
- mandatory flat timestamp: **16:00 London local time**.

UTC timestamps are converted with timezone-aware/DST-aware logic. Hard-coded seasonal UTC offsets are forbidden.

Only bars fully contained inside the relevant local window may contribute to that window. Incomplete Phase 2 bars (`is_complete == false`) are ineligible for signal/range construction.

### 10.4 Analytical price

Strategy analysis uses deterministic midpoint OHLC derived as the arithmetic mean of corresponding BID and ASK fields. Bid/ask remain untouched and are still used by the Phase 3 engine for all execution.

For a session:

- range high = maximum midpoint high of eligible range-window bars;
- range low = minimum midpoint low of eligible range-window bars;
- range width = range high minus range low.

A session with no complete positive-width range is `NO_TRADE`.

### 10.5 Breakout signal

Only the first qualifying directional breakout in a symbol/session may generate a trade candidate.

LONG candidate:

- a fully closed breakout-window bar has midpoint close strictly greater than `range_high + buffer`.

SHORT candidate:

- a fully closed breakout-window bar has midpoint close strictly less than `range_low - buffer`.

If neither occurs before the breakout window ends, the session is `NO_TRADE`.

If contradictory qualification could occur because of malformed data, the session is rejected rather than direction-picked after inspection.

### 10.6 Stop and target

LONG:

- stop = frozen session range low;
- target = `range_high + target_range_multiple * range_width`.

SHORT:

- stop = frozen session range high;
- target = `range_low - target_range_multiple * range_width`.

The risk engine sizes the trade from the actual executable reference entry and stop distance. Strategy code never selects units.

The declared latest exit is the 16:00 London-local timestamp for that session, mapped to the matching supplied bar label. If no exact eligible exit bar exists, the candidate is rejected with explicit evidence rather than silently moving the cutoff.

### 10.7 Predeclared parameter grid

Pip size:

- EURUSD/GBPUSD: `0.0001`;
- USDJPY: `0.01`.

Breakout buffer grid:

- `0` pips;
- `2` pips;
- `5` pips.

Target range-multiple grid:

- `0.5`;
- `1.0`;
- `1.5`.

This creates exactly **9 configurations per pair/timeframe**. No additional session-breakout parameter may be introduced after development results are seen without creating a new experiment ID and explicitly documenting the new hypothesis/search expansion.

## 11. Cost and risk scenarios

Spread is always the historical BID/ASK spread contained in the supplied bars.

The first session-breakout experiment uses zero commission and zero financing because the strategy is mandatorily flat intraday by 16:00 London; both assumptions must still be recorded explicitly.

Predeclared adverse slippage scenarios:

- baseline: `0.2` pips per fill;
- stress 1: `0.5` pips per fill;
- stress 2: `1.0` pip per fill.

Risk configuration remains the accepted research policy:

- requested risk/trade: `0.25%` of realized risk equity;
- hard max risk/trade: `0.50%`;
- maximum simultaneous open risk: `1.00%`;
- daily realized-loss halt: `1.50%` of UTC day-start realized risk equity.

The initial family is benchmarked per pair/timeframe, not as a multi-pair portfolio optimization. Portfolio/correlation construction is not part of this slice.

## 12. Development and validation discipline

For every pair/timeframe:

1. run all 9 predeclared configurations on the development split under baseline costs;
2. produce the full benchmark table, including losing configurations;
3. run predeclared cost sensitivities;
4. inspect neighboring-parameter stability and calendar-year/subperiod behavior;
5. reject configurations whose apparent edge is dominated by a tiny period or a few trades;
6. evaluate the same predeclared grid once on validation rather than inventing new points to repair development failures;
7. freeze any candidate selection before the final-test gate.

No configuration is promoted merely for being the single best development result.

Minimum serious-candidate evidence remains the repository research gate: positive net expectancy after realistic costs, adequate sample size for the observed strategy frequency, no discovered leakage, no obvious dependence on one tiny period/few outlier trades, and acceptable drawdown under fixed risk.

The runner reports trade count rather than inventing an arbitrary universal minimum before observing the natural strategy frequency; any later explicit minimum sample-size threshold must be predeclared in a new decision before it is used as a promotion rule.

## 13. Required reporting

The Phase 4 benchmark artifact must report, where mathematically meaningful:

- net return after costs;
- expectancy/trade;
- profit factor;
- win rate;
- average win;
- average loss;
- reward/risk distribution;
- maximum drawdown;
- recovery factor;
- Sharpe/Sortino when supported by the return series definition;
- trade count;
- longest winning/losing streaks;
- pair breakdown;
- timeframe breakdown;
- session breakdown;
- calendar-year/subperiod breakdown;
- cost-sensitivity breakdown.

The artifact must also preserve strategy `NO_TRADE` sessions, risk/execution rejections, and scheduled-exit counts so absence of trades is auditable.

## 14. Determinism and anti-leakage tests

The first Phase 4 implementation must include tests for:

- deterministic strategy candidate generation;
- midpoint derivation;
- exact session-window inclusion/exclusion;
- London DST examples on both sides of seasonal transitions;
- no use of breakout bar data before that bar closes;
- earliest execution on the next supplied bar only;
- first-breakout-only behavior per symbol/session;
- exact 0/2/5-pip buffer behavior for JPY and non-JPY pairs;
- exact 0.5/1.0/1.5 range-multiple target math;
- invalid/empty/zero-width session -> `NO_TRADE` or explicit rejection;
- scheduled LONG and SHORT time exits at executable-side open;
- stop/target before scheduled exit suppresses the later scheduled exit;
- scheduled exits processed before same-timestamp entries;
- Phase 3 regression suite remains green when no scheduled exits are supplied;
- split loader cannot read final-test dates during development/validation mode;
- deterministic experiment IDs/config serialization;
- deterministic repeated benchmark artifact bytes.

## 15. First implementation slice

The first Phase 4 implementation plan covers only:

1. research split and experiment contracts;
2. strategy protocol and candidate records;
3. narrow scheduled-exit extension to the accepted Phase 3 engine;
4. deterministic processed-Parquet research loader;
5. candidate-to-`Decision`/scheduled-exit adapter;
6. experiment runner and benchmark artifact writer;
7. session-breakout strategy with the frozen rules/grid above;
8. experiment-log integration;
9. development/validation-only source-free tests and acceptance fixtures.

Serious full-history experiment execution occurs only after this infrastructure is merged and verified. The final-test period remains inaccessible to the normal development/validation runner.

## 16. Explicit non-goals for this slice

Do not implement:

- the other five baseline families;
- generic Phase 5 feature tables;
- machine learning/statistical models;
- random search or Bayesian optimization;
- final-test evaluation;
- walk-forward evaluation;
- tick-data research;
- live quotes;
- broker adapters;
- shadow/demo/live modes;
- Supabase writes or raw-source acquisition;
- real-money permissions.

## 17. Phase 4 acceptance boundary

Completing the first session-breakout slice does **not** make Phase 4 PASS.

Phase 4 can close only after baseline benchmark tables exist for every family actually admitted to the Phase 4 baseline program and at least one of the documented Phase 4 outcomes is supported:

- one or more strategies qualify as serious candidates; or
- evidence clearly shows the current baselines have no robust edge, with failures preserved and the next research question justified.

Formal Phase 4 checkpoint remains `fmp-v1-phase4-baselines` and is not created by the first-family implementation slice.

## 18. Safety and phase boundaries

All Phase 4 commits and PR titles continue to use `[phase1-no-source]` while Phase 1 source-capable PR guards exist.

Phase 4 may read accepted processed data but must not mutate Phase 1 raw storage or trigger source acquisition. `docs/phase1-exact-gap-queue.json` remains untouched.

Phase 5 does not start during Phase 4. DEC-008 remains unchanged: real-money trading is locked.