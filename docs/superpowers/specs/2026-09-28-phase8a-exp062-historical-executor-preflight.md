# Phase 8A — EXP-062 Read-Only Historical Executor Preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO EXECUTE MODE  
**Decision:** DEC-325  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-324

## Purpose

DEC-325 adds a read-only current-main preflight for the source-authorized future
one-shot historical executor.

It proves whether the one historical slot remains empty and whether the exact future
dispatch command is still the only admissible target. It cannot submit that command.

## Source binding

DEC-325 pins the DEC-324 executor-contract source blob:

`12d514e86a2b458dd692810450e69b30f554a6bd`

and requires:

- one-shot executor source contract authorized: true;
- historical executor available: false;
- historical-result dispatch authorized: false;
- execute mode available: false.

## Current-main checks

A valid preflight requires:

- branch metadata exactly `main`;
- current main SHA equals the supplied expected head;
- the frozen EXP-062 proof remains the exact workflow run #1;
- zero historical-result attempts for the slot-available state;
- target run #2 / attempt 1.

While the slot is empty, the preflight may expose
`gh workflow run phase8a-exp062-discovery.yml --ref main` as evidence only.

If run #2 exists, the slot is immediately consumed and the command becomes null.

## Safety boundary

DEC-325 keeps false:

- historical executor availability;
- historical-result dispatch;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 robustness access;
- candidate compilation / promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Implementation

- source: `src/fmp/discovery/exp062_historical_executor_preflight.py`;
- CLI: `scripts/phase8a_exp062_historical_executor_preflight.py`;
- tests: `tests/test_phase8a_exp062_historical_executor_preflight.py`.

The CLI has only a `plan` subcommand.

## Next gate

The next safe gate is a repository-hosted **read-only executor-preflight proof** on
merged main. It must persist only immutable preflight evidence and must not submit the
historical workflow.
