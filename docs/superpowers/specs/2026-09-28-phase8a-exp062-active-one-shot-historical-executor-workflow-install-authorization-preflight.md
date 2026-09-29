# Phase 8A — EXP-062 Active Workflow Install-Authorization Preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN AUTHORIZATION PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-373  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-372

## Purpose

DEC-373 adds a read-only current-main preflight for the DEC-372 source-authorized
future install-authorization decision for the active one-shot historical executor
workflow.

The preflight proves that the active executor workflow path is still absent, current
main matches the requested head, and the sole historical-result slot remains unused.

## Source binding

DEC-373 pins the DEC-372 install-authorization-contract blob:

`ac4876d6b544567c238d9241ee050b763c2ed630`

It also requires the dormant executor template blob:

`51ce87584369be957482460d81649adb1cb9f05d`

## Read-only checks

A valid preflight requires:

- exact `main` metadata and head;
- the active executor workflow path does not exist;
- the frozen EXP-062 proof remains the only discovery run;
- zero historical-result attempts;
- target run #2 / attempt 1;
- install-authorization source authorization true;
- actual install authorization false;
- workflow installed false;
- executor availability false;
- dispatch false;
- execute mode false.

The CLI exposes only `plan`; there is no install, execute, advance, or dispatch
surface.

## Safety boundary

Rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a repository-hosted read-only proof of this install-authorization
preflight.
