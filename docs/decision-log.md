# FMP Decision Log

Later approved decisions override older assumptions only when this log says so and affected source-of-truth files are updated in the same change.

Detailed DEC-001 through DEC-013 text is preserved at commit `0ff45220cd930839059afcfba631e1e120cb38aa`, `docs/decision-log.md`, and remains authoritative for historical Phase 1 rules.

Active decision index:

- DEC-001 — Forex-only V1 — APPROVED
- DEC-002 — $0 development constraint — APPROVED
- DEC-003 — Python-owned trading engine — APPROVED
- DEC-004 — Canonical 1-minute bid/ask data — APPROVED
- DEC-005 — Initial historical data source candidate — SUPERSEDED BY DEC-009
- DEC-006 — Simpler model wins ties — APPROVED
- DEC-007 — Backtester before strategy benchmarking — APPROVED
- DEC-008 — Real-money lock — APPROVED
- DEC-009 — Phase 1 Dukascopy retrieval method — APPROVED
- DEC-010 — Dedicated Supabase raw snapshot persistence — APPROVED
- DEC-011 — Serialize and monthly-isolate Dukascopy acquisition — APPROVED
- DEC-012 — Sparse exact-gap Phase 1 cleanup and acceptance safety — APPROVED
- DEC-013 — No in-place cloud promotion of canonical `not_found` manifests — APPROVED
- DEC-014 — Phase 1 frozen snapshot accepted — APPROVED
- DEC-015 — Phase 2 exhaustive acceptance review — APPROVED
- DEC-016 — Phase 3 backtester semantics — APPROVED
- DEC-017 — Phase 3 deterministic acceptance review — APPROVED
- DEC-018 — Phase 4 baseline research protocol — APPROVED
- DEC-019 — Phase 4 trend-continuation baseline protocol — APPROVED
- DEC-020 — Phase 4 mean-reversion baseline protocol — APPROVED
- DEC-021 — Phase 4 mean-reversion experiment outcome — APPROVED
- DEC-022 — Phase 4 previous-day high/low rejection baseline protocol — APPROVED
- DEC-023 — Phase 4 previous-day high/low rejection experiment outcome — APPROVED
- DEC-024 — Phase 4 volatility-breakout baseline protocol — APPROVED
- DEC-025 — Phase 4 volatility-breakout experiment outcome — APPROVED
- DEC-026 — Phase 4 session high/low sweep-rejection baseline protocol — APPROVED
- DEC-027 — Phase 4 session high/low sweep-rejection experiment outcome — APPROVED
- DEC-028 — Phase 4 baseline strategy research acceptance review — APPROVED
- DEC-029 — Phase 5 leakage-safe feature-engine protocol — APPROVED
- DEC-030 — Phase 5 leakage-safe feature-engine acceptance review — APPROVED
- DEC-031 — Phase 6 statistical / ML filter protocol — APPROVED
- DEC-032 — Phase 6 statistical / ML filter experiment outcome and acceptance review — APPROVED
- DEC-033 — Phase 7 walk-forward evaluation protocol — APPROVED
- DEC-034 — Phase 7 Stage 1 final-gate outcome — APPROVED
- DEC-035 — Phase 7 walk-forward outcome and acceptance review — APPROVED
- DEC-036 — Phase 8 live shadow protocol — APPROVED
- DEC-037 — Phase 8 MT5 demo quote bridge amendment — APPROVED
- DEC-038 — Phase 8 bridge/market liveness separation amendment — APPROVED

## DEC-014 — Phase 1 frozen snapshot accepted

**Date:** 2026-09-13  
**Status:** APPROVED

Phase 1 is accepted for the frozen EURUSD, GBPUSD, and USDJPY BID/ASK snapshot covering 2015-01-01 through 2026-08-20 inclusive.

Evidence: 25,500 expected and present raw-backed manifests; zero missing/unexpected identities; zero inferred `not_found`; final cloud provenance run `34758527971` on `0ff45220cd930839059afcfba631e1e120cb38aa` reported zero invalid manifests/raw audits/checksum or size mismatches; cross-report acceptance was 55 passed, 0 failed. Frozen plan SHA-256 is `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`.

Consequences: Phase 1 PASS; Phase 2 unlocked; no further Phase 1 acquisition is required unless later integrity evidence demands it; DEC-008 remains unchanged.

## DEC-015 — Phase 2 exhaustive acceptance review

**Date:** 2026-09-14  
**Status:** APPROVED

`phase2-full-history` run `34782357048` on `158c1c121655867b7fb2886fe755585dfcd682ec` completed successfully on attempt 2. For each pair, acceptance proved exactly 8,500 verified reads, 140 months, 140 monthly partitions for each 1m/5m/15m/1h timeframe, row counts of 6,120,000 / 1,224,000 / 408,000 / 102,000, and a 561-artifact processed manifest.

Independent artifact inspection found zero digest, size, ledger-identity, or monthly-partition validation errors. All three quality reports have zero duplicates, missing BID/ASK rows, required nulls, missing open-market minutes, and suspicious gaps. Outlier telemetry is retained without silent mutation. Required canonical, quote-sanity, boundary/resampling, weekend-gap, DST, ledger, workflow-guard, and materialization tests were green.

USDJPY attempt 1 received one HTTP 401 from the read-only raw Edge Function; an isolated no-change rerun succeeded, so the failure did not reproduce as a deterministic data/materialization defect.

Checkpoint `fmp-v1-phase2-normalized-data` was created at verified acceptance commit `80e763c46fc365d48922fb37de1a70dfe188de70`.

Consequences: Phase 2 is formally PASS and closed at `fmp-v1-phase2-normalized-data`; Phase 3 remains unstarted; DEC-008 remains unchanged. Detailed evidence is in `docs/phase2-acceptance-evidence.md`.

## DEC-016 — Phase 3 backtester semantics

**Date:** 2026-09-14  
**Status:** APPROVED

Phase 3 uses a deterministic, broker-independent backtesting engine over the accepted canonical bid/ask data. Its risk and execution semantics are frozen as follows:

- Daily loss control uses UTC day-start **realized risk equity** as its basis.
- Realized daily PnL at or below `-1.50%` of that basis blocks new entries for the remainder of the UTC date.
- Existing positions are not force-closed solely because the daily-loss halt becomes active.
- Existing-position exits are processed before new entries at the same timestamp, so released risk is immediately available to later same-timestamp decisions.
- Simultaneous eligible decisions are ordered deterministically by `decision_id`.
- LONG entries execute from ASK and LONG exits from BID; SHORT entries execute from BID and SHORT exits from ASK.
- If both stop and target are reachable within a bar and the path is unresolved, STOP wins and the trade is marked intrabar-ambiguous.
- An adverse stop gap uses the worse executable-side open; a favorable target gap receives no price improvement beyond the declared target.
- End-of-data closure uses the final executable close side: BID close for LONG and ASK close for SHORT.
- Slippage is adverse and accounted exactly once; commission and financing are explicit cost components.
- USDJPY stop sizing converts quote-currency loss at the stop price, while realized USDJPY PnL converts at the executable exit price.
- Backtest artifacts are deterministic and contain no runtime clock, hostname, UUID, or process metadata.

These semantics grant no real-money permission and do not alter DEC-008. Phase 4 remains unstarted.

## DEC-017 — Phase 3 deterministic acceptance review

**Date:** 2026-09-14  
**Status:** APPROVED

Phase 3's acceptance gate is approved from merged-main evidence.

Implementation PR #78 merged as `96ca80b3baae4de511b5b14eb6c2f9d4d723645b`. The source-free acceptance-runner PR #79 merged as `f7d98676d40f9af67f2d6f6cde36b3a465f68741`. Exact merged-main test run `34838682046` completed successfully with 300 tests, workflow YAML validation, and package compile all passing.

Formal acceptance workflow run `34838682032` on exact main SHA `f7d98676d40f9af67f2d6f6cde36b3a465f68741` completed successfully and produced artifact `10344943075`, whose GitHub SHA-256 and independently recomputed ZIP SHA-256 both equal `357152cef5118163f06f9d6166e7e02cdd7ed556a3de1c5723a6a6079bd6c4f0`.

Independent inspection verified all five scripted scenarios, all primary/repeat artifact bytes, every manifest-listed SHA/size, run identities, realized-equity checkpoints, hand-calculated PnL/costs, rejection codes, and independently recomputed metrics with zero validation errors. The reviewed scenarios prove LONG/SHORT executable-side pricing, nonzero slippage/commission accounting, conservative same-bar ambiguity, simultaneous-risk rejection, daily realized-loss halt, and next-UTC-day reset. The merged-main suite additionally proves USDJPY sizing/PnL conversion, timing/no-lookahead, gap handling, exact risk boundaries, exit-before-entry risk release, stable decision ordering, EOD side selection, and deterministic serialization.

The evidence merge SHA triggered exactly `tests` and `phase3-acceptance`; no Phase 1 acquisition-capable workflow triggered for that SHA. No source acquisition, raw mutation, Supabase write, broker/live path, Phase 4 strategy code, or real-money permission was introduced.

Checkpoint branch `fmp-v1-phase3-backtester` was created after the acceptance-closure merge and independently verified to resolve exactly to commit `7685ba73f18457d5d3945f2fea21ceba3de81cf1`, which contains `docs/phase3-acceptance-evidence.md` and this acceptance decision.

Consequences: Phase 3 is formally PASS and closed at `fmp-v1-phase3-backtester`. Phase 4 remains unstarted and DEC-008 remains unchanged. Detailed evidence is in `docs/phase3-acceptance-evidence.md`.

## DEC-018 — Phase 4 baseline research protocol

**Date:** 2026-09-14  
**Status:** APPROVED

Phase 4 begins with the session-breakout family under a frozen chronological, anti-leakage, source-free research protocol. No profitability is assumed; failed and empty configurations remain evidence.

- Development: 2015-01-01 through 2020-12-31 inclusive.
- Validation: 2021-01-01 through 2023-12-31 inclusive.
- Final untouched test: 2024-01-01 through 2026-08-20 inclusive.
- The final-test data is unavailable from the normal development/validation runner. Final access requires a separate explicit promotion step after candidate selection is materially complete.
- Phase 2 derived bars are left-labelled. For a timeframe of width `W`, the observation label `T` identifies the start of the closed bar; true signal-known time is `T + W`. The Phase 3 decision timestamp remains `T`, while the earliest executable timestamp is `T + W`, preserving the accepted next-bar execution contract without implying same-bar knowledge.
- The session-breakout grid is exactly `(0, 0.5), (0, 1.0), (0, 1.5), (2, 0.5), (2, 1.0), (2, 1.5), (5, 0.5), (5, 1.0), (5, 1.5)`, representing buffer pips and target range multiples.
- Predeclared adverse slippage is 0.2, 0.5, and 1.0 pips per fill.
- The initial mandatory-intraday-flat family uses zero commission and zero financing; historical BID/ASK spread remains in execution prices.
- Phase 3 risk settings are unchanged: requested risk/trade: 0.25%; hard max risk/trade: 0.50%; maximum simultaneous open risk: 1.00%; daily realized-loss halt: 1.50% of UTC day-start realized risk equity.

Consequences: Phase 4 is ACTIVE for sequential baseline research. Development and validation may run only under the predeclared protocol; the final test remains untouched. Phase 5 remains unstarted, real-money trading remains locked, and DEC-008 remains unchanged.

## DEC-019 — Phase 4 trend-continuation baseline protocol

**Date:** 2026-09-14  
**Status:** APPROVED

The second sequential Phase 4 family is the deterministic trend-continuation baseline. DEC-018 remains authoritative for the chronological split, final-test lock, left-labelled timing bridge, source-free research boundary, cost model, and Phase 3 risk policy.

- Trend context uses midpoint-close simple moving averages with wall-clock window pairs exactly `2h/8h`, `4h/16h`, and `8h/32h`.
- LONG requires fast SMA above slow SMA and a rising slow SMA; SHORT is the exact inverse; equality is neutral.
- Eligible observation labels are 08:00 through 14:00 inclusive in `Europe/London`, using only fully closed bars and the DEC-018 true-known timing bridge.
- A LONG continuation requires the previous closed midpoint close at or below its fast SMA and the current close strictly above the current fast SMA under LONG trend context; SHORT is symmetric.
- Only the first qualifying directional signal per London date may become a candidate.
- The stop is a fixed three-bar structural stop: LONG uses the minimum midpoint low of the signal bar and two immediately preceding closed bars; SHORT uses the maximum midpoint high.
- Signal-time risk `R` is the distance from the signal midpoint close to the frozen structural stop. Targets are exactly `1.0R` and `1.5R` from the signal midpoint close.
- The actual next-bar BID/ASK entry may invalidate the frozen stop/target geometry; such orders are rejected with the accepted Phase 3 `INVALID_STOP_TARGET` semantics and are never repaired, chased, or retried.
- Every opened position carries the exact mandatory flat timestamp 16:00 `Europe/London`; missing exact exit data fails closed.
- The search grid is exactly 3 trend-window pairs × 2 target multiples = 6 strategy configurations per pair/timeframe.
- Development/validation evidence is exactly 3 pairs × 3 timeframes × 2 splits × 6 configurations × 3 cost scenarios = 324 benchmark configuration rows.
- Adverse slippage remains 0.2, 0.5, and 1.0 pips per fill; the family uses zero commission and zero financing, with historical BID/ASK spread inherent in Phase 3 fills.
- Phase 3 risk settings remain unchanged: requested risk/trade: 0.25%; hard max risk/trade: 0.50%; maximum simultaneous open risk: 1.00%; daily realized-loss halt: 1.50% of UTC day-start realized risk equity.
- Final untouched test: 2024-01-01 through 2026-08-20 inclusive. Normal trend-continuation tooling cannot access it.
- There is no post-result parameter expansion under `EXP-20260914-002`; losing, rejected, and no-trade configurations remain evidence.

Consequences: `EXP-20260914-002` may run only after this protocol is present on the result-producing implementation head. Phase 4 remains ACTIVE, the frozen session-breakout candidate remains unchanged, Phase 5 remains unstarted, final-test access remains locked, and DEC-008 remains unchanged.

## DEC-020 — Phase 4 mean-reversion baseline protocol

**Date:** 2026-09-14  
**Status:** APPROVED

The third sequential Phase 4 family is the deterministic intraday mean-reversion baseline described in `docs/superpowers/specs/2026-09-14-phase4-mean-reversion-design.md`. DEC-018 remains authoritative for the chronological split, final-test lock, left-labelled timing bridge, source-free research boundary, cost model, and accepted Phase 3 risk policy.

- Signal analysis uses midpoint close only; BID/ASK remain the sole execution-price source inside Phase 3.
- Eligible observation labels are 08:00 through 14:00 inclusive in `Europe/London`; exact mandatory flat timestamp is 16:00 local and missing exact exit data fails closed.
- Rolling reference lookbacks are exactly 4h, 8h, and 16h and must convert exactly to a whole number of 5m/15m/1h bars.
- For an observation at index `i`, the reference mean and population standard deviation use the **preceding N fully closed bars only**, excluding the observation bar itself. This makes the signal a displacement from pre-existing context and avoids self-dilution.
- Current z-score is `(current_mid_close - reference_mean) / reference_std`. The previous z-score uses the immediately preceding bar with its own preceding-N reference window; at the 08:00 session boundary that previous bar may lie before the eligible signal window.
- Both current and previous reference windows must have exact cadence, sufficient history, finite values, and positive finite population standard deviation. Otherwise the observation is ineligible and history is never shortened.
- Absolute fresh-excursion thresholds are exactly 1.5σ and 2.0σ. LONG requires previous `z > -k` and current `z <= -k`; SHORT requires previous `z < +k` and current `z >= +k`.
- Only the first qualifying directional signal per symbol/configuration/London date may become a candidate. Remaining outside the band does not retrigger; later signals that day are ignored even if the first order is rejected by Phase 3.
- LONG target is the signal-time reference mean and stop is `signal_mid_close - 1.0 * reference_std`; SHORT target is the reference mean and stop is `signal_mid_close + 1.0 * reference_std`.
- The actual next-bar BID/ASK entry may invalidate the frozen geometry; such orders are rejected with accepted `INVALID_STOP_TARGET` semantics and are never repaired, chased, widened, or retried.
- The grid is exactly 3 lookbacks × 2 thresholds = 6 strategy configurations per pair/timeframe.
- Development/validation evidence is exactly 3 pairs × 3 timeframes × 2 splits × 6 configurations × 3 adverse-slippage scenarios = 324 benchmark configuration rows.
- Adverse slippage remains 0.2, 0.5, and 1.0 pips per fill; commission and financing remain zero for the mandatory-intraday-flat family; historical BID/ASK spread remains inherent in Phase 3 fills.
- Phase 3 risk settings remain unchanged: requested risk/trade 0.25%; hard max risk/trade 0.50%; maximum simultaneous open risk 1.00%; daily realized-loss halt 1.50% of UTC day-start realized risk equity.
- A serious candidate must first use the same frozen lookback/threshold configuration to achieve positive net return, positive expectancy/trade, and profit factor above one on both development and validation at 0.2-pip baseline slippage. Any survivor is then reviewed for 0.5-pip stress, neighboring-parameter stability, subperiod concentration, sample size, drawdown, and top-winner dependence. The 1.0-pip scenario remains diagnostic rather than a universal mandatory promotion condition.
- There is no post-result parameter expansion under `EXP-20260914-003`; losing, rejected, and no-trade configurations remain evidence.
- Normal mean-reversion tooling cannot access the final 2024-01-01 through 2026-08-20 test split.

Consequences: `EXP-20260914-003` may run only after this protocol and its implementation are merged to `main`. The frozen USDJPY 15m session-breakout candidate remains unchanged; rejected trend-continuation parameters stay rejected; Phase 4 remains ACTIVE; Phase 5 remains unstarted; final-test access and broker/live/real-money permissions remain locked; DEC-008 remains unchanged.

## DEC-021 — Phase 4 mean-reversion experiment outcome

**Date:** 2026-09-14  
**Status:** APPROVED

Merged-main mean-reversion benchmark run `34875463677` on exact code commit `87003a3982ca61eb6fd030c5291616d98dbb0c1a` completed successfully. All 18 pair/timeframe/split cells succeeded and all 324 frozen configuration rows were independently verified with zero ZIP, manifest, code/data identity, split, grid, candidate-reuse, or cost/risk identity errors. The final-test split was not used.

At the predeclared 0.2-pip baseline gate, zero of 54 pair/timeframe/lookback/threshold points survived. More strongly, on both development and validation, zero of 54 baseline rows had positive net return, zero had positive expectancy/trade, and zero had profit factor above one. Because the first frozen promotion gate failed universally, no downstream cost result may be used to rescue or retune this experiment after observation.

Consequences: `EXP-20260914-003` is FAIL / REJECT; no mean-reversion candidate is promoted and no post-result parameter expansion is authorized under this experiment ID. The frozen USDJPY 15m session-breakout candidate remains unchanged. Phase 4 remains ACTIVE and the next approved baseline family is previous-day high/low rejection. The final-test period, Phase 5, broker/live integration, and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase4-mean-reversion-evidence.md`.

## DEC-022 — Phase 4 previous-day high/low rejection baseline protocol

**Date:** 2026-09-14  
**Status:** APPROVED

The fourth sequential Phase 4 family is the deterministic New-York-close previous-day high/low rejection baseline recorded as `EXP-20260914-004`. DEC-018 remains authoritative for the chronological split, final-test lock, left-labelled timing bridge, historical BID/ASK execution, source-free research boundary, cost model, and accepted Phase 3 risk policy.

- For each London research date, the reference is the most recent completed FX trading session `[17:00 America/New_York, 17:00 America/New_York)`, with session ends restricted to Monday through Friday. Monday-morning signals reference the completed Friday session rather than the Sunday reopen.
- The full reference session must have exact expected cadence at the tested signal timeframe; missing reference data fails closed.
- Previous-day high and low are midpoint-quote extrema at the tested signal timeframe. `previous_day_midpoint = (high + low) / 2` is frozen before the signal decision.
- Eligible observation labels remain 08:00 through 14:00 inclusive in `Europe/London`; the immediately preceding closed bar may lie before 08:00. The exact mandatory flat timestamp remains 16:00 local.
- Required signal-session cadence must be complete. Completeness failures and complete dates without a rejection emit deterministic reasoned no-trade evidence wherever a valid timestamp can be represented.
- Penetration buffers are exactly 0, 2, and 5 pips.
- SHORT requires the previous midpoint close at or below the previous-day high, the current midpoint high at or above `high + buffer`, and the current midpoint close strictly below the high. LONG is symmetric at the previous-day low.
- A bar qualifying simultaneously at both levels fails closed as `AMBIGUOUS_DUAL_REJECTION`.
- Only the first directional rejection per symbol/configuration/London date is emitted. A later Phase 3 rejection never permits another attempt that date.
- LONG stop is frozen at the signal midpoint low; SHORT stop is frozen at the signal midpoint high; the target is the frozen previous-day midpoint.
- Actual next-bar BID/ASK entry remains authoritative. Invalid stop/target geometry is rejected under existing Phase 3 semantics and is never repaired or chased.
- The grid is exactly 3 buffers per pair/timeframe. Candidate bytes for a fixed pair/timeframe/split/buffer are reused unchanged across cost scenarios.
- Development/validation evidence is exactly 3 pairs × 3 timeframes × 2 splits × 3 buffers × 3 adverse-slippage scenarios = 162 benchmark rows.
- Adverse slippage remains exactly 0.2, 0.5, and 1.0 pips per fill; historical BID/ASK spread remains authoritative; commission and financing remain zero.
- Phase 3 risk settings remain unchanged: requested risk/trade 0.25%; hard max risk/trade 0.50%; maximum simultaneous open risk 1.00%; daily realized-loss halt 1.50% of UTC day-start realized risk equity.
- Promotion begins at 0.2-pip slippage: the same buffer must have positive net return, positive expectancy/trade, and profit factor above one on both development and validation. Only survivors receive 0.5-pip robustness, neighboring-buffer stability, subperiod concentration, sample-size, drawdown, and top-winner-dependence review; 1.0 pip remains diagnostic.
- No post-result parameter expansion is permitted under `EXP-20260914-004`.
- Normal tooling for this experiment cannot access the final 2024-01-01 through 2026-08-20 test split.

Consequences: `EXP-20260914-004` may run only after this protocol and implementation are merged to `main`. The frozen USDJPY 15m session-breakout candidate remains unchanged. Phase 4 remains ACTIVE; Phase 5, final-test access, broker/live integration, and real-money trading remain locked; DEC-008 remains unchanged.

## DEC-023 — Phase 4 previous-day high/low rejection experiment outcome

**Date:** 2026-09-14  
**Status:** APPROVED

Merged-main previous-day rejection benchmark run `34883815436` on exact implementation commit `7db3a747236942fa393521e5866e3245d1a22a99` completed successfully. All 18 pair/timeframe/split cells succeeded and all 162 frozen configuration rows were independently verified with zero ZIP, manifest, code/data identity, split, grid, candidate-reuse, accounting, or cost/risk identity errors. The final-test split was not used.

At the frozen 0.2-pip baseline gate, exactly one of 27 pair/timeframe/buffer points survived: USDJPY 5m / 5-pip penetration buffer. Development was +4.0039% net return, +$138.0644 expectancy/trade, PF 1.9002 on 29 trades. Validation was only +0.0657%, +$2.3461 expectancy/trade, PF 1.0133 on 28 trades.

The survivor fails the predeclared robustness review. At 0.5-pip adverse slippage validation turns negative (-0.2343%, -$8.3685 expectancy/trade, PF 0.9547); both neighboring 0- and 2-pip buffers are negative on both development and validation; validation is negative in 2021 and 2022 and positive only in 2023; and the top three winners contribute about 85.38% of validation positive R. No post-result widening, alternate buffer search, or rescue rule is authorized.

Consequences: `EXP-20260914-004` is FAIL / REJECT; no previous-day high/low rejection candidate is promoted. The frozen USDJPY 15m session-breakout candidate remains unchanged. Phase 4 remains ACTIVE and the next baseline family in the original approved baseline-first sequence is **volatility breakout**; session high/low sweep/rejection remains the later sixth family. The volatility-breakout protocol must be separately predeclared before any result-producing implementation or benchmark. The final-test period, Phase 5, broker/live integration, and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase4-previous-day-rejection-evidence.md`.

## DEC-024 — Phase 4 volatility-breakout baseline protocol

**Date:** 2026-09-14  
**Status:** APPROVED

The fifth sequential Phase 4 family is the deterministic rolling volatility-breakout baseline recorded as `EXP-20260914-005`. DEC-018 remains authoritative for the chronological split, final-test lock, left-labelled timing bridge, historical BID/ASK execution, source-free research boundary, shared cost model, and accepted Phase 3 risk policy.

- Pairs are EURUSD, GBPUSD, and USDJPY; signal timeframes are 5m, 15m, and 1h.
- Eligible observation labels are 08:00 through 14:00 inclusive in `Europe/London`; the exact mandatory flat timestamp is 16:00 local.
- For an eligible signal bar left-labelled `T`, the rolling reference window is exactly `[T - 8h, T)` at the tested timeframe. The signal bar is excluded.
- The full 8-hour reference must have exact expected cadence and finite midpoint OHLC. Missing or malformed data fails closed; the window is never shortened or repaired.
- `reference_high` and `reference_low` are midpoint extrema over the reference window. `reference_median_range` is the median of each reference bar's midpoint high-minus-low range and must be finite and strictly positive.
- The only strategy configurations are range-expansion multipliers exactly 1.0x, 1.5x, and 2.0x.
- LONG requires the signal midpoint close strictly above `reference_high` and the signal midpoint range at least `multiplier * reference_median_range`. SHORT is symmetric below `reference_low`.
- Only the first qualifying directional breakout per symbol/configuration/London date is emitted. A later Phase 3 rejection does not permit another attempt that date.
- LONG stop is the signal midpoint low; SHORT stop is the signal midpoint high. Signal-time risk `R` is measured from signal midpoint close to that frozen stop, and the target is fixed at exactly 1.0R in the trade direction.
- Actual next-bar BID/ASK entry remains authoritative. Invalid executable stop/target geometry is rejected under existing Phase 3 `INVALID_STOP_TARGET` semantics and is never repaired, chased, widened, or retried.
- Required signal-session cadence through the exact 16:00 flat timestamp must be complete. Complete dates without a setup emit deterministic `NO_VOLATILITY_BREAKOUT` evidence; completeness failures fail closed with deterministic reasoned no-trade evidence where representable.
- Candidate generation and candidate bytes for a fixed pair/timeframe/split/multiplier are identical across cost scenarios.
- Development/validation evidence is exactly 3 pairs × 3 timeframes × 2 splits × 3 multipliers × 3 adverse-slippage scenarios = 162 benchmark rows.
- Adverse slippage remains exactly 0.2, 0.5, and 1.0 pips per fill; historical BID/ASK spread remains authoritative; commission and financing remain zero.
- Phase 3 risk settings remain unchanged: requested risk/trade 0.25%; hard max risk/trade 0.50%; maximum simultaneous open risk 1.00%; daily realized-loss halt 1.50% of UTC day-start realized risk equity.
- Promotion begins at 0.2-pip slippage: the same multiplier must have positive net return, positive expectancy/trade, and profit factor above one on both development and validation. Only survivors receive 0.5-pip robustness, neighboring-multiplier stability, subperiod concentration, sample-size, drawdown, and top-winner-dependence review; 1.0 pip remains diagnostic.
- No post-result parameter expansion, alternate lookback, extra multiplier, target retuning, or rescue rule is permitted under `EXP-20260914-005`.
- Normal EXP-005 tooling cannot access the final 2024-01-01 through 2026-08-20 test split.

Consequences: EXP-005 implementation and development/validation benchmarking are authorized only under this exact predeclared protocol after the protocol is present on the result-producing implementation head. The frozen USDJPY 15m session-breakout candidate remains unchanged. Session high/low sweep/rejection remains the later sixth baseline family. Phase 4 remains ACTIVE; Phase 5, final-test access, broker/live integration, and real-money trading remain locked; DEC-008 remains unchanged. Detailed predeclaration is in `docs/phase4-volatility-breakout-predeclaration.md`.

## DEC-025 — Phase 4 volatility-breakout experiment outcome

**Date:** 2026-09-14
**Status:** APPROVED

Merged-main volatility-breakout benchmark run `34888225242` on exact implementation commit `3bf36186900f5065e9e3ddced0305865433b9d69` completed successfully. Merged-main tests run `34888225240` and unchanged Phase 3 acceptance run `34888225252` also completed successfully. All 18 pair/timeframe/split cells succeeded and all 162 frozen benchmark rows were independently verified with zero ZIP, inner-manifest, code/data identity, split, grid, candidate-reuse, accounting, cost, or risk-identity errors. The final-test split was not used.

At the frozen 0.2-pip baseline gate, exactly one of 27 pair/timeframe/multiplier points survived: **USDJPY 1h / 2.0x range-expansion multiplier**. Development returned +11.4235% with +$19.1670 expectancy/trade, PF 1.2321, 596 trades, and 2.5228% max drawdown. Validation returned +5.5971% with +$15.3766 expectancy/trade, PF 1.1931, 364 trades, and 1.9853% max drawdown.

The survivor passes the predeclared 0.5-pip robustness review, remaining positive on both splits (+6.5350% development, PF 1.1297; +3.2953% validation, PF 1.1111). The 1.0-pip diagnostic is negative on both splits and remains a material cost-sensitivity limitation. Neighboring multipliers and adjacent timeframes do not confirm the development edge. Against those weaknesses, the exact point has a substantial sample, low drawdown, positive net PnL in all six development calendar years, positive validation in 2022 and 2023 despite a negative 2021, and very low top-winner dependence (top three positive-R trades about 1.30% of development positive R and 2.22% of validation positive R). No post-result widening, alternate lookback, extra multiplier, target retuning, or rescue rule is authorized.

Consequences: `EXP-20260914-005` is PASS / PROMOTE. Retain **USDJPY 1h / 2.0x / fixed 1.0R** unchanged as a serious Phase 4 research candidate. This adds a second serious candidate and does not supersede the frozen USDJPY 15m / 5-pip / 1.5x session-breakout candidate from EXP-001. Phase 4 remains ACTIVE and the next baseline family is the sixth planned **session high/low sweep/rejection** family. The final-test period, Phase 5, broker/live integration, and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase4-volatility-breakout-evidence.md`.

## DEC-026 — Phase 4 session high/low sweep-rejection baseline protocol

**Date:** 2026-09-14
**Status:** APPROVED

The sixth sequential Phase 4 family is the deterministic Asian-session high/low sweep-rejection baseline recorded as `EXP-20260914-006`. The approved written design is `docs/superpowers/specs/2026-09-14-phase4-session-sweep-rejection-design.md`. DEC-018 remains authoritative for the chronological split, final-test isolation, left-labelled timing bridge, source-free research boundary, historical BID/ASK execution, shared cost model, and accepted Phase 3 risk policy.

- Pairs are EURUSD, GBPUSD, and USDJPY; signal timeframes are 5m, 15m, and 1h.
- The frozen reference session is exactly `[00:00, 08:00) Europe/London` at the tested timeframe, with exact cadence and finite midpoint OHLC required. The reference high, low, and midpoint are frozen for the London date.
- Eligible current observation labels are 08:00 through 14:00 inclusive; exact mandatory flat is 16:00 London local. Time conversion must be DST-aware.
- Penetration buffers are exactly 0, 2, and 5 pips. These are the only strategy configurations.
- SHORT requires previous midpoint close `<= reference_high`, current midpoint high `>= reference_high + buffer`, and current midpoint close strictly `< reference_high`. LONG is symmetric at the frozen reference low.
- A bar satisfying both directional predicates fails closed as `AMBIGUOUS_DUAL_SESSION_SWEEP`.
- Only the first qualifying directional sweep/rejection per symbol/configuration/London date may become a candidate. A later Phase 3 rejection does not permit a retry that date.
- LONG stop is the signal midpoint low; SHORT stop is the signal midpoint high; target is the frozen session midpoint. Invalid signal-time or executable geometry is never repaired, chased, widened, or retried.
- Candidate generation and bytes for a fixed pair/timeframe/split/buffer are identical across costs.
- Development/validation evidence is exactly 3 pairs × 3 timeframes × 2 splits × 3 buffers × 3 adverse-slippage scenarios = 162 benchmark rows.
- Adverse slippage remains exactly 0.2, 0.5, and 1.0 pips per fill; commission and financing remain zero; historical BID/ASK spread remains authoritative.
- Phase 3 risk settings remain unchanged: requested risk/trade 0.25%; hard max risk/trade 0.50%; maximum simultaneous open risk 1.00%; daily realized-loss halt 1.50% of UTC day-start realized risk equity.
- Promotion begins at 0.2-pip slippage: the same buffer must have positive net return, positive expectancy/trade, and profit factor above one on both development and validation. Survivors then receive the established 0.5-pip robustness, neighboring-buffer, subperiod, sample-size, drawdown, and top-winner review; 1.0 pip remains diagnostic.
- No post-result parameter expansion, alternate reference session, extra buffer, target retuning, stop retuning, or rescue rule is permitted under `EXP-20260914-006`.
- Normal EXP-006 tooling cannot access the final 2024-01-01 through 2026-08-20 split.

Consequences: EXP-006 implementation and development/validation benchmarking are authorized only after this protocol is present on the result-producing implementation head. The two serious candidates from EXP-001 and EXP-005 remain frozen unchanged. Phase 4 remains ACTIVE; final-test access, Phase 5, broker/live integration, and real-money trading remain locked; DEC-008 remains unchanged.

## DEC-027 — Phase 4 session high/low sweep-rejection experiment outcome

**Date:** 2026-09-14
**Status:** APPROVED

Merged-main session sweep-rejection benchmark run `34895426037` on exact implementation commit `120348d4a5df806f674551590610b216a9bc33ac` completed successfully. Merged-main tests run `34895426082` and unchanged Phase 3 acceptance run `34895426066` also completed successfully. All 18 pair/timeframe/split cells succeeded and all 162 frozen benchmark rows were independently verified with zero ZIP, inner-manifest, code/data identity, split, grid, candidate-reuse, accounting, cost, or risk-identity errors. The final-test split was not used.

At the frozen 0.2-pip baseline gate, zero of 27 pair/timeframe/buffer points survive on both development and validation. The only development-only qualifier, USDJPY 5m / 2-pip buffer, reverses from +1.9167% development return, +$5.6874 expectancy/trade, and PF 1.0282 to -15.4056% validation return, -$64.1899 expectancy/trade, and PF 0.6706. Two USDJPY 1h validation-only qualifiers also fail development: the 2-pip point is -4.0619% development versus +0.5797% validation, and the 5-pip point is -0.3861% development versus +0.2743% validation. No downstream cost result may rescue a point that fails the predeclared two-split baseline gate.

Consequences: `EXP-20260914-006` is FAIL / REJECT; no session high/low sweep-rejection candidate is promoted and no post-result parameter expansion, alternate reference session, extra buffer, target/stop retuning, or rescue rule is authorized. The two serious candidates from EXP-001 and EXP-005 remain frozen unchanged. This completes development/validation benchmarking of all six planned Phase 4 baseline families. Phase 4 remains ACTIVE only until its separate acceptance/checkpoint review is formally recorded; the final-test period remains locked and is not authorized by this decision. Phase 5, broker/live integration, and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase4-session-sweep-rejection-evidence.md`.

## DEC-028 — Phase 4 baseline strategy research acceptance review

**Date:** 2026-09-14
**Status:** APPROVED

Phase 4 is accepted as PASS under the project-source acceptance gate. All six planned baseline families completed deterministic development/validation benchmarking and are recorded in the human-readable experiment registry, including rejected experiments. The six authoritative matrices comprise 108/108 successful pair/timeframe/split cells and 1,620/1,620 independently inspected frozen benchmark rows across EXP-001 through EXP-006. Every Phase 4 experiment records `Final-test touched?: NO`.

The acceptance gate is satisfied through the serious-candidate path. Two research candidates remain frozen unchanged: **USDJPY 15m / 5-pip breakout buffer / 1.5x target-range** from EXP-001 and **USDJPY 1h / 2.0x range-expansion multiplier / fixed 1.0R** from EXP-005. EXP-002 trend continuation, EXP-003 mean reversion, EXP-004 previous-day rejection, and EXP-006 session sweep-rejection remain rejected with their negative evidence preserved. No post-result rescue search or candidate retuning is authorized by this acceptance review.

Consequences: Phase 4 is formally PASS and closed. Checkpoint `fmp-v1-phase4-baselines` is to be created at the verified merged acceptance-closure commit after post-merge source-free regression checks succeed. Phase 5 becomes the next project phase but remains UNSTARTED until its own leakage-safe design/implementation work begins. The final untouched 2024-01-01 through 2026-08-20 test period remains locked; this decision does not authorize final-test inspection. Broker/live integration and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase4-acceptance-evidence.md`.

## DEC-029 — Phase 5 leakage-safe feature-engine protocol

**Date:** 2026-09-14
**Status:** APPROVED

Phase 5 begins under the user-approved written design in `docs/superpowers/specs/2026-09-14-phase5-leakage-safe-feature-engine-design.md`. The design is authoritative for `fmp-feature-v1` unless a later approved decision explicitly supersedes it.

Frozen V1 scope and leakage controls:

- Feature tables cover exactly EURUSD, GBPUSD, and USDJPY at 5m, 15m, and 1h. No separate 1m feature matrix is authorized.
- Normal Phase 5 feature generation may open processed source partitions only through 2023-12-31. Any request whose required source coverage reaches 2024-01-01 or later must fail before that final-test partition is opened.
- A feature row for a left-labelled bar beginning at `T` and width `D` becomes available only at `T + D`; the current fully closed bar may be used, but no observation ending after `available_at_utc` may contribute.
- `fmp-feature-v1` contains exactly eight promoted families: returns, volatility/range, trend/structure, momentum, candle structure, session/time, market location, and spread/quote quality. Relative source activity, cross-pair joins, multi-timeframe joins, labels, models, and target-driven feature selection are not authorized in this version.
- Price-distance features use deterministic midpoint OHLC with pip sizes EURUSD/GBPUSD `0.0001` and USDJPY `0.01`; Phase 3 BID/ASK execution semantics are unchanged.
- Rolling and exact-duration features require finite, exact-cadence source history. They never shorten lookbacks or generically forward-fill across closures/gaps. Warm-up and incomplete-reference cases remain null.
- Session/time features use named time zones with the approved Asia `09:00–17:00 Asia/Tokyo`, London `08:00–16:00 Europe/London`, and New York `08:00–17:00 America/New_York` definitions, including DST-mismatch tests.
- Previous-day/session location levels may persist only by explicit completed-reference semantics; incomplete sessions are never used. Previous FX day retains the tested New-York-close convention.
- Every promoted family must pass leakage tests including prefix equivalence, future perturbation, current-closed-bar allowance, cadence/closure behavior, reference-session completeness, DST correctness, deterministic regeneration, schema/key guards, and the hard final-test reader block.
- Phase 5 acceptance is exactly 3 pairs × 3 timeframes = 9 source-free generation cells over 2015-01-01 through 2023-12-31, with reproducible manifests/digests and unchanged repository-wide regression surfaces.

Consequences: Phase 5 is ACTIVE for test-first implementation of the approved leakage-safe feature engine. Phase 4 remains frozen PASS at checkpoint `fmp-v1-phase4-baselines`. The 2024-01-01 through 2026-08-20 final-test period remains locked; Phase 6 model fitting, broker/live/demo integration, and real-money trading remain unauthorized. DEC-008 remains unchanged.

## DEC-030 — Phase 5 leakage-safe feature-engine acceptance review

**Date:** 2026-09-15
**Status:** APPROVED

Phase 5 is accepted as PASS under DEC-029 and the build-order acceptance gate. The authoritative manual source-free `phase5-features` run `34910227756` executed on exact merged implementation SHA `74dce1b945ad31a05416a4fc9e63443a884cb90c`; all 9/9 EURUSD/GBPUSD/USDJPY × 5m/15m/1h cells succeeded. Each cell verified the accepted Phase 2 artifact and processed-manifest identity, regenerated `fmp-feature-v1` twice deterministically, verified locked pre-2024 coverage, and uploaded evidence.

Independent inspection of all nine evidence ZIPs verified 9/9 ZIP digests, 972/972 monthly Parquet SHA/size/footer-row-count records, exact 55-column schema agreement, 108 source months per cell from 2015-01 through 2023-12, 48 feature fields/null-count entries, no 1m outputs, no 2024+ output paths, and zero audit errors. Total accepted rows are 4,023,279. The merged-main implementation regression and unchanged Phase 3 acceptance runs `34910118880` and `34910118886` both succeeded.

Consequences: Phase 5 is formally PASS. Checkpoint `fmp-v1-phase5-features` is to be created at the verified merged acceptance-closure commit after post-merge source-free regression checks succeed. Phase 6 remains UNSTARTED and unauthorized until a separate approved design/implementation decision. The final untouched 2024-01-01 through 2026-08-20 test period remains locked; broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase5-acceptance-evidence.md`.

## DEC-031 — Phase 6 statistical / ML filter protocol

**Date:** 2026-09-15
**Status:** APPROVED

Phase 6 begins under the user-approved written design in `docs/superpowers/specs/2026-09-15-phase6-statistical-ml-filter-design.md`. The design is authoritative for `EXP-20260915-007` unless a later explicitly approved decision creates a new experiment or supersedes a named rule.

Frozen experiment scope:

- The only rule baselines are the unchanged Phase 4 serious candidates: USDJPY 15m session breakout with 5-pip buffer and 1.5x target range, and USDJPY 1h volatility breakout with 2.0x range expansion and fixed 1.0R target.
- Phase 5 feature identity remains `fmp-feature-v1` at checkpoint `fmp-v1-phase5-features` / `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`; accepted USDJPY processed-manifest SHA-256 remains `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Fit: 2015-01-01 through 2018-12-31 inclusive.
- Selection: 2019-01-01 through 2020-12-31 inclusive.
- Validation: 2021-01-01 through 2023-12-31 inclusive.
- The final untouched test remains 2024-01-01 through 2026-08-20 inclusive and normal Phase 6 APIs must fail before opening any required 2024+ source or feature partition.
- Model rows use exactly the 48 frozen Phase 5 feature values plus signal direction and must join at the exact strategy observation / `available_at_utc` identity. No future observation, target outcome, realized PnL, or validation statistic may be an input.
- The primary label is `target_before_stop`, resolved from future historical BID/ASK only after the feature row is frozen. Accepted Phase 3 stop/target/time-exit ordering remains authoritative, including conservative same-bar ambiguity.
- Training-only preprocessing is median imputation for both models and standard scaling for logistic regression only. Preprocessing parameters are fit on the fit period and frozen afterward; all-null fit columns fail closed.
- The modeling dependency is exactly `scikit-learn==1.9.1`. The only model families are the predeclared L2 logistic regression and shallow histogram gradient boosting configurations in the approved design, with global seed `20260915`.
- Score cutoffs are derived from fit scores only at retained fractions exactly 0.75, 0.50, and 0.25. Selection or validation scores may not alter a cutoff.
- Selection evaluates exactly six filtered variants per strategy on 2019-2020 at 0.2-pip adverse slippage and may freeze at most one challenger using the approved financial gate and deterministic tie-break. Validation cannot rescue a strategy with no qualifying selection-period challenger.
- There is no refit after selection. Any selected challenger is evaluated on 2021-2023 using the exact 2015-2018-fitted preprocessing, estimator, and cutoff. The 0.2-pip validation gate and 0.5-pip robustness gate are mandatory; 1.0 pip is diagnostic only.
- Financial comparison always uses the unchanged Phase 3 BID/ASK backtester, 0.25% requested risk, 0.50% hard per-trade maximum, 1.00% simultaneous risk maximum, 1.50% UTC day-start realized-loss halt, zero commission, and zero financing.
- Phase 6 may PASS whether an ML filter is promoted or all ML challengers are rejected, provided both frozen strategies complete the predeclared deterministic leakage-safe experiment. Failed variants remain evidence.
- No strategy-parameter retuning, new feature family, target-aware feature selection, pooled/cross-pair/cross-timeframe model, probability-based sizing, AutoML, neural network, post-result threshold widening, broker/live/demo path, or real-money trading is authorized under this experiment.

Consequences: Phase 6 is ACTIVE only for test-first implementation and execution of `EXP-20260915-007`. Phase 5 remains frozen PASS at `fmp-v1-phase5-features`; Phase 7 remains unstarted; the 2024-01-01 through 2026-08-20 final-test period remains locked; broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged.

## DEC-032 — Phase 6 statistical / ML filter experiment outcome and acceptance review

**Date:** 2026-09-15
**Status:** APPROVED

Authoritative `phase6-ml-filter` run `34966406652` on exact merged-main SHA `2dccb0f00d2a443bc41646ac1b3b494d81e1f13c` completed SUCCESS for both frozen `EXP-20260915-007` strategy cells. Each cell used the accepted Phase 2 USDJPY processed identity and Phase 5 `fmp-feature-v1` checkpoint, executed twice with byte-identical evidence, passed the pre-2024 evidence lock, and uploaded an independently audited artifact. Final-test touched: NO.

For USDJPY 15m `session_breakout`, `minutes_since_new_york_open` is all-null across the 428 fit-period model rows. The DEC-031 preprocessing rule therefore fails closed with `ALL_NULL_FIT_COLUMN` for both frozen model families instead of inventing a fill value. Both models record zero fits, all six model/retention variants remain durable `NOT_EVALUATED_MODEL_FIT_FAILED` evidence, `selected_variant = NO_ML_CHALLENGER`, and validation is not opened.

For USDJPY 1h `volatility_breakout`, both frozen models fit exactly once on 374 fit rows with fit-only preprocessing and cutoffs and no refit. All six predeclared selection variants fail the frozen all-conditions financial gate on 2019-2020. In particular, `net_return_beats_baseline` is false for every variant. No variant qualifies for the deterministic tie-break, so `selected_variant = NO_ML_CHALLENGER` and validation is not opened.

No strategy parameter, feature definition, model family, hyperparameter, retained fraction, cutoff rule, selection gate, validation gate, risk rule, or execution semantic was changed in response to the results. The failed first orchestration run is debugging history only and its successful volatility output was not used for selection decisions. Both authoritative outcomes preserve negative evidence and reject the optional ML overlay while retaining the two frozen Phase 4 rule baselines unchanged.

Consequences: `EXP-20260915-007` is complete with experiment status PASS and ML conclusion REJECT. Phase 6 is formally PASS. Checkpoint `fmp-v1-phase6-models` is to be created only at the verified acceptance-closure merge commit after fresh source-free merged-main tests and Phase 3 acceptance succeed. Phase 7 remains UNSTARTED. The untouched 2024-01-01 through 2026-08-20 final-test period remains locked; broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase6-ml-filter-evidence.md`.

## DEC-033 — Phase 7 walk-forward evaluation protocol

**Date:** 2026-09-15
**Status:** APPROVED

Phase 7 begins under the user-approved design in `docs/superpowers/specs/2026-09-15-phase7-walk-forward-design.md`. That design is authoritative for `EXP-20260915-008` unless a later explicitly approved decision supersedes a named rule.

Frozen protocol:

- The only candidates are the unchanged Phase 4 rule baselines retained by Phase 6: USDJPY 15m session breakout with 5-pip buffer and 1.5x target range, and USDJPY 1h volatility breakout with 2.0x range expansion and fixed 1.0R target.
- No ML overlay, feature selection, estimator, threshold, strategy retuning, neighboring-parameter rescue, candidate replacement, pair expansion, or timeframe expansion is authorized.
- Immutable upstream identities are Phase 6 checkpoint `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`; Phase 2 USDJPY artifact `10327600628` with ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`; and USDJPY processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Stage 1 scores exactly `2024-01-01 <= T < 2025-01-01`. At most seven immediately preceding calendar days may be opened as context, no earlier than `2023-12-25T00:00:00Z`; warm-up context can never become a scored decision, trade, PnL, or metric observation. Stage 1 starts at exactly $100,000.
- Slippage scenarios are exactly 0.2, 0.5, and 1.0 pips adverse per fill. The 0.2- and 0.5-pip scenarios are gating; 1.0 pip is diagnostic only. Historical BID/ASK spread remains authoritative and commission/financing remain zero.
- A candidate passes Stage 1 only if, at both 0.2 and 0.5 pips, net return and expectancy are strictly positive, profit factor is greater than 1.0, and maximum drawdown is at most 5%. The 0.2-pip baseline must additionally contain at least 40 completed trades.
- Stage 2 is authorized only for Stage 1 survivors and uses exactly seven non-overlapping forward windows: 2025-Q1, 2025-Q2, 2025-Q3, 2025-Q4, 2026-Q1, 2026-Q2, and the partial 2026-Q3 ending exclusively at `2026-08-21`.
- Every Stage 2 window starts independently at exactly $100,000 and records `refit_status = NOT_APPLICABLE_FIXED_RULE`. Up to seven immediately preceding calendar days may be used as context only; no context row is rescored in the new window.
- Stage 2 aggregate at 0.2 pips requires positive net return, positive expectancy, profit factor greater than 1.0, at least 100 completed trades, and maximum independent-window drawdown at most 5%. Aggregate 0.5-pip results require positive net return, positive expectancy, profit factor greater than 1.0, and maximum independent-window drawdown at most 5%.
- Stage 2 stability at 0.2 pips requires at least four of seven windows to have positive net PnL, and no single positive window may contribute more than 50% of total positive-window PnL.
- Aggregate maximum drawdown is the maximum of the seven independent window drawdowns; Phase 7 must not fabricate a chained-equity drawdown across independently reset windows.
- Existing Phase 4, Phase 5, and Phase 6 APIs retain their hard 2024+ fail-before-I/O guards. Phase 7 must use a dedicated promotion-only path with exact enumerated ranges and no generic `allow_final`, arbitrary dates, arbitrary strategy, or arbitrary parameter surface.
- Stage 2 must fail before required 2025/2026 source I/O unless the exact candidate/data/experiment identity has a verified Stage 1 PASS artifact.
- Evidence must be deterministic and bind code, upstream data/checkpoint identities, candidate parameters, scored/warm-up ranges, opened partitions, cost/risk identity, per-window metrics, aggregate metrics, gates, and final decision. Runtime clocks, hostnames, UUIDs, temporary paths, and nondeterministic ordering are forbidden from evidence bytes.

This protocol decision does not itself inspect final-test data. The first required 2024 partition may be opened only after the guarded Phase 7 implementation is merged and verified and the dedicated Stage 1 workflow is deliberately dispatched. Required 2025/2026 partitions remain locked behind Stage 1 PASS authorization.

Consequences: Phase 6 remains frozen PASS at `fmp-v1-phase6-models`; Phase 7 is ACTIVE only for test-first implementation of `EXP-20260915-008`, which is PLANNED with `Final-test touched: NO`. Phase 8 remains UNSTARTED. Broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged.

## DEC-034 — Phase 7 Stage 1 final-gate outcome

**Date:** 2026-09-15
**Status:** APPROVED

Authoritative manual `phase7-final-gate` run `35013047267` executed on the exact verified merged-main Phase 7 implementation SHA `e33270de1f89757d1bf2a0d12ef40b2dc36bc110` and completed `SUCCESS` for both frozen candidate cells. Before dispatch, tests run `35010868101` completed successfully with 620/620 tests, workflow YAML validation, and compile passing, and unchanged Phase 3 acceptance run `35010868091` completed successfully. Each Stage 1 cell executed twice and passed a complete byte-for-byte evidence comparison before upload.

The Stage 1 run used only the accepted Phase 2 USDJPY artifact `10327600628` / ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`, processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`, canonical schema `fmp-canonical-1m-v1`, and Phase 6 checkpoint `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`. Scoring was exactly `[2024-01-01, 2025-01-01)` with only the immediately preceding seven calendar days available as non-scored warm-up context. Final-test touched: YES — Stage 1 2024 only. No required 2025/2026 Stage 2 partition was opened.

For USDJPY 15m `session_breakout`, the authoritative artifact is `10414407590`, ZIP SHA-256 `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb`, with inner `manifest.json` SHA-256 `a8ca80186708aedbfd52fd688c843c4dc06e2ce8a81f543bd7224abc0a955faa`. At 0.2-pip slippage it completed 122 trades, returned +1.383287%, produced +$11.3384 expectancy/trade and PF 1.166401, with 1.181400% max drawdown. At 0.5 pips it returned +1.102509%, produced +$9.0370 expectancy/trade and PF 1.130773, with 1.305490% max drawdown. Every mandatory Stage 1 gate is true; the 1.0-pip diagnostic also remains positive. The audited outcome is `STAGE1_PASS`.

For USDJPY 1h `volatility_breakout`, the authoritative artifact is `10414905151`, ZIP SHA-256 `5ee8b6b96382741f454d2b72a6ae6de04e85c9eca04c17ac846c0d594fd27d24`, with inner `manifest.json` SHA-256 `a2526d90312e85a2ab2d57ab86d5502e8644a16735aa0a677cda5626976dda35`. At 0.2 pips it completed 103 trades but returned -2.603768%, produced -$25.2793 expectancy/trade and PF 0.720003, with 3.102796% max drawdown. At 0.5 pips it returned -3.051558%, produced -$29.6268 expectancy/trade and PF 0.680125, with 3.484070% max drawdown. It therefore fails the mandatory profitability, expectancy, and profit-factor gates while passing the sample-size and drawdown bounds. The audited outcome is `STAGE1_REJECT`.

Stage 2 is authorized only for `session_breakout`. Authorization is bound to candidate `session_breakout`, Stage 1 artifact `10414407590`, ZIP SHA-256 `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb`, code SHA `e33270de1f89757d1bf2a0d12ef40b2dc36bc110`, and the exact upstream identities above. The manual Stage 2 workflow must verify this package before opening any required 2025/2026 source partition. `volatility_breakout` is rejected for Stage 2 under `EXP-20260915-008`; no retuning, parameter substitution, rescue search, alternative candidate, or post-result threshold change is authorized.

Consequences: `EXP-20260915-008` remains RUNNING and Phase 7 remains ACTIVE for the frozen seven-window Stage 2 evaluation of the sole survivor. Phase 8 remains UNSTARTED. Broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged. Detailed audited evidence is in `docs/phase7-stage1-evidence.md`.

## DEC-035 — Phase 7 walk-forward outcome and acceptance review

**Date:** 2026-09-15
**Status:** APPROVED

Authoritative manual `phase7-walk-forward` run `35015277625` executed on exact merged-main SHA `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d` for the sole Stage 1 survivor, USDJPY 15m `session_breakout` with the unchanged 5-pip buffer and 1.5x target-range multiple. Before any required 2025/2026 source I/O, the workflow downloaded and verified Stage 1 PASS artifact `10414407590`, ZIP SHA-256 `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb`, then re-verified the accepted Phase 2 USDJPY artifact `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`, processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`, and Phase 6 checkpoint `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`.

The Stage 2 workflow executed the complete seven-window evaluation twice, compared the complete file sets and every evidence byte, independently reconstructed all seven frozen scored/warm-up ranges and exact partition keys, and recomputed the aggregate gate from all 21 window rows before upload. The authoritative artifact is `10414817824`, ZIP SHA-256 `2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4`; constituent `result.json` SHA-256 is `ce7ef3f732bf2da7cd9c0df5e5d695dcdadd63e309c9428a6f572801fcb197b7` and `windows.json` SHA-256 is `66a1d35b12b68a0762dd98cd6838a2befcaf57ef9ae43bce181241fe4d23a4f0`.

At the mandatory 0.2-pip cost, the seven independent windows aggregate to +0.757266% net return, +$3.8054 expectancy/trade, PF 1.062731, 199 completed trades, and 1.140640% maximum independent-window drawdown. Five of seven windows have positive net PnL and the largest positive window contributes 35.061843% of total positive-window PnL, satisfying both stability gates. At the mandatory 0.5-pip cost, aggregate net return is +0.262176%, expectancy is +$1.3175/trade, PF is 1.021310, and maximum independent-window drawdown is 1.170046%. Every frozen mandatory Stage 2 criterion is true.

The 1.0-pip diagnostic is negative: -0.562118% aggregate net return, -$2.8247 expectancy/trade, PF 0.955760, and 1.219045% maximum independent-window drawdown. This cost-sensitivity result is preserved as evidence and cannot be ignored, but DEC-033 explicitly defines the 1.0-pip scenario as diagnostic rather than gating. It therefore does not reverse a pass at both mandatory costs and was not used to retune the rule or alter any threshold after observation.

No strategy parameter, pair, timeframe, model, feature, risk setting, cost rule, forward boundary, warm-up rule, gate, or execution semantic changed after either Stage 1 or Stage 2 observation. `volatility_breakout` remains rejected from Stage 1 and was not opened in Stage 2. The audited final result is `PHASE7_PROMOTE_TO_SHADOW_DESIGN`.

Consequences: `EXP-20260915-008` is PASS / PROMOTE and Phase 7 is formally PASS. The unchanged USDJPY 15m `session_breakout` rule is eligible for Phase 8 shadow design only. Phase 8 remains UNSTARTED; no shadow implementation, broker integration, demo trading, live trading, order placement, or real-money trading is authorized by this decision. Checkpoint `fmp-v1-phase7-walk-forward` is to be created only at the verified merged acceptance-closure commit after fresh source-free merged-main tests and unchanged Phase 3 acceptance succeed. DEC-008 remains unchanged. Detailed evidence is in `docs/phase7-walk-forward-evidence.md`.


## DEC-036 — Phase 8 live shadow protocol

**Date:** 2026-09-15
**Status:** APPROVED

The approved `docs/superpowers/specs/2026-09-15-phase8-shadow-design.md` protocol is activated after checkpoint `fmp-v1-phase7-walk-forward` was verified to resolve exactly to Phase 7 acceptance-closure commit `b6fb0176555b071fef6d1070edf3407b03cd60c9`. The implementation plan `docs/superpowers/plans/2026-09-15-phase8-live-shadow.md` is also approved as the execution sequence.

Phase 8 admits only the unchanged USDJPY 15m `session_breakout` survivor with 5-pip buffer, 1.5x target-range multiple, existing London-session/DST semantics, exact 16:00 `Europe/London` flat rule, no ML overlay, and unchanged Phase 3 risk semantics. No parameter search, alternate pair/timeframe, or rescue candidate is authorized.

The selected initial live quote role is the OANDA v20 fxTrade Practice pricing stream only: fixed `GET` to `https://stream-fxpractice.oanda.com/v3/accounts/{account_id}/pricing/stream` for provider instrument `USD_JPY`, with `snapshot=true` and `includeHomeConversions=false`. Runtime architecture must make order/trade/position mutation structurally unavailable; production hosts, generic broker request surfaces, REST candle backfill, MT5 execution integration, demo orders, live orders, and real-money trading remain outside Phase 8. Credentials may exist only in memory/local secret input and durable evidence may contain only a one-way account fingerprint, never a token or plain account ID.

`EXP-20260915-009` is the frozen Phase 8 live-shadow experiment. Cost scenarios remain exactly 0.2/0.5/1.0 pips adverse per fill, with 0.2 and 0.5 gating and 1.0 diagnostic; each virtual scenario starts at $100,000 and carries independently through the registered campaign. Stale timeout is 15 seconds and entry/scheduled-exit quote deadlines are 5 seconds. Acceptance requires the exact operational, timing, spread-parity, financial, sample-size, coverage, evidence-integrity, and deterministic-replay gates frozen in the design; implementation completion alone is not Phase 8 PASS.

Consequences: Phase 8 becomes ACTIVE for shadow-only implementation, connector qualification, and later explicitly operator-started live evidence collection. Phase 9 remains locked. No practice/demo order placement, production/live order placement, broker mutation, or real-money path is authorized. `DEC-008` remains unchanged.

## DEC-037 — Phase 8 MT5 demo quote bridge amendment

**Date:** 2026-09-17
**Status:** APPROVED

The approved `docs/superpowers/specs/2026-09-17-phase8-mt5-bridge-amendment.md` supersedes DEC-036 only for the Phase 8 live quote-source connector. OANDA Practice qualification did not occur because the required account is unavailable to the operator's jurisdiction. The unchanged USDJPY 15m `session_breakout` strategy, 5-pip buffer, 1.5x target-range multiple, London-session/DST semantics, exact 16:00 `Europe/London` flat rule, three virtual slippage scenarios, campaign minima, acceptance thresholds, deterministic replay requirements, and exact review outcomes remain frozen.

The selected connector is `FP_MARKETS_MT5_DEMO` through the read-only `FMPPhase8QuoteBridge` MQL5 Expert Advisor attached only to `USDJPY`. The bridge may run only on demo account mode and only on `FPMarketsSC-Demo` or `FPMarketsSC-Demo2`, writes the fixed `FILE_COMMON` transport `FMP/phase8-usdjpy-feed.jsonl`, and exposes no order/trade/position mutation surface. Direct Python `MetaTrader5` integration, MT5 live servers, generic broker fallback, demo order placement, production/live order placement, broker mutation, and real-money trading remain forbidden.

`EXP-20260915-009` is stopped before qualification and produced no scored campaign evidence. `EXP-20260917-010` is the active Phase 8 MT5 demo live-shadow experiment. Successful connector qualification authorizes only historical-reference generation and campaign registration; it is not Phase 8 PASS. Phase 9 remains locked. `DEC-008` remains unchanged.


## DEC-038 — Phase 8 bridge/market liveness separation amendment

**Date:** 2026-09-22
**Status:** APPROVED

Prospective FP Markets MT5 demo evidence under `EXP-20260917-010` exposed a Phase 8 liveness-design defect rather than a strategy result. The local MT5/EA/file bridge continued to emit valid heartbeats while USDJPY sometimes produced no new tick for more than the original 15-second market-feed timeout. A diagnostic analysis of 46,721 normalized quotes found 102 quote-to-quote gaps above 15 seconds, 23 above 30 seconds, and 3 above 60 seconds, with a maximum gap of 4,301.580 seconds. During the long approximately 10:18–11:30 UTC no-tick interval on 2026-09-21, 870 valid bridge heartbeats were still received.

The approved `docs/superpowers/specs/2026-09-22-phase8-liveness-amendment.md` therefore supersedes DEC-036/DEC-037 only for live-capture interpretation of the 15-second liveness threshold. Bridge silence of 15 seconds remains a true `stale` continuity failure: the London date becomes ineligible, open simulated trade paths become unknown, affected bar time is stale, and no backfill is permitted. By contrast, a 15-second no-tick period while valid bridge records continue is recorded as `market_quiet` and does not by itself invalidate the whole London date.

Fail-closed market-path protections remain unchanged in substance. If a simulated position is open when `market_quiet` crosses the threshold, its outcome becomes `OUTCOME_UNKNOWN_AFTER_GAP` and is not financially scored. Required 1m/15m context must still be constructed from actually observed quotes; missing required context retains the existing incomplete-session/date-ineligible behavior. Entry and scheduled-exit quotes still have the frozen 5-second deadline. No tick, bar, stop/target path, or execution quote may be reconstructed or backfilled. Bounded connector qualification keeps its existing conservative market-liveness requirement.

`EXP-20260917-010` is stopped as INCONCLUSIVE / DIAGNOSTIC under the superseded live-runner semantics. Its local evidence must be preserved and must not count toward the amended campaign. `EXP-20260922-011` is the new Phase 8 experiment identity. It requires fresh merged-code verification, connector qualification, historical-reference generation, and campaign registration before scored observation. The evidence protocol remains `fmp-phase8-shadow-evidence-v2`; exact campaign and segment code-commit binding prevents old/new semantics from being mixed.

Consequences: Phase 8 remains ACTIVE and all original strategy, risk, cost, campaign-minimum, financial, spread, timing, replay, and structural no-order gates remain frozen except for the liveness interpretation explicitly amended above. Phase 9 remains locked. Demo order placement, production/live order placement, broker mutation, and real-money trading remain forbidden. DEC-008 remains unchanged.


## DEC-039 — Phase 8 portfolio-research pivot to multi-pair, multi-strategy architecture

**Date:** 2026-09-22
**Status:** APPROVED

The operator has revised the economic objective after reviewing the Phase 7 promoted strategy's actual forward performance. The sole promoted USDJPY 15m session-breakout strategy remains a valid Phase 7 result, but its Stage 2 aggregate return (+0.757266% at 0.2-pip adverse slippage; +0.262176% at 0.5 pips) is not economically attractive enough to justify spending the next multi-week campaign evaluating that strategy alone.

Phase 8 is therefore amended into two ordered subphases under the approved design `docs/superpowers/specs/2026-09-22-phase8a-portfolio-research-redesign.md`:

- **Phase 8A — Multi-pair, multi-strategy portfolio research**
- **Phase 8B — Multi-strategy live shadow**

Frozen scope and consequences:

- V1 remains exactly EURUSD, GBPUSD, and USDJPY.
- All accepted Dukascopy Phase 1/2 histories remain canonical and must be reused for Phase 8A research.
- The formerly untouched 2024-01-01 through 2026-08-20 period was opened in Phase 7. New post-Phase-7 strategy versions may use that history for retrospective research/robustness, but may not call it an untouched final test. New genuine forward evidence begins only after each challenger version/protocol is frozen.
- FMP may maintain many versioned strategies across all three pairs. Strategy versions progress through explicit lifecycle states and cannot mutate in place.
- Continuous learning is permitted only as a research/challenger process. An active champion set is immutable during a registered campaign. No learning process may hot-swap a strategy into shadow/demo/live execution or authorize broker orders.
- Portfolio routing may evaluate multiple eligible strategy versions, but portfolio exposure/conflict checks and the independent risk engine remain authoritative. Correlated/overlapping USD exposure must be measured.
- The operator's aspiration for very high returns, including possible +10% days, is recorded as a research objective to measure, not a guaranteed or mandatory daily pass criterion. Phase 8A must report daily-return distributions, monthly/annualized return, drawdown, tail concentration, cost sensitivity, and contribution by pair/strategy/regime at fixed explicit risk.
- Return improvement must come from stronger/diversified validated edges and capital utilization, not martingale, loss chasing, or silent leverage multiplication.
- Existing baseline strategy families and all prior PASS/FAIL evidence remain preserved. New parameter regions, strategy families, regime-conditioned variants, or portfolio combinations require new predeclared experiment records rather than retroactive edits to old experiments.

`EXP-20260922-011` is stopped before campaign registration. Its fresh connector qualification PASS and historical reference build are preserved as non-scored operational evidence. The reference SHA-256 is `e920b3254235d2bb0766762551b5eb9d21439d429c59aebd14c3e4bb16e8cc64`, bound to code commit `5cb884dfb15d7798b023658e025221a38dfec9fc`. No EXP-011 live-shadow segment is authorized to start.

Consequences: Phase 8A becomes ACTIVE under new experiment `EXP-20260922-012`. Phase 8B, Phase 9 demo trading, broker mutation, live-order placement, and real-money trading remain LOCKED. The first Phase 8A implementation task is the deterministic versioned strategy registry plus champion/challenger promotion lock. Existing Phase 8 shadow tooling is preserved but not launched as EXP-011.


## DEC-040 — Phase 8A joint portfolio simulation protocol

**Date:** 2026-09-22
**Status:** APPROVED

The approved `docs/superpowers/specs/2026-09-22-phase8a-joint-portfolio-simulation.md` defines the next Phase 8A research layer after the versioned registry/router foundation and retrospective batch runner.

The purpose is to evaluate explicitly supplied frozen strategy sets under one shared virtual account rather than summing independent strategy backtests. Strategy signals continue to use their exact 5m/15m/1h family contracts, while entries, stops, targets, time exits, PnL, and portfolio risk are evaluated on accepted canonical 1m BID/ASK bars after each signal becomes known.

Frozen joint-simulation rules:

- each 0.2/0.5/1.0-pip slippage scenario starts one shared $100,000 account;
- all strategies and all three V1 pairs share the unchanged Phase 3 risk state;
- requested risk remains 0.25%, hard per-trade max 0.50%, simultaneous open-risk max 1.00%, UTC day-start realized-loss halt 1.50%;
- no strategy receives a private risk budget that bypasses the shared account;
- same-symbol opposite-direction candidates conflict only when they have the same exact signal-known timestamp;
- same-symbol opposite directions at different timestamps are not automatically rejected;
- strategy-version signal timeframes remain limited to 5m/15m/1h, while 1m is an execution-data role only;
- missing required 1m execution bars fail closed; no interpolation, synthetic fill, or pre-known execution is permitted;
- evidence binds exact strategy fingerprints, pair manifests, range, runner commit, costs, risk identity, candidate ordering, and retrospective label;
- all already-opened historical results remain `RETROSPECTIVE_ALREADY_SEEN` with `untouched_oos = false`;
- joint portfolio results may report performance and interaction diagnostics but cannot select/promote a portfolio automatically.

DEC-040 intentionally does not define a combination-search or portfolio-selection algorithm. A later predeclared selection protocol is required before joint historical results can choose a Phase 8B shadow-candidate portfolio. Retired strategies remain retired unless a separate new challenger experiment creates a genuinely new immutable strategy version.

Consequences: Phase 8A remains ACTIVE under `EXP-20260922-012`. The next implementation milestone is time-local conflict routing, canonical 1m execution loading, deterministic candidate assembly, and shared-account joint backtesting. Phase 8B, Phase 9, broker mutation, demo orders, live orders, and real-money trading remain LOCKED.


## DEC-041 — Phase 8A opening-range momentum challenger round 1

**Date:** 2026-09-22
**Status:** APPROVED / PREDECLARED BEFORE BENCHMARK RESULTS

The approved `docs/superpowers/specs/2026-09-22-phase8a-challenger-round1-opening-range-momentum.md` opens `EXP-20260922-013` as the first genuinely new post-Phase-7 challenger family.

The frozen family is `opening_range_momentum` / `fmp-opening-range-momentum-v1` across EURUSD, GBPUSD, and USDJPY on 5m, 15m, and 1h signal bars. It uses a 06:00–08:00 `Europe/London` midpoint reference range, an 08:00–12:00 signal window, exact 16:00 London flat, fixed 2-pip breakout buffer, body-direction confirmation, and a body-to-candle-range threshold. Stop geometry is fixed at 0.25 reference-range depth inside the breached boundary and targets are fixed R-multiples from the signal close.

The only searched parameters are:

- body fraction threshold: 0.50 or 0.70;
- target R multiple: 1.0 or 1.5.

This is exactly 4 configurations per pair/timeframe and 36 pair/timeframe/configuration identities total. Every configuration is evaluated at 0.2, 0.5, and 1.0 pips adverse slippage. No additional parameter, pair, timeframe, session window, stop depth, buffer, or target may be introduced under EXP-013 after benchmark results are inspected.

Chronology is frozen:

- Stage A development: 2015-01-01 through 2020-12-31;
- Stage A validation: 2021-01-01 through 2023-12-31;
- Stage B retrospective chronological confirmation: 2024-01-01 through 2026-08-20, only for exact Stage A survivors.

All three ranges are labeled retrospective for this post-Phase-7 family. The Stage B range was already opened upstream and may not be called untouched OOS or prospective.

Stage A requires positive net return, expectancy, and PF>1.0 at both 0.2 and 0.5 pips on development and validation, max drawdown <=5% on all mandatory cells, at least 100 development and 50 validation trades at 0.2 pips, plus a same-pair/timeframe neighboring configuration that also passes the mandatory profitability/drawdown gates. An isolated single-point winner is rejected. The 1.0-pip scenario is diagnostic.

Stage B requires positive net return, expectancy, PF>1.0, and max drawdown <=5% at both 0.2 and 0.5 pips plus at least 75 completed 0.2-pip trades. A Stage B pass authorizes only `HISTORICAL_QUALIFIED` status for the immutable challenger. It does not authorize shadow validation, demo, live orders, or champion-set mutation.

Consequences: `EXP-20260922-013` is ACTIVE for test-first implementation only. Phase 8A remains active; Phase 8B and all broker-order paths remain locked. No benchmark result has been inspected at the time of this decision.


## DEC-042 — Phase 8A portfolio selection protocol

**Date:** 2026-09-22
**Status:** APPROVED

The approved `docs/superpowers/specs/2026-09-22-phase8a-portfolio-selection.md` freezes the Phase 8A portfolio-selection rules before any strategy-combination search is run.

DEC-042 may combine only immutable strategy versions already qualified by their own evidence. `DISCOVERY`, `CHALLENGER`, and `RETIRED` records are ineligible. The pool must contain between 2 and 12 eligible strategies; larger pools fail closed and require a separately predeclared reduction protocol. Every unique unordered set of 1 through 6 strategies is evaluated, with 1-strategy sets retained only as controls.

Every set uses the DEC-040 shared-account simulator over exactly `2019-01-01` inclusive through `2026-08-21` exclusive, with exact 0.2/0.5/1.0-pip adverse-slippage scenarios and unchanged Phase 3 risk. Mandatory selection gates at both 0.2 and 0.5 pips require positive net return and expectancy, profit factor above 1.0, maximum drawdown at or below 5%, and at least 200 completed trades. Additional 0.2-pip stability/concentration gates require at least 5 of 8 positive calendar-year windows, no positive year above 45% of total positive-year PnL, no strategy above 60% of total positive trade PnL, no pair above 70%, and completed-trade representation from at least two strategy families and two V1 pairs. The 1.0-pip scenario remains diagnostic. Frequency of >=10% days is reported but is not a pass gate.

Passing sets are ranked lexicographically by: higher 0.5-pip annualized compounded return, lower 0.5-pip drawdown, higher 0.5-pip profit factor, higher 0.2-pip annualized compounded return, lower strategy concentration, lower pair concentration, fewer strategies, then sorted fingerprint tuple. No post-result weight or threshold changes are allowed.

All DEC-042 evidence remains `RETROSPECTIVE_ALREADY_SEEN`, `untouched_oos = false`, and `promotion_authorized = false`. A selection PASS can identify only a future shadow candidate for separate acceptance/prospective testing; it cannot authorize demo/live execution.

The current frozen historical inventory contains only one `HISTORICAL_QUALIFIED` strategy, the Phase 7 USDJPY 15m session-breakout survivor. Therefore DEC-042 cannot yet execute a meaningful multi-strategy search. At least one additional immutable challenger must first pass a separately predeclared discovery/qualification experiment.

Consequences: Phase 8A remains ACTIVE. `EXP-20260922-014` is opened for implementation of the frozen selection machinery only; combination evaluation remains blocked until the qualified pool contains at least two strategies. Phase 8B, Phase 9, broker mutation, demo orders, live orders, and real-money trading remain LOCKED.



Identity correction: this section was initially committed with duplicate identifiers already assigned to the earlier `opening_range_momentum` decision/experiment. It was renumbered before any portfolio combination search or ranking result was produced.

## DEC-043 — Phase 8A rule-based challenger discovery and qualification

**Date:** 2026-09-22
**Status:** APPROVED

The approved `docs/superpowers/specs/2026-09-22-phase8a-challenger-discovery.md` opens a new bounded rule-based challenger experiment because DEC-042 is correctly blocked by the current pool of only one qualified strategy.

`EXP-20260922-015` searches only new, predeclared parameter regions for the six existing deterministic rule families across EURUSD, GBPUSD, USDJPY and 5m/15m/1h. The frozen search contains exactly 567 new immutable configurations. These parameter points do not overlap the original Phase 4 grid.

The chronological retrospective protocol is:

- Stage A discovery: 2015-01-01 through 2018-12-31 inclusive; all 567 candidates; strict 0.2/0.5 profitability, expectancy, PF > 1.05, max-DD <= 5%, and >=40-trade gates; at most 2 survivors per exact pair/family/timeframe cell.
- Stage B qualification: 2019-01-01 through 2022-12-31 inclusive; only Stage A survivors; same gating plus at least 3 of 4 positive calendar years at 0.2 pips.
- Stage C robustness: 2023-01-01 through 2026-08-20 inclusive; only Stage B passers; same profitability/PF/DD gates, >=30 trades, and at least 3 of the four 2023/2024/2025/2026-partial windows positive at 0.2 pips.

No downstream stage may open a candidate absent from the exact upstream survivor manifest. No parameter retuning, same-cell rescue, replacement, or threshold relaxation is allowed after observation.

Final shortlist ranking and diversity caps are frozen before Stage A results. At most 11 new challengers can become `HISTORICAL_QUALIFIED`, with no more than 4 per pair, 3 per family, and 2 per exact pair/family/timeframe cell. All other EXP-015 candidates are recorded as `RETIRED` with explicit reason. Adding the existing Phase 7 baseline later therefore keeps DEC-042's eligible pool at or below 12.

All evidence is `RETROSPECTIVE_ALREADY_SEEN` with `untouched_oos = false`. The 0.2 and 0.5-pip scenarios gate; 1.0 pip remains diagnostic. The full 567-candidate search count is preserved as multiple-comparison evidence.

Consequences: `EXP-20260922-015` becomes ACTIVE for implementation only. Stage A may not run until the new parameter validators, immutable challenger-grid generator, stage gates, authorization manifests, deterministic evidence, tests, and source-free verification are merged. DEC-042 combination search remains blocked until EXP-015 produces at least one additional qualified challenger. Phase 8B, Phase 9, broker mutation, demo/live orders, and real-money trading remain LOCKED.

Identity correction: this section was initially drafted as `DEC-042` / `EXP-20260922-014` while the selection-protocol duplicate was being reconciled. It was renumbered before any Stage A historical run or benchmark result.


## DEC-044 — EXP-015 Stage A survivor-cap arithmetic correction

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY HISTORICAL STAGE

An arithmetic inconsistency was found in DEC-043 before any EXP-015 historical data was opened. DEC-043 already freezes 3 symbols × 6 families × 3 timeframes = 54 exact `(symbol, family, timeframe)` cells and allows at most 2 Stage A survivors per exact cell. The written statement “Maximum Stage A survivors: 54” was therefore inconsistent with the specific per-cell rule.

DEC-044 preserves the specific at-most-2-per-cell rule and corrects the maximum Stage A survivor count to 108. No parameter value, strategy family, pair, timeframe, date range, cost scenario, risk assumption, gate, ranking key, downstream authorization rule, or final-shortlist cap changes.

No EXP-015 Stage A/B/C historical run, benchmark, survivor manifest, or shortlist existed when this correction was approved. The correction is protocol maintenance, not post-result tuning.

Consequences: EXP-015 remains ACTIVE — IMPLEMENTATION / NO HISTORICAL STAGE RUN YET. Stage A implementation must enforce 567 frozen inputs, 54 exact ranking cells, at most 2 survivors per cell, and an absolute maximum of 108 Stage A survivors.


## DEC-045 — Phase 8A acceptance review and shadow-candidate freeze

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY DEC-042 SELECTION RESULT

The approved `docs/superpowers/specs/2026-09-22-phase8a-acceptance-review.md` freezes the Phase 8A acceptance boundary required by DEC-039 step 9.

DEC-042 remains retrospective portfolio selection only and continues to emit `shadow_candidate_authorized = false`. DEC-045 independently consumes the exact DEC-042 preflight/selection artifacts and deterministically replays the stored set universe, gate results, and ranking before any lifecycle transition is allowed.

Before any DEC-042 result exists, DEC-045 operationally defines “materially improves the economic case” as: the exact DEC-042 selected multi-strategy portfolio must pass every frozen DEC-042 gate and its 0.5-pip annualized compounded return must be strictly greater than the Phase 7 baseline control evaluated over the same 2019-01-01 through 2026-08-21 range. No additional percentage-point hurdle, score weight, leverage change, or post-result margin may be introduced later.

If that rule passes, only the exact selected strategy records advance one lifecycle step from `HISTORICAL_QUALIFIED` to `SHADOW_CANDIDATE`, an immutable champion/shadow-candidate set is frozen, and `phase8b_design_authorized = true`. If DEC-042 has no selected portfolio or the strict baseline-improvement gate fails, the outcome is `PHASE8A_RESEARCH_REJECTED` and no lifecycle transition occurs.

Even an accepted candidate does not authorize demo orders, live orders, broker mutation, real-money trading, or Phase 9. It authorizes only Phase 8B read-only shadow design/capture for the exact frozen candidate set.

Consequences: `EXP-20260922-016` is opened for source-free implementation of the acceptance compiler and manual evidence-review workflow. No DEC-042 selection result or Phase 8A acceptance result exists yet.


## DEC-046 — Phase 8B multi-strategy read-only shadow design

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B CAMPAIGN

The approved `docs/superpowers/specs/2026-09-22-phase8b-shadow-design.md` freezes the Phase 8B design boundary without modifying the legacy USDJPY-only Phase 8 evidence path.

Only an exact DEC-045 `PHASE8A_SHADOW_CANDIDATE_ACCEPTED` artifact may produce a Phase 8B design. The design supports only EURUSD, GBPUSD, and USDJPY and derives the required symbol/timeframe union directly from the immutable accepted champion set.

The intended connector topology is one read-only MT5 EA instance per required symbol chart, fixed FILE_COMMON paths per V1 symbol, demo account/server only, no arbitrary symbol/path override, and no broker-order surface. DEC-038 bridge/market liveness separation is retained independently per required symbol.

A frozen design does not authorize campaign registration or capture. Every required feed must later pass Phase 8B qualification with common demo account/server identity before a separately frozen registration protocol can proceed.

Consequences: `EXP-20260922-017` is opened for source-free design-manifest implementation only. Phase 8B campaign registration/start, Phase 9, demo/live orders, broker mutation, and real-money trading remain LOCKED.


## DEC-047 — Phase 8B multi-symbol MT5 bridge qualification and registration

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B CAMPAIGN

The approved `docs/superpowers/specs/2026-09-22-phase8b-bridge-qualification-registration.md` freezes the read-only connector qualification and immutable registration boundary for Phase 8B.

DEC-047 introduces a separate `fmp-mt5-demo-multisymbol-file-bridge-v1` protocol and one fixed FILE_COMMON feed per required V1 symbol while preserving the legacy EXP-011 USDJPY bridge unchanged. Per-symbol qualification retains the existing conservative 600-second / 100-price / 6-heartbeat / 15-second liveness / 5-second source-time thresholds. The multi-symbol summary may PASS only when every required feed passes and all feeds share the same approved demo account fingerprint/server with distinct bridge session IDs.

A PASS may authorize immutable campaign registration only. Registration binds the exact DEC-046 design, qualification evidence, champion set, required symbols/timeframes, bridge files, common demo identity, per-symbol bridge sessions, liveness/cost contract, code commit, and timestamp.

Campaign start remains unauthorized under DEC-047. Phase 8B capture requires a later separately frozen protocol. Demo/live orders, broker mutation, real-money trading, and Phase 9 remain LOCKED.

Consequences: `EXP-20260922-018` is opened for implementation of the multi-symbol bridge/qualification/registration layer only.


## DEC-048 — Phase 8B campaign start authorization

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT

The approved `docs/superpowers/specs/2026-09-22-phase8b-campaign-start-authorization.md` freezes the final boundary between DEC-047 registration and any future prospective capture.

DEC-048 requires one exact valid DEC-047 registration and exact revalidation of every currently visible required-symbol `BRIDGE_START` against the registered symbol, protocol, bridge-session ID, account fingerprint, and approved server. Every `Phase8BBridgeFileTail` begins at the current EOF, so pre-reader records cannot enter future prospective evidence.

A valid start artifact freezes the registration SHA-256/fingerprint, champion-set identity, exact strategy/symbol/timeframe sets, current registered bridge sessions, common demo account/server, UTC start time, first `Europe/London` date, liveness/quote/cost contract, and start-authorization code commit.

Only a fully valid artifact sets `campaign_start_authorized = true` and `prospective_capture_authorized = true`. Broker/demo/live/real-money/Phase-9 authorization remains false.

DEC-048 adds no capture/run/start loop. A later separately frozen protocol must consume the exact authorization and independently revalidate bridge identity before a live-shadow segment can start.

Consequences: `EXP-20260922-019` is opened for source-free implementation of the exactly-once campaign-start authorization layer. No Phase 8B live-shadow segment has started.


## DEC-049 — Phase 8B prospective capture foundation

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT

The approved `docs/superpowers/specs/2026-09-22-phase8b-prospective-capture-foundation.md` opens `EXP-20260922-020` as a source-free boundary between DEC-048 start authorization and any later prospective runtime.

DEC-049 requires exact byte-digest and semantic cross-validation of the DEC-047 registration and DEC-048 start authorization, then independently revalidates every current required-symbol bridge session through fresh `Phase8BBridgeFileTail` readers that begin at EOF. Any changed session, account, server, protocol, symbol coverage, fixed bridge path, champion/strategy identity, liveness contract, cost scenario, or authorization flag fails closed.

A valid preflight freezes protocol `fmp-phase8b-capture-preflight-v1`, exact upstream digests/fingerprints, campaign start boundary, champion set, strategy/symbol/timeframe sets, bridge identities, common demo account/server, fixed bridge paths, liveness/cost contract, code commit, UTC preflight timestamp, and `TAIL_AT_EOF_NO_BACKFILL` semantics. It may record only `capture_runtime_ready = true`; it does not start a live-shadow segment, satisfy acceptance, promote a strategy, or authorize any order path.

DEC-049 also freezes the deterministic raw-record envelope that a later runtime must use for post-preflight bridge records. It retains the existing bridge-session validator semantics for duplicate ticks, source-time monotonicity, symbol/session/account/server continuity, and normalized quotes.

No `capture`, `run`, `start`, `replay`, or `review` CLI command is added under DEC-049. A later separately approved runtime/replay/acceptance decision remains mandatory before any prospective segment can begin.

Consequences: Phase 8B remains LOCKED for live-shadow capture. Demo/live orders, broker mutation, real-money trading, Phase 9, active-champion mutation, and acceptance/promotion remain LOCKED.


## DEC-050 — Phase 8B multi-strategy runtime and deterministic replay kernel

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT

The approved `docs/superpowers/specs/2026-09-22-phase8b-runtime-replay-kernel.md` opens `EXP-20260922-021` for source-free implementation of the finite-sequence Phase 8B market-processing, multi-strategy routing, shared-account shadow simulation, segment-evidence, and deterministic replay kernel.

DEC-050 consumes only one exact valid DEC-049 capture preflight plus an ordered finite sequence of exact `fmp-phase8b-capture-record-v1` envelopes. It revalidates every record, preserves per-symbol bridge/market liveness separation and `TAIL_AT_EOF_NO_BACKFILL`, derives only fully observed 1m and required 5m/15m/1h bars, reconstructs exact immutable strategy versions from their frozen identity JSON, reuses the existing strategy generators and portfolio router, and runs all accepted candidates through one shared Phase 3 risk state per 0.2/0.5/1.0-pip virtual-account scenario.

The segment compiler is deterministic and source-free: it cannot tail MT5 continuously and cannot start a prospective campaign. Offline replay must reproduce the canonical segment payload byte-for-byte from the exact same preflight and raw record sequence.

DEC-050 does not implement the final Phase 8B acceptance decision. The legacy 8-week / 30-date / 40-trade, coverage, timing, spread-parity, profitability, drawdown, replay, and safety gates remain frozen for a later separately approved acceptance compiler.

No `capture`, `run`, `start`, or `review` command is added under DEC-050. Demo/live orders, broker mutation, real-money trading, Phase 9, active-champion mutation, acceptance, and promotion remain locked.


## DEC-051 — Phase 8B acceptance compiler and prospective evidence contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT

The approved `docs/superpowers/specs/2026-09-22-phase8b-acceptance-compiler.md` opens `EXP-20260922-022` for source-free implementation of the deterministic Phase 8B acceptance compiler and the exact prospective campaign-evidence contract that a future live runtime must satisfy.

DEC-051 does not treat DEC-050 source-free segments as prospective evidence by themselves. Acceptance requires a separate exact `fmp-phase8b-campaign-evidence-v1` artifact binding the DEC-049 capture-preflight fingerprint, exact DEC-050 aggregate segment/replay fingerprints, frozen champion set, required symbols, cost scenarios, London-date coverage, timing/operational diagnostics, scenario financial metrics, trade representation, and live spread summaries. It also requires a separately frozen `fmp-phase8b-spread-reference-v1` artifact covering the exact required symbol set.

The legacy minimums remain: at least 40 completed 0.2-pip scorable trades, 8 elapsed calendar weeks, and 30 fully observed London dates. DEC-051 adds a pre-result portfolio-representation minimum of at least two strategy families and two V1 pairs with completed scored trades, matching the purpose of validating a multi-strategy/multi-pair champion rather than allowing one component to carry the entire prospective result.

Operational, timing, spread-parity, financial, safety, and replay gates are frozen exactly in the spec. PASS authorizes only exact champion lifecycle transition `SHADOW_CANDIDATE -> SHADOW_VALIDATED` and eligibility for a separate Phase 9 demo-design proposal. It does not authorize demo/live orders, broker mutation, real-money trading, or Phase 9 execution.

No live capture command is added under DEC-051. A later separately frozen capture/close protocol must produce the exact prospective campaign-evidence artifact before this compiler can issue a real acceptance outcome.


## DEC-052 — Phase 8B prospective capture segment journal

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT

The approved `docs/superpowers/specs/2026-09-22-phase8b-prospective-capture-segment.md` opens `EXP-20260922-023` for the first explicit operator-invoked prospective Phase 8B capture surface.

DEC-052 adds only a bounded `capture-segment` command. The command may discover and tail only the exact fixed required-symbol MT5 FILE_COMMON demo bridge files already bound by DEC-047 through DEC-049. On the first invocation it must build DEC-049 capture preflight and continue with the same EOF-positioned readers; later invocations validate the exact existing preflight and create fresh EOF readers, making restart gaps explicit and non-backfilled.

Every accepted TICK/HEARTBEAT is converted through the DEC-049 deterministic capture envelope and durably appended to create-only JSONL evidence. The record append is flushed/fsynced, and a separately fsynced audit row binds each record fingerprint to receive/completion monotonic timestamps and processing latency. Protocol/session/account/server drift, truncation, malformed records, and symbol mismatch fail closed.

A clean bounded segment close runs the exact DEC-050 compiler and deterministic replay over the durable raw records, requires replay match, and freezes `fmp-phase8b-prospective-segment-v1` evidence binding the raw/audit/operational digests plus DEC-050 segment and replay fingerprints. An interrupted/unclosed segment is retained but can never count as closed campaign evidence.

DEC-052 performs no multi-segment campaign aggregation and no acceptance review. A later separately frozen campaign-close protocol must aggregate only clean replay-matching DEC-052 segments and create the exact DEC-051 campaign-evidence artifact.

Demo/live orders, broker mutation, real-money trading, Phase 9 execution, champion mutation, acceptance, and promotion remain locked.


## DEC-053 — Phase 8B prospective campaign evidence close

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT

The approved `docs/superpowers/specs/2026-09-22-phase8b-campaign-close.md` opens `EXP-20260922-024` for deterministic multi-segment campaign evidence snapshots over exact DEC-052 journals.

DEC-053 fixes the cross-segment state-continuity boundary before any live segment exists. Child DEC-052 runtime results remain integrity evidence only; they are never summed as campaign financial evidence because each bounded child compile starts from the $100,000 baseline. Campaign close instead revalidates every clean raw journal and recompiles all ordered records as one continuous DEC-050 virtual campaign, preserving shared risk/equity/open-position state across process boundaries.

Monotonic receive timestamps remain segment-local. Cross-segment continuity is enforced by immutable prospective-segment identity, non-overlapping wall-clock intervals, per-symbol source-time progression, explicit restart-gap accounting, and no backfill. Aggregate replay must reproduce the campaign segment byte-for-byte.

DEC-053 derives the DEC-051 evidence fields rather than accepting free-form summaries: London weekday denominator/complete dates, nearest-rank p99 processing latency, deadline violations, representation, per-symbol live spread median/p95, scenario metrics, and structural/integrity evidence.

Each `close-campaign` invocation creates an immutable closure snapshot; it is not a permanent capture shutdown, so a later snapshot may include additional clean segments after DEC-051 `PHASE8B_NEED_MORE_DATA`.

The command is source-only over existing artifacts and does not access MT5 or any broker surface. Demo/live orders, broker mutation, real-money trading, Phase 9 execution, champion mutation, acceptance, and promotion remain locked.


## DEC-054 — Phase 8B acceptance review and shadow-validation freeze

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT

The approved `docs/superpowers/specs/2026-09-22-phase8b-acceptance-review.md` opens `EXP-20260922-025` for the final source-only Phase 8B review boundary.

DEC-054 freezes deterministic construction of the required DEC-051 historical spread reference from only the accepted Phase 8A complete canonical 1m retrospective snapshot, with fixed 2015-01-01 through 2026-08-21 range, fixed manifest layout, exact preflight/champion/symbol/cost binding, open/close spread definitions, median, nearest-rank p95, and create-only campaign-bound evidence.

A real `capture-segment` operator invocation is not permitted until that exact spread-reference artifact exists and validates against the campaign preflight. The historical market baseline therefore cannot be selected after prospective results become visible.

DEC-054 also freezes explicit `review-campaign` over one exact DEC-053 closure and the campaign-bound spread reference. NEED_MORE_DATA is non-terminal and permits later clean capture/closure snapshots. PASS or any rejection writes a terminal campaign marker that blocks further Phase 8B capture/review for that campaign.

Only exact PASS may create immutable SHADOW_CANDIDATE -> SHADOW_VALIDATED evidence using the existing registry transition function. Champion identity remains unchanged. PASS authorizes Phase 9 demo-design eligibility only; demo/live orders, broker mutation, real-money trading, Phase 9 execution, and DEMO_ELIGIBLE transition remain locked.


## DEC-055 — Phase 9 demo design proposal

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-demo-design.md` opens `EXP-20260922-026` for a source-only demo-design compiler after exact Phase 8B PASS.

DEC-055 may consume only one exact DEC-054 terminal PASS review and its shadow-validation artifact, plus the exact DEC-049 preflight bound to the same champion. The accepted Phase 8B provider identity selects the MT5 demo continuity path; changing execution provider requires a new decision.

The design freezes the future `fmp-mt5-demo-order-bridge-v1` requirements, exact accepted demo account/server/symbol identities, unchanged Phase 3 risk configuration, protective-stop/reconciliation/idempotency requirements, and secret-handling boundary.

A valid design may authorize source implementation of a future demo adapter only. It cannot enable AutoTrading, submit demo/live orders, mutate broker state, risk real money, or authorize Phase 10.


## DEC-056 — Phase 9 demo order protocol and locked adapter foundation

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-demo-order-protocol.md` opens `EXP-20260922-027` for source-only deterministic demo request, dry-run journal, reconciliation, restart/idempotency, and locked-adapter contracts.

DEC-056 consumes only exact DEC-055 demo designs and existing Phase 3 post-risk `OrderIntent` objects. It freezes deterministic client-order identity, exact accepted demo account/server/provider/symbol binding, mandatory protective-stop geometry, dry-run evidence, and reconciliation discrepancy semantics.

The implemented adapter foundation must contain no MT5/broker transport dependency. Its only submission method always raises `DemoExecutionLockedError`. Demo/live orders, broker mutation, real-money trading, Phase 10, and live execution remain locked.

A later separately approved decision is mandatory before any MT5 mutation transport can be implemented, wired, or enabled.


## DEC-057 — Phase 9 MT5 demo preflight and order-check foundation

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-mt5-demo-preflight.md` opens `EXP-20260922-028` for source-only MT5 practice-account assertion, symbol-contract normalization, exact units-to-volume translation, current-quote/stop validation, deterministic order-check payloads, normalized non-mutating order-check evidence, and immutable preflight evidence.

DEC-057 consumes only exact DEC-055 demo designs and DEC-056 demo-order requests. Phase 3/DEC-056 units and reserved risk remain authoritative; the adapter may not resize risk or silently round volume to fit broker constraints.

The DEC-057 backend boundary is read/check-only and exposes no `order_send`, close, modify, cancel, or other mutation method. The existing Phase 9 CLI remains design-only.

DEC-057 may mark only MT5 demo preflight source readiness. Demo execution/order submission, broker mutation, live orders, real money, Phase 10, and live execution remain locked. A later separately approved decision is mandatory before any mutation-capable MT5 backend may exist.


## DEC-058 — Phase 9 MT5 demo mutation transport source lock

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-mt5-demo-mutation-source.md` opens `EXP-20260922-029` for mutation-capable MT5 Python transport source behind a hard-disabled FMP execution gate.

DEC-058 may normalize the already-connected MetaTrader5 terminal, derive the exact Phase 8B account fingerprint as `sha256(str(ACCOUNT_LOGIN))`, translate freshly revalidated DEC-057 market requests to MetaTrader5 constants, normalize `order_send` results, and read active orders/positions for reconciliation.

The official FMP adapter remains compile-time disabled with `DEMO_EXECUTION_SOURCE_ARMED = False`. DEC-058 defines no builder, CLI flag, environment variable, config, artifact, setter, or public method that can change that value. The adapter checks the gate before any broker read or mutation and raises `DemoExecutionLockedError` while disabled.

The raw backend is infrastructure only and is not exposed by the CLI. Tests may use only fake in-memory MetaTrader5-compatible modules.

Demo execution/order submission, broker mutation through the FMP execution path, real-money trading, Phase 10, and live execution remain locked. A later separately approved decision must explicitly arm demo execution and freeze the operator/session/journal boundary before the first real practice-account order.


## DEC-059 — Phase 9 bounded first demo-session contract and journal

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-bounded-demo-session.md` opens `EXP-20260922-030` for source-only one-request practice-session authorization, readiness, durable journaling, at-most-one ambiguity handling, and recovery semantics.

One DEC-059 arm binds one exact DEC-056 post-risk request, exact champion/strategy/symbol, exact accepted DEMO account/server, one UTC-day-bounded window, one operator-approval reference, and `max_new_orders=1`.

DEC-059 keeps the DEC-058 source lock `DEMO_EXECUTION_SOURCE_ARMED = False`. No real arm artifact, arming CLI, broker-connected command, or demo order is created by this decision. Any submission path still reaches the locked DEC-058 adapter and fails before broker access.

The session contract reuses DEC-056 reconciliation, requires healthy startup state and daily halt inactive, fsyncs `SEND_ATTEMPTED` before any future mutation, spends the arm after one attempted send regardless of broker outcome, and requires post-send reconciliation before session closure.

DEC-059 does not define Phase 9 acceptance or Phase 10 eligibility. A later separately approved decision is mandatory before a real arm can exist, the source execution lock can change, or the first practice-account order can be submitted.


## DEC-060 — Phase 9 demo execution-arm artifact source contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-demo-execution-arm.md` opens `EXP-20260922-031` for source-only construction, validation, and create-only persistence of one exact future demo execution-arm package.

DEC-060 binds exact DEC-055 design, DEC-056 request/client identity, DEC-059 session-arm and session-ready evidence, champion/strategy/symbol, accepted DEMO account/server, exact UTC arm window, one operator approval reference, and `max_new_orders=1`.

The DEC-058 compile-time source gate remains `DEMO_EXECUTION_SOURCE_ARMED = False`. DEC-060 creates no real operator arm during repository verification, adds no arming or execution CLI, performs no broker access, and cannot submit an order.

A valid DEC-060 artifact means only that the arm-package contract is ready. Demo execution, demo-order submission, broker mutation, live orders, real money, and Phase 10 remain locked. A later separately approved decision is required before a real arm may be materialized or the source gate may change.


## DEC-061 — Phase 9 offline demo-arm materialization

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-demo-arm-materialization.md` opens `EXP-20260922-032` for one local-only `materialize-arm` command over already-frozen DEC-055/056/059/060 JSON evidence.

The command may parse and revalidate exact local artifacts and write the create-only DEC-060 execution-arm package. It exposes no semantic override for strategy, symbol, units, risk, stop/target, account/server/provider, client ID, UTC window, approval reference, or order count.

DEC-061 may not import or instantiate MetaTrader5 or a broker mutation backend and may not run order_check/order_send. DEC-058 `DEMO_EXECUTION_SOURCE_ARMED` remains false.

Successful materialization proves only that an exact future arm artifact can be constructed offline. Demo execution/order submission, broker mutation, live orders, real money, and Phase 10 remain locked. A later separately approved decision is required before an arm may become runtime authority or any broker-connected execution command may exist.


## DEC-062 — Phase 9 demo runtime arm authority contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-demo-runtime-authority.md` opens `EXP-20260922-033` for source-only runtime acceptance of one exact DEC-060/061 materialized execution arm.

DEC-062 revalidates exact DEC-055 design, DEC-056 request, DEC-059 session arm/readiness, DEC-060 execution arm, current UTC inside the unchanged arm window, daily-halt inactive, valid DEC-059 journal identity, and zero prior `SEND_ATTEMPTED` events.

A successful runtime-authority record may set only `demo_runtime_arm_authority_ready=true`. DEC-058 `DEMO_EXECUTION_SOURCE_ARMED` remains false and every demo/live order, broker-mutation, real-money, and Phase-10 authorization flag remains false.

DEC-062 adds no broker-connected or order-capable CLI and performs no MT5/broker access. A later separately approved decision is mandatory before the source execution gate may change or a broker-connected runner may consume runtime-authority evidence.


## DEC-063 — Phase 9 broker-connected demo launch preflight

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-demo-launch-preflight.md` opens `EXP-20260922-034` for the final fresh broker read/check verification layer before any separately approved first demo-order decision.

DEC-063 consumes exact DEC-055 through DEC-062 evidence, revalidates current UTC/daily-halt/journal zero-attempt state before broker access, then permits only current account/symbol/tick reads, non-mutating `order_check`, and open-order/open-position reconciliation.

The DEC-063 backend protocol intentionally exposes no `order_send`, submit, cancel, modify, close-position, or other mutation method. A successful launch preflight may set only `demo_launch_preflight_ready=true`; `DEMO_EXECUTION_SOURCE_ARMED` and every execution/order/mutation/live/real-money/Phase-10 authorization remain false.

DEC-063 adds no broker-connected or order-capable CLI. Tests use fake in-memory read/check backends only. A later separately approved decision is mandatory before any runner may invoke `order_send` or the first real practice-account order may be sent.


## DEC-064 — Phase 9 one-shot demo execution permit contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-demo-execution-permit.md` opens `EXP-20260922-035` for source-only construction, validation, and create-only persistence of one immutable future demo execution-permit artifact.

DEC-064 consumes exact DEC-055 through DEC-063 evidence and binds the exact fresh order-check request/result, healthy reconciliation, one-order arm, client-order identity, accepted DEMO account/server, arm window, operator approval reference, journal count/tip, and launch-preflight fingerprint.

A valid permit may set only `demo_execution_permit_artifact_ready=true`. `DEMO_EXECUTION_SOURCE_ARMED` remains false and every demo/live order, broker-mutation, real-money, and Phase-10 authorization flag remains false.

DEC-064 adds no CLI, performs no broker access, and cannot invoke `order_send`. A later separately approved decision is mandatory before any real execution runner may consume the permit or the first practice-account order may be sent.


## DEC-065 — Phase 9 permit-aware one-shot demo runner source

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-one-shot-demo-runner.md` opens `EXP-20260922-036` for source-only orchestration of one future permit-bound practice order behind the unchanged DEC-058 execution gate.

DEC-065 consumes exact DEC-055 through DEC-064 artifacts, validates the unchanged one-order arm window and journal prefix, requires the exact checked MT5 request bytes bound by the permit, and durably fsyncs `SEND_ATTEMPTED` before any future `order_send`.

After one attempted send the arm is spent regardless of broker outcome. The runner never retries, normalizes returned send evidence through DEC-058, performs one post-send reconciliation, records ambiguity explicitly, and permits no automatic broker repair.

Repository source keeps `DEMO_EXECUTION_SOURCE_ARMED=False`, adds no broker-connected or execution CLI, and repository verification uses only fake in-memory backends. A later separately approved decision is mandatory before a real permit can be consumed or the first practice-account order can be sent.


## DEC-066 — Phase 9 demo campaign evidence and acceptance contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-demo-acceptance.md` opens `EXP-20260922-037` for a source-only aggregate demo-evidence contract and deterministic acceptance compiler.

DEC-066 freezes the Phase 9 evidence minimum before any practice result exists: at least 40 completed demo trades, 8 elapsed calendar weeks, 30 distinct demo-session dates, two represented strategy families, and two represented V1 pairs.

PASS additionally requires structural safety, zero unresolved ambiguity/reconciliation/journal failures, a successful restart/recovery drill, and per-represented-pair actual adverse entry slippage with median <=0.5 pip and nearest-rank p95 <=1.0 pip.

Demo profitability metrics are recorded as diagnostics rather than a DEC-066 PASS gate; Phase 10 remains responsible for the combined economic deployment review.

A PASS outcome authorizes only eligibility for a separate Phase 10 deployment-review package. It does not authorize live orders, real money, Phase 11, strategy hot-swap, or any broker mutation.

DEC-066 keeps `DEMO_EXECUTION_SOURCE_ARMED=False`, adds no order-capable CLI, and performs no broker access. A separately approved first-demo execution decision remains mandatory before any real practice-account order may be sent.


## DEC-067 — Phase 9 first-demo authorization packet contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-first-demo-authorization-packet.md` opens `EXP-20260922-038` for a source-only immutable operator-review packet over one exact DEC-064 execution permit.

DEC-067 exposes the exact practice-account identity, strategy/symbol, direction, units/volume, reserved risk, checked price, stop/target, client-order ID, arm window, and checked-request/permit fingerprints without allowing any caller override.

The packet also binds the pre-result DEC-066 demo-campaign obligations and emits one deterministic authorization-challenge fingerprint. Any later explicit first-demo approval must bind this exact challenge and packet; changing any order/account/risk/window detail requires a different challenge and new approval.

DEC-067 does not itself record approval. It keeps `DEMO_EXECUTION_SOURCE_ARMED=False` and every demo-order, broker-mutation, live-order, real-money, Phase-10, and Phase-11 authorization false. It adds no broker-connected or order-capable CLI and performs no MT5 access.


## DEC-068 — Phase 9 explicit approval record and gate-activation contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-explicit-approval-gate-contract.md` opens `EXP-20260922-039` for source-only explicit-approval and operator gate-activation schemas over one exact DEC-067 authorization challenge.

A valid future approval record must bind the exact packet/challenge, permit/request/client identity, DEMO account/server, arm window, operator identity/reference, approval UTC, and the exact statement `APPROVE FIRST DEMO ORDER <challenge>`. Approval must occur inside the immutable launch/arm window.

A valid future gate-activation contract must bind that exact approval and packet and be created inside the same arm window after approval.

DEC-068 does not create a real approval artifact, does not change `DEMO_EXECUTION_SOURCE_ARMED=False`, does not wire the DEC-065 runner, and adds no broker-connected or execution CLI. Current repository evidence still contains no real Phase 8B acceptance/SHADOW_VALIDATED chain from which a real first-demo approval could be formed.


## DEC-069 — Phase 9 approval-gated one-shot runtime wiring

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER

The approved `docs/superpowers/specs/2026-09-22-phase9-approved-runtime-wiring.md` opens `EXP-20260922-040` for source-only wiring from one exact DEC-068 activation contract to the existing DEC-065 one-shot runner.

DEC-069 revalidates the complete DEC-055-through-068 chain, current UTC inside the immutable arm window, activation time ordering, daily-halt inactive, current journal integrity, and zero prior `SEND_ATTEMPTED` before delegation.

When and only when the repository source gate is true, the wrapper delegates to the exact DEC-065 runner; it does not rebuild the checked request, duplicate send logic, add retries, or reinterpret reconciliation/ambiguity outcomes.

Repository `DEMO_EXECUTION_SOURCE_ARMED=False` remains unchanged. Tests may patch the gate only in-process and use fake in-memory mutation backends. No real Phase 8B/Phase 9 artifact chain, approval, activation, broker mutation, or demo order is created by DEC-069.


## DEC-070 — Phase 8B prospective campaign readiness audit

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B PROSPECTIVE CAPTURE

The approved `docs/superpowers/specs/2026-09-22-phase8b-campaign-readiness.md` opens `EXP-20260922-041` for a read-only, non-authoritative campaign-readiness audit plus an updated multi-pair operator handoff.

DEC-070 validates the existing DEC-047 registration, optional DEC-048/049 start/preflight chain, optional DEC-054 spread reference, terminal state, and current fixed FILE_COMMON bridge identities for every exact required symbol. It prints a point-in-time JSON report only and writes no campaign artifact.

The readiness audit may identify `authorize-start`, `freeze-spread-reference`, or `capture-segment` as the next operator action, but even a ready result does not start a segment and sets no acceptance, promotion, Phase 9, order, broker-mutation, live, or real-money authorization.

DEC-070 also replaces the historical USDJPY-only operator handoff with the current Phase 8B portfolio workflow. No real bridge inspection or prospective capture is executed by repository verification.


## DEC-071 — Phase 8B prospective campaign progress preview

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8b-campaign-progress.md` opens `EXP-20260923-042` for a read-only progress preview over existing clean DEC-052 prospective segments.

DEC-071 reuses the exact DEC-053 campaign-close aggregation kernel for segment validation, duplicate/overlap checks, continuous aggregate simulation, replay, observation bounds, London-date coverage, completed 0.2-pip trades, and represented strategy-family/pair counts.

The preview reports the exact DEC-051 minimums and remaining amounts but creates no closure, campaign-evidence artifact, acceptance result, review, lifecycle transition, or terminal marker. Meeting every minimum in the preview is not Phase 8B PASS.

The CLI command `progress --campaign-dir <path>` prints JSON only and authorizes no promotion, SHADOW_VALIDATED transition, Phase 9 action, order, broker mutation, live trading, or real-money action.


## DEC-072 — Phase 8B interrupted segment observability amendment

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8b-interrupted-segment-observability.md` opens `EXP-20260923-043` to fix DEC-071 progress visibility for interrupted DEC-052 capture directories.

DEC-072 adds deterministic closed/unclosed segment inventory to the read-only progress report. In particular, a campaign whose first capture crashes before producing `prospective-segment.json` must report the retained unclosed directory instead of incorrectly reporting zero unclosed segments.

Unclosed directories remain excluded from aggregate simulation, replay, observation bounds, London-date completeness, trade counts, representation, and financial metrics. DEC-072 also adds diagnostic campaign-terminal context and a deterministic progress validator/fingerprint.

DEC-072 writes no campaign evidence, repairs/deletes no interrupted segment, starts no capture, changes no DEC-051 acceptance threshold, and authorizes no promotion, Phase 9 action, broker mutation, order, live trading, or real-money action.


## DEC-073 — Phase 8A direct market learning and controlled retraining amendment

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 MODEL-TRAINING RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-market-learning-foundation.md` opens `EXP-20260923-044` and amends the Phase 8A research architecture so FMP studies market behaviour directly from accepted Dukascopy-derived feature rows in addition to testing hand-written strategy families.

Existing Phase 4/7 rule strategies and the frozen EXP-015 567-configuration search remain valid, immutable benchmarks/challenger sources. DEC-073 does not rewrite their identities, results, or gates.

The new learning track starts from the accepted V1 universe (EURUSD, GBPUSD, USDJPY on 5m/15m/1h) and the leakage-safe Phase 5 feature definitions. The historical `fmp-feature-v1` artifact and its pre-2024 lock remain unchanged; broader retrospective coverage must be created as a new versioned market-learning feature materialization.

The first frozen target foundation labels every eligible feature-row timestamp directly at exact 60-minute and 240-minute horizons. It records future midpoint movement and hypothetical LONG/SHORT net pips under exact 0.2, 0.5, and 1.0 pip adverse slippage per fill using historical BID/ASK execution sides. Missing exact horizon bars fail closed and are never shifted or interpolated.

All historical EXP-044 evidence through 2026-08-20 is `RETROSPECTIVE_ALREADY_SEEN` with no untouched-OOS claim. The first source slice creates labels/contracts only. A later predeclared decision must freeze model families, preprocessing, chronological splits, target/threshold rules, and financial acceptance gates before any result-producing model fit.

Continuous learning is explicitly champion/challenger based: active shadow/demo models are immutable; new prospective observations are appended to an immutable learning ledger; retraining happens offline at a frozen cutoff into a new challenger identity; promotion requires a separate evidence gate. No running model may rewrite itself after a trade or hot-swap itself into an active campaign.

Consequences: Phase 8A remains ACTIVE; EXP-015 remains available as a parallel rule-based benchmark search; DEC-042 and Phase 8B retain their existing locks; no shadow/demo/live/broker/real-money authorization is created by DEC-073.


## DEC-074 — Phase 8A market-learning data-preparation readiness gate

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 MODEL-TRAINING RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-market-learning-readiness.md` adds a mandatory evidence gate between EXP-044 historical data preparation and any model-training protocol.

A readiness artifact may exist only after the persisted aggregate feature evidence and persisted aggregate outcome evidence both revalidate successfully. The outcome evidence must bind the exact supplied feature-evidence fingerprint. For each of the nine EURUSD/GBPUSD/USDJPY × 5m/15m/1h cells, the outcome evidence must also bind the exact feature-manifest SHA-256, the same accepted Phase 2 Dukascopy processed-manifest SHA-256, and the same feature-row count.

A passing readiness result means only `data_preparation_complete=true` and `model_protocol_source_open_authorized=true`. It permits drafting and freezing a separate model-training protocol. It does not authorize a result-producing training run.

The readiness artifact must retain `model_protocol_result_authorized=false`, `model_fit_authorized=false`, `promotion_authorized=false`, and all shadow/demo/broker-mutation/live/real-money authorization flags false.

DEC-074 chooses no model family, preprocessing, chronological split, target, prediction threshold, trading threshold, or financial acceptance gate. Those choices require a later predeclared decision before any fit. No readiness artifact exists until the authoritative feature and outcome workflows run successfully from merged `main`.


## DEC-075 — Phase 8A EXP-044 execution observability

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 MODEL-TRAINING RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-execution-observability.md` adds a read-only deterministic status layer over the existing EXP-044 feature, outcome, and DEC-074 readiness evidence chain.

The status layer validates exact manual workflow identity when run metadata is supplied, revalidates persisted readiness fingerprints, and reports the earliest unresolved state from feature dispatch through `MODEL_PROTOCOL_SOURCE_OPEN`.

DEC-075 creates no research-result authorization. `MODEL_PROTOCOL_SOURCE_OPEN` may be reported only when a valid DEC-074 readiness artifact is supplied and cross-bound to the exact feature/outcome evidence chain. Even then, `model_protocol_result_authorized=false`, `model_fit_authorized=false`, promotion remains false, and all shadow/demo/broker/live/real-money authorizations remain false.

DEC-075 does not change the next hard gate: the authoritative feature and outcome workflows must still run successfully from merged `main` before model-protocol source work may open.


## DEC-076 — Phase 8A EXP-044 pair-batched workflow execution

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-pair-batched-workflows.md` changes the feature and outcome workflow topology from pair × timeframe jobs to one job per pair, processing 5m, 15m, and 1h sequentially after one verified download of that pair's accepted Phase 2 Dukascopy artifact.

The exact nine logical feature cells and nine logical outcome cells remain unchanged. Per-timeframe artifact names, source artifact IDs and SHA-256 identities, feature definitions, outcome labels, cost assumptions, aggregate evidence, DEC-074 readiness, and DEC-075 status semantics remain unchanged.

This reduces accepted Phase 2 ZIP downloads from nine to three per workflow without changing any research result or authorization. No EXP-044 feature or outcome workflow had been dispatched before DEC-076.

Both workflows remain manual and merged-main only. DEC-076 authorizes no model fit, promotion, shadow/demo action, broker mutation, live order, or real-money action.


## DEC-077 — Phase 8A EXP-044 pair outcome materialization

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-pair-outcome-materialization.md` adds a pair-level outcome materializer that verifies and loads one symbol's accepted Phase 2 one-minute history once, then reuses that exact quote frame for the 5m, 15m, and 1h outcome cells.

Tests require the pair-level path to produce manifests identical to three independent single-cell materializations for the same inputs. The existing single-cell API remains available.

DEC-077 changes no Dukascopy identity, feature definition, horizon, slippage rule, label rule, output schema, artifact identity, aggregate evidence, DEC-074 readiness, or DEC-075 status semantics.

No EXP-044 feature or outcome workflow had been dispatched before DEC-077. Model fitting, promotion, shadow/demo actions, broker mutation, live orders, and real-money actions remain unauthorized.


## DEC-078 — Phase 8A EXP-044 source artifact availability preflight

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-source-artifact-preflight.md` adds a read-only source-artifact gate before both EXP-044 feature generation and outcome materialization.

The gate validates the exact frozen Phase 2 run `34782357048`, head SHA `158c1c121655867b7fb2886fe755585dfcd682ec`, artifact IDs/names, ZIP SHA-256 digests, sizes, main-branch identity, non-expired state, and at least 12 hours of remaining GitHub artifact lifetime.

On 2026-09-23 the three frozen Phase 2 artifacts were non-expired and downloadable. The earliest recorded expiry was `2026-12-12T20:57:47Z`.

DEC-078 performs no new Dukascopy acquisition and changes no research semantics or authorization. A failed/expired source must stop execution before heavy work; silent reacquisition or substitution is not authorized.


## DEC-079 — Phase 8A EXP-044 outcome identity projection

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-outcome-identity-projection.md` reduces pair-outcome memory by retaining only six outcome-identity/timing columns after each feature parquet has passed exact byte-size, SHA-256, full 55-column schema, and row-count validation.

A dedicated projected-identity outcome builder is frozen. Tests require it to produce exactly the same outcome rows and accounting as the original full-feature builder, and the existing full-frame/single-cell path remains available.

DEC-079 changes no feature artifact, quote source, horizon, cost model, label, output schema, evidence rule, readiness rule, or authorization. No EXP-044 result-producing workflow had been dispatched before this amendment.


## DEC-080 — Phase 8A EXP-044 reused-source feature determinism

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-reused-source-feature-determinism.md` changes feature workflow execution so each pair/timeframe Phase 2 source is validated/read once, then the EXP-044 feature frame is built twice sequentially from that same verified source for the existing deterministic A/B output comparison.

Tests require exact manifest and parquet equivalence with the existing single-cell feature generator and exactly one source-loader invocation per timeframe.

DEC-080 changes no source identity, feature definition, feature schema, artifact identity, evidence rule, readiness rule, outcome rule, model authorization, or trading authorization. No EXP-044 result-producing workflow had been dispatched before this amendment.


## DEC-081 — Phase 8A EXP-044 manual operator launch helper

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-operator-launch-helper.md` adds a dry-run-by-default operator CLI for the existing manual EXP-044 workflow-dispatch gates.

The helper requires an authenticated GitHub CLI, a clean local `main` exactly matching freshly fetched `origin/main`, and the exact `Dtwosam/FMP` origin. It refuses duplicate manual-main feature/outcome runs. Outcome preparation additionally validates the exact successful feature workflow run before constructing the dispatch command.

Actual dispatch requires an explicit `--execute` flag. Successful submission claims no research result and creates no model/trading authorization.

DEC-081 does not change either workflow trigger and does not bypass the manual gate.


## DEC-082 — Phase 8A EXP-044 operator source/evidence preflight

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-operator-evidence-preflight.md` strengthens the DEC-081 manual launch helper.

Before either stage, the helper now reuses DEC-078 to validate the live metadata and remaining lifetime of the exact accepted Phase 2 artifacts. Before outcome preparation, it additionally requires and downloads the exact non-expired aggregate feature-evidence artifact bound to the successful feature-run head SHA, fingerprint-validates the evidence, cross-binds its code commit to that run, and keeps every model/trading authorization false.

The workflows remain the final authority and independently repeat these checks. DEC-082 changes no workflow trigger, research semantic, or authorization.


## DEC-083 — Phase 8A EXP-044 operator readiness inspection

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 MODEL-TRAINING RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-operator-readiness-inspection.md` adds a read-only `readiness` mode to the EXP-044 operator helper.

Given exact feature and outcome run IDs, it verifies both successful manual-main workflow identities, downloads the exact non-expired aggregate feature evidence, aggregate outcome evidence, and DEC-074 readiness artifacts, runs the existing fingerprint loaders, and passes the complete chain to DEC-075 execution status.

The mode succeeds only when DEC-075 recomputes `MODEL_PROTOCOL_SOURCE_OPEN`. It performs no dispatch and keeps model-protocol-result, model-fit, promotion, shadow/demo/broker/live/real-money authorizations false.


## DEC-084 — Phase 8A EXP-044 Phase 2 release preservation

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-phase2-release-preservation.md` adds a manual merged-main workflow that preserves the exact already accepted Phase 2 Actions ZIP bytes as GitHub release assets before the original Actions artifacts expire.

The workflow re-verifies the original artifact IDs, exact ZIP byte sizes, ZIP SHA-256 identities, and embedded processed-manifest SHA-256 identities before creating a draft release. The uploaded release ZIP assets must expose the same frozen sizes and SHA-256 digests before publication.

The frozen release tag is `fmp-phase2-accepted-artifacts-v1`. No asset replacement is permitted and no new Dukascopy acquisition occurs.

DEC-081/082/083 operator behavior remains intact; DEC-084 adds a dry-run-by-default `preserve-phase2` operator stage. DEC-084 creates no research result, no new accepted dataset, and no model/trading authorization.


## DEC-085 — Phase 8A EXP-044 preserved Phase 2 source fallback

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-preserved-source-fallback.md` adds a run-wide exact-byte source resolver to the EXP-044 feature/outcome workflows and operator.

The resolver prefers the complete original DEC-078 Actions bundle. If that bundle is not fully ready, it may use only the complete published DEC-084 preservation release after revalidating the preservation manifest, exact release asset set, ZIP sizes/digests, and frozen Phase 2 identities.

Mixed Actions/release execution is forbidden. Pair jobs independently reverify ZIP size, ZIP SHA-256, and embedded processed-manifest SHA-256 regardless of source mode.

`preserve-phase2` remains strict to the original Actions artifacts. Feature/outcome operator stages may use the exact release fallback. DEC-085 performs no new data acquisition and creates no model/trading authorization.


## DEC-086 — Phase 8A EXP-044 operator continuation planner

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-operator-continuation-planner.md` adds a read-only `next` mode to the EXP-044 operator.

The planner requires at most one manual-main run per preservation/feature/outcome workflow, fails closed on duplicates, reports in-progress and failed-run review states without automatic retries, validates the published DEC-084 preservation release, reuses DEC-082 feature-evidence validation, reuses DEC-083 outcome/readiness inspection, and delegates final readiness classification to DEC-075.

The `next` mode has no `--execute` argument and never submits `gh workflow run`. Dispatch commands may be printed only as the next operator action. All model/trading authorization remains false.


## DEC-087 — Phase 8A EXP-044 single-step operator advance

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-single-step-advance.md` adds a dry-run-by-default `advance` mode that consumes the public DEC-086 `next` planner rather than duplicating gate logic.

Only preservation-, feature-, or outcome-dispatch-required states may map to a command. The command must exactly match the DEC-086 report. With `--execute`, the planner is run a second time and the two reports must be identical before exactly one workflow dispatch may be submitted.

In-progress, review-required, duplicate, readiness, and protocol-source-open states are non-executable. Failed workflows are never automatically retried. Dispatch submission claims no result and creates no model/trading authorization.


## DEC-088 — Phase 8A EXP-044 predeclared model-training protocol

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 MODEL-TRAINING RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-model-training-protocol.md` freezes the first direct-market model protocol only after DEC-074 readiness was actually satisfied by authoritative feature run `35867307338` and successful outcome run `35876715434`.

The exact V1 model universe is 18 independent cells: EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m. Each cell uses exactly the 48 frozen `FEATURE_VALUE_COLUMNS`; there is no pooled cross-pair, cross-timeframe, or cross-horizon model.

The only V1 target is the three-class `best_direction_0p5` outcome. Models therefore predict `LONG`, `SHORT`, or `NO_TRADE` after the already-frozen historical BID/ASK and 0.5-pip-per-fill target-cost semantics. Future outcome values and result-derived feature selection are forbidden as inputs.

Chronology is frozen as fit 2015-2020, selection 2021-2022, validation 2023-2024, and retrospective holdout 2025-01-01 through 2026-08-20. A row is admitted only if its exact target exit also remains before that split's end-exclusive boundary, creating the required 60m/240m boundary purge. The 2025-2026 holdout remains `RETROSPECTIVE_ALREADY_SEEN`, not untouched OOS evidence.

Preprocessing is fit-period median imputation for both families, fit-period standardization for logistic regression only, and fail-closed all-null fit columns. The only model families are fixed L2 logistic regression and shallow histogram gradient boosting under `scikit-learn==1.9.1`, with no hyperparameter search, class reweighting, resampling, calibration, AutoML, or neural-network expansion.

Candidate confidence cutoffs are exactly 0.50, 0.60, and 0.70. A trade candidate exists only when LONG or SHORT is the strict unique highest-probability class and meets the fixed cutoff; ties and insufficient confidence are `NO_TRADE`. Probability never changes position size.

Selection requires at least 250 directional candidates plus strictly positive total and mean 0.5-pip net pips and gross positive pips greater than absolute gross negative pips. At most one variant per cell survives under the frozen deterministic tie-break. There is no refit after selection. Validation and the gated retrospective holdout must independently satisfy the same conditions at both 0.5- and 1.0-pip adverse slippage; 0.2 pip remains diagnostic.

DEC-088 creates a canonical machine-readable protocol payload/fingerprint but authorizes no result-producing fit. `model_protocol_result_authorized=false`, `model_fit_authorized=false`, promotion and shadow/demo/broker/live/real-money authorizations remain false. A later separate guarded decision must bind the exact merged DEC-088 protocol fingerprint and the verified DEC-074 readiness chain before a model-training workflow may run.

Consequences: EXP-044 data preparation remains complete; the model protocol is frozen source-only; result-producing fit remains locked; no historical qualification, portfolio admission, shadow action, demo order, broker mutation, live order, or real-money action is created by DEC-088.


## DEC-089 — Phase 8A EXP-044 model-run source gate

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-044 MODEL-TRAINING RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-model-run-source-gate.md` adds a source-only fail-closed gate after DEC-088.

The gate binds the exact merged DEC-088 protocol fingerprint `1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605` from source commit `a9305ba9c42b7224e5d4b3f7d26f268447cdf469` to the already verified DEC-074 preparation chain: feature run `35867307338`, feature evidence fingerprint `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`, outcome run `35876715434`, aggregate outcome-evidence artifact `10758027876`, and readiness artifact `10757578276`.

DEC-075 must still reconstruct `MODEL_PROTOCOL_SOURCE_OPEN` from the actual persisted evidence contents before DEC-089 may report `MODEL_PROTOCOL_FROZEN`. Artifact IDs are additional frozen identities, not substitutes for evidence validation.

`MODEL_PROTOCOL_FROZEN` sets `model_run_source_open_authorized=true` only. It remains non-dispatchable under DEC-087 and authorizes no model-training workflow execution.

DEC-089 adds no estimator fit, no training workflow, and no result-producing run. `model_protocol_result_authorized=false`, `model_fit_authorized=false`, promotion and all shadow/demo/broker/live/real-money authorizations remain false.

Consequences: the first EXP-044 model protocol is now frozen and machine-bound to its verified preparation evidence, while actual model-run implementation and every result-producing fit remain behind a later separate decision.


## DEC-090 — Phase 8A EXP-044 deterministic model-training core

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY AUTHORITATIVE EXP-044 MODEL-TRAINING RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-model-training-core.md` implements the deterministic in-memory training/evaluation core for the unchanged DEC-088 protocol after DEC-089 froze that protocol/evidence identity.

The implementation validates exact feature/outcome identities, exact horizon timing, scenario-direction consistency, chronological split membership, all-three-class fit support, and the frozen processed-manifest identity before model calculations.

The two DEC-088 model families are each fit exactly once on the fit split. The fixed three confidence thresholds create exactly six selection variants. The core applies the predeclared 0.5-pip selection gate and deterministic tie-break, never refits after selection, opens validation only for a selected variant, and opens the retrospective holdout only after both 0.5- and 1.0-pip validation gates pass. The 0.2-pip scenario remains diagnostic.

The result preserves deterministic preprocessing/model fingerprints, probability and candidate-identity digests, classification diagnostics, financial metrics, every rejected variant, and a canonical result fingerprint. Promotion/shadow/demo/broker/live/real-money flags remain false in the core result.

DEC-090 intentionally adds no training workflow, no CLI, no artifact-backed authoritative runner, and no operator dispatch path. `MODEL_TRAINING_RESULT_EXECUTION_AUTHORIZED=false`. Synthetic unit-test fits are permitted only to validate source behavior; they are not historical EXP-044 evidence and grant no result authorization.

Consequences: deterministic model-training source now exists, but the authoritative historical EXP-044 model fit remains locked. A later separate decision must bind the exact merged DEC-090 source identity and revalidate the DEC-088/DEC-074 chain before any artifact-backed result-producing fit can run.


## DEC-091 — Phase 8A EXP-044 artifact-backed model-runner source

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY AUTHORITATIVE EXP-044 MODEL-TRAINING RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-model-artifact-runner.md` freezes the artifact-backed source required to consume the already-persisted EXP-044 feature/outcome evidence without regenerating market data.

DEC-091 binds the DEC-088 protocol fingerprint `1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605`, merged DEC-090 training-core commit `640274df9dcbefa0feee599bffdeb63a581db780`, feature run `35867307338`, outcome run `35876715434`, feature evidence fingerprint `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`, outcome evidence fingerprint `b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117`, and readiness fingerprint `412573f505ec7912ff934cc6338cf4591b604e0beddb2cb6abb79447c777b105`.

The source freezes all nine feature-cell and all nine outcome-cell GitHub artifact IDs/digests. It recomputes the readiness fingerprint from readiness content, then binds each extracted cell directory to readiness through exact manifest SHA-256, processed Phase 2 manifest SHA-256, code commit, row counts, feature/outcome versions, evidence label, horizons, slippage scenarios, and upstream feature evidence identity.

Every manifest-listed parquet file is independently checked for safe path, SHA-256, byte size, declared row count, actual row count, frozen column order, sorted unique artifact paths, concatenated row total, and schema fingerprint. Authoritative full-history cells require exactly 140 monthly partitions.

DEC-091 also freezes deterministic aggregate model-result evidence before any authoritative result exists. That evidence requires all 18 DEC-088 cells, canonical ordering, per-cell result fingerprints, DEC-088/090 identities, upstream feature/outcome/readiness identities, and all promotion/trading locks false.

`AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED=false`. The authoritative bundle runner refuses before loading cells or calling the training core. No model-training workflow, CLI, operator dispatch mapping, historical fit, promotion, shadow action, demo order, broker mutation, live order, or real-money action is introduced.

Consequences: the exact historical artifact consumption and result-evidence source is frozen, but the authoritative EXP-044 model result remains locked behind a later separately merged execution decision.


## DEC-092 — Phase 8A EXP-044 frozen model-training workflow source

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY AUTHORITATIVE EXP-044 MODEL-TRAINING RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-model-workflow-source.md` freezes the manual workflow, CLI, and fail-closed execution-gate source that may later run the already-frozen DEC-088 through DEC-091 stack.

The execution gate binds the unchanged DEC-091 artifact runner, DEC-090 training core, and DEC-088 protocol by exact Git blob identities `27c0848d16722a22b4762f5842396c2aebc92bec`, `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`, and `549b2a04f961d9d8ad83caea9c02b40ee54adec2`, plus the DEC-088 protocol fingerprint. Checked-out file bytes are converted to Git blob identities at runtime, so source drift fails closed.

The frozen workflow `.github/workflows/phase8a-exp044-model-training.yml` is manual-only, main-only, and has no user inputs. Its first job calls the execution gate. All nine pair/timeframe jobs depend on that authorization preflight, and the aggregate evidence job depends on all model-cell jobs.

The matrix freezes the exact nine feature artifact IDs/digests, nine outcome artifact IDs/digests, and readiness artifact ID/digest. When later authorized, each pair/timeframe job independently verifies downloaded ZIP SHA-256 before the DEC-091 manifest/parquet validation layer runs, then executes only the fixed 60m and 240m cells. No market-data acquisition, feature regeneration, outcome rematerialization, target/hyperparameter input, or alternate artifact discovery is present.

The CLI requires the execution gate before readiness/artifact loading, estimator fitting, or aggregate result compilation, and binds result execution to the exact checked-out Git HEAD.

Under DEC-092, `MODEL_RUN_DISPATCH_AUTHORIZED=false`, `AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED=false`, `MODEL_PROTOCOL_RESULT_AUTHORIZED=false`, and `MODEL_FIT_AUTHORIZED=false`. The operator reports `MODEL_RUN_WORKFLOW_SOURCE_FROZEN` with no dispatch command, so `advance --execute` remains non-mutating for model work.

Consequences: executable workflow source is frozen and inspectable before any result exists, but no authoritative model-training run is yet authorized or dispatched. A later separate decision must bind the exact merged DEC-092 workflow/CLI/gate source and explicitly open one guarded historical model-run dispatch while keeping promotion and all trading permissions false.


## DEC-093 — Phase 8A EXP-044 single historical model-result authorization

**Date:** 2026-09-23
**Status:** APPROVED BEFORE THE FIRST AUTHORITATIVE EXP-044 MODEL-TRAINING RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-model-run-authorization.md` authorizes exactly one result-producing historical EXP-044 model workflow after DEC-093 is merged.

The authorization is constrained to the unchanged DEC-088 protocol, DEC-090 training core, DEC-091 artifact runner/evidence contract, exact persisted feature run `35867307338`, exact persisted outcome run `35876715434`, and readiness artifact `10757578276`.

DEC-092 was merged at `9645bae73ec1d113383c9957569c6e05a70b2e96`. Before DEC-093 source work, GitHub reported zero manual-main `phase8a-exp044-model-training` runs. DEC-093 records the prior DEC-092 workflow/CLI/gate/operator blobs for audit, then intentionally hardens the workflow before opening execution.

The hardened workflow enforces the one-run invariant internally: it verifies the current manual-main run, lists all manual-main runs of the same workflow, excludes only its own `GITHUB_RUN_ID`, and fails if any prior run exists. A failed first model run consumes the slot and is not automatically retried or replaced.

The authorized runtime is pinned to Python `3.12.14` plus the exact dependency set in `requirements/exp044-model-run.txt`: NumPy 2.5.3, SciPy 1.18.1, scikit-learn 1.9.1, joblib 1.6.0, threadpoolctl 3.7.0, cloudpickle 3.1.2, narwhals 2.26.0, Polars 1.44.2, and polars-runtime-32 1.44.2. Runtime authorization also validates exact Git blobs for the dependency manifest, pyproject, preprocessing, feature schema, market contracts, and outcome source/schema in addition to the already-frozen protocol/training/artifact code.

DEC-093 sets model-run dispatch, authoritative result execution, protocol-result production, and model fitting authorization true only for the guarded first run. Promotion, shadow, demo, broker mutation, live-order, real-money, and trading authorization remain false.

The read-only operator exposes `MODEL_RUN_DISPATCH_REQUIRED` only when no model run exists. Once any model run exists, dispatch authorization is consumed at the operator layer. In-progress runs report `MODEL_RUN_IN_PROGRESS`, failures report `MODEL_RUN_REVIEW_REQUIRED`, and a successful run is independently revalidated before reporting `MODEL_RESULT_REVIEW_REQUIRED`.

DEC-093 also adds deterministic aggregate model-result validation: the evidence fingerprint is recomputed; all 18 exact cells are required; each cell result fingerprint is required; selection/validation/retrospective-holdout status chains must be logically consistent; and all promotion/trading locks remain false.

Consequences: exactly one historical EXP-044 model-result run is authorized after merge, but no run is dispatched by DEC-093 itself and no result is assumed. Any later promotion or shadow-candidate decision requires a separate review of the produced retrospective evidence.


## DEC-094 — Phase 8A EXP-044 failed model-run review and V1 closure

**Date:** 2026-09-23
**Status:** APPROVED AFTER THE SINGLE DEC-093 MODEL RUN FAILED

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp044-model-run-failure-review.md` records the terminal outcome of the one DEC-093-authorized historical model workflow, run `35891605645`, attempt 1, from `main` SHA `e97fa03d0e94fd505d0f926eb730e01a41947880`.

Authorization preflight succeeded. All nine matrix jobs completed. Five pair/timeframe jobs completed both 60m/240m model-cell computations and then failed because `actions/upload-artifact@v6` excluded the hidden `.results` directory by default: EURUSD 5m, EURUSD 1h, GBPUSD 15m, GBPUSD 1h, and USDJPY 1h. Their ephemeral JSON was not persisted and is not accepted as model evidence.

Four pair/timeframe jobs failed during fitting because frozen L2 logistic regression with `lbfgs` did not converge within DEC-088's `max_iter=2000`: EURUSD 15m, GBPUSD 5m, USDJPY 5m, and USDJPY 15m. DEC-090 correctly treated each convergence warning as a hard failure.

The aggregate model-evidence job was skipped and GitHub reports zero persisted artifacts for the run. Run `35891605645` remains immutable failed audit evidence and must not be rerun, retried, deleted, or automatically replaced.

DEC-094 repairs only the workflow's evidence-persistence source: pair/timeframe upload now runs `if: always()`, includes hidden files, and warns rather than errors when no result file exists; aggregate upload also includes hidden files. This source repair does not authorize another EXP-044 V1 run.

DEC-088's model universe and estimator parameters remain unchanged. In particular, DEC-094 does not increase logistic `max_iter`, change solver/tolerance/regularization, remove a family, change target/features/splits/thresholds, or otherwise rescue a result after observing V1 behavior.

DEC-094 closes model dispatch, authoritative result execution, model-protocol result production, and fitting authorization. Promotion, shadow, demo, broker mutation, live-order, real-money, and trading authorizations remain false.

The read-only operator machine-validates the exact run/job/failure/artifact inventory and reports `MODEL_RUN_FAILURE_REVIEWED`. EXP-044 V1 is closed with no authoritative aggregate model result.

Consequences: any continued direct-market model research requires a separately predeclared successor experiment/protocol that explicitly acknowledges post-result adaptation and cannot describe the reused historical data as untouched OOS evidence.


## DEC-095 — Phase 8A EXP-045 successor model protocol

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 MODEL RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp045-model-successor-protocol.md` opens `EXP-20260923-045` as a separately identified successor after DEC-094 closed EXP-044 V1.

EXP-045 explicitly binds failed predecessor run `35891605645`, predecessor head SHA `e97fa03d0e94fd505d0f926eb730e01a41947880`, DEC-094 failure review, and the DEC-088 base protocol fingerprint `1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605`. It is marked `prior_result_informed=true` and `untouched_oos=false`.

The successor preserves the 18 direct-market cells, exact 48 feature inputs, `best_direction_0p5` target, chronology, confidence thresholds, financial gates, no-refit rule, and both frozen model-family configurations. Logistic regression remains `lbfgs` with `max_iter=2000`; no solver fallback, iteration increase, preprocessing change, or post-result tuning is authorized.

DEC-095 predeclares the family-failure policy before any EXP-045 result. Each family is attempted once. If unchanged logistic regression emits `ConvergenceWarning` at its frozen limit, it is recorded as `FAILED_NON_CONVERGENCE` / `LBFGS_MAX_ITER_REACHED`; its three threshold variants remain present as `FAMILY_UNAVAILABLE` and ineligible, while the unchanged HGB family may continue. Any other family-fit failure remains fail-closed. If no family fits, the cell is `NO_MODEL_FAMILY_AVAILABLE`, distinct from a financial `NO_MODEL_CHALLENGER`.

DEC-095 also predeclares evidence persistence learned from EXP-044: completed pair/timeframe result JSON must be preserved even if a later cell fails, hidden result files must be included, missing result files warn without masking the original computation failure, aggregate hidden files must be included, and authoritative aggregate evidence still requires all 18 complete cells.

All result, fit, promotion, shadow, demo, broker, live, real-money, and trading authorizations remain false. DEC-095 creates no EXP-045 workflow and dispatches nothing.

Consequences: EXP-044 V1 remains closed as failed negative evidence. EXP-045 is source-predeclared but has no model result. A later separate decision may implement the deterministic EXP-045 training core; another later decision must separately authorize any historical result-producing fit.


## DEC-096 — Phase 8A EXP-045 deterministic successor training core

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp045-model-training-core.md` implements the deterministic in-memory training/evaluation core for the exact DEC-095 successor protocol.

DEC-096 binds the closed DEC-090 base training-core blob `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7` and the DEC-095 successor protocol blob `44129fc5337fb55b9c7d81f5ba0561ea788bd264`. The new successor training-core source is frozen at Git blob `3f0bc1bfa9640d08175e72cdf131bb97c94d562c`.

The implementation reuses DEC-090's already-tested frame validation, preprocessing, estimator construction, probability checking, candidate conversion, financial gate, tie-break, validation, and retrospective-holdout mechanics without changing any estimator parameter.

DEC-095's new family-failure control flow is implemented explicitly. Each family is attempted once. If unchanged logistic regression raises the exact DEC-090 convergence failure, EXP-045 records `FAILED_NON_CONVERGENCE` / `LBFGS_MAX_ITER_REACHED`, does not retry, preserves three `FAMILY_UNAVAILABLE` threshold slots, and allows unchanged HGB to continue. Any other family-fit exception still fails the cell closed.

The successor result identity carries `EXP-20260923-045`, DEC-096 core identity, DEC-095 protocol identity/fingerprint, DEC-088 base protocol fingerprint, predecessor failed run `35891605645`, `prior_result_informed=true`, and `untouched_oos=false`. No selected model is ever refit after fit.

`SUCCESSOR_TRAINING_RESULT_EXECUTION_AUTHORIZED=false` and `MODEL_FIT_AUTHORIZED=false`. DEC-096 creates no artifact-backed historical runner, CLI, GitHub Actions workflow, or operator dispatch path. Synthetic test fits are source validation only and are not EXP-045 historical evidence.

Promotion, shadow, demo, broker mutation, live-order, real-money, and trading authorizations remain false.

Consequences: deterministic EXP-045 training source now exists, but no EXP-045 historical result exists or is authorized. A later separate decision may freeze an artifact-backed runner/evidence contract; a still-later execution decision is required before any result-producing fit.


## DEC-097 — Phase 8A EXP-045 artifact-backed runner and aggregate evidence source

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp045-model-artifact-runner.md` freezes the artifact-backed EXP-045 source boundary after DEC-095 froze the successor protocol and DEC-096 implemented the deterministic training core.

DEC-097 binds the DEC-091 verified historical data-loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`, DEC-094 failed-run review blob `2260ad4ad08a7e9874bd28030be977a3e71436f9`, DEC-095 successor protocol blob `44129fc5337fb55b9c7d81f5ba0561ea788bd264`, and DEC-096 successor training-core blob `3f0bc1bfa9640d08175e72cdf131bb97c94d562c`. The DEC-097 runner source itself is frozen at Git blob `adebcc48130e8800741810c239528ef6c21eea6e`.

EXP-045 reuses only the already-verified EXP-044 feature/outcome/readiness artifacts as historical source data. It does not regenerate data or inherit EXP-044 model-result identity. Aggregate evidence records `source_data_experiment_id=EXP-20260923-044` while model-result identity remains `EXP-20260923-045`.

The old DEC-091 loader is reused only for readiness/manifest/parquet byte validation under an exact blob binding. EXP-045 cell computation uses only the DEC-096 successor core, and aggregate result identity is compiled by the new DEC-097 source.

The aggregate compiler requires all 18 exact cells, recomputes every cell result fingerprint, validates the exact successor/core/protocol/predecessor identities, requires exactly the two frozen family identities, permits only the predeclared logistic `FAILED_NON_CONVERGENCE` family state, preserves six variant slots, and validates successor chronology states including `NO_MODEL_FAMILY_AVAILABLE`, `NO_MODEL_CHALLENGER`, validation rejection, and validation/holdout pass/reject states.

Aggregate evidence is deterministic, canonically ordered, carries the future execution code commit, rebinds the exact historical feature/outcome/readiness evidence, and keeps all result/fit/promotion/shadow/demo/broker/live/real-money/trading locks false. Persisted aggregate JSON is independently revalidated by recomputing its canonical fingerprint and checking all 18 cell summaries before it can be returned to a later review/operator layer.

`AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED=false` and `SUCCESSOR_MODEL_FIT_AUTHORIZED=false`. The artifact-backed runner refuses before readiness validation, artifact loading, or model fitting. DEC-097 adds no CLI, workflow, operator dispatch, or historical result.

Consequences: EXP-045 now has frozen protocol, deterministic training core, verified artifact-consumption source, and aggregate evidence contract, but still no historical model result. A later separate decision may freeze workflow/CLI/execution-gate source; another separate authorization is required before any result-producing fit.


## DEC-098 — Phase 8A EXP-045 frozen model-workflow source

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp045-model-workflow-source.md` freezes the manual EXP-045 workflow, fail-closed CLI, pinned numerical runtime, and execution-gate source around the already-merged DEC-095/096/097 chain.

DEC-098 binds merged DEC-097 commit `f6c1090064cd3d85c7c3503dec1ef461eeba5da2`, DEC-097 runner blob `adebcc48130e8800741810c239528ef6c21eea6e`, DEC-096 core blob `3f0bc1bfa9640d08175e72cdf131bb97c94d562c`, DEC-095 protocol blob `44129fc5337fb55b9c7d81f5ba0561ea788bd264`, DEC-094 failure-review blob `2260ad4ad08a7e9874bd28030be977a3e71436f9`, and the DEC-091 historical data-loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`.

The frozen workflow blob is `d3e4d11a8e8270417d6bbced27e756b7cc23c324`, the CLI blob is `ff0ed231e22589c3597672bb8bab1f62b321647d`, and the execution-gate source blob is `6bdb3dfe3d8b548610259cbdfc6245398f9fc199`.

The workflow is manual-only, main-only, and exposes no user inputs. It freezes all nine persisted feature/outcome artifact pairs, the readiness artifact, the exact 60m/240m cell horizons, Python 3.12.14, and the pinned EXP-045 numerical runtime.

The pair/timeframe persistence behavior implements DEC-095 exactly: upload runs even after a cell failure, includes hidden `.results`, and warns when no result exists. Aggregate evidence remains all-or-nothing and includes hidden aggregate files.

Every result-producing job depends on authorization preflight. `SUCCESSOR_MODEL_RUN_DISPATCH_AUTHORIZED=false`, `AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED=false`, `SUCCESSOR_MODEL_PROTOCOL_RESULT_AUTHORIZED=false`, and `SUCCESSOR_MODEL_FIT_AUTHORIZED=false`. No operator dispatch mapping is added and no EXP-045 workflow run is submitted.

Consequences: EXP-045 now has frozen protocol, training core, artifact runner/evidence contract, workflow, CLI, runtime, and execution-gate source, but still no historical model result. A later separate decision must bind the exact merged DEC-098 identities before at most one guarded historical result-producing run can be authorized. Promotion, shadow, demo, broker, live, real-money, and trading authorization remain false.

## DEC-099 — Phase 8A EXP-045 single historical model-result authorization

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL-RESULT RUN

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp045-model-run-authorization.md` authorizes at most one guarded historical EXP-045 model-result workflow after DEC-099 is merged.

DEC-098 merged at `292a86fa2aa497b31c0dd4e0284115b185f31ed4`. Before DEC-099 source work, GitHub reported zero manual-main `phase8a-exp045-model-training` runs. DEC-099 binds that merged commit plus the prior DEC-098 workflow blob `d3e4d11a8e8270417d6bbced27e756b7cc23c324`, CLI blob `ff0ed231e22589c3597672bb8bab1f62b321647d`, and execution-gate blob `6bdb3dfe3d8b548610259cbdfc6245398f9fc199`.

The authorized workflow is hardened at Git blob `3c7fc17d747bca474bd91e44cb753c5cf4cc153b`. It remains manual-only, main-only, and input-free, and now rejects any prior manual-main EXP-045 model run before checking execution authorization. A failed or cancelled first run consumes the one-run slot; no rerun or replacement is automatically authorized.

DEC-099 sets the outer model-run dispatch, authoritative result execution, protocol-result production, and model-fit authorization flags true only for that guarded first historical run. The unchanged DEC-095 protocol and DEC-096 training-core source locks remain false beneath the separate authorization layer.

The frozen pair/timeframe inventory, 60m/240m horizons, persisted DEC-091/097 historical artifacts, Python 3.12.14 runtime, DEC-095 non-convergence policy, and DEC-097 all-18-cell aggregate evidence contract remain unchanged.

DEC-099 does not dispatch the workflow. Promotion, shadow, demo, broker mutation, live-order, real-money, and trading authorization remain false. Any produced result remains post-result-informed retrospective evidence and requires a later separate review.

## DEC-100 — Phase 8A EXP-045 predeclared terminal-result review

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp045-model-result-review.md` freezes the terminal-review contract for the one DEC-099-authorized EXP-045 historical model run before any result exists.

The review implementation is frozen at Git blob `eb52bca50652ad13112d8e88d776230b0da3d293`. It changes no workflow, CLI, execution-gate, protocol, training-core, artifact-runner, runtime, feature, outcome, or historical-data bytes.

DEC-100 requires the exact manual-main EXP-045 workflow identity, run attempt 1, exactly one authorization-preflight job, nine matrix jobs, one aggregate job, and artifacts restricted to the exact nine pair/timeframe result names plus the exact aggregate-result name tied to the workflow head SHA.

A successful run requires all 11 jobs to succeed, all nine cell artifacts, the aggregate artifact, and successful DEC-097 aggregate-evidence revalidation against the exact execution commit. It then stops at `SUCCESSOR_MODEL_RESULT_REVIEW_REQUIRED`.

A failed, cancelled, or timed-out first run may preserve a valid subset of pair/timeframe artifacts but cannot claim aggregate result evidence. It stops at `SUCCESSOR_MODEL_RUN_FAILURE_REVIEW_REQUIRED`.

Any rerun attempt is rejected. Replacement-run authorization, promotion, shadow, demo, broker mutation, live-order, real-money, and trading authorization remain false. EXP-045 evidence remains explicitly post-result-informed, retrospective, and not untouched OOS.

## DEC-101 — Phase 8A EXP-045 single-step operator source

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT

The approved `docs/superpowers/specs/2026-09-23-phase8a-exp045-single-step-operator.md` freezes the source-only operator that may perform the separate post-merge dispatch step already authorized by DEC-099.

DEC-101 is built after DEC-100 merged at `974127deef7ed2e5e745efc80da0336544a70a7d`, while GitHub still reported zero manual-main `phase8a-exp045-model-training` runs and the authenticated desktop runner remained offline.

The operator core is frozen at Git blob `dcb391c53182ec9775015273983d3e131248adcf`; the executable wrapper is frozen at Git blob `01d41a454df7653d58514cd1b9e129c9288e1709`.

The operator requires clean current `main`, exact `origin/main`, the expected repository remote, working GitHub CLI authentication, the exact DEC-099 execution gate, and at most one manual-main EXP-045 workflow run.

Only the missing-run state is dispatchable. It maps to exactly `gh workflow run phase8a-exp045-model-training.yml --ref main -R Dtwosam/FMP`. `advance --execute` invokes the public `next` planner twice and requires the complete second plan plus reconstructed command to equal the first before submitting the dispatch.

Once a run exists, operator dispatch authorization is consumed. Active runs are non-dispatchable. Terminal runs fetch exact run/jobs/artifacts; successful runs additionally download the exact aggregate artifact and revalidate it before the complete state is passed through the frozen DEC-100 review contract.

DEC-101 adds no alternate trigger, rerun/replacement command, workflow input, protocol/model/runtime change, promotion, shadow/demo permission, broker mutation, live-order permission, real-money permission, or trading authorization. No EXP-045 workflow is dispatched by this decision.

## DEC-102 — Phase 8A EXP-045 reviewed historical model result

**Date:** 2026-09-23
**Status:** REVIEWED AFTER THE SINGLE DEC-099-AUTHORIZED HISTORICAL RUN

Run `35911916239` executed once from `main` at `6d42a5053c5f2f696071715640dab24973a40517` with `run_attempt=1` and completed successfully. All 11 expected jobs succeeded, all nine pair/timeframe artifacts persisted, and the aggregate result artifact `10774927034` persisted with ZIP digest `sha256:8602d0b5e9bb6ad746f5cd5c96e878e631d6ed090dcd7a236c0ee00c6fadd5a5`.

The aggregate evidence fingerprint is `3e0ebac02dbba690b4c03dd10c3fdd30c5eb0d6356b881e38f9a3527f0135c55`, independently recomputed from canonical JSON. It contains all 18 exact model cells and remains labeled `RETROSPECTIVE_ALREADY_SEEN`, `prior_result_informed=true`, and `untouched_oos=false`.

The result contains 17 `NO_MODEL_CHALLENGER` cells and one selected cell: GBPUSD 5m / 240m. That selected cell failed validation (`validation_status=REJECT`) and the retrospective holdout remained locked. Therefore validation-pass count, holdout-pass count, and accepted-model-candidate count are all zero. Six cells recorded the predeclared DEC-095 logistic `FAILED_NON_CONVERGENCE` family outcome; all HGB families fitted.

DEC-102 classifies the reviewed result as `SUCCESSOR_MODEL_RESULT_REVIEWED_NO_ACCEPTED_CHALLENGER`. The one-run authorization is consumed and closed. No rerun/replacement, new fit, promotion, prospective shadow, demo order, broker mutation, live order, real-money action, or trading authorization is opened.

The machine-checkable reviewed-result source is `src/fmp/market_learning/model_successor_result_decision.py` at Git blob `d672fc334702fcea2edc4a50cd331598fb192586`. Any further model research requires a separately predeclared, explicitly post-result-informed successor experiment.

## DEC-103 — Phase 8A EXP-045 post-result diagnostic gate

**Date:** 2026-09-23
**Status:** POST-RESULT DIAGNOSTIC; NO SUCCESSOR EXECUTION AUTHORIZED

DEC-103 freezes the detailed diagnostic of all 18 EXP-045 cell results after DEC-102 reviewed run `35911916239`.

Of 108 configured family/threshold slots, 90 were evaluated; 18 logistic slots were unavailable because six cells recorded the predeclared `FAILED_NON_CONVERGENCE` family outcome. Thirty-seven evaluated variants met the 250-directional-candidate count criterion, but 36 of those failed one or more financial-sign criteria. Twenty-six evaluated variants had positive gross/mean/total financial signs, but 25 of those had fewer than 250 directional candidates. Only one variant passed the complete selection gate.

That selected variant was GBPUSD 5m / 240m HGB at confidence 0.6. It had 460 selection candidates, +5.1167 mean net pips, and +2353.7 total net pips under the 0.5-pip scenario. In validation it produced only 83 candidates, −16.8373 mean net pips, and −1397.5 total net pips. Candidate count/rate fell to about 18% of the selection level and financial sign reversed.

DEC-103 therefore records `TEMPORAL_STABILITY_FAILURE_DOMINANT` as the descriptive post-result diagnostic. It explicitly forbids retroactively lowering the 250-candidate floor or promoting the 25 low-count positive selection variants, because those identities were not validation-tested.

The machine-checkable source is `src/fmp/market_learning/model_successor_post_result_diagnostics.py` at Git blob `f1ccda0d393b851cd7c1db1399da57a920a0a7c1`.

DEC-103 opens only successor-protocol source work. EXP-045 rerun/replacement, successor result execution/model fit, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false.

## DEC-104 — Phase 8A EXP-046 temporal-stability successor protocol

**Date:** 2026-09-23
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-046 MODEL RESULT

DEC-104 opens `EXP-20260923-046` as a separately identified, explicitly post-result-informed successor after DEC-103 froze the detailed EXP-045 diagnostic.

EXP-046 preserves the exact 18 cells, 48 inputs, target, chronology, two model families/configurations, 0.50/0.60/0.70 confidence thresholds, 250-directional-candidate floor, original aggregate financial gate, validation/holdout scenarios, and logistic non-convergence policy.

The sole protocol change is a temporal-stability screen inside the existing 2021-2022 selection split. Aggregate-gate-passing variants are additionally evaluated in four non-overlapping half-year windows: 2021H1, 2021H2, 2022H1, and 2022H2. Every window must contribute at least 10% of the variant's full selection-period directional candidates and must have positive total net pips, positive mean net pips, and gross positive pips greater than absolute gross negative pips. All four windows must pass.

The 10% share is a concentration guard and does not replace or relax the aggregate 250-candidate floor. Low-count positive EXP-045 variants are not grandfathered into the successor.

The protocol source is `src/fmp/market_learning/model_successor_stability_protocol.py` at Git blob `4c8da2259f1fd6d27862a50a47a0d8108b58bc2e`.

DEC-104 authorizes no fit, historical result execution, workflow, model-family/config rescue, threshold/floor change, promotion, shadow/demo, broker mutation, live order, real-money action, or trading. A later separate decision must implement the deterministic stability-aware training core before any result-producing execution can be considered.

## DEC-105 — Phase 8A EXP-046 temporal-stability training core

**Date:** 2026-09-23
**Status:** SOURCE-ONLY; NO EXP-046 HISTORICAL RESULT AUTHORIZED

DEC-105 implements the deterministic in-memory training/evaluation core for the DEC-104 EXP-046 temporal-stability protocol.

It binds the DEC-104 merge commit `bb2ee82a7d081138e1c0847e8c406d6c3ac68589`, DEC-104 protocol blob `4c8da2259f1fd6d27862a50a47a0d8108b58bc2e`, and the DEC-096 predecessor training-core blob `3f0bc1bfa9640d08175e72cdf131bb97c94d562c`.

The core preserves the exact predecessor fit/scoring mechanics and scores the full 2021-2022 selection split once per fitted family. Only variants that pass the unchanged aggregate selection gate are evaluated in the four DEC-104 half-year stability windows. Each window slices the already-produced selection probabilities at exact chronological row indices, requires at least 10% of the full-selection directional candidates plus positive financial signs, and all four windows must pass. The aggregate 250-candidate floor is not reapplied per window.

Only variants passing both the aggregate gate and all stability windows enter the unchanged predecessor tie-break. Validation and retrospective holdout remain unchanged and no refit is allowed.

The source is `src/fmp/market_learning/model_successor_stability_training.py` at Git blob `6733d3c530fba944b9ea0c62783ed2110552e532`.

DEC-105 remains source-only. Authoritative result execution, model-fit authorization, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false.

## DEC-106 — Phase 8A EXP-046 artifact-backed runner/evidence contract

**Date:** 2026-09-23
**Status:** SOURCE-ONLY; AUTHORITATIVE EXP-046 RESULT EXECUTION CLOSED

DEC-106 freezes the artifact-backed historical-data runner and deterministic aggregate evidence contract around merged DEC-104/DEC-105.

It binds DEC-104 merge `bb2ee82a7d081138e1c0847e8c406d6c3ac68589` and protocol blob `4c8da2259f1fd6d27862a50a47a0d8108b58bc2e`, DEC-105 merge `7aa3d86f6c1fce61dd7e35d9ba9830b1fa7355b5` and training-core blob `6733d3c530fba944b9ea0c62783ed2110552e532`, plus the verified historical artifact-loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`.

The runner reuses only the exact verified EXP-044 feature/outcome/readiness artifacts. Cell-result validation requires all six family/threshold slots, exact aggregate-gate/stability/final-gate consistency, exact four DEC-104 windows for every aggregate-pass variant, recomputed candidate shares and financial-sign gates, valid chronology status chains, and canonical cell fingerprints.

Aggregate evidence requires all 18 exact cells, recomputes its canonical fingerprint, preserves exact historical source evidence identities, and records per-cell aggregate-pass/stable-pass/stability-reject variant counts.

The source is `src/fmp/market_learning/model_successor_stability_artifacts.py` at Git blob `2d8d6f82cd15f5bdb75bb384fe3efe1dc560857a`.

DEC-106 remains non-executable: the authoritative bundle raises before readiness validation or artifact loading. No CLI/workflow/dispatch, model-fit/result execution, promotion, shadow/demo, broker mutation, live order, real-money action, or trading authorization is introduced.

## DEC-107 — Phase 8A EXP-046 locked model workflow source

**Date:** 2026-09-23
**Status:** SOURCE-ONLY; EXP-046 EXECUTION AUTHORIZATION CLOSED

DEC-107 freezes the manual main-only input-free EXP-046 workflow, fail-closed CLI, pinned Python 3.12.14 runtime, and exact-source execution gate around merged DEC-104/105/106.

The workflow source is `.github/workflows/phase8a-exp046-stability-model-training.yml` at Git blob `eb4690091a92021bb0c60f153800dc6cd9111cd5`. The CLI is `scripts/phase8a_exp046_model_run.py` at blob `525be24ec365d50f6f7a390f7eb4f6ac370440b9`. The runtime requirements are frozen at blob `d25ab16056b9f5df283147d67b8f401f60ae7520`. The execution gate is `src/fmp/market_learning/model_successor_stability_execution_gate.py` at blob `d20ab76ec7ce112f6a1ca5485e78a395bacdf49b`.

The gate binds DEC-104 merge/protocol bytes, DEC-105 merge/core bytes, DEC-106 merge/artifact-runner bytes, the exact historical loader, workflow, CLI, runtime, pyproject, preprocessing, feature schema, contracts, and outcome source. Any byte drift fails closed.

The workflow preserves the exact nine pair/timeframe historical artifact identities, 60m/240m horizons, readiness artifact, partial-result upload semantics, and deterministic aggregate evidence namespace. It contains no alternate trigger and no automatic dispatch.

DEC-107 deliberately leaves model-run dispatch, authoritative result execution, protocol-result production, model fitting, promotion, shadow/demo, broker mutation, live-order, real-money, and trading authorization false. The workflow's authorization preflight therefore cannot pass under DEC-107.

A later separate decision should freeze terminal-result review before any one-run authorization is considered.

## DEC-108 — Phase 8A EXP-046 predeclared terminal-result review

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-046 HISTORICAL MODEL RESULT

DEC-108 freezes the terminal review contract before any EXP-046 historical model result and before any EXP-046 run authorization.

The review accepts only attempt-1 manual-main `phase8a-exp046-stability-model-training` runs, exactly one authorization-preflight job, nine matrix jobs, one aggregate job, and artifacts restricted to the exact nine pair/timeframe names plus the exact aggregate-result name tied to the workflow head SHA.

A successful run must have all 11 jobs succeed, all nine cell artifacts, the aggregate artifact, and successful DEC-106 aggregate-evidence revalidation against the exact execution commit. It stops at `STABILITY_MODEL_RESULT_REVIEW_REQUIRED`.

A failed, cancelled, or timed-out first run may preserve a valid subset of cell artifacts but cannot claim aggregate result evidence. It stops at `STABILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`.

The implementation is frozen at Git blob `e5ff3c6a0cb65ba14bb3bd43d5dd1d4a5a491cf6`. Any rerun attempt is rejected. Replacement-run authorization, promotion, shadow/demo, broker mutation, live-order, real-money, and trading authorization remain false. DEC-108 changes no DEC-107 execution authorization.

## DEC-109 — Phase 8A EXP-046 single historical model-run authorization

**Date:** 2026-09-23
**Status:** AUTHORIZED SOURCE; NO EXP-046 RUN DISPATCHED BY THIS DECISION

Before DEC-109 source work, GitHub reported zero manual-main `phase8a-exp046-stability-model-training` runs.

DEC-109 binds merged DEC-107 at `0ac50f49ed677ee767c02ca8c964fab569315127`, merged DEC-108 at `16ef2773a6f1bf6eae54d981ebd6f843e25d4e2a`, the pre-authorization workflow blob `eb4690091a92021bb0c60f153800dc6cd9111cd5`, CLI blob `525be24ec365d50f6f7a390f7eb4f6ac370440b9`, pre-authorization gate blob `d20ab76ec7ce112f6a1ca5485e78a395bacdf49b`, and DEC-108 review blob `e5ff3c6a0cb65ba14bb3bd43d5dd1d4a5a491cf6`.

The workflow is hardened at Git blob `3fc199f72665fad2a5d66c346645e9362b1e48e3`. Before installation or fitting it verifies its exact current run identity, lists manual-main runs for the exact EXP-046 workflow, excludes only its current run id, and fails if any prior run exists.

The authorized DEC-109 execution-gate source is frozen at Git blob `535a321967e6e9bff9c6a4d36b316ccaa0f79d4d`. It opens only the outer model-run dispatch, authoritative historical result execution, protocol-result production, and model-fit flags. The unchanged DEC-104/105/106 source-level execution locks remain false underneath the separate authorization layer.

The first manual-main attempt consumes the one-run slot whether it succeeds, fails, is cancelled, or times out. No rerun or replacement is automatically authorized. Any terminal result must use DEC-108 review.

DEC-109 does not dispatch the workflow. Promotion, prospective shadow, demo orders, broker mutation, live orders, real-money actions, and trading authorization remain false.

## DEC-110 — Phase 8A EXP-046 single-step operator source

**Date:** 2026-09-23
**Status:** SOURCE-ONLY BEFORE ANY EXP-046 HISTORICAL MODEL RESULT

DEC-110 freezes the clean-main, exact-origin, one-way EXP-046 operator that may perform the separate dispatch step already authorized by DEC-109.

DEC-110 is built after DEC-109 merged at `f134ebeac12a0e7f6d085a7fdcec291999ff30d6`, while GitHub still reported zero manual-main `phase8a-exp046-stability-model-training` runs.

The operator core is `src/fmp/market_learning/model_successor_stability_operator.py` at Git blob `c3fbe7591307592fe4e05cc783549524bddafad8`. The executable wrapper is `scripts/phase8a_exp046_operator.py` at blob `de942c5703dfddcc3b277387de98572bbe9bf562`.

Only the missing-run state is dispatchable. It maps to exactly `gh workflow run phase8a-exp046-stability-model-training.yml --ref main -R Dtwosam/FMP`. Once a run exists, operator dispatch authorization is consumed.

`advance --execute` runs the public `next` planner twice and requires the complete second plan plus reconstructed command to equal the first before submitting a dispatch. Any state drift aborts.

Terminal runs fetch exact run/jobs/artifacts and are passed through DEC-108. Successful runs additionally download and revalidate the exact DEC-106 aggregate evidence.

DEC-110 adds no alternate trigger, rerun/replacement command, protocol/model/runtime change, promotion, shadow/demo permission, broker mutation, live-order permission, real-money permission, or trading authorization. It does not dispatch EXP-046.

## DEC-111 — Phase 8A EXP-046 reviewed historical stability-model result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-109-AUTHORIZED HISTORICAL RUN

Run `35978474425` executed once from `main` at `dabafcc290d2b383531532d873c7d6c697198d5a` with `run_attempt=1` and completed successfully. All 11 expected jobs succeeded, all nine pair/timeframe artifacts persisted, and aggregate result artifact `10800835426` persisted with ZIP digest `sha256:f52ffa5d98eb196a33b97c6c09172a97c2c4ad712a41603ec7aef535825cb5d2`.

The aggregate evidence fingerprint is `499c91e4508f07bf8a637657969175fbba8e93d07236b94ded06ae884b386214`, independently recomputed from canonical JSON. It contains all 18 exact cells and remains labeled `RETROSPECTIVE_ALREADY_SEEN`, `prior_result_informed=true`, and `untouched_oos=false`.

All 18 cells end at `NO_STABLE_MODEL_CHALLENGER`. Two variants passed the unchanged predecessor aggregate selection gate and both were rejected by the DEC-104 four-window stability screen: EURUSD 5m / 60m logistic at confidence 0.6, and GBPUSD 5m / 240m HGB at confidence 0.6. No variant passed the stability screen, so validation and retrospective holdout remained locked for every cell. Five cells recorded the predeclared logistic `FAILED_NON_CONVERGENCE` family outcome; HGB fitted in all cells.

EURUSD 5m / 60m had 288 aggregate selection candidates and +3.7097 mean net pips, but only one candidate in each 2021 half-year; both 2021 windows were financially negative. GBPUSD 5m / 240m had 460 aggregate selection candidates and +5.1167 mean net pips, but only 6 and 35 candidates in 2021H1/2021H2, below the frozen 10% per-window share floor.

DEC-111 classifies the reviewed result as `STABILITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`. The one-run authorization is consumed and closed. No rerun/replacement, new fit, promotion, prospective shadow, demo order, broker mutation, live order, real-money action, or trading authorization is opened.

The machine-checkable reviewed-result source is `src/fmp/market_learning/model_successor_stability_result_decision.py` at Git blob `eb8970b21a48bb52c1ba75af64680f945abcbaa5`. Any further model research requires a separately predeclared, explicitly post-result-informed successor experiment.

## DEC-112 — Phase 8A model cross-run reproducibility audit

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; NO NEW MODEL EXECUTION AUTHORIZED

DEC-112 compares the persisted EXP-045 and EXP-046 result artifacts before any further successor protocol is designed. The two runs used byte-identical pinned runtime requirements at Git blob `d25ab16056b9f5df283147d67b8f401f60ae7520`, and DEC-105 reused the exact DEC-096 successor-training blob `3f0bc1bfa9640d08175e72cdf131bb97c94d562c`.

The HGB path is materially reproducible: all 18 model fingerprints match and all 54 thresholded candidate identity sets match across runs. Raw probability digests match only 4/18 cells, so DEC-112 distinguishes stable candidate decisions from bitwise floating-point equality.

The logistic path is not reproducible at family availability. Five cells changed between `FITTED` and `FAILED_NON_CONVERGENCE`: EURUSD 15m/240m, EURUSD 5m/60m, EURUSD 5m/240m, GBPUSD 5m/240m, and USDJPY 15m/240m. Among ten cells fitted in both runs, only 4 model fingerprints and 4 probability digests match; 29/30 thresholded candidate identity sets match.

Exactly one aggregate-gate outcome changed because of this variation: EURUSD 5m/60m logistic 0.6 was unavailable in EXP-045, but passed the aggregate gate and then failed the frozen stability screen in EXP-046. EXP-046 still had zero stability-pass variants and zero accepted model candidates, so the DEC-111 final result is unchanged.

The machine-checkable source is `src/fmp/market_learning/model_successor_cross_run_reproducibility.py` at Git blob `cf4f6ee1a7d387c3a48269a9f6aea8212dd56b1b`.

DEC-112 opens only successor-protocol source work. Logistic-family reuse for a new result-producing successor, execution of any numerical remedy, stability-screen relaxation, EXP-046 rerun/replacement, successor fit/result execution, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false.

## DEC-113 — Phase 8A EXP-047 HGB candidate-density successor protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-047 MODEL RESULT

DEC-113 opens `EXP-20260924-047` as a separately identified, explicitly post-result-informed HGB-only successor after DEC-112 froze the EXP-045/046 cross-run reproducibility audit.

EXP-047 excludes logistic regression from result-producing participation. DEC-112 established that HGB material candidate decisions reproduce across runs while logistic family availability changes in five cells. No logistic numerical remedy is introduced by DEC-113.

The predecessor HGB density diagnostic is frozen at 54 evaluated HGB variants: 23 meet the existing 250-candidate criterion, 13 have positive gross/mean/total financial signs, 12 of those positive variants remain below 250 candidates, and only one passes the full aggregate gate. That single aggregate pass failed the existing temporal-stability screen.

DEC-113 therefore preserves the exact data, 48 inputs, target, chronology, HGB configuration, 250-candidate floor, aggregate financial gate, and DEC-104 four-window temporal-stability screen. The sole research change is the candidate-density mapping.

The frozen selection candidate-budget anchors are 250, 500, and 1000. Selection rows with a unique LONG/SHORT top class are ranked by directional top-class probability descending and row identity ascending. The confidence of the budget-th row becomes the selection-derived numeric cutoff; all eligible rows at or above that cutoff are candidates, so ties may exceed the nominal budget. The exact cutoff is then applied unchanged to validation and retrospective holdout; no later-split quantile/budget recomputation is permitted.

The protocol source is `src/fmp/market_learning/model_successor_density_protocol.py` at Git blob `871936729a1090d675f6f5181ef04c8f32494394`.

DEC-113 authorizes no fit, historical result execution, workflow, dispatch, logistic reintroduction, threshold-floor/stability relaxation, promotion, shadow/demo, broker mutation, live order, real-money action, or trading. A later separate decision must implement the deterministic density-aware HGB core before any result-producing execution can be considered.

## DEC-114 — Phase 8A EXP-047 HGB candidate-density training core

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; NO EXP-047 HISTORICAL RESULT AUTHORIZED

DEC-114 implements the deterministic in-memory training/evaluation core for merged DEC-113 `EXP-20260924-047`.

It binds DEC-113 merge `060bde94835158d62d47640aaf1a77ec56b483ff`, DEC-113 protocol blob `871936729a1090d675f6f5181ef04c8f32494394`, and the unchanged base training-core blob `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`.

The core fits only hist-gradient boosting. Logistic regression is explicitly excluded with zero fit attempts.

Selection is scored once per cell. Directional rows are ranked by unique top-class directional probability descending and row identity ascending. Budget anchors 250/500/1000 derive selection cutoffs from the corresponding ranked row; all eligible rows at or above the cutoff are included, so cutoff ties may expand candidate count.

The unchanged 250-candidate aggregate floor and financial gate remain mandatory. Only aggregate passes reach the unchanged DEC-104 four-window stability screen. Validation and retrospective holdout reuse the exact selection-derived cutoff without recomputing a budget or quantile.

The implementation is `src/fmp/market_learning/model_successor_density_training.py` at Git blob `8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`.

DEC-114 remains source-only. Authoritative result execution, model-fit authorization, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false. A later separate decision must freeze an artifact-backed runner/evidence contract before any result-producing execution can be considered.

## DEC-115 — Phase 8A EXP-047 artifact-backed runner/evidence contract

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; AUTHORITATIVE EXP-047 RESULT EXECUTION CLOSED

DEC-115 freezes the artifact-backed historical-data runner and deterministic aggregate evidence contract around merged DEC-113/DEC-114.

It binds DEC-113 merge `060bde94835158d62d47640aaf1a77ec56b483ff` and protocol blob `871936729a1090d675f6f5181ef04c8f32494394`, DEC-114 merge `3e236169ae71074630ece7d78516d5e6586abe1f` and training-core blob `8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`, plus the verified historical artifact-loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`.

The runner reuses only the exact accepted historical feature/outcome/readiness artifacts. Each cell must contain exactly three HGB density variants at anchors 250/500/1000, logistic must remain `EXCLUDED_BY_DEC112_DEC113`, cutoff candidate counts and aggregate-gate status must reconcile, aggregate passes must carry the exact four temporal-stability windows, and cell fingerprints must recompute exactly.

Aggregate evidence requires all 18 exact cells and preserves the exact historical data identities, DEC-113/114 source identities, cell result fingerprints/status summaries, density/stability accounting, and all downstream authorization locks.

The source is `src/fmp/market_learning/model_successor_density_artifacts.py` at Git blob `2d3997ca97fb4568187be54914fe76e8dbf76ff5`.

DEC-115 remains non-executable: the authoritative bundle raises before readiness validation, artifact loading, or model fitting. No workflow/dispatch, model-fit/result execution, promotion, shadow/demo, broker mutation, live order, real-money action, or trading authorization is introduced.

## DEC-116 — Phase 8A EXP-047 locked model workflow source

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; EXP-047 EXECUTION AUTHORIZATION CLOSED

DEC-116 freezes the manual main-only, input-free EXP-047 workflow, CLI, pinned Python 3.12.14 numerical runtime, and fail-closed exact-source execution gate around merged DEC-113/114/115.

The workflow is `.github/workflows/phase8a-exp047-density-model-training.yml` at Git blob `7ae75dbca58266736be6a6cdf66bf58b61ec3b63`. The CLI is `scripts/phase8a_exp047_model_run.py` at blob `28941013c2cf9942a94667d58ec6b76de9d13cd2`. The runtime requirements are frozen at blob `d25ab16056b9f5df283147d67b8f401f60ae7520`. The execution gate is `src/fmp/market_learning/model_successor_density_execution_gate.py` at blob `8a581384a32c10246d123902c0cb30711456c268`.

The gate binds DEC-113 merge/protocol bytes, DEC-114 merge/core bytes, DEC-115 merge/artifact-runner bytes, the exact historical loader, workflow, CLI, runtime, pyproject, preprocessing, feature schema, contracts, and outcome source. Any byte drift fails closed.

The workflow preserves the exact nine pair/timeframe historical artifact identities, 60m/240m horizons, readiness artifact, partial-result upload semantics, and deterministic aggregate evidence namespace. It has no user inputs, alternate trigger, or automatic dispatch. Because DEC-116 is pre-authorization, it intentionally has no first-run rejection guard yet; a later authorization decision must add one before opening a one-run slot.

DEC-116 leaves model-run dispatch, authoritative result execution, protocol-result production, model fitting, promotion, shadow/demo, broker mutation, live-order, real-money, and trading authorization false. The workflow authorization preflight therefore cannot pass.

A later separate decision must predeclare terminal-result review before any one-run authorization is considered.

## DEC-117 — Phase 8A EXP-047 predeclared terminal-result review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-047 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION

DEC-117 freezes the terminal review contract before any EXP-047 historical model result and before any EXP-047 run authorization.

The reviewer accepts only attempt-1 manual-main `phase8a-exp047-density-model-training` runs, exactly one authorization-preflight job, nine matrix jobs, one aggregate job, and artifacts restricted to the exact nine pair/timeframe names plus the exact aggregate-result name tied to the workflow head SHA.

A successful run must have all 11 jobs succeed, all nine cell artifacts, the aggregate artifact, and successful DEC-115 aggregate-evidence revalidation against the exact execution commit. It stops at `DENSITY_MODEL_RESULT_REVIEW_REQUIRED`.

A failed, cancelled, or timed-out first run may preserve a valid subset of cell artifacts but cannot claim aggregate result evidence. It stops at `DENSITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`.

The implementation is frozen at Git blob `466e163edc42145b7cf2d698c48c713e0e804a95`. Any rerun attempt is rejected. Replacement-run authorization, promotion, shadow/demo, broker mutation, live-order, real-money, and trading authorization remain false. DEC-117 changes no DEC-116 execution authorization.

A later separate decision may consider at most one guarded historical EXP-047 run only after independently verifying zero prior manual-main runs and adding a first-run rejection guard.

## DEC-118 — Phase 8A EXP-047 single historical model-run authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-047 RUN DISPATCHED BY THIS DECISION

Before DEC-118 source work, GitHub reported zero manual-main `phase8a-exp047-density-model-training` runs.

DEC-118 binds merged DEC-116 at `b133424949c906d2683692e9d2ad746a33397ffc`, merged DEC-117 at `691448db95a0ab43e2ceb319b1f215c88a856613`, the pre-authorization workflow blob `7ae75dbca58266736be6a6cdf66bf58b61ec3b63`, CLI blob `28941013c2cf9942a94667d58ec6b76de9d13cd2`, pre-authorization gate blob `8a581384a32c10246d123902c0cb30711456c268`, and DEC-117 review blob `466e163edc42145b7cf2d698c48c713e0e804a95`.

The workflow is hardened at Git blob `34926f0863086e15fe8646b0d93dc3eebd1b2cc6`. Before installation or fitting it verifies its exact current run identity, lists manual-main runs for the exact EXP-047 workflow, excludes only its current run id, and fails if any prior run exists.

The authorized DEC-118 execution-gate source is frozen at Git blob `e20ee40678448df00af6885c7419506d476bcb75`. It opens only the outer model-run dispatch, authoritative historical result execution, protocol-result production, and model-fit flags. The unchanged DEC-113/114/115 source-level execution locks remain false underneath the separate authorization layer.

The first manual-main attempt consumes the one-run slot whether it succeeds, fails, is cancelled, or times out. No rerun or replacement is automatically authorized. Any terminal result must use DEC-117 review.

DEC-118 does not dispatch the workflow. Promotion, prospective shadow, demo orders, broker mutation, live orders, real-money actions, and trading authorization remain false.

## DEC-119 — Phase 8A EXP-047 single-step operator

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; NO EXP-047 RUN DISPATCHED BY THIS DECISION

DEC-119 freezes the clean-main one-way operator for the single DEC-118-authorized EXP-047 historical run.

The operator core is `src/fmp/market_learning/model_successor_density_operator.py` at Git blob `fb809b541f4b6f2805746f54c6c2073bc9aadb0a`. The executable wrapper is `scripts/phase8a_exp047_operator.py` at blob `1ac82196c1bd2cd1eb8c7edbce23deea55829ed0`. Focused tests are frozen at blob `9aa937f3edfaf7ce452db3a38e726c4e92154446`.

The operator requires clean current `main`, exact fetched `origin/main`, verified `Dtwosam/FMP` origin, and GitHub CLI authentication. It inspects only manual-main runs for `phase8a-exp047-density-model-training.yml` and fails if more than one exists.

Only the zero-run state is dispatchable. It exposes exactly `gh workflow run phase8a-exp047-density-model-training.yml --ref main -R Dtwosam/FMP`. Active and terminal states remove the dispatch command and turn result/fit authorization back off.

`advance --execute` invokes the public `next` planner twice and requires the complete second plan and reconstructed command to equal the first before dispatch.

Terminal success requires the exact aggregate artifact tied to the run head SHA, revalidates `model-result-evidence.json` through DEC-115, and routes the complete terminal state through DEC-117. Non-success routes exact partial evidence through DEC-117 without an aggregate evidence claim.

DEC-119 contains no rerun/replacement or alternate trigger and dispatches nothing by itself. The first EXP-047 attempt consumes the DEC-118 slot on any terminal outcome. Promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false.

## DEC-120 — Phase 8A EXP-047 operator gate-metadata repair

**Date:** 2026-09-24
**Status:** SOURCE-ONLY REPAIR; EXP-047 RUN SLOT UNCONSUMED

After DEC-119 merged, the local EXP-047 `next` command failed before planning because the CLI attempted to read nonexistent gate key `dec107_merged_commit`. Live GitHub still showed zero manual-main EXP-047 runs, so the DEC-118 one-run slot remained unconsumed.

DEC-120 moves gate metadata projection into the operator core through `density_operator_gate_metadata(...)`. It validates exact `DEC-116` / `DEC-118` decision identities plus the DEC-113 through DEC-117 merge/source chain and fails closed on missing or malformed metadata.

The repaired operator core is Git blob `00d4bbb4e239bc6ceba903a869a676bce816dacf`; the repaired executable wrapper is blob `0ad604619ef6f7067c494146960a092818a7b163`; focused regression tests are blob `6192b7213ed5a786e5301f8859e547a504098495`.

The regression suite explicitly forbids `dec107_merged_commit` in the public CLI and verifies missing current EXP-047 predecessor metadata fails closed.

DEC-120 changes no workflow, historical artifact, model protocol, training core, result evidence, execution authorization, terminal-review contract, or dispatch semantics. It dispatches nothing. Replacement-run, promotion, shadow/demo, broker mutation, live-order, real-money, and trading authorization remain false.

## DEC-121 — Phase 8A EXP-047 reviewed historical density-model result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-118-AUTHORIZED HISTORICAL RUN

Run `35993400007` executed once from `main` at `5c4d81c0ebc9f930b2361d54cb0245a3d8c886d2` with `run_attempt=1` and completed successfully. All 11 expected jobs succeeded, all nine pair/timeframe artifacts persisted, and aggregate result artifact `10805174168` persisted with ZIP digest `sha256:7e685380301ac82b5a64724d340cc4a3aa366e2e25098f31da0b97218135188a`.

The aggregate evidence fingerprint is `f047310749a2742d75d2e448243080d368b6a5cdf66bc119ec33e59cc192352f`, independently recomputed from canonical JSON. It contains all 18 exact cells and remains labeled `RETROSPECTIVE_ALREADY_SEEN`, `prior_result_informed=true`, and `untouched_oos=false`.

All 18 cells end at `NO_DENSITY_STABLE_MODEL_CHALLENGER`. Twelve budget variants passed the unchanged aggregate selection gate, but all 12 were rejected by the frozen four-window temporal-stability screen. No variant passed stability, so validation and retrospective holdout remained locked for every cell. No budget variant was unavailable. HGB fitted in all 18 cells and logistic remained excluded under DEC-112/DEC-113.

The 12 aggregate passes are concentrated in six cells: GBPUSD 1h/60m (1), GBPUSD 5m/240m (2), USDJPY 15m/60m (1), USDJPY 15m/240m (2), USDJPY 5m/60m (3), and USDJPY 5m/240m (3). The dominant rejection pattern is insufficient 2021 candidate share, often zero or near-zero, with additional negative later-window financial performance in some higher-density variants.

DEC-121 classifies the reviewed result as `DENSITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`. The one-run authorization is consumed and closed. No rerun/replacement, new fit, promotion, prospective shadow, demo order, broker mutation, live order, real-money action, or trading authorization is opened.

The machine-checkable reviewed-result source is `src/fmp/market_learning/model_successor_density_result_decision.py` at Git blob `1c1cffc360949609b2d4ae404a165154f3ce7b0f`. Any further model research requires a separately predeclared, explicitly post-result-informed successor diagnostic/protocol.

## DEC-122 — Phase 8A EXP-047 post-result temporal-concentration diagnostic

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; NO NEW MODEL EXECUTION AUTHORIZED

DEC-122 freezes the detailed diagnostic of the completed EXP-047 density experiment after DEC-121 reviewed run `35993400007`.

EXP-047 evaluated 54 HGB density variants with zero unavailable budgets. Twelve variants passed the aggregate financial gate and all 12 were rejected by the frozen four-window stability screen. Every aggregate pass fails the 10% per-window candidate-share criterion in at least one window. Ten of the 12 also fail one or more per-window financial-sign criteria; only two are share-only rejects.

Six aggregate-passing variants produce zero candidates across both 2021 half-years. Other passes often produce only a handful of 2021 candidates. The evidence therefore shows that broader candidate-density generation can create aggregate-financial passes but does not resolve temporal/regime concentration.

DEC-122 records `TEMPORAL_REGIME_CONCENTRATION_DOMINANT` as the descriptive post-result classification. It does not claim a causal market mechanism.

The machine-checkable source is `src/fmp/market_learning/model_successor_density_post_result_diagnostics.py` at Git blob `ceb18c634af55051d2bbd5c749a7bc5862eba470`.

DEC-122 explicitly forbids post-hoc relaxation of the 10% stability share floor, removal of the 2021 stability windows, simple widening of density anchors as a result-producing change, EXP-047 rerun/replacement, successor fit/result execution, promotion, shadow/demo, broker mutation, live order, real-money action, and trading. It opens only successor-protocol source work.

## DEC-123 — Phase 8A EXP-048 HGB fit-regime consensus successor protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-048 MODEL RESULT

DEC-123 opens `EXP-20260924-048` as a separately identified, explicitly post-result-informed HGB-only successor after DEC-122 froze temporal/regime concentration as the dominant EXP-047 failure mode.

EXP-048 preserves the exact universe, 48 inputs, target, outer chronology, HGB hyperparameters/runtime, 250/500/1000 density anchors, 250-candidate aggregate floor, aggregate financial gate, validation/holdout scenarios, and DEC-104 four-window stability screen.

The sole research change is the fit architecture. The 2015-2020 fit period is partitioned into three contiguous non-overlapping two-year windows: 2015-2016, 2017-2018, and 2019-2020. Each window fits its own HGB model with the frozen configuration.

A scored row is consensus-eligible only when all three regime models have the same unique LONG or SHORT top class. Disagreement, a NO_TRADE top class, or a top-class tie makes the row ineligible. Consensus confidence is the minimum probability assigned to the agreed directional class across the three models.

The unchanged 250/500/1000 selection density anchors are derived from consensus confidence and the exact selection-derived cutoff is reused unchanged on validation and retrospective holdout. All aggregate and temporal-stability gates remain mandatory. No fallback to a full-fit model or subset of regime models is authorized.

The protocol source is `src/fmp/market_learning/model_successor_regime_consensus_protocol.py` at Git blob `39b6b3f5adc7f34ffd8cebcf881138d6ca3eab84`.

DEC-123 authorizes no fit, historical result execution, workflow, dispatch, logistic reintroduction, stability relaxation, promotion, shadow/demo, broker mutation, live order, real-money action, or trading. A later separate decision must implement the deterministic regime-consensus core before any result-producing execution can be considered.

## DEC-124 — Phase 8A EXP-048 deterministic regime-consensus training core

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; NO EXP-048 HISTORICAL RESULT AUTHORIZED

DEC-124 implements the deterministic in-memory training/evaluation core for the DEC-123 `EXP-20260924-048` HGB fit-regime consensus protocol.

The core binds DEC-123 merge `39674f482e57922ac61fb0a6dff15a5ef621efd3`, DEC-123 protocol blob `39b6b3f5adc7f34ffd8cebcf881138d6ca3eab84`, base training-core blob `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`, and unchanged EXP-047 density-helper core blob `8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`. Source validation fails closed on byte drift.

Each cell fits exactly three HGB models on the frozen 2015-2016, 2017-2018, and 2019-2020 regime windows. Every regime must contain all three target classes and each model fits its own preprocessing state. No full-fit fallback and no logistic fit are present.

A row is consensus-eligible only when all three regime models have the same unique LONG or SHORT top class. Consensus confidence is the minimum probability assigned to that agreed class across the three models. The unchanged 250/500/1000 density anchors are derived from consensus confidence with row-id tie ordering, and cutoff ties may exceed the nominal budget.

The unchanged aggregate gate, 250-candidate floor, four-window temporal-stability screen, validation gate, and retrospective-holdout gate remain mandatory. The exact selection-derived cutoff and the same three frozen regime models are reused forward without refit or cutoff recomputation.

The implementation is `src/fmp/market_learning/model_successor_regime_consensus_training.py` at Git blob `d902f9601ef3b04e0deaead18951d43350cb09be`. Focused tests are frozen at blob `d2ce56fd55f3a2210642d568f8e3bc7a31a61271`.

DEC-124 authorizes no authoritative model fit, historical result execution, workflow, dispatch, promotion, shadow/demo, broker mutation, live order, real-money action, or trading. A later separate decision may freeze the artifact-backed EXP-048 runner/evidence contract.

## DEC-125 — Phase 8A EXP-048 regime-consensus artifact/evidence contract

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; AUTHORITATIVE EXP-048 RESULT EXECUTION CLOSED

DEC-125 freezes the artifact-backed historical-data runner and aggregate-evidence contract around merged DEC-123/DEC-124.

It binds DEC-123 merge `39674f482e57922ac61fb0a6dff15a5ef621efd3`, protocol blob `39b6b3f5adc7f34ffd8cebcf881138d6ca3eab84`, DEC-124 merge `83c5b40eebae884cda9b2b65a8494dcd63bcbb7a`, training-core blob `d902f9601ef3b04e0deaead18951d43350cb09be`, and the exact historical artifact loader.

The contract reuses only the accepted EXP-044 feature/outcome/readiness artifacts and validates all 18 exact EXP-048 cell results. It requires exactly three regime-model fits per cell with one attempt each, exact preprocessor/model fingerprints, explicit prohibition of full-fit fallback, logistic exclusion, valid consensus accounting/digests, and exact 250/500/1000 consensus-budget inventory.

DEC-125 recomputes aggregate financial-gate criteria, the four-window candidate-share/financial stability criteria, and validation/holdout financial gates. Every budget variant must reconcile to the same selection consensus-eligible row count. A selected cell must name the actual deterministic stable winner; a no-challenger result cannot hide a stable-passing variant. Forward stages must reuse the exact selected budget/cutoff.

The implementation is `src/fmp/market_learning/model_successor_regime_consensus_artifacts.py` at Git blob `b62f3ff775f30c96fa2f6f1a15256fd696ea5c2e`. Focused tests are frozen at blob `16a58dcc577952a9bf5bedf3f2e48bea38f679bc`.

DEC-125 remains non-executable: the authoritative bundle raises before readiness validation, historical artifact loading, or model fitting. No workflow/dispatch, authoritative fit/result execution, promotion, shadow/demo, broker mutation, live order, real-money action, or trading authorization is introduced.

## DEC-126 — Phase 8A EXP-048 locked model workflow source

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; EXP-048 EXECUTION AUTHORIZATION CLOSED

DEC-126 freezes the manual main-only, input-free EXP-048 workflow, model CLI, Python 3.12.14 numerical runtime, and fail-closed exact-source execution gate around merged DEC-123/124/125.

The workflow is `.github/workflows/phase8a-exp048-regime-consensus-model-training.yml` at Git blob `09d6d9fa710d18637648de23ae45968628032765`. The CLI is `scripts/phase8a_exp048_model_run.py` at blob `f4a6941512824c1d60bff98175dd2fce9353aa68`. The runtime requirements are frozen at blob `d25ab16056b9f5df283147d67b8f401f60ae7520`. The execution gate is `src/fmp/market_learning/model_successor_regime_consensus_execution_gate.py` at blob `b70e2a8854439f20b25a9549820fad9c95612390`.

The gate binds DEC-123 merge/protocol bytes, DEC-124 merge/core bytes, DEC-125 merge/artifact-runner bytes, the historical artifact loader, workflow, CLI, runtime, pyproject, preprocessing, feature schema, contracts, and outcomes source. Any byte drift fails closed.

The workflow preserves the exact nine pair/timeframe historical artifact identities, both 60m/240m horizons, exact readiness artifact, partial-result upload semantics, and deterministic EXP-048 aggregate-evidence namespace. It has no inputs, alternate trigger, automatic dispatch, or prior-run guard.

DEC-126 is intentionally pre-authorization: model-run dispatch, authoritative result execution, protocol-result production, and model fitting remain false, so the preflight cannot pass. A later authorization decision must add the first-run guard only after terminal review is predeclared and zero prior runs are independently verified.

Promotion, shadow/demo, broker mutation, live-order, real-money, and trading authorization remain false.

## DEC-127 — Phase 8A EXP-048 predeclared terminal-result review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-048 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION

DEC-127 freezes the terminal review contract before any EXP-048 historical result and before any run authorization.

Only attempt-1 manual-main `phase8a-exp048-regime-consensus-model-training` runs are reviewable. Exactly one authorization-preflight job, nine matrix jobs, one aggregate job, and artifacts restricted to the exact nine pair/timeframe names plus the exact aggregate-result name tied to the workflow head SHA are accepted.

A successful run must have all 11 jobs succeed, all nine cell artifacts, the aggregate artifact, and successful DEC-125 aggregate-evidence revalidation against the execution commit. It stops at `REGIME_CONSENSUS_MODEL_RESULT_REVIEW_REQUIRED`.

A failed, cancelled, or timed-out first run may preserve a valid subset of cell artifacts but cannot claim aggregate result evidence. It stops at `REGIME_CONSENSUS_MODEL_RUN_FAILURE_REVIEW_REQUIRED`.

The implementation is frozen at Git blob `0cd943cb4bb8780a6adfab02b0743c8415dcd5fe`. Any rerun attempt is rejected. Replacement-run authorization, promotion, shadow/demo, broker mutation, live-order, real-money, and trading authorization remain false. DEC-127 changes no DEC-126 execution authorization.

## DEC-128 — Phase 8A EXP-048 single historical model-run authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-048 RUN DISPATCHED BY THIS DECISION

DEC-128 independently verifies zero prior manual-main `phase8a-exp048-regime-consensus-model-training` runs after DEC-127 merged, hardens the workflow with a first-run rejection guard, and opens at most one outer historical result-producing attempt.

The guard verifies the current run's exact workflow name/path, `workflow_dispatch` event, and `main` branch, lists exact manual-main EXP-048 runs, excludes only the current `GITHUB_RUN_ID`, and fails if any prior run exists. The hardened workflow blob is `89a2c78af2c3d0925d7c8a2773af9291caacd95d`.

The authorization gate binds DEC-126 merge `e2713ab33648901d42f9a9e1c4b8e7f0ff7920a6`, pre-authorization workflow blob `09d6d9fa710d18637648de23ae45968628032765`, CLI blob `f4a6941512824c1d60bff98175dd2fce9353aa68`, pre-authorization gate blob `b70e2a8854439f20b25a9549820fad9c95612390`, DEC-127 merge `589782a92f9f1db2008bff99065cb070017311ca`, and DEC-127 review blob `0cd943cb4bb8780a6adfab02b0743c8415dcd5fe`.

The authorized gate source is Git blob `3312667537eedfc2cd41d1ec91c877e1b05770f9` and records `REGIME_CONSENSUS_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-128"`. Only the outer dispatch/result/protocol-result/model-fit flags are true; the underlying DEC-123/124/125 source-level execution locks remain false.

The first manual-main attempt consumes the slot on success, failure, cancellation, or timeout. No rerun/replacement is authorized. DEC-128 itself dispatches nothing. Promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false.

## DEC-129 — Phase 8A EXP-048 single-step operator

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; NO EXP-048 RUN DISPATCHED BY THIS DECISION

DEC-129 freezes the clean-main one-way operator for the single DEC-128-authorized EXP-048 historical run.

The operator core is `src/fmp/market_learning/model_successor_regime_consensus_operator.py` at Git blob `86789ed022c1cf3460ac724b8444f4464c6c464f`. The executable wrapper is `scripts/phase8a_exp048_operator.py` at blob `9b6c7e5f0952f0621543b9a561987cbfc00ef2b0`. Focused tests are frozen at blob `3ee1a9d15f67c17ef02e9890d8d3750907d0b6e8`.

The operator requires clean current `main`, exact fetched `origin/main`, verified `Dtwosam/FMP` origin, and GitHub CLI authentication. It inspects only manual-main runs for `phase8a-exp048-regime-consensus-model-training.yml` and fails if more than one exists.

Only the zero-run state is dispatchable. It exposes exactly `gh workflow run phase8a-exp048-regime-consensus-model-training.yml --ref main -R Dtwosam/FMP`. Active and terminal states remove the dispatch command and turn result/fit authorization back off.

The operator validates exact DEC-126/DEC-128 gate identities plus the DEC-123 through DEC-127 merge/source chain, avoiding the stale metadata-key class previously repaired under DEC-120.

`advance --execute` invokes the public `next` planner twice and requires the complete second plan and reconstructed command to equal the first before dispatch.

Terminal success requires the exact aggregate artifact tied to the run head SHA, revalidates `model-result-evidence.json` through DEC-125, and routes the complete terminal state through DEC-127. Non-success routes exact partial evidence through DEC-127 without an aggregate evidence claim.

DEC-129 contains no rerun/replacement or alternate trigger and dispatches nothing by itself. The first EXP-048 attempt consumes the DEC-128 slot on any terminal outcome. Promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false.

## DEC-130 — Phase 8A EXP-048 reviewed historical regime-consensus result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-128-AUTHORIZED HISTORICAL RUN

Run `36006524422` executed once from `main` at `60b2796a64f0a4f7f95660d45ef7ab7fac519e9c` with `run_attempt=1` and completed successfully. All 11 expected jobs succeeded, all nine pair/timeframe artifacts persisted, and aggregate result artifact `10811660325` persisted with ZIP digest `sha256:ea6f228baac35b7a858942452b8fb4fa44d312387a1c5812d164b5a954170d9f`.

The aggregate evidence fingerprint is `acd3a9d7708c345b05082026de9eecc515abb9090a901126034e91173eb30647`, independently recomputed from canonical JSON. It contains all 18 exact cells and remains labeled `RETROSPECTIVE_ALREADY_SEEN`, `prior_result_informed=true`, and `untouched_oos=false`.

All 18 cells end at `NO_REGIME_CONSENSUS_STABLE_MODEL_CHALLENGER`. Seventeen density-budget variants pass the unchanged aggregate selection gate and all 17 are rejected by the frozen temporal-stability screen. No variant passes stability, so validation and retrospective holdout remain locked for every cell. No budget variant is unavailable. The 18 cells contain 431,086 consensus-eligible selection rows in aggregate.

Aggregate passes occur in seven cells: EURUSD 15m/240m (3), EURUSD 1h/240m (3), EURUSD 5m/240m (2), GBPUSD 1h/60m (1), GBPUSD 5m/60m (2), USDJPY 5m/60m (3), and USDJPY 5m/240m (3). Every aggregate pass still fails the unchanged temporal-stability screen.

DEC-130 classifies the reviewed result as `REGIME_CONSENSUS_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`. The one-run authorization is consumed and closed. No rerun/replacement, new fit, promotion, prospective shadow, demo order, broker mutation, live order, real-money action, or trading authorization is opened.

The machine-checkable reviewed-result source is `src/fmp/market_learning/model_successor_regime_consensus_result_decision.py` at Git blob `0556da8c036a55ba3b94d933f67f439eb306f9c2`. Any further model research requires a separately predeclared, explicitly post-result-informed successor diagnostic/protocol.

## DEC-131 — Phase 8A EXP-048 post-result stability diagnostic

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; NO NEW MODEL EXECUTION AUTHORIZED

DEC-131 freezes the detailed diagnostic of the completed EXP-048 regime-consensus experiment after DEC-130 reviewed run `36006524422`.

EXP-048 evaluates 54 variants, with 17 aggregate selection passes and zero stability passes. All 17 aggregate passes fail at least one per-window financial-sign criterion. Thirteen also fail the frozen 10% candidate-share requirement; four satisfy candidate-share stability in every window but still fail a financial window. No aggregate pass fails only the share rule.

No aggregate-passing variant has zero candidates across both 2021 half-years, although five have zero candidates in one 2021 half-year. The observed failure therefore shifts descriptively away from the most extreme inactivity pattern seen under EXP-047 and toward per-window financial instability.

DEC-131 records `WINDOW_FINANCIAL_INSTABILITY_DOMINANT` as the descriptive post-result classification. It does not claim a causal market mechanism.

The machine-checkable source is `src/fmp/market_learning/model_successor_regime_consensus_post_result_diagnostics.py` at Git blob `165ab1e0e10a9fb6453ad0880ea1df97d0a35fa8`.

DEC-131 explicitly forbids post-hoc relaxation of candidate-share or financial stability rules, removal of the 2021 windows, EXP-048 rerun/replacement, successor fit/result execution, promotion, shadow/demo, broker mutation, live order, real-money action, and trading. It opens only successor-protocol source work.

## DEC-132 — Phase 8A EXP-049 HGB regime-utility successor protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-049 MODEL RESULT

DEC-132 opens `EXP-20260924-049` as a separately identified, explicitly post-result-informed HGB-only successor after DEC-131 froze `WINDOW_FINANCIAL_INSTABILITY_DOMINANT` as the descriptive EXP-048 failure classification.

EXP-049 preserves the exact three-pair / three-timeframe / two-horizon universe, 48 feature inputs, outer chronology, three disjoint EXP-048 fit-regime windows, HGB structural settings/runtime, 250/500/1000 candidate-budget anchors, 250-candidate aggregate floor, aggregate financial gate, four half-year stability windows, 10% per-window candidate-share floor, per-window financial signs, validation/holdout scenarios, and no-refit forward rule.

The sole research change is the model objective. Each fit regime now fits two `HistGradientBoostingRegressor` models on the already materialized 0.5-pip cost-aware outcomes `long_net_pips_0p5` and `short_net_pips_0p5`, for exactly six regressors per cell. Structural HGB settings remain frozen; squared-error loss is used for the regression objective.

Within a regime, a row receives a directional vote only when one predicted directional utility is uniquely larger and strictly positive. A row is eligible only when all three fit regimes vote for the same LONG or SHORT direction. Its robust-utility score is the minimum predicted net pips for that agreed direction across the three regimes.

The unchanged 250/500/1000 budgets derive one numeric robust-utility cutoff from the selection split. Ties may exceed the nominal budget. The exact selection-derived cutoff is reused unchanged on validation and retrospective holdout. No half-year-specific cutoff, utility recalibration, gate relaxation, 2021-window removal, density rescue, classifier fallback, or logistic reintroduction is authorized.

The protocol source is `src/fmp/market_learning/model_successor_regime_utility_protocol.py` at Git blob `ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac`. Focused tests are `tests/test_phase8a_exp049_regime_utility_protocol.py` at Git blob `647523e86bcf7d54755ea745866ab7c66c89dc6d`.

DEC-132 authorizes no model fit, historical result execution, workflow, dispatch, promotion, shadow/demo, broker mutation, live order, real-money action, or trading. A later separate decision must implement and bind the deterministic EXP-049 training/evaluation core before any result-producing execution can be considered.

## DEC-133 — Phase 8A EXP-049 deterministic regime-utility training core

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NO AUTHORITATIVE EXP-049 FIT

DEC-133 implements the deterministic in-memory training/evaluation core for the DEC-132 protocol and binds the exact DEC-132 merge `d17326eebf6b456211225d7bad3a182a0307b707`, protocol blob `ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac`, base EXP-044 training helper blob `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`, and density/stability helper blob `8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`.

For every cell, the core rebuilds the exact three fit-regime windows and fits exactly two `HistGradientBoostingRegressor` models per regime on `long_net_pips_0p5` and `short_net_pips_0p5`. Each target receives regime-local median preprocessing, finite-target checks, deterministic preprocessor/model fingerprints, and row-bound prediction digests.

Scoring implements the frozen DEC-132 rule exactly: a regime votes LONG or SHORT only when that predicted utility is uniquely larger and strictly positive; all three regimes must vote the same direction; robust utility is the minimum agreed-direction prediction across regimes. The 250/500/1000 selection cutoffs rank robust utility deterministically, and ties may exceed the nominal budget.

Realized selection still must pass the unchanged 0.5-pip aggregate gate and all four unchanged temporal-stability windows before any variant is selected. Validation reuses the exact six fitted regressors and exact selection-derived numeric cutoff without refit/recalibration. Retrospective holdout remains locked unless validation passes.

The training core is `src/fmp/market_learning/model_successor_regime_utility_training.py` at Git blob `e1018b20210b7bb8d666071d8eb878aba5899111`. Focused tests are `tests/test_phase8a_exp049_regime_utility_training.py` at Git blob `0606d8208b8c7edac40f1073e5b5e8248dfc107b`.

DEC-133 adds no workflow, dispatch path, authoritative historical fit, result execution, promotion, shadow/demo, broker mutation, live order, real-money action, or trading authorization. A later separate decision must freeze an artifact-backed runner/evidence contract before any historical execution can be considered.

## DEC-134 — Phase 8A EXP-049 artifact-backed result-evidence contract

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-134 freezes the artifact-backed runner/evidence contract for `EXP-20260924-049`. It binds the exact DEC-132 protocol, merged DEC-133 training core `a6420e35a9219c81e65c5179843488f94b6668d3`, DEC-133 training-core Git blob `e1018b20210b7bb8d666071d8eb878aba5899111`, accepted historical artifact loader Git blob `27c0848d16722a22b4762f5842396c2aebc92bec`, and the existing authoritative feature/outcome/readiness identities.

The contract requires complete 18-cell result evidence and exactly 108 regime/target regressors. It independently validates each target summary and fit fingerprint, nested regime/target prediction digests, unanimous positive-utility consensus accounting, the exact 250/500/1000 budget semantics, recomputed aggregate financial gates, all four unchanged temporal-stability windows, selection/validation/holdout status chains, and both cell-level and aggregate evidence fingerprints.

A no-challenger result cannot hide a stable variant. Full-fit, HGB-classifier, and logistic fallbacks remain forbidden. Any unlocked validation or retrospective-holdout block must preserve the exact selection-derived positive utility cutoff and internally recomputable financial gate evidence.

The artifact/evidence source is `src/fmp/market_learning/model_successor_regime_utility_artifacts.py` at Git blob `6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13`. Focused tests are `tests/test_phase8a_exp049_regime_utility_artifacts.py` at Git blob `0c7c746ee0e7365e5e4dd0fef96cc4c3eac7418a`.

The authoritative bundle checks `AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED` before loading readiness or historical feature/outcome artifacts. DEC-134 keeps that flag false, keeps authoritative model fit false, and opens no workflow, dispatch, promotion, shadow/demo, broker mutation, live order, real-money action, or trading authorization. A later separate decision may freeze a manual-main workflow/CLI while keeping dispatch closed until terminal review and one-run authorization are separately predeclared.

## DEC-135 — Phase 8A EXP-049 locked model workflow source

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; EXP-049 EXECUTION AUTHORIZATION CLOSED

DEC-135 freezes the manual main-only, input-free EXP-049 workflow, model CLI, Python 3.12.14 numerical runtime, and fail-closed exact-source execution gate around merged DEC-132/DEC-133/DEC-134.

The workflow is `.github/workflows/phase8a-exp049-regime-utility-model-training.yml` at Git blob `955152835ec1cedf39d6d31e54d6028a7953fab5`. The CLI is `scripts/phase8a_exp049_model_run.py` at blob `cba5ece4eda8e02a7ca07a780d8caa69a239e094`. Runtime requirements are `requirements/exp049-model-run.txt` at blob `d25ab16056b9f5df283147d67b8f401f60ae7520`. The execution gate is `src/fmp/market_learning/model_successor_regime_utility_execution_gate.py` at Git blob `9d2ffc670a1572febb0e4a29bfda426f8252e5ee`.

The gate binds DEC-132 merge/protocol bytes, DEC-133 merge/core bytes, DEC-134 merge/artifact-runner bytes, the accepted historical artifact loader, workflow, CLI, runtime requirements, pyproject, preprocessing, feature schema, market-learning contracts, and outcome schema. Any bound byte drift fails closed.

The workflow preserves the exact nine accepted pair/timeframe artifact identities, both 60m/240m horizons, exact readiness artifact, partial-result upload semantics, and deterministic EXP-049 aggregate-evidence namespace. It has no inputs, schedule, pull-request trigger, alternate trigger, or first-run guard.

DEC-135 is intentionally pre-authorization: model-run dispatch, authoritative result execution, protocol-result production, and model fitting remain false, so the preflight cannot pass before readiness loading, historical artifact loading, or fitting. A first-run guard may only be introduced by a later authorization decision after terminal review is separately predeclared and zero prior manual-main EXP-049 runs are independently verified.

Focused tests are `tests/test_phase8a_exp049_model_workflow.py` at Git blob `906474f199d595579b29c96b683299fa269c7e8d`. Promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false.

## DEC-136 — Phase 8A EXP-049 predeclared terminal-result review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-049 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION

DEC-136 freezes the exact terminal review contract before any EXP-049 historical result and before any run authorization.

Only attempt-1 manual-main `phase8a-exp049-regime-utility-model-training` runs are reviewable. Exactly one authorization-preflight job, nine matrix jobs, one aggregate job, and artifacts restricted to the exact nine pair/timeframe names plus the exact aggregate-result name tied to the workflow head SHA are accepted.

A successful run must have all 11 jobs succeed, all nine cell artifacts, the aggregate artifact, and successful DEC-134 aggregate-evidence revalidation against the execution commit. It stops at `REGIME_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`.

A failed, cancelled, or timed-out first run may preserve a valid subset of cell artifacts but cannot claim aggregate result evidence or an aggregate artifact. It stops at `REGIME_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`.

The review binds DEC-135 merge `0fe11d26fd74355e39f7379f3eeba869d848271c`, workflow blob `955152835ec1cedf39d6d31e54d6028a7953fab5`, CLI blob `cba5ece4eda8e02a7ca07a780d8caa69a239e094`, and execution-gate blob `9d2ffc670a1572febb0e4a29bfda426f8252e5ee`.

The implementation is `src/fmp/market_learning/model_successor_regime_utility_result_review.py` at Git blob `1c48405fa8b754ee8d6756dac701332ac72816bd`. Focused tests are frozen at blob `7d072b0ced240afe33135e6fde689bae511fbc54`.

Any rerun attempt is rejected. Replacement-run authorization, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false. DEC-136 changes no DEC-135 execution authorization. A later separate decision may verify zero prior runs, add a first-run guard, and authorize at most one outer historical attempt without dispatching it.

## DEC-137 — Phase 8A EXP-049 single historical model-run authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-049 RUN DISPATCHED BY THIS DECISION

DEC-137 independently verifies zero prior manual-main `phase8a-exp049-regime-utility-model-training` runs after DEC-136 merged. The latest 30 repository Actions runs extended back to 15:41:59Z, before the workflow first entered `main` with DEC-135 at 16:06:45Z, and none matched the exact EXP-049 workflow name/path.

It binds DEC-135 merge `0fe11d26fd74355e39f7379f3eeba869d848271c`, pre-authorization workflow blob `955152835ec1cedf39d6d31e54d6028a7953fab5`, CLI blob `cba5ece4eda8e02a7ca07a780d8caa69a239e094`, pre-authorization gate blob `9d2ffc670a1572febb0e4a29bfda426f8252e5ee`, DEC-136 merge `3f7f6e00ecd8580266d5728a516bff3b700ade0a`, and DEC-136 review blob `1c48405fa8b754ee8d6756dac701332ac72816bd`.

The workflow is hardened with a first-run rejection guard before runtime installation or model fitting. It verifies the current run's exact workflow name/path, `workflow_dispatch` event, and `main` branch, lists exact manual-main EXP-049 runs, excludes only the current `GITHUB_RUN_ID`, and fails if any prior run exists. The hardened workflow blob is `2d012acdea55f363938156844ae7a74899a2bd40`.

The authorized outer execution gate is `src/fmp/market_learning/model_successor_regime_utility_execution_gate.py` at Git blob `dda941efb7542dbc4fcaa890154df4f39f006f07` and records `REGIME_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-137"`. Only the outer dispatch/result/protocol-result/model-fit flags are true; underlying DEC-132/DEC-133/DEC-134 source-level execution and fit locks remain false and are validated as frozen dependencies.

The first manual-main EXP-049 attempt consumes the slot on success, failure, cancellation, or timeout. No rerun/replacement is authorized. DEC-137 itself dispatches nothing. Promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false. A later separate decision must freeze a clean-main one-way operator before any dispatch.

## DEC-138 — Phase 8A EXP-049 clean-main single-step operator

**Date:** 2026-09-24
**Status:** SOURCE-ONLY OPERATOR; NO EXP-049 RUN DISPATCHED BY THIS DECISION

DEC-138 freezes the one-way operator around the single historical EXP-049 attempt authorized by DEC-137.

The operator core is `src/fmp/market_learning/model_successor_regime_utility_operator.py` at Git blob `f523ff3e2353c0c347e136f9a998a2b1434a561b`. The public CLI is `scripts/phase8a_exp049_operator.py` at blob `9f1c3881e45322e5dda267bc7adaff1c86317ec2`. Focused tests are `tests/test_phase8a_exp049_operator.py` at blob `ec73bb478c62966edfeb066d43b871511642574b`.

The operator binds DEC-137 merge `33227b25cd1a888c3e0c7db3a50bd0cb61f5aad6`, requires a clean local `main` exactly matching fetched `origin/main`, verifies the `Dtwosam/FMP` remote, and reads only the exact manual-main `phase8a-exp049-regime-utility-model-training` workflow state.

The state machine is one-way. Only a missing run may expose the exact dispatch command. An active or terminal run exposes no dispatch path, and more than one manual-main run fails closed. The public CLI is read-only by default; `advance --execute` re-runs the public `next` planner and refuses dispatch if live state changes between planning and execution.

Terminal success requires the exact non-expired aggregate artifact tied to the run head SHA, loads the DEC-134 aggregate evidence, and routes the full terminal evidence through DEC-136. Non-success routes through DEC-136 without aggregate evidence. No rerun or replacement path exists.

DEC-138 itself dispatches nothing. Replacement-run authorization, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false. After merge and normal regression gates, the operator may be inspected from clean current `main`; only an exact zero-run read-only plan may expose the single DEC-137-authorized dispatch.

## DEC-139 — Phase 8A EXP-049 reviewed historical regime-utility result

**Date:** 2026-09-24
**Status:** REVIEWED / EXP-049 HISTORICAL RUN CLOSED

DEC-139 reviews the single DEC-137-authorized EXP-049 historical model run `36029925264`. The run completed successfully on attempt 1 at execution commit `eeb735bca7d38c3246f22a9606dfafe9c3df8279`; all 11 required jobs succeeded and all nine pair/timeframe cell artifacts plus the aggregate artifact were persisted.

The reviewed aggregate artifact is id `10822530555`, name `exp049-regime-utility-model-result-evidence-eeb735bca7d38c3246f22a9606dfafe9c3df8279-from-feature-35867307338-outcome-35876715434`, with GitHub artifact digest `sha256:2cafb18dc1130f4fe0bf229b7df1deda24bfb7b1295f9a6ad688c1f5c1fd407c`. The downloaded ZIP independently hashes to the same value and contains exactly one `model-result-evidence.json`.

DEC-134 evidence revalidation succeeds. The canonical evidence fingerprint is `29ecbb5bf3ce00f35c825e977d9b3fff1777e165ce9bef311fefcb7bfbdb091e`. All 18 cells and all 108 regime/target regressors verify. Eight regime-utility density variants pass the unchanged aggregate selection gate, zero pass the frozen temporal-stability gate, all 18 cells terminate at `NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER`, and validation/retrospective holdout remain locked. Thirty-one budget variants are unavailable for insufficient utility rows and the verified utility-eligible selection-row total is 14,158.

The result-decision source is `src/fmp/market_learning/model_successor_regime_utility_result_decision.py` at Git blob `dce13838f32fbb8aa0e403c550b669f778dd0742`; focused tests are `tests/test_phase8a_exp049_model_result_decision.py` at blob `f47c22ba6199ff2a7b7be11dc4ebdacca9bc3652`; the reviewed-result record is `docs/superpowers/specs/2026-09-24-phase8a-exp049-reviewed-model-result.md` at blob `c744f3ad11286220e9574553aa81e54373574cb3`.

The DEC-137 one-run slot is consumed. Model-run dispatch, replacement-run authorization, authoritative result execution, protocol-result production, model fitting, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization are all closed. No second EXP-049 run is authorized. Any post-result diagnostic or successor protocol requires a later separate decision and may not alter this reviewed evidence.

## DEC-140 — Phase 8A EXP-049 post-result regime-utility diagnostic

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; SUCCESSOR SOURCE WORK ONLY

DEC-140 freezes the post-result diagnostic over the immutable DEC-139 / EXP-049 evidence before any successor protocol is written. It performs no new model fit, changes no reviewed gate, and authorizes no historical result execution.

The source binding is DEC-139, workflow run `36029925264`, execution commit `eeb735bca7d38c3246f22a9606dfafe9c3df8279`, evidence fingerprint `29ecbb5bf3ce00f35c825e977d9b3fff1777e165ce9bef311fefcb7bfbdb091e`, DEC-139 merge `3535e47d2224802eadf154330ef57519c8ea674c`, and reviewed-result source blob `dce13838f32fbb8aa0e403c550b669f778dd0742`.

Of the 54 predeclared budget variants, 31 are unavailable because the frozen positive regime-utility consensus produces fewer utility-eligible rows than the requested budget. Twenty-three variants are available; eight pass the unchanged aggregate selection gate and 15 reject there. Thirteen of 18 cells have at least one unavailable budget and seven cells have all three budgets unavailable.

All eight aggregate passes occur at the 240-minute horizon across four cells: EURUSD 1h, GBPUSD 5m, USDJPY 15m, and USDJPY 5m. All eight fail the frozen 10% candidate-share requirement in both 2021 half-year windows, and all eight also fail at least one per-window financial-sign requirement. Six fail financial signs in 2022 H2. Two have zero candidates in at least one 2021 half, and USDJPY 5m / 240m / budget 250 has zero candidates in both 2021 halves.

DEC-140 records the descriptive diagnostic classification `UTILITY_COVERAGE_AND_DUAL_TEMPORAL_STABILITY_LIMITED`. This is not a causal market claim. It records that positive-utility coverage limits many budget variants and that every aggregate-financial pass still fails both share and financial temporal stability.

The diagnostic source is `src/fmp/market_learning/model_successor_regime_utility_post_result_diagnostics.py` at Git blob `e286be2574d4cee60322a4b65213af76ab34b381`. Focused tests are `tests/test_phase8a_exp049_post_result_diagnostics.py` at blob `6fa290bacab4363ab823771f6ca04aa19f8095be`. The diagnostic spec is `docs/superpowers/specs/2026-09-24-phase8a-exp049-post-result-diagnostics.md` at blob `ea4a9e3a9ef962aecb0d6e88857dc5b8e65527ff`.

DEC-140 does not authorize lowering the positive-utility rule, adding smaller budget anchors as a result-producing rescue, relaxing candidate-share or financial stability, removing the 2021 windows, rerunning or replacing EXP-049, successor fitting/result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. It opens only separately frozen successor-protocol source work.

## DEC-141 — Phase 8A EXP-050 temporal-jackknife regime-utility successor protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NO EXP-050 MODEL EXECUTION AUTHORIZED

DEC-141 opens `EXP-20260924-050` as a post-result-informed successor to DEC-139/DEC-140. It is bound to EXP-049 run `36029925264`, execution commit `eeb735bca7d38c3246f22a9606dfafe9c3df8279`, evidence fingerprint `29ecbb5bf3ce00f35c825e977d9b3fff1777e165ce9bef311fefcb7bfbdb091e`, DEC-140 merge `04f06deb4d68f9936438eec20dbb9610683bbc2e`, DEC-140 diagnostic blob `e286be2574d4cee60322a4b65213af76ab34b381`, and DEC-139 reviewed-result blob `dce13838f32fbb8aa0e403c550b669f778dd0742`.

DEC-140 recorded two simultaneous limitations: 31 of 54 predeclared budget variants were unavailable for insufficient positive regime-utility consensus rows, while all eight aggregate-financial passes failed both candidate-share and financial temporal stability. DEC-141 does not lower the positive-utility threshold, add smaller budget anchors, weaken stability, remove a 2021 window, or authorize an EXP-049 rerun.

The sole EXP-050 research change is the utility-regressor fit-view construction. The three frozen predecessor two-year regimes remain unchanged, but each of three deterministic temporal-jackknife views fits on the union of exactly two regimes while leaving the third entirely out. Each view therefore uses four fit years; each predecessor regime is excluded by one view and included by two. The middle view intentionally unions 2015-2016 with 2019-2020 and does not interpolate or use rows from the excluded 2017-2018 block.

Each view fits exactly the same two cost-aware HGB regressors as EXP-049: LONG and SHORT net pips at 0.5-pip adverse slippage. Structural HGB configuration is unchanged. The model inventory remains six regressors per cell.

Eligibility remains fail-closed and unanimous. Each view must choose the unique higher LONG/SHORT prediction and that predicted utility must be greater than zero. All three views must choose the same direction. Robust utility remains the minimum predicted net pips for the agreed direction across the three views. Majority voting, view weighting, fit-view fallback, full-fit fallback, classifier fallback, logistic reintroduction, and utility-threshold relaxation are not authorized.

Candidate-budget anchors remain 250/500/1000. Aggregate minimum count and financial signs, the four half-year temporal-stability windows, the 10% per-window share floor, all per-window financial signs, validation and retrospective-holdout scenarios, selection-derived cutoff reuse, and no-refit semantics remain unchanged.

The protocol source is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_protocol.py` at Git blob `b41b817b03aa0cc03a9d893227caa399b46d3cf8`. Focused tests are `tests/test_phase8a_exp050_temporal_jackknife_utility_protocol.py` at blob `f458891e6160bb4e3af6c7a4b82b69b37771efe7`. The detailed spec is `docs/superpowers/specs/2026-09-24-phase8a-exp050-temporal-jackknife-utility-protocol.md`.

DEC-141 keeps model-protocol result production, model fit, historical result execution, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization false. A later separate decision may implement only the deterministic in-memory EXP-050 training/evaluation core against this exact protocol source.

## DEC-142 — Phase 8A EXP-050 temporal-jackknife utility training core

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NO AUTHORITATIVE EXP-050 FIT

DEC-142 implements the deterministic in-memory EXP-050 training/evaluation core against the exact DEC-141 protocol. It binds DEC-141 merge `4729da0e769f76f44b97ff6349ee25c5b7c0f5c7`, DEC-141 protocol blob `b41b817b03aa0cc03a9d893227caa399b46d3cf8`, and predecessor EXP-049 training-core blob `e1018b20210b7bb8d666071d8eb878aba5899111`.

The implementation intentionally reuses the exact DEC-133 utility scoring, cutoff, realized-financial, temporal-stability, and selection-tie-break helpers under that predecessor-core blob binding. New code is limited to the DEC-141 fit-view topology, view-frame assembly, view-aware scoring/digests, and EXP-050 result identity.

The core reconstructs the three predecessor two-year fit regimes and builds exactly three leave-one-regime-out views. Each view concatenates exactly two frozen regime frames, excludes the third, verifies row-count accounting, and fits the same LONG/SHORT 0.5-pip HGB regressors. There remain exactly six regressors per cell.

Selection still requires unanimous positive utility across all three views and uses minimum agreed-direction predicted utility as the robust score. Candidate budgets remain 250/500/1000; aggregate and four-window temporal-stability gates remain unchanged; the exact selection-derived cutoff is reused unchanged in validation and retrospective holdout.

The training core is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_training.py` at Git blob `ec97a9941af052d6e223e4bafab9a9989ec57ff0`. Focused tests are `tests/test_phase8a_exp050_temporal_jackknife_utility_training.py` at blob `f7066a775659b1b391b0e29af13601cff015ebb5`. The detailed spec is `docs/superpowers/specs/2026-09-24-phase8a-exp050-temporal-jackknife-utility-training-core.md`.

DEC-142 keeps authoritative EXP-050 model fit/result execution, workflow execution, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization false. A later separate decision may freeze an artifact-backed runner/evidence contract against this exact training-core blob.

## DEC-143 — Phase 8A EXP-050 artifact-backed result-evidence contract

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-143 freezes the artifact-backed runner/evidence contract for `EXP-20260924-050`. It binds DEC-141 protocol source, DEC-142 training core, the accepted historical feature/outcome/readiness identities, the accepted historical artifact loader, and the generic DEC-134 financial/stability validation helpers under exact Git-blob bindings.

Exact source identities include DEC-142 merge `fa6fd14a880a84a44795efe4099679ed0f642497`, DEC-142 training-core blob `ec97a9941af052d6e223e4bafab9a9989ec57ff0`, DEC-141 protocol blob `b41b817b03aa0cc03a9d893227caa399b46d3cf8`, predecessor EXP-049 training-core blob `e1018b20210b7bb8d666071d8eb878aba5899111`, DEC-134 artifact-helper blob `6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13`, and accepted historical loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`.

The contract requires complete 18-cell aggregate evidence and exactly 108 jackknife-view/target regressors. It independently validates exact included/excluded regime identities for all three views, target summaries and fit fingerprints, complete view/target prediction digests, unanimous positive-utility consensus accounting, exact 250/500/1000 budget semantics, realized aggregate financial gates, temporal-stability evidence, selection/validation/holdout status chains, and both cell-level and aggregate canonical fingerprints.

A no-challenger result cannot hide a stable variant. Full-fit fallback, view-weight search, view fallback, HGB classifier fallback, and logistic fallback remain forbidden or excluded.

The authoritative bundle checks `AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED` before readiness validation or historical artifact loading. DEC-143 keeps that flag false and keeps authoritative model fit false.

The artifact/evidence source is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_artifacts.py` at Git blob `60076ccb45b3468bce68f88f667225e0b5662d92`. Focused tests are `tests/test_phase8a_exp050_temporal_jackknife_utility_artifacts.py` at blob `2247d07528cf20ed1d57f41305da83cbac648e7a`. The detailed contract is `docs/superpowers/specs/2026-09-24-phase8a-exp050-temporal-jackknife-utility-artifact-contract.md`.

DEC-143 opens no workflow, dispatch, historical result execution, promotion, shadow/demo, broker mutation, live order, real-money action, or trading authorization. A later separate decision may freeze a manual-main workflow/CLI while keeping execution closed until terminal review and one-run authorization are separately predeclared.

## DEC-144 — Phase 8A EXP-050 manual-main workflow source gate

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / EXECUTION AUTHORIZATION CLOSED

DEC-144 freezes the input-free manual-main workflow, public CLI, Python 3.12.14 numerical runtime, and exact-source execution gate for `EXP-20260924-050`.

The gate binds DEC-141 merge `4729da0e769f76f44b97ff6349ee25c5b7c0f5c7` and protocol blob `b41b817b03aa0cc03a9d893227caa399b46d3cf8`; DEC-142 merge `fa6fd14a880a84a44795efe4099679ed0f642497` and training-core blob `ec97a9941af052d6e223e4bafab9a9989ec57ff0`; DEC-143 merge `f0f584f2bfa1d6f0858af46312e41ffde5fe7d71` and artifact/evidence blob `60076ccb45b3468bce68f88f667225e0b5662d92`; and the accepted historical loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`.

The frozen workflow is `.github/workflows/phase8a-exp050-temporal-jackknife-utility-model-training.yml` at blob `ec8ed4ab3f0b8a18ffc735af92172e059ed29955`. It is manual `workflow_dispatch` only, input-free, main-only, read-only for contents/actions, and contains no schedule or pull-request trigger. DEC-144 intentionally contains no first-run guard; that guard belongs to a later one-run authorization decision only after terminal review is frozen and zero prior manual-main EXP-050 runs are independently verified.

The public CLI is `scripts/phase8a_exp050_model_run.py` at blob `70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09`. It exposes only `status`, `require-execution`, `run-cell`, and `aggregate`; it contains no dispatch command and evaluates the execution requirement before readiness loading, artifact loading, fitting, or aggregation.

The pinned runtime is `requirements/exp050-model-run.txt` at blob `d25ab16056b9f5df283147d67b8f401f60ae7520`, with Python 3.12.14 and the same pinned numerical packages as EXP-049. The exact accepted nine pair/timeframe source cells and 60m/240m horizons remain unchanged.

The execution gate is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_execution_gate.py` at blob `4814f0db86bec943d7282ab13586559b1eb8caa7`. Focused tests are `tests/test_phase8a_exp050_model_workflow.py` at blob `cce991971cef68fdeeb14cb2c26ecf54ba35985f`.

DEC-144 keeps run dispatch, authoritative result execution, model-protocol result production, model fit, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization false. Therefore the workflow source is complete but `require-execution` fails closed at the dispatch-authorization check.

Before any historical run authorization, a separate decision must predeclare the exact attempt-1 terminal review, required job/artifact inventory, complete-success and partial-failure evidence semantics, and no-rerun/replacement policy. DEC-144 dispatches nothing.
