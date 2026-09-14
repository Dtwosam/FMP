# Phase 5 Leakage-Safe Feature Engine Design

**Status:** PROPOSED — written-spec approval required before DEC-029, implementation, or feature generation  
**Date:** 2026-09-14  
**Phase 4 checkpoint:** `fmp-v1-phase4-baselines` → `115bb8080e951db16ca1a1174227ffa181a03d1b`  
**Final-test touched?: NO**

## 1. Goal and source constraints

Phase 5 creates reusable descriptive market features from the accepted Phase 2 processed data without hiding future information. The feature layer is a transformation layer only: it does not generate labels, choose strategies/models, size risk, send orders, or change the two frozen Phase 4 candidates.

The project source requires:

- features computable only from information available at decision time;
- timezone/DST-correct session features;
- deterministic, versioned/reproducible feature datasets;
- reset-boundary tests for previous-day/session features;
- no accidental forward-fill across inappropriate market closures;
- leakage tests for every promoted feature family;
- checkpoint `fmp-v1-phase5-features` only after the Phase 5 acceptance gate passes.

This design keeps the untouched 2024-01-01 through 2026-08-20 final-test period inaccessible throughout Phase 5.

## 2. Bounded V1 feature-set scope

### Included research timeframes

Generate independent feature tables for exactly:

- 5m
- 15m
- 1h

for exactly EURUSD, GBPUSD, and USDJPY.

The canonical 1m history remains the immutable upstream source used by Phase 2, but Phase 5 V1 does **not** create a separate 1m feature dataset. The reason is scope control: 5m/15m/1h are the approved research timeframes and cover both frozen Phase 4 candidates. Adding a 1m feature matrix later requires an explicit Phase 5 amendment rather than silently multiplying dataset size.

### Included history

Feature generation may open processed partitions only for:

- 2015-01-01 through 2023-12-31 inclusive.

It must reject any request whose output or required source partition reaches 2024-01-01 or later **before that partition is opened**. The final-test period remains untouched, not merely excluded from model fitting.

### Promoted feature families for `fmp-feature-v1`

Exactly eight source-approved families are promoted into the initial feature set:

1. returns
2. volatility/range
3. trend/structure
4. momentum
5. candle structure
6. session/time
7. market location vs previous/session highs/lows
8. spread/quote quality

`relative source activity` is deliberately **not** promoted in `fmp-feature-v1`. The source permits it only “where valid,” and Dukascopy/source activity must not be described as total global spot-FX volume. Activity features require a separate semantic/data-validity decision after the core feature engine passes.

Cross-pair joins and multi-timeframe joins are also deferred. Each V1 feature row depends only on the same symbol and same timeframe, removing an unnecessary alignment/leakage surface from the first feature-engine acceptance.

## 3. Row-time / availability contract

Phase 2 derived bars are left-labelled. For a bar labelled `bar_start_utc = T` with duration `D`:

- `bar_end_utc = T + D`
- `available_at_utc = bar_end_utc`
- the feature row represents information available only after that bar has fully closed.

A Phase 5 feature at row `available_at_utc` may use:

- the complete current closed bar `[T, T + D)`; and
- earlier closed bars whose `bar_end_utc <= available_at_utc`.

It may never use any observation from a bar ending after `available_at_utc`.

Every persisted row includes at minimum:

- `symbol`
- `timeframe`
- `bar_start_utc`
- `bar_end_utc`
- `available_at_utc`
- `feature_set_version = fmp-feature-v1`
- accepted Phase 2 processed-manifest SHA256

Rows are sorted by `(symbol, timeframe, bar_start_utc)` and are unique on that key.

## 4. Price basis and pip semantics

Descriptive price features use midpoint OHLC derived deterministically from BID/ASK. Execution semantics remain BID/ASK and are not changed by Phase 5.

Pip size is exactly:

- EURUSD: `0.0001`
- GBPUSD: `0.0001`
- USDJPY: `0.01`

All price-distance features named `*_pips` divide a price difference by this pip size.

For duration-based windows, expected bar counts are derived exactly from the timeframe. A rolling/duration feature is null unless its required timestamps are present, finite, and cadence-complete. Rolling windows do not bridge market closures/gaps by carrying the last observation forward.

## 5. Frozen `fmp-feature-v1` dictionary

### 5.1 Returns

Using midpoint close `C_t` at the current closed bar:

- `return_1bar = C_t / C_{t-1} - 1`
- `return_1h = C_t / C_{t-1h} - 1`
- `return_24h = C_t / C_{t-24h} - 1`
- `log_return_1bar = ln(C_t / C_{t-1})`

Duration-return anchors require an exact timestamp match and a cadence-complete path between anchor and current row; otherwise null.

### 5.2 Volatility / range

- `range_pips = (mid_high_t - mid_low_t) / pip_size`
- `true_range_pips = max(high-low, abs(high-prev_close), abs(low-prev_close)) / pip_size`
- `realized_vol_1h = sqrt(sum(log_return_1bar^2))` over the complete trailing 1h including current closed bar
- `realized_vol_8h` analogously over trailing 8h
- `realized_vol_24h` analogously over trailing 24h
- `range_vs_prior_median_8h = current_range / median(prior closed-bar ranges over [T-8h, T))`

The prior-median reference excludes the current bar. Zero/non-finite denominators produce null.

### 5.3 Trend / structure

For complete trailing windows including the current closed bar:

- `sma_distance_2h_pips = (C_t - mean(close, trailing 2h)) / pip_size`
- `sma_distance_8h_pips = (C_t - mean(close, trailing 8h)) / pip_size`
- `sma_slope_2h_pips = (SMA_2h(t) - SMA_2h(t-1bar)) / pip_size`
- `sma_slope_8h_pips = (SMA_8h(t) - SMA_8h(t-1bar)) / pip_size`
- `breakout_above_prior_8h = 1` iff `C_t > max(mid_high over [T-8h, T))`, else `0`
- `breakout_below_prior_8h = 1` iff `C_t < min(mid_low over [T-8h, T))`, else `0`

The breakout reference excludes the current bar.

### 5.4 Momentum

- `roc_4h = C_t / C_{t-4h} - 1`
- `roc_8h = C_t / C_{t-8h} - 1`
- `momentum_accel_4h = roc_4h(t) - roc_4h(t-4h)`

All anchors require exact timestamps and cadence-complete paths.

### 5.5 Candle structure

From midpoint OHLC of the current closed bar:

- `body_pips = abs(close-open) / pip_size`
- `upper_wick_pips = (high-max(open,close)) / pip_size`
- `lower_wick_pips = (min(open,close)-low) / pip_size`
- `body_to_range = abs(close-open)/(high-low)`
- `close_location = (close-low)/(high-low)`
- `candle_direction = -1, 0, +1` for bearish/doji/bullish
- `directional_streak` = number of consecutive non-doji bars ending at the current bar with the same direction, capped at 20

Zero-range bars produce null for ratio/location fields rather than fabricated values.

### 5.6 Session / time

Session membership is computed from the bar interval start using named time zones; a bar is session-labelled only when its complete interval lies within the stated local session.

Frozen V1 session definitions:

- Asia: `09:00 <= local time < 17:00`, `Asia/Tokyo`
- London: `08:00 <= local time < 16:00`, `Europe/London`
- New York: `08:00 <= local time < 17:00`, `America/New_York`
- London/New York overlap: both London and New York flags are true for the same bar interval

Features:

- `hour_utc`
- `minute_utc`
- `day_of_week_utc` (`0=Monday ... 6=Sunday`)
- `is_asia_session`
- `is_london_session`
- `is_new_york_session`
- `is_london_new_york_overlap`
- `minutes_since_asia_open` (null outside Asia)
- `minutes_since_london_open` (null outside London)
- `minutes_since_new_york_open` (null outside New York)

DST tests must include both Europe/London and America/New_York transition regimes, including weeks where US and UK DST transitions do not coincide.

### 5.7 Market location

Reference levels come only from **completed** sessions with exact cadence and finite midpoint OHLC. A level is intentionally carried until the next qualifying completed reference session; this is reference-level semantics, not generic forward-fill.

Previous FX day uses the already-tested New-York-close convention: `[17:00 America/New_York, 17:00 America/New_York)`.

Features:

- `prev_fx_day_high_dist_pips = (C_t - previous_completed_fx_day_high) / pip_size`
- `prev_fx_day_low_dist_pips = (C_t - previous_completed_fx_day_low) / pip_size`
- `prev_fx_day_close_dist_pips = (C_t - previous_completed_fx_day_close) / pip_size`
- `prev_asia_high_dist_pips` / `prev_asia_low_dist_pips` from the most recent completed `09:00–17:00 Asia/Tokyo` session
- `prev_london_high_dist_pips` / `prev_london_low_dist_pips` from the most recent completed `08:00–16:00 Europe/London` session

If no complete prior reference session exists, the relevant fields are null.

### 5.8 Spread / quote quality

Current close spread uses authoritative BID/ASK close values:

- `spread_close_pips = (ask_close-bid_close)/pip_size`
- `spread_mean_1h_pips` over a complete trailing 1h including current closed bar
- `spread_median_prior_8h_pips` over `[T-8h, T)`, excluding current
- `spread_vs_prior_median_8h = current_spread / prior_8h_median`
- `spread_percentile_prior_24h` = fraction of complete prior-24h spread-close observations `<= current_spread`

Non-positive/non-finite denominators produce null. No quote anomaly is silently repaired.

## 6. Missingness and market-closure policy

No generic forward-fill is permitted for price, return, volatility, trend, momentum, candle, or spread features.

A rolling feature becomes null when:

- any required bar/timestamp is missing;
- a non-finite required value is present;
- the exact cadence requirement fails; or
- the required rolling window crosses a market closure/gap rather than containing a complete continuous bar sequence.

After a reopen, each rolling feature remains null until enough post-reopen history exists to satisfy its full window.

Session/time flags remain computable from timestamps. Completed previous-day/session reference levels may persist by explicit definition until superseded by the next complete reference session.

Warm-up nulls are expected and are never backfilled from future rows.

## 7. Architecture and outputs

Create a new package boundary:

- `src/fmp/features/`

The feature module consumes accepted processed bars and does not mutate them. It has no dependency on strategies, risk, execution, broker/live adapters, or model labels.

Each family is implemented behind a separate deterministic function/module so leakage and formula tests can target it independently.

Output layout (Git-ignored data, evidence manifests retained as workflow artifacts):

```text
data/features/fmp-feature-v1/<symbol>/<timeframe>/<year>/<month>.parquet
```

Each 3-pair × 3-timeframe generation cell produces an evidence manifest containing at minimum:

- feature-set version
- code commit
- accepted Phase 2 processed-manifest SHA256
- symbol/timeframe
- source coverage actually opened
- output coverage
- row count and unique-key count
- schema / feature-column list and schema hash
- null counts per feature
- output file names, byte sizes, and SHA256 digests
- generation parameters (which are fixed by this design)

A tracked human-readable dictionary, `docs/phase5-feature-dictionary.md`, must match the machine-readable schema used by the generator.

## 8. Determinism / leakage test contract

Implementation is not accepted unless tests cover all eight promoted families and include at least:

1. **Prefix equivalence:** generating features on history truncated at time `U` must produce byte/value-equivalent rows through `U` to a full-history generation.
2. **Future perturbation:** modifying bars whose `bar_end_utc` is strictly after a feature row's `available_at_utc` must not change that row or any earlier row.
3. **Current-bar allowance:** modifying the current closed bar may change the feature row available at that bar end, proving the contract is “current closed data allowed,” not an accidental one-bar lag.
4. **Exact-cadence failures:** missing/incomplete rolling windows return null deterministically rather than shortening the lookback.
5. **Closure behavior:** no generic feature is forward-filled through weekend/market closure gaps; post-reopen warm-up is enforced.
6. **Reference-session completeness:** incomplete previous-day/Asia/London reference sessions are not used; complete prior-session levels persist only by explicit reference semantics.
7. **DST/session examples:** named-zone session flags/open-minute features are correct across US and UK DST transitions and their mismatched transition weeks.
8. **Deterministic regeneration:** same code + same processed-manifest identity + same inputs produces identical canonical dataset digests and evidence manifests.
9. **Final-test hard block:** requests or source-partition reads reaching 2024-01-01 or later fail before final-period data is opened.
10. **Schema/key guards:** output rows remain sorted, unique, finite where required, and feature dictionary/schema identity is stable.

## 9. Acceptance workflow

A source-free Phase 5 acceptance workflow will operate only on the accepted Phase 2 processed artifacts/manifests. It may not call Dukascopy, Supabase raw acquisition/write paths, brokers, or any live endpoint.

Frozen acceptance matrix:

- 3 pairs × 3 timeframes = 9 feature-generation cells
- output through 2023-12-31 only
- all eight promoted feature families in every cell

For each cell, acceptance requires:

- generation SUCCESS;
- manifest/data identity exact;
- deterministic regeneration digest match;
- leakage/cadence/DST/reset/closure tests PASS;
- no final-test partition opened;
- feature dictionary/schema match;
- reproducible artifact hashes recorded.

Phase 5 PASS requires all 9 cells plus the repository-wide unit/YAML/compile and unchanged Phase 3 regression surfaces to be green.

After merged-main acceptance evidence is verified, create checkpoint `fmp-v1-phase5-features` at the exact accepted Phase 5 closure commit.

## 10. Explicit non-goals / locks

This phase does not:

- create labels or targets;
- fit scalers, encoders, feature selectors, or models;
- select features based on profitability or target association;
- retune either Phase 4 candidate;
- read the 2024-01-01 through 2026-08-20 final-test period;
- add 1m feature matrices;
- add cross-pair or multi-timeframe joins;
- promote relative source activity features;
- touch broker/live/demo/real-money execution.

Phase 6 remains responsible for statistical/ML questions and chronological train-only fitting of preprocessors/models.

## 11. Approval gate

Approval of this written design would authorize a formal DEC-029 predeclaration and a test-first Phase 5 implementation plan. It would **not** authorize final-test access or model fitting.