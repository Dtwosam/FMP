# Phase 8A — EXP-062 One-Shot Historical Executor Activation Contract

**Date:** 2026-09-28  
**Status:** SOURCE ACTIVATION CONTRACT AUTHORIZED / EXECUTOR + DISPATCH STILL LOCKED  
**Decision:** DEC-330  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-329

## Purpose

DEC-330 authorizes only the source contract for future activation of the one-shot
historical executor. It binds the concrete DEC-329 executor-preflight runtime freeze.

It does not make an executor available, expose an execute mode, or authorize a
historical workflow submission.

## Frozen prerequisite

DEC-330 pins the DEC-329 runtime-freeze source blob:

`f9f727ae23b88fe52ca9c41739f04ab26bec0b4e`

and requires the exact DEC-329 runtime-freeze fingerprint:

`5c4e081fca4848cf18f8ed03c68e5d7854723e92368eded03fb5e9b54756ab61`.

The predecessor must still prove:

- DEC-326 preflight proof run `36422936991`;
- job `108929843306`;
- artifact `10970303347`;
- zero historical-result attempts;
- an unconsumed historical-result slot;
- target run #2 / attempt 1;
- the exact frozen discovery command;
- executor availability, actual dispatch, and execute mode false.

## Authorization split

DEC-330 records:

- one-shot executor activation source authorized: **true**;
- historical executor available: **false**;
- historical-result dispatch authorized: **false**;
- historical execute mode available: **false**;
- historical discovery/result production for target run #2: **true**;
- rerun / retry / replacement: **false**;
- reserved 2023-2026 access: **false**;
- candidate compilation / promotion: **false**;
- Phase 8B / demo / broker / live / real-money / trading: **false**.

## Next gate

The next safe gate is a **read-only current-main executor activation preflight**. It
must recheck the current main head, exact DEC-329/330 source identities, the frozen
proof inventory, zero historical-result attempts, and target run #2 / attempt 1.

That preflight may expose activation readiness as evidence only and must not dispatch
the workflow.
