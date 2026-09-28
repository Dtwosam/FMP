# Phase 8A — EXP-062 Read-Only Executor Activation Preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN ACTIVATION PREFLIGHT / NO EXECUTE MODE  
**Decision:** DEC-331  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-330

## Purpose

DEC-331 adds a read-only current-main preflight for the DEC-330 source-authorized
future activation of the one-shot historical executor.

It proves whether the single historical slot remains empty and whether the exact future
workflow command is still the sole target. It cannot submit that command.

## Source binding

DEC-331 pins the DEC-330 activation-contract blob:

`35edfdfed85e52ebd723f2637060f4f102e7920b`

and requires:

- one-shot executor activation source authorized: true;
- historical executor available: false;
- historical-result dispatch authorized: false;
- execute mode available: false.

## Current-main checks

A valid preflight requires exact `main` metadata and head, the frozen EXP-062 proof
as workflow run #1, zero historical-result attempts, and target run #2 / attempt 1.

While the slot is empty, the preflight may expose:

`gh workflow run phase8a-exp062-discovery.yml --ref main`

as evidence only.

If run #2 exists, the slot is immediately consumed and the command becomes null.

## Safety boundary

DEC-331 keeps false:

- historical executor availability;
- historical-result dispatch;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

## Next gate

The next safe gate is a repository-hosted **read-only executor activation-preflight
proof** on merged main. It must persist only immutable preflight evidence and must not
submit the historical workflow.
