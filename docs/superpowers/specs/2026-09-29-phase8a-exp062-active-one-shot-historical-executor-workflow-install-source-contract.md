# Phase 8A — EXP-062 Active Executor Workflow Install Source Contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY WORKFLOW-INSTALL CONTRACT / NO INSTALL OR DISPATCH  
**Decision:** DEC-402  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-401

## Purpose

DEC-402 creates the final source-only workflow-install contract without mutating the
historical DEC-360 contract module.

It pins the concrete DEC-401 runtime-evidence freeze and the dormant executor
workflow template. The active executor workflow path must remain absent.

## Frozen predecessor

DEC-402 requires:

- DEC-401 runtime-freeze blob:
  `bc18c1970e1927aa57a24c578351a5a4a797b7d8`;
- DEC-401 runtime-freeze fingerprint:
  `e2ee9e46bfe0a0fc132c5ce3f06bbad343ddb739ccaf0d22893886d1f41fbd2c`;
- dormant executor template blob:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- zero historical-result attempts;
- target historical run #2 / attempt 1.

## Authority boundary

The five predecessor source-only gates remain true. DEC-402 adds only
`active_one_shot_historical_executor_workflow_install_source_authorized=true`.

Actual workflow-install authorization, installed state, historical executor
availability, historical-result dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a read-only current-main workflow-install source preflight.
It may verify that the final source contract remains valid, but cannot install the
workflow or dispatch historical discovery.
