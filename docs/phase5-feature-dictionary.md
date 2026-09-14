# Phase 5 Feature Dictionary — `fmp-feature-v1`

DEC-029 freezes this dictionary. A row is available only at `available_at_utc`, the end of the current fully closed left-labelled bar. Price-distance fields use midpoint OHLC and the frozen symbol pip size. Rolling windows require exact finite cadence; there is **no generic forward-fill** through gaps or market closures. Normal Phase 5 generation cannot open a processed partition reaching `2024-01-01` or later.

Identity columns are `symbol`, `timeframe`, `bar_start_utc`, `bar_end_utc`, `available_at_utc`, `feature_set_version`, and `processed_manifest_sha256`.

## Returns
- `return_1bar`: midpoint close / previous contiguous midpoint close - 1.
- `return_1h`: exact 1-hour midpoint-close return.
- `return_24h`: exact 24-hour midpoint-close return.
- `log_return_1bar`: natural log of the one-bar close ratio.

## Volatility / range
- `range_pips`: current midpoint high-low range in pips.
- `true_range_pips`: max(current range, high-prev close distance, low-prev close distance) in pips.
- `realized_vol_1h`: square root of summed one-bar log-return squares across a complete trailing 1 hour including the current bar.
- `realized_vol_8h`: analogous complete trailing 8-hour realized volatility.
- `realized_vol_24h`: analogous complete trailing 24-hour realized volatility.
- `range_vs_prior_median_8h`: current range divided by the median range over complete prior `[T-8h,T)`, excluding current.

## Trend / structure
- `sma_distance_2h_pips`: current close minus complete trailing-2h close mean, in pips.
- `sma_distance_8h_pips`: current close minus complete trailing-8h close mean, in pips.
- `sma_slope_2h_pips`: current complete 2h SMA minus prior-bar complete 2h SMA, in pips.
- `sma_slope_8h_pips`: current complete 8h SMA minus prior-bar complete 8h SMA, in pips.
- `breakout_above_prior_8h`: 1 iff current close strictly exceeds the complete prior-8h midpoint high, else 0.
- `breakout_below_prior_8h`: 1 iff current close strictly falls below the complete prior-8h midpoint low, else 0.

## Momentum
- `roc_4h`: exact 4-hour close rate of change.
- `roc_8h`: exact 8-hour close rate of change.
- `momentum_accel_4h`: current 4h ROC minus the 4h ROC exactly four hours earlier.

## Candle structure
- `body_pips`: absolute midpoint close-open body in pips.
- `upper_wick_pips`: midpoint high minus max(open,close), in pips.
- `lower_wick_pips`: min(open,close) minus midpoint low, in pips.
- `body_to_range`: absolute body divided by current range; null for zero range.
- `close_location`: `(close-low)/(high-low)`; null for zero range.
- `candle_direction`: -1 bearish, 0 doji, +1 bullish.
- `directional_streak`: consecutive same-direction non-doji bars ending current, capped at 20.

## Session / time
- `hour_utc`: UTC hour of bar start.
- `minute_utc`: UTC minute of bar start.
- `day_of_week_utc`: UTC weekday, Monday=0 through Sunday=6.
- `is_asia_session`: complete interval lies within 09:00-17:00 Asia/Tokyo.
- `is_london_session`: complete interval lies within 08:00-16:00 Europe/London.
- `is_new_york_session`: complete interval lies within 08:00-17:00 America/New_York.
- `is_london_new_york_overlap`: both London and New York flags are true.
- `minutes_since_asia_open`: local minutes from Tokyo session open; null outside.
- `minutes_since_london_open`: local minutes from London session open; null outside.
- `minutes_since_new_york_open`: local minutes from New York session open; null outside.

## Market location
Only exact-cadence, finite completed references qualify. A valid reference may persist until superseded by a later valid completed reference; incomplete references never overwrite it.
- `prev_fx_day_high_dist_pips`: current close distance from most recent completed New-York-close FX-day high.
- `prev_fx_day_low_dist_pips`: current close distance from that FX-day low.
- `prev_fx_day_close_dist_pips`: current close distance from that FX-day close.
- `prev_asia_high_dist_pips`: current close distance from most recent completed Asia-session high.
- `prev_asia_low_dist_pips`: current close distance from most recent completed Asia-session low.
- `prev_london_high_dist_pips`: current close distance from most recent completed London-session high.
- `prev_london_low_dist_pips`: current close distance from most recent completed London-session low.

## Spread / quote quality
- `spread_close_pips`: authoritative ask-close minus bid-close in pips.
- `spread_mean_1h_pips`: mean close spread over a complete trailing 1 hour including current.
- `spread_median_prior_8h_pips`: median close spread over complete prior `[T-8h,T)`, excluding current.
- `spread_vs_prior_median_8h`: current spread divided by positive finite prior-8h median; otherwise null.
- `spread_percentile_prior_24h`: fraction of complete prior-24h spread observations `<=` current spread.

Warm-up, missing cadence, incomplete required bars, non-finite required values, or invalid denominators produce null rather than shortened windows or future backfill.
