# Phase 8A — EXP-051 Single-Step Historical Model Operator

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY OPERATOR; THIS DECISION DOES NOT DISPATCH EXP-051
**Decision:** DEC-156
**Experiment:** EXP-20260924-051

## Purpose

DEC-156 freezes a fail-closed one-way operator around the single historical EXP-051 attempt authorized by DEC-155.

The operator may expose a dispatch command only while no manual-main EXP-051 run exists. Once any such run exists, active or terminal, the operator cannot expose a second dispatch.

DEC-156 itself does not execute the dispatch command.

## Authorization chain

The operator binds:

- DEC-155 merge: `a8b6204faccf411fd489ca5a1d004d90ed75be33`;
- execution-gate decision: `DEC-153`;
- execution-authorization decision: `DEC-155`;
- merged DEC-150 through DEC-154 identities returned by the exact source gate;
- hardened EXP-051 workflow and CLI source identities;
- DEC-154 terminal-review identity.

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

`phase8a-exp051-temporal-calibrated-utility-model-training.yml`

Workflow path:

`.github/workflows/phase8a-exp051-temporal-calibrated-utility-model-training.yml`

Workflow name:

`phase8a-exp051-temporal-calibrated-utility-model-training`

Only manual `workflow_dispatch` runs on `main` are considered.

The live run listing endpoint is fixed to branch `main`, event `workflow_dispatch`, and at most the first 100 runs. DEC-155's workflow-level first-run guard independently rejects a second run.

## One-way run state

The operator has exactly three run states:

- `MISSING`: no manual-main EXP-051 run exists;
- `IN_PROGRESS`: exactly one run exists and is not completed;
- `TERMINAL`: exactly one run exists and is completed.

More than one manual-main run is an error.

Only `MISSING` can expose:

`gh workflow run phase8a-exp051-temporal-calibrated-utility-model-training.yml --ref main -R Dtwosam/FMP`

`IN_PROGRESS` and `TERMINAL` expose no dispatch command and set outer result/fit/dispatch permissions false in the operator report.

## Read-only planning and double-check execution

The public CLI exposes:

- `next`: read live state and emit the single next action;
- `advance`: emit the same plan without dispatch by default;
- `advance --execute`: dispatch only when the live plan is dispatchable.

Before `advance --execute` runs the frozen dispatch command, it invokes the public `next` path a second time.

If the confirmed report differs from the first parsed JSON plan, execution stops.

No rerun command exists.

## Terminal review

For a terminal run, the operator fetches:

- exact run metadata;
- all workflow jobs;
- workflow artifacts.

A successful run must expose exactly one non-expired aggregate artifact named:

`exp051-temporal-calibrated-utility-model-result-evidence-<head-sha>-from-feature-35867307338-outcome-35876715434`

The operator downloads that artifact, safely extracts it, requires exactly one `model-result-evidence.json`, loads it through the DEC-152 evidence loader against the run head SHA, and then routes the complete terminal evidence through DEC-154.

A non-success terminal run is routed through DEC-154 without aggregate evidence.

The operator does not authorize a retry or replacement.

## Source identity

Operator core:

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_operator.py`

Git blob:

`de021a9cde4bd7c995ccb95e340df883c692d9dd`

Public CLI:

`scripts/phase8a_exp051_operator.py`

Git blob:

`bdf798e7db33917c3432f2e153c0eba563ab7ce3`

Focused tests:

`tests/test_phase8a_exp051_operator.py`

Git blob:

`47dc36184e3088322c1f983112781c3ec330d865`

## Authorization state

DEC-156 does not itself dispatch.

The operator report preserves false:

- replacement-run authorization;
- promotion authorization;
- shadow authorization;
- demo-order authorization;
- broker mutation;
- live orders;
- real-money action;
- trading authorization.

The DEC-155 outer one-run authorization remains the sole basis for a first dispatch, and only the clean-main / zero-run state may expose it.

## Next gate

After DEC-156 is merged and repository regressions pass, the operator may be run from a clean current `main`.

A read-only `next`/dry `advance` report must be inspected first. Only if it still reports the exact zero-run dispatch state may the separately guarded `advance --execute` path submit the single authorized workflow dispatch.

The first manual-main EXP-051 attempt consumes the slot regardless of terminal outcome.
