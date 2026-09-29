# Phase 8A — EXP-062 Install-Execution Authorization Preflight Proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY EXECUTION-AUTHORIZATION PREFLIGHT PROOF / NO INSTALL OR DISPATCH  
**Decision:** DEC-386  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-384, DEC-385

DEC-386 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-385
install-execution authorization preflight.

The proof pins DEC-384/385 source identities, the dormant executor template, the
active discovery workflow, and the pinned planning runtime. It requires the active
executor workflow path to remain absent, checks exact merged main and the EXP-062 run
inventory, and invokes only the DEC-385 `plan` surface.

A valid proof requires zero historical-result attempts, target run #2 / attempt 1,
all three source-only gates true, and actual install authorization / installed state /
executor availability / dispatch / execute mode all false.

The workflow has contents/actions read permissions only, no write permission, no
`workflow_dispatch` trigger, and never installs the executor workflow or submits
historical discovery.

A successful run uploads only
`active-one-shot-historical-executor-workflow-install-execution-authorization-preflight.json`.

The next safe gate after real successful DEC-386 runtime evidence is immutable proof
review and freezing before any actual workflow installation can advance.
