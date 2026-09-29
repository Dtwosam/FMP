# Phase 8A — EXP-062 Install-Execution Authorization Preflight Proof Review

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH  
**Decision:** DEC-387  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-386

DEC-387 reviews a successful DEC-386 merged-main proof of the active one-shot
historical executor workflow install-execution authorization preflight.

It pins the DEC-386 proof workflow, DEC-385 preflight/CLI, DEC-384 execution-
authorization contract, the dormant executor template, and the active discovery
workflow. A valid review requires exact run #1 / attempt 1 success, exactly one
successful proof job, one non-expired artifact, and exact DEC-385 preflight bytes.

The reviewer records raw and canonical SHA-256 hashes of the preflight artifact.

The active executor workflow path must remain absent. The install-authorization,
install-decision, and install-execution-authorization source gates may be true, but
actual workflow-install authorization, workflow installed state, historical executor
availability, historical-result dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

Next gate after real successful DEC-386 evidence: immutable deterministic
proof-review freeze.
