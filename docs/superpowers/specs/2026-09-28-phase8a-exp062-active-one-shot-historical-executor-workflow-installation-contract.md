# Phase 8A — EXP-062 Active One-Shot Historical Executor Workflow-Installation Contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY INSTALLATION CONTRACT / ACTIVE WORKFLOW STILL ABSENT  
**Decision:** DEC-366  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-365

DEC-366 pins the concrete DEC-365 runtime freeze and the exact dormant executor
workflow template, then authorizes only the active workflow-installation **source
contract**.

The active workflow path remains:

`.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`

and must remain absent under this decision.

DEC-366 sets only:

`active_one_shot_historical_executor_workflow_installation_source_authorized = true`

It keeps false:

- workflow-install authorization;
- workflow installed state;
- historical executor availability;
- historical-result dispatch authorization;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future historical attempt.

Next gate: read-only current-main active workflow-installation preflight.
