# Phase 8A — EXP-044 Model-Run Source Gate

**Date:** 2026-09-23
**Status:** APPROVED — SOURCE GATE ONLY; RESULT RUN STILL LOCKED
**Decision:** DEC-089
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-088 froze the first EXP-044 model-training protocol before any model-training result.

DEC-089 adds a fail-closed source gate proving that the exact merged DEC-088 protocol remains unchanged and that the verified DEC-074 preparation chain is still authoritative before model-run implementation work may begin.

DEC-089 does not fit a model and does not create a model-training workflow.

## 2. Frozen DEC-088 identity

- decision: `DEC-088`;
- version: `fmp-exp044-model-protocol-v1`;
- merged source commit: `a9305ba9c42b7224e5d4b3f7d26f268447cdf469`;
- protocol fingerprint: `1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605`.

Any protocol-fingerprint drift fails closed.

## 3. Frozen preparation evidence

- feature run `35867307338`;
- feature evidence fingerprint `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`;
- outcome run `35876715434`;
- aggregate outcome-evidence artifact `10758027876`;
- DEC-074 readiness artifact `10757578276`.

DEC-075 must first recompute `MODEL_PROTOCOL_SOURCE_OPEN` from the actual persisted feature, outcome, and readiness contents. Artifact IDs are additional frozen identities and never replace content/fingerprint validation.

## 4. New source-only stage

After both the DEC-075 evidence chain and the exact DEC-088 fingerprint validate, the operator may report `MODEL_PROTOCOL_FROZEN` with `model_protocol_frozen=true` and `model_run_source_open_authorized=true`.

This authorizes only source/design work for a later guarded model-run implementation.

## 5. Non-dispatchability

`MODEL_PROTOCOL_FROZEN` is explicitly non-dispatchable. DEC-087 `advance` must return no command for this stage even when `--execute` is supplied.

No model-training workflow file is introduced by DEC-089.

## 6. Authorization locks

DEC-089 retains `model_protocol_result_authorized=false`, `model_fit_authorized=false`, `promotion_authorized=false`, and all shadow/demo/broker/live/real-money authorization flags false.

## 7. Next gate

A later separately approved decision may implement the deterministic DEC-088 training/evidence runner and its guarded manual workflow. No result-producing fit may occur until a later decision explicitly changes the result/fit authorization state.
