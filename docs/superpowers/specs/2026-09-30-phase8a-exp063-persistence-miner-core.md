# Phase 8A — EXP-063 Deterministic Persistence Miner Core

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY CORE / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-445  
**Experiment:** EXP-20260930-063  
**Predecessor:** DEC-444

## Purpose

DEC-445 implements the deterministic in-memory miner for the frozen DEC-444
persistence-first protocol.

It does not load repository artifacts, request historical source data, dispatch any
workflow, open the reserved 2023-2026 robustness block, compile executable
candidates, or authorize any trading surface.

## Bound sources

DEC-445 binds:

- DEC-444 merge `86d16d06444e56a1c6615f18e2906e8ecdaadbdf`;
- DEC-444 protocol source blob
  `2c781dd2811b66d2d88f008007bf5c8bcf99f14f`;
- predecessor deterministic miner blob
  `495a67699eb5014e52129f0238a2737049fe38e6`.

The new core source is
`src/fmp/discovery/exp063_persistence_miner.py`.

## Reused contracts

DEC-445 reuses the predecessor in-memory feature/outcome/state contracts and pattern
enumeration machinery:

- exact EURUSD/GBPUSD/USDJPY symbols;
- exact 5m/15m/1h timeframes;
- exact 60m/240m horizons;
- exact 20 continuous features plus session state;
- fixed 2015-2017 empirical-tertile calibration;
- one/two-dimension pattern enumeration only;
- exact 2,075-pattern and 4,150 directional-hypothesis per-cell/horizon bounds;
- deterministic state encoding.

The successor identity uses the DEC-444 EXP-063 pattern fingerprint, not the
predecessor EXP-061 identity.

## Design-only scoping

Mining uses only rows whose available timestamps fall in 2015-2022 and whose fixed
horizon exits remain strictly inside the same annual design window.

Rows in 2023-2026 are not merely ignored after scoring; they never enter:

- persistence event sets;
- annual support;
- annual net-pip totals;
- ranking;
- deduplication;
- shortlist;
- frozen output.

Focused tests inject catastrophic 2023-2026 rows and require the complete
in-memory result to remain exactly equal to the baseline result.

## Persistence evaluation

For every enumerated pattern, the core forms its 2015-2022 event set once and then
evaluates LONG and SHORT independently.

Patterns failing DEC-444's support prerequisites are skipped before financial
scoring. Passing directional hypotheses are evaluated with the exact DEC-444
annual-stat and persistence-gate functions.

The persisted metrics include:

- total support;
- minimum yearly support;
- aggregate 0.5-pip mean;
- aggregate 1.0-pip stress mean;
- positive-year count;
- worst annual mean;
- lower-half annual mean;
- each fixed two-year-block mean;
- minimum two-year-block mean.

No metric is redefined by the miner.

## Ranking and deduplication

The exact DEC-444 ranking order is implemented:

1. lower-half annual mean;
2. minimum two-year-block mean;
3. positive-year count;
4. worst annual mean;
5. aggregate 0.5-pip mean;
6. aggregate 1.0-pip mean;
7. total support;
8. pattern depth;
9. EXP-063 fingerprint.

Same-direction event-Jaccard deduplication at 0.90 is retained. At most 10
hypotheses per cell/horizon enter the shortlist, and at most the first 3 enter the
frozen output.

## Output semantics

Every frozen object remains:

`RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED`

No confirmation/validation language is used, because 2015-2022 is already-seen
design evidence.

## Fail-closed behavior

The core rejects:

- duplicate design feature identities;
- duplicate design outcome identities;
- outcome rows with no matching feature row;
- feature/outcome identity drift;
- unsupported symbol/timeframe/horizon/direction;
- persistence ranking-contract drift;
- enumeration beyond the frozen bound.

## Locks preserved

DEC-445 keeps false:

- source-data access;
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

After green merge, the next safe gate is a separate source-only EXP-063
artifact/evidence contract that can describe deterministic cell and aggregate
evidence for this exact core while historical execution remains closed.
