# Phase 8A — EXP-061 Historical Terminal Review Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY PREDECLARED TERMINAL REVIEW / NO RESULT YET  
**Decision:** DEC-290  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-289

## Purpose

DEC-290 predeclares how the sole EXP-061 historical workflow run #2 will be reviewed after it reaches a terminal state.

This contract is defined **before** run #2 exists so success/failure criteria are not chosen after seeing the result.

It cannot dispatch, rerun, retry, replace, promote, demo trade, live trade, or touch reserved 2023-2026 robustness data.

## Exact historical run identity

A reviewable historical run must be:

- workflow: `phase8a-exp061-discovery`;
- path: `.github/workflows/phase8a-exp061-discovery.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- workflow run number: `2`;
- run attempt: `1`;
- exact caller-supplied DEC-289 merged-main head;
- terminal status: `completed`;
- distinct from the frozen proof run `36319888985`.

Any other run number, attempt, head, branch, workflow identity, or non-terminal state fails closed.

## Success terminal shape

A run with conclusion `success` is valid only if it has the exact DEC-274 success inventory:

- 20 materialized jobs:
  - 1 preflight;
  - 18 expanded cell jobs;
  - 1 aggregate;
- every job conclusion is `success`;
- no unexpanded matrix placeholder;
- exactly 20 non-expired artifacts:
  - 1 preflight artifact;
  - 18 cell artifacts;
  - 1 aggregate artifact;
- every artifact name exactly matches the DEC-274 commit-scoped contract.

Only then is the run classified:

`EXP061_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED`

Even this classification does **not** authorize candidate compilation. The aggregate and cell result contents still require separate deterministic review.

## Non-success terminal shape

Any terminal run whose conclusion is not `success` is classified:

`EXP061_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED`

The sole historical-result slot is permanently consumed.

Partial expected evidence may be preserved, but:

- every materialized job name must belong to the expected DEC-274 inventory;
- every preserved artifact name must belong to the expected DEC-274 inventory;
- preserved artifacts must be non-expired;
- no unexpected job or artifact is allowed;
- no rerun, retry, or replacement is authorized.

## GitHub skipped-matrix compatibility

DEC-280 established that GitHub may represent a skipped matrix dependency after an early failure as one literal unexpanded job template:

`exp061-cell-${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-${{ matrix.dataset.horizon }}m`

DEC-290 predeclares that exact API shape as acceptable only when:

- the run is non-success;
- that placeholder is `skipped`;
- no expanded cell jobs coexist with it.

A successful run can never use the placeholder shape.

## Frozen implementation

Terminal review source:

`src/fmp/discovery/historical_result_review_contract.py`

Git blob:

`2df4caa00aa683b8d627d061ae806178fbd5cd9c`

Focused tests:

`tests/test_phase8a_exp061_historical_terminal_review_contract.py`

Git blob:

`f6a166f425c2a00b17a2063e71e801f0bc64739d`

The implementation reuses the exact DEC-274 expected job/artifact inventory.

## Locks preserved

Regardless of terminal outcome, DEC-290 keeps false:

- historical rerun;
- historical retry;
- replacement run;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After run #2 reaches a terminal state, a later decision must bind its exact:

- run id/head/conclusion;
- job inventory;
- artifact ids/names/digests;
- cell evidence;
- aggregate evidence if present.

If run #2 is successful and complete, the aggregate result may then be inspected to determine whether any pattern hypotheses survived validation.

If run #2 is non-success, the experiment closes for that attempt with no retry/replacement unless a future separately justified decision explicitly opens a new experiment identity.
