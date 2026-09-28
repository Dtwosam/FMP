# Phase 8A — EXP-062 Workflow-Preflight Proof Review

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FUTURE RUNTIME-EVIDENCE REVIEWER / NO DISPATCH  
**Decision:** DEC-345  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-344

DEC-345 reviews a future successful DEC-344 merged-main proof. It requires exact
workflow/run/job/artifact identity, a non-expired artifact, and exact DEC-343
workflow-preflight bytes.

The reviewer pins DEC-344, DEC-343 preflight/CLI, DEC-342 workflow contract, and the
active discovery workflow. It records raw and canonical preflight SHA-256 hashes.

A valid review preserves zero historical-result attempts, an unconsumed slot, target
run #2 / attempt 1, both source authorizations, and all executor/dispatch/trading
authority locks.

The next safe gate is an immutable deterministic freeze of a valid DEC-345 review.
