# Phase 8A — EXP-063 Artifact / Evidence Contract

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY EVIDENCE CONTRACT / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-446  
**Experiment:** EXP-20260930-063  
**Predecessor:** DEC-445

## Purpose

DEC-446 freezes deterministic cell and aggregate evidence formats for the
DEC-444/445 EXP-063 persistence-first protocol and miner core.

It does not load source artifacts, execute historical research, open the reserved
2023-2026 block, compile executable candidates, or authorize promotion or trading.

## Bound sources

DEC-446 binds:

- DEC-445 merge `f13988c78470ae00e3c3b9944a774bf2fed42f59`;
- DEC-445 miner source blob
  `40c49a372b35dbc113dbfb71374b1ae5fc7acc45`;
- DEC-444 protocol source blob
  `2c781dd2811b66d2d88f008007bf5c8bcf99f14f`.

Contract source:

`src/fmp/discovery/exp063_evidence_contract.py`

## Canonical evidence

Cell and aggregate evidence use deterministic canonical JSON:

- lexicographically sorted keys;
- compact separators;
- no NaN / infinity;
- one trailing newline;
- SHA-256 over the unsigned object.

Compilation is self-validating: a compiled cell or aggregate object is passed
through the same fail-closed validator before it is returned.

Recomputing a fingerprint over semantically invalid data is therefore insufficient
to create valid evidence.

## Cell evidence

Each cell binds:

- EXP-063 experiment identity;
- DEC-444 protocol fingerprint;
- DEC-445 miner identity and source blob;
- exact code commit;
- processed, feature, and outcome manifest SHA-256 values;
- feature and outcome evidence fingerprints;
- exact symbol / timeframe / horizon identity;
- frozen state-model cutpoints;
- active feature inventory;
- enumerated and directional search counts;
- qualifying and deduplicated counts;
- complete persistence shortlist;
- exact first-three frozen fingerprint inventory;
- output kind;
- all downstream authority locks.

Every shortlist row stores:

- exact EXP-063 fingerprint;
- direction and predicates;
- eight annual 2015-2022 support / 0.5-pip / 1.0-pip totals;
- total and minimum annual support;
- aggregate 0.5-pip and 1.0-pip means;
- positive-year count;
- worst annual mean;
- lower-half annual mean;
- four fixed two-year-block means;
- minimum two-year-block mean.

The validator rebuilds each `AnnualPersistenceStat`, re-runs the exact DEC-444
persistence gate, recomputes all persisted metrics, recomputes the pattern
fingerprint and ranking key, checks rank order, and verifies the frozen inventory is
exactly the first up-to-three shortlist fingerprints.

## Aggregate evidence

Aggregate evidence requires exactly the 18 frozen cells:

EURUSD / GBPUSD / USDJPY × 5m / 15m / 1h × 60m / 240m.

For every cell, the aggregate compiler first validates full cell semantics.

The aggregate then enforces:

- exact code-commit equality across all cells;
- exact Phase 2 processed source manifest for each symbol;
- identical feature/outcome manifest pair across the two horizons of a given
  symbol/timeframe;
- one singular feature evidence fingerprint;
- one singular outcome evidence fingerprint;
- unique cell evidence fingerprints;
- deterministic sorted cell order;
- global shortlist <= 180;
- global frozen hypotheses <= 54;
- every frozen fingerprint list equals the first up-to-three shortlist identities.

The aggregate stores no validation-accepted count because EXP-063 uses already-seen
2015-2022 design evidence only. Its frozen output remains:

`RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED`

## Contamination boundary

All evidence is explicitly labeled:

`RETROSPECTIVE_ALREADY_SEEN`

and:

`untouched_oos = false`

The contract requires:

`reserved_robustness_opened = false`

Nothing in DEC-446 reads, validates, or exposes 2023-2026 outcomes.

## Locks preserved

Cell and aggregate evidence require false for:

- source-data access;
- historical execution;
- historical result authorization;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Tests

Focused tests verify:

- deterministic cell evidence;
- semantic validation after re-fingerprinting;
- frozen-inventory tamper rejection;
- exact 18-cell aggregation;
- duplicate / missing cell rejection;
- cross-horizon manifest drift rejection;
- authority-tamper rejection.

## Next gate

After green merge, the next safe gate is a separate source-only EXP-063
workflow / CLI / runtime source freeze. That future decision may describe how the
frozen miner and evidence contract would be wired for historical execution, but
execution, dispatch, and any historical slot remain closed until separately
authorized.
