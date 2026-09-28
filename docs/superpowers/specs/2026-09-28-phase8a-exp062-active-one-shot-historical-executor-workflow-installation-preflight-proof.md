# Phase 8A — EXP-062 Active Workflow-Installation Preflight Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY PREFLIGHT PROOF / NO INSTALL OR DISPATCH  
**Decision:** DEC-368  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-366, DEC-367

DEC-368 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-367
active workflow-installation preflight.

The proof pins DEC-366/367, the exact dormant executor template, the active discovery
workflow, and the pinned planning runtime. It requires the active executor workflow
path to remain absent, checks exact merged main plus the EXP-062 run inventory, and
invokes only the DEC-367 plan surface.

A valid proof requires zero historical-result attempts, target run #2 / attempt 1,
installation-source authorization true, and install authorization / installed state /
executor availability / historical dispatch / execute mode all false.

The workflow has contents/actions read permissions only, no actions:write permission,
no workflow_dispatch trigger, and no install or historical dispatch command.

It uploads only
`active-one-shot-historical-executor-workflow-installation-preflight.json`.

Next gate after real successful runtime evidence: immutable installation-preflight
proof review/freeze.
