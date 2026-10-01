# Phase 8A — EXP-064 Continuous-Stability Research Direction

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY SUCCESSOR DIRECTION OPEN  
**Decision:** DEC-451  
**Successor:** EXP-20261001-064  
**Source result:** DEC-450 / EXP-20260930-063

## Purpose

DEC-451 defines the next research direction after the frozen negative EXP-063 result.

It does not rerun EXP-063, relax its thresholds, redefine its patterns, open the
reserved 2023-2026 block, or authorize any historical execution.

## Source result

DEC-451 binds:

- DEC-450 merge:
  `839af1e85b526c3c2a11b228e4aa8d3865589f06`;
- DEC-450 result-review source blob:
  `b572dbf4801c211b72285049654ebf4d96744cf1`;
- EXP-063 historical run:
  `36773288493`;
- EXP-063 aggregate evidence fingerprint:
  `d0562d29da38c8ee4c0d3b28c35b3de7c9c42a5157910eef319a91b67ca4be42`.

The frozen EXP-063 result was:

- 37,350 patterns;
- 74,700 directional hypotheses;
- 0 qualifying directional hypotheses;
- 0 persistence shortlist;
- 0 frozen hypotheses;
- classification:
  `NO_DIRECTIONAL_HYPOTHESIS_PASSED_FROZEN_PERSISTENCE_GATE`.

## Research interpretation

The combination of EXP-062 and EXP-063 does not support continuing the same
LOW/MID/HIGH one/two-predicate atomic-state hypothesis family.

EXP-062 produced confirmation survivors that did not persist through its already-seen
2019-2022 validation block. EXP-063 then imposed persistence-first selection over
2015-2022 and produced zero qualifying hypotheses.

DEC-451 therefore closes that hypothesis family rather than weakening the
persistence requirements to obtain survivors.

This is a structural pivot, not a rescue operation.

## Successor identity

The new source-only successor is:

`EXP-20261001-064`

Its primary question is whether simple continuous or rank-based effects from the
same already-approved leakage-safe feature set can exhibit stable sign and economic
effect across the already-seen annual history without relying on tertile atomic
state enumeration.

## Closed research family

DEC-451 closes for successor research:

- empirical-tertile LOW/MID/HIGH atomic states as the primary hypothesis unit;
- the EXP-061/063 one-predicate and two-predicate state enumeration family;
- result-driven relaxation of DEC-444 thresholds;
- rescue, reranking, or reinterpretation of failed EXP-063 patterns.

EXP-063 remains immutable.

## Bounded successor universe

DEC-451 keeps the same:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60 and 240 minutes;
- 20 leakage-safe continuous feature columns;
- fixed historical transaction-cost conventions to be bound by the successor
  protocol.

DEC-451 does not authorize:

- new raw features;
- new symbols;
- new timeframes;
- new horizons;
- external alternative data.

## Source design newly permitted

Only source-level protocol design is opened.

The EXP-064 protocol may define deterministic transforms of the existing 20
continuous features, such as normalization or rank representations, and may define
simple continuous-effect or rank-effect hypothesis forms.

The exact following items are deliberately deferred to the next protocol decision:

- normalization or rank method;
- effect estimator;
- sign/economic-effect gate;
- annual-stability gate;
- interaction policy;
- multiplicity/search-volume bound;
- ranking/deduplication method;
- shortlist/freeze caps.

Those choices must be frozen before any execution can be authorized.

## Chronology

2015-01-01 through 2022-12-31 remains:

`ALREADY_SEEN_DESIGN_EVIDENCE`

It may not be described as fresh validation for EXP-064.

The reserved robustness interval remains closed:

2023-01-01 through 2026-08-20.

DEC-451 does not open it.

## Authorizations

DEC-451 sets true only:

- successor protocol source design is open;
- deterministic transforms of existing approved features may be designed;
- continuous/rank-effect source forms may be designed.

It keeps false:

- successor execution;
- successor historical result production;
- EXP-063 rerun;
- EXP-063 retry;
- EXP-063 replacement;
- EXP-063 threshold relaxation;
- EXP-063 pattern redefinition/rescue;
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

Research-direction source:

`src/fmp/discovery/exp064_research_direction.py`

blob:

`6a7de1e93515fd3771e3763641ee6a07e425ee8a`.

Focused tests:

`tests/test_phase8a_exp064_research_direction.py`

blob:

`0f7924c553f49813007e845e7d7b3d26b8832172`.

## Next gate

`SOURCE_ONLY_EXP064_CONTINUOUS_STABILITY_PROTOCOL`

The next decision must freeze the exact EXP-064 estimator, annual stability
requirements, search bound, transaction-cost treatment, ranking, and evidence
semantics before any runtime or historical execution work begins.
