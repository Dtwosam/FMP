# Phase 8A — EXP-052 Single-Step Historical Model Operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY OPERATOR; THIS DECISION DOES NOT DISPATCH EXP-052
**Decision:** DEC-169
**Experiment:** EXP-20260925-052

## Purpose

DEC-169 freezes a fail-closed one-way operator around the single historical EXP-052 attempt authorized by DEC-168.

The operator may expose a dispatch command only while no manual-main EXP-052 run exists. Once any such run exists, active or terminal, it cannot expose a second dispatch.

DEC-169 itself does not execute the dispatch command.

## Authorization chain

The operator binds:

- DEC-168 merge: `673b96906002b898dd09ff913a0efe6b9be369e3`;
- execution-gate decision: `DEC-166`;
- execution-authorization decision: `DEC-168`;
- merged DEC-163 through DEC-167 source metadata returned by the exact source gate;
- hardened EXP-052 workflow and CLI identities;
- DEC-167 terminal-review identity.

The operator never relaxes promotion, shadow/demo, broker mutation, live-order, real-money, or trading locks.

## Clean-main checkout gate

Before reporting or dispatching, the public operator CLI must:

- fetch `origin/main`;
- require local branch `main`;
- require local HEAD exactly equals fetched `origin/main`;
- require an empty porcelain working-tree status;
- require `origin` to identify exactly `Dtwosam/FMP`.

Any mismatch fails closed.

## Exact workflow identity

Workflow file:

`phase8a-exp052-fit-temporal-support-utility-model-training.yml`

Workflow path:

`.github/workflows/phase8a-exp052-fit-temporal-support-utility-model-training.yml`

Workflow name:

`phase8a-exp052-fit-temporal-support-utility-model-training`

Only manual `workflow_dispatch` runs on `main` are considered.

The live run listing endpoint is fixed to branch `main`, event `workflow_dispatch`, and at most the first 100 runs. DEC-168's workflow-level first-run guard independently rejects a second run.

## One-way run state

The operator has exactly three states:

- `MISSING`: no manual-main EXP-052 run exists;
- `IN_PROGRESS`: exactly one run exists and is not completed;
- `TERMINAL`: exactly one run exists and is completed.

More than one manual-main run is an error.

Only `MISSING` can expose:

`gh workflow run phase8a-exp052-fit-temporal-support-utility-model-training.yml --ref main -R Dtwosam/FMP`

`IN_PROGRESS` and `TERMINAL` expose no dispatch command and set outer result/fit/dispatch permissions false in the operator report.

## Read-only planning and double-check execution

The public CLI exposes:

- `next`: inspect live EXP-052 state and emit the single next action;
- `advance`: emit the same plan without dispatch by default;
- `advance --execute`: dispatch only when the live plan is dispatchable.

Before `advance --execute` runs the frozen dispatch command, it invokes the public `next` path a second time.

If the confirmed report differs from the first parsed JSON plan, execution stops.

No rerun command exists.

## Terminal review

For a terminal run, the operator fetches exact run metadata, all jobs, and all workflow artifacts.

A successful run must expose exactly one non-expired aggregate artifact named:

`exp052-fit-temporal-support-utility-model-result-evidence-<head-sha>-from-feature-35867307338-outcome-35876715434`

The operator downloads that artifact, safely extracts exactly one `model-result-evidence.json`, loads it through the DEC-165 evidence loader against the run head SHA, and routes the complete terminal evidence through DEC-167.

A non-success terminal run is routed through DEC-167 without aggregate evidence.

The operator does not authorize a retry or replacement.

## Source identity

Operator core:

`src/fmp/market_learning/model_successor_fit_temporal_support_utility_operator.py`

Git blob:

`9e57fa87215d8e7ca373d226f8e2fec873a0fd10`

Public CLI:

`scripts/phase8a_exp052_operator.py`

Git blob:

`1c4c212e3bcc16c1e241efeb9ef5986d0bc5b24d`

Focused tests:

`tests/test_phase8a_exp052_operator.py`

Git blob:

`9550f0126c4fe959d0ad979a096c03bcbc9f0199`

## Authorization state

DEC-169 does not itself dispatch.

The operator report preserves false:

- replacement-run authorization;
- promotion authorization;
- shadow authorization;
- demo-order authorization;
- broker mutation;
- live orders;
- real-money action;
- trading authorization.

The DEC-168 outer one-run authorization remains the sole basis for a first dispatch, and only the clean-main / zero-run state may expose it.

## Next gate

After DEC-169 is merged and repository regressions pass, the operator may be run from a clean current `main`.

A read-only `next`/dry `advance` report must be inspected first. Only if it still reports the exact zero-run dispatch state may a separately guarded execution path submit the single authorized workflow attempt.

The first manual-main EXP-052 attempt consumes the slot regardless of terminal outcome.
