# Phase 8A — EXP-062 Workflow Install-Activation Preflight Proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY INSTALL-ACTIVATION PROOF  
**Decision:** DEC-398  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-396, DEC-397

DEC-398 adds a push-to-main, first-run/attempt-1 proof of the DEC-397 workflow
install-activation preflight.

It pins DEC-396/397 source identities, the dormant executor template, active
discovery workflow, and planning runtime. It requires the active executor workflow
path to remain absent, checks exact merged main plus the EXP-062 run inventory, and
invokes only the DEC-397 `plan` surface.

A valid proof requires all five source-only gates true, zero historical-result
attempts, target run #2 / attempt 1, while actual workflow-install authorization,
installed state, executor availability, historical-result dispatch, and execute mode
remain false.

The workflow has contents/actions read permissions only, no write permission, no
`workflow_dispatch` trigger, and uploads only the activation-preflight JSON.

Next gate after real success: immutable activation-preflight proof review/freeze.
