# Phase 8A — EXP-061 Read-Only Historical Execution Operator

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY READ-ONLY OPERATOR / NO EXECUTE MODE  
**Decision:** DEC-286  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-285

## Purpose

DEC-286 adds the read-only operator for the one-shot historical runtime authorized by DEC-285.

It does not dispatch the workflow and contains no execute mode.

## Frozen predecessor binding

DEC-286 binds DEC-285 historical execution authorization source:

`src/fmp/discovery/historical_execution_authorization.py`

Git blob:

`30258e076f6a786c977fac8c588ac2b22aeed66e`

The operator requires DEC-285 to remain source-authorized for historical runtime while DEC-285 historical-result dispatch authorization remains false.

## Live run inventory

DEC-286 reads the current EXP-061 workflow-run inventory and preserves the DEC-281 one-slot classifier.

The frozen proof must remain:

- workflow run id `36319888985`;
- workflow run number `1`;
- run attempt `1`;
- terminal failure;
- manual `main` dispatch.

If no later historical attempt exists, the operator reports:

`EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE`

and exposes only the future command:

`gh workflow run phase8a-exp061-discovery.yml --ref main`

as read-only plan evidence.

The operator also freezes the target runtime identity:

- expected target workflow run number: `2`;
- expected target run attempt: `1`.

If a later historical attempt already exists, it must be exactly workflow run number 2 / attempt 1. The operator then reports:

`EXP061_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED`

and removes the dispatch command.

Any second historical attempt, run number 3+, or rerun attempt fails closed.

## Main-head binding

The operator requires:

- current `main` branch metadata;
- current EXP-061 workflow-run history;
- an exact caller-supplied expected main head.

Current main must equal the supplied expected head.

## Authorization split

The read-only plan reports:

- historical execution source authorized: true;
- historical discovery execution authorized inside target runtime: true;
- discovery-result production authorized inside target runtime: true;
- historical-result dispatch authorized: false;
- execute mode available: false;
- rerun: false;
- retry: false;
- replacement: false;
- reserved robustness access: false;
- candidate compilation: false;
- promotion: false;
- Phase 8B: false;
- demo orders: false;
- broker mutation: false;
- live orders: false;
- real-money action: false;
- trading: false.

## Frozen implementation

Operator source:

`src/fmp/discovery/historical_execution_operator.py`

Git blob:

`a711b14fb613f1c9952f5b2a6bf85d892bd2c4a5`

Operator CLI:

`scripts/phase8a_exp061_historical_execution_operator.py`

Git blob:

`1f43e1218072918d2ebb33b2c312ba8e950881f9`

Focused tests:

`tests/test_phase8a_exp061_historical_execution_operator.py`

Git blob:

`42523ca36927e85a8c14566bf597d666a7ec1d20`

## CLI surface

The CLI exposes one command only:

`plan`

It reads local JSON snapshots and prints a validated plan.

There is no execute, advance, retry, rerun, or replacement mode.

## Next gate

After DEC-286 merges green, the next safe gate is a repository-hosted read-only proof of the exact DEC-286 slot-available execution plan on merged main.

That proof may capture the future dispatch command and target run-number identity as immutable evidence, but must not dispatch EXP-061.

A one-shot executor may be considered only after that proof succeeds and is reviewed.
