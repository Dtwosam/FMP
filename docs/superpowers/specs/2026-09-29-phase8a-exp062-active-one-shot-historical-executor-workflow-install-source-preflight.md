# Phase 8A — EXP-062 Workflow Install Source Preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN SOURCE PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-403  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-402

DEC-403 verifies the new DEC-402 workflow-install source contract on the exact
current `main` commit.

It pins DEC-402 source identity, requires the active executor workflow path to remain
absent, confirms the historical-result slot is still unused, and preserves all six
source-only gates.

The CLI exposes only `plan`. There is no install, execute, advance, or workflow
dispatch surface.

Actual workflow-install authorization, installed state, historical executor
availability, historical-result dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

Next gate: repository-hosted read-only workflow-install source-preflight proof.
