# Phase 8A — EXP-061 Historical Run Authorization Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY ONE-SLOT AUTHORIZATION / DISPATCH + EXECUTION STILL LOCKED  
**Decision:** DEC-281  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-280

## Purpose

DEC-281 freezes the source-only authorization contract for the first and only bounded EXP-061 historical discovery-result attempt.

It does not dispatch the workflow and does not open the existing execution gate.

## Live run inventory at authorization time

Immediately after DEC-280 merged, the exact manual-main EXP-061 workflow history contains one relevant run only:

- run id: `36319888985`;
- workflow: `phase8a-exp061-discovery`;
- path: `.github/workflows/phase8a-exp061-discovery.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head: `041b7b2f5aac8821156fab346df8ab30f4be2a7b`;
- attempt: `1`;
- status: `completed`;
- conclusion: `failure`.

DEC-280 already froze that run as the expected fail-closed proof. DEC-281 therefore excludes exactly that immutable run from the future historical-result slot.

There is no historical discovery-result attempt yet.

## Frozen source stack

DEC-281 binds the exact merged DEC-280 stack:

- DEC-280 merge: `da40f1cf3b45b111bb87099353ec79d5f2b95918`;
- reviewed proof: `src/fmp/discovery/proof_result_decision.py` blob `fbed3788ab0c1c1e00dccfe0f84a293ff04f6ccd`;
- active workflow blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- CLI blob: `bd40f17566f4c03e623215fe9e615b00b2fc9039`;
- runtime requirements blob: `1ff32214dee10d877a067e750cd69ffad96d5fe5`;
- run contract blob: `260eb6930673427266463517546969635188b143`;
- workflow-source blob: `68566fc86ff3470cc8b6ebef606becaff9f3450b`;
- locked-install blob: `e959a782fdbb6bf5b578e60e44f5e015b50086a6`;
- proof-contract blob: `4c0a6f58e5611cfeb14eed15f62893e8956f09a7`;
- pattern protocol blob: `63b3f0121d6a50eb9e8e62ab666d70eb91791621`;
- pattern miner blob: `495a67699eb5014e52129f0238a2737049fe38e6`;
- market-learning adapter blob: `978a33554fad7e9d78b002778c4896be0af3333a`;
- range-limited loader blob: `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`.

All pre-existing execution, result, rerun, retry, replacement, reserved-data, candidate, Phase 8B, demo, broker/live, real-money, and trading booleans in those frozen layers must still be false.

## One-slot semantics

DEC-281 authorizes only the existence of one future historical-result slot in source governance.

The slot state is valid only while:

1. the exact DEC-280 proof run exists once;
2. that proof retains its exact immutable terminal identity;
3. no other manual-main EXP-061 run exists.

The proof run does not consume the historical-result slot.

The first later non-proof manual-main EXP-061 run consumes the historical-result slot immediately, regardless of whether it is queued, running, succeeds, fails, is cancelled, or times out.

A second historical-result attempt is invalid.

A GitHub rerun with `run_attempt != 1` is invalid.

Retry and replacement remain unauthorized.

## Historical data boundary

The later bounded result attempt may use only the already-frozen EXP-061 historical source range:

- start: 2015-01-01 inclusive;
- end: 2023-01-01 exclusive.

The reserved robustness block remains closed:

- 2023-01-01 inclusive;
- 2026-08-21 exclusive.

DEC-281 does not alter the DEC-270 protocol, 18-cell inventory, source artifacts, hypothesis caps, confirmation rules, validation rules, or aggregate evidence semantics.

## Authorization split

DEC-281 records:

- historical-result slot source authorization: **true**;
- workflow dispatch authorization: **false**;
- historical-result dispatch authorization: **false**;
- historical discovery execution authorization: **false**;
- discovery-result authorization: **false**;
- rerun: **false**;
- retry: **false**;
- replacement: **false**;
- reserved robustness access: **false**;
- candidate compilation: **false**;
- promotion: **false**;
- Phase 8B: **false**;
- demo orders: **false**;
- broker mutation: **false**;
- live orders: **false**;
- real-money action: **false**;
- trading: **false**.

This distinction matters: DEC-281 says a single later historical-result slot may exist. It does not provide any way to use that slot yet.

## Frozen implementation

- source: `src/fmp/discovery/historical_run_authorization.py`;
- source blob: `1eab1cee2fc81441cf1c3168cc73275cd29addf5`;
- focused tests: `tests/test_phase8a_exp061_historical_run_authorization.py`;
- focused-test blob: `07886d2fde86e75eb1c92509733909c58c95c8ee`.

The implementation independently validates the frozen source blobs and classifies workflow history into:

- `EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE`; or
- `EXP061_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED`.

The source authorization builder succeeds only in the first state.

## Next gate

After DEC-281 merges green, the next safe gate is a separate clean-main read-only operator.

That operator may expose the single historical dispatch command only while the exact DEC-281 inventory remains slot-available. It must have no execute mode.

DEC-281 itself does not dispatch or execute the historical workflow.
