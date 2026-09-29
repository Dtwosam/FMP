# Phase 8A — EXP-062 Workflow Install Source Preflight Proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY SOURCE PREFLIGHT PROOF / NO INSTALL OR DISPATCH  
**Decision:** DEC-404  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-402, DEC-403

DEC-404 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-403
workflow-install source preflight.

The proof pins exact DEC-402/403 source identities, the dormant executor template,
the active discovery workflow, and the pinned planning runtime. It requires the
active executor workflow path to remain absent, checks exact merged main and the
EXP-062 run inventory, and invokes only the DEC-403 `plan` surface.

A valid proof requires all six source-only gates true, zero historical-result
attempts, target run #2 / attempt 1, and actual workflow-install authorization,
installed state, historical executor availability, historical-result dispatch, and
execute mode all false.

The workflow has contents/actions read permissions only, no write permission, no
`workflow_dispatch` trigger, and never submits historical discovery.

A successful run uploads only
`active-one-shot-historical-executor-workflow-install-source-preflight.json`.

The next safe gate after real successful DEC-404 runtime evidence is immutable proof
review and freezing before any actual workflow installation can advance.
