# Phase 8A — EXP-050 Single-Step Historical Model Operator

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY OPERATOR; THIS DECISION DOES NOT DISPATCH EXP-050
**Decision:** DEC-147
**Experiment:** EXP-20260924-049

## Purpose

DEC-147 freezes a fail-closed one-way operator around the single historical EXP-050 attempt authorized by DEC-146.

The operator may expose a dispatch command only while no manual-main EXP-050 run exists. Once any such run exists, active or terminal, the operator cannot expose a second dispatch.

DEC-147 itself does not execute the dispatch command.

## Authorization chain

The operator binds:

- DEC-146 merge: `dd40df2522cf3ae9cfa5802d3d2a95a995570981`;
- execution-gate decision: `DEC-135`;
- execution-authorization decision: `DEC-146`;
- merged DEC-132 through DEC-145 identities returned by the exact source gate;
- hardened EXP-050 workflow and CLI source identities;
- DEC-145 terminal-review identity.

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

`phase8a-exp050-temporal-jackknife-utility-model-training.yml`

Workflow path:

`.github/workflows/phase8a-exp050-temporal-jackknife-utility-model-training.yml`

Workflow name:

`phase8a-exp050-temporal-jackknife-utility-model-training`

Only manual `workflow_dispatch` runs on `main` are considered.

The live run listing endpoint is fixed to branch `main`, event `workflow_dispatch`, and at most the first 100 runs. DEC-146's workflow-level first-run guard independently rejects a second run.

## One-way run state

The operator has exactly three run states:

- `MISSING`: no manual-main EXP-050 run exists;
- `IN_PROGRESS`: exactly one run exists and is not completed;
- `TERMINAL`: exactly one run exists and is completed.

More than one manual-main run is an error.

Only `MISSING` can expose:

`gh workflow run phase8a-exp050-temporal-jackknife-utility-model-training.yml --ref main -R Dtwosam/FMP`

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

`exp050-temporal-jackknife-utility-model-result-evidence-<head-sha>-from-feature-35867307338-outcome-35876715434`

The operator downloads that artifact, safely extracts it, requires exactly one `model-result-evidence.json`, loads it through the DEC-134 evidence loader against the run head SHA, and then routes the complete terminal evidence through DEC-145.

A non-success terminal run is routed through DEC-145 without aggregate evidence.

The operator does not authorize a retry or replacement.

## Source identity

Operator core:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_operator.py`

Git blob:

`d0284ff447fb0f1560a5fb42e558c8708a76de49`

Public CLI:

`scripts/phase8a_exp050_operator.py`

Git blob:

`e0b5c31793226740abf73c944e80c2ae0fb995c8`

Focused tests:

`tests/test_phase8a_exp050_operator.py`

Git blob:

`067cc3b9f6ac15f69f33b326e5395b9b49a0cf37`

## Authorization state

DEC-147 does not itself dispatch.

The operator report preserves false:

- replacement-run authorization;
- promotion authorization;
- shadow authorization;
- demo-order authorization;
- broker mutation;
- live orders;
- real-money action;
- trading authorization.

The DEC-146 outer one-run authorization remains the sole basis for a first dispatch, and only the clean-main / zero-run state may expose it.

## Next gate

After DEC-147 is merged and repository regressions pass, the operator may be run from a clean current `main`.

A read-only `next`/dry `advance` report must be inspected first. Only if it still reports the exact zero-run dispatch state may the separately guarded `advance --execute` path submit the single authorized workflow dispatch.

The first manual-main EXP-050 attempt consumes the slot regardless of terminal outcome.
