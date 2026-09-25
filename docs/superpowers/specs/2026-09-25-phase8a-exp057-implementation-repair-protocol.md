# Phase 8A — EXP-057 Implementation-Repair Protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-220
**Experiment:** EXP-20260925-057

## Purpose

DEC-220 opens a new experiment identity after the EXP-056 historical slot was consumed by an implementation failure before any model evidence was produced.

EXP-057 preserves EXP-056 model semantics exactly.

The only newly authorized source change is the DEC-219 implementation dependency-boundary repair.

## Frozen predecessor bindings

DEC-220 binds:

- DEC-219 merge: `acc0fab2219b76af061d602863c257b335a32d05`
- DEC-219 diagnostic blob: `d94fb02c5037aec4c2cd2a1b020aa1317193d862`
- DEC-218 result-decision blob: `75fc25ae97c03730ab75a3036059f761d8234630`
- EXP-056 protocol blob: `14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d`
- failed EXP-056 training-core blob: `c472ed48e7b79d22056d43deb0fe09166ccf34c9`

DEC-219 must still classify the failure as:

`EXP056_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_INTERMEDIATE_PREDECESSOR_EXPORT_DRIFT`

and must still keep successor model fit and historical result execution false.

## Semantic identity

EXP-057 retains the EXP-056 protocol semantics exactly:

- same feature inputs;
- same LONG/SHORT utility targets;
- same chronology;
- same HGB configuration;
- same three jackknife views;
- same unanimous positive-utility eligibility;
- same pooled out-of-fit utility calibration;
- same fit-temporal utility support;
- same fit-temporal feature support;
- same residual-bound utility;
- same residual-breadth score;
- same fixed worst-three residual lower-tail mean;
- same 250 / 500 / 1000 budgets;
- same lower-tail-first seven-part ranking;
- same seven-part cutoff;
- same aggregate financial gates;
- same four temporal-stability windows;
- same 10% per-window candidate-share floor;
- same validation and retrospective-holdout chronology;
- same no-refit forward semantics.

DEC-220 does not use the failed EXP-056 attempt as a model result.

## Exact implementation repair authorization

The sole authorized implementation change is:

`_predecessor.<name> -> _base.<name>`

for exactly these seven inherited EXP-054 names:

1. `FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE`
2. `FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL`
3. `FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL`
4. `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`
5. `MIN_STABILITY_WINDOW_CANDIDATE_SHARE`
6. `ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE`
7. `ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE`

Legitimate EXP-055 breadth-specific accesses remain on `_predecessor`.

No other dependency, calculation, model, ranking, cutoff, financial gate, stability rule, or chronology change is authorized.

## Protocol payload

The EXP-057 payload deep-copies the full EXP-056 semantic blocks.

Only identity and repair metadata differ.

The EXP-056 lower-tail definition is marked retained rather than newly added.

## Authorization state

DEC-220 opens only:

- implementation dependency repair in a later deterministic training core.

DEC-220 keeps false:

- protocol semantic changes;
- model-protocol result production;
- model fitting;
- historical result execution;
- feature changes;
- target changes;
- chronology changes;
- HGB structural changes;
- jackknife changes;
- consensus changes;
- positive-utility eligibility changes;
- calibration/support changes;
- residual-bound changes;
- residual-breadth changes;
- residual lower-tail changes;
- selection-window calibration;
- selection-window quotas;
- validation/holdout recalibration;
- realized selection-outcome ranking;
- density-anchor changes;
- minimum candidate-count changes;
- stability-screen changes;
- per-window financial-gate changes;
- per-window cutoff tuning;
- logistic/classifier fallback;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Source identity

Protocol source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_protocol.py`

Git blob:

`2f355526476a4d41967bb46e1bfad6aa525cbfa9`

Focused tests:

`tests/test_phase8a_exp057_implementation_repair_protocol.py`

Git blob:

`272b3683b1f21e76a0a3b0d2c5904d1604ae2efa`

Protocol version:

`fmp-exp057-fit-temporal-residual-lower-tail-utility-implementation-repair-protocol-v1`

## Evidence status

EXP-057 is prior-result-informed retrospective research.

It is not untouched out-of-sample evidence.

No EXP-057 model fit or historical result exists under DEC-220.

## Next gate

The next safe gate is a deterministic in-memory EXP-057 training/evaluation core that starts from the frozen EXP-056 core and changes exactly the seven dependency roots authorized above.

That implementation must remain source-only and non-executable.
