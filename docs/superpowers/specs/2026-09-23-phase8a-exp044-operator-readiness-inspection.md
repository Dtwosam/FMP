# Phase 8A — EXP-044 Operator Readiness Inspection

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 MODEL-TRAINING RESULT  
**Decision:** DEC-083  
**Experiment:** EXP-20260923-044

## 1. Purpose

After the EXP-044 outcome workflow eventually completes, the next legitimate state is not model fitting.

The outcome workflow must first produce and bind:

- aggregate feature evidence;
- aggregate outcome evidence;
- DEC-074 training readiness.

DEC-083 adds a read-only operator inspection mode that verifies those artifacts together and reports protocol-source-open only when the existing DEC-075 execution-status machine independently recomputes the full chain.

## 2. Operator interface

The DEC-081/082 helper gains:

`python scripts/phase8a_exp044_operator.py readiness --feature-run-id <id> --outcome-run-id <id>`

This mode performs no workflow dispatch and has no `--execute` option.

## 3. Feature side

The readiness inspection:

1. verifies the exact successful feature workflow run;
2. requires the exact non-expired aggregate feature-evidence artifact;
3. fingerprint-validates the complete feature evidence;
4. cross-binds the evidence code commit to the feature-run head SHA.

## 4. Outcome run

The exact outcome-run ID must identify:

- `phase8a-exp044-market-outcomes`;
- the exact outcome workflow path;
- a manual `workflow_dispatch`;
- `main`;
- completed status;
- successful conclusion;
- a valid 40-character head SHA.

## 5. Outcome artifacts

For the exact feature SHA and outcome SHA, the outcome run must contain exactly one non-expired artifact of each form:

- `exp044-market-outcome-evidence-<outcome SHA>-from-<feature SHA>`;
- `exp044-market-learning-readiness-<outcome SHA>-from-<feature SHA>`.

Both artifacts are downloaded and safely extracted to temporary storage.

The operator requires exactly one `outcome-evidence.json` and exactly one `readiness.json`.

## 6. Full-chain validation

The existing EXP-044 loaders validate the outcome-evidence and readiness fingerprints/contracts.

The operator then calls the DEC-075 execution-status builder with:

- feature run;
- feature evidence;
- outcome run;
- outcome evidence;
- readiness.

DEC-075 rebuilds the readiness artifact from the supplied feature/outcome evidence and requires exact equality.

It additionally cross-binds:

- feature evidence commit to feature-run SHA;
- outcome evidence commit to outcome-run SHA;
- outcome evidence feature fingerprint to feature evidence;
- readiness feature/outcome fingerprints;
- readiness feature/outcome commits.

## 7. Only accepted state

The operator inspection succeeds only if the recomputed execution state is exactly:

`MODEL_PROTOCOL_SOURCE_OPEN`

The report retains:

- `model_protocol_source_open_authorized=true`;
- `model_protocol_result_authorized=false`;
- `model_fit_authorized=false`;
- `promotion_authorized=false`;
- trading authorization false.

If any link is missing, expired, malformed, contradictory, or differently bound, the inspection fails closed.

## 8. Authorization boundary

`MODEL_PROTOCOL_SOURCE_OPEN` means only that source work may begin on a separately predeclared model-training protocol.

It does not authorize:

- choosing a model after seeing results;
- fitting a model;
- evaluating model results;
- strategy/model promotion;
- shadow/demo trading;
- broker mutation;
- live orders;
- real-money trading.

## 9. Next gate

Until the real feature and outcome workflows exist and this inspection verifies their evidence chain, the project remains at EXP-044 historical data preparation.

After a verified `MODEL_PROTOCOL_SOURCE_OPEN` state, the next source task is to draft and freeze a separate model-training protocol before any fit occurs.
