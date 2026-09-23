# Phase 8A — EXP-046 Single-Step Operator Source

**Date:** 2026-09-23
**Status:** SOURCE-ONLY BEFORE ANY EXP-046 HISTORICAL MODEL RESULT
**Decision:** DEC-110
**Experiment:** EXP-20260923-046

## 1. Purpose

DEC-110 freezes the local operator source that may perform the separate post-merge dispatch step authorized by DEC-109.

DEC-110 does not dispatch EXP-046, create a model result, authorize a retry/replacement, promote a candidate, start prospective shadow/demo activity, mutate a broker, place a live order, or permit real-money trading.

## 2. Predecessor boundary

DEC-110 is built after DEC-109 merged at:

`f134ebeac12a0e7f6d085a7fdcec291999ff30d6`

At the start of DEC-110 work GitHub still reported zero manual-main:

`phase8a-exp046-stability-model-training`

runs.

The DEC-109 workflow-internal first-run guard remains an independent second barrier against duplicate execution.

## 3. Frozen operator identities

Operator core:

`src/fmp/market_learning/model_successor_stability_operator.py`

Git blob:

`c3fbe7591307592fe4e05cc783549524bddafad8`

Executable wrapper:

`scripts/phase8a_exp046_operator.py`

Git blob:

`de942c5703dfddcc3b277387de98572bbe9bf562`

Focused tests:

`tests/test_phase8a_exp046_operator.py`

Git blob:

`245dd27a3b0f7cff5106708fe1803980f96700ed`

DEC-110 changes no protocol, model core, artifact/evidence runner, workflow, model CLI, execution gate, runtime, historical artifacts, or DEC-108 review semantics.

## 4. Checkout preflight

The operator requires:

- local branch `main`;
- fetched `origin/main`;
- local HEAD exactly equal to fetched `origin/main`;
- a clean working tree;
- `origin` exactly matching `Dtwosam/FMP`;
- working GitHub CLI authentication.

Any mismatch fails closed before planning or dispatch.

## 5. Live run inspection

The operator queries only:

`phase8a-exp046-stability-model-training.yml`

with:

- branch `main`;
- event `workflow_dispatch`.

The listing may contain at most one manual-main EXP-046 run.

More than one is a hard error because DEC-109 authorizes only one.

## 6. One-way operator state machine

When no run exists, `next` reports:

`STABILITY_MODEL_RUN_DISPATCH_REQUIRED`

and exposes exactly:

`gh workflow run phase8a-exp046-stability-model-training.yml --ref main -R Dtwosam/FMP`

This is the only dispatchable state.

Once any run exists, operator dispatch authorization is consumed.

An active run reports:

`STABILITY_MODEL_RUN_IN_PROGRESS`

A terminal run first reports the terminal-review boundary and is then passed through the frozen DEC-108 review contract.

No active or terminal state contains a dispatch command.

## 7. Double-plan execution guard

`advance` is dry-run by default.

`advance --execute`:

1. invokes the public `next` planner;
2. verifies the report maps to the exact frozen dispatch command;
3. invokes `next` again immediately before execution;
4. requires the complete second plan to equal the first;
5. requires the reconstructed command to equal the first command;
6. only then submits one GitHub workflow dispatch.

Any checkout, authorization, workflow, or live-run-state drift between the two plans aborts execution.

## 8. Terminal review integration

For a terminal run, the operator fetches:

- exact workflow run metadata;
- complete job inventory;
- artifact listing.

On success it requires the exact aggregate artifact tied to the run head SHA, safely extracts exactly one `model-result-evidence.json`, revalidates it through the DEC-106 evidence validator, then passes the complete state through DEC-108.

For non-success, it supplies no aggregate evidence claim and passes the exact run/jobs/artifacts through DEC-108 partial-evidence review.

## 9. No retry or bypass

DEC-110 contains:

- no rerun command;
- no replacement-run command;
- no alternate workflow trigger;
- no workflow inputs;
- no repository-dispatch path;
- no push-trigger shortcut.

The first EXP-046 attempt consumes the DEC-109 slot regardless of terminal outcome.

## 10. Locks

DEC-110 keeps false:

- replacement-run authorization;
- promotion;
- prospective shadow;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization;
- trading authorization.

EXP-046 remains post-result-informed and not untouched OOS.

## 11. Next gate

After DEC-110 merges, an authenticated local operator may first run:

`python scripts/phase8a_exp046_operator.py next`

from clean current `main`.

Only if it returns `STABILITY_MODEL_RUN_DISPATCH_REQUIRED` may a separate explicit:

`python scripts/phase8a_exp046_operator.py advance --execute`

submit the single guarded historical run.
