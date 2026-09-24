# Phase 8A — EXP-048 Single-Step Operator Source

**Date:** 2026-09-24
**Status:** SOURCE-ONLY BEFORE ANY EXP-048 HISTORICAL MODEL RESULT
**Decision:** DEC-129
**Experiment:** EXP-20260924-048

## 1. Purpose

DEC-129 freezes the clean-main operator source that may perform the separate post-merge dispatch step authorized by DEC-128.

DEC-129 itself dispatches nothing. It does not authorize a retry/replacement, promote a candidate, start prospective shadow/demo activity, mutate a broker, place a live order, or permit real-money trading.

## 2. Predecessor boundary

DEC-129 is built after DEC-128 merged at:

`7a0d502345982fc4bb987dc34c441227a2bef5ff`

At the start of DEC-129 work GitHub still reported zero manual-main:

`phase8a-exp048-regime-consensus-model-training`

runs.

The DEC-128 workflow-internal first-run rejection guard remains an independent duplicate-execution barrier.

## 3. Frozen operator identities

Operator core:

`src/fmp/market_learning/model_successor_regime_consensus_operator.py`

Git blob:

`86789ed022c1cf3460ac724b8444f4464c6c464f`

Executable wrapper:

`scripts/phase8a_exp048_operator.py`

Git blob:

`9b6c7e5f0952f0621543b9a561987cbfc00ef2b0`

Focused tests:

`tests/test_phase8a_exp048_operator.py`

Git blob:

`3ee1a9d15f67c17ef02e9890d8d3750907d0b6e8`

DEC-129 changes no protocol, training core, artifact/evidence runner, workflow, model CLI, execution gate, runtime, historical artifacts, or DEC-127 terminal-review semantics.

## 4. Checkout preflight

The operator requires:

- local branch exactly `main`;
- fetched `origin/main`;
- local HEAD exactly equal to fetched `origin/main`;
- a clean working tree;
- `origin` exactly matching `Dtwosam/FMP`;
- working GitHub CLI authentication.

Any mismatch fails closed before planning or dispatch.

## 5. Live run inspection

The operator queries only:

`phase8a-exp048-regime-consensus-model-training.yml`

with branch `main` and event `workflow_dispatch`.

The listing may contain at most one manual-main EXP-048 run. More than one is a hard error because DEC-128 authorizes only one.

## 6. One-way state machine

When no run exists, `next` reports:

`REGIME_CONSENSUS_MODEL_RUN_DISPATCH_REQUIRED`

and exposes exactly:

`gh workflow run phase8a-exp048-regime-consensus-model-training.yml --ref main -R Dtwosam/FMP`

This is the only dispatchable state.

Once any run exists, operator dispatch authorization is consumed.

An active run reports:

`REGIME_CONSENSUS_MODEL_RUN_IN_PROGRESS`

A terminal run reports:

`REGIME_CONSENSUS_MODEL_TERMINAL_REVIEW_REQUIRED`

and is passed through DEC-127.

No active or terminal state contains a dispatch command.

## 7. Gate metadata validation

The operator validates the exact DEC-126/DEC-128 decision identities and requires valid Git identities for:

- DEC-123 through DEC-127 merged commits;
- DEC-126 pre-authorization workflow/CLI/gate blobs;
- DEC-127 review blob;
- current authorized workflow blob;
- current model CLI blob.

This preserves the fail-closed metadata repair pattern introduced after EXP-047.

## 8. Double-plan execution guard

`advance` is dry-run by default.

`advance --execute`:

1. invokes the public `next` planner;
2. verifies the report maps to the exact frozen dispatch command;
3. invokes `next` again immediately before execution;
4. requires the complete second plan to equal the first;
5. requires the reconstructed command to equal the first command;
6. only then submits one GitHub workflow dispatch.

Any checkout, authorization, workflow, or live-run-state drift aborts execution.

## 9. Terminal review integration

For a terminal run, the operator fetches exact workflow metadata, job inventory, and artifacts.

On success it requires the exact aggregate artifact tied to the run head SHA:

`exp048-regime-consensus-model-result-evidence-<HEAD_SHA>-from-feature-35867307338-outcome-35876715434`

It safely extracts exactly one `model-result-evidence.json`, revalidates it through DEC-125, then passes the complete state through DEC-127.

For non-success it supplies no aggregate evidence claim and passes exact run/jobs/artifacts through DEC-127 partial-evidence review.

## 10. No retry or bypass

DEC-129 contains no rerun command, replacement-run command, alternate workflow trigger, workflow inputs, repository-dispatch path, or push-trigger shortcut.

The first EXP-048 attempt consumes the DEC-128 slot regardless of terminal outcome.

## 11. Locks

DEC-129 keeps false:

- replacement-run authorization;
- promotion;
- prospective shadow;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization;
- trading authorization.

EXP-048 remains post-result-informed and not untouched OOS.

## 12. Next gate

After DEC-129 merges, an authenticated local operator may first run:

`python scripts/phase8a_exp048_operator.py next`

from clean current `main`.

Only if it returns `REGIME_CONSENSUS_MODEL_RUN_DISPATCH_REQUIRED` may a separate explicit:

`python scripts/phase8a_exp048_operator.py advance --execute`

submit the single guarded historical run.
