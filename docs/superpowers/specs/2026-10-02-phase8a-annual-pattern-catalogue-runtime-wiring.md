# Phase 8A Annual Pattern Catalogue Locked Runtime Wiring

**Decision:** DEC-475  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY LOCKED RUNTIME / HISTORICAL EXECUTION LOCKED  
**Source adapter:** DEC-474 merge `d88d5bb2f5d1f76278c4d588136bbcc5e65731a7`

## Purpose

DEC-475 composes the already frozen annual-catalogue source layers into one callable
cell path while keeping the first operation a hard authorization gate.

The intended call order is exactly:

`authorization gate -> DEC-473 verified loader -> DEC-474 adapter -> DEC-471 miner -> DEC-472 cell evidence compiler`.

This layer installs no GitHub Actions workflow, no dispatch surface, and no
historical result-writing path.

## Unit of work

The runtime unit is one:

`annual segment × symbol × timeframe × horizon`.

The frozen universe remains the DEC-470 universe: 12 annual segments, three symbols,
three timeframes, and two horizons, for exactly 216 annual cells.

## Hard gate

`run_locked_annual_catalogue_cell` must call
`require_historical_catalogue_execution_authorized` before any filesystem-backed
historical loader can run.

The gate requires all three authorities before a cell can proceed:

- historical artifact read;
- historical catalogue execution;
- historical result production.

All three are false in DEC-475. Therefore calling the runtime now raises before
DEC-473 can read an evidence index, manifest, or Parquet partition.

## Source flow after a future separate authorization

Only if a later explicit decision changes the relevant authorities may the locked
cell path:

1. load one verified DEC-473 annual-segment bundle;
2. adapt it through DEC-474 while retaining source/evidence identity;
3. mine exactly one DEC-471 annual cell at the requested horizon;
4. compile the full DEC-472 cell evidence and catalogue payload bytes.

The runtime does not aggregate cells or compare patterns across years.

## Authority

DEC-475 keeps false:

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

It also records:

- workflow installed: false;
- workflow dispatch authorized: false.

## Next gate

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_PLAN`

That next source-only gate may specify how the exact 216 cells would be partitioned,
gated, persisted, and aggregated, but it must not install or dispatch a workflow or
open historical execution.
