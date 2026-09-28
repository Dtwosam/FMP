# Phase 8A — EXP-062 Read-Only One-Shot Dispatch Operator

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN PLAN / NO EXECUTE MODE  
**Decision:** DEC-319  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-318

## Purpose

DEC-319 adds a read-only current-main planner for the future one-shot historical
dispatch contract authorized by DEC-318.

It can expose the exact discovery command as evidence only while the slot remains
empty. It cannot execute the command.

## Source binding

DEC-319 pins the DEC-318 dispatch-authorization source blob:

`b5360751459212cfabb37a3dd7758fe0cc28c4a6`

and requires:

- one-shot dispatch source contract authorized: true;
- actual historical-result dispatch authorized: false;
- historical executor available: false.

## Current-main checks

A valid plan requires:

- branch metadata exactly `main`;
- current main SHA equals the supplied expected head;
- frozen proof remains the exact EXP-062 discovery run #1;
- zero later historical attempts for the available state.

If a historical run #2 already exists, the slot is immediately treated as consumed
and the command becomes null.

## Available-slot output

While the slot is empty DEC-319 reports:

- stage `EXP062_ONE_SHOT_DISPATCH_SLOT_AVAILABLE`;
- target run #2 / attempt 1;
- command evidence:
  `gh workflow run phase8a-exp062-discovery.yml --ref main`;
- source dispatch contract: true;
- actual dispatch authorization: false;
- executor available: false;
- execute mode available: false.

## Consumed-slot output

If the one historical attempt exists:

- stage becomes
  `EXP062_ONE_SHOT_DISPATCH_SLOT_CONSUMED_REVIEW_REQUIRED`;
- the command is null;
- a second dispatch cannot be planned.

Multiple attempts, duplicate inventory, main-head drift, or authority escalation fail
closed.

## Implementation

- source: `src/fmp/discovery/exp062_historical_dispatch_operator.py`;
- CLI: `scripts/phase8a_exp062_historical_dispatch_operator.py`;
- tests: `tests/test_phase8a_exp062_historical_dispatch_operator.py`.

The CLI has only a `plan` subcommand.

## Next gate

The next safe gate is a repository-hosted **read-only dispatch-plan proof** on merged
main. It must run only DEC-319 planning, persist only plan evidence, and must not
submit the discovery workflow.
