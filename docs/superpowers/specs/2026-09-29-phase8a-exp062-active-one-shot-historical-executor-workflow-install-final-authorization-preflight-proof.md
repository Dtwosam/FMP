# Phase 8A — EXP-062 Final Workflow-Install Authorization Preflight Proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY PREFLIGHT PROOF / NO INSTALL OR DISPATCH  
**Decision:** DEC-413  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-411, DEC-412

DEC-413 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-412
final workflow-install authorization preflight.

The proof pins DEC-411/412 source identities, the dormant executor template, the
active discovery workflow, and the pinned planning runtime. It requires the active
executor workflow path to remain absent, checks exact merged main plus the EXP-062
run inventory, and invokes only the DEC-412 `plan` surface.

A valid proof requires all seven source-only gates true, zero historical-result
attempts, target run #2 / attempt 1, and actual workflow-install authorization,
installed state, executor availability, historical dispatch, and execute mode all
false.

The workflow has contents/actions read permissions only and uploads only the final
authorization-preflight JSON.

The next safe gate after real successful DEC-413 runtime evidence is immutable proof
review and freezing before any installation mutation can advance.
