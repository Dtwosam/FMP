# Phase 8A Annual Pattern Catalogue Full-History Loader

**Decision:** DEC-473  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY LOADER / HISTORICAL EXECUTION LOCKED  
**Source evidence contract:** DEC-472 head `43e5acb986bd963572defa7fd422fb828231dd75`

## Purpose

DEC-473 defines the verified loading boundary between the already accepted EXP-044
full-history feature/outcome artifacts and the DEC-470/471 annual catalogue.

It does not acquire new market data, materialize new features or outcomes, execute
the annual miner, produce catalogue results, compare years, or synthesize Strategy
V1.

## Reused historical materialization

The loader reuses the accepted EXP-044 materialized universe exactly:

- collection start: 2015-01-01;
- collection end: 2026-08-20 inclusive;
- feature set: `fmp-market-feature-v1`;
- accepted EXP-044 outcome set;
- existing processed-source manifests;
- existing feature manifests and aggregate feature evidence;
- existing outcome manifests and aggregate outcome evidence.

No new source, symbol, timeframe, horizon, feature family, or alternative dataset
is introduced.

The accepted range contains exactly 140 monthly partitions from 2015-01 through
2026-08.

## Annual isolation

The loader exposes one annual catalogue segment at a time.

The frozen segment universe is exactly:

- 2015 through 2025 as eleven complete calendar years;
- `2026_YTD_TO_2026_08_20` as the final partial segment.

For a requested segment, only monthly partitions intersecting that segment may be
selected. Feature rows must have `available_at_utc` inside the segment.

Outcome rows must satisfy both:

- signal availability is inside the annual segment; and
- the fixed-horizon exit timestamp is strictly before the segment end.

This duplicates the DEC-471 annual-boundary protection at the artifact-loading
layer so an outcome crossing into the following year cannot enter that year's
catalogue input.

## Artifact verification

Every selected partition must be present in its accepted manifest and is checked
before use for:

- path identity and root containment;
- byte size;
- SHA-256;
- exact schema;
- manifest row count.

The feature and outcome manifests are checked against their aggregate EXP-044
evidence cells. The loader also checks:

- EXP-044 experiment identity;
- feature/outcome set identities;
- evidence label;
- evidence fingerprints recomputed from canonical JSON;
- complete-evidence flags;
- processed-source identity;
- outcome-to-feature-manifest binding;
- outcome-evidence-to-feature-evidence binding;
- existing no-model/no-promotion/no-trading locks.

## Returned source bundle

A successful segment load returns only verified source frames and identities:

- annual segment label;
- symbol and timeframe;
- segment-scoped feature frame;
- segment-scoped outcome frame;
- processed manifest SHA;
- feature manifest SHA;
- outcome manifest SHA;
- feature evidence fingerprint;
- outcome evidence fingerprint;
- exact selected feature artifact paths;
- exact selected outcome artifact paths.

It does not call DEC-471 and cannot create DEC-472 cell or aggregate evidence.

## Authority

DEC-473 adds source code for the verified loading path but does not authorize the
path to be executed against historical artifacts yet.

The following remain false:

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

New data acquisition, feature materialization, and outcome materialization also
remain false.

## Next gate

`ANNUAL_PATTERN_CATALOGUE_FULL_HISTORY_LOADER_EXECUTION_AUTHORIZATION`

That later gate may authorize a bounded read/execution path only after DEC-473 is
merged and its exact source/tests are frozen. It must not silently authorize
cross-year results, Strategy V1 synthesis, or trading.
