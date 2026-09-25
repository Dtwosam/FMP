# Phase 8A — EXP-056 Model Workflow Source Freeze

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED
**Decision:** DEC-212
**Experiment:** EXP-20260925-056

## Purpose

DEC-212 freezes the manual-main workflow, CLI, pinned numerical runtime, and exact-source execution gate for EXP-056 after DEC-211 completes the non-executable artifact/evidence contract.

The source surface exists so a later separately authorized historical run can be exact and reproducible. DEC-212 itself does not authorize or dispatch that run.

## Frozen predecessor bindings

DEC-212 binds:

- DEC-209 merge: `d2e1aabba6c0f283da6802fe315a5a29b22b503c`
- DEC-209 protocol blob: `14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d`
- DEC-210 merge: `029159999fae7eaa67811f8b3d8bf2bf8834e491`
- DEC-210 training-core blob: `c472ed48e7b79d22056d43deb0fe09166ccf34c9`
- DEC-211 merge: `193312de6d03dc8286956f7594602f67688b1d23`
- DEC-211 artifact-contract blob: `f554011c092f5c4ec5d3f9b8e2330bfc974376f8`

The protocol, training core, and artifact contract must all still expose their internal result-execution/model-fit authorizations as false.

## Workflow shape

Workflow:

`.github/workflows/phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml`

Git blob:

`83e5434c065167294b854b58308fec6d39d800db`

It is:

- `workflow_dispatch` only;
- input-free;
- manual-main only;
- read-only for contents and Actions;
- Python 3.12.14;
- pinned to `requirements/exp056-model-run.txt`;
- nine pair/timeframe datasets × two horizons;
- max-parallel 3;
- partial cell artifacts preserved with `if: always()`;
- deterministic 18-cell aggregate compilation.

The workflow has no first-run guard under DEC-212. That guard belongs to a later separate authorization decision.

## Frozen data/readiness identities

DEC-212 preserves the same accepted feature, outcome, and readiness artifact identities already used by the prior exact historical research path.

Readiness artifact:

- id: `10757578276`
- ZIP SHA-256: `d35248b0690531561818ce13ec6bf371bf31eeaf120182d75eb788417a97ffa8`

The nine feature/outcome dataset artifact ids and ZIP hashes remain frozen in the workflow matrix.

## Public CLI

CLI:

`scripts/phase8a_exp056_model_run.py`

Git blob:

`30e79ef7ef20d12d75fc97103b9411b7b467ecef`

The CLI supports:

- `status`
- `require-execution`
- `run-cell`
- `aggregate`

For every command other than `status`, the authoritative execution gate is checked before readiness loading, artifact loading, cell execution, or aggregate compilation.

The CLI contains no direct `gh workflow run` path.

## Runtime lock

Runtime requirements:

`requirements/exp056-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

The numerical runtime matches the frozen predecessor stack exactly.

## Exact-source execution gate

Gate source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_execution_gate.py`

Git blob:

`a81f746c8b19abc63f1bb83da0c32f1023644b94`

The gate binds the exact protocol/core/artifact/workflow/CLI/runtime and shared source blobs.

Under DEC-212 it reports:

- workflow source frozen: true;
- model-run dispatch authorized: false;
- authoritative historical result execution authorized: false;
- model-protocol result authorized: false;
- model fit authorized: false.

`require-execution` therefore fails closed before artifact loading.

## Focused tests

Focused tests:

`tests/test_phase8a_exp056_model_workflow.py`

Git blob:

`938f2abd2f1488affcb3ce0e7a3d64c2ec0f0165`

They verify exact source bindings, manual-main/input-free workflow shape, absence of a first-run guard, exact matrix/runtime, evidence preservation, execution-before-artifact-loading order, and closed authorizations.

## Downstream locks

DEC-212 keeps false:

- model-run dispatch;
- authoritative result execution;
- model-protocol result production;
- model fit;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

The next safe gate is a separately predeclared attempt-1 terminal-review contract.

Only after that review source is frozen may a later decision prove zero prior EXP-056 runs, add a first-run rejection guard, and consider one explicitly bounded historical-result slot.
