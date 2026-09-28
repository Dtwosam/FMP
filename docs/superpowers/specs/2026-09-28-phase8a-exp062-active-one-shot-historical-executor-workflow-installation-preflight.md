# Phase 8A — EXP-062 Active Workflow-Installation Preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-367  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-366

DEC-367 adds a read-only current-main preflight for the DEC-366 source-authorized
active workflow-installation contract.

A valid preflight requires exact `main`, the exact dormant executor template,
the active executor workflow path absent, and the historical-result slot unused with
target run #2 / attempt 1.

The CLI exposes only `plan`; there is no install, execute, advance, or workflow-
dispatch surface.

Workflow-install authorization, installed state, historical executor availability,
historical-result dispatch, execute mode, rerun/retry/replacement, reserved
2023-2026 access, candidate compilation/promotion, Phase 8B, demo, broker/live,
real-money, and trading remain false.

Next gate: repository-hosted read-only active workflow-installation preflight proof.
