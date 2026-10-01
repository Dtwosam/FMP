# Phase 8A — EXP-065 Pairwise Interaction Miner

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY MINER FROZEN / EXECUTION LOCKED  
**Decision:** DEC-462  
**Experiment:** EXP-20261001-065  
**Predecessor:** DEC-461

## Purpose

DEC-462 freezes the deterministic in-memory EXP-065 pairwise-interaction miner
against the repaired DEC-461 protocol.

This decision adds no historical source adapter, workflow, CLI, artifact writer,
dispatch path, or result-production authority.

## Frozen lineage

DEC-462 binds:

- DEC-461 merge:
  `2a8127b505c9b0d9e1adb562bd18a5cafc171df6`;
- repaired EXP-065 protocol blob:
  `b54267d790667659749a96123ad23a491ff50dfa`;
- base feature/outcome observation model blob:
  `495a67699eb5014e52129f0238a2737049fe38e6`.

The superseded DEC-460 protocol blob is not an allowed miner dependency.

## Input contract

The miner accepts only in-memory:

- `FeatureObservation` rows;
- `OutcomeObservation` rows;
- one exact symbol;
- one exact timeframe;
- one exact frozen horizon.

It does not load files, query databases, call networks, read workflow artifacts,
or open historical/reserved sources.

Rows are filtered to 2015-01-01 through 2022-12-31 design availability. Outcomes
must also exit before the end of their calendar year, preserving the exact frozen
horizon without crossing an annual boundary.

Feature/outcome identity mismatches and duplicate observation identities fail
closed.

## Constituent feature calibration

For each of the frozen 20 continuous features, the miner applies the DEC-452
full-design empirical-midrank calibration across the exact 2015-2022 feature
rows.

A feature is active only if the frozen calibration helper accepts it. Missing,
non-finite, insufficient, or low-distinct-value features do not create an
alternate threshold or substitute feature.

The nominal protocol universe remains 20 features regardless of which features are
evaluable in a concrete in-memory input.

## Pair calibration

The miner enumerates all 190 canonical unordered feature pairs from the frozen
feature list.

For a pair to become evaluable:

1. both constituent feature calibrations must exist;
2. every usable row is converted to the two constituent empirical percentiles;
3. the raw interaction is exactly
   `2 * (p_a - 0.5) * (p_b - 0.5)`;
4. the repaired DEC-461 pair-calibration helper must accept the complete
   2015-2022 raw interaction series.

Pairs failing the frozen 600-row / 20-distinct-value calibration contract are
skipped as non-evaluable. They are not repaired, imputed, substituted, or removed
from the nominal hypothesis count.

## Nominal versus evaluable search counts

The report always records:

- nominal hypotheses per cell/horizon: **760**.

This is the frozen 190 pairs × 2 directions × 2 polarities universe.

`evaluable_hypothesis_count` is separate. It counts only exact hypotheses for
which all eight annual statistic rows can be constructed under the frozen
calibration and nonsingular OLS requirements.

This separation prevents data availability from silently redefining the protocol
search space.

## Annual interaction statistics

For each evaluable pair × direction × polarity, the miner constructs all eight
calendar years 2015-2022.

Within each year it computes:

- constituent empirical percentiles;
- pair interaction percentile under the full-design pair calibration;
- 0.5-pip and 1.0-pip direction-specific net outcomes;
- annual main-effect-controlled interaction coefficient from the exact DEC-460/461
  OLS estimator;
- polarity-signed partial interaction coefficient;
- main-effects-only residuals;
- selected interaction-tail raw mean at 0.5 pip;
- selected interaction-tail main-effect residual mean at 0.5 pip;
- selected interaction-tail raw mean at 1.0 pip;
- evaluable and selected-tail support.

Any singular annual OLS design or missing selected tail makes that hypothesis
non-evaluable. There is no regularization, alternate solver, fallback estimator, or
post-result rescue.

## Qualification

The miner delegates qualification to the repaired frozen protocol:

`pairwise_interaction_gate_passes(...)`.

No threshold is reimplemented or relaxed in DEC-462.

Therefore the exact support, 6/8 annual-sign, equal-year, lower-half, every
two-year-block, incrementality, and 1.0-pip stress requirements remain those frozen
by DEC-460 and preserved by DEC-461.

## Deterministic ranking

For qualifying hypotheses, the miner applies the exact frozen DEC-460 ranking
order:

1. lower-half incremental selected-tail residual mean;
2. minimum two-year-block incremental residual mean;
3. lower-half raw selected-tail mean;
4. minimum two-year-block raw selected-tail mean;
5. lower-half signed partial interaction slope;
6. minimum two-year-block signed partial interaction slope;
7. positive incremental-tail years;
8. positive raw-tail years;
9. positive partial-slope years;
10. equal-year 1.0-pip stress mean;
11. total selected-tail support;
12. canonical feature A;
13. canonical feature B;
14. direction;
15. polarity.

Canonical pair identity plus direction and polarity fully determine ties.

## Near-duplicate handling

For every qualifying hypothesis, the miner freezes its exact selected-tail
observation-id set.

Following DEC-460, two ranked hypotheses are near-duplicates when those selected
event sets have Jaccard similarity >= 0.95.

The higher-ranked hypothesis is retained; lower-ranked near-duplicates are removed.

No additional feature-similarity, coefficient-similarity, or discretionary
deduplication rule is introduced.

## Carry-forward caps

After deterministic deduplication:

- maximum shortlist per cell/horizon: 3;
- maximum frozen per cell/horizon: 1.

The global DEC-460 caps remain 54 shortlist and 18 frozen when cell evidence is
later aggregated.

A frozen retrospective hypothesis is still not validated, promoted, executable,
or tradeable.

## Reserve isolation

Any supplied observations in 2023-2026 are excluded before calibration and
evaluation.

The miner therefore cannot use reserved rows for:

- constituent rank calibration;
- pair calibration;
- annual regression;
- tail selection;
- ranking;
- deduplication;
- shortlist/freeze output.

The reserved block remains closed.

## Evidence semantics

The miner output kind remains:

`RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED`.

2015-2022 remains already-seen design evidence and is not untouched OOS.

## Authority

DEC-462 keeps false:

- historical source access;
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

## Frozen source pins

Miner:

`src/fmp/discovery/exp065_pairwise_interaction_miner.py`

blob:

`7dac382838d2b8fcc4df5d02c4949ad65c17635b`.

Focused tests:

`tests/test_phase8a_exp065_pairwise_interaction_miner.py`

blob:

`f97bf2ec31c92e9866eb771ce5f526045e2ed482`.

The focused tests cover:

- exact DEC-461 lineage pins;
- nominal 760-hypothesis reporting;
- deterministic stable incremental pair discovery;
- main-effect incrementality preservation;
- 0.95 Jaccard near-duplicate removal;
- every-two-year-block rejection;
- 2023-2026 reserve isolation;
- duplicate feature/outcome identity failure;
- all execution/downstream authority locks.

## Next gate

The next gate is:

`SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_EVIDENCE_CONTRACT`.

That evidence contract must freeze deterministic cell and aggregate evidence
shapes, fingerprints, lineage, exact nominal/evaluable/qualifying counts,
shortlist/frozen limits, and downstream locks before any historical runtime is
considered.
