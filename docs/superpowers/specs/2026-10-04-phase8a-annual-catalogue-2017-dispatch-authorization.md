# Phase 8A — 2017 Dispatch Authorization

**Date:** 2026-10-04  
**Status:** SOURCE-DESIGN ONLY / PENDING CONCRETE DEC-540 EVIDENCE  
**Decision:** DEC-541

## Purpose

DEC-541 may authorize only the source contract for one fresh annual-catalogue
dispatch: annual segment `2017`, global workflow run `379`, attempt `1`,
with concrete predecessor annual freeze run `37206992367`.

DEC-541 must not exist as a live authorization until DEC-540 has landed on
`main`, its repository-hosted read-only workflow has completed successfully,
and its exact workflow run, head SHA, artifact ID, artifact digest, and
preflight fingerprint are bound into the implementation.

## Required DEC-540 source state

The eventual implementation must pin:

- DEC-540 source blob
  `0e048756a1a9ca5f8d45896c6ff212d386996ed0`;
- active annual workflow blob
  `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`;
- installed 2017 runtime gate blob
  `c1853eeec55ee98b3155a6054f07cf360793ba9b`;
- installed annual runtime blob
  `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`;
- concrete DEC-540 workflow run ID and attempt;
- concrete DEC-540 workflow head SHA;
- concrete DEC-540 artifact ID and SHA-256 digest;
- concrete DEC-540 preflight fingerprint.

The DEC-540 value must remain read-only and must freeze:

- annual segment `2017`;
- previous annual freeze run ID `37206992367`;
- expected run number `379`;
- expected run attempt `1`;
- runtime authorization installed = true;
- runtime gate active = true;
- dispatch command present = false;
- annual workflow dispatch authorized = false;
- historical read/execution/result authority = false.

## DEC-541 authorization boundary

After all concrete DEC-540 checks succeed, DEC-541 may set only:

- `annual_workflow_dispatch_authorized = true`;
- `historical_artifact_read_authorized = true`;
- `historical_catalogue_execution_authorized = true`;
- `historical_result_production_authorized = true`;
- `authorization_contract_validated = true`;
- `source_only_authorization = true`.

DEC-541 must keep all action surfaces closed:

- `dispatch_command_present = false`;
- `dispatch_action_executed = false`;
- `rerun_authorized = false`;
- `retry_authorized = false`;
- `replacement_run_authorized = false`;
- `run_380_or_later_authorized = false`;
- `next_segment_execution_authorized = false`;
- `cross_year_result_production_authorized = false`;
- `strategy_v1_synthesis_authorized = false`;
- `promotion_authorized = false`;
- `phase8b_authorized = false`;
- `demo_order_authorized = false`;
- `broker_mutation_authorized = false`;
- `live_order_authorized = false`;
- `real_money_authorized = false`;
- `trading_authorized = false`.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_DISPATCH_ACTION_PREFLIGHT`

DEC-541 itself must contain no `gh workflow run`, rerun, repository mutation,
broker, order, real-money, or trading command.
