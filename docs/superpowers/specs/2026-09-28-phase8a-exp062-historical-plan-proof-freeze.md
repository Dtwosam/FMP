# Phase 8A — EXP-062 Historical Plan Proof Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE READ-ONLY PLAN PROOF FROZEN / HISTORICAL EXECUTION STILL LOCKED  
**Decision:** DEC-311  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-306, DEC-307, DEC-308, DEC-309, DEC-310

## Purpose

DEC-311 binds the actual successful DEC-309 read-only historical-plan proof to exact
GitHub runtime identities and independently verified artifact/plan hashes.

It does not dispatch the EXP-062 discovery workflow and does not authorize historical
execution. It closes the evidence-binding gate required by DEC-310 before a separate
source-only historical execution authorization may be considered.

## Frozen runtime evidence

The DEC-309 plan proof is frozen as:

- merged head: `95c193343a905acd40daf0eea5d27d55fd2537e1`;
- workflow: `phase8a-exp062-historical-plan`;
- run id: `36403342301`;
- run number / attempt: `1 / 1`;
- conclusion: `success`;
- sole job id: `108866149073`;
- job: `read-only-historical-plan`, success;
- sole artifact id: `10960559187`;
- artifact name:
  `exp062-dec309-historical-plan-95c193343a905acd40daf0eea5d27d55fd2537e1`;
- GitHub artifact digest:
  `sha256:07679d85ea3ee0a9373bbd78363ab98eb973377ace6d68828528f91188ff3cf8`;
- independently recomputed artifact ZIP SHA-256:
  `07679d85ea3ee0a9373bbd78363ab98eb973377ace6d68828528f91188ff3cf8`.

The artifact contains exactly the read-only `historical-plan.json` evidence produced
by DEC-309.

## Frozen plan identities

The downloaded plan is bound by:

- raw JSON SHA-256:
  `ac34769d589dbcc18a056d1ebaf960b6881f943f221d771e80216df32d313672`;
- canonical JSON SHA-256:
  `d6cd04c0c29a2e82da12e687ce56ae80387f7ad3c9727b23018ee548684e62a6`.

DEC-311 re-runs DEC-310 review against the supplied raw run/job/artifact/plan evidence
before accepting these identities.

The plan proves:

- DEC-308 operator / DEC-307 source authorization;
- frozen gate-proof run `36358289723` remains the only EXP-062 discovery run;
- historical-result attempt count is zero;
- the one source-authorized historical-result slot remains unconsumed;
- the future command
  `gh workflow run phase8a-exp062-discovery.yml --ref main`
  exists as frozen plan evidence only.

## Source binding

DEC-311 pins the merged DEC-310 reviewer source:

- DEC-310 merge:
  `243833543b9c76d4e51ca6b554cbdda4f5aa1a53`;
- DEC-310 reviewer blob:
  `5c8870c10e86122342bb181cb5a15ebc709924ce`.

DEC-310 in turn pins DEC-309/308/307/306 source identities.

## Safety boundary

The freeze keeps all of the following false:

- historical-result dispatch;
- historical execute mode;
- historical discovery execution;
- discovery-result production;
- rerun / retry / replacement;
- reserved 2023-2026 robustness access;
- candidate compilation / promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

The historical-result slot is verified available, but it is not executable under
DEC-311.

## Next gate

The next safe gate is a separate **source-only historical execution authorization
contract**. That contract may define the exact future run #2 / attempt 1 runtime
identity and execution-gate semantics, but it must still provide no dispatch path.

A later read-only execution-plan proof must precede any one-shot dispatcher.
