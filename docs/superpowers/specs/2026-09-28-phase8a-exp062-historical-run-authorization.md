# Phase 8A — EXP-062 Historical Run Authorization Contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY ONE-SLOT AUTHORIZATION / DISPATCH + EXECUTION STILL LOCKED  
**Decision:** DEC-307  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-306

## Purpose

DEC-307 freezes the source-only authorization contract for the first and only bounded
EXP-062 historical discovery-result attempt.

It does not dispatch the workflow and does not open the existing execution gate.

## Frozen proof excluded from the slot

The exact DEC-306 fail-closed proof is excluded from the future historical-result slot:

- run id: `36358289723`;
- workflow: `phase8a-exp062-discovery`;
- path: `.github/workflows/phase8a-exp062-discovery.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head: `f2c55ac36a1a9ba7596ec0d4559c877a66cda0fb`;
- run number / attempt: `1 / 1`;
- terminal conclusion: `failure`.

DEC-306 already proved this run failed closed at the historical execution gate with no
cell-result or aggregate-result artifact. The later redundant DEC-303 executor run
`36360111479` belongs to a different workflow, failed before dispatch, and created no
second EXP-062 discovery run.

## Frozen source stack

DEC-307 binds the exact merged DEC-306 stack:

- DEC-306 merge: `cd3dbb87d142ce5841e3d376f3519460c80a1915`;
- DEC-306 runtime proof freeze:
  `src/fmp/discovery/exp062_runtime_proof_freeze.py` blob
  `8e9baec1ae7b24055064535fbf7e262055dffeca`;
- active workflow blob:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`;
- EXP-062 CLI blob:
  `e6a94c1733f952a8edc01584a198ead1816f4410`;
- runtime requirements blob:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`;
- EXP-062 run contract blob:
  `d304c8fafcff64f967f6777b1c494819f69d4a03`;
- EXP-062 workflow-source blob:
  `e20ded13de24f99e8ea6cfdc6cb0d1309d984f24`;
- EXP-062 locked-install blob:
  `febb2bc00342364c67a75c69439136079eba0a2c`;
- repaired adapter blob:
  `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- verified adapter-proof freeze blob:
  `18b7dde7eadf0f051a09fda04e648650bb270eb7`;
- frozen predecessor pattern protocol/miner/adapter/loader blobs remain unchanged.

All pre-existing dispatch, execution, result, rerun, retry, replacement, reserved-data,
candidate, Phase 8B, demo, broker/live, real-money, and trading booleans in those
layers must still be false.

## One-slot semantics

DEC-307 authorizes only the existence of one future historical-result slot in source
governance.

The slot remains available only while:

1. the exact DEC-306 proof run exists once as workflow run #1 / attempt 1;
2. that proof retains its exact immutable terminal identity;
3. no other matching manual-main EXP-062 discovery run exists.

The only valid future historical attempt is workflow run #2 / attempt 1. The first such
non-proof run consumes the slot immediately, regardless of whether it is queued,
running, succeeds, fails, is cancelled, or times out.

A second historical attempt is invalid. A rerun attempt is invalid. Reuse of the
frozen proof head is invalid. Retry and replacement remain unauthorized.

## Historical data boundary

The later bounded result attempt may use only the already-frozen research range:

- start: 2015-01-01 inclusive;
- end: 2023-01-01 exclusive.

The reserved robustness block remains closed:

- 2023-01-01 inclusive;
- 2026-08-21 exclusive.

DEC-307 does not alter the DEC-270 discovery semantics, 18-cell inventory, search
limits, confirmation rules, validation rules, or aggregate evidence semantics. It
preserves the isolated DEC-293 non-finite-to-null adapter repair verified by DEC-297.

## Authorization split

DEC-307 records:

- historical-result slot source authorization: **true**;
- historical-result dispatch authorization: **false**;
- historical discovery execution authorization: **false**;
- discovery-result authorization: **false**;
- rerun / retry / replacement: **false**;
- reserved robustness access: **false**;
- candidate compilation / promotion: **false**;
- Phase 8B: **false**;
- demo orders / broker mutation / live orders: **false**;
- real-money action / trading: **false**.

This distinction is intentional: DEC-307 says one later historical slot may exist. It
provides no way to use that slot.

## Frozen implementation

- source: `src/fmp/discovery/exp062_historical_run_authorization.py`;
- focused tests:
  `tests/test_phase8a_exp062_historical_run_authorization.py`.

The implementation independently validates the frozen source blobs and classifies
workflow history into:

- `EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE`; or
- `EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED`.

The source-authorization builder succeeds only in the first state.

## Next gate

After DEC-307 merges green, the next safe gate is a separate clean-main read-only
operator.

That operator may expose the single future historical dispatch command only while the
exact DEC-307 inventory remains slot-available. It must have no execute mode.

DEC-307 itself does not dispatch or execute the historical workflow.
