# Phase 8A — EXP-062 Repaired Adapter and Cell Evidence

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY / NON-EXECUTABLE  
**Decision:** DEC-293  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-292

## Purpose

DEC-293 implements the exact NaN-to-null adapter repair authorized by DEC-292 while preserving the failed EXP-061 adapter as immutable predecessor evidence.

## Exact repair

For each continuous feature value immediately before `FeatureObservation` construction:

- floating-point NaN becomes `None`;
- finite integers/floats are unchanged;
- positive infinity remains invalid;
- negative infinity remains invalid;
- session flags are unchanged.

No feature calculation or source artifact is modified.

## Adaptation semantics retained

The repaired adapter reuses the frozen EXP-061 implementation for:

- cell identity validation;
- required column inventory;
- feature-set and processed-manifest identity;
- UTC checks;
- observation-id construction;
- 2015-2022 input boundary;
- outcome adaptation;
- target rejection at/after 2023;
- feature/outcome observation matching;
- immutable `FeatureObservation` / `OutcomeObservation` contracts.

Therefore the only changed behavior is representation of floating-point NaN as missing/null.

## EXP-062 evidence identity

Cell evidence is first compiled through the frozen EXP-061 compiler, then wrapped with:

- experiment id `EXP-20260927-062`;
- evidence protocol `fmp-exp062-cell-evidence-v1`;
- DEC-292 repair decision/version;
- EXP-062 repair protocol fingerprint;
- semantic predecessor EXP-061 experiment/protocol fingerprint;
- exact predecessor cell-evidence fingerprint;
- `nan_to_null_adapter_repair_applied=true`;
- `positive_negative_infinity_normalization_authorized=false`.

The EXP-062 validator deterministically reconstructs the predecessor EXP-061 cell evidence and re-runs the frozen EXP-061 semantic validator. Nested pattern/search/result semantics therefore cannot drift under the wrapper.

## Frozen source bindings

DEC-293 requires:

- DEC-292 repair protocol blob `1d26da24134c825e2f405224316e1dd3136a38fb`;
- failed EXP-061 adapter blob `978a33554fad7e9d78b002778c4896be0af3333a`.

Repaired adapter/evidence source:

`src/fmp/discovery/nan_null_repair_adapter.py`

Git blob:

`53f85d99bad42decb673e9fa2ff0f771150e17db`

Focused tests:

`tests/test_phase8a_exp062_nan_null_repair_adapter.py`

Git blob:

`83a5d61527b3b8cad0cba5473ec148f1e0f343bc`

## Test guarantees

Focused tests require:

- NaN -> None;
- finite values unchanged;
- session flags unchanged;
- positive/negative infinity still fail;
- repaired feature/outcome observations preserve matching observation identity;
- EXP-062 evidence is deterministic;
- EXP-062 evidence round-trips through the frozen EXP-061 semantic validator;
- reserved robustness and every trading/downstream authorization remain false.

## Authorization state

DEC-293 authorizes only the repaired adapter/evidence source.

It keeps false:

- historical result execution;
- discovery result production;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After DEC-293 is green and merged, the next safe gate is a non-executing EXP-062 run/evidence contract defining the exact 18 cells, commit-scoped artifacts, aggregate reconstruction, and attempt-1 terminal semantics.

No workflow dispatch is authorized by DEC-293.
