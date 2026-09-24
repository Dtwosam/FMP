# Phase 8A — EXP-047 Single-Step Operator Source

**Date:** 2026-09-24
**Status:** SOURCE-ONLY BEFORE ANY EXP-047 HISTORICAL MODEL RESULT
**Decision:** DEC-119
**Experiment:** EXP-20260924-047

## 1. Purpose

DEC-119 freezes the clean-main operator source that may perform the separate post-merge dispatch step authorized by DEC-118.

DEC-119 itself dispatches nothing. It does not authorize a retry/replacement, promote a candidate, start prospective shadow/demo activity, mutate a broker, place a live order, or permit real-money trading.

## 2. Predecessor boundary

DEC-119 is built after DEC-118 merged at:

`3009cc2df570201ab744dbeb7594bbe7d514feeb`

At the start of DEC-119 work GitHub still reported zero manual-main:

`phase8a-exp047-density-model-training`

runs.

The DEC-118 workflow-internal first-run rejection guard remains an independent duplicate-execution barrier.

## 3. Frozen operator identities

Operator core:

`src/fmp/market_learning/model_successor_density_operator.py`

Git blob:

`fb809b541f4b6f2805746f54c6c2073bc9aadb0a`

Executable wrapper:

`scripts/phase8a_exp047_operator.py`

Git blob:

`1ac82196c1bd2cd1eb8c7edbce23deea55829ed0`

Focused tests:

`tests/test_phase8a_exp047_operator.py`

Git blob:

`9aa937f3edfaf7ce452db3a38e726c4e92154446`

DEC-119 changes no protocol, model core, artifact/evidence runner, workflow, model CLI, execution gate, runtime, historical artifacts, or DEC-117 terminal-review semantics.

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

`phase8a-exp047-density-model-training.yml`

with branch `main` and event `workflow_dispatch`.

The listing may contain at most one manual-main EXP-047 run. More than one is a hard error because DEC-118 authorizes only one.

## 6. One-way state machine

When no run exists, `next` reports:

`DENSITY_MODEL_RUN_DISPATCH_REQUIRED`

and exposes exactly:

`gh workflow run phase8a-exp047-density-model-training.yml --ref main -R Dtwosam/FMP`

This is the only dispatchable state.

Once any run exists, operator dispatch authorization is consumed.

An active run reports:

`DENSITY_MODEL_RUN_IN_PROGRESS`

A terminal run reports the terminal-review boundary and is passed through DEC-117.

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

Any checkout, authorization, workflow, or live-run-state drift aborts execution.

## 8. Terminal review integration

For a terminal run, the operator fetches exact workflow metadata, job inventory, and artifacts.

On success it requires the exact aggregate artifact tied to the run head SHA:

`exp047-density-model-result-evidence-<HEAD_SHA>-from-feature-35867307338-outcome-35876715434`

It safely extracts exactly one `model-result-evidence.json`, revalidates it through DEC-115, then passes the complete state through DEC-117.

For non-success it supplies no aggregate evidence claim and passes exact run/jobs/artifacts through DEC-117 partial-evidence review.

## 9. No retry or bypass

DEC-119 contains no rerun command, replacement-run command, alternate workflow trigger, workflow inputs, repository-dispatch path, or push-trigger shortcut.

The first EXP-047 attempt consumes the DEC-118 slot regardless of terminal outcome.

## 10. Locks

DEC-119 keeps false:

- replacement-run authorization;
- promotion;
- prospective shadow;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization;
- trading authorization.

EXP-047 remains post-result-informed and not untouched OOS.

## 11. Next gate

After DEC-119 merges, an authenticated local operator may first run:

`python scripts/phase8a_exp047_operator.py next`

from clean current `main`.

Only if it returns `DENSITY_MODEL_RUN_DISPATCH_REQUIRED` may a separate explicit:

`python scripts/phase8a_exp047_operator.py advance --execute`

submit the single guarded historical run.
