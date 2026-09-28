# Phase 8A — EXP-062 Active Workflow Install Preflight Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY ACTIVE INSTALL PREFLIGHT PROOF  
**Decision:** DEC-362  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-360, DEC-361

DEC-362 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-361
active workflow-install preflight.

The proof pins DEC-360/361, the exact dormant executor template, active discovery
workflow, and pinned planning runtime. It explicitly requires the active executor
workflow path to remain absent and invokes only the DEC-361 plan surface.

A valid proof requires zero historical-result attempts, target run #2 / attempt 1,
active install-source authorization true, and install authorization / installed
state / executor availability / dispatch / execute mode all false.

The workflow has contents/actions read permissions only, no write permission, no
workflow_dispatch trigger, and never installs or dispatches anything.

A successful run uploads only:

`active-one-shot-historical-executor-workflow-install-preflight.json`

The next safe gate after real successful DEC-362 runtime evidence is immutable proof
review and freezing before any active workflow installation can advance.
