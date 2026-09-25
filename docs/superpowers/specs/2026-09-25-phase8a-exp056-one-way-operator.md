# Phase 8A — EXP-056 Clean-Main One-Way Operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED
**Decision:** DEC-215
**Experiment:** EXP-20260925-056

## Purpose

DEC-215 freezes a clean-main, one-way operator around the bounded DEC-214 EXP-056 historical-result slot.

The operator can inspect live workflow state and derive at most one exact next action. DEC-215 itself does not dispatch the model workflow.

## Frozen authorization binding

DEC-215 binds DEC-214 merged commit:

`9a46e2b8e708e298691d22dcda88f4865c0289bb`

The exact workflow identity is:

- file: `phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml`
- path: `.github/workflows/phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml`
- name: `phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training`

The operator validates the current execution gate as:

- workflow-source decision: DEC-212
- bounded execution-authorization decision: DEC-214
- DEC-209/210/211/212/213 merged commit identities
- DEC-212 workflow/CLI/gate blobs
- DEC-213 terminal-review blob
- current guarded EXP-056 workflow blob
- current EXP-056 model-run CLI blob

## Clean-main preflight

Before planning, the operator requires:

- local branch exactly `main`;
- local HEAD is a valid 40-character Git SHA;
- fetched `origin/main` is a valid 40-character Git SHA;
- local HEAD exactly equals fetched `origin/main`;
- clean worktree;
- origin remote resolves exactly to `Dtwosam/FMP`.

Any mismatch fails closed.

## One-way live-state classification

The operator reads only exact manual-main EXP-056 workflow runs.

It allows at most one such run.

Live state is classified as:

- `MISSING`
- `IN_PROGRESS`
- `TERMINAL`

If more than one exact manual-main run exists, planning fails closed because DEC-214 authorizes only one attempt.

## MISSING state

Only `MISSING` may expose the exact command:

`gh workflow run phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml --ref main -R Dtwosam/FMP`

The read-only plan reports:

- run dispatch authorized: true
- authoritative historical result execution authorized: true
- model-protocol result authorized: true
- model fit authorized: true
- replacement model run authorized: false
- promotion/shadow/demo/broker/live/real-money/trading: false

## IN_PROGRESS state

When the exact run already exists and is not completed:

- no dispatch command is exposed;
- all four historical-run controls become false in the plan;
- replacement remains false;
- the only safe action is inspection of the existing run.

## TERMINAL state

When the exact run is completed:

- no dispatch command is exposed;
- no replacement is authorized;
- terminal evidence routes through the frozen DEC-213 review contract;
- successful aggregate evidence is selected only by the exact expected artifact name/head SHA and validated through DEC-213.

## Double-plan execution surface

The public CLI provides:

- `next` — read-only live plan;
- `advance` — prepare the next action without execution;
- `advance --execute` — execution-capable path used only by a later separately frozen executor.

For `advance --execute`, the CLI obtains the plan once, then obtains a second independent `next` plan immediately before dispatch. The two structured plans and exact derived commands must match.

Any live-state drift fails closed before dispatch.

No rerun/retry/replacement command exists.

## Source identity

Operator source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_operator.py`

Git blob:

`de7e4134ba29c619d9d12c9f372bfee96fc1c902`

Public CLI:

`scripts/phase8a_exp056_operator.py`

Git blob:

`db626a1703cb2238948d4f832ce6e8db093880f4`

Focused tests:

`tests/test_phase8a_exp056_operator.py`

Git blob:

`e20ae3068c9d7e24c49fb0fbb8057d597db9addf`

## Downstream locks

DEC-215 does not itself dispatch the historical workflow or consume the DEC-214 slot.

It keeps false:

- replacement model run;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After DEC-215 is green and merged, the next safe gate is a repository-hosted read-only plan runner that invokes only `next`.

That proof runner must contain no dispatch path.
