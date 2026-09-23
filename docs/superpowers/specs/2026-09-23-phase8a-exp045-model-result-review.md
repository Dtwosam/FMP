# Phase 8A — EXP-045 Predeclared Terminal Result Review

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT
**Decision:** DEC-100
**Experiment:** EXP-20260923-045

## 1. Purpose

DEC-099 authorizes at most one guarded historical EXP-045 model-result run.

DEC-100 predeclares how that one run must be reviewed after it reaches a terminal state. This source is frozen before any EXP-045 result exists so success/failure handling cannot be rewritten around the observed outcome.

DEC-100 does not dispatch the workflow and does not authorize a replacement run, promotion, prospective shadow admission, demo orders, broker mutation, live orders, real-money trading, or trading.

## 2. Reviewed workflow identity

The only reviewable workflow is:

`.github/workflows/phase8a-exp045-model-training.yml`

with workflow name:

`phase8a-exp045-model-training`

A reviewable run must be:

- `workflow_dispatch`;
- on branch `main`;
- attempt `1`;
- terminal with status `completed`;
- tied to a valid 40-character Git commit.

Any rerun attempt is rejected.

## 3. Exact job inventory

The terminal review requires exactly 11 jobs:

- one `authorization-preflight`;
- nine `model-cells (...)` matrix jobs;
- one `aggregate-model-evidence`.

Every reviewed job must itself be terminal.

Unexpected or duplicated job identities fail closed.

## 4. Exact artifact namespace

The only accepted pair/timeframe artifacts are the nine names:

`exp045-model-cell-results-<SYMBOL>-<TIMEFRAME>-<HEAD_SHA>`

for:

- EURUSD 5m/15m/1h;
- GBPUSD 5m/15m/1h;
- USDJPY 5m/15m/1h.

The only accepted aggregate artifact is:

`exp045-model-result-evidence-<HEAD_SHA>-from-feature-35867307338-outcome-35876715434`

Artifacts must be non-expired, unique, and from that exact namespace.

## 5. Successful-run review

A successful workflow requires:

- authorization preflight success;
- all nine matrix jobs success;
- aggregate job success;
- all nine cell artifacts;
- exactly one aggregate artifact;
- aggregate evidence supplied to the reviewer.

The aggregate evidence is revalidated with the frozen DEC-097 validator against the exact workflow head SHA.

A successful historical result stops at:

`SUCCESSOR_MODEL_RESULT_REVIEW_REQUIRED`

It does not promote anything.

## 6. Non-success terminal review

The predeclared non-success conclusions are:

- `failure`;
- `cancelled`;
- `timed_out`.

A non-success run may preserve any valid subset of pair/timeframe artifacts.

It may not claim aggregate result evidence or an aggregate result artifact.

The aggregate job must be terminal as skipped, failed, or cancelled.

The review reports the number of successful, failed, cancelled, and skipped matrix jobs and stops at:

`SUCCESSOR_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

No replacement model run is authorized.

## 7. Evidence interpretation

All EXP-045 evidence remains:

- post-result-informed;
- retrospective;
- not untouched OOS;
- not prospective evidence.

Partial evidence is preserved as review evidence only.

A complete aggregate result is still not prospective proof.

## 8. Locks

DEC-100 keeps the following false:

- replacement model run authorization;
- promotion;
- shadow admission;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization;
- trading authorization.

## 9. Next action

The already-authorized single EXP-045 workflow may still be dispatched only through the separate DEC-099 post-merge gate.

DEC-100 changes no workflow, CLI, execution-gate, protocol, training-core, artifact-runner, runtime, feature, outcome, or historical-data bytes.

After the one run terminates, its exact GitHub run metadata, job inventory, artifact listing, and aggregate evidence if present must be passed through this frozen review contract before any later decision.
