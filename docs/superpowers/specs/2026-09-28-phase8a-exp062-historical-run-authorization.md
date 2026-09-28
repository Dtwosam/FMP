# Phase 8A — EXP-062 Historical-Run Source Authorization

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY ONE-SLOT AUTHORIZATION / DISPATCH + EXECUTION LOCKED  
**Decision:** DEC-307  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-306

## Purpose

DEC-307 opens only a source-governance slot for at most one later EXP-062 historical
discovery-result attempt. It does not dispatch the workflow and it does not make the
DEC-299 runtime execution gate pass.

The contract is intentionally separate from dispatch/execution authority.

## Frozen proof excluded from the slot

The authoritative gate proof is workflow run `36358289723`, run #1 / attempt 1, on
`f2c55ac36a1a9ba7596ec0d4559c877a66cda0fb`. DEC-306 freezes its exact runtime
evidence. That proof is excluded from historical-result slot consumption.

With that proof as the only matching manual-main EXP-062 discovery run, DEC-307
classifies the inventory as `EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE`.

## One-attempt rule

The first later matching manual-main EXP-062 discovery run must be workflow run #2 /
attempt 1. It consumes the historical-result slot immediately, including while queued or
running and regardless of its eventual terminal outcome.

A second historical attempt, workflow run number drift, GitHub rerun
(`run_attempt != 1`), or proof identity drift fails closed.

## Source binding

DEC-307 pins the exact DEC-306 runtime proof freeze, DEC-305 reviewed proof freeze,
DEC-304 reviewer, DEC-301 proof contract, DEC-300 install, DEC-299 workflow source,
DEC-298 run contract, DEC-293 repaired adapter, unchanged discovery protocol/miner/
loader, active workflow, CLI, and pinned runtime requirements.

It also requires every earlier execution/dispatch/result/rerun/retry/replacement and
downstream trading authority to remain false.

## Research boundary

The future historical slot remains restricted to the unchanged research data window:

- historical research data: 2015-01-01 through 2023-01-01 exclusive;
- reserved robustness block: 2023-01-01 through 2026-08-21 exclusive and CLOSED;
- expected discovery cells: 18;
- candidate compilation/promotion: locked;
- Phase 8B and demo/live trading: locked.

## What DEC-307 authorizes

Only `historical_result_slot_source_authorized=true`.

Historical-result dispatch, historical discovery execution, discovery-result
production, rerun, retry, replacement, reserved-data access, candidate compilation,
promotion, Phase 8B, demo, broker mutation, live orders, real-money action, and trading
all remain false.

The next safe gate is a clean-main read-only operator that may expose the single
historical dispatch command only while the exact DEC-307 inventory remains available.
