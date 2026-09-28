# Phase 8A — EXP-062 Active Install Preflight Proof Review

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FUTURE RUNTIME-EVIDENCE REVIEWER  
**Decision:** DEC-363  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-362

DEC-363 reviews a future successful DEC-362 merged-main proof. It requires exact
workflow/run/job/artifact identity, a non-expired artifact, and exact DEC-361
active-install-preflight bytes.

The reviewer pins DEC-362, DEC-361 preflight/CLI, DEC-360 install contract, the
dormant executor template, and the active discovery workflow. It records raw and
canonical preflight SHA-256 hashes.

A valid review preserves the absent active workflow path, zero historical-result
attempts, target run #2 / attempt 1, active install-source authorization, and all
install / executor / dispatch / execute / trading authority locks.

The next safe gate is an immutable deterministic freeze of a valid DEC-363 review.
