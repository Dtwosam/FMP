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

### EXP-20260914-003 — Mean reversion baseline

- Date: 2026-09-14
- Status: FAIL
- Hypothesis: Fresh intraday displacement from a preceding rolling midpoint-close distribution may revert toward its pre-existing mean strongly enough to overcome historical spread and adverse slippage under fixed-risk execution. No profitability was assumed.
- Code commit: `87003a3982ca61eb6fd030c5291616d98dbb0c1a`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic London-session mean-reversion baseline using preceding-N midpoint-close population mean/std, fresh z-score excursions, first signal only, and exact 16:00 Europe/London flat.
- Features: midpoint close, rolling mean, rolling population standard deviation, and current/previous z-score; Phase 3 historical BID/ASK execution remained authoritative.
- Parameters/search space: lookbacks 4h/8h/16h × fresh-excursion thresholds 1.5σ/2.0σ; exactly 6 configurations per pair/timeframe.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: accepted Phase 3 policy unchanged: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: no promoted candidate; full 324-row matrix retained in evidence.
- Net return after costs: no promoted candidate; all 54 development and all 54 validation baseline rows were negative.
- Expectancy/trade: no promoted candidate; all baseline rows were negative on both splits.
- Profit factor: no promoted candidate; development range 0.6150–0.9596 and validation range 0.5396–0.9582 at baseline.
- Max drawdown: no candidate-level value; fixed-risk drawdowns remain in benchmark evidence.
- Key subperiod results: the family failed broadly rather than through one isolated chronology reversal.
- Robustness/cost sensitivity: zero baseline survivors; 0.5/1.0-pip rows remain diagnostic evidence only and cannot rescue the family.
- Result summary: merged-main benchmark run `34875463677` completed SUCCESS; 18/18 artifacts and 324/324 rows independently verified with zero integrity/identity/grid/candidate-reuse/accounting errors.
- Conclusion: REJECT
- Reason: zero of 54 pair/timeframe/lookback/threshold points achieved positive net return, positive expectancy, and PF > 1 on both development and validation at 0.2-pip baseline.
- Follow-up: retain EXP-001 unchanged; no post-result expansion; final-test remains locked. Detailed evidence: `docs/phase4-mean-reversion-evidence.md`.

### EXP-20260914-004 — Previous-day high/low rejection baseline

- Date: 2026-09-14
- Status: FAIL
- Hypothesis: Penetration beyond the previous completed New-York-close FX session high/low followed by a close back inside may revert toward the frozen previous-day midpoint strongly enough to overcome costs. No profitability was assumed.
- Code commit: `7db3a747236942fa393521e5866e3245d1a22a99`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic previous-day high/low rejection using the most recent completed New-York-close FX session, first directional rejection only, and exact 16:00 Europe/London flat.
- Features: previous-day midpoint high/low/midpoint and current midpoint penetration/rejection; Phase 3 BID/ASK execution.
- Parameters/search space: penetration buffers 0/2/5 pips; no post-result expansion.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: accepted Phase 3 policy unchanged: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: sole baseline survivor USDJPY 5m / 5-pip buffer had 29 development and 28 validation trades.
- Net return after costs: +4.0039% development and +0.0657% validation for the sole baseline survivor at 0.2 pips.
- Expectancy/trade: +$138.0644 development and +$2.3461 validation.
- Profit factor: 1.9002 development and 1.0133 validation.
- Max drawdown: 2.0245% development and 1.7179% validation.
- Key subperiod results: validation negative in 2021 and 2022 and positive only in 2023; top three winners contributed about 85.38% of validation positive R.
- Robustness/cost sensitivity: validation turned negative at 0.5-pip slippage; neighboring 0/2-pip buffers were negative on both splits; 1.0-pip validation also failed.
- Result summary: merged-main benchmark run `34883815436` completed SUCCESS; 18/18 artifacts and 162/162 rows independently verified with zero integrity/identity/grid/candidate-reuse/accounting errors.
- Conclusion: REJECT
- Reason: the only baseline survivor was thin, isolated, cost-sensitive, chronologically concentrated, and winner-dependent, failing the predeclared robustness review.
- Follow-up: no candidate promoted and no rescue search authorized. Detailed evidence: `docs/phase4-previous-day-rejection-evidence.md`.

### EXP-20260914-005 — Rolling volatility-breakout baseline

- Date: 2026-09-14
- Status: PASS
- Hypothesis: A close outside a preceding rolling 8h midpoint channel accompanied by contemporaneous range expansion may continue far enough to overcome historical spread and adverse slippage. No profitability was assumed.
- Code commit: `3bf36186900f5065e9e3ddced0305865433b9d69`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic rolling 8h volatility breakout; strict close beyond rolling channel plus current range expansion; first signal only; signal-bar extreme stop; fixed 1.0R target; exact 16:00 Europe/London flat.
- Features: rolling midpoint high/low, median reference bar range, current midpoint range, and expansion multiple.
- Parameters/search space: range-expansion multipliers 1.0x/1.5x/2.0x; fixed 1.0R target.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: accepted Phase 3 policy unchanged: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: promoted USDJPY 1h / 2.0x point had 596 development and 364 validation trades.
- Net return after costs: +11.4235% development and +5.5971% validation at 0.2 pips.
- Expectancy/trade: +$19.1670 development and +$15.3766 validation.
- Profit factor: 1.2321 development and 1.1931 validation.
- Max drawdown: 2.5228% development and 1.9853% validation.
- Key subperiod results: all six development years positive; validation negative in 2021 but positive in 2022 and 2023; top-three winner dependence about 1.30% development and 2.22% validation positive R.
- Robustness/cost sensitivity: survives 0.5-pip stress on both splits but fails 1.0-pip diagnostic; neighboring multipliers and adjacent timeframes do not confirm the development edge.
- Result summary: merged-main benchmark run `34888225242` completed SUCCESS; 18/18 artifacts and 162/162 rows independently verified; exactly one of 27 baseline points survived: USDJPY 1h / 2.0x.
- Conclusion: PROMOTE
- Reason: the exact predeclared point clears both chronological splits, survives required 0.5-pip stress, has a substantial sample and low drawdown, broad development-year support, and very low top-winner dependence despite parameter/timeframe isolation and 2021 weakness.
- Follow-up: freeze USDJPY 1h / 2.0x / fixed 1.0R as the second serious Phase 4 candidate alongside EXP-001. Detailed evidence: `docs/phase4-volatility-breakout-evidence.md`.

### EXP-20260914-006 — Session high/low sweep-rejection baseline

- Date: 2026-09-14
- Status: FAIL
- Hypothesis: Intrabar penetration beyond the frozen 00:00–08:00 Europe/London session high/low followed by a strict close back inside may revert toward the frozen session midpoint strongly enough to overcome costs. No profitability was assumed.
- Code commit: `120348d4a5df806f674551590610b216a9bc33ac`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic session high/low sweep-rejection; frozen 00:00–08:00 Europe/London midpoint range; strict rejection back inside; first signal only; signal-bar extreme stop; session-midpoint target; exact 16:00 flat.
- Features: frozen session midpoint high/low/midpoint and current midpoint sweep/rejection state.
- Parameters/search space: penetration buffers 0/2/5 pips; no alternate session or rescue grid.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: accepted Phase 3 policy unchanged: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: no promoted candidate; clearest split-only point USDJPY 5m / 2 pips had 337 development and 240 validation trades.
- Net return after costs: that point reversed from +1.9167% development to -15.4056% validation at baseline.
- Expectancy/trade: +$5.6874 development versus -$64.1899 validation.
- Profit factor: 1.0282 development versus 0.6706 validation.
- Max drawdown: 7.6380% development versus 16.7821% validation.
- Key subperiod results: zero of 27 pair/timeframe/buffer points cleared the required development-and-validation gate; two USDJPY 1h validation-only qualifiers failed development.
- Robustness/cost sensitivity: no baseline survivor, so downstream cost rows cannot rescue any point and remain evidence only.
- Result summary: merged-main benchmark run `34895426037` completed SUCCESS; 18/18 artifacts and 162/162 rows independently verified with zero ZIP/manifest/identity/grid/candidate-reuse/accounting/cost/risk errors.
- Conclusion: REJECT
- Reason: no exact predeclared buffer achieved positive net return, positive expectancy, and PF > 1 on both development and validation at 0.2-pip baseline.
- Follow-up: promote nothing; retain EXP-001 and EXP-005 candidates frozen unchanged. This completes all six planned Phase 4 baseline families. Detailed evidence: `docs/phase4-session-sweep-rejection-evidence.md`.

### EXP-20260915-007 — Phase 6 statistical / ML candidate filters

- Date: 2026-09-15
- Status: PASS
- Hypothesis: A predeclared supervised outcome model may filter lower-quality entries from either frozen Phase 4 serious rule candidate and improve financial quality without changing the strategy, execution, or fixed-risk contract. No model improvement was assumed.
- Code commit: `2dccb0f00d2a443bc41646ac1b3b494d81e1f13c`
- Data manifest/version: Phase 5 `fmp-feature-v1` checkpoint `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`; accepted USDJPY processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`; authoritative Phase 5 USDJPY 15m artifact `10374600839` ZIP `2e9b19935fc2699c94e5c3b91675c332892da9448e994438e479cf501e3c6215`; USDJPY 1h artifact `10374645600` ZIP `3db4d9d4fd4613c9e91f4c3fc1d815750038e33ea993608513066cec53aa617f`.
- Pair(s): USDJPY
- Timeframe(s): 15m session breakout and 1h volatility breakout
- Data range: accepted pre-2024 data only; fit 2015-2018 and selection 2019-2020 were opened. The predeclared 2021-2023 validation split remained unopened because neither strategy produced a qualifying selection-period challenger.
- Train period: fit 2015-01-01 through 2018-12-31 inclusive; selection 2019-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive, gated and not opened
- Final-test touched?: NO
- Strategy/model: unchanged USDJPY 15m session-breakout 5-pip/1.5x rule and USDJPY 1h volatility-breakout 2.0x/1.0R rule; exact L2 logistic regression and shallow histogram gradient boosting challengers.
- Features: exactly 48 frozen `fmp-feature-v1` values plus signal direction; exact observation/availability join; no outcome/PnL/future feature input.
- Parameters/search space: exactly two model families × retained fractions 0.75, 0.50, and 0.25 per strategy; cutoffs derived from fit scores only; no post-result widening, extra model, or rescue search.
- Random seed (if relevant): `20260915`
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2 pips per fill for selection; 0.5-pip validation robustness only for a selected challenger; 1.0 pip diagnostic only. Validation was not opened because no challenger survived selection.
- Risk assumptions: unchanged Phase 3 contract: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: selection rule baselines were 192 session-breakout trades and 222 volatility-breakout trades; no filtered candidate was promoted.
- Net return after costs: selection rule baselines were +3.8558% session breakout and +3.8457% volatility breakout at 0.2-pip adverse slippage. No session ML variant was fit; all six volatility filtered variants were below the volatility baseline net return.
- Expectancy/trade: selection rule baselines +$20.0822 session breakout and +$17.3228 volatility breakout. Best volatility filtered expectancy was +$21.0354 for logistic 0.50, but that variant still failed the all-conditions gate because its +2.7136% net return was below baseline.
- Profit factor: selection rule baselines 1.3010 session breakout and 1.2014 volatility breakout. No session model fit; volatility filtered PF ranged 0.9703 to 1.2101 and did not produce a qualifying all-conditions variant.
- Max drawdown: selection rule baselines 1.4390% session breakout and 1.4105% volatility breakout; drawdown improvement alone could not rescue a variant that failed another frozen selection condition.
- Key subperiod results: no validation subperiod result exists because DEC-031 forbids validation from rescuing a strategy without a qualifying selection-period challenger.
- Robustness/cost sensitivity: validation and the 0.5-pip robustness gate remained unopened for both strategies; no 1.0-pip diagnostic result was used.
- Result summary: authoritative run `34966406652` completed SUCCESS with double execution, byte-identical evidence, and locked pre-2024 coverage. Session breakout failed closed for both models on `ALL_NULL_FIT_COLUMN` / `minutes_since_new_york_open`, leaving all six variants not evaluated. Volatility breakout fit both models once, but all six variants failed selection and every variant had `net_return_beats_baseline = false`. Audited artifacts are session `10395810196` / ZIP `36cb9f80ca043da23250669dd974036eb9fb985c3f7f9ffd7844b9d99c96073d` and volatility `10395670751` / ZIP `0cf71a4d725fb1e609a512bb95aa13e4ad8771ae2b5864dd09e2833fe160a8d2`.
- Conclusion: REJECT
- Reason: neither frozen strategy produced a valid ML challenger under the predeclared selection protocol; `NO_ML_CHALLENGER` is the authoritative outcome for both.
- Follow-up: retain both frozen Phase 4 rule candidates unchanged, close Phase 6 as PASS because the deterministic leakage-safe experiment completed correctly with negative evidence preserved, create `fmp-v1-phase6-models` only after verified acceptance-closure merge, keep Phase 7 UNSTARTED, and keep the final-test period locked. Detailed evidence: `docs/phase6-ml-filter-evidence.md`.

### EXP-20260915-008 — Phase 7 walk-forward evaluation

- Date: 2026-09-15
- Status: PASS
- Hypothesis: Either frozen Phase 4 serious rule candidate may retain positive, cost-robust expectancy through a one-shot untouched 2024 out-of-sample gate and repeated 2025-2026 forward windows without parameter retuning or ML filtering. No viability was assumed.
- Code commit: Stage 1 `e33270de1f89757d1bf2a0d12ef40b2dc36bc110`; Stage 2 `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`.
- Data manifest/version: Phase 6 checkpoint `fmp-v1-phase6-models` / `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`; accepted Phase 2 USDJPY artifact `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`; accepted USDJPY processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): USDJPY
- Timeframe(s): 15m session breakout and 1h volatility breakout
- Data range: Stage 1 opened bounded 2023-12 warm-up context plus scored 2024; Stage 2 for the sole survivor opened only the exact seven frozen forward windows plus each immediate seven-day warm-up, covering scored 2025-01-01 through 2026-08-20 inclusive.
- Train period: not applicable; both strategies are fixed rules and no Phase 7 refit or optimization is authorized.
- Validation period: Stage 1 one-shot OOS gate 2024-01-01 through 2024-12-31; Stage 2 seven frozen independent forward windows 2025-Q1 through 2026-partial-Q3 for the sole Stage 1 survivor.
- Final-test touched?: YES — Stage 1 2024 and Stage 2 2025-2026
- Strategy/model: unchanged USDJPY 15m session breakout, 5-pip buffer, 1.5x target range; unchanged USDJPY 1h volatility breakout, 2.0x range expansion, fixed 1.0R target; no ML overlay.
- Features: existing strategy-native midpoint OHLC/reference logic only; historical BID/ASK remains the execution source of truth; Phase 5 model features are not used.
- Parameters/search space: no search space. Candidate identities and parameters remained frozen exactly; no neighboring-parameter substitution, rescue search, candidate replacement, or post-result threshold change.
- Random seed (if relevant): not applicable; deterministic fixed-rule evaluation.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: exactly 0.2, 0.5, and 1.0 pips adverse per fill; 0.2 and 0.5 are gating, 1.0 is diagnostic only.
- Risk assumptions: unchanged Phase 3 contract: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt; every Stage 1/Stage 2 evaluation window starts independently at $100,000 as specified.
- Trade count: Stage 1 `session_breakout` 122 trades at each cost and `volatility_breakout` 103 trades at each cost. Stage 2 `session_breakout` completed 199 trades across the seven independent windows at each cost.
- Net return after costs: Stage 1 `session_breakout` +1.383287% / +1.102509% / +0.636234% at 0.2 / 0.5 / 1.0 pips; Stage 1 `volatility_breakout` -2.603768% / -3.051558% / -3.793353%. Stage 2 `session_breakout` aggregate +0.757266% at 0.2 pips and +0.262176% at 0.5 pips; the 1.0-pip diagnostic is -0.562118%.
- Expectancy/trade: Stage 2 `session_breakout` +$3.8054 at 0.2 pips and +$1.3175 at 0.5 pips; 1.0-pip diagnostic -$2.8247.
- Profit factor: Stage 2 `session_breakout` 1.062731 at 0.2 pips and 1.021310 at 0.5 pips; 1.0-pip diagnostic 0.955760.
- Max drawdown: Stage 2 maximum independent-window drawdown 1.140640% at 0.2 pips, 1.170046% at 0.5 pips, and 1.219045% in the 1.0-pip diagnostic.
- Key subperiod results: at 0.2 pips, five of seven Stage 2 windows have positive net PnL. The two negative windows are 2025-Q1 (-0.520185%) and 2026-partial-Q3 (-0.645978%). The maximum positive-window contribution is 35.061843%, below the frozen 50% concentration ceiling.
- Robustness/cost sensitivity: Stage 2 remains positive with PF > 1, positive expectancy, and sub-5% drawdown at both mandatory 0.2- and 0.5-pip costs. The negative 1.0-pip diagnostic is retained as material cost-sensitivity evidence and does not change the frozen outcome because DEC-033 explicitly defines it as non-gating.
- Result summary: Stage 1 run `35013047267` produced `session_breakout` `STAGE1_PASS` artifact `10414407590` / ZIP `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb` and `volatility_breakout` `STAGE1_REJECT` artifact `10414905151` / ZIP `5ee8b6b96382741f454d2b72a6ae6de04e85c9eca04c17ac846c0d594fd27d24`. Authoritative Stage 2 run `35015277625` on exact merged-main SHA `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d` completed SUCCESS after verifying the exact Stage 1 PASS package before source I/O, re-verifying accepted Phase 2 identity, executing twice with byte-identical complete evidence, independently validating all 21 window rows, and recomputing the gate. Stage 2 artifact `10414817824` has ZIP SHA-256 `2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4`; final status `PHASE7_PROMOTE_TO_SHADOW_DESIGN`. Detailed evidence: `docs/phase7-stage1-evidence.md` and `docs/phase7-walk-forward-evidence.md`.
- Conclusion: PROMOTE
- Reason: `session_breakout` is the sole frozen candidate to pass the one-shot Stage 1 gate and then every mandatory Stage 2 aggregate/stability criterion without retuning, refitting, rescue search, or protocol changes. `volatility_breakout` remains rejected from Stage 1. The successful mandatory costs are accompanied by a negative 1.0-pip diagnostic, which remains a deployment-cost limitation rather than a failed predeclared gate.
- Follow-up: close Phase 7 as PASS after the acceptance evidence/state change is merged and freshly verified on `main`; create checkpoint `fmp-v1-phase7-walk-forward` at that verified closure commit. The surviving `session_breakout` is eligible for Phase 8 shadow design only. Phase 8 remains UNSTARTED, and broker/demo/live/real-money trading remain locked.


### EXP-20260915-009 — Phase 8 live shadow evaluation

- Date: 2026-09-15
- Status: INCONCLUSIVE
- Connector transition: STOPPED BEFORE QUALIFICATION — OANDA Practice account unavailable to the operator jurisdiction; no qualification or scored live-shadow campaign occurred.
- Hypothesis: The sole Phase 7 survivor may preserve materially comparable timing, spread conditions, operational integrity, and positive hypothetical after-cost behavior when driven by real-time OANDA Practice USD_JPY quotes without any broker order-submission capability. No live viability is assumed.
- Code commit: source-of-truth activation commit first; shadow runtime implementation commits and accepted campaign code identity will be recorded as they are verified.
- Data manifest/version: upstream Phase 7 checkpoint `fmp-v1-phase7-walk-forward` / `b6fb0176555b071fef6d1070edf3407b03cd60c9`; accepted Phase 2 USDJPY artifact `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`; processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`; live evidence uses the Phase 8 append-only evidence protocol and manifest defined by DEC-036.
- Pair(s): USDJPY only; provider instrument `USD_JPY`.
- Timeframe(s): frozen 15m session breakout; 1m shadow-live bars are an operational construction input only.
- Data range: future explicitly registered live-shadow campaign only; no hidden historical backfill is permitted after campaign gaps.
- Train period: not applicable; fixed rule, no fitting or optimization.
- Validation period: live campaign after frozen connector qualification/implementation verification; acceptance review requires the predeclared minimum sample/time/coverage gates.
- Final-test touched?: YES upstream in Phase 7; Phase 8 itself opens no additional historical final-test search and performs no retuning.
- Strategy/model: unchanged USDJPY 15m `session_breakout`, 5-pip buffer, 1.5x target range, exact London timing, no ML overlay.
- Features: strategy-native midpoint/session structure only; no Phase 5 model features or new predictive features.
- Parameters/search space: none. Provider/environment, method/host/path/instrument, stale threshold, quote deadlines, bar completeness, cost scenarios, risk settings, historical spread-reference method, sample minimums, and acceptance thresholds are frozen by DEC-036.
- Random seed (if relevant): not applicable; deterministic fixed-rule shadow/replay pipeline.
- Spread/cost model: observed live bid/ask spread plus zero commission and zero financing for the mandatory intraday-flat strategy.
- Slippage model: exactly 0.2, 0.5, and 1.0 pips adverse per fill; 0.2 and 0.5 are gating, 1.0 is diagnostic only.
- Risk assumptions: unchanged Phase 3 policy — 0.25% default requested risk, 0.50% hard per-trade maximum, 1.00% simultaneous open-risk maximum, 1.50% UTC day-start realized-loss halt; independent $100,000 virtual account per cost scenario.
- Trade count: pending live campaign; at least 40 completed financially scorable 0.2-pip trades are required before acceptance review.
- Net return after costs: pending.
- Expectancy/trade: pending.
- Profit factor: pending.
- Max drawdown: pending.
- Key subperiod results: pending; acceptance also requires at least 8 elapsed calendar weeks, at least 30 fully observed London dates, and at least 90% valid denominator-date coverage.
- Robustness/cost sensitivity: pending; mandatory gates apply at 0.2 and 0.5 pips while 1.0 pip remains diagnostic.
- Result summary: STOPPED BEFORE QUALIFICATION. The required OANDA Practice account was unavailable to the operator jurisdiction, so no qualification or scored live-shadow campaign occurred. DEC-037 supersedes only the connector path and preserves this negative operational evidence.
- Conclusion: NEED_MORE_DATA
- Reason: the OANDA connector path could not be qualified and produced no scored campaign evidence.
- Follow-up: preserve this record as stopped operational history; continue Phase 8 only under `EXP-20260917-010` and DEC-037. Keep Phase 9/demo/live-order/real-money paths locked.

### EXP-20260917-010 — Phase 8 MT5 demo live-shadow evaluation

- Date: 2026-09-17
- Status: INCONCLUSIVE / STOPPED FOR LIVENESS AMENDMENT
- Hypothesis: The unchanged Phase 7-promoted USDJPY 15m session-breakout rule can be evaluated prospectively using a read-only FP Markets MT5 demo quote bridge without changing strategy, execution-simulation, risk, or acceptance semantics.
- Code commit: UTC-correct campaign implementation `97715805498784badcb617debabc2b81c15cf5a8`.
- Data manifest/version: historical reference remains bound to accepted Phase 2 USDJPY identity and Phase 7 checkpoint; live evidence protocol `fmp-phase8-shadow-evidence-v2`.
- Pair(s): USDJPY only
- Timeframe(s): 15m strategy bars built from live 1m bid/ask bars
- Data range: prospective live-shadow diagnostic capture only; no backfill.
- Train period: not applicable; fixed rule, no refit.
- Validation period: prospective Phase 8 registered campaign.
- Final-test touched?: YES upstream in Phase 7; Phase 8 itself is prospective and performs no historical retuning.
- Strategy/model: unchanged `session_breakout`, 5-pip buffer, 1.5x target-range multiple, London-session/DST semantics, exact 16:00 `Europe/London` flat, no ML overlay.
- Features: live bid/ask quote stream only; no new feature/model fitting.
- Parameters/search space: none.
- Random seed (if relevant): not applicable.
- Spread/cost model: observed live demo bid/ask spread; zero commission and zero financing.
- Slippage model: 0.2, 0.5, and 1.0 adverse pips per fill; 0.2/0.5 gating, 1.0 diagnostic.
- Risk assumptions: existing Phase 3 risk policy unchanged; three independent $100,000 virtual scenarios.
- Trade count: no scored acceptance result; this experiment is diagnostic only.
- Net return after costs: not scored for acceptance.
- Expectancy/trade: not scored for acceptance.
- Profit factor: not scored for acceptance.
- Max drawdown: not scored for acceptance.
- Key operational result: clean UTC-source-time qualification passed, and the live bridge/capture remained active. Diagnostic quote-gap analysis over 46,721 normalized quotes found 102 gaps above 15 seconds, 23 above 30 seconds, 3 above 60 seconds, and a maximum gap of 4,301.580 seconds. During the long approximately 10:18–11:30 UTC no-tick interval on 2026-09-21, 870 valid bridge heartbeats continued.
- Result summary: the original live runner treated any 15-second market no-tick interval as a whole-date stale continuity failure even when the bridge remained healthy. That behavior made valid-date eligibility depend on tick sparsity and invalidated the first prospective Tuesday within minutes. The issue is a liveness-protocol defect, not evidence for or against strategy profitability.
- Conclusion: NEED_MORE_DATA
- Reason: DEC-038 amends live-capture liveness semantics; evidence collected under the superseded EXP-010 runner semantics cannot be reclassified or counted toward the amended campaign.
- Follow-up: preserve EXP-010 evidence for audit. Continue only with fresh `EXP-20260922-011` qualification/reference/registration after the DEC-038 implementation is merged and verified.

### EXP-20260922-011 — Phase 8 MT5 demo live-shadow evaluation with separated bridge/market liveness

- Date: 2026-09-22
- Status: STOPPED BEFORE REGISTRATION / SUPERSEDED BY PHASE 8A
- Protocol decision: DEC-038 APPROVED
- Hypothesis: The unchanged Phase 7-promoted USDJPY 15m session-breakout rule can be evaluated prospectively when true bridge continuity failures are separated from heartbeat-healthy no-tick intervals, while unseen trade paths and missing strategy context still fail closed.
- Code commit: DEC-038 implementation merged by PR #119 to `main` at `71fca1ccbfd14edd71c736f61187558f6f6a7909`; all qualification/reference/campaign evidence must bind this merged implementation identity.
- Data manifest/version: accepted Phase 2 USDJPY artifact `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`; processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`; Phase 7 checkpoint `fmp-v1-phase7-walk-forward` / `b6fb0176555b071fef6d1070edf3407b03cd60c9`; live evidence protocol remains `fmp-phase8-shadow-evidence-v2`.
- Pair(s): USDJPY only
- Timeframe(s): 15m strategy bars built from observed live 1m bid/ask bars
- Data range: fresh prospective live-shadow campaign only after new qualification and registration; no EXP-010 evidence is scored or backfilled.
- Train period: not applicable; fixed rule, no refit.
- Validation period: prospective Phase 8 registered campaign.
- Final-test touched?: YES upstream in Phase 7; Phase 8 remains prospective, not historical retuning.
- Strategy/model: unchanged `session_breakout`, 5-pip buffer, 1.5x target-range multiple, London-session/DST semantics, exact 16:00 `Europe/London` flat, no ML overlay.
- Features: live bid/ask quote stream only.
- Parameters/search space: none.
- Random seed (if relevant): not applicable.
- Spread/cost model: observed live demo bid/ask spread; zero commission and zero financing.
- Slippage model: exactly 0.2, 0.5, and 1.0 adverse pips per fill; 0.2/0.5 gating, 1.0 diagnostic.
- Risk assumptions: unchanged Phase 3 policy; independent $100,000 virtual account per scenario.
- Liveness semantics: 15-second bridge silence remains date-invalidating `stale`; 15-second no-tick intervals with healthy bridge records emit `market_quiet` and do not by themselves invalidate the date. Open simulated positions crossing such a gap become `OUTCOME_UNKNOWN_AFTER_GAP`; missing required bars remain incomplete; 5-second entry/scheduled-exit quote deadlines remain frozen.
- Campaign minimums: at least 8 elapsed calendar weeks, 30 fully observed London dates, 40 completed scorable 0.2-pip trades, and at least 90% valid denominator-date coverage, plus all existing timing/spread/financial/replay/safety gates.
- Trade count: no EXP-011 campaign was registered; zero scored campaign trades.
- Net return after costs: not scored.
- Expectancy/trade: not scored.
- Profit factor: not scored.
- Max drawdown: not scored.
- Result summary: DEC-038 implementation and source-free verification passed. The operator then completed a fresh local qualification under code commit `5cb884dfb15d7798b023658e025221a38dfec9fc`: PASS, 100 prices, 15 heartbeats, zero rejection codes, max bridge/market liveness gap 3.884147625s. A fresh historical reference was also built under the same commit with SHA-256 `e920b3254235d2bb0766762551b5eb9d21439d429c59aebd14c3e4bb16e8cc64` and 199 historical trades. Before campaign registration, the operator rejected the economic case for evaluating this strategy alone and approved DEC-039.
- Conclusion: STOPPED
- Reason: research objective changed before campaign registration; the sole Phase 7 strategy is too economically weak for the operator's revised multi-strategy/high-return objective despite having passed its prior robustness gate.
- Follow-up: preserve qualification/reference and all EXP-009/010/011 evidence; do not register or start EXP-011. Continue under EXP-20260922-012 / Phase 8A.


### EXP-20260922-012 — Phase 8A multi-pair, multi-strategy portfolio research

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION
- Protocol decisions: DEC-039 APPROVED; DEC-040 APPROVED for joint-account retrospective simulation
- Hypothesis: a versioned portfolio of independently tested strategies across EURUSD, GBPUSD, and USDJPY can materially improve capital utilization and the economic return profile relative to the sole Phase 7 USDJPY 15m session-breakout strategy without relying on martingale, loss chasing, hidden leverage escalation, or hot-swapped self-modification.
- Code commit: implementation branch begins from `5cb884dfb15d7798b023658e025221a38dfec9fc`; exact result-producing commit(s) will be recorded as the experiment progresses.
- Data manifest/version: accepted Phase 1/2 Dukascopy EURUSD/GBPUSD/USDJPY canonical 1m BID/ASK histories plus deterministic 5m/15m/1h derived bars. Existing accepted manifests/checksums remain authoritative.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h where each strategy contract is valid.
- Data range: accepted historical coverage through 2026-08-20 for retrospective research/robustness; later prospective observations only after a challenger version is frozen.
- Train period: strategy-specific and must be predeclared before each new experiment result is inspected.
- Validation period: strategy-specific chronological validation / retrospective walk-forward; no post-Phase-7 strategy may call 2024-2026 an untouched final test.
- Final-test touched?: YES — the former final-test period was already opened by Phase 7.
- Strategy/model: multi-strategy library; initial research reuses implemented baseline families and may add new predeclared strategy/regime experiments. No strategy version may mutate in place after its evidence identity is frozen.
- Features: existing canonical bars and leakage-safe Phase 5 features may be used only under explicit experiment protocols; future information remains forbidden.
- Parameters/search space: each strategy/version search surface must be predeclared in its own experiment record before promotion use. Earlier rejected parameter points remain rejected under their original experiments.
- Random seed (if relevant): experiment-specific and recorded when stochastic methods are used.
- Spread/cost model: historical BID/ASK spread remains authoritative; 0.2/0.5/1.0-pip adverse-slippage views remain the default sensitivity set unless a later strategy-specific decision justifies a different executable model.
- Risk assumptions: existing Phase 3 risk contract remains the default: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous open-risk max, 1.50% UTC day-start realized-loss halt. Portfolio exposure/correlation controls are added above, not around, this risk engine.
- Economic objective: materially improve on the Phase 7 single-strategy economic case. The operator's aspiration includes possible +10% days; the experiment measures the frequency and risk required for such days rather than assuming or guaranteeing them.
- Required reporting: daily return distribution, monthly/annualized net return, expectancy, profit factor, max drawdown, losing streaks, tail/concentration diagnostics, trade count, cost sensitivity, and contribution by pair/strategy/timeframe/session/regime.
- Continuous-learning rule: new observations may create challengers, but active champions are immutable during registered campaigns. No challenger can automatically replace a champion or authorize demo/live orders.
- Trade count: pending implementation and research runs.
- Net return after costs: pending.
- Expectancy/trade: pending.
- Profit factor: pending.
- Max drawdown: pending.
- Conclusion: NEED_MORE_DATA
- Implementation progress: PR #121 merged the registry/lifecycle/router and explicit retrospective evaluator; PR #122 merged the deterministic retrospective batch/CLI/manual 3-pair × 3-timeframe workflow; PR #123 merged the DEC-040 shared-account simulator with 1m execution, time-local conflict routing, and a single Phase 3 risk state. PR #122 pre-merge verification completed with 819 tests PASS; PR #123 pre-merge verification completed with 828 tests PASS; unchanged Phase 3 acceptance passed for both.
- Joint-simulation protocol: DEC-040 freezes canonical 1m BID/ASK as the execution path, strategy-native 5m/15m/1h bars as the signal path, one shared $100,000 account/risk state per slippage scenario, and time-local same-symbol conflict handling. These results remain `RETROSPECTIVE_ALREADY_SEEN` and cannot authorize promotion.
- Follow-up: complete deterministic joint evidence packaging and explicit-fingerprint manual CLI. After that evidence layer is green, predeclare a separate portfolio-selection protocol before any historical combination search or winner selection is allowed. Phase 8B live shadow remains locked until Phase 8A acceptance.


### EXP-20260922-013 — Phase 8A opening-range momentum challenger round 1

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION / NO BENCHMARK RESULTS INSPECTED
- Protocol decision: DEC-041 APPROVED / PREDECLARED
- Hypothesis: a breakout of the 06:00–08:00 London opening range may carry more persistent intraday information when the breakout candle also shows directional body conviction, producing a more robust multi-pair edge than an unfiltered range break.
- Family/version: `opening_range_momentum` / `fmp-opening-range-momentum-v1`
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Reference window: 06:00–08:00 `Europe/London`
- Signal window: 08:00–12:00 `Europe/London`
- Mandatory flat: exact 16:00 `Europe/London`
- Fixed buffer: 2 pips
- Fixed stop geometry: 0.25 reference-range depth inside the breached boundary
- Parameters/search space: `body_fraction_threshold ∈ {0.50, 0.70}`; `target_r_multiple ∈ {1.0, 1.5}`; exactly 36 pair/timeframe/configuration identities
- Stage A development: 2015-01-01 through 2020-12-31 inclusive
- Stage A validation: 2021-01-01 through 2023-12-31 inclusive
- Stage B retrospective confirmation: 2024-01-01 through 2026-08-20 inclusive, only for exact Stage A survivors
- Final-test touched?: YES upstream; all EXP-013 evidence is retrospective and Stage B must not be labeled untouched OOS
- Spread/cost model: historical BID/ASK plus 0.2/0.5/1.0-pip adverse-slippage scenarios; 0.2 and 0.5 mandatory, 1.0 diagnostic
- Commission/financing: zero / zero under mandatory intraday flat
- Risk assumptions: unchanged Phase 3 risk — $100,000 starting equity, 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous risk max, 1.50% UTC daily realized-loss halt
- Stage A gate: positive net return/expectancy/PF>1.0 and DD<=5% at 0.2 and 0.5 on both development and validation; at least 100 development and 50 validation 0.2-pip trades; at least one same-pair/timeframe neighboring grid point must also pass mandatory profitability/drawdown gates
- Stage B gate: positive net return/expectancy/PF>1.0 and DD<=5% at both 0.2 and 0.5; at least 75 completed 0.2-pip trades
- Trade count: pending implementation and benchmark
- Net return after costs: pending
- Expectancy/trade: pending
- Profit factor: pending
- Max drawdown: pending
- Conclusion: NEED_MORE_DATA
- Implementation status: PR #125 merged the signal contract, 36 challenger identities, Stage A cell runner, and frozen gate logic. PR #128 merged deterministic Stage A development/validation/gate artifacts, nine-cell authorization aggregation, and the frozen manual Stage A workflow. PR #129 merged strategy-source SHA-256 binding plus the guarded Stage B confirmation runner/workflow. PR #128 verified 868 tests PASS; PR #129 verified 875 tests PASS; unchanged Phase 3 acceptance passed for both. No EXP-013 Stage A or Stage B historical workflow has been dispatched.
- Follow-up: deliberately dispatch Stage A only when an authorized workflow-dispatch path is available. No Stage B source may open unless the resulting nine-cell authorization artifact explicitly lists one or more exact survivor fingerprints and the opening-range strategy source SHA-256 still matches.


### EXP-20260922-014 — Phase 8A frozen portfolio selection

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION ONLY / SEARCH BLOCKED
- Protocol decision: DEC-042 APPROVED
- Hypothesis: if Phase 8A produces at least two independently qualified immutable strategies, a bounded shared-account portfolio chosen under predeclared stability, concentration, cost, drawdown, and deterministic ranking rules can improve the economic case without post-result threshold changes.
- Eligible lifecycle states: HISTORICAL_QUALIFIED, SHADOW_CANDIDATE, SHADOW_VALIDATED, DEMO_ELIGIBLE only.
- Current eligible baseline count: 1 — the existing Phase 7 USDJPY 15m session-breakout survivor.
- Search status: BLOCKED until at least one additional immutable challenger reaches HISTORICAL_QUALIFIED under a separate predeclared discovery/qualification experiment.
- Pool bounds: 2 to 12 eligible strategies.
- Portfolio cardinality: evaluate all unique unordered sets of 1 through 6; 1-strategy sets are controls only.
- Retrospective selection range: 2019-01-01 inclusive through 2026-08-21 exclusive.
- Execution: DEC-040 shared $100,000 account, canonical 1m BID/ASK execution, native 5m/15m/1h signal bars, unchanged Phase 3 risk.
- Slippage scenarios: exactly 0.2, 0.5, and 1.0 pips adverse per fill; 0.2/0.5 gating, 1.0 diagnostic.
- Mandatory gates: positive net return/expectancy, PF > 1.0, max drawdown <= 5%, and >=200 trades at both gating costs; additional 0.2-pip yearly-stability, strategy/pair concentration, and diversity gates per DEC-042.
- Ranking: immutable lexicographic order frozen in DEC-042; no tunable score weights.
- Evidence label: RETROSPECTIVE_ALREADY_SEEN.
- Untouched OOS?: NO.
- Promotion authorized?: NO.
- Trade count: not run.
- Net return after costs: not run.
- Expectancy/trade: not run.
- Profit factor: not run.
- Max drawdown: not run.
- Conclusion: NEED_MORE_DATA
- Implementation status: PR #133 merged the guarded DEC-042 runner and manual workflow to `main` at `a10bf42b75b48c300ac48edaa6616a4af6fa2e9c` after 910 tests PASS, compile PASS, and unchanged Phase 3 acceptance PASS. It reconstructs the Phase 7 baseline + exact EXP-015 HISTORICAL_QUALIFIED shortlist, binds the EXP-015 final artifact by SHA-256, freezes the complete 1–6 strategy set universe before historical source download, evaluates only that immutable universe, converts joint evidence to frozen DEC-042 metrics, and emits deterministic winner/no-winner evidence. A zero-trade scenario represents expectancy as null and therefore fails the positive-expectancy gate rather than raising.
- Execution status: SEARCH BLOCKED / NOT RUN. EXP-015 Stage A/B/C are still undispatched, so no eligible challenger pool exists yet. A 12-strategy pool would enumerate 2,509 sets and 7,527 cost runs; practical sharding/caching may be added without changing the frozen set universe or gates before any large-pool dispatch.
- Follow-up: preserve source-free dispatch guards and do not run DEC-042 until an exact successful EXP-015 final shortlist produces at least one new HISTORICAL_QUALIFIED challenger.


- Identity correction: initially recorded with duplicate EXP-013 / DEC-041 identifiers already assigned to opening_range_momentum; renumbered before any portfolio combination search or result.

### EXP-20260922-015 — Phase 8A rule-based challenger discovery

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION / NO HISTORICAL STAGE RUN YET
- Protocol decisions: DEC-043 APPROVED; DEC-044 APPROVED BEFORE ANY HISTORICAL STAGE
- Hypothesis: new predeclared parameter regions of the existing deterministic rule families can produce additional robust immutable challengers across EURUSD, GBPUSD, and USDJPY without reviving rejected Phase 4 points or tuning after later-period observation.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Families: session_breakout, trend_continuation, mean_reversion, previous_day_rejection, volatility_breakout, session_sweep_rejection
- Frozen candidate count: 567 new configurations, all non-overlapping with the original Phase 4 parameter grid.
- Stage A: 2015-01-01 to 2019-01-01 exclusive; all 567 candidates; 54 exact pair/family/timeframe ranking cells; at most 2 survivors per cell; absolute maximum 108 survivors under DEC-044.
- Stage B: 2019-01-01 to 2023-01-01 exclusive; only Stage A survivors; no retune.
- Stage C: 2023-01-01 to 2026-08-21 exclusive; only Stage B passers; no retune.
- Cost model: 0.2/0.5/1.0 pips adverse per fill; 0.2/0.5 gating, 1.0 diagnostic.
- Risk: unchanged Phase 3 defaults; $100,000 starting equity per independent strategy/scenario run; 0.25% requested risk.
- Final shortlist: at most 11 new HISTORICAL_QUALIFIED challengers under frozen cross-pair/family/cell caps.
- Evidence label: RETROSPECTIVE_ALREADY_SEEN
- Untouched OOS?: NO
- Broker/shadow promotion authorized?: NO
- Stage A opened?: NO
- Stage B opened?: NO
- Stage C opened?: NO
- Trade count: not run.
- Net return after costs: not run.
- Expectancy/trade: not run.
- Profit factor: not run.
- Max drawdown: not run.
- Conclusion: NEED_MORE_DATA
- Implementation status: PR #130 merged the validator-region + exact 567-identity catalog at `7e3eac44a14815ab65b1f85af9e2469517ed3efb` after 880 tests PASS and unchanged Phase 3 acceptance PASS. DEC-044 corrected the pre-run Stage A survivor arithmetic from 54 to 108 while retaining at most 2 survivors in each of 54 exact ranking cells. PR #131 merged the Stage A preflight catalog freeze, exact 63-strategy/189-scenario pair-timeframe cells, deterministic family rankings, richer gate/ranking authorization evidence, and manual Stage A workflow at `bde29280d08cf347265ea06f186972a61f2561f4` after 891 tests PASS, compile PASS, and unchanged Phase 3 acceptance PASS. No EXP-015 historical stage has been dispatched.
- Implementation status continued: PR #132 merged guarded Stage B/C execution and final deterministic shortlist/lifecycle accounting to `main` at `3d36368811e155d41d45b73313827bca83a66518` after 898 tests PASS, compile PASS, and unchanged Phase 3 acceptance PASS. Stage B/C validate upstream artifact hashes, runner commits, catalog/source digests, processed manifests, yearly gates, and candidate-sequence identity before downstream source access. Finalization applies the frozen Stage B/C ranking and 11-total / 4-per-pair / 3-per-family / 2-per-cell caps, then records one explicit lifecycle disposition for all 567 candidates.
- Follow-up: keep Stage A/B/C undispatched until an authorized workflow-dispatch path is available; all downstream stages remain cryptographically gated by exact upstream artifacts and the authoritative workflows must run only from merged `main`.
- Identity correction: initially drafted as EXP-014 / DEC-042 during reconciliation; renumbered before any historical stage or benchmark result.


### EXP-20260922-016 — Phase 8A acceptance review

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION ONLY / NO ACCEPTANCE RESULT
- Protocol decision: DEC-045 APPROVED BEFORE ANY DEC-042 SELECTION RESULT
- Purpose: deterministically review exact DEC-042 preflight/selection evidence and either freeze one immutable multi-strategy shadow candidate or record a credible Phase 8A research rejection.
- Inputs: exact successful DEC-042 manual run from main; exact preflight.json and selection.json bytes and SHA-256 values; exact frozen Phase 7 baseline control in the DEC-042 pool.
- Economic-improvement gate: the DEC-042 selected portfolio must already pass all frozen DEC-042 gates and have strictly higher 0.5-pip annualized compounded return than the Phase 7 baseline control over the same 2019-01-01..2026-08-21 selection range.
- Acceptance outcome: selected strategy records transition exactly HISTORICAL_QUALIFIED -> SHADOW_CANDIDATE and an immutable champion/shadow-candidate set is frozen.
- Rejection outcome: no lifecycle transition; Phase 8B remains locked.
- No new historical data may be opened and no strategy/backtest may run under EXP-016.
- Evidence remains RETROSPECTIVE_ALREADY_SEEN; untouched_oos = false.
- Broker/demo/live/real-money promotion remains false.
- Historical run status: NOT RUN.
- Implementation status: current `phase8a/acceptance-review` branch contains the deterministic acceptance compiler, lifecycle/champion-set freeze, resolver, artifact writer, CLI, guarded main-only manual workflow, exact DEC-042 upstream provenance/artifact binding, full repository/compile checks, and deterministic Phase 3 verification before artifact creation. No DEC-042 or DEC-045 historical/result workflow has been dispatched.
- Follow-up: source-free verify and merge the DEC-045 implementation; only then may a future successful DEC-042 run be reviewed.


### EXP-20260922-017 — Phase 8B shadow design

- Date: 2026-09-22
- Status: ACTIVE — DESIGN IMPLEMENTATION ONLY / NO CAMPAIGN
- Protocol decision: DEC-046 APPROVED BEFORE ANY PHASE 8B CAMPAIGN
- Purpose: compile an exact accepted DEC-045 shadow candidate into an immutable multi-symbol read-only Phase 8B design without opening a live campaign.
- Required input: exact `PHASE8A_SHADOW_CANDIDATE_ACCEPTED` DEC-045 artifact.
- Supported symbols: EURUSD / GBPUSD / USDJPY only; exact required subset derived from accepted champion set.
- Intended connector topology: one read-only MT5 EA per required symbol chart; fixed FILE_COMMON feed per symbol; common demo account fingerprint/server; no arbitrary path/symbol override; no broker-order surface.
- Liveness: DEC-038 bridge/market separation retained independently per required symbol.
- Campaign registration authorized?: NO.
- Campaign start authorized?: NO.
- Demo/live/broker mutation/real-money/Phase 9 authorized?: NO.
- Historical/live run status: NOT RUN.
- Implementation status: current `phase8b/design-contract` branch contains the deterministic design compiler/validator/artifact writer, source-free CLI, guarded main-only manual workflow, and tests that derive the exact symbol/file topology from an accepted DEC-045 champion set while keeping campaign/order authorizations false.
- Follow-up: source-free verify/merge DEC-046 design implementation, then separately freeze and implement multi-symbol MT5 bridge qualification/registration before any Phase 8B campaign can start.


### EXP-20260922-018 — Phase 8B bridge qualification and registration

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION ONLY / NO CAMPAIGN
- Protocol decision: DEC-047 APPROVED BEFORE ANY PHASE 8B CAMPAIGN
- Purpose: implement the separate multi-symbol read-only MT5 bridge, per-symbol qualification, cross-feed identity gate, and immutable registration boundary for an accepted DEC-046 design.
- Bridge protocol: fmp-mt5-demo-multisymbol-file-bridge-v1.
- Required feeds: exact DEC-046 symbol subset only, using fixed FILE_COMMON files.
- Per-symbol qualification: <=600 seconds, >=100 prices, >=6 heartbeats, bridge gap <=15 seconds, market gap <=15 seconds during qualification, source-time skew <=5 seconds.
- Multi-symbol PASS: every required symbol PASS; same approved demo account fingerprint/server; distinct bridge session IDs; exact required-symbol coverage.
- Qualification PASS authorizes registration only.
- Campaign start authorized?: NO.
- Demo/live/broker mutation/real-money/Phase 9 authorized?: NO.
- Runtime status: NOT RUN.
- Implementation status: current `phase8b/bridge-qualification-registration` branch contains the separate multi-symbol bridge parser/session validator/file-tail discovery, read-only Phase 8B MT5 EA, exact legacy-threshold per-symbol qualification, cross-feed account/server/session gate, deterministic qualification evidence, immutable exactly-once registration, and CLI/tests exposing only `design`, `qualify`, and `register`. No `run`/capture/start command exists.
- Follow-up: source-free verify/merge DEC-047. A later separately frozen decision is still required before any Phase 8B live-shadow segment may start.


### EXP-20260922-019 — Phase 8B campaign start authorization

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION ONLY / NO LIVE-SHADOW SEGMENT
- Protocol decision: DEC-048 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: verify that the currently visible multi-symbol MT5 bridge sessions still exactly match one immutable DEC-047 campaign registration, freeze the prospective start boundary, and establish EOF-only reader semantics before any later capture runtime may begin.
- Input: exact valid `fmp-phase8b-campaign-registration-v1` artifact and its SHA-256; fixed required-symbol bridge files only.
- Start gate: every required symbol's active `BRIDGE_START` must match the registration on symbol, protocol, bridge session, account fingerprint, and server; required coverage must be exact.
- Reader semantics: `TAIL_AT_EOF_NO_BACKFILL`; all pre-reader transport content is excluded from future prospective evidence.
- Frozen boundary: explicit UTC start timestamp plus derived `Europe/London` first date, registration/champion/strategy identities, bridge sessions, liveness, quote deadline, and slippage scenarios.
- Authorized on PASS: `campaign_start_authorized = true`; `prospective_capture_authorized = true`.
- Still forbidden: promotion, demo/live orders, broker mutation, real money, Phase 9.
- CLI scope: add only `authorize-start`; no `run`, `start`, `capture`, or `review` command under DEC-048.
- Implementation status: the current DEC-048 branch adds deterministic registration/session revalidation, London start-date freezing, `TAIL_AT_EOF_NO_BACKFILL`, start-authorization fingerprinting, exactly-once artifacts, and the sole new CLI command `authorize-start`. The implementation contains no prospective capture loop.
- Historical/live execution status: NOT RUN.
- Follow-up: merge DEC-048 only after the final exact branch head passes the repository suite, compile checks, and unchanged Phase 3 acceptance. A later separately frozen capture/replay/acceptance protocol must independently revalidate DEC-048 evidence before any live-shadow segment can begin.


### EXP-20260922-020 — Phase 8B prospective capture foundation

- Date: 2026-09-22
- Status: ACTIVE — SOURCE-FREE IMPLEMENTATION MERGED / NO LIVE-SHADOW SEGMENT
- Protocol decision: DEC-049 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: freeze and implement the exact source-free boundary between DEC-048 campaign-start authorization and a later live capture/replay/acceptance runtime.
- Required inputs: one exact valid DEC-047 `fmp-phase8b-campaign-registration-v1` artifact plus one exact valid DEC-048 `fmp-phase8b-campaign-start-v1` artifact.
- Upstream binding: exact registration/start-artifact SHA-256 values and semantic equality for champion set, strategies, symbols/timeframes, connector identity, fixed bridge files, account/server, bridge sessions, liveness, slippage, and all safety authorization flags.
- Fresh-session gate: every required-symbol bridge is independently revalidated from a fresh EOF-tailing reader against the frozen registration/start identity.
- Reader semantics: `TAIL_AT_EOF_NO_BACKFILL`.
- New source-free artifact: `fmp-phase8b-capture-preflight-v1`, with deterministic fingerprint and `capture_runtime_ready = true` while `live_shadow_segment_started = false`.
- Raw envelope: `fmp-phase8b-capture-record-v1` freezes deterministic post-preflight TICK/HEARTBEAT serialization with receive UTC/monotonic metadata and existing bridge-session duplicate/source-time/identity validation.
- CLI scope: unchanged; no `capture`, `run`, `start`, `replay`, or `review` command.
- Broker/demo/live/real-money/Phase 9 authorized?: NO.
- Live execution status: NOT RUN.
- Implementation status: PR #140 merged DEC-049 to `main` at `39066f10c60bd1bade4f6f6e78e05ab3b7621c8e`, adding capture preflight/record-envelope APIs, exactly-once preflight artifacts, exports, and six focused contract tests. The exact final PR head passed 961 tests plus workflow-YAML validation and compile checks in run `35745448870`; unchanged Phase 3 acceptance run `35745448859` passed.
- Follow-up: separately freeze and implement the Phase 8B runtime/replay/acceptance protocol before any prospective Phase 8B segment may begin.


### EXP-20260922-021 — Phase 8B runtime and deterministic replay kernel

- Date: 2026-09-22
- Status: ACTIVE — SOURCE-FREE IMPLEMENTATION MERGED / NO LIVE-SHADOW SEGMENT
- Protocol decision: DEC-050 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: implement the deterministic finite-sequence market-processing, multi-strategy routing, shared-account shadow simulation, segment evidence, and offline replay kernel over exact DEC-049 capture records.
- Input boundary: one exact valid `fmp-phase8b-capture-preflight-v1` artifact plus an ordered finite sequence of exact `fmp-phase8b-capture-record-v1` envelopes.
- Market processing: per-symbol bridge/market liveness separation; no backfill/interpolation; only fully observed 1m bars; exact 5m/15m/1h aggregation from complete one-minute constituents.
- Strategy path: immutable `StrategyVersion` reconstruction from frozen identity JSON; recomputed fingerprint validation; existing Phase 8A strategy generators reused unchanged.
- Routing: existing champion eligibility, same-symbol same-time direction-conflict handling, and USD exposure accounting reused.
- Simulation: one shared $100,000 Phase 3 risk account per 0.2/0.5/1.0-pip scenario across all champion strategies and symbols; five-second entry/exit deadlines; symbol-specific stale-path invalidation.
- Replay: exact same preflight + exact ordered raw envelopes must reproduce the canonical segment payload byte-for-byte.
- CLI scope: unchanged; no `capture`, `run`, `start`, or `review` command.
- Broker/demo/live/real-money/Phase 9 authorized?: NO.
- Live execution status: NOT RUN.
- Implementation status: PR #141 merged DEC-050 to `main` at `4a8431d17f3fd050839d7841fc27e5543b258dc4`, adding the runtime/replay kernel, deterministic segment/replay artifact support, Phase 8B API exports, and five focused runtime/replay tests. Exact final PR-head verification passed 966 tests plus workflow-YAML validation and compile checks; unchanged Phase 3 acceptance passed.
- Follow-up: separately freeze and implement the Phase 8B acceptance compiler before any prospective Phase 8B segment may begin.


### EXP-20260922-022 — Phase 8B acceptance compiler and prospective evidence contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE-FREE IMPLEMENTATION MERGED / NO LIVE-SHADOW SEGMENT
- Protocol decision: DEC-051 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: freeze and implement the deterministic Phase 8B acceptance compiler plus the exact prospective campaign-evidence and historical spread-reference contracts required before any champion can become SHADOW_VALIDATED.
- Campaign-evidence protocol: `fmp-phase8b-campaign-evidence-v1`; prospective=true and closed=true are mandatory, with exact DEC-049 preflight, DEC-050 segment/replay, champion/strategy/symbol/cost identities and deterministic fingerprint validation.
- Spread-reference protocol: `fmp-phase8b-spread-reference-v1`; exact symbol coverage, historical spread sample counts and median/p95 entry/exit values, bound to the same preflight/champion/cost identities.
- Minimum evidence: >=40 completed 0.2-pip scorable trades, >=8 elapsed weeks, >=30 complete London dates, >=2 represented strategy families, and >=2 represented V1 pairs.
- Operational gates: >=90% date coverage, zero malformed records silently admitted, zero stale-gap trades in financial metrics, complete operational logging, identical candidate sequence across scenarios, replay match, p99 processing <=250ms, and zero scored entry/scheduled-exit deadline violations.
- Spread gate: live median/p95 entry/exit spread per traded required symbol <= historical value +0.5 pip.
- Financial gates: at 0.2 and 0.5 pips, net return >0, expectancy >0, PF >1, max drawdown <=5%; 1.0 pip diagnostic only.
- Outcome precedence: protocol failure -> safety rejection -> replay/integrity operational rejection -> NEED_MORE_DATA -> operational rejection -> market mismatch -> financial mismatch -> PASS.
- PASS authority: exact champion SHADOW_CANDIDATE -> SHADOW_VALIDATED transition plus demo-design eligibility only; all demo/live/broker/real-money/Phase-9 execution authorizations remain false.
- Live execution status: NOT RUN.
- Initial PR CI: run `35749097079` correctly failed one tamper test because a derived 0.2-pip trade-count check fired before the immutable evidence fingerprint check; unchanged Phase 3 acceptance `35749097176` passed.
- Fix: commit `8628f0810a55353da3bbe299635d0bd89fa4ab94` authenticates campaign and spread-reference fingerprints before derived consistency validation.
- Fixed verification: PR tests run `35749385885` passed 973 tests plus workflow-YAML validation and compile checks; unchanged Phase 3 acceptance run `35749385867` passed.
- Merge status: PR #143 merged DEC-051 to `main` at `2c9577be8eafb9e307e05214609206dfeb7c6c69`. Superseded PR #142 remained unmerged because its displayed head lagged the branch ref; a fresh exact-head PR was used instead.
- Follow-up: a later separately frozen prospective capture/close protocol must create real `fmp-phase8b-campaign-evidence-v1` evidence; DEC-051 itself cannot create prospective evidence or start a live-shadow segment.


### EXP-20260922-023 — Phase 8B prospective capture segment journal

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION MERGED / NO LIVE SEGMENT CAPTURED
- Protocol decision: DEC-052 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: add the first explicit bounded operator-invoked quote-only capture surface while preserving fixed bridge identity, EOF/no-backfill semantics, deterministic DEC-050 processing/replay, and all order-path locks.
- CLI scope: adds only `capture-segment --campaign-dir <path> --duration-seconds <1..86400>`; polling remains fixed at 0.10 seconds; generic run/start/review/campaign-close commands remain absent.
- First-segment rule: if no DEC-049 capture preflight exists, build it from the exact registration/start artifacts and continue capture on the same fresh EOF readers.
- Restart rule: later invocations use fresh EOF readers and therefore exclude records written while FMP was not observing; restart gaps are retained for later campaign-close accounting.
- Durable evidence: create-only per-segment directory, fsynced capture-record JSONL, one fsynced audit row per retained record with receive-to-raw-append latency, fsynced operational events, DEC-050 segment/replay artifacts, and immutable `fmp-phase8b-prospective-segment-v1` close artifact.
- Failure semantics: malformed/truncated/session-drift/identity failures terminate the invocation and may leave retained raw evidence, but no `prospective-segment.json` close artifact.
- Broker/demo/live/real-money/Phase 9 authorized?: NO.
- Acceptance/promotion authorized?: NO.
- Live execution status: NOT RUN.
- Implementation status: PR #144 merged DEC-052 to `main` at `8d28dc3dfdc1bb41112034f7b1a91fd54ad55e46`. The exact final PR head `0d61fcb6f678a8c76cef78b6ab93df5485abe791` passed 977 tests plus workflow-YAML validation and compile checks in run `35751972199`; unchanged Phase 3 acceptance run `35751972226` passed.
- Follow-up: separately freeze and implement the multi-segment campaign-close protocol before DEC-051 acceptance can consume real prospective evidence.


### EXP-20260922-024 — Phase 8B prospective campaign evidence close

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION MERGED / NO ACCEPTANCE RESULT
- Protocol decision: DEC-053 APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
- Purpose: compile immutable DEC-051 campaign-evidence snapshots from exact ordered DEC-052 prospective segment journals without resetting the shared virtual account at process boundaries.
- Segment eligibility: exact valid prospective-segment closure, raw/audit/operational digests, child DEC-050 segment identity, child replay match, exact DEC-049 preflight identity, no duplicate prospective/runtime/replay/capture fingerprints, and non-overlapping wall-clock intervals.
- Restart semantics: receive monotonic values remain segment-local; cross-segment source-time progression is mandatory; restart gaps are explicit and never backfilled.
- Aggregate runtime: all eligible raw records are replayed as one continuous DEC-050 aggregate with one shared $100,000 Phase 3 risk account per slippage scenario; child financial summaries are integrity-only and are never summed.
- Terminal snapshot rule: every aggregate scenario must have zero open and zero pending hypothetical decisions before campaign evidence can be written.
- Derived DEC-051 evidence: London weekday denominator/full-day coverage, nearest-rank p99 processing latency, entry/exit deadline violations, strategy-family/pair representation, exact live entry/exit spread samples and median/p95, scenario financial metrics, structural safety, and integrity evidence.
- Snapshot semantics: each close is immutable and create-only, but not a permanent capture shutdown; later clean segments may produce a newer snapshot after NEED_MORE_DATA.
- CLI scope: adds only `close-campaign --campaign-dir <path>`; it reads existing artifacts only and does not access MT5 or a broker.
- Broker/demo/live/real-money/Phase 9 authorized?: NO.
- Acceptance/lifecycle transition executed?: NO.
- Initial CI: run `35754471148` found one test-ordering issue: a copied duplicate segment failed as temporal overlap before duplicate immutable identity. Phase 3 acceptance `35754471080` passed.
- Fix: commit `8f1eb49fb8ea84093c86da52779e74b91650591d` authenticates duplicate segment/runtime/replay/capture identities before interval overlap evaluation.
- Additional pre-result safety amendment: commits `7d845ce8d437c8ab0b515358d075dd5c912de000` and `3244459b456f4c05e07cb4e52ae7c50aeef96061` freeze and enforce zero open/pending aggregate decisions before closure.
- Verification: exact source head `3244459b456f4c05e07cb4e52ae7c50aeef96061` passed 982 tests plus workflow-YAML validation and compile checks in run `35754791092`; unchanged Phase 3 acceptance run `35754790877` passed.
- Merge status: PR #145 merged DEC-053 to `main` at `3b0d7be25a8d5f2ff6eff2fb495aaa6c2ca3c09f`. The exact final PR head `ddce81d0e3fc948eb0d251e7d2dc488eba5cefae` passed 982 tests plus workflow-YAML validation and compile checks in run `35754982384`; unchanged Phase 3 acceptance run `35754982244` passed.
- Follow-up: no real DEC-052 capture or DEC-051 acceptance result has been produced. The next milestone is to freeze the explicit acceptance-review invocation/lifecycle transition boundary over immutable DEC-053 snapshots and pre-frozen spread-reference evidence.


### EXP-20260922-025 — Phase 8B acceptance review and shadow-validation freeze

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION MERGED / NO REAL ACCEPTANCE RESULT
- Protocol decision: DEC-054 APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
- Purpose: freeze the final source-only Phase 8B review boundary over exact DEC-053 closures and one deterministic campaign-bound DEC-051 historical spread reference.
- Pre-capture ordering: `authorize-start` now persists DEC-048 start authorization and DEC-049 capture preflight from the same fresh EOF readers, then stops without capturing a prospective record.
- Historical spread reference: fixed accepted Phase 8A complete canonical 1m snapshot, 2015-01-01 through 2026-08-21, fixed manifest layout, entry spread from bar open, exit spread from bar close, exact sample counts, median, nearest-rank p95, and exact processed-manifest/month provenance.
- Capture gate: `capture-segment` requires the exact campaign-bound spread reference and fails after any terminal campaign marker.
- Review: `review-campaign --campaign-dir <path> --closure-id <sha256>` binds one exact closure, one exact campaign-bound spread reference, and the review code commit into a deterministic create-only review ID.
- NEED_MORE_DATA: non-terminal; writes acceptance evidence only and permits later clean capture/closure/review snapshots.
- PASS/rejection: terminal for Phase 8B capture/review; writes `fmp-phase8b-campaign-terminal-v1` with all order/broker/real-money/Phase-9 execution flags false.
- PASS lifecycle evidence: only exact PASS may create `fmp-phase8b-shadow-validation-v1`, applying existing registry transition SHADOW_CANDIDATE -> SHADOW_VALIDATED while reproducing the exact champion-set fingerprint.
- Demo/live orders, broker mutation, real-money trading, DEMO_ELIGIBLE transition, and Phase 9 execution authorized?: NO.
- Live execution status: NOT RUN.
- Verification: PR #146 implementation head `57b94fc0ec1f30fea0acb036364d1ca0667f8c8c` passed 988 tests plus workflow-YAML validation and compile checks in run `35758432987`; unchanged Phase 3 acceptance run `35758432967` passed.
- Merge status: PR #146 merged DEC-054 to `main` at `7e3e1f03fcdf9f2314cd96864eb1825b1b3c2a18`. The exact final PR head `aaa5500776fa4a8d7a4e5ddcfb0b8ec4d24498c5` passed 988 tests plus workflow-YAML validation and compile checks in run `35758599011`; unchanged Phase 3 acceptance run `35758598901` passed.
- Follow-up: no real prospective capture, spread-reference freeze, campaign closure review, lifecycle transition, or Phase 9 design has been executed. A later separately frozen Phase 9 demo-design protocol may consume only an exact DEC-054 PASS/shadow-validation artifact.


### EXP-20260922-026 — Phase 9 demo design proposal

- Date: 2026-09-22
- Status: ACTIVE — SOURCE DESIGN MERGED / NO DEMO ORDER
- Protocol decision: DEC-055 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: freeze a source-only Phase 9 demo architecture from one exact terminal DEC-054 PASS review while preserving accepted Phase 8B champion/account/server/symbol identity and unchanged Phase 3 risk policy.
- Input boundary: exact DEC-049 preflight, exact terminal DEC-054 PASS review/acceptance/shadow-validation bytes, and exact campaign-terminal marker.
- Integrity: Phase 9 loader verifies the DEC-054 review-manifest SHA-256 bindings for acceptance and shadow-validation before compiling the design.
- Provider path: accepted FP Markets MT5 demo identity only; changing provider requires a new decision.
- Future protocol: `fmp-mt5-demo-order-bridge-v1` requirements frozen for practice-account assertion, deterministic client order IDs, mandatory protective stops, requested-vs-fill logging, order journal, startup reconciliation, orphan fail-closed behavior, restart/recovery, daily halt, and secret handling.
- Risk: exact unchanged Phase 3 `RiskConfig` is embedded; DEC-055 cannot widen per-trade, simultaneous-risk, or daily-loss limits.
- CLI: separate Phase 9 source-only `design-demo --campaign-dir <path> --review-id <sha256>`; no `run-demo`, `order`, `trade`, broker, or live command.
- Authorization: `demo_adapter_source_authorized=true` only. Demo execution/order, live order, broker mutation, real-money trading, and Phase 10 remain false.
- Live/demo execution status: NOT RUN.
- Verification: PR #147 exact implementation head `c796c4988ebafb6d357b5a49de2d6ced928bd2a5` passed 993 tests plus workflow-YAML validation and compile checks in run `35759609550`; unchanged Phase 3 acceptance run `35759609484` passed.
- Merge status: PR #147 merged DEC-055 to `main` at `559d8787daf014e64ba1b1d114f8384bed5ab84f`. The exact final PR head `660c92274e64f5a8786cf18e71d037bbaecc48ee` passed 993 tests plus workflow-YAML validation and compile checks in run `35759782638`; unchanged Phase 3 acceptance run `35759782621` passed.
- Follow-up: a later separately frozen decision is required before any demo order adapter can be implemented or enabled. No real Phase 8B PASS or Phase 9 design artifact has been executed.


### EXP-20260922-027 — Phase 9 locked demo-order protocol foundation

- Date: 2026-09-22
- Status: ACTIVE — SOURCE PROTOCOL MERGED / NO DEMO ORDER
- Protocol decision: DEC-056 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: implement only the deterministic post-risk request, dry-run journal, reconciliation, and structurally locked adapter boundary required by DEC-055 before any future MT5 mutation transport exists.
- Request source: exact existing Phase 3 `OrderIntent` values only; units and reserved risk are copied, never recomputed or widened.
- Deterministic identity: `fmp-phase9-demo-order-request-v1` binds exact DEC-055 design/champion/strategy/decision/symbol/direction/units/stop-target/timing identity and derives `fmp9-<24 hex>` client order IDs.
- Practice identity: provider, DEMO account fingerprint, server, and identity symbol mapping are copied from the exact DEC-055 design with no caller override surface.
- Protective geometry: mandatory direction-aware stop and optional target are validated against a reference price that is not a fill and causes no broker action.
- Dry-run evidence: `fmp-phase9-demo-dry-run-v1` validates the exact request while keeping submission, broker mutation, demo/live order, real-money, and Phase 10 flags false; writes are create-only.
- Reconciliation: `fmp-phase9-demo-reconciliation-v1` normalizes caller-supplied fixtures only, replays duplicate/unknown/orphan/missing-stop diagnostics from the snapshot itself, and performs no broker read.
- Adapter lock: `LockedDemoOrderAdapter` contains no broker/MT5 transport field; its only submission method validates the request then always raises `DemoExecutionLockedError`.
- CLI scope: unchanged Phase 9 design-only CLI; no `run-demo`, `submit-order`, `order`, `trade`, broker, or mutation command.
- Demo execution/order, live order, broker mutation, real-money trading, and Phase 10 authorized?: NO.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `97e8153ae7b8b00e0960ab95eba076dd027de982` passed 999 tests plus workflow-YAML validation and compile checks in run `35762091445`; unchanged Phase 3 acceptance run `35762091454` passed.
- Merge status: PR #148 merged DEC-056 to `main` at `c069e33fec82fc1e516120ee23923955f054bf89`. The exact final PR head `b3cfb9e1e2d2f0a3306a026566ad4b25df55a99b` passed 999 tests plus workflow-YAML validation and compile checks in run `35762297677`; unchanged Phase 3 acceptance run `35762297505` passed. Post-merge `main` runs `35762518616` and `35762518646` also passed.
- Follow-up: a later separately frozen decision is mandatory before any MT5 mutation transport can be implemented, wired, or enabled. No real Phase 8B PASS, Phase 9 design artifact, demo order, or broker mutation has been executed.


### EXP-20260922-028 — Phase 9 MT5 demo preflight and order-check foundation

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-057 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: add only the MT5-specific practice-account, symbol-contract, current-quote, exact volume translation, protective-stop validation, and non-mutating order-check layer required before any future broker mutation transport exists.
- Input boundary: exact DEC-055 demo design plus exact DEC-056 post-risk demo-order request.
- Backend boundary: `MT5DemoCheckBackend` exposes account/symbol/tick snapshots and `order_check` only; it exposes no `order_send`, submit, modify, cancel, or close-position method.
- Practice identity: exact accepted DEMO account fingerprint and server are asserted; no caller override surface exists.
- Volume: Phase 3/DEC-056 units remain authoritative and are translated by exact `units / trade_contract_size`; non-representable broker volume-grid requests fail closed rather than being resized or rounded.
- Market/stop validation: BUY uses current ask, SELL uses current bid; broker price grid and minimum stop-distance constraints are checked without widening/removing stops or targets.
- Order-check semantics: deterministic `fmp-phase9-mt5-demo-order-check-request-v1`, fixed GTC, broker filling mode, check-only deviation 0, and only normalized MT5 `retcode=0` is check-passed.
- Preflight evidence: successful source-only checks produce `fmp-phase9-mt5-demo-preflight-v1` with all execution/order/mutation/real-money/Phase-10 flags false; writes are create-only.
- CLI scope: unchanged Phase 9 design-only CLI; no broker-connected or order-capable command was added.
- Demo execution/order, live order, broker mutation, real-money trading, and Phase 10 authorized?: NO.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `19a6ad3f653b053d6c32e2f6e95dd05c999bddb1` passed 1005 tests plus workflow-YAML validation and compile checks in run `35766703078`; unchanged Phase 3 acceptance run `35766703266` passed.
- Merge status: PR #149 merged DEC-057 to `main` at `366f271ca951108cf8fdb1df01604817baa076dc`. The exact final PR head `b5e97f06658f487ad553241616ff53049c7f2fba` passed 1005 tests plus workflow-YAML validation and compile checks in run `35766872553`; unchanged Phase 3 acceptance run `35766872565` passed. Post-merge `main` runs `35767028347` and `35767028362` also passed.
- Follow-up: a later separately frozen decision is required before any backend containing `order_send` or any broker mutation method can exist. No real Phase 8B PASS, Phase 9 design/preflight artifact, demo order, or broker mutation has been executed.


### EXP-20260922-029 — Phase 9 gated MT5 mutation transport source

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-058 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: implement the MetaTrader5 Python mutation-capable infrastructure source while keeping the official FMP demo execution path hard-disabled.
- Identity continuity: current terminal login is hashed exactly as the Phase 8B bridge, `sha256(str(ACCOUNT_LOGIN))`; account mode/server/trade permissions are read from the connected terminal rather than accepted as caller overrides.
- Symbol policy: actual symbol execution/filling properties determine RETURN/FOK/IOC behavior; Market Execution requires allowed FOK or IOC and otherwise fails closed.
- Request integrity: future `order_send` receives the exact freshly checked DEC-057 request with no post-check resize, stop/target edit, symbol/account swap, or price-field mutation.
- Result semantics: `fmp-phase9-mt5-demo-send-result-v1` normalizes retcode/tickets/fill volume/price/bid/ask/comment/request ID; only retcode 10009 with full confirmed volume is marked completed.
- Reconciliation reads: active order/position fixtures are normalized with client-order comments and deterministic protective-stop presence identifiers.
- Hard gate: `DEMO_EXECUTION_SOURCE_ARMED=false`; no DEC-058 setter, config, environment variable, artifact, or CLI can change it. The official adapter checks the gate before any broker read or mutation.
- CLI scope: unchanged Phase 9 design-only CLI; no run-demo/order-send/trade/close/cancel/broker command was added.
- Demo execution/order, live order, FMP broker mutation, real-money trading, and Phase 10 authorized?: NO.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `daf97700e123a025db626ea2d18bc1e7a8fecde2` passed 1011 tests plus workflow-YAML validation and compile checks in run `35767811967`; unchanged Phase 3 acceptance run `35767812096` passed.
- Merge status: PR #150 merged DEC-058 to `main` at `03617bcd609b61084f4dd09690f9d2166b391a61`. The exact final PR head `46825d1138392baff7b71465704df17260c28d88` passed 1011 tests plus workflow-YAML validation and compile checks in run `35768044631`; unchanged Phase 3 acceptance run `35768044648` passed. Post-merge `main` runs `35768227486` and `35768227484` also passed.
- Follow-up: a later separately frozen decision must explicitly arm one bounded demo session and freeze its operator/journal/recovery boundary before any real practice-account order. No real Phase 8B PASS, Phase 9 design/preflight/session artifact, demo order, or broker mutation has been executed.


### EXP-20260922-030 — Phase 9 bounded first demo-session contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-059 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: freeze one exact post-risk request into a one-order, practice-only, UTC-day-bounded demo-session contract before the DEC-058 execution source lock can ever change.
- Arm identity: exact DEC-055 design, DEC-056 request/client ID, champion, strategy, symbol, accepted DEMO account/server, one operator approval reference, and `max_new_orders=1`.
- Risk-day guard: not-before/expiry must remain inside one UTC civil date; readiness requires `daily_halt_active=false`.
- Startup safety: exact DEC-056 reconciliation must be healthy; duplicate/unknown/orphan/missing-stop states fail closed and no auto-mutation is attempted.
- Ambiguity/idempotency: after one `SEND_ATTEMPTED` journal event the arm is spent regardless of eventual broker result.
- Journal: `fmp-phase9-demo-session-journal-v1` is create-only, hash-chained, identity-stable, sequence-contiguous, and every append is flushed/fsynced.
- Future send ordering: the durable SEND_ATTEMPTED event binds the freshly checked DEC-057 payload digest before any later-approved mutation call.
- Source lock: DEC-058 `DEMO_EXECUTION_SOURCE_ARMED=false` is unchanged; `BoundedDemoSessionController` still reaches the locked adapter and fails before broker access.
- CLI scope: unchanged design-only Phase 9 CLI; no arm/run/order/broker/mutation command and no repository-created real arm.
- Phase 9 acceptance / Phase 10 authorized?: NO. One first practice order would not by itself satisfy deployment review.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `c273bb5a21d865d09edefbd425f18c4049e58399` passed 1017 tests plus workflow-YAML validation and compile checks in run `35768964040`; unchanged Phase 3 acceptance run `35768964070` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before a real arm can be created or the DEC-058 execution lock can change.


### EXP-20260922-031 — Phase 9 demo execution-arm artifact contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT MERGED / NO REAL ARM / NO DEMO ORDER
- Protocol decision: DEC-060 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: implement only the deterministic future operator execution-arm artifact over exact DEC-055/056/059 identities while keeping the DEC-058 source gate false.
- Input binding: exact demo design, exact post-risk request/client ID, exact DEC-059 session-arm and session-ready fingerprints, unchanged champion/strategy/symbol, accepted DEMO account/server, exact UTC window, exact operator approval reference, and max-new-orders=1.
- Override policy: the builder exposes no caller parameters for account/server/symbol/units, arm window, or approval reference; those values are copied from already validated upstream artifacts.
- Readiness guard: session-ready must be healthy, daily halt inactive, zero prior attempts, max-new-orders=1, and bound to the exact arm/design/request.
- Source-gate guard: construction fails closed if DEC-058 `DEMO_EXECUTION_SOURCE_ARMED` is anything other than false.
- Persistence: create-only `execution-arm.json` + manifest with deterministic fingerprint and byte SHA-256.
- CLI scope: unchanged Phase 9 design-only CLI; no arming/run-demo/submit-order/broker command.
- Demo execution/order, broker mutation, live order, real-money trading, and Phase 10 authorized?: NO.
- Real operator arm created?: NO.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `a62be09eda02f09b255211ea5dca8b63055ae361` passed 1023 tests plus workflow-YAML validation and compile checks in run `35771299138`; unchanged Phase 3 acceptance run `35771299314` passed.
- Merge status: PR #152 merged DEC-060 to `main` at `71cb40bd00970696cee91f4c35755ca87c9f3eab`. The exact final PR head `5694c7b54d0729e0340539aa280f126d7cc420e9` passed 1023 tests plus workflow-YAML validation and compile checks in run `35771474118`; unchanged Phase 3 acceptance run `35771474159` passed.
- Follow-up: a later separately frozen decision is required before a real arm can be materialized or the execution source gate may change.


### EXP-20260922-032 — Phase 9 offline demo-arm materialization

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION MERGED / NO REAL DEMO ORDER
- Protocol decision: DEC-061 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: add one local-only operator command that materializes the exact DEC-060 execution-arm package from already-frozen JSON evidence without MT5/broker access.
- CLI: adds only `materialize-arm --design --request --session-arm --session-ready --out-dir` beside `design-demo`.
- Override policy: no CLI option exists for strategy, symbol, units, reserved risk, stop/target, account/server/provider, client-order ID, UTC arm window, approval reference, or order count.
- Import boundary: `src/fmp/phase9/cli.py` directly imports only local artifact/validation code for materialization and does not directly import or instantiate the mutation backend, MetaTrader5 wrapper, or order-send runner.
- Gate refactor: the hard source lock remains `DEMO_EXECUTION_SOURCE_ARMED=false` in neutral `execution_gate.py`; DEC-058 mutation source and DEC-060 arming validation both consume that lock without adding a setter/config/env/artifact override.
- Persistence: materialization writes only create-only `execution-arm.json` and manifest; repository tests use temporary fixture directories only.
- Broker access/order_check/order_send performed?: NO.
- Demo execution/order, broker mutation, live order, real-money trading, and Phase 10 authorized?: NO.
- Real operator arm for an actual broker session created?: NO.
- Verification: exact source head `25f7a315266605097d51b92c2faca9364a1651db` passed 1025 tests plus workflow-YAML validation and compile checks in run `35772227156`; unchanged Phase 3 acceptance run `35772227085` passed.
- Merge status: PR #153 merged DEC-061 to `main` at `ad4dea51f537225f7bbb18335c68beebb9c58067`. The exact final PR head `b6584aff886dad7fac513cdeb57d3c86430b67c4` passed 1025 tests plus workflow-YAML validation and compile checks in run `35772414863`; unchanged Phase 3 acceptance run `35772414631` passed.
- Follow-up: a later separately frozen decision is required before a materialized arm can become runtime authority or the execution source gate can change.


### EXP-20260922-033 — Phase 9 demo runtime arm authority contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-062 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: accept one exact DEC-060/061 materialized demo arm as source-only runtime authority evidence without changing the DEC-058 execution source lock.
- Upstream chain: exact DEC-055 design, DEC-056 request/client ID, DEC-059 session arm/readiness, and DEC-060 execution-arm fingerprints are revalidated and bound.
- Runtime checks: current UTC must remain inside the unchanged arm window and not precede session readiness; daily halt must be inactive; one-order budget remains exactly one.
- Journal replay: exact DEC-059 journal identity is validated; event count and tip fingerprint are bound; any prior `SEND_ATTEMPTED` fails closed.
- Source isolation: runtime-authority source imports no MetaTrader5 backend or mutation adapter, adds no broker-connected CLI, and performs no broker access.
- Authorization: only `demo_runtime_arm_authority_ready=true`; `DEMO_EXECUTION_SOURCE_ARMED=false` and every demo/live order, broker-mutation, real-money, and Phase-10 flag remain false.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `f17f67c4407e6100abbb47c855fd564a88b46bc3` passed 1031 tests plus workflow-YAML validation and compile checks in run `35774162526`; unchanged Phase 3 acceptance run `35774162520` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before the source execution gate can become true or any broker-connected runner may consume runtime-authority evidence.

- Merge status: PR #154 merged DEC-062 to `main` at `d0046f2b8119d34bf991ecb5d7f08136536a780a`. The exact final PR head `5fc6290b1a23cdee1d7d5acc72fb25284b9e38d2` passed 1031 tests plus workflow-YAML validation and compile checks in run `35774454431`; unchanged Phase 3 acceptance run `35774454262` passed. Post-merge `main` runs `35774570313` and `35774570327` also passed.
- Follow-up: a separately frozen decision is required before a broker-connected runtime preflight may consume the authority record; the source execution gate remains false and no demo order has been sent.


### EXP-20260922-034 — Phase 9 broker-connected demo launch preflight

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-063 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: consume exact DEC-062 runtime-authority evidence and perform only the final fresh DEMO account/symbol/tick reads, non-mutating order_check, and open-order/open-position reconciliation required before any later first-demo-order decision.
- Runtime guard: current UTC, daily halt, append-only journal prefix, exact journal identity, and zero SEND_ATTEMPTED events are revalidated before the first backend read.
- Backend boundary: `Phase9DemoLaunchPreflightBackend` exposes only account/symbol/tick reads, `order_check`, broker-orders read, and broker-positions read. It exposes no `order_send`, submit, cancel, modify, or close-position method.
- Fresh execution validation: exact DEC-057 no-resize volume, broker price-grid, stop-distance, target-geometry, filling-mode, practice-account identity, and retcode=0 order-check rules are reused.
- Fresh reconciliation: exact DEC-056 reconciliation must remain healthy; no automatic broker repair is permitted.
- Evidence: create-only `fmp-phase9-demo-launch-preflight-v1` binds exact runtime authority, current journal tip, account/symbol/tick evidence, order-check request/result, and reconciliation.
- Authorization: only `demo_launch_preflight_ready=true`; `DEMO_EXECUTION_SOURCE_ARMED=false` and every demo/live order, broker-mutation, real-money, and Phase-10 flag remain false.
- CLI: unchanged; no broker-connected or order-capable command was added.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `2f6a684f74058a7210e1613e2d9f6d729579b0bf` passed 1038 tests plus workflow-YAML validation and compile checks in run `35775307825`; unchanged Phase 3 acceptance run `35775308344` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before the execution source gate can change or any runner may invoke `order_send`.

- Merge status: PR #155 merged DEC-063 to `main` at `4d053c8edfc7ff1325da50530405cc876e33ba61`. The exact final PR head `d87bc0547584c9b9f756fe99325ff0b1da95e23c` passed 1038 tests plus workflow-YAML validation and compile checks in run `35775591842`; unchanged Phase 3 acceptance run `35775591852` passed. Post-merge `main` runs `35775737773` and `35775737735` also passed.
- Follow-up: a separately frozen one-shot execution-permit contract is required before any future execution runner may be authorized; no real demo order has been sent.


### EXP-20260922-035 — Phase 9 one-shot demo execution permit contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-064 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: define only the immutable future one-shot execution-permit artifact over exact DEC-063 launch-preflight evidence.
- Exact binding: DEC-055 design, DEC-056 request/client ID, DEC-059 session arm/readiness, DEC-060 execution arm, DEC-062 runtime authority, DEC-063 launch preflight, champion/strategy/symbol, accepted DEMO account/server, UTC arm window, operator approval reference, and max-new-orders=1.
- Checked-request immutability: permit binds fresh order-check request/result fingerprints, healthy reconciliation fingerprint, and canonical SHA-256 of the exact checked MT5 request payload.
- Arm semantics: permit copies the exact one-order window and does not spend or widen it; future execution must still durably journal SEND_ATTEMPTED before any mutation call.
- Persistence: create-only `execution-permit.json` plus manifest.
- Source isolation: permit source imports no MetaTrader5 backend, mutation adapter, or broker runner and adds no CLI.
- Authorization: only `demo_execution_permit_artifact_ready=true`; `DEMO_EXECUTION_SOURCE_ARMED=false` and every execution/order/mutation/live/real-money/Phase-10 flag remain false.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `fc9fcc586fad03b90963ff636cb2275bbcbe1fd7` passed 1043 tests plus workflow-YAML validation and compile checks in run `35776256682`; unchanged Phase 3 acceptance run `35776256435` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before any real execution runner may consume the permit or invoke `order_send`.


### EXP-20260922-036 — Phase 9 permit-aware one-shot demo runner source

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-065 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: implement the future one-shot permit-aware practice-order runner while keeping the DEC-058 execution source gate false.
- Upstream binding: exact DEC-055 design, DEC-056 request/client identity, DEC-059 session arm/readiness and journal, DEC-060 execution arm, DEC-062 runtime authority, DEC-063 launch preflight, and DEC-064 execution permit.
- Immediate checks: exact arm window, launch time ordering, daily halt inactive, exact permit journal count/tip, zero prior SEND_ATTEMPTED, one-order cap, practice-only identity, and exact checked MT5 request SHA-256.
- One-shot spend: future armed-path simulation fsyncs SEND_ATTEMPTED before any mutation call and never retries order_send.
- Send evidence: returned results are normalized through exact DEC-058 send-result semantics; broker-returned non-completion is distinct from transport ambiguity.
- Ambiguity: order_send exceptions spend the arm, journal SESSION_HALTED, prohibit retry, and still attempt one post-send reconciliation.
- Post-send reconciliation: exactly one broker-order/position read cycle is normalized through DEC-056 reconciliation; no automatic repair is allowed.
- Source lock: repository `DEMO_EXECUTION_SOURCE_ARMED=false`; current source fails before journal mutation and broker access. Armed-path tests patch only the runner-local gate and use fake in-memory backends.
- CLI: unchanged; no broker-connected or order-capable command added.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `54efe65ff66e90ff5939a11ad5bad704d9b60b70` passed 1049 tests plus workflow-YAML validation and compile checks in run `35779123073`; unchanged Phase 3 acceptance run `35779123145` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before the execution source gate may be true in an operator path or the first practice-account order may actually be sent.


- Merge status: PR #157 merged DEC-065 to `main` at `94eb6d4af4f146e751f2baed86f9b85fae4e8cac`. The exact final PR head `797ca4c9f3f3af20367d47a47e0c2e2972d9cdf6` passed 1049 tests plus workflow-YAML validation and compile checks in run `35779313105`; unchanged Phase 3 acceptance run `35779312681` passed. Post-merge `main` runs `35779467788` and `35779467811` also passed.
- Follow-up: source-only construction is complete through the permit-aware one-shot runner. A separately approved first-demo execution decision is required before the execution source gate may be true in an operator path or any real practice-account order may be sent.


### EXP-20260922-037 — Phase 9 demo campaign evidence and acceptance contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-066 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: freeze the amount and quality of Phase 9 practice-account evidence required before a Phase 10 deployment review, before any practice result exists.
- Minimum evidence: at least 40 completed practice trades, 8 elapsed calendar weeks, 30 distinct demo-session dates, two represented strategy families, and two represented V1 pairs.
- Safety gate: zero practice-account assertion failures, live orders, real-money access, unauthorized broker mutations, duplicate client-order submissions, retries after durable SEND_ATTEMPTED, completed sends without protective stops, and daily-halt violations.
- Operational gate: zero journal-integrity failures, unresolved ambiguous sends, startup/post-send reconciliation failures, or restart/recovery failures; at least one restart/recovery drill; exact attempt accounting; requested-vs-fill completeness; and exact per-pair slippage sample accounting.
- Execution-cost gate: for every represented V1 pair, completed-send adverse entry slippage median <=0.5 pip and nearest-rank p95 <=1.0 pip.
- Financial evidence: demo return, expectancy, profit factor, and drawdown are diagnostic under DEC-066 and are reserved for the combined Phase 10 economic review rather than becoming a short-run demo promotion rule.
- Outcomes: NEED_MORE_DATA, safety rejection, operational rejection, execution-cost rejection, or PASS eligible only for a separate Phase 10 deployment review.
- Source isolation: compiler imports no MT5/backend/runner surface and performs no broker access.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `f105926b52b2b302bc549b50ce5ef21c4a269476` passed 1059 tests plus workflow-YAML validation and compile checks in run `35781835318`; unchanged Phase 3 acceptance run `35781835216` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. First-demo execution still requires a separately approved authorization decision.


- Merge status: PR #158 merged DEC-066 to `main` at `95f7001d98593d9d181b5176ad1f347352f667a4`. The exact final PR head `3c00e33eb38509d562c03d6139912fdfb007aa7a` passed 1059 tests plus workflow-YAML validation and compile checks in run `35781992487`; unchanged Phase 3 acceptance run `35781992474` passed. Post-merge `main` runs `35782129020` and `35782128865` also passed.
- Follow-up: Phase 9 demo evidence/acceptance criteria are frozen before any practice result. A separately approved first-demo execution authorization is still required before the source gate may be enabled in an operator path or any real practice-account order may be sent.


### EXP-20260922-038 — Phase 9 first-demo authorization packet contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-067 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: produce one immutable human-review packet for the exact future first practice order without recording approval or enabling execution.
- Exact review binding: accepted DEMO account/server/provider, champion and strategy identity, family/timeframe, symbol/broker symbol, direction, units, MT5 volume, reserved USD risk, reference and checked prices, protective stop, optional target, fill mode, time-in-force, client-order ID, decision/executable timestamps, launch-preflight time, arm window, session operator reference, checked-request SHA-256, and exact DEC-064 execution-permit fingerprint.
- Acceptance context: packet binds the frozen DEC-066 obligations of 40 completed trades, 8 elapsed weeks, 30 demo-session dates, two represented strategy families, two represented V1 pairs, median adverse entry slippage <=0.5 pip, and p95 <=1.0 pip.
- Approval challenge: one deterministic authorization-challenge fingerprint is derived solely from the immutable order-review payload; builder-code changes do not change the challenge, while any review-detail change does.
- Independent defense-in-depth: checked MT5 request hash, MT5 side, client comment, broker symbol, stop, and target are rechecked locally even after upstream DEC-064 validation.
- Non-authorization: explicit execution approval remains unrecorded; source gate, demo execution/order, broker mutation, live order, real money, Phase 10, and Phase 11 remain false.
- Source isolation: no MetaTrader5 mutation adapter, runner, order_send, or SEND_ATTEMPTED dependency; CLI unchanged.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `289dff872f3819c18ea37a2e33e27a35e27e3853` passed 1066 tests plus workflow-YAML validation and compile checks in run `35783034440`; unchanged Phase 3 acceptance run `35783034271` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required to record explicit approval against the exact challenge and define any operator-only source-gate activation.


- Merge status: PR #159 merged DEC-067 to `main` at `a966147f31127b929d3a88e80d7ff7294a5c5fb4`. The exact final PR head `7c696843813df9be19cae9fd9cab4079ad38f300` passed 1066 tests plus workflow-YAML validation and compile checks in run `35783187529`; unchanged Phase 3 acceptance run `35783187315` passed. Post-merge `main` runs `35783318956` and `35783319029` also passed.
- Follow-up: the exact first-demo order can now be rendered as an immutable approval challenge, but no approval has been recorded. A separately approved decision must define explicit challenge-bound approval recording and any operator-only source-gate activation before a real practice order can be sent.


### EXP-20260922-039 — Phase 9 explicit approval record and gate-activation contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO REAL APPROVAL / NO DEMO ORDER
- Protocol decision: DEC-068 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: define source-only challenge-bound explicit-approval and gate-activation artifacts without creating a real approval or enabling execution.
- Approval binding: exact DEC-067 packet/challenge, DEC-064 permit, request/client identity, DEMO account/server, arm window, opaque operator identity/reference, approval UTC, and exact statement `APPROVE FIRST DEMO ORDER <challenge>`.
- Approval timing: approval must be at/after launch preflight and inside the unchanged arm window.
- Activation binding: exact approval/packet/challenge plus activation UTC; activation must follow approval and remain inside the same arm window.
- Source semantics: fixture approval records may set `explicit_execution_approval_recorded=true`, but `demo_execution_source_armed=false`, runner activation remains unwired, and broker/live/real-money/Phase-10/Phase-11 authorizations remain false.
- Source isolation: no MetaTrader5, mutation adapter, runner import, order_send, SEND_ATTEMPTED, gate setter, environment override, config hook, or execution CLI.
- Real evidence status: no real Phase 8B acceptance/SHADOW_VALIDATED chain, no real Phase 9 artifact chain, no real approval record, and no demo order.
- Verification: exact source head `df64999f99aa8d5114b0a462e5d23723cb868fe1` passed 1075 tests plus workflow-YAML validation and compile checks in run `35784906657`; unchanged Phase 3 acceptance run `35784906607` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately approved operator-action decision is required before any real approval artifact, source-gate activation, runner wiring, or practice order.


- Merge status: PR #160 merged DEC-068 to `main` at `88d23744b23faf5035b2c67075af73b0e1c25abc`. The exact final PR head `c54ca6ae1a0bce9d74465039e85008c643d5fa28` passed 1075 tests plus workflow-YAML validation and compile checks in run `35785056511`; unchanged Phase 3 acceptance run `35785056455` passed. Post-merge `main` runs `35785181147` and `35785181186` also passed.
- Follow-up: challenge-bound approval and gate-activation schemas now exist, but no real approval record or activation has been created. A separately approved operator-action/runtime-wiring decision is required before the hard source gate can be enabled or the DEC-065 runner can consume a real activation contract.


### EXP-20260922-040 — Phase 9 approval-gated one-shot runtime wiring

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO REAL APPROVAL / NO DEMO ORDER
- Protocol decision: DEC-069 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: wire one exact DEC-068 activation contract to the existing DEC-065 one-shot runner while preserving the repository hard source lock.
- Validator separation: immutable DEC-060/062/064/067/068 artifact validators are now independent of current source-gate state; their builders and create-only writers still require source-unarmed operation, and the artifacts themselves still bind all embedded non-authorization flags false.
- Runtime checks: exact DEC-068 activation lineage, current UTC inside the immutable arm window and at/after activation, daily halt inactive, journal integrity, zero prior SEND_ATTEMPTED, practice-only identity, one-order cap, and exact account/request/client/permit identities.
- Delegation: after the DEC-069 source-gate check, all send-attempt journaling, exact checked-request use, no-retry behavior, DEC-058 send-result normalization, ambiguity handling, and post-send reconciliation remain delegated to DEC-065.
- Repository safety: `DEMO_EXECUTION_SOURCE_ARMED=false`; no setter/env/config/artifact hook or order-capable CLI added. Armed-path unit tests patch the wrapper in-process and do not access a broker.
- Real evidence status: no real Phase 8B prospective campaign/acceptance/SHADOW_VALIDATED transition; no real Phase 9 artifact chain, approval, activation, demo order, or broker mutation.
- Verification: exact source head `b52c026324b67216f2060d120b13c36d30a6677d` passed 1080 tests plus workflow-YAML validation and compile checks in run `35786753220`; unchanged Phase 3 acceptance run `35786753236` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. After DEC-069, source construction for the first practice-order path is complete, but real execution still requires the real Phase 8B/Phase 9 evidence chain plus explicit operator action in a separately approved armed runtime.


- Merge status: PR #161 merged DEC-069 to `main` at `0569b2cafb97bf4529cc95224a0133423396d9b9`. The exact final PR head `123f89d9cd5e2559f57a1b24cfe61affceff8e25` passed 1080 tests plus workflow-YAML validation and compile checks in run `35786935231`; unchanged Phase 3 acceptance run `35786935239` passed. Post-merge `main` runs `35787170070` and `35787170138` also passed.
- Follow-up: source construction for the first practice-order path is complete. No real Phase 8B acceptance or Phase 9 artifact/approval/activation chain exists yet, so the next meaningful milestone is real prospective evidence and explicit operator action in a separately approved armed runtime; repository execution remains hard-locked.


### EXP-20260922-041 — Phase 8B prospective campaign readiness audit

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO REAL CAPTURE
- Protocol decision: DEC-070 APPROVED BEFORE ANY PHASE 8B PROSPECTIVE CAPTURE
- Purpose: add a read-only, non-authoritative readiness inspection over the real Phase 8B campaign directory and current fixed bridge identities.
- Readiness protocol: `fmp-phase8b-campaign-readiness-v1`.
- CLI: `readiness --campaign-dir <path>` prints one point-in-time JSON report only and writes no campaign artifact.
- Artifact checks: DEC-047 registration, optional DEC-048 start authorization, DEC-049 capture preflight, DEC-054 spread reference, and campaign terminal state are validated and cross-bound by exact SHA/fingerprint/portfolio identity.
- Bridge checks: exact required-symbol coverage, connector protocol, DEMO mode, common account/server, and frozen bridge-session IDs. The audit opens tails at current EOF but never calls `read_available` and therefore consumes no post-EOF tick/heartbeat evidence.
- Readiness semantics: ready only means current capture prerequisites align; it does not prove 15-second bridge liveness or 5-second quote freshness and is never consumed as authorization by `capture-segment`.
- Next actions: `authorize-start`, `freeze-spread-reference`, or `capture-segment`; terminal campaigns report `none-terminal`.
- Operator handoff: replaced the historical USDJPY-only workflow with the current `FMPPhase8BQuoteBridge.mq5` multi-symbol EURUSD/GBPUSD/USDJPY portfolio process while retaining AutoTrading OFF, fixed FILE_COMMON paths, approved DEMO servers, no-backfill semantics, and explicit non-authorization wording.
- Safety: no prospective segment started, no campaign artifact written by readiness, no broker mutation, no order API, no Phase 9 action, and repository `DEMO_EXECUTION_SOURCE_ARMED=false`.
- Verification: exact source head `a0bce886dc64e62eeafac9d642f63d13848c2ffb` passed 1085 tests plus workflow-YAML validation and compile checks in run `35789539447`; unchanged Phase 3 acceptance run `35789539375` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. The next meaningful action after merge is an explicit real operator Phase 8B campaign preparation/readiness/capture workflow; repository verification itself still performs none of those live actions.


- Merge status: PR #162 merged DEC-070 to `main` at `5e918a9a9ed7b9ab112d62993eee6f4e7672e186`. The exact final PR head `5a26f9c6cd38040871a841c8a17567b1785ff753` passed 1085 tests plus workflow-YAML validation and compile checks in run `35789729752`; unchanged Phase 3 acceptance run `35789729689` passed. Post-merge `main` runs `35789967258` and `35789967219` also passed; the merge-commit test run executed 1085 tests.
- Follow-up: Phase 8B source/operator preparation is complete. No real readiness inspection, prospective segment, campaign close/review, acceptance result, or SHADOW_VALIDATED transition has been executed. The next meaningful milestone is explicit real prospective shadow evidence on the accepted MT5 DEMO bridge; Phase 9 execution remains hard-locked.


### EXP-20260923-042 — Phase 8B prospective campaign progress preview

- Date: 2026-09-23
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO REAL CAPTURE
- Protocol decision: DEC-071 APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
- Purpose: provide a read-only in-campaign progress preview over clean DEC-052 prospective segments without creating closure/review/acceptance evidence.
- Aggregation parity: reuses the exact DEC-053 segment loader, duplicate/overlap checks, continuous aggregate simulation, deterministic replay, observation bounds, London-date coverage, and strategy-family/pair representation logic.
- Minimum parity: exact DEC-051 definitions for 8 elapsed weeks, 30 complete London dates, 40 completed 0.2-pip trades, 2 represented strategy families, and 2 represented pairs, including remaining amounts.
- Closeability diagnostic: reports whether all 0.2/0.5/1.0 scenarios currently have zero open/pending decisions and whether aggregate replay matches.
- Empty-campaign behavior: no clean closed segment returns PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS rather than protocol failure.
- Persistence: stdout JSON only; no closure directory, campaign-evidence artifact, review, acceptance, lifecycle transition, or terminal marker.
- Safety: all promotion/SHADOW_VALIDATED/Phase-9/order/broker/live/real-money authorization flags remain false.
- Verification: exact source head `2252f8889683992cdacce0d6080363ec3b19772f` passed 1089 tests plus workflow-YAML validation and compile checks in run `35801819236`; unchanged Phase 3 acceptance run `35801819264` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. Real prospective MT5 DEMO evidence remains the next operational milestone.


- Merge status: PR #163 merged DEC-071 to `main` at `e45f6a496885863be69f87fd2caa8c3f577b784e`. The exact final PR head `021aa2bc8f9337d4f1830985c2ec4ca03cd16f4f` passed 1089 tests plus workflow-YAML validation and compile checks in run `35801932548`; unchanged Phase 3 acceptance run `35801932553` passed. Post-merge `main` runs `35802013847` and `35802013896` also passed.
- Follow-up: Phase 8B now has read-only pre-capture readiness and in-campaign progress tooling. No real prospective capture, closure/review, acceptance result, SHADOW_VALIDATED transition, or Phase 9 artifact chain has been executed; real MT5 DEMO prospective evidence remains the next operational milestone.


### EXP-20260923-043 — Phase 8B interrupted segment observability amendment

- Date: 2026-09-23
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO REAL CAPTURE
- Protocol decision: DEC-072 APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
- Purpose: make DEC-071 progress truthfully report retained interrupted DEC-052 segment directories even when no clean segment has closed yet.
- Inventory: shared deterministic segment inventory reports sorted closed and unclosed segment-directory identities; non-directory entries remain outside campaign segment evidence.
- Empty/interrupted behavior: no closed segment still returns `PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS`, but the true unclosed count/IDs are preserved rather than forced to zero.
- Mixed behavior: unclosed directories remain excluded from aggregate simulation, replay, coverage, trade counts, representation, and financial metrics.
- Identity hardening: a closed segment directory name must equal the immutable `segment_id` inside `prospective-segment.json`; renamed/copied closed directories fail closed before aggregation.
- Progress integrity: result now includes campaign terminal context, deterministic progress fingerprint, and validator-enforced count/list parity, sorted uniqueness, disjoint inventories, and all authorization flags false.
- Campaign-close parity: DEC-053 evidence still receives only the unclosed directory count; acceptance semantics are unchanged.
- Safety: no capture, repair, deletion, closure/review/acceptance artifact, broker mutation, Phase 9 action, or order is executed.
- Verification: exact corrected source head `1654564b4fc3cd971d369ea5717d0f7268aaf326` passed 1092 tests plus workflow-YAML validation and compile checks in run `35803297613`; unchanged Phase 3 acceptance run `35803297604` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. Real prospective MT5 DEMO evidence remains the next operational milestone.


- Merge status: PR #164 merged DEC-072 to `main` at `2732e00fa502219bf18de35ae861e72befe62661`. The exact final PR head `5efc050f31811e0f179638fc2c9bb83587eb22ef` passed 1092 tests plus workflow-YAML validation and compile checks in run `35803436296`; unchanged Phase 3 acceptance run `35803436276` passed. Post-merge `main` runs `35803529547` and `35803529528` also passed.
- Follow-up: interrupted prospective capture is now visible from the first failed attempt onward without being repaired or counted. No real prospective segment, campaign close/review, acceptance result, SHADOW_VALIDATED transition, or Phase 9 artifact chain has been executed; real MT5 DEMO prospective evidence remains the next operational milestone.


### EXP-20260923-044 — Phase 8A direct market-learning foundation

- Date: 2026-09-23
- Status: ACTIVE — SOURCE FOUNDATION / NO MODEL-TRAINING RESULT
- Protocol decision: DEC-073 APPROVED BEFORE ANY EXP-044 MODEL-TRAINING RESULT
- Purpose: restore the broader FMP learning objective by learning future market behaviour directly from leakage-safe market-state rows rather than training only on signals emitted by hand-written strategies.
- Universe: EURUSD, GBPUSD, USDJPY × 5m/15m/1h over accepted Phase 2 Dukascopy-derived BID/ASK history.
- Existing features: first generation reuses the 48 Phase 5 leakage-safe feature definitions; the historical `fmp-feature-v1` artifact is not rewritten or unlocked.
- Direct labels: exact 60m and 240m horizons from feature-row `available_at_utc`; future midpoint move plus hypothetical LONG/SHORT net pips at 0.2/0.5/1.0-pip adverse slippage; exact missing horizon is unavailable rather than shifted/interpolated.
- Evidence status: historical evidence is `RETROSPECTIVE_ALREADY_SEEN`; `untouched_oos=false`; no promotion authorization.
- Continuous learning: future shadow/demo observations may feed a later offline challenger retrain, but the active champion is immutable and cannot self-update after trades.
- Foundation merge: PR #166 merged the DEC-073 direct-outcome-label foundation to `main` at `b438ddd00bcc8b1f4b9adab0a0b84cc2777546df`. Exact PR head `0cea40d29139587c6707140c7f573228538d3403` passed 1101 tests plus workflow-YAML validation and compile in run `35836471528`; unchanged Phase 3 acceptance run `35836471517` passed.
- Full-history feature merge: PR #167 merged `fmp-market-feature-v1` source to `main` at `4e7af50751c3e74c29f7df82d05b6677fe4bd2ba`. Exact final PR head `0baa2848e9d4aeba975d959fc16e3c6421d65c91` passed 1107 tests plus workflow-YAML validation and compile in run `35837614313`; unchanged Phase 3 acceptance run `35837614254` passed. Post-merge `main` runs `35837744074` and `35837743994` also passed.
- Current deliverable: deterministic direct market-outcome labels plus a separate `fmp-market-feature-v1` full-history materialization path that reuses the exact 48 Phase 5 feature definitions while preserving the historical `fmp-feature-v1` lock. The manual `phase8a-exp044-market-features` workflow is frozen for nine EURUSD/GBPUSD/USDJPY × 5m/15m/1h cells over 2015-01-01 through 2026-08-20 inclusive, with deterministic double-generation and exact accepted Phase 2 artifact verification.
- Execution status: no authoritative EXP-044 full-history feature workflow has been dispatched yet; no model fit, model selection result, portfolio admission, shadow capture, demo order, broker mutation, live order, or real-money action exists.
- Existing-data rule: the EXP-044 feature workflow reuses the already accepted Phase 2 Dukascopy artifacts and verifies their frozen processed-manifest SHA-256 identities; it performs no new Dukascopy acquisition.
- Aggregate verification source: after all nine feature cells succeed, a dedicated evidence job verifies exact cell coverage, exact source hashes, every emitted artifact byte, the retrospective evidence label, and all non-promotion locks, then writes one deterministic feature-evidence fingerprint. This evidence still sets `model_fit_authorized=false`.
- Aggregate verifier merge: PR #169 merged to `main` at `f8e3b160c45dc346d22ad3aa8f5ac1a54df26174`. Exact final PR head `42875569e8d48862be20453b4963c57335904e45` passed 1111 tests plus workflow-YAML validation and compile in run `35840325472`; unchanged Phase 3 acceptance run `35840325448` passed. No EXP-044 historical feature workflow has been dispatched as a result of this merge.
- Source extension: a vectorized `fmp-market-outcome-grid-v1` layer now prepares the direct 60m/240m supervised targets from exact 1-minute BID/ASK opens. The three frozen adverse-slippage scenarios are stored side-by-side per observation/horizon to avoid tripling row count. Exact missing entry/exit timestamps are counted and excluded rather than shifted or interpolated. Outcome artifacts require a 64-character verified feature-evidence fingerprint and remain `model_fit_authorized=false`.
- Outcome materialization source: persisted aggregate feature evidence is reloaded and fingerprint-verified before use. Each requested cell must match its aggregate manifest SHA-256 and Phase 2 source identity; every feature parquet and every canonical 1-minute Dukascopy parquet used by the materializer is rechecked for size, SHA-256, row count, and schema before the outcome grid is written. The materializer is source-only and still emits `model_fit_authorized=false`.
- Outcome-grid merge: PR #171 merged to `main` at `4dfd9b4cc5d62d2585b027946a3056415fcd3ab7`; exact final PR head `cd6805af35865e589ad606ecd7065f1060ca474a` passed 1117 tests plus YAML/compile in run `35845107487`, and unchanged Phase 3 acceptance run `35845107495` passed.
- Outcome-materializer merge: PR #172 merged to `main` at `428541b310ccc806662818d2141bfe356df023d1`; exact final PR head `be55f852713c1544063b0590cd36207cd1417277` passed 1122 tests plus YAML/compile in run `35845611187`, and unchanged Phase 3 acceptance run `35845611278` passed.
- Outcome workflow source: `phase8a-exp044-market-outcomes` is manual and accepts one required successful feature-run ID. It validates that source run is the exact feature workflow, `workflow_dispatch`, successful, and from `main`; revalidates the feature-evidence fingerprint; rechecks the existing accepted Phase 2 Dukascopy ZIP/manifest identities; materializes the nine pair/timeframe outcome cells; and aggregates them into one deterministic outcome-evidence fingerprint. The aggregate evidence still sets `model_fit_authorized=false` and all shadow/demo/broker/live/real-money flags false. No outcome workflow has been dispatched.
- Outcome-workflow merge: PR #173 merged to `main` at `fc05230462d8743ba5780d3bd2633649e4019b00`; exact PR head `e29437e2ab93462b1a669797e973b7b18dfacd33` passed 1129 tests plus YAML/compile in run `35846186938`, and unchanged Phase 3 acceptance run `35846186891` passed. Post-merge main runs `35846386839` and `35846386975` passed.
- DEC-074 readiness source: after aggregate outcome evidence succeeds, the workflow re-downloads and revalidates the exact source aggregate feature evidence and cross-checks all nine cells. A readiness artifact may set `data_preparation_complete=true` and `model_protocol_source_open_authorized=true` only when outcome evidence binds the exact feature-evidence fingerprint, feature-manifest SHA-256, Phase 2 Dukascopy identity, and feature row count in every cell. It keeps `model_protocol_result_authorized=false`, `model_fit_authorized=false`, promotion false, and all shadow/demo/broker/live/real-money flags false.
- Follow-up: first dispatch and preserve the nine full-history feature artifacts plus aggregate feature evidence from merged `main`; then dispatch the outcome workflow against that exact successful feature-run ID and preserve its nine outcome cells plus aggregate outcome evidence. Only after both evidence layers exist may a separate predeclared model-training protocol freeze model families, preprocessing, chronological splits, targets, thresholds, and financial gates before any result-producing fit.

- DEC-075 execution observability source: a read-only status machine now distinguishes feature dispatch, feature success/evidence, outcome dispatch, outcome success/evidence, DEC-074 readiness, and protocol-source-open. It validates supplied workflow-run identity and persisted readiness fingerprints and fails closed on contradictory evidence. It creates no model-fit or trading authorization.
- DEC-075 merge: PR #176 merged to `main` at `212f3acb24a40084b5f19b24a5290ccb7be0930d`. Exact final PR head `ad0b7f94b5f44547e666ff03e512dcac02673d65` passed 1143 tests plus workflow-YAML validation and compile in run `35848603110`; unchanged Phase 3 acceptance run `35848603258` passed. Post-merge `main` tests run `35848748205` and Phase 3 acceptance run `35848748235` also passed. No EXP-044 feature or outcome workflow has been dispatched by this merge.

- DEC-076 execution optimization: before any EXP-044 feature/outcome run, both workflows were changed from nine pair/timeframe jobs to three pair jobs. Each pair now downloads and verifies its accepted Phase 2 Dukascopy artifact once, then processes 5m/15m/1h sequentially while still uploading the same nine per-timeframe artifacts and preserving the same aggregate evidence gates.
- DEC-076 merge: PR #178 merged to `main` at `b0c29b354470a27145847071a5f8b92fc87eb303`. Exact final PR head `5506add7da89c2ed47f34325882814c4ffb1130d` passed 1147 tests plus workflow-YAML validation and compile in run `35850179816`; unchanged Phase 3 acceptance run `35850179878` passed. Post-merge `main` tests run `35850302402` and Phase 3 acceptance run `35850302338` also passed. No EXP-044 feature or outcome workflow had been dispatched at the time of this merge.
- Point-in-time source availability check on 2026-09-23: accepted Phase 2 artifacts 10325737935, 10326096831, and 10327600628 were all downloadable; downloaded ZIP SHA-256 values exactly matched the frozen EURUSD, GBPUSD, and USDJPY identities already recorded by Phase 2.

- DEC-077 outcome execution optimization: the outcome workflow now uses one pair-level materializer per symbol. After all three feature cells bind the same accepted Phase 2 processed-manifest identity, the 140 one-minute monthly partitions are checksum-verified/read once and the same quote frame is reused sequentially for 5m/15m/1h. Regression tests require exact manifest equivalence with three independent single-cell materializations. No EXP-044 result-producing workflow had run before this amendment.

- DEC-077 merge: PR #180 merged to `main` at `30c500136283117ac24bad734abbc30b34831d46`. Exact final PR head `653b76866bae9dad299866c986a455d6f535430e` passed 1149 tests plus workflow-YAML validation and compile in run `35851579729`; unchanged Phase 3 acceptance run `35851579622` passed. Post-merge `main` tests run `35851703196` and Phase 3 acceptance run `35851703084` also passed.
- DEC-078 source availability gate: the accepted Phase 2 artifact metadata is now a precondition for both EXP-044 workflows. On 2026-09-23 EURUSD artifact `10325737935` (182037581 bytes), GBPUSD `10326096831` (190706384 bytes), and USDJPY `10327600628` (160033414 bytes) were non-expired and retained the frozen SHA-256 identities. EURUSD/GBPUSD expire at `2026-12-12T20:57:47Z`; USDJPY expires at `2026-12-12T21:42:34Z`. The workflow now requires at least 12 hours of remaining lifetime before heavy work begins.

- DEC-078 merge: PR #181 merged to `main` at `e2675cc6f0bac096895e422531443d34230d7109`. Exact final PR head `758cfc34d04af73ae57c224fa8b39109a68042a3` passed 1155 tests plus workflow-YAML validation and compile in run `35852173729`; unchanged Phase 3 acceptance run `35852173707` passed. Post-merge `main` tests run `35852290238` and Phase 3 acceptance run `35852290251` also passed.
- DEC-079 outcome memory optimization: pair-level outcome materialization still validates each complete 55-column feature parquet by size, SHA-256, schema, and row count, but retains only six identity/timing columns in memory for labeling. Projected-label output is required to be exactly equivalent to the full-feature builder.
- DEC-079 merge: PR #182 merged to `main` at `8a6628ed967c1f0318cc522a837554676519194e`. Exact final PR head `fafb8d677422ec924656756ecbadc28ba04d9035` passed 1157 tests plus workflow-YAML validation and compile in run `35852816657`; unchanged Phase 3 acceptance run `35852816582` passed. Post-merge `main` tests run `35852996238` and Phase 3 acceptance run `35852996232` also passed. No EXP-044 feature or outcome workflow had been dispatched at the time of this merge.

- DEC-080 feature execution optimization: each pair/timeframe Phase 2 derived-bar source is now checksum-verified/read once and reused for two sequential feature builds. The A/B outputs remain separately materialized and byte-compared, and regression tests require exact equivalence with the existing single-cell generator. No EXP-044 result-producing workflow had run before this amendment.

- DEC-080 merge: PR #184 merged to `main` at `64b43076751d576212015f40219264bde1d9ff97`. Exact corrected PR head `0d51aeba38d8e95fefb16f75d1dc6df4ba25965c` passed 1159 tests plus workflow-YAML validation and compile in run `35854983964`; unchanged Phase 3 acceptance run `35854983892` passed. Post-merge `main` tests run `35855107489` and Phase 3 acceptance run `35855107485` also passed. No EXP-044 feature or outcome workflow had been dispatched at merge time.
- DEC-081 operator launch source: a dry-run-by-default CLI now reproduces the exact manual feature/outcome dispatch commands while requiring clean merged `main`, exact repository identity, GitHub CLI authentication, no duplicate manual-main run, and (for outcomes) an exact successful feature-run identity. The helper itself claims no workflow result and authorizes no model/trading action.

- DEC-081 merge: PR #185 merged to `main` at `9895ec60ebedadc653f0ccf626d128a881de17e4`. Exact PR head `9be7dc5baebaffc9f35ae68972ed9dc0a21a6d36` passed 1165 tests plus workflow-YAML validation and compile in run `35855512952`; unchanged Phase 3 acceptance run `35855512940` passed. Post-merge `main` tests run `35855680240` and Phase 3 acceptance run `35855680389` also passed. No EXP-044 feature/outcome run existed after merge.
- DEC-082 preservation source: a manual merged-main workflow now preserves the exact original Phase 2 ZIP bytes as a draft-verified GitHub release before publication. The release contract freezes original Actions IDs, source run/head, ZIP hashes/sizes, processed-manifest hashes, tag/title, and asset names. No new data acquisition or model/trading authorization is introduced.
