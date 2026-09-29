# Phase 8A — EXP-062 Active Workflow Install-Authorization Contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY AUTHORIZATION CONTRACT / INSTALL STILL LOCKED  
**Decision:** DEC-372  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-371

## Purpose

DEC-372 defines the source-only contract for a future authorization decision to install
the active one-shot historical executor workflow.

It pins the concrete DEC-371 runtime freeze and the exact dormant executor template,
while requiring the active workflow path to remain absent.

## Frozen predecessor

DEC-372 pins:

- DEC-371 runtime-freeze blob:
  `fb9f968fcfc953217234f7484b14d98293087f02`;
- DEC-371 runtime-freeze fingerprint:
  `a498bf1cae3c6e92803fc750331c3090c35bb3af13bf01a62866831d29bb95f8`;
- dormant executor-template blob:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- zero historical-result attempts;
- target run #2 / attempt 1.

## Authorization boundary

DEC-372 sets only:

`active_one_shot_historical_executor_workflow_install_authorization_source_authorized = true`

It keeps:

- `historical_executor_workflow_install_authorized = false`;
- workflow installed state false;
- historical executor availability false;
- historical-result dispatch authorization false;
- execute mode false.

The active workflow path must remain absent.

## Safety boundary

Rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a read-only current-main install-authorization preflight. That
gate may prove the authorization source and active-path absence, but cannot install
or dispatch the workflow.
