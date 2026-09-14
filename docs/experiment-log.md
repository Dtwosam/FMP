# FMP Experiment Log

This file is the human-readable experiment registry until/unless a machine-readable registry is introduced. Do not delete failed experiments.

## Experiment ID format

`EXP-YYYYMMDD-NNN`

Example: `EXP-20260903-001`

## Required experiment record

Copy this section for each serious experiment:

```markdown
### EXP-YYYYMMDD-NNN — Short descriptive name

- Date:
- Status: PLANNED | RUNNING | PASS | FAIL | INCONCLUSIVE
- Hypothesis:
- Code commit:
- Data manifest/version:
- Pair(s):
- Timeframe(s):
- Data range:
- Train period:
- Validation period:
- Final-test touched?: NO
- Strategy/model:
- Features:
- Parameters/search space:
- Random seed (if relevant):
- Spread/cost model:
- Slippage model:
- Risk assumptions:
- Trade count:
- Net return after costs:
- Expectancy/trade:
- Profit factor:
- Max drawdown:
- Key subperiod results:
- Robustness/cost sensitivity:
- Result summary:
- Conclusion: PROMOTE | REJECT | REVISE | NEED_MORE_DATA
- Reason:
- Follow-up:
```

## Registry

### EXP-20260914-001 — Session breakout baseline

- Date: 2026-09-14
- Status: PASS
- Hypothesis: After a completed pre-London range, a confirmed break during the early London session may exhibit enough short-horizon continuation on some V1 pair/timeframe combinations to overcome historical spread and adverse slippage under fixed-risk execution. No profitability was assumed.
- Code commit: `cc01929b80cbd1d5619de8476caa8f3d3410262e`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; this experiment loaded development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic `session_breakout` baseline, `Europe/London`; range 00:00–08:00, breakout observation 08:00–12:00, exact mandatory flat timestamp 16:00 local; first qualifying breakout only.
- Features: midpoint OHLC only for range/signal analysis; Phase 3 historical BID/ASK execution remained the sole fill/PnL source of truth.
- Parameters/search space: `buffer_pips = {0, 2, 5}` × `target_range_multiple = {0.5, 1.0, 1.5}`; exactly 9 predeclared configurations per pair/timeframe and no post-result expansion under this experiment ID.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: 0.25% requested; 0.50% hard per-trade max; 1.00% simultaneous max; 1.50% UTC day-start realized-loss halt; accepted Phase 3 sizing/execution rules unchanged.
- Trade count: frozen serious candidate USDJPY 15m, 5-pip buffer, 1.5x target: 620 development trades and 362 validation trades.
- Net return after costs: at 0.2-pip slippage, +5.8023% development and +3.7076% validation for the frozen serious candidate.
- Expectancy/trade: at 0.2-pip slippage, +$9.3585 development and +$10.2421 validation.
- Profit factor: at 0.2-pip slippage, 1.1477 development and 1.1449 validation.
- Max drawdown: at 0.2-pip slippage, 2.9370% development and 2.9860% validation.
- Key subperiod results: selected-candidate yearly net PnL at 0.2-pip slippage was 2015 -$1,025.12, 2016 +$2,794.76, 2017 -$870.72, 2018 +$975.35, 2019 +$7.88, 2020 +$3,920.14; validation was 2021 -$1,308.81, 2022 +$4,595.37, 2023 +$421.08. About 91.6% of validation gross positive PnL occurred in 2022, a material concentration weakness.
- Robustness/cost sensitivity: all three USDJPY 15m target-1.5 buffer neighbors remain positive on both splits at 0.5-pip slippage; the same 5-pip / 1.5x point also remains positive on both splits at 5m and 1h under 0.5-pip slippage. The selected USDJPY 15m point is +3.4625% development / +2.5224% validation at 0.5 pips. At 1.0 pip it is -0.3228% development / +0.5769% validation, and no configuration in the full experiment remains positive on both splits at 1.0-pip stress.
- Result summary: merged-main run `34848137086` completed SUCCESS. All 18/18 matrix artifacts and 486/486 configuration rows were independently inspected with zero ZIP, manifest, code/data identity, grid, candidate-reuse, or accounting discrepancies. At 0.5-pip stress exactly nine configurations remain positive on both development and validation, all USDJPY. GBPUSD has two baseline 5m target-1.5 points positive on both splits but neither survives 0.5-pip stress; EURUSD has no baseline configuration positive on both splits.
- Conclusion: PROMOTE
- Reason: promote the frozen USDJPY 15m, 5-pip buffer, 1.5x target configuration as a serious Phase 4 candidate because development and validation agree, neighboring parameter points show support, moderate 0.5-pip cost stress survives, and the same parameter point has cross-timeframe support. Promotion is limited by 1.0-pip cost failure and material 2022 validation concentration.
- Follow-up: retain this candidate unchanged, proceed to the next predeclared Phase 4 family, trend continuation, and keep the 2024-01-01 through 2026-08-20 final-test period untouched until candidate selection across the admitted baseline program is materially complete. This conclusion does not make Phase 4 PASS, start Phase 5, authorize broker/live integration, or unlock real-money trading. Detailed evidence is in `docs/phase4-session-breakout-evidence.md`.

### EXP-20260914-002 — Trend continuation baseline

- Date: 2026-09-14
- Status: FAIL
- Hypothesis: During the London trading day, a pullback that temporarily crosses a short trend average and then resumes in the direction of an established multi-hour trend may have enough continuation to overcome historical BID/ASK spread and adverse slippage under fixed-risk execution. No profitability was assumed.
- Code commit: `d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; this experiment loaded development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic London-session trend-continuation baseline; signals observed on fully closed bars from 08:00 through 14:00 `Europe/London`, first qualifying signal only, exact mandatory flat timestamp 16:00 local.
- Features: midpoint OHLC only for SMA context, pullback/resumption detection, three-bar structural stop, and frozen R-target geometry; Phase 3 historical BID/ASK execution remained the sole fill/PnL source of truth.
- Parameters/search space: trend windows `2h/8h`, `4h/16h`, `8h/32h` × target `{1.0R, 1.5R}`; exactly 6 strategy configurations per pair/timeframe and no post-result parameter expansion under this experiment ID.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: 0.25% requested; 0.50% hard per-trade max; 1.00% simultaneous max; 1.50% UTC day-start realized-loss halt; accepted Phase 3 sizing/execution rules unchanged.
- Trade count: no promoted candidate; the full frozen matrix is preserved in the benchmark artifacts and detailed evidence.
- Net return after costs: no candidate-level value because no configuration passed the development-to-validation promotion screen. Strongest split-only baseline example was GBPUSD 1h `8h/32h / 1.5R`: +14.8309% development versus -2.7022% validation.
- Expectancy/trade: no promoted candidate; that same split-only GBPUSD 1h point was +$24.7595 development versus -$8.5784 validation.
- Profit factor: no promoted candidate; that same split-only GBPUSD 1h point was 1.2294 development versus 0.9251 validation.
- Max drawdown: no candidate-level value; the split-only GBPUSD 1h point had 3.3801% development max drawdown and 7.4834% validation max drawdown.
- Key subperiod results: split instability dominates. EURUSD validation had zero baseline qualifiers on all three timeframes. GBPUSD development produced isolated 15m/1h positives that did not persist into validation. USDJPY 15m reversed the other way: zero development qualifiers but two validation qualifiers, with `2h/8h / 1.5R` reaching +9.2320% in validation.
- Robustness/cost sensitivity: matched development↔validation survivors are zero for every pair/timeframe at 0.2-pip baseline slippage, and remain zero at 0.5-pip and 1.0-pip stress. Cost stress therefore cannot rescue the missing temporal agreement.
- Result summary: merged-main run `34863705913` completed SUCCESS on exact commit `d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2`. All 18/18 matrix artifacts and 324/324 configuration rows were independently inspected with zero ZIP, manifest, code/data identity, split, grid, candidate-reuse, or accounting discrepancies.
- Conclusion: REJECT
- Reason: no frozen configuration achieved positive net return, positive expectancy, and profit factor above one on both development and validation even at baseline 0.2-pip adverse slippage. Split-only winners reverse across chronology and fail the predeclared temporal-robustness requirement.
- Follow-up: retain the frozen USDJPY 15m session-breakout candidate unchanged and proceed to the next predeclared Phase 4 family, mean reversion. Keep the 2024-01-01 through 2026-08-20 final-test period untouched. This rejection does not make Phase 4 PASS, start Phase 5, authorize broker/live integration, or unlock real-money trading. Detailed evidence is in `docs/phase4-trend-continuation-evidence.md`.
