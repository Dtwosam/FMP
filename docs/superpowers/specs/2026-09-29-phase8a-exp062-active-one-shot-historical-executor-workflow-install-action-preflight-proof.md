# Phase 8A — EXP-062 Workflow-Install Action Preflight Proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY PREFLIGHT PROOF / NO INSTALL OR DISPATCH  
**Decision:** DEC-419  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-417, DEC-418

DEC-419 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-418
workflow-install action preflight.

The proof pins DEC-417/418 source identities, the dormant executor template, the
active discovery workflow, and the pinned planning runtime. It requires the active
executor workflow path to remain absent, checks exact merged main and the EXP-062
run inventory, and invokes only the DEC-418 `plan` surface.

A valid proof requires all eight source-only gates true, zero historical-result
attempts, target run #2 / attempt 1, and actual workflow-install authorization,
installed state, executor availability, historical dispatch, and execute mode all
false.

The workflow has contents/actions read permissions only, no write permission, no
`workflow_dispatch` trigger, and never installs the executor workflow or submits
historical discovery.

A successful run uploads only the action-preflight JSON.

The next safe gate after real successful DEC-419 evidence is immutable proof review
and freezing before any workflow mutation.
