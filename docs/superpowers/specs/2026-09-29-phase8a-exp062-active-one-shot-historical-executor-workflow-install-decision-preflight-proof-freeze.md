# Phase 8A — EXP-062 Install-Decision Preflight Proof Freeze

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC REVIEW FREEZE / NO INSTALL OR DISPATCH  
**Decision:** DEC-382  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-381

DEC-382 deterministically freezes an already-valid DEC-381 review of a successful
DEC-380 install-decision-preflight proof.

The freeze preserves exact proof run/job/artifact identities, artifact digest,
raw/canonical DEC-379 preflight hashes, DEC-379/378 identities, the dormant executor
template, active workflow-absent state, target run #2 / attempt 1, and the exact
DEC-381 review source map.

It emits one canonical `freeze_fingerprint_sha256` for later concrete
runtime-evidence binding. It cannot invent runtime evidence, install the executor
workflow, dispatch historical discovery, or expose execute mode.

Install-authorization and install-decision source contracts may be true. Actual
workflow-install authorization, installed state, historical executor availability,
historical-result dispatch, rerun/retry/replacement, reserved 2023-2026 access,
candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain locked.

Next gate after real DEC-380 evidence: concrete install-decision-preflight proof
runtime-evidence binding before any workflow installation.
