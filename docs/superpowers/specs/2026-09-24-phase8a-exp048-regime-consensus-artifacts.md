# Phase 8A — EXP-048 Regime-Consensus Artifact/Evidence Contract

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; AUTHORITATIVE EXP-048 RESULT EXECUTION CLOSED
**Decision:** DEC-125
**Experiment:** EXP-20260924-048

## 1. Purpose

DEC-125 freezes the artifact-backed historical-data runner and deterministic aggregate-evidence contract around merged DEC-123/DEC-124.

The contract remains non-executable for authoritative EXP-048 model fitting.

## 2. Frozen source bindings

DEC-125 binds:

- DEC-123 merge: `39674f482e57922ac61fb0a6dff15a5ef621efd3`
- DEC-123 protocol blob: `39b6b3f5adc7f34ffd8cebcf881138d6ca3eab84`
- DEC-124 merge: `83c5b40eebae884cda9b2b65a8494dcd63bcbb7a`
- DEC-124 training-core blob: `d902f9601ef3b04e0deaead18951d43350cb09be`
- historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`
- base training-core blob: `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`
- unchanged EXP-047 density-helper core blob: `8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`

Any byte drift fails closed.

## 3. Historical artifact identity

The runner reuses only the exact already accepted EXP-044 feature/outcome/readiness artifacts:

- feature run: `35867307338`
- feature evidence artifact: `10753455784`
- outcome run: `35876715434`
- outcome evidence artifact: `10758027876`
- readiness artifact: `10757578276`

The existing authoritative cell loader remains responsible for exact manifest, schema, symbol/timeframe, and source-artifact verification.

## 4. Cell-result validation

Every one of the 18 exact model cells must revalidate before aggregate evidence compilation.

DEC-125 requires:

- exact EXP-048 protocol/training identities;
- exact historical processed-manifest identity;
- exact split row-count inventory;
- exactly three regime models;
- exact regime names: 2015-2016, 2017-2018, 2019-2020;
- one fit attempt per regime;
- all three target classes present in every regime fit;
- exact preprocessor and model SHA-256 fingerprints for every regime;
- full-fit fallback explicitly forbidden with zero attempts;
- logistic regression explicitly excluded with zero attempts;
- valid deterministic cell-result fingerprint.

## 5. Consensus validation

Selection and any unlocked forward split must carry:

- exact row count;
- LONG/SHORT/NO_TRADE consensus counts summing to the row count;
- consensus-eligible count equal to LONG+SHORT;
- exact consensus-eligible rate;
- valid min/max consensus confidence when eligible rows exist;
- no confidence bounds when no eligible rows exist;
- exactly three regime probability digests;
- valid consensus digest.

Every selection budget variant must report the same consensus-eligible selection-row count.

## 6. Density/stability variant validation

Exactly three budget variants are required: 250, 500, 1000.

Unavailable variants must:

- use `UNAVAILABLE_INSUFFICIENT_CONSENSUS_ROWS`;
- contain fewer eligible consensus rows than the nominal budget;
- contain no cutoff;
- fail aggregate/final selection gates;
- contain no stability windows.

Available variants must:

- have at least the nominal budget of eligible consensus rows;
- preserve cutoff-tie expansion;
- provide the exact 0.5-pip selection scenario;
- have financial-gate criteria recomputed by DEC-125;
- reconcile selected-at-cutoff count with financial candidate count;
- preserve the unchanged aggregate gate.

Only aggregate passes may contain the exact four stability windows. DEC-125 recomputes the 10% candidate-share and positive-financial-sign criteria for every window.

## 7. Deterministic winner

A selected cell must identify the exact deterministic winner among all stable-passing variants:

1. higher 0.5-pip total net pips;
2. higher directional candidate count;
3. smaller candidate-budget anchor.

A no-challenger status is invalid if any stable-passing variant exists.

## 8. Forward status chain

A selected variant must reuse its exact budget and exact numeric cutoff on validation and retrospective holdout.

Validation and unlocked holdout must contain exactly the 0.2, 0.5, and 1.0 scenarios.

DEC-125 recomputes each financial gate.

Validation passes only if both 0.5 and 1.0 scenarios pass.

Retrospective holdout remains locked unless validation passes.

No-selection cells must keep both forward stages locked.

## 9. Aggregate evidence

Aggregate evidence requires all 18 exact cells and preserves:

- code commit;
- protocol/core/runner identities;
- exact source-data run/artifact/fingerprint identities;
- every cell result fingerprint;
- every regime model fingerprint;
- consensus-eligible selection-row count;
- selection/validation/holdout statuses;
- aggregate/stability/unavailable-budget accounting;
- all downstream authorization locks.

The aggregate evidence receives a canonical SHA-256 fingerprint over its complete unsigned JSON object.

## 10. Source identity

Implementation:

`src/fmp/market_learning/model_successor_regime_consensus_artifacts.py`

Git blob:

`b62f3ff775f30c96fa2f6f1a15256fd696ea5c2e`

Runner version:

`fmp-exp048-regime-consensus-artifact-runner-v1`

Runner decision:

`DEC-125`

Focused tests:

`tests/test_phase8a_exp048_regime_consensus_artifacts.py`

Git blob:

`16a58dcc577952a9bf5bedf3f2e48bea38f679bc`

## 11. Authorization state

DEC-125 keeps false:

- authoritative EXP-048 model-result execution;
- model-fit authorization;
- model-protocol result production;
- workflow/dispatch authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

The authoritative bundle raises `PermissionError` before readiness validation, artifact loading, or model fitting.

## 12. Next gate

A later separate decision may freeze a manual-main, input-free EXP-048 workflow/CLI/runtime and exact-source execution gate around merged DEC-123/DEC-124/DEC-125.

No workflow dispatch or historical result execution is authorized by DEC-125.
