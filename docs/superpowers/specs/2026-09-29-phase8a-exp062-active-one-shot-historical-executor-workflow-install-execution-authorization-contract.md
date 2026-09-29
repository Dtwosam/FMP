# Phase 8A — EXP-062 Workflow Install-Execution Authorization Contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY EXECUTION-AUTHORIZATION CONTRACT / NO INSTALL OR DISPATCH  
**Decision:** DEC-384  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-383

## Purpose

DEC-384 creates the source-only authorization contract for a later execution of the
active one-shot historical executor workflow installation.

It pins the exact DEC-383 runtime-evidence freeze and its deterministic fingerprint,
plus the dormant executor workflow template. The active executor workflow path must
still be absent.

## Frozen predecessor

DEC-384 requires:

- DEC-383 runtime-freeze blob:
  `b946d5b3d390d008634d49a2a0b560211d18aa2b`;
- DEC-383 runtime-freeze fingerprint:
  `e4369f71272b8fd8a3ef4104f12aaf748bd7c938e4feb648a87c6aadd14e2e19`;
- dormant executor template blob:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- active executor workflow path absent;
- zero historical-result attempts;
- target historical run #2 / attempt 1.

## Authority boundary

Only the install-execution authorization source is authorized. DEC-384 does not
authorize or perform workflow installation.

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

The next safe gate is a read-only current-main install-execution authorization
preflight. It may verify that the execution-authorization source is still valid, but
cannot install the workflow or dispatch historical discovery.
