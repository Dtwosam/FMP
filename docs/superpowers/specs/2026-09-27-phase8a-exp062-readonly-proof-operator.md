# Phase 8A — EXP-062 Read-Only Gate-Proof Operator

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY READ-ONLY PLANNER / NO EXECUTE MODE  
**Decision:** DEC-302  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-301

## Purpose

DEC-302 adds the read-only planner for the proof-only EXP-062 gate run predeclared by DEC-301.

It cannot dispatch or execute the workflow.

## Exact plan behavior

The operator requires:

- exact current `main` branch metadata;
- exact caller-supplied expected main head;
- current `phase8a-exp062-discovery` workflow-run history.

If there are zero matching manual-main runs, it reports:

`EXP062_PROOF_DISPATCH_AUTHORIZATION_REQUIRED`

and exposes only:

`gh workflow run phase8a-exp062-discovery.yml --ref main`

as plan evidence.

If exactly one matching run exists, it must remain:

- workflow run number `1`;
- attempt `1`.

The operator then reports:

`EXP062_PROOF_RUN_PRESENT_REVIEW_REQUIRED`

and removes the dispatch command.

More than one matching run, workflow run-number drift, attempt drift, duplicate run ids, or main-head drift fails closed.

## Authorization boundary

DEC-302 keeps false:

- proof dispatch;
- proof execute mode;
- historical-result dispatch;
- historical discovery execution;
- discovery-result production;
- rerun/retry/replacement;
- reserved 2023-2026 access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Frozen implementation

Operator source:

`src/fmp/discovery/exp062_proof_operator.py`

Git blob:

`bc33c377ee9865766613a3ad64ddd9fd751d88fa`

Plan-only CLI:

`scripts/phase8a_exp062_proof_operator.py`

Git blob:

`1b3525d8424a83bd02f46439eeab19956686b1c9`

Focused tests:

`tests/test_phase8a_exp062_proof_operator.py`

Git blob:

`f3e1f1acc4263a534e679d254ae0b23d95365737`

## CLI surface

The CLI exposes one subcommand only:

`plan`

There is no execute, advance, dispatch, retry, rerun, or replacement mode.

## Next gate

After DEC-302 merges green, the next safe layer is a separately reviewed one-shot **proof executor**.

That executor may submit only the DEC-302 proof command, only when a fresh plan still shows zero EXP-062 manual-main runs, and must preserve the distinction between:

- proof dispatch, which consumes no historical-result slot;
- later historical-result dispatch, which remains locked.
