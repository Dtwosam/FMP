# Phase 4 Mean-Reversion Baseline Design

**Date:** 2026-09-14  
**Status:** APPROVED IN CHAT — written-spec review pending  
**Repository:** `Dtwosam/FMP`  
**Base commit:** `212d9214d0d0da2d7ed1525b5d79e37466779a65`  
**Phase:** Phase 4 — Baseline Strategy Research  
**Experiment:** `EXP-20260914-003`  
**Decision:** `DEC-020`

## 1. Objective

The third sequential Phase 4 family is a deterministic intraday mean-reversion baseline. The purpose is to test whether a fresh statistically large displacement of fully closed midpoint price from its recent rolling mean tends to revert toward that mean quickly enough to overcome historical BID/ASK spread and adverse slippage under the already accepted Phase 3 execution and risk model.

No profitability is assumed. A failed family is a valid research outcome and must remain recorded.

This design does not change Phase 3 execution semantics, does not alter the frozen session-breakout candidate, does not revisit rejected trend-continuation parameters, does not unlock the final-test split, does not start Phase 5, and does not authorize broker/live or real-money trading.

## 2. Governing source-of-truth decisions

This family is subordinate to the existing approved rules.

- DEC-018 remains authoritative for the Phase 4 chronological split, final-test lock, source-free research boundary, left-labelled timing bridge, cost-sensitivity requirements, and unchanged Phase 3 risk settings.
- DEC-019 remains the historical protocol for `EXP-20260914-002` only; its rejected trend-continuation grid is not modified or reused as a tuning surface here.
- DEC-008 remains unchanged: real-money trading is locked.
- The approved Phase 4 family order remains session breakout, trend continuation, mean reversion, previous-day high/low rejection, volatility breakout, session high/low sweep/rejection.

## 3. Chosen formulation and rejected alternatives

The admitted formulation is a rolling midpoint-close z-score mean-reversion baseline.

Two alternatives were considered but are not part of `EXP-20260914-003`:

1. RSI/oscillator mean reversion — rejected for this experiment because it adds indicator smoothing and threshold degrees of freedom without improving structural interpretability.
2. Rolling-range or Donchian-style mean reversion — rejected for this experiment because it overlaps materially with later approved previous-day high/low and session sweep/rejection families.

The z-score formulation is preferred because its lookback, displacement threshold, target, and stop can all be defined directly from a closed rolling price distribution with a small bounded grid.

## 4. Eligible universe

Pairs:

- EURUSD;
- GBPUSD;
- USDJPY.

Signal timeframes:

- 5m;
- 15m;
- 1h.

Canonical 1m remains the origin of Phase 2 derived bars but is not an eligible signal timeframe for this experiment.

Each pair/timeframe is benchmarked independently. Multi-pair portfolio optimization, correlation sizing, and cross-symbol signals are outside this experiment.

## 5. Chronological split and final-test lock

The frozen Phase 4 chronology is unchanged.

- **Development:** 2015-01-01 through 2020-12-31 inclusive.
- **Validation:** 2021-01-01 through 2023-12-31 inclusive.
- **Final untouched test:** 2024-01-01 through 2026-08-20 inclusive.

Normal mean-reversion development/validation tooling must reject any request for the final split before loading market data.

No result from the final-test period may be inspected under `EXP-20260914-003`. Final access remains reserved for a later explicit promotion gate after baseline candidate selection is materially complete.

## 6. Price series and timing contract

### 6.1 Analytical price

All signal calculations use midpoint close only:

`mid_close = (bid_close + ask_close) / 2`

BID/ASK prices remain untouched and remain the sole execution-price source inside the Phase 3 backtester.

### 6.2 Left-labelled bar timing

Phase 2 derived bars are left-labelled. A bar labelled `T` represents the interval beginning at `T` and is usable only after that full bar has closed.

For a timeframe of width `W`:

- observation label: `T`;
- signal-known time: `T + W`;
- Phase 3 decision timestamp: `T`;
- earliest executable timestamp: `T + W`, which is the next supplied bar label under the accepted timing bridge.

No signal may execute on its own observation bar.

### 6.3 London session

Named timezone: `Europe/London`.

For each London-local trading date:

- eligible observation labels are 08:00 through 14:00 inclusive;
- only fully closed bars may contribute to reference statistics or signals;
- exact mandatory flat timestamp is 16:00 London local time.

UTC conversion must use timezone-aware/DST-aware logic. Hard-coded seasonal UTC offsets are forbidden.

If the exact 16:00 London exit bar is unavailable, that session fails closed as non-tradable evidence; the exit is never shifted to a nearby bar.

## 7. Rolling statistic

### 7.1 Wall-clock lookback grid

Lookbacks are exactly:

- 4h;
- 8h;
- 16h.

Each duration must convert exactly to a whole number of bars for the selected timeframe.

Examples:

| Lookback | 5m bars | 15m bars | 1h bars |
| --- | ---: | ---: | ---: |
| 4h | 48 | 16 | 4 |
| 8h | 96 | 32 | 8 |
| 16h | 192 | 64 | 16 |

No shortened history or partial lookback is allowed.

### 7.2 Reference mean and standard deviation

The observation bar is **not** included in its own reference distribution. This avoids self-dilution of the excursion and ensures every declared threshold remains reachable even for the four-bar 1h/4h configuration.

At eligible observation bar index `i`, for lookback size `N`, use the `N` fully closed midpoint closes immediately preceding `i`:

`R_i = {x_(i-N), ..., x_(i-1)}`

Reference mean:

`mean_i = sum(R_i) / N`

Population variance:

`variance_i = sum((x_j - mean_i)^2 for x_j in R_i) / N`

Population standard deviation:

`std_i = sqrt(variance_i)`

Current z-score:

`z_i = (x_i - mean_i) / std_i`

The previous z-score `z_(i-1)` is computed independently against its own preceding `N`-bar reference window `R_(i-1) = {x_(i-N-1), ..., x_(i-2)}`. Therefore neither the current nor previous observation is included in the distribution against which that observation is standardized.

### 7.3 Eligibility requirements

A signal observation is ineligible unless both the current and previous z-scores are valid.

That requires:

- complete `N`-bar reference window before the current observation;
- complete `N`-bar reference window before the previous observation;
- exact expected timestamp cadence throughout every required bar from the first bar of the previous reference window through the current observation bar;
- positive finite population standard deviation in both reference windows;
- finite midpoint closes, means, and z-scores.

A missing cadence, zero variance, non-finite statistic, or insufficient history makes the observation ineligible. History is never shortened to recover a signal.

## 8. Fresh-excursion signal

### 8.1 Threshold grid

Absolute z-score thresholds are exactly:

- 1.5 standard deviations;
- 2.0 standard deviations.

Combined with the three lookbacks, this produces exactly six strategy configurations per pair/timeframe.

### 8.2 LONG

For threshold `k`, LONG requires a fresh lower-band excursion:

- previous `z > -k`; and
- current `z <= -k`.

### 8.3 SHORT

For threshold `k`, SHORT requires a fresh upper-band excursion:

- previous `z < +k`; and
- current `z >= +k`.

### 8.4 Equality and retriggering

Equality is handled exactly by the formulas above:

- touching the threshold on the current bar qualifies if the previous z-score was strictly inside the band;
- a previous z-score exactly on the threshold is not considered inside and therefore does not create a new crossing on the next still-outside bar.

Remaining outside the band does not retrigger. A directional candidate requires a fresh crossing from inside the band to on/beyond the threshold.

### 8.5 One signal per London date

Only the first qualifying directional signal for the symbol/configuration on a London-local date may become a candidate.

After the first qualifying directional signal is emitted, later crossings that day are ignored for that configuration regardless of whether the resulting order is accepted, rejected by Phase 3 geometry/risk, or later stopped/targeted.

If no qualifying fresh excursion occurs during the eligible window, the session is retained as `NO_TRADE` evidence.

## 9. Frozen stop and target geometry

Signal-time geometry is derived only from the current observation close and its immediately preceding closed reference distribution, then frozen.

Let:

- `x = current signal midpoint close`;
- `m = current reference mean from R_i`;
- `s = current reference population standard deviation from R_i`.

### 9.1 LONG geometry

For a lower-band excursion:

- target = `m`;
- stop = `x - 1.0 * s`.

### 9.2 SHORT geometry

For an upper-band excursion:

- target = `m`;
- stop = `x + 1.0 * s`.

### 9.3 Geometry invariants

At signal time, a valid LONG setup requires `stop < x < target`; a valid SHORT setup requires `target < x < stop`.

Any signal-time violation is emitted as explicit non-tradable evidence rather than repaired.

The actual next-bar BID/ASK executable entry may make the frozen stop/target invalid under Phase 3 rules. If so, the order is rejected with the accepted `INVALID_STOP_TARGET` semantics. Strategy/research code must not move the stop, move the target, chase the entry, widen risk, or retry later.

The target remains the signal-time reference mean even though later reference means will change as new bars close.

## 10. Mandatory intraday exit

Every directional candidate declares the exact 16:00 `Europe/London` flat timestamp for its London date.

Execution remains owned by Phase 3:

- LONG time exit sells on BID;
- SHORT time exit buys on ASK;
- executable-side open is used at the exact scheduled-exit bar;
- existing adverse slippage and commission semantics apply;
- a position already closed by stop/target makes the scheduled exit a deterministic no-op;
- existing-position exits continue to precede same-timestamp new entries.

Missing exact exit data fails closed.

## 11. Frozen parameter grid

The strategy grid is exactly:

| Lookback | Threshold |
| --- | ---: |
| 4h | 1.5σ |
| 4h | 2.0σ |
| 8h | 1.5σ |
| 8h | 2.0σ |
| 16h | 1.5σ |
| 16h | 2.0σ |

There are exactly **6 strategy configurations per pair/timeframe**.

No additional threshold, lookback, stop multiple, target definition, session window, trend filter, volatility filter, or retrigger behavior may be introduced after results are observed under `EXP-20260914-003`.

Any later expanded mean-reversion hypothesis requires a new experiment ID and a new pre-result decision.

## 12. Cost and risk assumptions

Historical BID/ASK spread is inherent in the supplied bars and Phase 3 fills.

Adverse slippage scenarios are exactly:

- 0.2 pips per fill;
- 0.5 pips per fill;
- 1.0 pip per fill.

Commission: zero.  
Financing: zero.

These zero assumptions are admissible only because the family is mandatorily flat intraday by 16:00 London and remain explicit in every experiment identity/artifact.

Accepted Phase 3 risk settings remain unchanged:

- requested risk/trade: 0.25% of realized risk equity;
- hard maximum risk/trade: 0.50%;
- maximum simultaneous reserved open risk: 1.00%;
- daily realized-loss halt: 1.50% of UTC day-start realized risk equity.

Strategy code never sizes positions and never computes executable fills.

## 13. Benchmark matrix and deterministic candidate reuse

The result-producing benchmark is fixed at:

- 3 pairs;
- 3 timeframes;
- 2 chronological splits;
- 6 strategy configurations;
- 3 cost scenarios.

Workflow cells:

`3 × 3 × 2 = 18`

Configuration rows:

`18 × 6 × 3 = 324`

For each pair/timeframe/split/lookback/threshold configuration, signal candidates must be generated exactly once. The same deterministic candidate bytes, candidate count, and reason-count breakdown are reused across all three slippage scenarios.

Changing costs must not regenerate or mutate alpha candidates.

## 14. Experiment identity and artifacts

The experiment is `EXP-20260914-003 — Mean reversion baseline`.

Every result artifact must bind at least:

- experiment/protocol identity;
- strategy family/version;
- exact merged-main code commit;
- accepted Phase 2 processed-manifest SHA-256;
- canonical schema version;
- pair and timeframe;
- split name and exact boundaries;
- lookback and threshold;
- candidate SHA-256/count/reason counts;
- adverse slippage;
- commission/financing identity;
- risk configuration;
- starting equity;
- deterministic backtest run identity;
- research metrics and required breakdowns.

The benchmark artifact and manifest must be deterministic and internally hash/size verified using the existing Phase 4 artifact pattern.

Runtime clock, hostname, UUID, and process-specific metadata remain forbidden from deterministic evidence.

## 15. Promotion screen

The same frozen strategy configuration — same lookback and threshold — must first satisfy all three baseline conditions on both development and validation at 0.2-pip adverse slippage:

- net return > 0;
- expectancy/trade > 0;
- profit factor > 1.

Development-only or validation-only winners are not serious candidates.

A baseline survivor is then assessed under the repository research standard for:

- 0.5-pip adverse-slippage survival;
- neighboring lookback/threshold stability;
- calendar-year/subperiod concentration;
- adequate trade count for the observed frequency;
- fixed-risk maximum drawdown;
- top-winner dependence/outlier concentration;
- absence of leakage or timing defects.

The 1.0-pip slippage scenario is diagnostic and is not a universal mandatory promotion condition.

A single best point without neighborhood support is not enough for promotion.

No arbitrary universal trade-count minimum is invented here; the observed sample is reported and judged under the existing Phase 4 research standard.

## 16. Source-free and safety boundary

Mean-reversion research may consume only accepted Phase 2 processed artifacts through the existing read-only research data path.

The implementation and benchmark must not:

- request Dukascopy or any upstream source;
- invoke Phase 1 acquisition commands;
- mutate `fmp-raw`;
- write through `fmp-raw-read`;
- modify `docs/phase1-exact-gap-queue.json`;
- use Phase 1 acquisition credentials;
- access the final-test split;
- add broker/live integration;
- unlock real-money trading.

All post-Phase1 commits/PR titles retain `[phase1-no-source]`.

## 17. Module boundaries

Implementation, after written-spec approval and an implementation plan, will follow existing Phase 4 family boundaries.

### `fmp.strategies.mean_reversion`

Owns only deterministic setup logic:

- config validation;
- duration-to-bar conversion;
- midpoint-close reference mean/population standard deviation/z-score;
- fresh-excursion detection;
- first-signal-per-date behavior;
- frozen stop/target geometry;
- deterministic `SignalCandidate` generation and metadata.

It does not load storage, size positions, apply slippage, simulate fills, or write conclusions.

### `fmp.research.mean_reversion`

Owns research orchestration:

- exact six-point grid;
- exact three cost scenarios;
- accepted split loader;
- deterministic candidate hashing/reuse;
- candidate-to-Phase3 decision adaptation;
- Phase 3 backtest invocation;
- research metric aggregation;
- fixed result protocol and artifact payload.

### Thin CLI and workflow

A thin script/workflow will follow the existing source-free family pattern:

- explicit pair/timeframe/development-or-validation inputs only;
- no final split argument;
- fixed 18-cell merged-main matrix;
- accepted Phase 2 artifact download/read only;
- one deterministic benchmark artifact per cell;
- fail closed on identity mismatch or missing data.

## 18. Required tests

Implementation must proceed test-first and cover at minimum:

### Statistics and configuration

- config accepts only 4h/8h/16h and 1.5σ/2.0σ;
- duration-to-bar counts are exact for 5m/15m/1h;
- hand-calculated midpoint reference mean is correct;
- hand-calculated population standard deviation and z-score are correct;
- the observation close is excluded from its own reference distribution;
- the 1h/4h/2.0σ configuration can produce a qualifying synthetic signal;
- zero standard deviation is ineligible;
- insufficient history is ineligible;
- missing cadence anywhere in the previous/current required context is ineligible.

### Signal semantics

- LONG requires previous z strictly above `-k` and current z at/below `-k`;
- SHORT requires previous z strictly below `+k` and current z at/above `+k`;
- intrabar high/low threshold touches do not matter because signal statistic uses closed midpoint close;
- remaining outside the band does not retrigger;
- returning inside and crossing again later is still ignored after the first qualifying signal that London date;
- first qualifying direction only per London date;
- complete session without crossing produces auditable `NO_TRADE`;
- candidate serialization is byte deterministic.

### Geometry and timing

- LONG target equals the signal-time preceding-window reference mean and stop equals signal close minus one reference standard deviation;
- SHORT geometry is symmetric;
- target/stop remain frozen after the signal;
- observation label, true-known time, and next-bar execution follow DEC-018 exactly;
- actual next-bar fill that invalidates geometry is rejected rather than repaired;
- exact 16:00 London scheduled exit is required;
- London winter/summer DST examples map correctly to UTC;
- missing exact exit fails closed.

### Runner and evidence

- final split is rejected before data loading;
- grid is exactly six strategy configurations;
- slippage scenarios are exactly 0.2/0.5/1.0;
- candidate SHA/count/reason counts are identical across cost scenarios for a fixed strategy configuration;
- one cell preserves exactly 18 configuration rows;
- full workflow shape is 18 cells / 324 rows;
- accepted Phase 2 processed-manifest identity is bound;
- artifacts and manifests are deterministic;
- workflow is source-free and path-scoped to the mean-reversion surface;
- Phase 1 source-capable PR guards skip with `[phase1-no-source]`;
- existing Phase 3 and prior Phase 4 regression suites remain green.

## 19. Implementation sequence after written-spec approval

No code is authorized by this document alone until the written-spec review gate is passed and a detailed implementation plan is produced.

After that gate, implementation should proceed in this order:

1. pre-result state/contract tests for DEC-020 and EXP-003;
2. mean-reversion config/statistic RED tests;
3. minimal statistic/config implementation;
4. signal/geometry/timing RED tests;
5. minimal deterministic candidate generator;
6. research-grid/runner RED tests;
7. minimal research orchestrator;
8. thin source-free CLI;
9. source-free fixed-matrix workflow plus workflow tests;
10. full regression/guard review;
11. merge implementation only after exact green CI;
12. run the fixed merged-main 18-cell benchmark;
13. independently verify every artifact before recording any result;
14. record PASS/PROMOTE or FAIL/REJECT without post-result grid expansion.

## 20. Acceptance of this design

This design is complete when the written specification has been reviewed and accepted with no unresolved placeholders or ambiguous signal/execution rules.

Approval of this design authorizes an implementation plan, not a benchmark result, Phase 4 completion, final-test access, Phase 5, broker/live work, or real-money trading.
