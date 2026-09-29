# Phase 8A — EXP-062 Active Executor Workflow Install-Execution Contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY INSTALL-EXECUTION CONTRACT / NO INSTALL OR DISPATCH  
**Decision:** DEC-390  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-389

## Purpose

DEC-390 creates the source-only contract for the future installation execution
decision. It binds the concrete DEC-389 runtime-evidence freeze and the dormant
executor workflow template while keeping the active executor workflow path absent.

## Frozen predecessor

DEC-390 requires:

- DEC-389 runtime-freeze blob:
  `fada14bd598265f374eaa9ddeff39393bec80ddb`;
- DEC-389 runtime-freeze fingerprint:
  `3517e83d30097041e7a8a74219d6da8b6fe77cf6ae3f048bffec923913826bc1`;
- real DEC-386 merged head:
  `cdbef40d1c9908650155933ae5073909ad9be24d`;
- dormant executor template blob:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- zero historical-result attempts;
- target historical run #2 / attempt 1.

## Authority boundary

The prior source-only gates remain true and DEC-390 additionally authorizes only
the install-execution contract source.

Actual workflow-install authorization, workflow installed state, historical executor
availability, historical-result dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a read-only current-main workflow install-execution preflight.
It may verify the install-execution contract remains valid, but cannot install the
workflow or dispatch historical discovery.
