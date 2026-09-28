# Phase 8A — EXP-062 Workflow-Install Preflight Proof Freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO INSTALL OR EXECUTOR  
**Decision:** DEC-352  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-351

DEC-352 freezes an already-valid DEC-351 review of a future successful DEC-350
workflow-install-preflight proof.

It preserves exact proof run/job/artifact identities, artifact digest, raw/canonical
preflight hashes, DEC-349/348 identities, the absent executor workflow path, target
run #2 / attempt 1, and the exact DEC-351 review source map.

The freeze emits a deterministic `freeze_fingerprint_sha256` over canonical JSON.

Workflow-install authorization, workflow installed state, historical executor
availability, historical-result dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

Next gate after real DEC-350 proof evidence: concrete runtime-evidence binding against
the exact DEC-351 review and DEC-352 fingerprint.
