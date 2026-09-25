# Phase 8A — EXP-056 Implementation-Failure Diagnostic

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC
**Decision:** DEC-219
**Experiment:** EXP-20260925-056

## Purpose

DEC-219 explains why the sole EXP-056 historical attempt failed before producing any model evidence.

It does not reinterpret the failed run as a model-selection result and does not reopen the consumed EXP-056 slot.

## Frozen bindings

DEC-219 binds:

- DEC-218 merge: `2f2171f0166f22c19482a905d6906d1cfd672275`
- DEC-218 result-decision blob: `75fc25ae97c03730ab75a3036059f761d8234630`
- EXP-056 training-core blob: `c472ed48e7b79d22056d43deb0fe09166ccf34c9`
- EXP-055 predecessor training-core blob: `c9517b7516940c78621448088c3933aa1c57e281`
- EXP-054 base training-core blob: `4f3f189c104d41352433397421f021896c03a5e9`

The reviewed failed run remains `36175841645`.

## Diagnostic method

The diagnostic parses the frozen Python sources with the Python AST.

It inventories every direct attribute dereference from the EXP-056 core against:

- `_predecessor` — the EXP-055 residual-breadth training module;
- `_base` — the frozen EXP-054 residual-bound training module.

It independently inventories the top-level names actually exported by the frozen predecessor and base sources.

No model data, selection outcomes, validation outcomes, holdout outcomes, or external market information enters this diagnostic.

## Exact implementation defect

The EXP-056 lower-tail core correctly defines:

`_base = _predecessor._predecessor`

but seven inherited EXP-054 constants/rules are dereferenced from the intermediate EXP-055 module instead of from `_base`.

The exact seven invalid `_predecessor` accesses are:

1. `FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE`
2. `FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL`
3. `FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL`
4. `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`
5. `MIN_STABILITY_WINDOW_CANDIDATE_SHARE`
6. `ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE`
7. `ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE`

All seven names are present on the frozen EXP-054 `_base` module.

The historical attempt directly observed two of these missing exports:

- `MIN_STABILITY_WINDOW_CANDIDATE_SHARE`
- `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`

The other five are latent invalid dereferences that the failed run did not reach.

## Classification

DEC-219 classifies the failure as:

`EXP056_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_INTERMEDIATE_PREDECESSOR_EXPORT_DRIFT`

This is an implementation dependency-boundary defect.

It is not a change in:

- protocol semantics;
- model family;
- feature inputs;
- target construction;
- chronology;
- lower-tail definition;
- residual breadth;
- residual-bound utility;
- candidate budgets;
- financial gates;
- temporal-stability gates;
- validation;
- retrospective holdout.

## Exact repair boundary

A future successor implementation may repair only the seven invalid accesses:

`_predecessor.<name> -> _base.<name>`

for the seven names listed above.

Legitimate EXP-055 breadth-specific accesses must remain on `_predecessor`.

No protocol math, model configuration, ranking, cutoff, gate, chronology, data identity, or forward-evaluation rule may change under this repair.

## Authorization state

DEC-219 keeps false:

- EXP-056 rerun;
- EXP-056 replacement run;
- successor model fit;
- successor historical result execution;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

It opens only:

- successor protocol source design.

The successor must use a new experiment identity because the EXP-056 historical slot is already consumed.

## Source identity

Diagnostic source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_failure_diagnostics.py`

Git blob:

`d94fb02c5037aec4c2cd2a1b020aa1317193d862`

Focused tests:

`tests/test_phase8a_exp056_implementation_failure_diagnostics.py`

Git blob:

`71d3fb31e21f2873423375358ecc05097c36370d`

## Next gate

After DEC-219 is green and merged, the next safe gate is a source-only successor protocol for a new experiment identity that preserves EXP-056 protocol semantics exactly and authorizes only the implementation dependency-boundary correction above.

No model fitting or historical execution is authorized by DEC-219.
