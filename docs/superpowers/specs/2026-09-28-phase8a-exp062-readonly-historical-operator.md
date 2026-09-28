# Phase 8A — EXP-062 Read-Only Historical Slot Operator

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY READ-ONLY PLANNER / NO EXECUTE MODE  
**Decision:** DEC-308  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-307

## Purpose

DEC-308 provides a clean-main read-only operator for the single DEC-307
source-authorized EXP-062 historical-result slot.

It can show the exact future GitHub CLI dispatch command as plan evidence only. It has
no execute mode and grants no dispatch authority.

## Inputs

The operator requires:

- current `main` branch metadata;
- current EXP-062 discovery workflow-run inventory;
- caller-supplied expected main head SHA.

The actual `main` commit must exactly equal the expected head or the operator fails
closed.

## Empty-slot behavior

When the exact DEC-306 frozen proof is the only matching manual-main EXP-062 run,
DEC-307 classifies the historical slot as available. DEC-308 returns:

- stage `EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE`;
- zero historical-result attempts;
- slot not consumed;
- plan evidence:
  `gh workflow run phase8a-exp062-discovery.yml --ref main`.

The command is evidence of what a later, separately authorized executor could submit.
DEC-308 itself cannot submit it.

## Consumed-slot behavior

Once any valid run #2 / attempt 1 exists, the operator returns
`EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED`, marks the slot consumed, and
sets `planned_dispatch_command=null`.

It cannot plan a second historical run.

## Safety boundary

The following remain false:

- historical-result dispatch;
- execute mode;
- historical discovery execution;
- discovery-result production;
- rerun/retry/replacement;
- reserved 2023-2026 access;
- candidate compilation/promotion;
- Phase 8B;
- demo/broker/live/real-money/trading.

The next safe gate is a repository-hosted read-only proof of the exact merged-main
DEC-308 slot-available plan. That proof must not dispatch the historical workflow.
