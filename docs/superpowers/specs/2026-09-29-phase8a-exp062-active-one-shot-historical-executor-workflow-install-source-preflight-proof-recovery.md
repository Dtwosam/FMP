# Phase 8A — EXP-062 Workflow-Install Source-Preflight Proof Recovery

**Date:** 2026-09-29  
**Status:** EXPLICIT READ-ONLY PROOF RECOVERY / NO INSTALL OR DISPATCH  
**Decision:** DEC-407  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-402, DEC-403, DEC-404 failure

## Purpose

DEC-407 recovers from the real merged-main DEC-404 proof failure without rewriting
history or pretending run #1 succeeded.

DEC-404 run #1 / attempt 1:

- run: `36613664506`;
- head: `0db04ae49b3533778b08afa31e9ef9a26576b80c`;
- job: `109561121322`;
- DEC-403 preflight step: success;
- wrapper verification step: failure;
- immutable artifact upload: skipped.

The failure was caused by the wrapper asserting a field that DEC-403 never emits:
`install_source_slot_verified_available`.

## Recovery contract

DEC-407 keeps the same workflow path so the recovery run is explicitly:

- workflow run #2;
- attempt 1;
- push to exact merged `main`;
- read-only `contents` and `actions` permissions;
- no `workflow_dispatch`;
- no install, execute, advance, or historical-dispatch command.

The workflow pins the failed DEC-404 run/job as provenance, re-runs the exact DEC-403
`plan` surface, verifies only fields actually emitted by DEC-403, and uploads one
immutable recovery preflight JSON artifact.

## Authority boundary

All six source-only gates may remain true.

The following remain false:

- workflow-install authorization;
- workflow installed state;
- historical executor availability;
- historical-result dispatch;
- historical execute mode;
- rerun / retry / replacement historical execution;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

## Next gate

After a successful DEC-407 run #2 / attempt 1, the next safe gate is a source-only
review of that concrete recovery proof evidence, followed by deterministic freezing
and runtime-evidence binding before any installation authorization can advance.
