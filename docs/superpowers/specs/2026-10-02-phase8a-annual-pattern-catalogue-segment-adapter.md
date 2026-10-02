# Phase 8A Annual Pattern Catalogue Segment Adapter

**Decision:** DEC-474  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY ADAPTER / HISTORICAL EXECUTION LOCKED  
**Source loader:** DEC-473 merge `f3fd12018ff9602dbc233b0b5c99bf6764489ea8`

## Purpose

DEC-474 defines the source-only conversion boundary from a verified DEC-473 annual
segment bundle into the exact in-memory observation types consumed by DEC-471.

It exists because the earlier EXP-061 adapter is intentionally range-limited to
2015-2022 and must not be silently reused for the now-authorized 2015-2026 annual
catalogue scope.

DEC-474 does not read historical artifacts, call the annual miner, serialize
catalogue evidence, compare years, or synthesize Strategy V1.

## Input authority

The public adapter accepts only
`VerifiedAnnualCatalogueSegmentFrames` produced by the DEC-473 loader contract.

The adapter preserves:

- annual segment label;
- symbol and timeframe;
- processed-source manifest SHA;
- feature manifest SHA;
- outcome manifest SHA;
- aggregate feature evidence fingerprint;
- aggregate outcome evidence fingerprint;
- exact selected feature artifact paths;
- exact selected outcome artifact paths.

This prevents a raw DataFrame from bypassing the loader's artifact/evidence chain.

## Observation identity

DEC-474 keeps the accepted EXP-044/EXP-061 observation identity projection.

The observation ID is the SHA-256 of canonical JSON containing:

- symbol;
- timeframe;
- bar-start timestamp;
- availability timestamp;
- feature-set version;
- processed-source manifest SHA.

Feature and outcome rows for the same market observation must therefore resolve to
the same observation ID before DEC-471 can consume them.

## Feature conversion

For every feature row DEC-474 requires:

- exact bundle symbol/timeframe;
- accepted feature-set version;
- exact processed-source identity;
- unique symbol/timeframe/bar-start identity;
- UTC bar-start and availability timestamps;
- availability equal to bar start plus the exact timeframe;
- availability inside the requested annual segment;
- all frozen continuous feature columns;
- all frozen session flag columns.

Non-finite continuous feature values are normalized to null before constructing
`FeatureObservation`. This preserves the already accepted DEC-293 behavior and
lets DEC-471 treat unavailable/non-finite values as unavailable rather than as
numeric market states.

## Outcome conversion

For every outcome row DEC-474 requires:

- exact bundle symbol/timeframe;
- accepted feature-set and outcome-set versions;
- retrospective evidence label;
- exact processed-source identity;
- unique symbol/timeframe/bar-start/horizon identity;
- UTC bar-start, availability, and exit timestamps;
- availability equal to bar start plus the exact timeframe;
- availability inside the requested annual segment;
- one of the frozen 60m/240m horizons;
- exit strictly before the annual segment boundary;
- finite base/stress LONG and SHORT net-pip outcomes.

The constructed `OutcomeObservation` additionally enforces that exit timestamp is
exactly availability plus the frozen horizon.

Every adapted outcome observation ID must have a matching adapted feature
observation ID.

## Authority

DEC-474 remains source-only. The following stay false:

- historical artifact read authorization;
- historical annual catalogue execution;
- historical result production;
- cross-year result production;
- Strategy V1 synthesis;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_RUNTIME_WIRING`

That gate may wire DEC-473 loader -> DEC-474 adapter -> DEC-471 miner -> DEC-472
evidence compiler in a locked callable path, but it must still add no historical
artifact-read or execution authorization.
