# Phase 8A — EXP-062 Active Workflow-Install Preflight Proof Freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO INSTALL OR EXECUTOR  
**Decision:** DEC-364  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-363

DEC-364 freezes an already-valid DEC-363 review of a successful DEC-362
active-workflow-install-preflight proof.

It preserves exact proof run/job/artifact identities, artifact digest, raw/canonical
preflight hashes, DEC-361/360 identities, dormant executor-template identity, active
workflow-absent state, target run #2 / attempt 1, and the exact DEC-363 review source
map.

The freeze emits a deterministic `freeze_fingerprint_sha256` over canonical JSON.

Workflow-install authorization, workflow installed state, historical executor
availability, historical-result dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

Next gate after real DEC-362 proof evidence: concrete runtime-evidence binding against
the exact DEC-363 review and DEC-364 fingerprint.
