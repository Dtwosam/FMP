# Phase 8A — EXP-062 One-Shot Historical Executor Workflow Contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY WORKFLOW CONTRACT / RUNTIME + DISPATCH LOCKED  
**Decision:** DEC-342  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-341

## Purpose

DEC-342 adds the source-only contract for a future one-shot EXP-062 historical
executor workflow.

It pins the concrete DEC-341 source-proof runtime freeze and verifies that the sole
historical-result slot is still empty with target run #2 / attempt 1.

The contract defines only that a future workflow source may be considered. It does
not make an executor available, authorize historical-result dispatch, expose execute
mode, or submit the historical workflow.

## Frozen predecessor

DEC-342 pins:

- DEC-341 runtime-freeze blob:
  `b99a2f453423734a92d79d8f8d1c2fa1fa20d45f`;
- DEC-341 runtime-freeze fingerprint:
  `7375b8fa30a425d660e6a0c392eb6c0084d9f0bb65c7b141d5ef11a6459650da`;
- DEC-340 freeze fingerprint:
  `e340394fb987c68d9203a57c9cd363f255729b3424a9600ec03533ff421960a8`;
- DEC-334 terminal-review identity;
- zero historical-result attempts;
- target run #2 / attempt 1.

## Authority boundary

DEC-342 sets only:

`one_shot_historical_executor_workflow_source_authorized = true`

The earlier one-shot executor source authorization remains true as provenance.

All runtime authority remains false:

- historical executor availability;
- historical-result dispatch authorization;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

## Next gate

The next safe gate is a read-only current-main one-shot executor workflow preflight.
That preflight may inspect the exact current main and the historical slot, but it must
not dispatch or execute the historical workflow.
