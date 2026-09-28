# Phase 8A — EXP-062 One-Shot Historical Executor Workflow Preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN WORKFLOW PREFLIGHT / NO EXECUTE MODE  
**Decision:** DEC-343  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-342

## Purpose

DEC-343 adds a read-only current-main preflight for the DEC-342 source-authorized
future one-shot historical executor workflow.

The preflight proves whether the sole historical-result slot remains empty and whether
target run #2 / attempt 1 is still exact. It may expose the frozen historical workflow
command as evidence only; it cannot submit it.

## Source binding

DEC-343 pins the DEC-342 workflow-contract blob:

`d87bf8f4fc3ad8fc081760c1250dc0f8dc9ffadc`

and requires:

- one-shot executor workflow source authorization: true;
- historical executor available: false;
- historical-result dispatch authorized: false;
- execute mode available: false.

## Current-main checks

A valid preflight requires exact `main` metadata and head, the frozen EXP-062 gate
proof as discovery run #1, zero historical-result attempts, and target run #2 /
attempt 1.

While the slot is empty, the preflight may expose:

`gh workflow run phase8a-exp062-discovery.yml --ref main`

as data only.

If run #2 exists, the slot is consumed immediately and the command becomes null.

## Safety boundary

DEC-343 keeps false:

- historical executor availability;
- historical-result dispatch;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

## Next gate

The next safe gate is a repository-hosted read-only proof of this workflow preflight.
