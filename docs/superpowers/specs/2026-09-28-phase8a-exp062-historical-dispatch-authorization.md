# Phase 8A — EXP-062 One-Shot Historical Dispatch Authorization Contract

**Date:** 2026-09-28  
**Status:** SOURCE CONTRACT AUTHORIZED / DISPATCH + EXECUTOR STILL LOCKED  
**Decision:** DEC-318  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-317

## Purpose

DEC-318 authorizes only the existence of a source contract for one future historical
dispatch. It does not authorize a runtime submission and does not provide an executor.

## Frozen prerequisite

DEC-318 pins the concrete DEC-317 runtime-evidence freeze source blob:

`9626f6cd1c66a67d91dd3acf743e120ea8d2e9c0`

and requires the exact DEC-317 runtime-freeze fingerprint:

`eeac1b77b7bd77b14880aeb192ea1df664c15b91e440e3938b8cba0a67b95619`.

The predecessor must still prove:

- DEC-314 plan proof run `36414282818`;
- job `108901556593`;
- artifact `10966632240`;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact frozen discovery command;
- historical execution/result authority only for the exact DEC-312 runtime;
- historical dispatch and all downstream authorities false.

## Authorization split

DEC-318 records:

- one-shot dispatch source contract authorized: **true**;
- historical-result dispatch authorized: **false**;
- historical executor available: **false**;
- historical discovery execution authorization for target run #2: **true**;
- discovery-result production for target run #2: **true**;
- rerun / retry / replacement: **false**;
- reserved 2023-2026 access: **false**;
- candidate compilation / promotion: **false**;
- Phase 8B / demo / broker / live / real-money / trading: **false**.

This distinction is intentional. DEC-318 allows later code to define a read-only
current-main dispatch check. It does not submit the workflow.

## Next gate

The next safe gate is a **read-only current-main one-shot dispatch operator**. It must
recheck:

- current main head;
- exact DEC-317/318 source identities;
- frozen proof remains workflow run #1;
- historical-result attempt count is still zero;
- target remains workflow run #2 / attempt 1.

That operator may expose the exact dispatch command as evidence only and must still
have no execute mode.
