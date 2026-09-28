# Phase 8A — EXP-062 Workflow-Install Preflight Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY INSTALL PREFLIGHT PROOF / NO INSTALL OR DISPATCH  
**Decision:** DEC-350  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-348, DEC-349

DEC-350 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-349
workflow-install preflight.

The proof pins DEC-348/349 source identities, requires the future executor workflow
path to remain absent, checks exact merged main and the EXP-062 run inventory, and
invokes only the DEC-349 plan surface.

A valid proof requires zero historical-result attempts, target run #2 / attempt 1,
install-source authorization true, and install authorization / installed state /
executor availability / dispatch / execute mode all false.

The workflow has contents/actions read permissions only, no write permission, no
workflow_dispatch trigger, and never submits historical discovery.

A successful run uploads only
`one-shot-historical-executor-workflow-install-preflight.json`.

The next safe gate after real successful DEC-350 runtime evidence is immutable proof
review and freezing before any workflow installation source can advance.
