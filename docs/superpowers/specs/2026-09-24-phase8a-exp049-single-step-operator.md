# Phase 8A — EXP-049 Single-Step Historical Model Operator

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY OPERATOR; THIS DECISION DOES NOT DISPATCH EXP-049
**Decision:** DEC-138
**Experiment:** EXP-20260924-049

## Purpose

DEC-138 freezes a fail-closed one-way operator around the single historical EXP-049 attempt authorized by DEC-137.

The operator may expose a dispatch command only while no manual-main EXP-049 run exists. Once any such run exists, active or terminal, the operator cannot expose a second dispatch.

DEC-138 itself does not execute the dispatch command.

## Authorization chain

The operator binds:

- DEC-137 merge: `33227b25cd1a888c3e0c7db3a50bd0cb61f5aad6`;
- execution-gate decision: `DEC-135`;
- execution-authorization decision: `DEC-137`;
- merged DEC-132 through DEC-136 identities returned by the exact source gate;
- hardened EXP-049 workflow and CLI source identities;
- DEC-136 terminal-review identity.

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

`phase8a-exp049-regime-utility-model-training.yml`

Workflow path:

`.github/workflows/phase8a-exp049-regime-utility-model-training.yml`

Workflow name:

`phase8a-exp049-regime-utility-model-training`

Only manual `workflow_dispatch` runs on `main` are considered.

The live run listing endpoint is fixed to branch `main`, event `workflow_dispatch`, and at most the first 100 runs. DEC-137's workflow-level first-run guard independently rejects a second run.

## One-way run state

The operator has exactly three run states:

- `MISSING`: no manual-main EXP-049 run exists;
- `IN_PROGRESS`: exactly one run exists and is not completed;
- `TERMINAL`: exactly one run exists and is completed.

More than one manual-main run is an error.

Only `MISSING` can expose:

`gh workflow run phase8a-exp049-regime-utility-model-training.yml --ref main -R Dtwosam/FMP`

`IN_PROGRESS` and `TERMINAL` expose no dispatch command and set outer result/fit/dispatch permissions false in the operator report.

## Read-only planning and double-check execution

The public CLI exposes:

- `next`: read live state and emit the single next action;
- `advance`: emit the same plan without dispatch by default;
- `advance --execute`: dispatch only when the live plan is dispatchable.

Before `advance --execute` runs the frozen dispatch command, it invokes the public `next` path a second time.

If the confirmed report differs byte-for-byte in parsed JSON meaning from the first plan, execution stops.

No rerun command exists.

## Terminal review

For a terminal run, the operator fetches:

- exact run metadata;
- all workflow jobs;
- workflow artifacts.

A successful run must expose exactly one non-expired aggregate artifact named:

`exp049-regime-utility-model-result-evidence-<head-sha>-from-feature-35867307338-outcome-35876715434`

The operator downloads that artifact, safely extracts it, requires exactly one `model-result-evidence.json`, loads it through the DEC-134 evidence loader against the run head SHA, and then routes the complete terminal evidence through DEC-136.

A non-success terminal run is routed through DEC-136 without aggregate evidence.

The operator does not authorize a retry or replacement.

## Source identity

Operator core:

`src/fmp/market_learning/model_successor_regime_utility_operator.py`

Git blob:

`f523ff3e2353c0c347e136f9a998a2b1434a561b`

Public CLI:

`scripts/phase8a_exp049_operator.py`

Git blob:

`9f1c3881e45322e5dda267bc7adaff1c86317ec2`

Focused tests:

`tests/test_phase8a_exp049_operator.py`

Git blob:

`ec73bb478c62966edfeb066d43b871511642574b`

## Authorization state

DEC-138 does not itself dispatch.

The operator report preserves false:

- replacement-run authorization;
- promotion authorization;
- shadow authorization;
- demo-order authorization;
- broker mutation;
- live orders;
- real-money action;
- trading authorization.

The DEC-137 outer one-run authorization remains the sole basis for a first dispatch, and only the clean-main / zero-run state may expose it.

## Next gate

After DEC-138 is merged and repository regressions pass, the operator may be run from a clean current `main`.

A read-only `next`/dry `advance` report must be inspected first. Only if it still reports the exact zero-run dispatch state may the separately guarded `advance --execute` path submit the single authorized workflow dispatch.

The first manual-main EXP-049 attempt consumes the slot regardless of terminal outcome.
