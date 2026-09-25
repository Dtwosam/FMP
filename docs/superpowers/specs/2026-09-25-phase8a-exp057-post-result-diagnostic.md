# Phase 8A — EXP-057 Post-Result Diagnostic

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC
**Decision:** DEC-230
**Experiment:** EXP-20260925-057

## Purpose

DEC-230 diagnoses the reviewed EXP-057 result against the nearest prior successful historical baseline, EXP-055.

EXP-056 is excluded as a model-outcome baseline because its sole historical attempt failed before producing model evidence. DEC-230 therefore compares the last successful pre-lower-tail result to the repaired lower-tail result.

## Frozen bindings

DEC-230 binds:

- DEC-229 merge: `7a2c53712a85f69e106a707dc1245e664c68bcbb`
- DEC-229 result-decision blob: `185e2cdf089cb6f1a12619af58fd32860366498f`
- DEC-208 diagnostic blob: `5ff61be317b225d9d7ec656b4789c4561d52b522`
- DEC-207 EXP-055 result-decision blob: `e2226117ebf10b762557d43549390c46c243bbae`

Evidence fingerprints:

- EXP-055: `f3a386dad7f23ac9d6867d030ac90e0884f3ab658c9ffecce8647048037d2510`
- EXP-057: `4bf67108e0df38d4f213d08898fadd338285ac7a2ce56920b61e4dba0f3eec4c`

## Unchanged accounting

EXP-055 and EXP-057 retain identical:

- 54 total budget variants;
- 28 available variants;
- 26 unavailable variants;
- 26,392 utility-eligible selection rows;
- zero stable selection-pass variants;
- zero accepted model candidates.

The lower-tail ranking did not change eligibility, budget availability, chronology, financial gates, or the temporal-stability threshold.

## Aggregate-pass change

EXP-055 aggregate passes:

- USDJPY / 5m / 60m / budget 250;
- USDJPY / 5m / 60m / budget 1000.

EXP-057 retains both and adds:

- USDJPY / 5m / 60m / budget 500.

No EXP-055 aggregate pass is lost.

The aggregate-pass count therefore increases from 2 to 3, while the stable-pass count remains 0.

## Available-variant financial mix

Across the same 28 available variants at 0.5-pip slippage:

- 15 have higher aggregate total net pips in EXP-057;
- 13 have lower aggregate total net pips;
- 0 are unchanged.

This is a mixed financial shift, not a universal improvement.

## Common USDJPY 5m / 60m cell

Aggregate total net pips:

| Budget | EXP-055 | EXP-057 |
| --- | ---: | ---: |
| 250 | 576.6000000000067 | 301.40000000000646 |
| 500 | -470.799999999977 | 88.99999999999636 |
| 1000 | 40.50000000001137 | 362.0999999999858 |

The lower-tail ranking improves budgets 500 and 1000 enough for budget 500 to become a new aggregate pass, but budget 250 weakens.

## Temporal concentration

Budget 250 window candidate counts:

- EXP-055: `0 / 0 / 0 / 251`
- EXP-057: `0 / 0 / 0 / 250`

The top-250 selection remains entirely concentrated in 2022 H2.

New EXP-057 budget 500 pass:

- `0 / 0 / 3 / 497`

Only 3 of 500 candidates appear in 2022 H1 and none in the two 2021 windows. The unchanged 10% minimum window share is not approached.

Budget 1000:

- EXP-055: `0 / 1 / 83 / 916`
- EXP-057: `0 / 1 / 73 / 926`

EXP-057 improves the aggregate and late-window financial totals at budget 1000, but candidate concentration shifts further toward 2022 H2. The 2022 H1 count falls from 83 to 73, below the 100-candidate 10% floor.

## Diagnostic classification

DEC-230 classifies the result as:

`LOWER_TAIL_RANKING_CHANGED_CANDIDATE_FINANCIAL_MIX_AND_ADDED_AGGREGATE_PASS_BUT_DID_NOT_CREATE_TEMPORAL_STABILITY`

The continuous lower-tail ranking is informative enough to change candidate identity and aggregate financial outcomes, but it does not create selection-time chronological breadth.

The failure mode is therefore still temporal concentration, not lack of aggregate-pass candidates.

## Fail-closed interpretation

DEC-230 does not authorize:

- EXP-057 rerun;
- EXP-057 replacement run;
- relaxing temporal candidate-share thresholds;
- relaxing temporal financial gates;
- removing early stability windows;
- ranking directly on selection-window outcomes;
- recalibrating on selection windows;
- adding selection-window quotas;
- retuning lower-tail thresholds on selection outcomes;
- successor model fit;
- successor historical execution;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

Only successor protocol source design is open.

Any successor must preserve the frozen historical chronology and cannot use selection-window outcomes to tune or rank the model.

## Source identity

Diagnostic source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_post_result_diagnostics.py`

Git blob:

`09e88b85a51b858296a3af7d146251606f1d5533`

Focused tests:

`tests/test_phase8a_exp057_post_result_diagnostics.py`

Git blob:

`c3486a0b9b5daf43fdf5cc66b6ddc6546d12b0cd`

## Next safe gate

After DEC-230 is green and merged, the next safe gate is successor protocol source design only.

That successor must target the persistent selection-time temporal-concentration failure without using selection-window outcomes, weakening temporal gates, or reopening EXP-057.
