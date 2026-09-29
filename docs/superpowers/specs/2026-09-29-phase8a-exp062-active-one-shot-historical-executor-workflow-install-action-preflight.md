# Phase 8A — EXP-062 Workflow-Install Action Preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-418  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-417

DEC-418 checks that the source-only workflow-install action contract is still valid
on the exact current `main` commit before any repository-hosted proof or actual
workflow mutation can advance.

It pins the DEC-417 contract blob
`7931d86d7b567894767f17efa990fbdac63e613e`, requires the dormant template
unchanged, requires the active executor workflow path to remain absent, and verifies
that the historical-result slot is still unused.

All eight source-only gates remain true. The CLI exposes only `plan`. There is no
install, execute, advance, or workflow-dispatch surface.

Actual workflow-install authorization, installed state, executor availability,
historical dispatch, execute mode, reserved-data access, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

## Next gate

A repository-hosted, read-only first-run/attempt-1 proof of this action preflight.
