# Phase 8A — EXP-062 One-Shot Historical Executor Contract

**Date:** 2026-09-28  
**Status:** SOURCE CONTRACT AUTHORIZED / EXECUTOR + DISPATCH STILL LOCKED  
**Decision:** DEC-324  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-323

## Purpose

DEC-324 authorizes only the source contract for a future one-shot historical executor.
It binds the concrete DEC-323 dispatch-plan runtime freeze and does not make an
executor available.

## Frozen prerequisite

DEC-324 pins the DEC-323 runtime-freeze source blob:

`44815c9ff23fcd022346558e8c043673154ca0b3`

and requires the exact DEC-323 runtime-freeze fingerprint:

`d412cc0fe115f7c10da6b0cfee092de718539ade041c8476659f6c30f8adc8c3`.

The predecessor must still prove:

- DEC-320 dispatch-plan proof run `36418793172`;
- job `108916232597`;
- artifact `10967344018`;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact frozen discovery command;
- actual dispatch, executor availability, and execute mode false.

## Authorization split

DEC-324 records:

- one-shot executor source contract authorized: **true**;
- historical executor available: **false**;
- historical-result dispatch authorized: **false**;
- historical execute mode available: **false**;
- historical discovery/result production for target run #2: **true**;
- rerun / retry / replacement: **false**;
- reserved 2023-2026 access: **false**;
- candidate compilation / promotion: **false**;
- Phase 8B / demo / broker / live / real-money / trading: **false**.

## Next gate

The next safe gate is a **read-only current-main executor preflight**. It must recheck:

- exact current main head;
- DEC-323/324 source identities;
- the frozen proof remains run #1;
- historical-result attempts remain zero;
- target remains run #2 / attempt 1;
- executor availability and actual dispatch remain false.

That preflight may expose executor readiness as evidence only and must not submit the
workflow.
