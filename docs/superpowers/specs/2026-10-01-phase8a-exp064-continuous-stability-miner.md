# Phase 8A — EXP-064 Continuous-Stability Miner Core

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY MINER CORE / EXECUTION LOCKED  
**Decision:** DEC-453  
**Experiment:** EXP-20261001-064  
**Predecessor:** DEC-452

## Purpose

DEC-453 implements the deterministic in-memory EXP-064 miner defined by DEC-452.

It does not load repository artifacts, access historical source data, execute a
workflow, open reserved 2023-2026 robustness, compile executable candidates, or
authorize trading.

## Bound sources

DEC-453 binds:

- DEC-452 merge:
  `b44af18b7cc5f3fa67d2f938529151f74d9deceb`;
- DEC-452 protocol blob:
  `c108ea047c7bfb3e588bfbac33993180066c28ad`;
- predecessor observation-model blob:
  `495a67699eb5014e52129f0238a2737049fe38e6`.

Miner source:

`src/fmp/discovery/exp064_continuous_stability_miner.py`

blob:

`b0d799ec1afaf43b0441290c97a9f39c37ecd2fd`.

Focused tests:

`tests/test_phase8a_exp064_continuous_stability_miner.py`

blob:

`da2c7b6dac890aec9f2eca0b19a4b8c946223912`.

## Design-only scoping

The miner explicitly scopes feature calibration and effect estimation to:

2015-01-01 inclusive through 2023-01-01 exclusive.

Rows outside that range are ignored before calibration.

Outcome rows are additionally required to exit before the end of their annual
design window so fixed-horizon outcomes cannot leak across year boundaries.

Duplicate feature or outcome observation identities fail closed.

Every outcome must match a feature row by:

- observation id;
- symbol;
- timeframe;
- available timestamp.

## Rank calibration

For each of the 20 frozen continuous features, the miner calls the DEC-452
`rank_calibration_values` contract over design-only feature rows.

Features that do not meet the frozen 600-row / 20-distinct-value calibration
requirements are inactive for that cell.

No tied/degenerate feature is repaired or substituted.

The returned in-memory result carries deterministic frozen calibration values for
each active feature.

## Frozen hypothesis enumeration

The report always records the frozen DEC-452 search bound:

80 hypotheses per cell/horizon.

For every active feature the miner evaluates:

- LONG / INCREASING;
- LONG / DECREASING;
- SHORT / INCREASING;
- SHORT / DECREASING.

No interactions are generated.

A hypothesis whose annual statistics cannot be formed is unevaluable and cannot
qualify.

## Annual effect calculation

For each hypothesis/year:

- empirical percentile is computed from the frozen full-design calibration;
- the primary effect is DEC-452 polarity-signed rank slope at 0.5-pip cost;
- the deterministic upper/lower quartile tail is selected by polarity;
- selected-tail means are computed at 0.5-pip and 1.0-pip cost.

If a year has fewer than two evaluable rank/outcome pairs, no selected-tail
observations, or zero rank variance, the hypothesis is unevaluable and cannot
qualify.

No missing annual statistic is imputed.

## Qualification

Annual statistics are passed directly to the DEC-452
`continuous_stability_gate_passes` function.

DEC-453 does not duplicate, relax, or reinterpret the frozen gate.

A qualifying hypothesis is materialized with all DEC-452 persistence metrics and
an exact EXP-064 fingerprint.

## Ranking and deduplication

Ranking is exactly the 12-field DEC-452 order and the module fails closed if that
field inventory drifts.

Near-duplicate selected-tail event sets use Jaccard >= 0.95 within the same
cell/horizon/market direction.

The higher frozen rank is retained.

The miner returns:

- up to 5 shortlist hypotheses per cell/horizon;
- the first up to 2 shortlist hypotheses as frozen retrospective hypotheses.

Frozen remains a research label only. It is not validation or an executable
strategy.

## Reserved-row invariance

Focused tests append catastrophic 2023-2026 feature and outcome rows.

The complete in-memory EXP-064 result, including calibration values, report,
shortlist, frozen hypotheses, metrics, fingerprints, and counts, must remain exactly
equal to the baseline result without those rows.

This proves that reserved rows cannot influence the DEC-453 in-memory computation.

## Locks preserved

DEC-453 keeps false:

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

After green merge, the next safe gate is a separate source-only EXP-064
artifact/evidence contract bound to this exact deterministic miner.

Historical execution remains closed.
