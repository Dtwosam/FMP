# Phase 8A — EXP-065 Pairwise Interaction Research Direction

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY SUCCESSOR DIRECTION OPEN  
**Decision:** DEC-459  
**Experiment:** EXP-20261001-065  
**Predecessor:** DEC-458

## Purpose

DEC-459 opens a new source-only research direction after the frozen EXP-064
negative result.

EXP-063 showed that the frozen LOW/MID/HIGH one/two-predicate atomic-state family
produced zero persistence qualifiers. EXP-064 then tested all 1,440 frozen
single-feature continuous/rank hypotheses under the DEC-452 annual-stability and
cost-stress gate and produced zero qualifiers.

DEC-459 therefore changes the hypothesis representation again. It does not relax,
reinterpret, or rerun either predecessor experiment.

## Frozen source result

DEC-459 binds:

- DEC-458 merge:
  `e3c2a7a1dbb6592a8438f3949ffa83177e31f4e6`;
- DEC-458 result-review source:
  `src/fmp/discovery/exp064_historical_result_review.py`;
- DEC-458 result-review source blob:
  `c5878685950e14a632b4eb8d2616d9540afb12d2`;
- EXP-064 historical run:
  `36853290904`;
- EXP-064 aggregate evidence fingerprint:
  `832e8c814ac578b614764d37cba15e64569e2f841dfa6f72f2c9cd9a8fdbcbb1`.

The frozen source result is:

- hypotheses: `1,440`;
- evaluable hypotheses: `1,440`;
- qualifying hypotheses: `0`;
- deduplicated hypotheses: `0`;
- continuous-stability shortlist: `0`;
- frozen hypotheses: `0`;
- classification:
  `NO_CONTINUOUS_STABILITY_HYPOTHESIS_PASSED_FROZEN_GATE`.

## Successor identity

The new experiment identity is:

`EXP-20261001-065`.

Its research question is whether tightly bounded, exactly-two-feature interactions
from the same leakage-safe feature set can exhibit stable economic effects across
already-seen years where single-feature effects did not.

## Prior families remain closed

DEC-459 keeps closed:

- the EXP-061/063 LOW/MID/HIGH atomic-state family;
- one/two-predicate discrete state rescue;
- EXP-064 single-feature continuous/rank hypotheses;
- EXP-064 threshold relaxation;
- EXP-064 protocol redefinition;
- EXP-064 hypothesis rescue.

No EXP-064 result may be reclassified as a survivor under a later threshold.

## Source-only pairwise direction

DEC-459 permits source-only design of hypotheses containing exactly two distinct
existing continuous features.

It does not yet freeze:

- feature-pair construction;
- interaction transform;
- estimator;
- main-effect control/residualization policy;
- interaction sign/polarity representation;
- search-volume bound;
- annual stability gate;
- cost-stress gate;
- ranking;
- deduplication;
- shortlist/freeze caps.

Those must be declared in the next protocol decision before any execution can be
authorized.

The future protocol must also define an interaction-incrementality requirement so
a pair cannot qualify merely because one constituent feature carries the effect.
The exact incrementality test is deliberately deferred, but it must be deterministic
and frozen before execution.

## Hard complexity ceiling

DEC-459 authorizes at most two features per successor hypothesis.

Three-or-more-feature interactions, trees, arbitrary rule search, AutoML, neural
networks, symbolic search, genetic search, unrestricted expression search, or
post-result feature combination expansion are not authorized.

## Bounded market/data universe

EXP-065 retains exactly:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m and 240m;
- the same 20 leakage-safe continuous features.

DEC-459 authorizes no new:

- raw feature;
- symbol;
- timeframe;
- horizon;
- alternative data;
- data repair path.

## Chronology

2015-01-01 through 2022-12-31 remains:

`ALREADY_SEEN_DESIGN_EVIDENCE`.

It may not be described as fresh validation.

The reserved robustness block remains closed:

2023-01-01 through 2026-08-20.

No DEC-459 authority can read or open it.

## Authority

DEC-459 opens only:

`successor_protocol_source_open_authorized=true`.

It keeps false:

- successor execution;
- successor historical result production;
- EXP-064 rerun;
- EXP-064 retry;
- EXP-064 replacement;
- EXP-064 threshold relaxation;
- EXP-064 protocol redefinition;
- EXP-064 hypothesis rescue;
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

`src/fmp/discovery/exp065_pairwise_interaction_research_direction.py`

blob:

`7d9350f714bfec7cc39ebf76b2e6e313261e9a68`.

Focused tests:

`tests/test_phase8a_exp065_pairwise_interaction_research_direction.py`

blob:

`b177a0aa1244e3f7b7c186dbcf5169b78e76b82a`.

## Next gate

The next gate is:

`SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_PROTOCOL`.

That protocol must freeze the exact two-feature hypothesis representation,
interaction estimator, main-effect/incrementality treatment, bounded search
volume, stability gate, cost stress, ranking/deduplication, and freeze caps before
any historical execution is considered.
