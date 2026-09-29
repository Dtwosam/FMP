# Phase 8A — EXP-062 Workflow Install Source Preflight Proof Review

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH  
**Decision:** DEC-405  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-404

DEC-405 reviews a successful DEC-404 merged-main proof of the workflow-install
source preflight.

It pins the DEC-404 proof workflow, DEC-403 preflight/CLI, DEC-402 source contract,
the dormant executor template, and the active discovery workflow. A valid review
requires exact run #1 / attempt 1 success, exactly one successful proof job, one
non-expired artifact, and exact DEC-403 preflight bytes.

The reviewer records raw and canonical SHA-256 hashes of the preflight artifact.

All six source-only gates may be true, but the active executor workflow path must
remain absent. Actual workflow-install authorization, installed state, historical
executor availability, historical-result dispatch, execute mode,
rerun/retry/replacement, reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading remain
false.

Next gate after real successful DEC-404 evidence: immutable deterministic
proof-review freeze.
