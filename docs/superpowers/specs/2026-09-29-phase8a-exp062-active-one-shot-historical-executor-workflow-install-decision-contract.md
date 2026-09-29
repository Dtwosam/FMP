# Phase 8A — EXP-062 Active Executor Workflow Install-Decision Contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY INSTALL-DECISION CONTRACT / NO INSTALL OR DISPATCH  
**Decision:** DEC-378  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-377

## Purpose

DEC-378 creates the source-only decision contract for the future installation of the
active one-shot historical executor workflow.

It pins the exact DEC-377 concrete runtime-evidence freeze and its deterministic
fingerprint, plus the dormant executor workflow template. The active executor
workflow path must still be absent.

## Frozen predecessor

DEC-378 requires:

- DEC-377 runtime-freeze blob:
  `0caa3b69f537f92bb13a41c6f28275f5513c9a07`;
- DEC-377 runtime-freeze fingerprint:
  `24619aed5578085ee3e2d3555e1b109817d9816042f646446dbc406b20f13593`;
- dormant executor template blob:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- active executor workflow path:
  `.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`;
- zero historical-result attempts;
- target historical run #2 / attempt 1.

## Authority boundary

Only the install-decision source is authorized. DEC-378 does not authorize or
perform workflow installation.

The following remain false:

- workflow-install authorization;
- workflow installed state;
- historical executor availability;
- historical-result dispatch authorization;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

## Next gate

The next safe gate is a read-only current-main active executor workflow
install-decision preflight. It may verify that the decision slot is still valid, but
cannot install the workflow or dispatch historical discovery.
