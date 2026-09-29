# Phase 8A — EXP-062 Install-Decision Preflight Proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY DECISION PREFLIGHT PROOF / NO INSTALL OR DISPATCH  
**Decision:** DEC-380  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-378, DEC-379

DEC-380 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-379
install-decision preflight.

The proof pins DEC-378/379 source identities, the dormant executor template, the
active discovery workflow, and the pinned planning runtime. It requires the active
executor workflow path to remain absent, checks exact merged main and the EXP-062 run
inventory, and invokes only the DEC-379 `plan` surface.

A valid proof requires zero historical-result attempts, target run #2 / attempt 1,
install-authorization source and install-decision source authorization true, while
actual install authorization / installed state / executor availability / dispatch /
execute mode all remain false.

The workflow has contents/actions read permissions only, no write permission, no
`workflow_dispatch` trigger, and never submits historical discovery.

A successful run uploads only
`active-one-shot-historical-executor-workflow-install-decision-preflight.json`.

The next safe gate after real successful DEC-380 runtime evidence is immutable proof
review and freezing before any actual workflow installation can advance.
