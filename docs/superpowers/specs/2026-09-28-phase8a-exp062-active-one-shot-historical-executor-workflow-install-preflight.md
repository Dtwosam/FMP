# Phase 8A — EXP-062 Active Executor Workflow Install Preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN ACTIVE INSTALL PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-361  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-360

DEC-361 adds a read-only current-main preflight for the source-authorized future
active one-shot historical executor workflow installation.

A valid preflight requires:

- exact current `main` and requested head;
- exact DEC-360 active install contract source;
- exact dormant executor template source;
- the active executor workflow path remains absent;
- the frozen EXP-062 proof remains the only historical-discovery run;
- zero historical-result attempts;
- target run #2 / attempt 1;
- active install-source authorization true;
- install authorization false;
- workflow installed false;
- executor availability false;
- historical dispatch false;
- execute mode false.

The CLI exposes only `plan`; it has no install, execute, advance, or workflow-dispatch
surface.

Rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is a repository-hosted read-only proof of this active workflow
install preflight.
