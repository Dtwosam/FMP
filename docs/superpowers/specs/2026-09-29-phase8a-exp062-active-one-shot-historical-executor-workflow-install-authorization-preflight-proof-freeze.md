# Phase 8A — EXP-062 Active Install-Authorization Preflight Proof Freeze

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO INSTALL OR EXECUTOR  
**Decision:** DEC-376  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-375

DEC-376 freezes an already-valid DEC-375 review of the successful DEC-374
install-authorization-preflight proof.

It preserves exact proof run/job/artifact identities, artifact digest, raw/canonical
preflight hashes, DEC-373/372 identities, dormant executor-template identity, active
workflow-absent state, target run #2 / attempt 1, and the exact DEC-375 review source
map.

The freeze emits a deterministic `freeze_fingerprint_sha256` over canonical JSON.

Actual workflow-install authorization, workflow installed state, historical executor
availability, historical-result dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

Next gate: concrete runtime-evidence binding against the exact DEC-375 review and
DEC-376 fingerprint.
