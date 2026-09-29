# Phase 8A — EXP-062 Workflow Install-Activation Preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN INSTALL-ACTIVATION PREFLIGHT / NO INSTALL  
**Decision:** DEC-397  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-396

DEC-397 adds a read-only current-main preflight for the source-authorized DEC-396
workflow install-activation contract.

It pins the exact DEC-396 contract, requires exact current main, requires the active
executor workflow path to remain absent, and rechecks the still-unused historical
result slot with target run #2 / attempt 1.

All five source-only gates remain true. The CLI exposes only `plan`; there is no
install, execute, advance, or workflow-dispatch surface. Actual workflow-install
authorization, installed state, executor availability, historical dispatch, execute
mode, reserved data, and downstream trading authority remain false.

Next gate: repository-hosted read-only workflow install-activation preflight proof.
