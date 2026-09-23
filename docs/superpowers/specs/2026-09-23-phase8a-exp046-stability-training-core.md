# Phase 8A — EXP-046 Temporal-Stability Training Core

**Date:** 2026-09-23
**Status:** SOURCE-ONLY; NO EXP-046 HISTORICAL RESULT AUTHORIZED
**Decision:** DEC-105
**Experiment:** EXP-20260923-046

## 1. Purpose

DEC-105 implements the deterministic in-memory training/evaluation core for the DEC-104 temporal-stability protocol.

It changes no frozen model family, model configuration, feature, target, chronology, confidence threshold, minimum-candidate floor, validation scenario, holdout scenario, or logistic non-convergence policy.

DEC-105 creates no artifact-backed authoritative result, workflow, CLI, dispatch path, model promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading authorization.

## 2. Exact predecessor bindings

DEC-105 binds:

- DEC-104 merge commit: `bb2ee82a7d081138e1c0847e8c406d6c3ac68589`
- DEC-104 protocol source blob: `4c8da2259f1fd6d27862a50a47a0d8108b58bc2e`
- DEC-096 successor training-core blob: `3f0bc1bfa9640d08175e72cdf131bb97c94d562c`

The DEC-104 protocol source is revalidated before any later authoritative use of this core.

## 3. Frozen fit and scoring mechanics

For each of the existing 18 model cells, DEC-105 reuses the predecessor mechanics:

1. validate exact feature/outcome identities and join;
2. construct the unchanged fit, selection, validation, and retrospective-holdout splits;
3. require all three target classes in fit;
4. fit each frozen model family at most once;
5. preserve the DEC-095 logistic non-convergence family-level failure policy;
6. score the full 2021-2022 selection split exactly once per fitted family;
7. preserve the resulting probability matrix, row identities, classification diagnostics, and probability digest.

No temporal-stability window triggers refitting, re-preprocessing, or rescoring.

## 4. Aggregate selection gate

For every fitted family and every frozen confidence threshold (0.50, 0.60, 0.70), DEC-105 first evaluates the unchanged full-selection 0.5-pip gate.

The aggregate requirements remain:

- directional candidate count >= 250;
- total net pips > 0;
- mean net pips > 0;
- gross positive pips > absolute gross negative pips.

If the aggregate gate fails, temporal-stability evaluation is locked for that variant and the variant is not selection-eligible.

## 5. Temporal-stability implementation

Only an aggregate-gate-passing variant is evaluated in the four DEC-104 windows.

For each window, DEC-105:

- selects rows using the same chronology rule:
  - `available_at_utc >= start`;
  - `available_at_utc < end_exclusive`;
  - `exit_timestamp_utc < end_exclusive`;
- slices the already-produced full-selection probability matrix at the exact same row indices;
- reuses the same frozen threshold;
- calculates the same 0.5-pip financial metrics;
- calculates directional-candidate share as:
  - window directional candidate count / full-selection directional candidate count.

A stability window passes when:

- directional-candidate share >= 0.10;
- total net pips > 0;
- mean net pips > 0;
- gross positive pips > absolute gross negative pips.

The 250-candidate minimum is **not** re-applied to each six-month window. It remains an aggregate selection gate exactly as DEC-104 specifies.

All four windows must pass.

## 6. Selection semantics

DEC-105 records separately:

- `aggregate_selection_gate_passed`;
- complete temporal-stability window evidence;
- final `selection_gate_passed`.

Final selection eligibility is:

`aggregate_selection_gate_passed AND temporal_stability.status == PASS`

Only final stability-qualified variants enter the unchanged predecessor tie-break.

If fitted families exist but no final stability-qualified variant exists, the cell selection status is:

`NO_STABLE_MODEL_CHALLENGER`

If every family is unavailable, the predecessor:

`NO_MODEL_FAMILY_AVAILABLE`

semantics are preserved.

## 7. Validation and retrospective holdout

If a stability-qualified variant is selected, DEC-105 evaluates it with no refit using the unchanged predecessor:

- validation split and scenarios;
- validation pass/reject semantics;
- retrospective holdout lock;
- retrospective holdout scenarios.

A validation reject still prevents retrospective-holdout evaluation.

## 8. Deterministic result evidence

The source-only cell result records:

- EXP-046 experiment/protocol/core identities;
- exact predecessor source identities;
- fit-family status;
- selection diagnostics and probability digests;
- aggregate gate evidence;
- all temporal-stability window metrics and gates;
- selected variant identity, if any;
- validation/holdout evidence, if unlocked;
- deterministic result fingerprint;
- post-result-informed / not-untouched-OOS labels;
- all downstream execution locks.

## 9. Source identity

Training-core source:

`src/fmp/market_learning/model_successor_stability_training.py`

Git blob:

`6733d3c530fba944b9ea0c62783ed2110552e532`

Version:

`fmp-exp046-stability-training-core-v1`

Decision:

`DEC-105`

Focused tests:

`tests/test_phase8a_exp046_stability_training.py`

Git blob:

`cea8efeba7d0fd8cebc75845f1f6cf90b54fc004`

## 10. Authorization boundary

DEC-105 keeps false:

- authoritative EXP-046 training-result execution;
- model fit authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

The in-memory core may be exercised only by synthetic/unit-test fixtures under DEC-105 source validation. No authoritative persisted market-history result is authorized.

## 11. Next gate

A later separate decision may freeze an EXP-046 artifact-backed runner/evidence contract around the merged DEC-104/DEC-105 source.

That later source must remain non-executable until another separate authorization decision.
