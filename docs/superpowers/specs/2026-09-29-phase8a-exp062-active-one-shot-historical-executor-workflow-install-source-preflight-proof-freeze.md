# Phase 8A — EXP-062 Workflow-Install Source Preflight Proof Freeze

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC REVIEW FREEZE / NO INSTALL OR DISPATCH  
**Decision:** DEC-406  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-405

DEC-406 deterministically freezes an already-valid DEC-405 review of a successful
DEC-404 workflow-install source-preflight proof.

The freeze preserves exact proof run/job/artifact identities, artifact digest,
raw/canonical DEC-403 preflight hashes, DEC-403/402 identities, the dormant executor
template, active workflow-absent state, target run #2 / attempt 1, and the exact
DEC-405 review source map.

It emits one canonical `freeze_fingerprint_sha256` for later concrete
runtime-evidence binding. It cannot invent runtime evidence, install the executor
workflow, dispatch historical discovery, or expose execute mode.

All six source-only gates may be true. Actual workflow-install authorization,
installed state, historical executor availability, historical-result dispatch,
rerun/retry/replacement, reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading remain
locked.

Next gate after real DEC-404 evidence: concrete workflow-install source-preflight
proof runtime-evidence binding before install.
