# Phase 8A — EXP-055 Post-Result Diagnostic

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC
**Decision:** DEC-208
**Experiment:** EXP-20260925-055

## Purpose

DEC-208 explains what changed from EXP-054 to EXP-055 after DEC-207 closes the sole EXP-055 historical slot with no stable challenger.

The diagnostic is retrospective and result-informed. It authorizes no rerun, no gate relaxation, no selection-window tuning, no model fit, and no historical result execution.

## Frozen result bindings

DEC-208 binds:

- DEC-207 merge: `78b1081aec39f8b79fe751ba2935ef49a1cb5ad1`
- DEC-207 result-decision blob: `e2226117ebf10b762557d43549390c46c243bbae`
- DEC-197 diagnostic blob: `3f53e79b52d3a2e4de1e7f61e142ecc55197aa87`
- EXP-054 evidence fingerprint: `307b576f06c6aa2fb01a267232a0de553bfa79c1bdbe6bf5d55b2bfc3b40787c`
- EXP-055 evidence fingerprint: `f3a386dad7f23ac9d6867d030ac90e0884f3ab658c9ffecce8647048037d2510`

Both experiments retain the same 54 total budget variants, 28 available variants, 26 unavailable variants, and 26,392 utility-eligible selection rows.

## Aggregate pass identity

EXP-054 and EXP-055 produce the same two aggregate-selection-pass variants:

- USDJPY / 5m / 60m / budget 250
- USDJPY / 5m / 60m / budget 1000

Both experiments produce zero stable-selection-pass variants and zero accepted model candidates.

Residual breadth therefore changed ranking composition without expanding the aggregate-pass set or creating a stable selection.

## Common-cell comparison

For USDJPY / 5m / 60m:

### Budget 250

EXP-054:

- aggregate total net pips at 0.5 pip slippage: `644.3`
- window counts: `0 / 0 / 0 / 250`

EXP-055:

- aggregate total net pips at 0.5 pip slippage: `576.6`
- window counts: `0 / 0 / 0 / 251`
- residual-breadth cutoff: `10/12`

The high fit-period breadth cutoff does not transfer into selection-period chronological breadth. All candidates remain concentrated in 2022 H2.

### Budget 1000

EXP-054:

- aggregate total net pips: `302.3`
- window counts: `0 / 3 / 72 / 925`
- window net pips: `0.0 / 21.2 / 510.5 / -229.4`

EXP-055:

- aggregate total net pips: `40.5`
- window counts: `0 / 1 / 83 / 916`
- window net pips: `0.0 / -2.8 / 464.3 / -421.0`
- residual-breadth cutoff: `0/12`

The 2022 H1 candidate share increases from 7.2% to 8.3%, but remains below the unchanged 10% stability floor. 2021 H2 becomes sparser and financially negative, while 2022 H2 remains financially negative and worsens.

## Available-variant financial comparison

Across the same 28 available variants, comparing aggregate 0.5-pip total net pips between EXP-054 and EXP-055:

- improved: 7
- worsened: 16
- unchanged: 5

This count is a diagnostic comparison of overlapping research variants, not an independent portfolio performance statistic.

## Classification

DEC-208 classifies the result as:

`FIT_RESIDUAL_BREADTH_DID_NOT_TRANSFER_TO_SELECTION_TEMPORAL_BREADTH_AND_WEAKENED_PASS_VARIANT_FINANCIALS`

The evidence supports these conclusions:

- eligibility did not change;
- budget availability did not change;
- aggregate-pass identity did not change;
- stable-pass count did not improve;
- the top-250 row set can have high fit residual breadth while remaining completely concentrated in one later selection window;
- budget-1000 gains only a small 2022 H1 share increase that does not clear the stability floor;
- surviving aggregate-pass financial quality is weaker under breadth-first ranking;
- binary fit residual breadth is not sufficient as the next successor signal by itself.

## Prohibited responses

DEC-208 does not authorize:

- EXP-055 rerun;
- replacement EXP-055 run;
- lowering the 10% stability-share floor;
- weakening per-window financial requirements;
- removing early stability windows;
- using realized selection outcomes in ranking;
- recalibrating on selection windows;
- adding selection-window quotas;
- retuning residual breadth on selection outcomes;
- promotion;
- shadow/demo execution;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next safe gate

DEC-208 opens only a successor protocol source-design gate.

A successor may use immutable fit-period information to define a materially different temporal-robustness ranking quantity, but it must remain selection-outcome blind and must preserve the existing stability gate unless a separately justified decision explicitly changes that rule.

No successor model fit or historical result execution is authorized by DEC-208.

## Source identity

Diagnostic source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_post_result_diagnostics.py`

Git blob:

`5ff61be317b225d9d7ec656b4789c4561d52b522`

Focused tests:

`tests/test_phase8a_exp055_post_result_diagnostics.py`

Git blob:

`ed25527485617b0e4e3e4e0119f2692907234f1f`
