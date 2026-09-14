# Phase 4 Baseline Strategy Research — Acceptance Evidence

**Review date:** 2026-09-14
**Result:** PASS
**Decision:** DEC-028 — pending acceptance-closure merge
**Checkpoint:** `fmp-v1-phase4-baselines` — pending acceptance-closure merge and post-merge verification
**Final-test touched?: NO**

## Acceptance gate

The approved project source defines Phase 4 PASS when baseline benchmark tables exist for every tested family and at least one of the following is true: one or more strategies qualify as serious candidates, or the recorded failures clearly justify the next research question.

The gate is satisfied through the stronger first path: all six planned baseline families have completed deterministic development/validation benchmarking and two serious candidates have been promoted and frozen unchanged.

## Completed baseline families

| Experiment | Family | Outcome | Authoritative benchmark | Verified rows | Candidate outcome |
| --- | --- | --- | --- | ---: | --- |
| `EXP-20260914-001` | session breakout | PASS | run `34848137086` | 486/486 | PROMOTE USDJPY 15m / 5-pip buffer / 1.5x target-range |
| `EXP-20260914-002` | trend continuation | FAIL | run `34863705913` | 324/324 | REJECT |
| `EXP-20260914-003` | mean reversion | FAIL | run `34875463677` | 324/324 | REJECT |
| `EXP-20260914-004` | previous-day high/low rejection | FAIL | run `34883815436` | 162/162 | REJECT |
| `EXP-20260914-005` | volatility breakout | PASS | run `34888225242` | 162/162 | PROMOTE USDJPY 1h / 2.0x / fixed 1.0R |
| `EXP-20260914-006` | session high/low sweep-rejection | FAIL | run `34895426037` | 162/162 | REJECT |

Across the six experiment matrices, 108/108 pair/timeframe/split cells completed successfully and 1,620/1,620 frozen benchmark rows were independently inspected under their experiment-specific evidence audits. The required human-readable experiment registry records all six experiments, including failures.

## Frozen serious candidates

### Candidate A — session breakout

`EXP-20260914-001`: **USDJPY 15m / 5-pip breakout buffer / 1.5x target-range**.

At 0.2-pip adverse slippage:

- development: 620 trades, +5.8023% net return, +$9.3585 expectancy/trade, PF 1.1477, max drawdown 2.9370%
- validation: 362 trades, +3.7076% net return, +$10.2421 expectancy/trade, PF 1.1449, max drawdown 2.9860%

It remains positive on both splits at 0.5-pip stress. The candidate remains a research candidate rather than deployment evidence because of regime sensitivity and failure of the 1.0-pip full-family stress screen.

### Candidate B — volatility breakout

`EXP-20260914-005`: **USDJPY 1h / 2.0x range-expansion multiplier / fixed 1.0R**.

At 0.2-pip adverse slippage:

- development: 596 trades, +11.4235% net return, +$19.1670 expectancy/trade, PF 1.2321, max drawdown 2.5228%
- validation: 364 trades, +5.5971% net return, +$15.3766 expectancy/trade, PF 1.1931, max drawdown 1.9853%

It remains positive on both splits at 0.5-pip stress. Material limitations remain: 2021 validation is negative, neighboring multipliers and adjacent timeframes do not confirm the development edge, and the 1.0-pip diagnostic fails.

Neither candidate is retuned by this acceptance review. Their frozen identities remain unchanged.

## Rejected-family evidence

The four rejected families remain useful negative evidence rather than discarded trials:

- trend continuation: zero two-split 0.2-pip survivors; chronology reversals dominate isolated winners
- mean reversion: zero of 54 baseline points pass; all baseline development and validation rows are negative
- previous-day rejection: one thin baseline survivor fails 0.5-pip robustness, neighboring-buffer stability, chronology, and winner-concentration review
- session sweep-rejection: zero of 27 baseline points pass the two-split gate; the clearest development-only point reverses sharply in validation

No post-result rescue search is authorized by this acceptance review.

## Boundary verification

- Development remained 2015-01-01 through 2020-12-31 inclusive.
- Validation remained 2021-01-01 through 2023-12-31 inclusive.
- Final untouched test remained 2024-01-01 through 2026-08-20 inclusive.
- Every Phase 4 experiment records `Final-test touched?: NO`.
- Historical BID/ASK execution, adverse slippage, and accepted Phase 3 risk semantics remained authoritative.
- No Phase 1 acquisition is required or authorized by this closure.
- Broker/live integration and real-money trading remain locked; DEC-008 is unchanged.

## Acceptance conclusion

Phase 4 satisfies its approved acceptance gate and is ready to close as **PASS**. The two serious candidates remain frozen for later cross-family/model comparison. Phase 5 may become the next project phase for leakage-safe feature-engine work, but this Phase 4 closure does **not** authorize final-test inspection, broker/live integration, or real-money trading.

After the acceptance closure is merged and its source-free regression checks pass on `main`, create checkpoint `fmp-v1-phase4-baselines` at the verified closure commit.