# Phase 8A — EXP-064 Continuous-Stability Protocol

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY PROTOCOL FROZEN / EXECUTION LOCKED  
**Decision:** DEC-452  
**Experiment:** EXP-20261001-064  
**Predecessor:** DEC-451

## Purpose

DEC-452 freezes the exact EXP-064 research protocol before any historical execution.

The protocol replaces the retired EXP-061/063 LOW/MID/HIGH atomic-state pattern
family with a much smaller single-feature continuous/rank-effect search.

It does not access source artifacts, execute research, open 2023-2026 robustness,
compile executable candidates, or authorize trading.

## Bound source direction

DEC-452 binds:

- DEC-451 merge:
  `e55df61f766ae49c72f04ac6259928252ae113dc`;
- DEC-451 direction source blob:
  `6a7de1e93515fd3771e3763641ee6a07e425ee8a`.

Protocol source:

`src/fmp/discovery/exp064_continuous_stability_protocol.py`

blob:

`c108ea047c7bfb3e588bfbac33993180066c28ad`.

Focused tests:

`tests/test_phase8a_exp064_continuous_stability_protocol.py`

blob:

`ff09cc2f4a489e08cd682627c4422ceb8772edb2`.

## Frozen universe

The market/data universe remains exactly:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m, 240m;
- the same 20 leakage-safe continuous features already used by EXP-061/063.

No new raw features, symbols, timeframes, horizons, or alternative data are added.

There are exactly 18 symbol/timeframe/horizon cells.

## Rank calibration

Each feature is transformed per symbol/timeframe using the full already-seen
2015-2022 design set only.

The frozen transform is:

`full_design_empirical_midrank_cdf`

Rules:

- finite values only;
- at least 600 calibration rows;
- at least 20 distinct values;
- ties use empirical midrank;
- percentile is centered as `percentile - 0.5`;
- values outside the calibration range naturally map to 0 or 1 under the empirical
  CDF;
- no 2023-2026 row may influence calibration.

The use of the full 2015-2022 design distribution is explicitly retrospective.
It is not described as fresh validation.

## Hypothesis unit

Each hypothesis contains exactly:

- one feature;
- one market direction: LONG or SHORT;
- one feature-effect polarity:
  - INCREASING;
  - DECREASING.

No feature interactions are allowed in EXP-064 v1.

This creates:

- 20 features × 2 directions × 2 polarities = 80 hypotheses per cell;
- 80 × 18 cells = 1,440 hypotheses globally.

This is the complete search universe. No result-driven hypothesis expansion is
permitted.

## Primary continuous effect

For each annual slice, the primary effect is the polarity-signed ordinary least
squares slope of 0.5-pip net outcome on centered empirical rank.

For INCREASING hypotheses the raw slope is used.

For DECREASING hypotheses the raw slope is multiplied by -1.

A positive signed slope therefore always means that the predeclared effect polarity
is supported.

## Economic tail

Each hypothesis also has a deterministic selected tail:

- INCREASING: feature percentile >= 0.75;
- DECREASING: feature percentile <= 0.25.

The tail is not separately searched or optimized.

The selected-tail mean net pips is measured at:

- 0.5-pip design cost;
- 1.0-pip stress cost.

This prevents a statistically monotone effect from qualifying without an
economically positive selected subset.

## Annual persistence statistics

The design years are exactly:

2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022.

For every hypothesis/year the protocol requires statistics for:

- evaluable support;
- selected-tail support;
- signed rank slope at 0.5-pip cost;
- selected-tail mean at 0.5-pip cost;
- selected-tail mean at 1.0-pip stress.

Equal-year aggregation is used so one high-volume year cannot dominate the
persistence decision.

The fixed two-year blocks are:

- 2015-2016;
- 2017-2018;
- 2019-2020;
- 2021-2022.

The lower-half statistic is the arithmetic mean of the four weakest annual values.

## Frozen qualification gate

A hypothesis qualifies only when all of the following hold:

- total selected-tail support >= 600;
- selected-tail support >= 75 in every year;
- signed rank slope is positive in at least 6 of 8 years;
- selected-tail 0.5-pip mean is positive in at least 6 of 8 years;
- equal-year signed rank slope at 0.5-pip cost >= 0.25 pips;
- equal-year selected-tail mean at 0.5-pip cost >= 0.25 pips;
- lower-half annual signed rank slope > 0;
- lower-half annual selected-tail 0.5-pip mean > 0;
- every fixed two-year block has positive signed rank slope;
- every fixed two-year block has positive selected-tail 0.5-pip mean;
- equal-year selected-tail mean at 1.0-pip stress > 0.

These gates are frozen before any EXP-064 historical execution.

## Ranking

Qualifying hypotheses are ranked by:

1. lower-half selected-tail 0.5-pip mean descending;
2. minimum two-year-block selected-tail 0.5-pip mean descending;
3. lower-half signed rank slope descending;
4. minimum two-year-block signed rank slope descending;
5. positive selected-tail year count descending;
6. positive slope year count descending;
7. equal-year selected-tail 1.0-pip stress mean descending;
8. total selected-tail support descending;
9. feature name ascending;
10. direction ascending;
11. polarity ascending;
12. fingerprint ascending.

Maximum shortlist:

- 5 per cell/horizon;
- 90 globally.

Maximum frozen retrospective hypotheses:

- 2 per cell/horizon;
- 36 globally.

A frozen item remains a research hypothesis, not an executable strategy.

## Deduplication

Near-duplicate selected-tail event sets are deduplicated only within the same:

- symbol;
- timeframe;
- horizon;
- market direction.

The Jaccard threshold is 0.95.

The higher frozen rank is retained.

## Evidence semantics

All 2015-2022 outcomes are:

`RETROSPECTIVE_ALREADY_SEEN`

with:

`untouched_oos = false`.

The output kind is:

`RETROSPECTIVE_CONTINUOUS_STABILITY_HYPOTHESIS_NOT_VALIDATED`.

No EXP-064 output may be called fresh validation.

## Reserved robustness

The reserved robustness interval remains:

2023-01-01 through 2026-08-20.

It remains closed and must not affect rank calibration, effect estimation, ranking,
shortlisting, or freezing.

## Locks preserved

DEC-452 keeps false:

- source access;
- historical execution;
- historical result production;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After green merge, the next safe gate is a deterministic source-only EXP-064
in-memory miner core implementing exactly this protocol.

Historical execution remains closed.
