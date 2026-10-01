# Phase 8A — EXP-065 Pairwise Interaction Protocol

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY PROTOCOL FROZEN / EXECUTION LOCKED  
**Decision:** DEC-460  
**Experiment:** EXP-20261001-065  
**Predecessor:** DEC-459

## Purpose

DEC-460 freezes the exact EXP-065 pairwise-interaction hypothesis protocol before
any historical execution.

The protocol is intentionally source-only. It does not read historical artifacts,
produce results, open the reserved robustness block, compile a candidate, authorize
Phase 8B, or create any broker/order path.

## Frozen lineage

DEC-460 binds:

- DEC-459 merge:
  `c0d8ba052cc0cd662149aa787722874c7207ce4a`;
- DEC-459 research-direction source blob:
  `7d9350f714bfec7cc39ebf76b2e6e313261e9a68`;
- DEC-452 rank-transform protocol blob:
  `c108ea047c7bfb3e588bfbac33993180066c28ad`.

The predecessor EXP-064 result remains frozen negative. DEC-460 does not relax or
reinterpret it.

## Bounded universe

EXP-065 keeps exactly:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m and 240m;
- the same 20 leakage-safe continuous features.

No new raw feature, symbol, timeframe, horizon, alternative data, or repair path is
authorized.

## Exactly-two-feature hypothesis unit

The canonical feature list contains 20 features. EXP-065 enumerates each unordered
pair exactly once:

`C(20, 2) = 190` feature pairs.

Each hypothesis is exactly:

- one unordered feature pair;
- one market direction: LONG or SHORT;
- one interaction polarity: INCREASING or DECREASING.

Therefore the frozen search volume is:

- 190 pairs × 2 directions × 2 polarities = **760 hypotheses per cell/horizon**;
- 18 cells/horizons × 760 = **13,680 hypotheses globally**.

Same-feature pairs are forbidden. Three-or-more-feature interactions remain
forbidden.

## Rank and interaction transform

Each constituent feature uses the same full-design empirical-midrank CDF semantics
already frozen by DEC-452 over 2015-2022 only.

For constituent feature percentiles `p_a` and `p_b`, the raw pair interaction is:

`2 * (p_a - 0.5) * (p_b - 0.5)`.

This lies in `[-0.5, 0.5]` and is symmetric in feature order.

For each symbol/timeframe/feature-pair, the complete 2015-2022 raw interaction
series is itself calibrated with a full-design empirical-midrank CDF. At least 600
finite calibration rows and at least 20 distinct values are required. Ties use the
same deterministic empirical-midrank rule.

The resulting interaction percentile is centered by subtracting 0.5 for the
interaction estimator.

Reserved 2023-2026 rows may not affect constituent calibration, pair calibration,
ranking, or any result.

## Selected economic tail

Interaction polarity defines the selected tail:

- INCREASING: interaction percentile >= 0.75;
- DECREASING: interaction percentile <= 0.25.

The selected tail therefore remains a deterministic extreme-quartile subset of the
pair interaction representation.

## Main-effect-controlled interaction estimator

The primary annual effect is not a raw pair correlation.

For each calendar year and exact symbol/timeframe/horizon/direction/pair/polarity,
EXP-065 fits deterministic OLS:

`net_pips_0p5 ~ 1 + centered_rank(feature_a) + centered_rank(feature_b) + centered_rank(interaction)`.

The primary interaction statistic is the polarity-signed coefficient on the
centered interaction rank.

This controls both constituent linear rank effects. Singular designs fail closed
using an exact protocol tolerance of `1e-12`; they are never repaired or
regularized.

## Incrementality requirement

The protocol separately fits the annual main-effects-only model:

`net_pips_0p5 ~ 1 + centered_rank(feature_a) + centered_rank(feature_b)`.

Its residuals represent outcome variation not explained by the two constituent
main effects under this frozen linear-rank control.

The selected interaction tail must therefore show both:

1. positive raw economic outcome; and
2. positive selected-tail mean of the main-effect residual.

This prevents a pair from qualifying merely because one constituent main effect
carries the economics.

No post-result residualization variant, alternate control model, regularizer,
nonlinear main-effect model, or rescue estimator is authorized.

## Frozen annual qualification gate

All eight calendar years 2015 through 2022 must be present.

Support:

- total selected-tail support >= 600;
- selected-tail support >= 75 in every year.

Annual sign counts:

- positive polarity-signed partial interaction slope in at least 6/8 years;
- positive raw selected-tail mean at 0.5-pip design cost in at least 6/8 years;
- positive incremental selected-tail residual mean in at least 6/8 years.

Equal-year requirements:

- mean polarity-signed partial interaction slope at 0.5 pip >= 0.25;
- mean raw selected-tail net pips at 0.5 pip >= 0.25;
- mean incremental selected-tail residual at 0.5 pip > 0;
- mean raw selected-tail net pips at 1.0-pip stress > 0.

Lower-half requirements:

- lower-half annual partial interaction slope > 0;
- lower-half annual raw selected-tail mean > 0;
- lower-half annual incremental selected-tail residual mean > 0.

Every fixed two-year block must also be positive for:

- partial interaction slope;
- raw selected-tail mean;
- incremental selected-tail residual mean.

The fixed blocks are 2015-2016, 2017-2018, 2019-2020, and 2021-2022.

This keeps the predecessor stability philosophy while adding an explicit
interaction-incrementality constraint.

## Ranking and multiplicity controls

The frozen ranking prioritizes:

1. lower-half incremental selected-tail residual mean;
2. worst two-year incremental residual block;
3. lower-half raw selected-tail mean;
4. worst two-year raw selected-tail block;
5. lower-half partial interaction slope;
6. worst two-year partial interaction slope;
7. positive-year counts;
8. 1.0-pip stress performance;
9. support;
10. deterministic pair/direction/polarity identity.

Selected-tail event sets with Jaccard similarity >= 0.95 are near-duplicates and
the higher frozen rank is retained.

Because EXP-065 expands the hypothesis count relative to EXP-064, the carry-forward
caps are tightened:

- shortlist maximum: 3 per cell/horizon;
- shortlist maximum: 54 globally;
- frozen retrospective hypotheses: 1 per cell/horizon;
- frozen retrospective hypotheses: 18 globally.

Frozen still means retrospective candidate evidence only. It does not mean
validated, promoted, or executable.

## Evidence semantics

All EXP-065 design evidence remains:

`RETROSPECTIVE_ALREADY_SEEN`

with:

`untouched_oos = false`.

The protocol output kind is:

`RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED`.

2015-2022 may not be described as fresh validation.

## Reserved robustness

The reserved block remains closed:

2023-01-01 through 2026-08-20.

DEC-460 authorizes no access to that block.

## Authority

DEC-460 keeps false:

- source access through a historical runtime;
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

## Frozen source

Protocol source:

`src/fmp/discovery/exp065_pairwise_interaction_protocol.py`

blob:

`5ed8b86207076264096d5e6ac5aaf25472172407`.

Focused tests:

`tests/test_phase8a_exp065_pairwise_interaction_protocol.py`

blob:

`b50d3f62d5ee25e260403bc323317cf84a4b4d01`.

## Next gate

The next gate is:

`SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_MINER`.

That miner must implement this exact frozen protocol deterministically, remain
restricted to 2015-2022 already-seen data, and stay execution-locked until a later
separate evidence/runtime authorization chain.
