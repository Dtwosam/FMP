# Phase 8A Annual Pattern Catalogue Workflow Plan

**Decision:** DEC-476  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY WORKFLOW PLAN / NO WORKFLOW INSTALLED  
**Source runtime:** DEC-475 head `0cf867d3e5f794e647e763d8f9e64bf150eab2c4`

## Purpose

DEC-476 freezes the future execution shape before any annual-catalogue workflow is
installed or dispatched.

The plan preserves the governing DEC-469 method: each historical annual segment is
processed and frozen independently before the next segment can become authoritative,
and cross-year comparison cannot begin until all required annual freezes exist.

This decision does not install a GitHub Actions workflow, read historical artifacts,
run DEC-475, produce catalogue results, compare years, or synthesize Strategy V1.

## Run unit

A future run may cover exactly one annual segment.

Each segment run contains exactly:

- one preflight job;
- 18 annual cell jobs = 3 symbols × 3 timeframes × 2 horizons;
- one annual-segment freeze job;
- 20 jobs total;
- 20 planned artifacts total.

The annual freeze job depends on all 18 cell jobs for that same segment.

A single workflow that mines all 216 annual cells in one execution is explicitly
forbidden by this plan because it would weaken the year-by-year freeze boundary.

## Required segment sequence

The exact ordered segment universe is:

1. 2015
2. 2016
3. 2017
4. 2018
5. 2019
6. 2020
7. 2021
8. 2022
9. 2023
10. 2024
11. 2025
12. `2026_YTD_TO_2026_08_20`

The full collection is still exactly 216 cells, but operationally it is represented
as 12 separately frozen 18-cell annual runs.

A later segment cannot become authoritative until the prior segment's freeze is
complete and accepted.

## Cell shape

Within a segment, the cell universe is deterministic and complete:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m, 240m.

Every segment therefore contains the same 18 cell identities.

No annual winner selection, ranking, deduplication, cross-year comparison, or
Strategy V1 synthesis occurs inside a segment run.

## Annual freeze dependency

DEC-476 deliberately stops before defining the annual freeze payload itself.

The next source-only contract must define how all 18 validated DEC-472 cell
evidence objects for one segment are bundled, fingerprinted, and frozen so that:

- no cell is missing or duplicated;
- every cell belongs to the same annual segment;
- all source/code/protocol identities are bound;
- all 4,970 records per cell have already passed DEC-472 semantic validation;
- the annual freeze can be accepted before the next segment;
- cross-year comparison cannot substitute for or bypass an annual freeze.

## Authority

DEC-476 keeps all of the following false:

- workflow source authorization;
- workflow installation;
- workflow dispatch;
- historical artifact reads;
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

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_SEGMENT_FREEZE_CONTRACT`
