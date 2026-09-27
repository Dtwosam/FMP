# Phase 8A — EXP-061 Read-Only Historical Slot Operator

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY READ-ONLY OPERATOR / NO EXECUTE MODE  
**Decision:** DEC-282  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-281

## Purpose

DEC-282 adds the read-only operator for the single source-authorized EXP-061 historical-result slot.

It does not dispatch the workflow and has no execute, advance, retry, rerun, or replacement mode.

## Inputs

The operator requires:

- current `main` branch metadata;
- current EXP-061 workflow-run history;
- an exact caller-supplied expected main head.

The current main head must equal the supplied expected head or the operator fails closed.

## Slot logic

The operator delegates run-history classification to the frozen DEC-281 authorization contract.

A valid empty slot requires:

- exactly the frozen DEC-280 proof run `36319888985`;
- no other manual-main EXP-061 runs;
- DEC-281 source-slot authorization intact.

Only in that state does the operator expose the future command:

`gh workflow run phase8a-exp061-discovery.yml --ref main`

The command is plan evidence only.

The report still records:

- historical-result dispatch authorization: false;
- execute mode available: false;
- historical discovery execution authorization: false;
- discovery-result authorization: false.

If any later historical-result run is present, the operator removes the command and reports:

`EXP061_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED`

The slot is then consumed and no second command can be planned.

## Frozen implementation

- DEC-281 authorization source blob: `1eab1cee2fc81441cf1c3168cc73275cd29addf5`;
- operator source: `src/fmp/discovery/historical_operator.py`;
- operator source blob: `1ffef37d94b04a8206f665c375dc0b2642c4caa9`;
- CLI: `scripts/phase8a_exp061_historical_operator.py`;
- CLI blob: `4d667d05ef2a5bd672cb9d98a81f13dd2ba9370c`;
- focused tests: `tests/test_phase8a_exp061_historical_operator.py`;
- focused-test blob: `16399b4602fbd94b875d00abe706ae6fc815e802`.

## CLI surface

The CLI contains one command only:

`plan`

It reads local JSON snapshots and prints a validated plan.

There is no execute mode.

## Downstream locks

DEC-282 keeps false:

- historical-result dispatch;
- historical discovery execution;
- discovery-result production;
- rerun;
- retry;
- replacement;
- reserved 2023-2026 access;
- candidate compilation;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After DEC-282 merges green, the next safe gate is a repository-hosted read-only proof of the exact DEC-282 plan on merged main.

That proof may verify the slot is still empty and capture the exact future command as immutable evidence. It must not dispatch anything.
