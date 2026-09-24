# Phase 8A — EXP-049 Regime-Utility Artifact / Evidence Contract

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY; AUTHORITATIVE EXP-049 RESULT EXECUTION CLOSED
**Decision:** DEC-134
**Experiment:** EXP-20260924-049

## Purpose

DEC-134 freezes the artifact-backed historical-data runner and aggregate-evidence contract around the already merged DEC-132 protocol and DEC-133 deterministic training core.

This decision adds no new research logic. It only defines which accepted artifacts may feed the core, how every cell result must be validated, how the 18-cell aggregate evidence is compiled, and which exact source identities a later execution gate must bind.

## Frozen source chain

- DEC-132 merge: `d17326eebf6b456211225d7bad3a182a0307b707`
- DEC-132 protocol blob: `ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac`
- DEC-133 merge: `a6420e35a9219c81e65c5179843488f94b6668d3`
- DEC-133 training-core blob: `e1018b20210b7bb8d666071d8eb878aba5899111`
- legacy accepted EXP-044 artifact loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`
- base training helper blob: `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`
- density/stability helper blob: `8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`

Any byte drift in those bound source files fails closed.

## Accepted historical inputs

The runner may reuse only the already accepted EXP-044 data-preparation chain:

- authoritative feature run/evidence;
- authoritative outcome run/evidence;
- authoritative readiness artifact;
- exact nine pair/timeframe feature/outcome cells;
- exact Phase 2 processed-manifest identities already bound by those artifacts.

No new historical acquisition is introduced.

The evidence remains `RETROSPECTIVE_ALREADY_SEEN`, `prior_result_informed=true`, and `untouched_oos=false`.

## Cell-result contract

All 18 pair/timeframe/horizon cells are mandatory.

Each cell must preserve:

- exact DEC-132/133 experiment, protocol, and training-core identities;
- exact processed-manifest fingerprint;
- exact split row counts;
- exactly three fit regimes;
- exactly two fitted regressors per regime;
- exactly six regressors per cell;
- exact financial targets `long_net_pips_0p5` and `short_net_pips_0p5`;
- one deterministic preprocessor fingerprint and model fingerprint per regime/target;
- finite target summaries with exact row accounting;
- classifier fallback excluded;
- logistic regression excluded;
- no full-fit fallback.

## Utility-consensus evidence

Selection and any unlocked forward split must record:

- LONG/SHORT/NO_TRADE consensus-direction counts;
- consensus-eligible row count and rate;
- minimum and maximum robust utility when eligible rows exist;
- exact per-regime/per-target prediction digests;
- one deterministic consensus digest.

All eligible robust-utility values must be finite and strictly positive.

## Density and stability validation

Every budget variant must be exactly one of 250, 500, or 1000.

Unavailable budgets must show fewer eligible utility rows than the requested budget and no cutoff.

Available budgets must show:

- finite positive selection-derived robust-utility cutoff;
- candidate count at cutoff at least the budget;
- exact 0.5-pip realized financial metrics;
- unchanged aggregate financial gate;
- if aggregate-passing, all four unchanged temporal-stability windows;
- unchanged 10% per-window candidate-share floor;
- unchanged positive financial signs in each window.

A cell reporting no challenger cannot hide a stable-passing budget.

A selected cell must identify the deterministic winner under the frozen tie-break.

## Forward validation

If a cell selects a variant:

- validation must reuse the exact selected budget and numeric cutoff;
- forward consensus evidence must preserve exact regime/target prediction digests;
- validation must evaluate 0.2/0.5/1.0-pip scenarios;
- PASS still requires both 0.5 and 1.0 gates;
- retrospective holdout stays locked after validation rejection;
- if validation passes, holdout uses the same frozen models/rule/cutoff and the same scenario contract.

## Aggregate evidence

Aggregate evidence must contain exactly 18 unique cell summaries and bind:

- DEC-132 protocol source identity and fingerprint;
- DEC-133 training-core source identity;
- exact code commit;
- accepted EXP-044 feature/outcome/readiness identities;
- per-cell result fingerprints;
- per-regime/per-target model fingerprints;
- selection / validation / holdout status;
- aggregate-pass, stable-pass, stability-reject, and unavailable-budget counts;
- total utility-eligible selection rows.

The aggregate artifact has one canonical JSON SHA-256 fingerprint.

## Structural non-execution

The authoritative bundle wrapper checks `AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED` before source validation, readiness validation, historical artifact loading, or model fitting.

Under DEC-134 that flag is false.

Therefore DEC-134 source cannot produce an authoritative EXP-049 historical result.

## Source identity

Artifact/evidence source:

`src/fmp/market_learning/model_successor_regime_utility_artifacts.py`

Git blob:

`edd8fbb447df1b4336e5174706a8e39b40c4573a`

Focused tests:

`tests/test_phase8a_exp049_regime_utility_artifacts.py`

Git blob:

`7ed29dbd8c079a99919fd9a7d1d6cb9ab19f3f96`

## Authorization state

DEC-134 keeps false:

- authoritative historical result execution;
- model fitting;
- model-protocol result production;
- promotion;
- shadow;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading authorization.

## Next gate

A later separate decision may freeze the manual main-only workflow, CLI/runtime, and exact-source execution gate around merged DEC-132/133/134.

That later source must remain non-executable until terminal review is predeclared and a separate run authorization is granted.
