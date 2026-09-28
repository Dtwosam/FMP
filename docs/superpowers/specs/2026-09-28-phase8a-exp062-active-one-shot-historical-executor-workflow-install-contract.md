# Phase 8A — EXP-062 Active One-Shot Historical Executor Workflow Install Contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY ACTIVE INSTALL CONTRACT / ACTIVE WORKFLOW ABSENT  
**Decision:** DEC-360  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-359

## Purpose

DEC-360 adds the source-only contract for a future active one-shot historical
executor workflow installation.

It pins the concrete DEC-359 dormant-source runtime freeze and the exact disabled
executor template. It does not copy that template into `.github/workflows/` and
does not authorize installation or dispatch.

## Frozen predecessor

DEC-360 pins:

- DEC-359 runtime-freeze blob:
  `3d4b7912396fbf7d51b6de4b30138bcd75566387`;
- DEC-359 runtime-freeze fingerprint:
  `f7e1a6d1946dd42a5f72fbd9c154d1efa448db5d4e38b7469cbf0d0485fde84f`;
- dormant executor template blob:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- zero historical-result attempts;
- target run #2 / attempt 1.

## Active workflow boundary

The reserved active workflow path is:

`.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`

DEC-360 sets only:

`active_one_shot_historical_executor_workflow_install_source_authorized = true`

It keeps:

- active workflow path absent;
- workflow-install authorization false;
- workflow installed false;
- historical executor availability false;
- historical-result dispatch authorization false;
- execute mode false.

## Safety boundary

Rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a read-only current-main active workflow-install preflight.
That gate may prove the active path is absent, the dormant template is exact, and the
historical slot remains empty, but it must not install or dispatch anything.
