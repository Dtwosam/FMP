# Phase 8A Annual Pattern Catalogue Dormant Workflow Source

**Decision:** DEC-478  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY DORMANT WORKFLOW / NOT INSTALLED  
**Source annual-freeze contract:** DEC-477 head `df3de17a5363c1df0610faa2db9ec72b554fb9bd`

## Purpose

DEC-478 freezes the dormant GitHub Actions source for the future one-year-at-a-time
annual catalogue workflow without installing it under `.github/workflows`.

It binds the DEC-476 run shape and DEC-477 annual freeze contract to the already
accepted EXP-044 feature/outcome artifacts.

The workflow source remains disabled at:

`docs/superpowers/templates/phase8a-annual-pattern-catalogue.yml.disabled`

The reserved active path is:

`.github/workflows/phase8a-annual-pattern-catalogue.yml`

That active path must not exist under DEC-478.

## Exact annual input

The workflow accepts one explicit `annual_segment_label` choice only.

The available values are exactly the 12 DEC-469 segments:

- 2015 through 2025;
- `2026_YTD_TO_2026_08_20`.

The CLI validates the same set independently so direct CLI use cannot bypass the
workflow choice constraint.

## Sequential annual dependency

The workflow also accepts an optional `previous_annual_freeze_run_id`.

For `2015`, that input must be empty because there is no predecessor segment.

For every later segment, the input is mandatory and must identify the immediately
preceding successful annual-catalogue run:

- 2016 requires a validated 2015 freeze;
- 2017 requires a validated 2016 freeze;
- ...
- `2026_YTD_TO_2026_08_20` requires a validated 2025 freeze.

After the separately locked execution gate passes, the preflight fetches that prior
run metadata and its exact annual-freeze artifact, verifies the artifact ZIP digest,
validates the embedded DEC-477 freeze evidence, requires the prior run to be a
successful `workflow_dispatch` on `main`, and requires the freeze `code_commit`
to equal the prior run head SHA.

The Python source independently freezes the same predecessor mapping, so neither a
manual dispatch input nor direct CLI use can skip a year or substitute a non-adjacent
annual freeze.

## Source reuse

DEC-478 reuses the exact accepted EXP-044 source snapshots already bound by the
earlier discovery source contracts:

- feature run 35867307338;
- outcome run 35876715434;
- exact feature/outcome evidence artifacts;
- exact nine pair/timeframe feature artifacts;
- exact nine pair/timeframe outcome artifacts.

No new market data, new feature materialization, or new outcome materialization is
introduced.

## Dormant workflow shape

For one requested annual segment the disabled template contains exactly:

- one preflight job;
- 18 cell jobs = 3 symbols × 3 timeframes × 2 horizons;
- one annual freeze job.

That is 20 jobs and 20 planned artifacts.

Each cell writes both:

- `cell-evidence.json`;
- `catalogue-payload.json`.

The annual freeze job downloads exactly the same-segment cell artifact pattern and
compiles one `annual-freeze.json` through DEC-477.

There is no full-collection aggregate job and no cross-year comparison job.

## Gate ordering

The preflight job validates exact accepted source metadata and then calls the
separately locked execution gate.

Only after that gate may a post-2015 run download and validate the immediately prior
annual-freeze artifact. The annual cell matrix depends on the complete preflight, so
no cell can start until the prior-year dependency passes.

Each cell then rechecks the execution gate before any accepted EXP-044 artifact ZIP
is downloaded.

The annual freeze job rechecks the gate before opening any historical cell-result
artifact.

All relevant execution constants remain false, so the source cannot currently read
historical artifact bytes or produce catalogue results.

## Installation boundary

DEC-478 creates only:

- the source contract module;
- a dormant CLI source;
- the disabled workflow template;
- focused tests;
- documentation.

It does not create the reserved active workflow path.

Template installation, workflow installation, workflow dispatch, historical reads,
catalogue execution, and historical result production all remain unauthorized.

## Authority

The following remain false:

- workflow template installation;
- workflow installed;
- workflow dispatch;
- historical artifact reads;
- historical annual catalogue execution;
- historical result production;
- next-segment execution;
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

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_CONTRACT`

That gate may define the exact repository mutation required to copy the frozen
disabled template to the reserved active workflow path, but must still keep dispatch
and historical execution unauthorized.
