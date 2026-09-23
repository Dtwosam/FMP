# Phase 8A — EXP-045 Post-Result Diagnostic Gate

**Date:** 2026-09-23
**Status:** POST-RESULT DIAGNOSTIC; NO SUCCESSOR EXECUTION AUTHORIZED
**Decision:** DEC-103
**Source experiment:** EXP-20260923-045
**Source result:** DEC-102

## 1. Purpose

DEC-103 freezes the detailed post-result diagnostic from the complete EXP-045 cell artifacts before any successor model protocol is written.

Its purpose is to distinguish the dominant observed failure mode from tempting post-hoc parameter changes and to open only successor-protocol source work.

DEC-103 authorizes no model fit, historical result execution, prospective shadow, broker mutation, order placement, or trading.

## 2. Source identity

The diagnostic is bound to:

- reviewed result decision: `DEC-102`
- source experiment: `EXP-20260923-045`
- source workflow run: `35911916239`
- source execution commit: `6d42a5053c5f2f696071715640dab24973a40517`
- source aggregate evidence fingerprint: `3e0ebac02dbba690b4c03dd10c3fdd30c5eb0d6356b881e38f9a3527f0135c55`

All 18 pair/timeframe/horizon cell result files were inspected from the nine persisted DEC-102 cell artifacts.

## 3. Variant accounting

The EXP-045 selection stage contained 108 configured family/threshold slots.

Six cells recorded predeclared logistic `FAILED_NON_CONVERGENCE`; those cells contribute 18 unavailable logistic threshold slots.

Therefore 90 variants were actually evaluated.

At the frozen 0.5-pip selection scenario:

- evaluated variants: **90**
- variants meeting the `directional_candidate_count >= 250` criterion: **37**
- variants meeting that count criterion but failing one or more financial-sign criteria: **36**
- variants with positive gross/mean/total financial signs: **26**
- variants with positive financial signs but fewer than 250 directional candidates: **25**
- variants passing the complete selection gate: **1**

Thus the 250-candidate floor is not the sole reason EXP-045 failed to produce an accepted challenger. Most count-sufficient variants failed the financial criteria, and the only complete selection-gate pass later failed validation.

## 4. The only selected challenger

The only selection-gate pass was:

- symbol: GBPUSD
- timeframe: 5m
- horizon: 240m
- family: hist-gradient boosting
- confidence threshold: 0.6

Selection metrics under the frozen 0.5-pip scenario:

- directional candidates: **460**
- directional candidate rate: **0.002188475298774454**
- mean net pips: **+5.116739130434755**
- total net pips: **+2353.6999999999875**

Validation metrics under the same frozen 0.5-pip scenario:

- directional candidates: **83**
- directional candidate rate: **0.0003943367540858989**
- mean net pips: **−16.83734939759037**
- total net pips: **−1397.5000000000007**

The validation candidate count is approximately **18.04%** of the selection candidate count. The validation candidate rate is approximately **18.02%** of the selection candidate rate.

The selected challenger therefore changed both signal frequency and financial sign materially between selection and validation.

DEC-103 classifies the dominant diagnostic as:

`TEMPORAL_STABILITY_FAILURE_DOMINANT`

This classification is descriptive of the observed EXP-045 evidence. It is not a promotion or trading judgment.

## 5. Low-count positive variants

Twenty-five evaluated variants had positive gross/mean/total financial signs but failed the 250-candidate minimum.

Examples include:

- GBPUSD 5m / 240m logistic at 0.6: 153 candidates, +17.82 mean net pips;
- GBPUSD 5m / 240m logistic at 0.7: 50 candidates, +101.54 mean net pips;
- USDJPY 5m / 240m HGB at 0.7: 61 candidates, +32.85 mean net pips;
- GBPUSD 15m / 240m logistic at 0.6: 75 candidates, +14.30 mean net pips.

These variants were not selected under the frozen protocol and have no validation evidence under their own identities.

DEC-103 therefore explicitly keeps:

`RELAX_MIN_DIRECTIONAL_CANDIDATE_COUNT_AUTHORIZED = false`

and:

`PROMOTE_LOW_COUNT_POSITIVE_VARIANTS_AUTHORIZED = false`

A future protocol may study alternative signal-density mechanics only if they are predeclared before execution. DEC-103 does not retroactively pass these variants.

## 6. Logistic non-convergence

Six cells recorded the predeclared DEC-095 logistic family outcome `FAILED_NON_CONVERGENCE`.

HGB fitted in all 18 cells.

Because an HGB family remained available in every affected cell, logistic non-convergence is recorded as a secondary family-availability issue rather than the dominant reason no model was accepted.

A future successor protocol may alter logistic preprocessing/solver mechanics only through a separately frozen protocol. No rescue fit is authorized here.

## 7. Successor design guardrails

Any successor protocol source opened after DEC-103 must preserve these boundaries:

1. EXP-045 may not be rerun or replaced.
2. The EXP-045 250-directional-candidate gate may not be retroactively relaxed.
3. Low-count positive EXP-045 variants may not be promoted or relabeled as validation-tested.
4. The single EXP-045 selected variant remains a validation rejection.
5. A successor should address temporal stability explicitly rather than merely lower the selection floor.
6. Any changed model family, solver, confidence mechanism, temporal-stability test, or signal-density rule must be frozen before a successor result-producing run.
7. All successor evidence must remain explicitly post-result-informed unless a genuinely untouched future dataset is separately created.

## 8. Source-only gate

The machine-checkable diagnostic source is:

`src/fmp/market_learning/model_successor_post_result_diagnostics.py`

Git blob:

`f1ccda0d393b851cd7c1db1399da57a920a0a7c1`

DEC-103 sets only:

`SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = true`

It keeps false:

- successor historical result execution;
- successor model fit;
- EXP-045 rerun;
- EXP-045 replacement run;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 9. Next gate

A later separate decision may freeze an exact successor protocol consistent with the DEC-103 guardrails.

No successor workflow, model fit, or result-producing execution is authorized by DEC-103.
