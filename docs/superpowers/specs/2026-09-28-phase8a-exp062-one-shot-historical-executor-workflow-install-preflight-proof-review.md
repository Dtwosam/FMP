# Phase 8A — EXP-062 Workflow-Install Preflight Proof Review

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FUTURE RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH  
**Decision:** DEC-351  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-350

DEC-351 reviews a future successful DEC-350 merged-main proof. It requires exact
workflow/run/job/artifact identity, a non-expired artifact, and exact DEC-349
workflow-install-preflight bytes.

The reviewer pins DEC-350, DEC-349 preflight/CLI, DEC-348 install contract, and the
active discovery workflow. It records raw and canonical preflight SHA-256 hashes.

A valid review preserves the absent executor workflow path, zero historical-result
attempts, target run #2 / attempt 1, install-source authorization, and all install /
executor / dispatch / execute / trading authority locks.

The next safe gate is an immutable deterministic freeze of a valid DEC-351 review.
