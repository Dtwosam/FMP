# Phase 8A — EXP-063 Persistence-First Pattern Protocol

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY PROTOCOL / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-444  
**Experiment:** EXP-20260930-063  
**Predecessor:** DEC-443

## Purpose

DEC-444 freezes the exact source-only protocol for the persistence-first successor
selected by DEC-443.

EXP-063 does not rescue or rerun EXP-062. It retains the same bounded market-state
search universe while changing selection so temporal persistence is evaluated across
all already-seen 2015-2022 design years before any reserved robustness data may be
opened.

## Bound predecessors

DEC-444 binds:

- DEC-443 merge `2ff960cf51d614c8c446d5f7f4c85569312bfec8`;
- DEC-443 direction source blob
  `e32fe0da11e01e463a8c5110201b0b1ed223f85e`;
- base EXP-061/062 pattern protocol blob
  `63b3f0121d6a50eb9e8e62ab666d70eb91791621`.

## Bounded search universe

EXP-063 preserves:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m and 240m;
- the same 20 leakage-safe continuous features;
- the same five mutually exclusive session states;
- LOW/MID/HIGH empirical-tertile states;
- one- or two-dimension patterns only;
- LONG and SHORT hypotheses;
- 65 maximum atomic states;
- 2,075 admissible patterns per cell/horizon;
- 4,150 directional hypotheses per cell/horizon;
- 74,700 directional hypotheses globally.

No new feature, symbol, timeframe, horizon, third predicate, or result-driven search
expansion is authorized.

## State calibration

Feature-state cutpoints remain calibrated from 2015-01-01 through 2017-12-31 only,
using the exact empirical-tertile method inherited from the predecessor protocol.

Those fixed cutpoints are then applied through 2022. Tied cutpoints still skip the
affected dimension for that symbol/timeframe rather than being repaired.

## Retrospective chronology

The eight design years are exactly 2015 through 2022. Each year is treated as an
equal-status persistence slice and is labeled already-seen design evidence.

The four fixed two-year persistence blocks are:

- 2015-2016;
- 2017-2018;
- 2019-2020;
- 2021-2022.

2019-2022 may not be called fresh validation because its outcomes already informed
DEC-442 and DEC-443.

The 2023-01-01 through 2026-08-20 reserved robustness block remains closed. Outcomes
crossing a year or reserved-block boundary are purged.

## Annual evidence contract

For each directional pattern, each design year records:

- support;
- total net pips at 0.5-pip cost;
- total net pips at 1.0-pip stress cost.

Annual support must be a non-negative integer. Annual net-pip totals must be finite.

Exactly one annual record is required for every year 2015-2022.

## Persistence metrics

The protocol deterministically computes:

- total support;
- minimum annual support;
- event-weighted aggregate mean net pips at 0.5 pip;
- event-weighted aggregate mean net pips at 1.0 pip;
- count of positive 0.5-pip annual means;
- worst annual 0.5-pip mean;
- **lower-half annual mean**: arithmetic mean of the four weakest annual 0.5-pip
  means, giving years equal status;
- equal-year arithmetic mean for each fixed two-year block;
- minimum of the four two-year-block means.

The lower-half metric and block metrics prevent one unusually strong period from
dominating selection.

## Persistence gate

A pattern passes only when all conditions hold:

- total support >= 600;
- support in every design year >= 75;
- aggregate 0.5-pip mean net pips >= 0.25;
- aggregate 1.0-pip stress mean net pips > 0;
- at least 6 of 8 annual 0.5-pip means are positive;
- lower-half annual 0.5-pip mean > 0;
- every fixed two-year block mean > 0.

These support and aggregate-mean requirements do not relax the prior discovery gate.

## Ranking and deduplication

Passing patterns rank by:

1. lower-half annual 0.5-pip mean, descending;
2. minimum two-year-block 0.5-pip mean, descending;
3. positive-year count, descending;
4. worst annual 0.5-pip mean, descending;
5. aggregate 0.5-pip mean, descending;
6. aggregate 1.0-pip mean, descending;
7. total support, descending;
8. pattern depth, ascending;
9. pattern fingerprint, ascending.

Near-duplicate handling remains same-cell/horizon/direction only, with event Jaccard
threshold 0.90 and the higher frozen rank retained.

At most 10 patterns per cell/horizon may remain in the persistence shortlist, for a
global maximum of 180. At most 3 per cell/horizon may be frozen, for a global
maximum of 54.

## Result meaning

A frozen EXP-063 object is:

`RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED`

It is not an executable strategy, not a validated candidate, and not permission to
open the reserved robustness block.

## Locks preserved

DEC-444 keeps false:

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

The next safe gate is a deterministic in-memory EXP-063 miner core implementing
exactly this frozen protocol. That core must remain source-only and must prove that
2023-2026 rows cannot influence any EXP-063 result.
