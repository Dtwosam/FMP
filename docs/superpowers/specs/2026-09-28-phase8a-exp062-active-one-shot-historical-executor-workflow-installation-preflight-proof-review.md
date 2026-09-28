# Phase 8A — EXP-062 Active Workflow-Installation Preflight Proof Review

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FUTURE RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH  
**Decision:** DEC-369  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-368

DEC-369 reviews a future successful DEC-368 merged-main active workflow-installation
preflight proof.

It requires the exact DEC-368 workflow, run #1 / attempt 1 success, one successful
read-only job, one non-expired artifact, and exact DEC-367 preflight bytes.

The reviewer pins DEC-368, DEC-367 preflight/CLI, DEC-366 installation contract, the
dormant executor template, and the active discovery workflow. It records raw and
canonical preflight SHA-256 hashes.

A valid review preserves the active executor workflow path as absent, zero historical-
result attempts, target run #2 / attempt 1, installation-source authorization, and
all install / executor / dispatch / execute / trading authority locks.

Next gate: immutable deterministic review freeze.
