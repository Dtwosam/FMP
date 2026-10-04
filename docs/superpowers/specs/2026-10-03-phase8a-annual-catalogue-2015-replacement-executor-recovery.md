# Phase 8A — 2015 Replacement Executor Recovery

**Date:** 2026-10-03  
**Status:** ONE-SHOT RECOVERY EXECUTOR / ANNUAL RUN-2 SLOT STILL EMPTY  
**Decision:** DEC-517  
**Predecessors:** DEC-499, DEC-512, DEC-513

The original DEC-512 executor run `37149151549` failed before dispatch because its environment did not install the pinned annual-catalogue Python runtime. The target annual workflow inventory therefore still contains only failed run `37126711695` / run 1 / attempt 1.

DEC-517 is a separate recovery workflow. It does not rerun the failed executor.

A valid recovery must:
- run only once from a merged-main push touching the recovery workflow;
- verify the exact failed DEC-512 executor identity and conclusion;
- prove the annual `workflow_dispatch` inventory still contains exactly one failed run;
- install `requirements/exp061-discovery-run.txt` plus the repository package before importing DEC-499;
- rebuild DEC-499 against exact current main;
- submit exactly one 2015 replacement dispatch;
- resolve exactly annual workflow run 2 / attempt 1 at the recovery merge SHA;
- reject any run 3+;
- record dispatch only, with no result claim.

DEC-513 is rebound to require the successful DEC-517 recovery executor at the same target head before it may review/freeze/bind run 2.

No retry, rerun, 2016+ execution, promotion, broker mutation, order placement, real-money action, or trading authority is added.

## Next gate

`SUCCESSFUL_2015_REPLACEMENT_RUN_2_THEN_DEC_513_CONCRETE_BINDING`
