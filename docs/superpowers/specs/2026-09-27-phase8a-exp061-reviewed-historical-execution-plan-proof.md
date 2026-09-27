# Phase 8A — EXP-061 Reviewed Historical Execution Plan Proof

**Date:** 2026-09-27  
**Status:** REVIEWED / RUN-2 SLOT VERIFIED AVAILABLE / DISPATCH STILL LOCKED  
**Decision:** DEC-288  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-287

## Purpose

DEC-288 freezes the exact successful merged-main read-only historical execution-plan proof produced by DEC-287.

It adds no dispatch, execute, retry, rerun, replacement, robustness, promotion, demo, live, real-money, or trading authority.

## Exact proof run

DEC-287 merged to main at:

`958a0b830bb867d1c11e2a82be7fc301a6a75474`

The repository-hosted execution-plan proof run is:

- run id: `36329787371`;
- workflow: `phase8a-exp061-historical-execution-plan`;
- path: `.github/workflows/phase8a-exp061-historical-execution-plan.yml`;
- event: `push`;
- branch: `main`;
- head: `958a0b830bb867d1c11e2a82be7fc301a6a75474`;
- workflow run number: `1`;
- attempt: `1`;
- terminal status: `completed`;
- conclusion: `success`.

Every proof step completed successfully, including exact merged-main checkout, source identity checks, clean-worktree proof, live run-inventory read, DEC-286 plan execution, run-#2 target validation, and immutable artifact upload.

## Exact proof artifact

Exactly one execution-plan proof artifact exists:

- artifact id: `10935233025`;
- name: `exp061-dec287-historical-execution-plan-958a0b830bb867d1c11e2a82be7fc301a6a75474`;
- digest: `sha256:bb81bd8f0cb1adfc0054db4f5c16f13808793c520d443a0f05a89a90f92a415d`;
- expired: `false`.

The downloaded artifact ZIP independently hashes to the same SHA-256 digest.

It contains exactly one file:

`historical-execution-plan.json`

Plan raw SHA-256:

`2ca76921e17096b444202573a950825244e07c27e0f476cecfb510ad5e0a95e5`

Plan canonical SHA-256:

`86b37433e183bfd9199822da0212b79fe11950461206335fc53e6f783210a74e`

## Frozen plan meaning

The exact plan proves:

- operator decision: `DEC-286`;
- authorization decision: `DEC-285`;
- expected head equals DEC-287 merged main;
- frozen fail-closed proof run id: `36319888985`;
- frozen fail-closed proof run count: `1`;
- frozen fail-closed proof workflow run number: `1`;
- historical-result attempt count: `0`;
- historical-result slot consumed: `false`;
- stage: `EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE`;
- expected future target workflow run number: `2`;
- expected future target run attempt: `1`;
- historical execution source authorization: `true`;
- historical discovery execution authorization inside the target runtime: `true`;
- discovery-result production authorization inside the target runtime: `true`;
- planned future command: `gh workflow run phase8a-exp061-discovery.yml --ref main`.

The command remains evidence only. DEC-288 does not execute it.

## Frozen source bindings

DEC-288 binds:

- DEC-287 proof workflow blob: `6f4b6a04291465f0f32f1f8e9276ff4a62417ec2`;
- DEC-286 historical execution operator blob: `a711b14fb613f1c9952f5b2a6bf85d892bd2c4a5`;
- DEC-286 historical execution operator CLI blob: `1f43e1218072918d2ebb33b2c312ba8e950881f9`;
- DEC-285 historical execution authorization blob: `30258e076f6a786c977fac8c588ac2b22aeed66e`;
- activated EXP-061 CLI blob: `477aa9e8de4452e6444d1ee4361218aca445180d`;
- active discovery workflow blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`.

Reviewed-proof implementation:

`src/fmp/discovery/historical_execution_plan_result_decision.py`

Git blob:

`b01ee28b7ab636cb6729423504ff8e2038ce4375`

Focused tests:

`tests/test_phase8a_exp061_reviewed_historical_execution_plan_proof.py`

Git blob:

`54b24c60063032ccae3abe6cda897031edcf24e4`

## Locks preserved

DEC-288 keeps false:

- historical-result dispatch;
- historical execute mode;
- rerun;
- retry;
- replacement;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

No historical-result slot is consumed.

## Next gate

After DEC-288 merges green, the next safe step is a separate one-shot historical executor source.

That executor must:

- bind this exact reviewed DEC-288 proof;
- re-read current main and EXP-061 run inventory immediately before dispatch;
- require the inventory still contains only proof run #1;
- require the planned target to remain workflow run #2 / attempt #1;
- submit at most one `phase8a-exp061-discovery.yml` manual-main dispatch;
- treat the first later historical run as consuming the slot immediately;
- forbid executor reruns, historical reruns, retries, and replacements;
- keep the 2023-2026 robustness block closed;
- keep candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading locked.

The historical result itself must be reviewed separately before any downstream gate opens.
