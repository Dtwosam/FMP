# Phase 8A — EXP-062 One-Shot Historical Executor Workflow-Install Contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY INSTALL CONTRACT / WORKFLOW NOT INSTALLED  
**Decision:** DEC-348  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-347

## Purpose

DEC-348 adds the source-only contract for a future one-shot historical executor
workflow installation.

It pins the concrete DEC-347 runtime freeze and defines the expected future workflow
path without installing that workflow or enabling any runtime authority.

## Frozen predecessor

DEC-348 pins:

- DEC-347 runtime-freeze blob:
  `4781dae661a78d7b50e2070e87b8d7e34ea49f3c`;
- DEC-347 runtime-freeze fingerprint:
  `b714ceec4a30fde0693db5c21eab2ce62d7a63c1c724c55321bc8cb13b423e03`;
- DEC-346 freeze fingerprint:
  `3ba4b6aba0cafab3989c1f20536ad36603786efdcef49964a31bc99b73a79988`;
- DEC-334 terminal-review identity;
- zero historical-result attempts;
- target run #2 / attempt 1.

## Future workflow identity

The only expected future executor workflow path is:

`.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`

DEC-348 sets only:

`one_shot_historical_executor_workflow_install_source_authorized = true`

It keeps:

- `historical_executor_workflow_installed = false`;
- historical executor availability false;
- historical-result dispatch authorization false;
- execute mode false.

## Safety boundary

Rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a read-only current-main workflow-install preflight. That gate
may prove whether the expected workflow is absent and the slot remains empty, but it
must not install or dispatch the workflow.
