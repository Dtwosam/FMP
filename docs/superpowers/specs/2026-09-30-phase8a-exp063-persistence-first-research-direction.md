# Phase 8A — Post-EXP-062 Persistence-First Research Direction

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY RESEARCH-DIRECTION DECISION / SUCCESSOR EXECUTION LOCKED  
**Decision:** DEC-443  
**Successor experiment:** EXP-20260930-063  
**Predecessor:** DEC-442

## Purpose

DEC-443 selects the next Phase 8A research direction after the immutable EXP-062
result and DEC-442 diagnostic.

It does not authorize historical execution. It opens only source design for a new
successor experiment whose primary objective is to reduce temporal edge decay before
any future reserved-block evaluation.

## Diagnostic basis

DEC-442 establishes that all 11 EXP-062 confirmation-frozen patterns later failed
the frozen 2019-2022 validation gate:

- all 11 have non-positive aggregate validation mean at 0.5-pip cost;
- all 11 have fewer than three positive validation years;
- only one also fails minimum per-year support;
- there is no broad validation sample-size shortage;
- there is no runtime or adapter failure.

DEC-443 therefore does not authorize lower validation thresholds or rescue of the
failed EXP-062 patterns.

## Successor identity

EXP-062 is closed and its historical slot is consumed. Any successor work uses new
identity:

`EXP-20260930-063`

## Research direction

The next protocol must make temporal persistence a first-class selection property,
not a post-hoc rescue criterion.

The protocol design must require:

- persistence-aware selection;
- retrospective year balance;
- protection against one period dominating the selected edge;
- deterministic, predeclared persistence metrics;
- deterministic, predeclared internal chronology.

The exact persistence metric and exact internal chronology are intentionally deferred
to the next source-only protocol decision. DEC-443 does not choose them.

## Bounded universe

DEC-443 retains the existing V1 universe:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m and 240m.

DEC-443 itself authorizes no new feature, symbol, timeframe, horizon, or unbounded
search expansion.

## Chronology and contamination boundary

Because the 2019-2022 outcomes were inspected and directly informed DEC-442/443,
they may no longer be represented as fresh validation for EXP-063.

For successor design purposes, 2015-2022 is labeled:

`ALREADY_SEEN_DESIGN_EVIDENCE`

The 2023-01-01 through 2026-08-20 robustness block remains closed and untouched.
Any future opening of that block requires a later explicit repository decision after
the successor protocol and candidate semantics are frozen.

## Locks preserved

DEC-443 keeps false:

- EXP-062 rerun/retry/replacement;
- threshold relaxation;
- EXP-062 pattern redefinition;
- search-universe expansion;
- reserved robustness access;
- successor execution;
- successor historical result production;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

The next safe gate is a source-only EXP-063 persistence-first protocol that freezes
the exact retrospective chronology, persistence statistic, ranking/gating semantics,
search budget, duplicate handling, and later reserved-block boundary before any
execution source is considered.
