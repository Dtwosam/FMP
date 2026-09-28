# Phase 8A — EXP-062 Install-Authorization Preflight Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY AUTHORIZATION PREFLIGHT PROOF / NO INSTALL OR DISPATCH  
**Decision:** DEC-374  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-372, DEC-373

DEC-374 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-373
install-authorization preflight.

The proof pins DEC-372/373 source identities, the dormant executor template, the
active discovery workflow, and the pinned planning runtime. It requires the active
executor workflow path to remain absent, checks exact merged main and the EXP-062 run
inventory, and invokes only the DEC-373 plan surface.

A valid proof requires zero historical-result attempts, target run #2 / attempt 1,
install-authorization source authorization true, and actual install authorization /
installed state / executor availability / dispatch / execute mode all false.

The workflow has contents/actions read permissions only, no write permission, no
workflow_dispatch trigger, and never submits historical discovery.

A successful run uploads only
`active-one-shot-historical-executor-workflow-install-authorization-preflight.json`.

The next safe gate after real successful DEC-374 runtime evidence is immutable proof
review and freezing before any actual workflow-install authorization can advance.
