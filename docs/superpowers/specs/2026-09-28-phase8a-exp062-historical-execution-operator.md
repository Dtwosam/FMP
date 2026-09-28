# Phase 8A — EXP-062 Historical Execution Operator

**Date:** 2026-09-28  
**Status:** READ-ONLY EXECUTION PLAN / NO EXECUTE MODE  
**Decision:** DEC-313  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-312

## Purpose

DEC-313 adds the read-only exact-main planner for the one historical execution slot
authorized by DEC-312.

It can describe the sole future dispatch command while the slot is empty. It cannot
execute the command and does not authorize dispatch.

## Preconditions

The operator independently validates DEC-312 source authorization, including the
activated EXP-062 CLI and concrete DEC-311 reviewed plan proof. It then requires:

- current branch metadata is exactly `main`;
- current main head equals the caller-supplied expected SHA;
- frozen EXP-062 gate proof remains exactly workflow run #1 / attempt 1;
- at most one later historical run exists;
- any later historical run is exactly workflow run #2 / attempt 1.

## Empty-slot behavior

While the frozen proof is the only matching manual-main discovery run, DEC-313 reports:

- stage: `EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE`;
- historical-result attempts: `0`;
- target run: #2 / attempt 1;
- plan evidence:
  `gh workflow run phase8a-exp062-discovery.yml --ref main`.

The command is evidence only.

## Present-run behavior

Once a run #2 exists, the slot is immediately treated as consumed and:

- the plan command becomes null;
- the run is routed to review;
- a second run cannot be planned.

Multiple later runs, run-number drift, reruns, proof drift, duplicate run IDs, or main
head drift fail closed.

## Authorization split

DEC-313 preserves DEC-312 runtime authorization:

- historical execution source authorized: **true**;
- historical discovery execution inside exact run #2 runtime: **true**;
- discovery-result production inside exact run #2 runtime: **true**.

But the operator itself keeps:

- historical-result dispatch authorized: **false**;
- execute mode available: **false**;
- rerun / retry / replacement: **false**;
- reserved robustness access: **false**;
- candidate compilation / promotion: **false**;
- Phase 8B / demo / broker / live / real-money / trading: **false**.

## Frozen implementation

- source: `src/fmp/discovery/exp062_historical_execution_operator.py`;
- CLI: `scripts/phase8a_exp062_historical_execution_operator.py`;
- focused tests: `tests/test_phase8a_exp062_historical_execution_operator.py`.

## Next gate

The next safe gate is a repository-hosted **read-only execution-plan proof** on merged
main. That proof may run only the DEC-313 planner, must persist only immutable plan
evidence, and must not execute the dispatch command.

A one-shot executor may be considered only after that proof is separately reviewed and
frozen.
