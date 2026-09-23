# Phase 8A — EXP-045 Single-Step Operator Source

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT
**Decision:** DEC-101
**Experiment:** EXP-20260923-045

## 1. Purpose

DEC-099 authorizes at most one guarded historical EXP-045 model-result run.

DEC-100 predeclares terminal review for that run before any result exists.

DEC-101 freezes the local operator source that may perform the separate post-merge dispatch step required by DEC-099.

DEC-101 is source-only. It does not dispatch the workflow, create a model result, authorize a retry, promote a candidate, open prospective shadow/demo activity, mutate a broker, place a live order, or permit real-money trading.

## 2. Frozen predecessor state

DEC-099 authorization merged at:

`d5ab9b96fa055c30a4607840f5a9f032c5353a11`

DEC-100 terminal-review source merged at:

`974127deef7ed2e5e745efc80da0336544a70a7d`

Before DEC-101 source work, GitHub still reported zero manual-main runs of:

`phase8a-exp045-model-training`

The authenticated desktop runner remained offline, so no dispatch occurred while this operator source was prepared.

## 3. Frozen operator identities

The EXP-045 operator core is:

`src/fmp/market_learning/model_successor_operator.py`

with Git blob:

`dcb391c53182ec9775015273983d3e131248adcf`

The executable wrapper is:

`scripts/phase8a_exp045_operator.py`

with Git blob:

`01d41a454df7653d58514cd1b9e129c9288e1709`

DEC-101 changes no EXP-045 workflow, model CLI, execution-gate, protocol, training-core, artifact-runner, runtime, feature, outcome, or historical-data bytes.

## 4. Checkout preflight

The operator requires:

- local branch `main`;
- fetched `origin/main`;
- local HEAD exactly equal to fetched `origin/main`;
- a clean working tree;
- `origin` exactly matching `Dtwosam/FMP`;
- working GitHub CLI authentication.

Any mismatch fails closed before planning or dispatch.

## 5. Live workflow inspection

The operator queries only:

`phase8a-exp045-model-training.yml`

for:

- branch `main`;
- event `workflow_dispatch`.

The run listing must contain at most one manual-main EXP-045 run.

If more than one exists, the operator fails closed because DEC-099 authorizes only one.

## 6. One-way state machine

When no run exists, `next` reports:

`SUCCESSOR_MODEL_RUN_DISPATCH_REQUIRED`

with exactly:

`gh workflow run phase8a-exp045-model-training.yml --ref main -R Dtwosam/FMP`

This is the only dispatchable state.

Once a run exists, dispatch authorization is consumed at the operator layer.

An active run reports:

`SUCCESSOR_MODEL_RUN_IN_PROGRESS`

A terminal run first reports the terminal-review boundary and is then passed through the frozen DEC-100 review contract.

No in-progress or terminal state contains a dispatch command.

## 7. Double-plan execution guard

`advance` is dry-run by default.

`advance --execute`:

1. invokes the public `next` planner;
2. verifies the report maps to the exact frozen dispatch command;
3. invokes `next` again immediately before execution;
4. requires the second complete plan to equal the first;
5. requires the reconstructed command to equal the first command;
6. only then submits the one GitHub workflow dispatch.

Any repository, authorization, or workflow-state drift between the two plans aborts execution.

## 8. Terminal review integration

For a terminal run, the operator fetches the exact:

- workflow run metadata;
- job inventory;
- artifact listing.

For a successful run it additionally requires the exact aggregate artifact name tied to the workflow head SHA, downloads the artifact ZIP, safely extracts exactly one `model-result-evidence.json`, and revalidates it through the frozen DEC-097 evidence validator.

The complete terminal state is then passed through DEC-100.

A non-success run does not download or claim aggregate result evidence.

## 9. No retry or bypass

DEC-101 introduces:

- no rerun command;
- no replacement-run command;
- no alternate workflow trigger;
- no workflow inputs;
- no repository-dispatch path;
- no push-trigger shortcut.

The existing workflow-internal DEC-099 prior-run guard remains the second independent barrier against a duplicate run.

## 10. Locks

DEC-101 keeps false:

- replacement model-run authorization;
- promotion;
- prospective shadow admission;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization;
- trading authorization.

EXP-045 remains explicitly post-result-informed, retrospective, and not untouched OOS.

## 11. Next gate

After DEC-101 merges, the authenticated operator may be run only from clean current `main`.

If `next` still reports `SUCCESSOR_MODEL_RUN_DISPATCH_REQUIRED`, a separate explicit `advance --execute` may submit exactly one guarded historical EXP-045 workflow.

If any run already exists, no new run may be dispatched.
