# Phase 8A — EXP-059 Fit-Regime Balance Protocol

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-242
**Experiment:** EXP-20260926-059

## Purpose

DEC-242 opens one successor ranking change after DEC-241 shows that EXP-058 regime-floor ranking changes candidate identity and financial mix but still does not create selection-time temporal stability.

EXP-059 adds a fit-only regime-balance score derived from the same three frozen EXP-058 regime means.

## Frozen predecessor bindings

DEC-242 binds:

- DEC-241 merge: `761696ac8619841efde494ff4c827c4c91e8895c`
- DEC-241 diagnostic blob: `c0717252dabd625bd6a65b78f9acb5217ed44c84`
- DEC-240 result-decision blob: `f5a5f7e49b7088f4af9b35a9143e486c3fba3d1a`
- predecessor EXP-058 protocol blob: `8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2`
- predecessor evidence fingerprint: `7e5019f0e00ada90a8f9c111d2b6fdb4ba41908f86a47203258b333439c8c8ee`

## Regime-balance score

For each already eligible row, EXP-059 reuses the exact three finite fit-regime means produced by EXP-058.

Let the three means be `m1, m2, m3`.

The score is:

`mean(m1,m2,m3) - (max(m1,m2,m3) - min(m1,m2,m3))`

The penalty multiplier is frozen at exactly `1.0`.

The score therefore rewards high central fit-regime utility while penalizing dispersion across fit eras.

No new residual reference, jackknife view, fit regime, model fit, selection-window statistic, validation result, or holdout result enters the score.

## Ranking and cutoff

Eligible rows rank by:

1. regime-balance utility descending;
2. regime-floor utility descending;
3. residual lower-tail mean descending;
4. residual breadth descending;
5. robust residual-bound utility descending;
6. feature support descending;
7. utility support descending;
8. pooled calibrated utility descending;
9. raw utility descending;
10. row identity ascending.

Each unchanged budget 250 / 500 / 1000 freezes the budget-th row's nine-part numeric cutoff.

Exact nine-part ties may exceed the nominal budget under the unchanged inclusive final-component policy.

## Forward application

Validation and retrospective holdout reuse:

- the exact six frozen jackknife regressors;
- six pooled calibration references;
- 24 utility-support references;
- 12 feature-support references;
- 24 residual references;
- the same twelve residual bounds;
- the same three fit-regime means;
- regime-floor utility;
- regime-balance utility;
- the exact frozen nine-part cutoff.

No refit, recalibration, budget retuning, selection-window tuning, or outcome-driven ranking is allowed.

## Unchanged gates

DEC-242 changes none of:

- row eligibility;
- candidate budgets;
- financial gates;
- four temporal-stability windows;
- 10% minimum per-window candidate-share floor;
- validation chronology;
- retrospective-holdout chronology;
- feature set;
- target construction;
- HGB configuration;
- jackknife views.

## Authorization state

DEC-242 authorizes only the regime-balance protocol source change.

It keeps false:

- model-protocol result production;
- model fit;
- historical result execution;
- rerun/replacement;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Source identity

Protocol source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_protocol.py`

Git blob:

`cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc`

Focused tests:

`tests/test_phase8a_exp059_regime_balance_protocol.py`

Git blob:

`42277506ffb39c0a9969b0253127a0cf10b79fd9`

## Next gate

After DEC-242 is green and merged, the next safe gate is a deterministic in-memory EXP-059 training/evaluation core only.
