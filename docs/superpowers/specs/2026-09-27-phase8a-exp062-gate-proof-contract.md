# Phase 8A — EXP-062 Gate-Proof Terminal Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY PREDECLARED PROOF REVIEW / NO PROOF DISPATCH  
**Decision:** DEC-301  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-300

## Purpose

DEC-301 predeclares the exact fail-closed terminal shape for the first proof-only manual-main run of the installed EXP-062 workflow.

The proof is not a historical discovery result and must not consume a historical-result slot.

## Required proof run identity

A valid proof run must be:

- workflow `phase8a-exp062-discovery`;
- path `.github/workflows/phase8a-exp062-discovery.yml`;
- event `workflow_dispatch`;
- branch `main`;
- exact proof head;
- workflow run number `1`;
- attempt `1`;
- terminal `completed`;
- conclusion `failure`.

## Required fail-closed behavior

Preflight must:

- validate the exact accepted EXP-044 source inventory;
- validate the exact DEC-299 workflow source/dependency stack;
- emit source-ready evidence;
- then fail at the still-locked DEC-299 historical execution gate.

Any downstream materialized job must be `skipped`.

DEC-301 explicitly supports GitHub's known early-failure API behavior where the cell matrix appears as one literal skipped template job:

`exp062-cell-${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-${{ matrix.dataset.horizon }}m`

That placeholder may not coexist with expanded cell jobs.

## Artifact shape

Exactly one non-expired artifact is allowed:

`phase8a-exp062-preflight-<proof-head>`

No cell or aggregate artifact may exist.

## Slot and authorization state

A valid proof records:

- historical-result slot consumed: false;
- historical discovery execution occurred: false;
- cell-result artifact count: 0;
- aggregate-result artifact count: 0.

All remain false:

- proof dispatch;
- historical-result dispatch;
- historical discovery execution;
- discovery-result production;
- rerun/retry/replacement;
- reserved 2023-2026 access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo/broker/live/real-money/trading.

## Frozen implementation

Proof contract:

`src/fmp/discovery/exp062_proof_contract.py`

Git blob:

`dcc513d1918e95e2bc0bc02a04774291c6b340c0`

Focused tests:

`tests/test_phase8a_exp062_gate_proof_contract.py`

Git blob:

`7022c0a821144c63daf2a74c4aca6871c384dd27`

## Next gate

After DEC-301 merges green, the next safe layer is a read-only proof operator that:

- requires exact current main;
- verifies zero existing EXP-062 manual-main runs;
- exposes one future proof dispatch command as evidence only;
- has no execute mode.

Proof dispatch remains separately locked until a later one-shot proof executor decision.
