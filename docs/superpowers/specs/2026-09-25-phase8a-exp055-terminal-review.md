# Phase 8A — EXP-055 Predeclared Terminal Review

**Date:** 2026-09-25
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED
**Decision:** DEC-202
**Experiment:** EXP-20260925-055

## Purpose

DEC-202 predeclares the exact terminal review for any later separately authorized first EXP-055 historical model-result attempt.

The review exists before any first-run authorization. DEC-202 does not dispatch a workflow, open a historical run slot, fit a model, or authorize result production.

## Frozen workflow bindings

DEC-202 binds merged DEC-201:

`a5825ec8008cbb9bf9783b15135faed1d7f5fb73`

and exact DEC-201 source identities:

- workflow blob: `da5b498deb7c8d15993eaeb686127f138ce9f161`
- CLI blob: `41eeb09fe0730f5184e71a9f7413a3bc5f568e63`
- execution-gate blob: `e252f0550ca1c0bdc2ea16d32bc0b6a854b1c39c`

The reviewed workflow must be exactly:

`phase8a-exp055-fit-temporal-residual-breadth-utility-model-training`

at:

`.github/workflows/phase8a-exp055-fit-temporal-residual-breadth-utility-model-training.yml`

on branch `main`, event `workflow_dispatch`, attempt 1.

## Exact terminal job inventory

Terminal review requires exactly 11 completed workflow jobs:

- one `authorization-preflight`
- nine `model-cells (...)` jobs
- one `aggregate-model-evidence`

No rerun attempt is accepted.

## Successful terminal review

A successful run requires:

- preflight success
- all nine matrix jobs success
- aggregate job success
- all nine expected pair/timeframe cell artifacts present
- the one exact aggregate artifact present
- every artifact non-expired
- aggregate evidence supplied to the review
- deterministic recompilation under DEC-200 equal byte-for-structure to the supplied aggregate evidence

The aggregate revalidation therefore proves:

- 18 cells
- 108 regressors
- 108 pooled calibration references
- 432 fit-temporal utility-support references
- 216 fit-temporal feature-support references
- 432 fit-temporal residual references
- 12 residual-breadth lower-bound comparisons per eligible scored row
- the exact DEC-200 evidence fingerprint

A successful workflow does not itself authorize promotion or trading.

## Terminal non-success review

Accepted terminal non-success conclusions are:

- failure
- cancelled
- timed_out

A non-success may preserve only cell artifacts actually produced.

It may not claim:

- an aggregate artifact
- aggregate result evidence
- a rerun
- a retry
- a replacement run

The review records preflight/matrix terminal counts for diagnosis only.

## Artifact naming

Expected cell artifacts are exactly:

`exp055-fit-temporal-residual-breadth-utility-model-cell-results-<symbol>-<timeframe>-<head_sha>`

for the nine frozen pair/timeframe datasets.

The aggregate artifact is exactly:

`exp055-fit-temporal-residual-breadth-utility-model-result-evidence-<head_sha>-from-feature-35867307338-outcome-35876715434`

Unexpected or duplicate artifacts fail closed.

## Source identity

Terminal-review source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_result_review.py`

Git blob:

`341d228b2521441c7d4b32d92349bc001cc78a91`

Focused tests:

`tests/test_phase8a_exp055_model_result_review.py`

Git blob:

`37cf99ae72c5e444d077c98c8e2f8d8221c9b8c3`

## Authorization state

DEC-202 keeps false:

- model-run dispatch
- replacement model run
- authoritative historical result execution
- model-protocol result production
- model fitting
- promotion
- shadow execution
- demo orders
- broker mutation
- live orders
- real-money action
- trading

## Next gate

Only after DEC-202 is green and merged may a separate decision verify that zero prior manual-main EXP-055 model runs exist, add a first-run rejection guard, and consider opening exactly one bounded outer historical-result slot.

The first attempt, if later authorized, must consume the slot on any terminal outcome and route through this review.