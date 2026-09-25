# Phase 8A — EXP-057 Deterministic Implementation-Repair Training Core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-221
**Experiment:** EXP-20260925-057

## Purpose

DEC-221 implements the deterministic in-memory EXP-057 training/evaluation core against the exact DEC-220 repair protocol.

The implementation starts from the frozen EXP-056 lower-tail core and changes only:

- experiment/protocol/training identity and source bindings;
- the exact seven dependency roots authorized by DEC-219/220.

No model, data, ranking, cutoff, chronology, gate, or forward-evaluation semantics change.

## Frozen source bindings

DEC-221 binds:

- DEC-220 merge: `865ab1569a0765078ed099008a5722f8a6d310b4`
- DEC-220 protocol blob: `2f355526476a4d41967bb46e1bfad6aa525cbfa9`
- failed EXP-056 training-core blob: `c472ed48e7b79d22056d43deb0fe09166ccf34c9`
- EXP-055 predecessor training-core blob: `c9517b7516940c78621448088c3933aa1c57e281`

The frozen EXP-055 source must still report model-fit and result-execution authorization false.

## Exact repaired dereferences

The EXP-057 core contains zero direct `_predecessor` dereferences for these seven inherited EXP-054 names:

1. `FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE`
2. `FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL`
3. `FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL`
4. `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`
5. `MIN_STABILITY_WINDOW_CANDIDATE_SHARE`
6. `ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE`
7. `ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE`

Every required use of those names now resolves through `_base`.

Legitimate EXP-055 breadth-specific accesses remain on `_predecessor`.

## Preserved training/evaluation semantics

The core retains the complete EXP-056 mechanics:

- frame validation and chronological splits;
- three jackknife views;
- two HGB utility regressors per view;
- six regressors per cell;
- pooled out-of-fit calibration;
- 24 fit-half-year utility-support references;
- 12 fit-half-year feature-support references;
- 24 target-specific residual references;
- residual-bound utility;
- 12-bound residual breadth;
- fixed worst-three residual lower-tail mean;
- lower-tail-first seven-part ranking;
- 250 / 500 / 1000 budget cutoffs;
- aggregate financial gates;
- four temporal-stability windows;
- 10% per-window candidate-share floor;
- validation and retrospective holdout;
- deterministic result fingerprinting;
- no-refit forward semantics.

## Full cell runner

DEC-221 exposes the full deterministic cell core:

`run_fit_temporal_residual_lower_tail_utility_model_cell_core`

The implementation is not a partial helper gate.

## Gate metadata

The source-only training gate explicitly reports:

- residual lower-tail retained: true;
- residual lower-tail protocol change authorized: false;
- implementation dependency repair authorized: true;
- result execution authorized: false;
- model fit authorized: false.

## Authorization state

DEC-221 keeps false:

- authoritative result execution;
- model fit authorization outside this deterministic source core;
- artifact loading;
- readiness execution;
- workflow dispatch;
- rerun/replacement;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Source identity

Training core:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_training.py`

Git blob:

`ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`

Focused tests:

`tests/test_phase8a_exp057_implementation_repair_training.py`

Git blob:

`c5bfc3cb94cc3b03523063ad19b571328854dc4c`

Training-core version:

`fmp-exp057-fit-temporal-residual-lower-tail-utility-implementation-repair-training-core-v1`

## Next gate

After DEC-221 is green and merged, the next safe gate is a separate non-executable EXP-057 artifact/evidence contract bound to this exact repaired core.

No workflow source or historical execution is authorized by DEC-221.
