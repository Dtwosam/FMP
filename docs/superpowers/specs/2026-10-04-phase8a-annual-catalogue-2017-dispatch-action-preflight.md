# Phase 8A — 2017 Dispatch Action Preflight

**Date:** 2026-10-04  
**Status:** SOURCE-DESIGN ONLY / PENDING CONCRETE DEC-541  
**Decision:** DEC-542

## Purpose

DEC-542 is the final read-only gate before any 2017 annual-catalogue dispatch.
It may freeze the exact dispatch parameters only after a concrete DEC-541
source-only authorization has been produced and bound.

It must never submit a workflow, mutate the repository, rerun a prior run, or
claim a result.

## Required authorization

The eventual implementation must require a concrete DEC-541 value with:

- annual segment `2017`;
- prior segment `2016`;
- previous annual freeze run ID `37206992367`;
- expected run number `379`;
- expected run attempt `1`;
- runtime authorization installed = true;
- runtime gate active = true;
- authorization contract validated = true;
- annual workflow dispatch authorized = true;
- historical artifact read authorized = true;
- historical catalogue execution authorized = true;
- historical result production authorized = true;
- source-only authorization = true;
- dispatch command present = false;
- dispatch action executed = false.

DEC-542 must also re-read current `main` and the annual workflow inventory.
The inventory must remain exactly:

- run 1 / attempt 1: failure;
- run 376 / attempt 1: failure;
- run 377 / attempt 1: success;
- run 378 / attempt 1: success;
- no run 379 or later.

## Frozen dispatch parameters

Only these future action parameters may be frozen:

- ref: `main`;
- `annual_segment_label=2017`;
- `previous_annual_freeze_run_id=37206992367`;
- expected global run number: `379`;
- expected attempt: `1`.

The resulting preflight must record:

- `dispatch_parameters_frozen = true`;
- `preflight_read_only = true`;
- `dispatch_command_present = false`;
- `dispatch_action_executed = false`.

## Locked authority

DEC-542 must keep all unrelated/later authority false:

- rerun/retry/replacement;
- run 380 or later;
- 2018+ / next-segment execution;
- cross-year result production;
- Strategy V1 synthesis;
- promotion / Phase 8B;
- demo/live orders;
- broker mutation;
- real-money action;
- trading.

## Next gate

`EXACT_2017_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`

The exact dispatcher must be a separate, provenance-bound action installed only
after concrete DEC-542 evidence exists.
