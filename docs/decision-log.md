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

## DEC-145 — Phase 8A EXP-050 predeclared terminal-result review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-050 RUN AUTHORIZATION

DEC-145 freezes the exact terminal-review contract for the future first `EXP-20260924-050` historical model run before any result-producing authorization exists.

The review binds DEC-144 merge `9f2986c783823cf7d9647ed4b0a50c66470bea21`, workflow blob `ec8ed4ab3f0b8a18ffc735af92172e059ed29955`, CLI blob `70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09`, and execution-gate blob `4814f0db86bec943d7282ab13586559b1eb8caa7`.

Only attempt 1 of the exact manual-main `phase8a-exp050-temporal-jackknife-utility-model-training` workflow is reviewable. The terminal payload must contain exactly 11 completed jobs: one authorization preflight, nine model-cell matrix jobs, and one aggregate job. Rerun attempts are rejected.

A successful run requires all 11 jobs to succeed, all nine exact non-expired cell artifacts, the exact aggregate artifact, and independent DEC-143 aggregate-evidence revalidation against the run head SHA. The success stage is `TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`.

A first-attempt failure, cancellation, or timeout may preserve only a subset of valid cell artifacts. It may not claim an aggregate artifact or aggregate result evidence. The failure stage is `TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`, with preflight/matrix outcome counts and persisted cell-artifact count recorded.

The review source is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_result_review.py` at Git blob `e93f7f26e6f0cf8541c9dffd0d359acf0a7ec64e`. Focused tests are `tests/test_phase8a_exp050_model_result_review.py` at blob `54dd7a4c973a685efcc7a4b732c2be46e64e7aff`.

DEC-145 authorizes no dispatch, replacement run, fitting, promotion, shadow/demo, broker mutation, live order, real-money action, or trading. After merge, a later separate decision may independently verify zero prior manual-main EXP-050 runs, add the first-run rejection guard, and authorize at most one outer historical result-producing attempt without dispatching it.

## DEC-145 — Phase 8A EXP-050 predeclared terminal-result review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-050 HISTORICAL RESULT OR RUN AUTHORIZATION

DEC-145 freezes the exact terminal review for a possible future `EXP-20260924-050` run before any authorization or result exists.

Only attempt-1 manual-main runs of `phase8a-exp050-temporal-jackknife-utility-model-training` are reviewable. The review binds DEC-144 merge `9f2986c783823cf7d9647ed4b0a50c66470bea21`, workflow blob `ec8ed4ab3f0b8a18ffc735af92172e059ed29955`, CLI blob `70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09`, and execution-gate blob `4814f0db86bec943d7282ab13586559b1eb8caa7`.

Exactly 11 completed jobs are accepted: one authorization preflight, nine matrix jobs, and one aggregate job. Artifacts are restricted to the exact nine pair/timeframe cell-result names plus the exact aggregate-result name tied to the workflow head SHA.

A successful run requires all 11 jobs to succeed, all nine cell artifacts, the aggregate artifact, and successful DEC-143 aggregate-evidence revalidation against the execution commit. It stops at `TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`.

A failed, cancelled, or timed-out first attempt may preserve only a valid subset of cell artifacts. It cannot claim an aggregate artifact or aggregate evidence and stops at `TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`.

The review source is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_result_review.py` at blob `e93f7f26e6f0cf8541c9dffd0d359acf0a7ec64e`. Focused tests are `tests/test_phase8a_exp050_model_result_review.py` at blob `54dd7a4c973a685efcc7a4b732c2be46e64e7aff`. The detailed review contract is `docs/superpowers/specs/2026-09-24-phase8a-exp050-model-result-review.md`.

Any rerun attempt is rejected. Replacement-run authorization, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false. DEC-145 changes none of DEC-144's false dispatch/result/protocol-result/model-fit flags. A later separate decision may independently verify zero prior manual-main runs, add a first-run guard, and authorize at most one outer historical attempt without dispatching it.

## DEC-146 — Phase 8A EXP-050 single historical model-run authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-050 RUN DISPATCHED BY THIS DECISION

DEC-146 independently verifies zero prior manual-main `phase8a-exp050-temporal-jackknife-utility-model-training` runs after DEC-145 merged. The latest 100 repository Actions runs extend back to `2026-09-24T15:43:22Z`, before DEC-144 first put the workflow on `main` at `2026-09-24T18:13:58Z`; none match the exact workflow path with `workflow_dispatch` on `main`.

DEC-146 binds DEC-144 merge `9f2986c783823cf7d9647ed4b0a50c66470bea21`, pre-authorization workflow blob `ec8ed4ab3f0b8a18ffc735af92172e059ed29955`, CLI blob `70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09`, pre-authorization gate blob `4814f0db86bec943d7282ab13586559b1eb8caa7`, DEC-145 merge `b2907cced930afa4d877596a8268ec3bc49ceb9c`, and DEC-145 review blob `e93f7f26e6f0cf8541c9dffd0d359acf0a7ec64e`.

The workflow is hardened with a first-run rejection guard before runtime installation or fitting. It validates the exact current run identity, lists exact manual-main EXP-050 workflow runs, excludes only the current `GITHUB_RUN_ID`, and fails if any prior matching run exists. The hardened workflow blob is `7a5875c69d8cdf33e9aaae58fc321dba0537ce0b`.

The authorized execution gate is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_execution_gate.py` at blob `4b1e6723928f122fc2eaa3ba7564283088664296` and records `TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-146"`. Only the outer dispatch/result/protocol-result/model-fit flags are true. The underlying DEC-141 protocol, DEC-142 training core, and DEC-143 artifact-runner source-level result/fit locks remain false and are explicitly validated.

The first manual-main EXP-050 attempt consumes the slot on success, failure, cancellation, or timeout. No rerun, automatic retry, or replacement run is authorized. Any terminal outcome must route through DEC-145.

Focused workflow tests are `tests/test_phase8a_exp050_model_workflow.py` at blob `c5893e6a18fd9d0330001d4b35f5e34bbb8c33c1`. The detailed authorization record is `docs/superpowers/specs/2026-09-24-phase8a-exp050-single-model-run-authorization.md`.

DEC-146 itself dispatches nothing. Replacement-run authorization, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false. A later separate decision must freeze a clean-main one-way operator before any dispatch.

## DEC-147 — Phase 8A EXP-050 clean-main single-step operator

**Date:** 2026-09-24
**Status:** SOURCE-ONLY OPERATOR; NO EXP-050 RUN DISPATCHED BY THIS DECISION

DEC-147 freezes the one-way operator around the single historical EXP-050 attempt authorized by DEC-146.

The operator core is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_operator.py` at Git blob `d0284ff447fb0f1560a5fb42e558c8708a76de49`. The public CLI is `scripts/phase8a_exp050_operator.py` at blob `e0b5c31793226740abf73c944e80c2ae0fb995c8`. Focused tests are `tests/test_phase8a_exp050_operator.py` at blob `067cc3b9f6ac15f69f33b326e5395b9b49a0cf37`.

The operator binds DEC-146 merge `dd40df2522cf3ae9cfa5802d3d2a95a995570981`, requires a clean local `main` exactly matching fetched `origin/main`, verifies the `Dtwosam/FMP` remote, and reads only the exact manual-main `phase8a-exp050-temporal-jackknife-utility-model-training` workflow state.

The state machine is one-way. Only a missing run may expose the exact dispatch command. An active or terminal run exposes no dispatch path, and more than one manual-main run fails closed. The public CLI is read-only by default; `advance --execute` re-runs the public `next` planner and refuses dispatch if live state changes between planning and execution.

Terminal success requires the exact non-expired aggregate artifact tied to the run head SHA, loads the DEC-143 aggregate evidence, and routes the full terminal evidence through DEC-145. Non-success routes through DEC-145 without aggregate evidence. No rerun or replacement path exists.

DEC-147 itself dispatches nothing. Replacement-run authorization, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization remain false. After merge and normal regression gates, the operator may be inspected from clean current `main`; only an exact zero-run read-only plan may expose the single DEC-146-authorized dispatch.

## DEC-148 — Phase 8A EXP-050 reviewed historical temporal-jackknife utility result

**Date:** 2026-09-24
**Status:** REVIEWED / EXP-050 HISTORICAL RUN CLOSED

DEC-148 reviews the single DEC-146-authorized EXP-050 historical model run `36049824739`. The run completed successfully on attempt 1 at execution commit `25d48828b981c4309f4a859d2a33a56094638f21`; all 11 required jobs succeeded and all nine pair/timeframe cell artifacts plus the aggregate artifact were persisted.

The reviewed aggregate artifact is id `10829959147`, name `exp050-temporal-jackknife-utility-model-result-evidence-25d48828b981c4309f4a859d2a33a56094638f21-from-feature-35867307338-outcome-35876715434`, with GitHub artifact digest `sha256:4a2b223425c2e8df60e13ec0ad22c46da618957999a7a7d23908ff9fd3b20275`. The downloaded ZIP independently hashes to the same value and contains exactly one `model-result-evidence.json`.

DEC-143 aggregate-evidence revalidation succeeds. The canonical evidence fingerprint is `866b4a8f26553bad8c80a7b2e0e68aedb50bfa42b3c767ce91478c9dfd720023`, and all 18 individual cell-result fingerprints recompute exactly. All 18 cells and all 108 regressors verify. Three variants pass the unchanged aggregate selection gate, zero pass the frozen temporal-stability gate, all 18 cells terminate at `NO_TEMPORAL_JACKKNIFE_UTILITY_STABLE_MODEL_CHALLENGER`, and validation/retrospective holdout remain locked. Twenty-six budget variants are unavailable and the verified utility-eligible selection-row total is 26,392.

All three aggregate passes are USDJPY 5m / 60m at budgets 250, 500, and 1000. They produce 250, 501, and 1000 selection candidates respectively, with 0.5-pip selection total net pips of 612.9, 247.4, and 504.3. All three fail temporal stability. All three have zero candidates in 2021 H1; the 250 and 500 variants also have zero candidates in 2021 H2; the 1000 variant has one 2021 H2 candidate and fails both share and financial signs there. The 500 and 1000 variants have positive 2022 H1 financial signs but miss the 10% share floor. All three pass the 2022 H2 stability window.

The result-decision source is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_result_decision.py` at Git blob `70402f6c21f4ed22b4991025c98e6c1664215215`. Focused tests are `tests/test_phase8a_exp050_model_result_decision.py` at blob `cce218e5a05d7c567884aae5b1e08e632489377a`. The reviewed-result record is `docs/superpowers/specs/2026-09-24-phase8a-exp050-reviewed-model-result.md` at blob `887814acd498257b35012d736d8e9080ec8674a0`.

The DEC-146 one-run slot is consumed. Model-run dispatch, replacement-run authorization, authoritative result execution, protocol-result production, model fitting, promotion, shadow/demo, broker mutation, live order, real-money action, and trading authorization are all closed. No second EXP-050 run is authorized. Any post-result diagnostic or successor protocol requires a later separate decision and may not alter this reviewed evidence.

## DEC-149 — Phase 8A EXP-050 post-result temporal-jackknife utility diagnostic

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; SUCCESSOR SOURCE WORK ONLY

DEC-149 freezes the post-result diagnostic over the immutable DEC-148 / EXP-050 evidence before any later successor protocol is written. It performs no new model fit, changes no reviewed gate, and authorizes no historical result execution.

The source binding is DEC-148, workflow run `36049824739`, execution commit `25d48828b981c4309f4a859d2a33a56094638f21`, evidence fingerprint `866b4a8f26553bad8c80a7b2e0e68aedb50bfa42b3c767ce91478c9dfd720023`, DEC-148 merge `50ae34098ece275959d52ca9d104a07374a7ff6a`, and reviewed-result source blob `70402f6c21f4ed22b4991025c98e6c1664215215`.

Of the 54 predeclared budget variants, 26 are unavailable and 28 are available. Three available variants pass the unchanged aggregate selection gate and 25 reject there. All three passes are the USDJPY 5m / 60m cell at budget anchors 250, 500, and 1000; zero pass temporal stability.

All three aggregate passes have zero candidates in 2021 H1. The 250 and 500 variants also have zero candidates in 2021 H2; the 1000 variant has one 2021 H2 candidate and fails both share and financial signs there. The 500 and 1000 variants have positive 2022 H1 financial signs but still miss the 10% candidate-share floor. All three pass the 2022 H2 window.

Relative to EXP-049, the reviewed utility-eligible selection-row count increases from 14,158 to 26,392, available budget variants increase from 23 to 28, and unavailable variants decrease from 31 to 26. DEC-149 records the descriptive diagnostic classification `UTILITY_COVERAGE_INCREASED_BUT_EARLY_TEMPORAL_COVERAGE_LIMITED`. This is not a causal market claim and does not reinterpret any failed stability window as passing.

The diagnostic source is `src/fmp/market_learning/model_successor_temporal_jackknife_utility_post_result_diagnostics.py` at Git blob `f23465ca30249ce8abab3c9fdf07ce39a8679a9a`. Focused tests are `tests/test_phase8a_exp050_post_result_diagnostics.py` at blob `d2ff1d90b1c37e5a392742a3dfc960113b6d7bd1`. The diagnostic spec is `docs/superpowers/specs/2026-09-24-phase8a-exp050-post-result-diagnostics.md` at blob `fdf915fa167b548331f28b05043f0f525cc0c099`.

DEC-149 does not authorize lowering candidate-share or financial stability, removing a 2021 window, changing jackknife views, weakening unanimous positive-utility consensus, lowering the positive-utility requirement, adding smaller budget anchors as a result-producing rescue, rerunning or replacing EXP-050, successor fitting/result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. It opens only separately frozen successor-protocol source work.

## DEC-150 — Phase 8A EXP-051 out-of-fit calibrated utility successor protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NO EXP-051 MODEL EXECUTION AUTHORIZED

DEC-150 opens `EXP-20260924-051` as a post-result-informed successor to DEC-148/DEC-149. It binds EXP-050 run `36049824739`, execution commit `25d48828b981c4309f4a859d2a33a56094638f21`, evidence fingerprint `866b4a8f26553bad8c80a7b2e0e68aedb50bfa42b3c767ce91478c9dfd720023`, DEC-149 merge `d8874bf213c420fb506cc9ee8c4dfb2caffbb9e1`, DEC-149 diagnostic blob `f23465ca30249ce8abab3c9fdf07ce39a8679a9a`, DEC-148 reviewed-result blob `70402f6c21f4ed22b4991025c98e6c1664215215`, and EXP-050 protocol blob `b41b817b03aa0cc03a9d893227caa399b46d3cf8`.

DEC-149 recorded increased utility-eligible coverage versus EXP-049 but zero stable challengers: 28 of 54 budget variants were available, three passed the aggregate gate, all three passes were concentrated in USDJPY 5m / 60m, and all three had zero candidates in 2021 H1. DEC-150 does not lower the positive-utility rule, change the three jackknife views, weaken unanimous direction consensus, add smaller budget anchors, remove a 2021 window, or relax candidate-share or financial stability.

The sole EXP-051 research change is an out-of-fit calibration of the ranking scale. Each frozen EXP-050 jackknife view continues to fit the same LONG and SHORT 0.5-pip HGB utility regressors on the same four fit years. After fitting, each view scores exactly its excluded two-year fit regime separately for LONG and SHORT. The sorted finite predictions form six immutable calibration-reference vectors per cell. Realized outcomes and all selection/validation/holdout rows are excluded from calibration.

EXP-050 eligibility remains unchanged: every view must choose the same unique LONG or SHORT direction and each chosen raw predicted utility must be greater than zero. For an eligible row, each view's agreed-direction raw utility is mapped to the right empirical CDF of that view/target excluded-regime reference. The EXP-051 ranking score is the minimum calibrated percentile across the three views. The predecessor minimum raw utility is retained as a secondary score.

Candidate budgets remain 250/500/1000. Selection ranks by calibrated percentile descending, raw robust utility descending, then row identity ascending; the budget-th calibrated/raw score pair becomes the frozen cutoff. Validation and retrospective holdout reuse the exact six regressors, six calibration references, unanimous direction rule, and selection-derived cutoff pair without refit or recalibration.

Aggregate financial gates, the four half-year temporal-stability windows, the 10% per-window candidate-share floor, all per-window financial signs, validation/holdout chronology, and no-refit semantics remain unchanged. EXP-051 does not reserve candidates by year or window and does not use selection-period dates to construct calibration, so the stability screen remains capable of rejecting the successor completely.

The protocol source is `src/fmp/market_learning/model_successor_temporal_calibrated_utility_protocol.py` at Git blob `c39309c4115cae1ea058e56f30cae4af6407e36e`. Focused tests are `tests/test_phase8a_exp051_temporal_calibrated_utility_protocol.py` at blob `ac2814dea9c4f4d2771b5abe8b5d602e9b86b059`. The detailed spec is `docs/superpowers/specs/2026-09-24-phase8a-exp051-temporal-calibrated-utility-protocol.md` at blob `8f548ce735d52c5d5b8aa483b2db8668672c395e`.

DEC-150 keeps model-protocol result production, model fit, historical result execution, workflow dispatch, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization false. A later separate decision may implement only the deterministic in-memory EXP-051 training/evaluation core against this exact protocol source.

## DEC-151 — Phase 8A EXP-051 temporal-calibrated utility training core

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NO AUTHORITATIVE EXP-051 FIT

DEC-151 implements the deterministic in-memory EXP-051 training/evaluation core against the exact DEC-150 protocol. It binds DEC-150 merge `b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833`, DEC-150 protocol blob `c39309c4115cae1ea058e56f30cae4af6407e36e`, and predecessor EXP-050 training-core blob `ec97a9941af052d6e223e4bafab9a9989ec57ff0`.

The core preserves the exact EXP-050 three-view jackknife fit topology and six HGB utility regressors per cell. It reuses the predecessor fit and scoring helpers through the frozen training-core binding; no HGB structure, target, feature set, fit window, direction-eligibility rule, budget anchor, aggregate financial gate, temporal-stability gate, validation chronology, or holdout chronology is changed.

After each view is fitted, DEC-151 scores the exact two-year fit regime excluded from that view separately for LONG and SHORT. Finite predictions are sorted into six immutable out-of-fit calibration-reference vectors per cell. Each reference records its excluded-regime identity, row count, prediction summary, row-bound prediction digest, and sorted-reference digest. Realized outcomes and all selection/validation/holdout rows remain outside calibration.

Selection and forward scoring preserve EXP-050 unanimous positive raw-utility direction eligibility. For eligible rows, the core maps each view's agreed-direction raw utility to the right empirical CDF of the frozen view/target reference, takes the minimum percentile across views as robust calibrated utility, and retains the predecessor minimum raw utility as secondary score.

For budgets 250/500/1000, rows rank by calibrated utility descending, raw robust utility descending, then row identity ascending. The budget-th row freezes a calibrated/raw cutoff pair. Candidate application, aggregate financial metrics, four-window temporal stability, validation, and retrospective holdout reuse that same pair unchanged. Exact calibrated/raw ties may exceed the nominal budget; budgets remain unavailable when fewer than the requested number of EXP-050-eligible rows exist.

The training core is `src/fmp/market_learning/model_successor_temporal_calibrated_utility_training.py` at Git blob `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`. Focused tests are `tests/test_phase8a_exp051_temporal_calibrated_utility_training.py` at blob `70d1e3ae39566fd7ee0ea53c030f0cc65f89b3ab`. The detailed spec is `docs/superpowers/specs/2026-09-24-phase8a-exp051-temporal-calibrated-utility-training-core.md` at blob `a353ae2c67666b0d492b2cfe35c1078e0e4561ef`.

DEC-151 keeps authoritative EXP-051 artifact loading, model-result execution, workflow dispatch, authoritative model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization false. A later separate decision may freeze an artifact-backed EXP-051 runner/evidence contract against this exact training-core blob.

## DEC-152 — Phase 8A EXP-051 temporal-calibrated utility artifact-backed result-evidence contract

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-152 freezes the artifact-backed runner and aggregate evidence contract for `EXP-20260924-051`. It binds DEC-150 merge `b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833` and protocol blob `c39309c4115cae1ea058e56f30cae4af6407e36e`; DEC-151 merge `68028ef37b72e3f0695b475928434ede40ad7690` and training-core blob `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`; predecessor EXP-050 training-core blob `ec97a9941af052d6e223e4bafab9a9989ec57ff0`; accepted historical loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`; and generic regime-utility artifact-helper blob `6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13`.

The contract requires exactly the frozen 18 model cells, six HGB regressors per cell, and six excluded-regime calibration references per cell. Across a complete aggregate result it therefore independently verifies 108 regressors and 108 calibration references, in addition to exact cell identity, accepted data-manifest identity, split row counts, selection/validation/holdout chronology, and canonical cell/result fingerprints.

Each calibration reference must bind the exact jackknife view and excluded regime, contain both LONG and SHORT target records, carry positive row counts, finite and ordered prediction summaries, and expose both the row-bound prediction digest and sorted-reference digest. Full-fit fallback, view-weight search, view fallback, selection-window calibration, HGB classification, and logistic fallback remain explicitly forbidden or excluded.

Selection and forward consensus evidence now validates both positive raw robust-utility bounds and calibrated robust-utility bounds inside [0,1], complete three-view/two-target prediction digests, and the calibrated-consensus fingerprint. Available budget variants must carry a finite calibrated cutoff in [0,1], a positive finite raw cutoff, exact 0.5-pip realized financial evidence, and the unchanged temporal-stability screen. Budget-unavailable variants must keep both cutoffs null.

The no-challenger state is `NO_TEMPORAL_CALIBRATED_UTILITY_STABLE_MODEL_CHALLENGER`. A selected variant must uniquely match one stable persisted variant by HGB family, budget anchor, calibrated cutoff, and raw cutoff. Validation and retrospective holdout preserve the frozen status chain and exact pair cutoff without recalibration.

The aggregate evidence contract reuses the accepted authoritative feature, outcome, and readiness identities, validates exact all-cell completeness, recomputes the aggregate summary from validated cells, and requires exactly 108 verified regressors and 108 verified calibration references. The aggregate fingerprint is recomputed from canonical JSON.

The artifact/evidence source is `src/fmp/market_learning/model_successor_temporal_calibrated_utility_artifacts.py` at Git blob `3b25ad8dee80ad2d68a421b01b3e7789b1de9f1a`. Focused tests are `tests/test_phase8a_exp051_temporal_calibrated_utility_artifacts.py` at blob `1c0bec0b6f337266d97fc3b79efa1afdab60e8b1`. The detailed contract is `docs/superpowers/specs/2026-09-24-phase8a-exp051-temporal-calibrated-utility-artifact-contract.md` at blob `42b68626a5a91464cd8a225a3157d00fddc7a694`.

The authoritative bundle checks `AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED` before source validation, readiness validation, historical artifact loading, fitting, or result compilation. DEC-152 keeps that flag false and keeps authoritative model fit false.

DEC-152 opens no workflow, dispatch, historical result execution, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading authorization. A later separate decision may freeze a manual-main workflow, public CLI, pinned numerical runtime, and exact-source execution gate while keeping execution authorization closed.

## DEC-153 — Phase 8A EXP-051 manual-main workflow source gate

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / EXECUTION AUTHORIZATION CLOSED

DEC-153 freezes the manual-main, input-free workflow, public CLI, Python 3.12.14 numerical runtime, and exact-source execution gate for `EXP-20260924-051`. It binds DEC-150 merge `b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833` and protocol blob `c39309c4115cae1ea058e56f30cae4af6407e36e`; DEC-151 merge `68028ef37b72e3f0695b475928434ede40ad7690` and training-core blob `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`; DEC-152 merge `9f8fc93096fb29579924932c5c3b526598afaf28` and artifact/evidence blob `3b25ad8dee80ad2d68a421b01b3e7789b1de9f1a`; and the accepted historical loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`.

The frozen workflow is `.github/workflows/phase8a-exp051-temporal-calibrated-utility-model-training.yml` at blob `4ab7480e31e91cbfe39eb5e289eccadde428d1a4`. It is manual `workflow_dispatch` only, input-free, main-only, read-only for contents/actions, and contains no schedule or pull-request trigger. DEC-153 intentionally contains no first-run guard; that guard belongs to a later one-run authorization decision only after terminal review is frozen and zero prior manual-main EXP-051 runs are independently verified.

The workflow preserves the exact accepted nine pair/timeframe source cells and both 60m/240m horizons. It reuses the accepted feature, outcome, and readiness artifact IDs and ZIP digests, preserves partial pair/timeframe evidence under an `if: always()` upload, and compiles complete aggregate evidence only through the DEC-152 contract.

The public CLI is `scripts/phase8a_exp051_model_run.py` at blob `c88b05a14bc961391ff59e29f742c1dac27272b6`. It exposes only `status`, `require-execution`, `run-cell`, and `aggregate`; contains no dispatch command; and evaluates the DEC-153 execution requirement before readiness loading, historical artifact loading, fitting, or aggregation.

The pinned runtime is `requirements/exp051-model-run.txt` at blob `d25ab16056b9f5df283147d67b8f401f60ae7520`, with Python 3.12.14 and the same numerical package versions as EXP-050.

The exact-source execution gate is `src/fmp/market_learning/model_successor_temporal_calibrated_utility_execution_gate.py` at blob `37a0b7af464c464beff0976addc1464f68e916cc`. It revalidates the DEC-150/151/152 source chain and exact workflow/CLI/runtime/common-source blobs while requiring all upstream protocol/core/runner execution and fit flags to remain false.

Focused tests are `tests/test_phase8a_exp051_model_workflow.py` at blob `572c179a3be96fd7ae23d575d206d308232da78c`. The detailed source contract is `docs/superpowers/specs/2026-09-24-phase8a-exp051-temporal-calibrated-utility-workflow-source.md` at blob `7235bf7d9c018ae2718251680a674284f31aabfc`.

DEC-153 keeps run dispatch, authoritative result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization false. Therefore `require-execution` fails closed at the dispatch-authorization check.

Before any historical run authorization, a separate decision must predeclare exact attempt-1 terminal review, required job/artifact inventory, complete-success and partial-failure evidence semantics, and no-rerun/replacement policy. DEC-153 dispatches nothing.

## DEC-154 — Phase 8A EXP-051 predeclared terminal-result review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-051 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION

DEC-154 freezes the exact terminal-review contract for a possible future first `EXP-20260924-051` historical model run before any result-producing authorization exists.

Only attempt-1 manual-main runs of `phase8a-exp051-temporal-calibrated-utility-model-training` are reviewable. The review binds DEC-153 merge `b0fb55aca2d818e7306a15b200b1e10fcc151ad2`, workflow blob `4ab7480e31e91cbfe39eb5e289eccadde428d1a4`, CLI blob `c88b05a14bc961391ff59e29f742c1dac27272b6`, and execution-gate blob `37a0b7af464c464beff0976addc1464f68e916cc`.

Exactly 11 completed jobs are accepted: one authorization preflight, nine matrix jobs, and one aggregate job. Artifacts are restricted to the exact nine pair/timeframe cell-result names plus the exact aggregate-result name tied to the workflow head SHA.

A successful run requires all 11 jobs to succeed, all nine cell artifacts, the aggregate artifact, and successful DEC-152 aggregate-evidence revalidation against the execution commit. DEC-152 independently requires complete 18-cell evidence with 108 regressors, 108 calibration references, calibrated/raw cutoff evidence, frozen chronology/status chains, and canonical fingerprints. A successful review stops at `TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`.

A failed, cancelled, or timed-out first attempt may preserve only a valid subset of cell artifacts. It cannot claim an aggregate artifact or aggregate evidence and stops at `TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`.

The review source is `src/fmp/market_learning/model_successor_temporal_calibrated_utility_result_review.py` at Git blob `bd46dfd1cb8674ab8088d858b378ca37c5d75687`. Focused tests are `tests/test_phase8a_exp051_model_result_review.py` at blob `132ec628d41f6ef84797c683e8114f3b3d935a22`. The detailed review contract is `docs/superpowers/specs/2026-09-24-phase8a-exp051-temporal-calibrated-utility-result-review.md` at blob `44a820cde551b7c89a1ef65e5475d13b49a6479e`.

Any rerun attempt is rejected. Replacement-run authorization, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization remain false. DEC-154 changes none of DEC-153's false dispatch/result/protocol-result/model-fit flags.

A later separate decision may independently verify zero prior manual-main EXP-051 runs, add a first-run rejection guard, and authorize at most one outer historical attempt without dispatching it.

## DEC-155 — Phase 8A EXP-051 single historical model-run authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-051 RUN DISPATCHED BY THIS DECISION

After DEC-154 merged, repository Actions history was independently inspected. The latest 100 runs extend back to `2026-09-24T17:24:51Z`, before DEC-153 first put the EXP-051 workflow on `main` at `2026-09-24T21:12:27Z`. Across that entire possible workflow lifetime, zero runs match the exact EXP-051 workflow path with `workflow_dispatch` on `main`.

DEC-155 binds DEC-153 merge `b0fb55aca2d818e7306a15b200b1e10fcc151ad2`, pre-authorization workflow blob `4ab7480e31e91cbfe39eb5e289eccadde428d1a4`, CLI blob `c88b05a14bc961391ff59e29f742c1dac27272b6`, pre-authorization execution-gate blob `37a0b7af464c464beff0976addc1464f68e916cc`, DEC-154 merge `fce3859d8eaf9b779c539f3c49b464b4ee72c467`, and DEC-154 review blob `bd46dfd1cb8674ab8088d858b378ca37c5d75687`.

The workflow is hardened with a first-run rejection guard before runtime installation or model fitting. It verifies the exact current run identity, lists exact manual-main EXP-051 workflow runs, excludes only the current `GITHUB_RUN_ID`, and fails if any prior matching run exists. The hardened workflow blob is `8c0f77a2585715bdc758e6a158c0c5db6cc4e8c9`.

The authorized execution gate is `src/fmp/market_learning/model_successor_temporal_calibrated_utility_execution_gate.py` at blob `cfb16316f2bf9f09e037f48b3f80867562231bf8` and records `TEMPORAL_CALIBRATED_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-155"`. Only the outer dispatch/result/protocol-result/model-fit flags are true. The underlying DEC-150 protocol, DEC-151 training core, and DEC-152 artifact-runner source-level result/fit locks remain false and are explicitly validated.

The first manual-main EXP-051 attempt consumes the slot on success, failure, cancellation, or timeout. No rerun, automatic retry, or replacement run is authorized. Any terminal outcome must route through DEC-154.

Focused workflow tests are `tests/test_phase8a_exp051_model_workflow.py` at blob `2c46fe19d2875e5d3fd7625d9d685f3e5797f41e`. The detailed authorization record is `docs/superpowers/specs/2026-09-24-phase8a-exp051-single-model-run-authorization.md` at blob `44ce3ae831ca553ad05300441b47cd6a706d7152`.

DEC-155 itself dispatches nothing. Replacement-run authorization, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization remain false. A later separate decision must freeze a clean-main, one-way operator before any dispatch.

## DEC-156 — Phase 8A EXP-051 clean-main one-way operator

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY OPERATOR; NO EXP-051 RUN DISPATCHED BY THIS DECISION

DEC-156 freezes a fail-closed clean-main operator around the single historical EXP-051 attempt authorized by DEC-155. It binds DEC-155 merge `a8b6204faccf411fd489ca5a1d004d90ed75be33`, the DEC-153 execution-gate identity, DEC-155 execution-authorization identity, the full DEC-150 through DEC-154 source metadata returned by that gate, the hardened EXP-051 workflow/CLI identities, and the DEC-154 terminal-review contract.

The operator permits exactly three live run states: `MISSING`, `IN_PROGRESS`, and `TERMINAL`. Only `MISSING` may expose the frozen command `gh workflow run phase8a-exp051-temporal-calibrated-utility-model-training.yml --ref main -R Dtwosam/FMP`. Once any manual-main EXP-051 run exists, active or terminal, the operator exposes no second dispatch. More than one matching run is a fail-closed error.

Before reporting or dispatching, the public operator requires local branch `main`, a clean worktree, local HEAD exactly equal to freshly fetched `origin/main`, and an origin URL identifying exactly `Dtwosam/FMP`. `advance` is dry by default. `advance --execute` first obtains a read-only `next` plan, obtains a second independent `next` plan immediately before execution, and stops if the parsed reports or frozen dispatch commands differ.

Terminal runs are routed through DEC-154. For a successful run, the operator fetches the exact run/jobs/artifact payloads, requires the exact non-expired aggregate artifact name, safely extracts exactly one `model-result-evidence.json`, loads it through the DEC-152 evidence loader against the run head SHA, and supplies the aggregate evidence to DEC-154. Non-success terminal runs are reviewed without aggregate evidence. No retry, rerun, or replacement command exists.

The operator core is `src/fmp/market_learning/model_successor_temporal_calibrated_utility_operator.py` at Git blob `de021a9cde4bd7c995ccb95e340df883c692d9dd`. The public CLI is `scripts/phase8a_exp051_operator.py` at blob `bdf798e7db33917c3432f2e153c0eba563ab7ce3`. Focused tests are `tests/test_phase8a_exp051_operator.py` at blob `47dc36184e3088322c1f983112781c3ec330d865`. The detailed operator spec is `docs/superpowers/specs/2026-09-24-phase8a-exp051-single-step-operator.md` at blob `eed8a0612e79b1ba4a754a66bd37140728ce1507`.

DEC-156 itself dispatches nothing. Replacement-run authorization, promotion, shadow/demo execution, broker mutation, live order, real-money action, and trading authorization remain false. After merge and green repository checks, a read-only clean-main operator plan must be inspected before any separately authorized first dispatch.

## DEC-157 — Phase 8A EXP-051 read-only operator plan runner

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY READ-ONLY RUNNER; NO EXP-051 DISPATCH

DEC-157 adds a repository-hosted read-only runner for the exact merged DEC-156 operator `next` path. It exists only to obtain the clean-main zero-run plan while the user's local Desktop Commander execution environment is unavailable.

The runner is `.github/workflows/phase8a-exp051-operator-plan.yml` at Git blob `ede8d1a7e7e4f4bd2dcad643e354b606b8ecb925`. It triggers only on a push to `main` that changes that workflow file, checks out `main` with full history, requires local HEAD to equal `origin/main`, installs the frozen Python 3.12.14 EXP-051 runtime, and executes only `python scripts/phase8a_exp051_operator.py next`.

The runner contains no `workflow_dispatch` trigger, no schedule, no pull-request trigger, no operator `advance` call, no `advance --execute` call, and no direct `gh workflow run phase8a-exp051-temporal-calibrated-utility-model-training.yml` command. It therefore cannot submit the historical model workflow.

The persisted plan must prove `operator_decision = DEC-156`, `read_only = true`, no run present, `run_state = MISSING`, and stage `TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`. It also rechecks the exact frozen dispatch command as plan evidence, the four DEC-155 outer historical-run flags as true, and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks as false.

A successful runner persists `operator-plan.json` in artifact `exp051-dec156-read-only-operator-plan-<commit>`. Focused tests are `tests/test_phase8a_exp051_operator_plan_runner.py` at blob `0ba4ee0d163d2e5611baa7fa91974f82e9dcf384`. The detailed spec is `docs/superpowers/specs/2026-09-24-phase8a-exp051-operator-plan-runner.md` at blob `d81999642a13d244a2bdf9c985fb3a82ae64b201`.

DEC-157 changes no model-run authorization and consumes no run slot. It authorizes no retry, replacement, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading. After merge, the automatic read-only plan must be inspected before any separate environment-specific executor may invoke the existing DEC-156 `advance --execute` path.

## DEC-158 — Phase 8A EXP-051 read-only operator plan runner environment repair

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY REPAIR; NO EXP-051 DISPATCH

DEC-157 merged at `c80e1224cd092539cb904c1f58bdeb8b072aed63` and automatically started read-only plan run `36064683930`. That run passed exact merged-main checkout, push/main identity checks, Python setup, and pinned runtime installation, then the exact DEC-156 `next` invocation failed closed with `ValueError: EXP-051 dispatch requires a clean working tree`.

The failure consumed no EXP-051 run slot and submitted no model workflow. It confirmed that DEC-156's independent clean-worktree gate was operating correctly.

The cause was DEC-157's editable repository install, `python -m pip install -r requirements/exp051-model-run.txt -e .`, which mutated the checkout with local package-install metadata before DEC-156 inspected the worktree.

DEC-158 repairs only the runner environment. It exports `PYTHONPATH=${{ github.workspace }}/src`, installs only `requirements/exp051-model-run.txt` without `-e .`, and adds an explicit `test -z "$(git status --porcelain)"` check before invoking the operator. The repaired runner is `.github/workflows/phase8a-exp051-operator-plan.yml` at blob `e1bf3a4db4804ec237638c5b87bf9fb99b2c5ed3`.

Focused tests are `tests/test_phase8a_exp051_operator_plan_runner.py` at blob `1534a732930036b4bf3a1ed120cf7338f85b873f`. The detailed repair record is `docs/superpowers/specs/2026-09-24-phase8a-exp051-operator-plan-runner-repair.md` at blob `8f202980a4326f29c1a61949cece6c58c8d3f778`.

The trigger, read-only permissions, exact DEC-156 `next` invocation, zero-run plan validation, plan artifact, and absence of `advance`, `advance --execute`, direct model-workflow dispatch, retry, replacement, promotion, and trading paths remain unchanged.

DEC-158 changes no DEC-155 authorization flag and dispatches nothing. After merge, the workflow-file change must automatically rerun the repaired read-only plan and prove the exact `MISSING` / `RUN_DISPATCH_REQUIRED` state before any executor decision is considered.

## DEC-159 — Phase 8A EXP-051 read-only operator plan output-path repair

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY REPAIR; NO EXP-051 DISPATCH

DEC-158 merged at `a72bb89b9e4edcc3d7a3617a1b917d64b6ec4d97` and automatically started repaired read-only plan run `36065119686`. That run passed exact merged-main checkout, non-editable dependency installation, and the explicit post-install clean-worktree check, then the exact DEC-156 `next` invocation again failed closed with `ValueError: EXP-051 dispatch requires a clean working tree`.

No EXP-051 model workflow was dispatched and the DEC-155 single-run slot remained unconsumed.

The remaining mutation was caused by the shell opening checkout-local `operator-plan.json` for `tee` before DEC-156 performed its independent checkout preflight. DEC-159 moves all plan persistence outside the repository to `$RUNNER_TEMP/operator-plan.json`.

The repaired workflow is `.github/workflows/phase8a-exp051-operator-plan.yml` at blob `187011b6b4f1179c2b83c90062d58d15a29f9639`. It runs `python scripts/phase8a_exp051_operator.py next > "$RUNNER_TEMP/operator-plan.json"`, verifies that external file, and uploads `${{ runner.temp }}/operator-plan.json`.

Focused tests are `tests/test_phase8a_exp051_operator_plan_runner.py` at blob `0490a32292b67559701d765dacff7997a4d57ce0`. The detailed repair record is `docs/superpowers/specs/2026-09-24-phase8a-exp051-operator-plan-output-repair.md` at blob `bed09d0476c300442db7243f34326045c6c1133b`.

All DEC-158 environment protections remain, including non-editable dependency installation, `PYTHONPATH=src`, and the explicit post-install clean-worktree assertion. The runner still contains no `advance`, `advance --execute`, direct model-workflow dispatch, retry, replacement, promotion, or trading path.

DEC-159 changes no DEC-155 authorization flag and dispatches nothing. After merge, its workflow-file change must automatically rerun the read-only plan and prove the exact `MISSING` / `RUN_DISPATCH_REQUIRED` state before any executor decision is considered.

## DEC-160 — Phase 8A EXP-051 one-shot operator executor

**Date:** 2026-09-24
**Status:** APPROVED SOURCE; EXECUTION ONLY THROUGH DEC-156

DEC-159 merged at `a997808602ab3a9f4ca53982895c05cb0a358e67`. Its automatic read-only plan run `36065565456` completed successfully on attempt 1 and persisted artifact `10835714803`, named `exp051-dec156-read-only-operator-plan-a997808602ab3a9f4ca53982895c05cb0a358e67`. That plan proved the exact merged DEC-156 state was read-only, `MISSING`, and `TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`, with the DEC-155 outer historical-run flags true and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

DEC-160 adds exactly one repository-hosted executor whose only execution action is `python scripts/phase8a_exp051_operator.py advance --execute`. The executor contains no direct `gh workflow run phase8a-exp051-temporal-calibrated-utility-model-training.yml` command and no model-workflow dispatch REST endpoint. All live dispatch logic remains inside DEC-156, including clean-main validation, live zero-run selection, first and second `next` plans, parsed-plan equality, frozen-command equality, and fail-closed refusal if any run appears.

The executor workflow is `.github/workflows/phase8a-exp051-operator-execute.yml` at blob `0c93bdf44bfbe63b997d62f116f20de776873d06`. It triggers only when that workflow file itself is introduced or changed on `main`, has `contents: read` and `actions: write`, installs the pinned runtime without mutating the checkout, requires a clean worktree, independently revalidates the exact successful DEC-159 plan run/artifact, and writes its execution receipt under `RUNNER_TEMP`.

The receipt is accepted only when DEC-156 reports `advance_execute_requested = true`, `advance_dispatchable = true`, `dispatch_submitted = true`, `result_claimed = false`, and the original live state was `MISSING` / `RUN_DISPATCH_REQUIRED`. It must also keep replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

Focused tests are `tests/test_phase8a_exp051_operator_executor.py` at blob `6b734dc9f06488e584a10ff99407c78a3c04548f`. The detailed executor record is `docs/superpowers/specs/2026-09-24-phase8a-exp051-operator-executor.md` at blob `258684ee56aa9ad916842561909ebbf77287f85d`.

DEC-160 does not alter the research protocol and authorizes no retry, replacement, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading. After merge, the executor's automatic push run is the only new action; if DEC-156 submits the model workflow, that resulting manual-main EXP-051 run becomes the consumed DEC-155 attempt 1 and must be observed to terminal state and reviewed through DEC-154 without rerun.

## DEC-161 — Phase 8A EXP-051 reviewed temporal-calibrated utility model result

**Date:** 2026-09-24
**Status:** REVIEWED; NO STABLE CHALLENGER; RUN SLOT CLOSED

The single DEC-155-authorized EXP-051 historical workflow run `36066217609` completed successfully on attempt 1 at execution commit `3443b95ae3c524c74df4b2daebe9c526eb01ec9c`. All 11 DEC-154-required jobs completed successfully: authorization preflight, nine pair/timeframe matrix jobs, and aggregate-model-evidence. The run produced all nine expected cell artifacts plus aggregate artifact `10837836415`, named `exp051-temporal-calibrated-utility-model-result-evidence-3443b95ae3c524c74df4b2daebe9c526eb01ec9c-from-feature-35867307338-outcome-35876715434`, with GitHub artifact digest `sha256:ffbd18124dfe94c6eb25ae92fa4fda9650a26bd152173b000549b9a6e9fcace0`. The downloaded ZIP independently hashes to the same value and contains exactly one `model-result-evidence.json`.

The aggregate evidence binds DEC-150/151/152, code commit `3443b95ae3c524c74df4b2daebe9c526eb01ec9c`, 18 cells, 108 regressors, and 108 excluded-regime calibration references. The stored evidence fingerprint `7dd836ed1c76c8eefd09b2b75e1eef9e875f5c6261c6fbb2cac8e3209781aaea` recomputes exactly, and all 18 individual cell-result fingerprints also recompute exactly.

DEC-152 summary evidence records zero selected cells, 18 no-stable-challenger cells, one aggregate-selection-pass variant, zero stable-selection-pass variants, 26 unavailable budget variants, 26,392 utility-eligible selection rows, zero validation-pass cells, and zero retrospective-holdout-pass cells.

The sole aggregate pass is USDJPY 5m / 60m at budget 250 with 250 selected candidates and 1,288.1 total net pips. Its frozen calibrated/raw cutoff pair is approximately 0.9971023442510035 / 1.852905399735933. Temporal stability still rejects: 2021 H1 has zero candidates, 2021 H2 has zero candidates, 2022 H1 has three candidates with -28.1 total net pips, and only 2022 H2 passes with 247 candidates and 1,316.2 total net pips. No validation or holdout stage is unlocked.

The reviewed-result source is `src/fmp/market_learning/model_successor_temporal_calibrated_utility_result_decision.py` at Git blob `14bc6f2e9172aa325aeb556b7abeacf2c756c475`. Focused tests are `tests/test_phase8a_exp051_model_result_decision.py` at blob `691ec9d8a0bda18812374467d5f31ad44a02619a`. The detailed reviewed-result spec is `docs/superpowers/specs/2026-09-24-phase8a-exp051-reviewed-model-result.md` at blob `852057f95605b4aa58f0fbcb6c584e4b270a2180`.

DEC-161 closes the consumed EXP-051 run slot. Model-run dispatch, replacement run, authoritative result execution, protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization are all false. No second EXP-051 run is authorized. The next gate is a separate post-result diagnostic over immutable DEC-161 evidence before any later successor protocol is considered.

## DEC-162 — Phase 8A EXP-051 post-result diagnostics

**Date:** 2026-09-25
**Status:** APPROVED POST-RESULT DIAGNOSTIC / SUCCESSOR SOURCE DESIGN MAY OPEN

DEC-162 compares immutable reviewed EXP-050 and EXP-051 evidence after DEC-161 closes the consumed EXP-051 run slot. It binds DEC-161 merge `0a67a2353f3f2f2c5106074bd9e7e620a37d1649`, DEC-161 result-decision blob `14bc6f2e9172aa325aeb556b7abeacf2c756c475`, DEC-149 merge `d8874bf213c420fb506cc9ee8c4dfb2caffbb9e1`, DEC-149 diagnostic blob `f23465ca30249ce8abab3c9fdf07ce39a8679a9a`, and the exact EXP-050/EXP-051 reviewed evidence fingerprints.

The comparison confirms that calibrated ranking changes candidate ordering without changing raw direction eligibility or budget availability: both experiments contain 26,392 utility-eligible selection rows, 28 available budget variants, and 26 unavailable variants.

Aggregate passes contract from three in EXP-050 to one in EXP-051. Both experiments' aggregate passes remain concentrated in USDJPY 5m / 60m. EXP-050 passes budgets 250/500/1000, while EXP-051 passes budget 250 only. Stable-selection passes remain zero in both experiments.

For the common budget-250 variant, EXP-051 changes the candidate identity digest, shifts the direction mix from 249 LONG / 1 SHORT to 239 LONG / 11 SHORT, and improves realized selection total net pips from `612.8999999999933` to `1288.1000000000117`, a delta of `675.2000000000185`. Mean net pips rises by `2.7008000000000743`.

That improvement does not broaden early temporal support. Both EXP-050 and EXP-051 select zero candidates in 2021 H1 and 2021 H2. EXP-051 adds three 2022 H1 candidates, but they lose `-28.100000000000477` net pips and represent only 1.2% of the full candidate count. The calibrated rank instead concentrates 247 of 250 candidates in 2022 H2, where realized total net pips rises to `1316.2000000000123`.

Broader calibrated ranks degrade: EXP-050 budget 500 passes the aggregate gate with `247.4000000000135` pips, while EXP-051 budget 500 rejects with `-766.5999999999894`; EXP-050 budget 1000 passes with `504.3000000000052`, while EXP-051 budget 1000 rejects with `-3.200000000010732`.

DEC-162 therefore classifies the result as `TOP_250_FINANCIAL_QUALITY_IMPROVED_BUT_EARLY_TEMPORAL_COVERAGE_UNCHANGED_AND_BROAD_BUDGETS_DEGRADED`. The remaining blocker is robust temporal support in the ranked candidate set, not merely raw utility scale mismatch.

The diagnostic source is `src/fmp/market_learning/model_successor_temporal_calibrated_utility_post_result_diagnostics.py` at blob `00b9cbb5b0c95bd161d429d1f973d1e807f02a48`. Focused tests are `tests/test_phase8a_exp051_post_result_diagnostics.py` at blob `4c914eb34b5413ae26455f05b6ea6f347a995d1e`. The detailed diagnostic spec is `docs/superpowers/specs/2026-09-25-phase8a-exp051-post-result-diagnostics.md` at blob `85859be4f89bbf13e65c372d29c018ad290dd84a`.

DEC-162 authorizes only source design for a later successor protocol. It does not authorize rerun/replacement of EXP-051, gate relaxation, selection-window recalibration, use of realized selection outcomes in ranking, successor result execution, successor model fitting, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## DEC-163 — Phase 8A EXP-052 fit-temporal-support utility protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY PROTOCOL / NO EXP-052 FIT

DEC-163 opens EXP-052 as a narrow source-only successor to DEC-162. It binds DEC-162 merge `3d8453c544fc4b06c691d1068828ec6da9fc7110`, DEC-162 diagnostic blob `00b9cbb5b0c95bd161d429d1f973d1e807f02a48`, DEC-161 result-decision blob `14bc6f2e9172aa325aeb556b7abeacf2c756c475`, predecessor EXP-051 protocol blob `c39309c4115cae1ea058e56f30cae4af6407e36e`, and predecessor result-evidence fingerprint `7dd836ed1c76c8eefd09b2b75e1eef9e875f5c6261c6fbb2cac8e3209781aaea`.

EXP-052 preserves EXP-051 through raw direction eligibility: three leave-one-regime-out jackknife views, six HGB utility regressors, positive-utility unanimous direction consensus, robust raw utility, all six pooled excluded-regime calibration references, the 250/500/1000 budget anchors, aggregate financial gate, four half-year selection stability windows, 10% candidate-share floor, validation/holdout chronology, and no-refit forward semantics.

The sole research change is fit-only temporal-support calibration. Each view's excluded two-year fit regime is split into four frozen half-years. Each already-fitted view regressor scores its four excluded-regime half-years separately for LONG and SHORT, yielding 24 out-of-fit support-reference vectors per cell. No realized outcomes or selection/validation/holdout rows enter these references.

For an EXP-051-eligible row, the agreed-direction raw utility is mapped to 12 view-by-half-year empirical percentiles. Robust fit-temporal support is the minimum of those 12 percentiles. Selection ranks by robust fit-temporal support descending, EXP-051 pooled calibrated utility descending, robust raw utility descending, then row identity ascending. The budget-th row freezes a support/pooled/raw cutoff triple; forward stages reuse the exact six models, six pooled references, 24 support references, and frozen triple.

The protocol source is `src/fmp/market_learning/model_successor_fit_temporal_support_utility_protocol.py` at Git blob `01d5080560ec5d41653694b4df086ff2f10e770d`. Focused tests are `tests/test_phase8a_exp052_fit_temporal_support_utility_protocol.py` at blob `fac0c626fc72ce9e4f88beb15e59c01e39a3af4c`. The detailed protocol spec is `docs/superpowers/specs/2026-09-25-phase8a-exp052-fit-temporal-support-utility-protocol.md` at blob `479143fa61e9e8b8b88d1e5378a5618c5e0676c4`.

DEC-163 keeps authoritative protocol-result production, model fitting, historical result execution, selection-window calibration, validation/holdout calibration, realized selection-outcome ranking, gate relaxation, per-window tuning, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization false. The next gate is a deterministic in-memory EXP-052 training/evaluation core against this exact protocol source.

## DEC-164 — Phase 8A EXP-052 fit-temporal-support training core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NO AUTHORITATIVE EXP-052 FIT

DEC-164 implements the deterministic in-memory EXP-052 training/evaluation core against the exact DEC-163 protocol. It binds DEC-163 merge `9108cd170b2eccf73bddb6cbf8d6d7118dbd9cd1`, DEC-163 protocol blob `01d5080560ec5d41653694b4df086ff2f10e770d`, and predecessor DEC-151 training-core blob `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`.

The core preserves the exact EXP-051 six-regressor jackknife fit topology and six pooled out-of-fit calibration references per cell. It then builds exactly 24 additional support references per cell by scoring each view's four excluded-regime half-years separately for LONG and SHORT. Every support reference is out-of-fit for the model that produces it and contains no realized outcome, selection, validation, or holdout row.

For each EXP-051-eligible row, DEC-164 computes robust fit-temporal support as the minimum agreed-direction empirical percentile across 12 view-by-half-year comparisons. Selection ranks by support descending, pooled EXP-051 calibrated utility descending, raw robust utility descending, then row identity. Each budget freezes a support/pooled/raw cutoff triple; exact triple ties may exceed the nominal anchor.

The existing aggregate financial gate, four half-year stability windows, 10% share floor, per-window financial requirements, post-gate variant tie-break, validation chronology, holdout chronology, and no-refit forward semantics are reused unchanged. Validation and holdout, if unlocked, reuse the exact six models, six pooled references, 24 support references, and selection-derived cutoff triple.

The training core is `src/fmp/market_learning/model_successor_fit_temporal_support_utility_training.py` at Git blob `fe5664438752a161134bbed6f55d9985f1c1470a`. Focused tests are `tests/test_phase8a_exp052_fit_temporal_support_utility_training.py` at blob `fbf19a91e8225421e30f0d8ec2e5280d21ef35fd`. The detailed training-core spec is `docs/superpowers/specs/2026-09-25-phase8a-exp052-fit-temporal-support-utility-training-core.md` at blob `011945add9d080c7c454a50aacdd86b6f9582fa9`.

DEC-164 keeps accepted historical artifact loading, authoritative EXP-052 model-result execution, authoritative model fit, workflow dispatch, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization false. The next gate is a separately frozen artifact-backed EXP-052 runner/evidence contract against the exact DEC-163/164 blobs.

## DEC-165 — Phase 8A EXP-052 fit-temporal-support artifact/evidence contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-165 freezes the artifact-backed runner and aggregate evidence contract for EXP-052 against DEC-163/164. It binds DEC-163 merge `9108cd170b2eccf73bddb6cbf8d6d7118dbd9cd1`, DEC-163 protocol blob `01d5080560ec5d41653694b4df086ff2f10e770d`, DEC-164 merge `d9f893504b2d790eb73bc49edf4c0919ef2ff914`, DEC-164 training-core blob `fe5664438752a161134bbed6f55d9985f1c1470a`, predecessor DEC-151 training-core blob `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`, accepted historical artifact-loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`, and generic financial/stability artifact-helper blob `6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13`.

The contract independently validates the complete 18-cell result shape. Every cell must prove exactly six HGB regressors, six pooled EXP-051 excluded-regime references, and 24 fit-half-year support references. Support references are checked by exact view, target, parent regime, half-year name, date bounds, positive row count, finite prediction summary, row-bound prediction digest, and sorted-reference digest. A complete aggregate must therefore contain exactly 108 regressors, 108 pooled references, and 432 fit-temporal-support references.

Selection evidence must preserve the unchanged 250/500/1000 budget inventory. Available variants require a finite support/pooled/raw cutoff triple, exact 0.5-pip selection financial evidence, unchanged aggregate gate, and unchanged temporal-stability validation. Unavailable variants require null cutoffs and no stability windows. The no-challenger state is `NO_FIT_TEMPORAL_SUPPORT_UTILITY_STABLE_MODEL_CHALLENGER`; any selected variant must uniquely match one stable persisted variant by family, budget, and exact cutoff triple.

Validation and retrospective holdout preserve the frozen status chain and, if unlocked, must reuse complete support consensus evidence, the exact cutoff triple, and the frozen diagnostic/gate scenario inventory. Cell and aggregate fingerprints are independently recomputed from canonical JSON.

The artifact/evidence source is `src/fmp/market_learning/model_successor_fit_temporal_support_utility_artifacts.py` at Git blob `ae06184b9a84405119b6ed434a8973139d8ae006`. Focused tests are `tests/test_phase8a_exp052_fit_temporal_support_utility_artifacts.py` at blob `90de05fd9f74930d9c04c0432d4f6ca0fd4241ef`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp052-fit-temporal-support-utility-artifact-contract.md` at blob `e9a8c5a5745d4f2258429684f8e300813add5c29`.

DEC-165 keeps authoritative EXP-052 result execution and model fit false. The authoritative bundle rejects before source/readiness validation or historical artifact loading while the outer execution flag remains false. Workflow dispatch, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization remain false. The next gate is a separately frozen manual-main workflow/CLI/pinned-runtime source and exact-source execution gate, still non-executable.

## DEC-166 — Phase 8A EXP-052 manual-main workflow source gate

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-166 freezes the manual-main, input-free EXP-052 workflow source, public CLI, pinned numerical runtime, and exact-source execution gate against the merged DEC-163/164/165 source chain.

The frozen workflow is `.github/workflows/phase8a-exp052-fit-temporal-support-utility-model-training.yml` at Git blob `a49af5daeb14177a44154ef96b135f64a98a85bf`. It exposes only `workflow_dispatch`, accepts no user inputs, has no schedule or pull-request trigger, requires `refs/heads/main`, preserves the exact nine pair/timeframe historical artifact matrix, runs both 60m and 240m horizons, uses `max-parallel: 3`, and preserves partial cell artifacts plus the aggregate evidence artifact shape.

DEC-166 intentionally omits any first-run rejection guard. It contains no prior-run query, run-slot accounting, retry authorization, or replacement authorization. A later decision must freeze terminal review first and then independently verify run history before any one-run authorization is considered.

The public CLI is `scripts/phase8a_exp052_model_run.py` at blob `728691476a2285ec4cdec594a020aa5c84b04c5e`. Its non-status commands require the separate execution gate before readiness loading, authoritative artifact loading, cell fitting, or aggregate compilation. It contains no direct GitHub workflow-dispatch command.

The pinned runtime is `requirements/exp052-model-run.txt` at blob `d25ab16056b9f5df283147d67b8f401f60ae7520`, using Python `3.12.14` and the exact reviewed predecessor numerical package versions.

The exact-source gate is `src/fmp/market_learning/model_successor_fit_temporal_support_utility_execution_gate.py` at blob `139028be1c354a99599a3ed6505a1a4725889c02`. It binds DEC-163 merge `9108cd170b2eccf73bddb6cbf8d6d7118dbd9cd1` and protocol blob `01d5080560ec5d41653694b4df086ff2f10e770d`; DEC-164 merge `d9f893504b2d790eb73bc49edf4c0919ef2ff914` and core blob `fe5664438752a161134bbed6f55d9985f1c1470a`; DEC-165 merge `0753e85546bcef430863eceb99bdc38f43572477` and artifact-contract blob `ae06184b9a84405119b6ed434a8973139d8ae006`; the accepted historical loader; workflow; CLI; runtime; pyproject; preprocessing; feature schema; market contracts; and outcomes.

Focused tests are `tests/test_phase8a_exp052_model_workflow.py` at blob `3c40d8c8fbcbde98005e394cf15b25fb7629505f`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp052-fit-temporal-support-utility-workflow-source.md` at blob `ac1de3e0b81744078f2b6f358ad40b06eae617f4`.

DEC-166 freezes `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN = true` while keeping model-run dispatch, authoritative result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization false. Calling the execution requirement therefore fails closed.

The next gate is a separately frozen attempt-1 terminal-review contract before any one-run authorization or dispatch can be considered.

## DEC-167 — Phase 8A EXP-052 predeclared terminal-result review

**Date:** 2026-09-25
**Status:** APPROVED BEFORE ANY EXP-052 HISTORICAL RESULT OR RUN AUTHORIZATION

DEC-167 freezes the exact terminal-review contract for the future first EXP-052 historical model run before any result-producing authorization exists. It binds DEC-166 merge `2883cc46c65ff7c672c9f8d7192fc7fb240a9835`, workflow blob `a49af5daeb14177a44154ef96b135f64a98a85bf`, CLI blob `728691476a2285ec4cdec594a020aa5c84b04c5e`, and execution-gate blob `139028be1c354a99599a3ed6505a1a4725889c02`.

Only attempt 1 of the exact `phase8a-exp052-fit-temporal-support-utility-model-training` workflow on manual `main` is reviewable. The run must be completed and conclude success, failure, cancellation, or timeout. Any rerun attempt greater than 1 fails closed.

The terminal job payload must contain exactly 11 completed jobs: one authorization preflight, nine model-cell matrix jobs, and one aggregate job. Artifact names are restricted to the exact nine pair/timeframe cell namespaces plus the single aggregate namespace for the reviewed run head SHA.

A successful terminal run requires successful preflight, all nine successful matrix jobs, successful aggregate job, all nine cell artifacts, the aggregate artifact, and supplied aggregate evidence. That aggregate evidence is revalidated through DEC-165 against the run head commit and therefore must independently prove 18 cells, 108 regressors, 108 pooled references, 432 fit-temporal-support references, cutoff triples, frozen financial/stability gates, status chronology, and canonical fingerprints.

Failure, cancellation, or timeout may preserve valid partial cell artifacts but cannot claim aggregate evidence or aggregate artifact. DEC-167 records partial-job counts and opens no retry or replacement path.

The review source is `src/fmp/market_learning/model_successor_fit_temporal_support_utility_result_review.py` at Git blob `dbccea23117adbc50fa54345ec418fde54f254a3`. Focused tests are `tests/test_phase8a_exp052_model_result_review.py` at blob `a03655452521c0bad378c045f323fa63f52e2cb6`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp052-fit-temporal-support-utility-result-review.md` at blob `9af455ad0868d3e6765c8cd0294a946687713775`.

DEC-167 authorizes no dispatch, historical result execution, model fit, replacement run, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. After merge, a later decision may independently verify zero prior manual-main EXP-052 runs, add a first-run rejection guard, and authorize at most one outer historical result-producing attempt without dispatching it.

## DEC-168 — Phase 8A EXP-052 single historical model-run authorization

**Date:** 2026-09-25
**Status:** AUTHORIZED SOURCE; NO EXP-052 RUN DISPATCHED BY THIS DECISION

After DEC-167 merged, repository Actions history was independently inspected. The latest 100 runs extend back to `2026-09-24T21:06:09Z`, before DEC-166 first put the EXP-052 workflow on `main` at `2026-09-25T00:39:05Z`. Across that complete possible workflow lifetime, zero runs match the exact EXP-052 workflow path with `workflow_dispatch` on `main`.

DEC-168 binds DEC-166 merge `2883cc46c65ff7c672c9f8d7192fc7fb240a9835`, pre-authorization workflow blob `a49af5daeb14177a44154ef96b135f64a98a85bf`, CLI blob `728691476a2285ec4cdec594a020aa5c84b04c5e`, pre-authorization execution-gate blob `139028be1c354a99599a3ed6505a1a4725889c02`, DEC-167 merge `32af27a80cdb50a8be069b21ffe1757f0b6aaa10`, and DEC-167 review blob `dbccea23117adbc50fa54345ec418fde54f254a3`.

The workflow is hardened with a first-run rejection guard before runtime installation or model fitting. It verifies the exact current run identity, lists exact manual-main EXP-052 workflow runs, excludes only the current `GITHUB_RUN_ID`, and fails if any prior matching run exists. The hardened workflow blob is `c4310d4d4a58436eca75afaf147fa570ac725088`.

The authorized execution gate is `src/fmp/market_learning/model_successor_fit_temporal_support_utility_execution_gate.py` at blob `7d5fb31ee5e31d042f06426a699b06fb84237338` and records `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-168"`. Only the outer dispatch/result/protocol-result/model-fit flags are true. The underlying DEC-163 protocol, DEC-164 training core, and DEC-165 artifact-runner source-level result/fit locks remain false and are explicitly validated.

The first manual-main EXP-052 attempt consumes the slot on success, failure, cancellation, or timeout. No rerun, automatic retry, or replacement run is authorized. Any terminal outcome must route through DEC-167.

Focused workflow tests are `tests/test_phase8a_exp052_model_workflow.py` at blob `407113e0a55e9f24b3bb23fed91e19de4327d8fb`. The detailed authorization record is `docs/superpowers/specs/2026-09-25-phase8a-exp052-single-model-run-authorization.md` at blob `11ac877d0c208c3817a49323aa97a00f32dec47f`.

DEC-168 itself dispatches nothing. Replacement-run authorization, promotion, shadow/demo execution, broker mutation, live order, real-money action, and trading authorization remain false. A later separate decision must freeze a clean-main, one-way operator before any dispatch.

## DEC-169 — Phase 8A EXP-052 clean-main one-way operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY OPERATOR; NO EXP-052 RUN DISPATCHED BY THIS DECISION

DEC-169 freezes a fail-closed clean-main operator around the single historical EXP-052 attempt authorized by DEC-168. It binds DEC-168 merge `673b96906002b898dd09ff913a0efe6b9be369e3`, the DEC-166 execution-gate identity, DEC-168 execution-authorization identity, the full DEC-163 through DEC-167 source metadata returned by that gate, the hardened EXP-052 workflow/CLI identities, and the DEC-167 terminal-review contract.

The operator permits exactly three live run states: `MISSING`, `IN_PROGRESS`, and `TERMINAL`. Only `MISSING` may expose the frozen command `gh workflow run phase8a-exp052-fit-temporal-support-utility-model-training.yml --ref main -R Dtwosam/FMP`. Once any manual-main EXP-052 run exists, active or terminal, the operator exposes no second dispatch. More than one matching run is a fail-closed error.

Before reporting or dispatching, the public operator requires local branch `main`, a clean worktree, local HEAD exactly equal to freshly fetched `origin/main`, and an origin URL identifying exactly `Dtwosam/FMP`. `advance` is dry by default. `advance --execute` first obtains a read-only `next` plan, obtains a second independent `next` plan immediately before execution, and stops if the parsed reports or frozen dispatch commands differ.

Terminal runs are routed through DEC-167. For a successful run, the operator fetches the exact run/jobs/artifact payloads, requires the exact non-expired aggregate artifact name, safely extracts exactly one `model-result-evidence.json`, loads it through the DEC-165 evidence loader against the run head SHA, and supplies the aggregate evidence to DEC-167. Non-success terminal runs are reviewed without aggregate evidence. No retry, rerun, or replacement command exists.

The operator core is `src/fmp/market_learning/model_successor_fit_temporal_support_utility_operator.py` at Git blob `9e57fa87215d8e7ca373d226f8e2fec873a0fd10`. The public CLI is `scripts/phase8a_exp052_operator.py` at blob `1c4c212e3bcc16c1e241efeb9ef5986d0bc5b24d`. Focused tests are `tests/test_phase8a_exp052_operator.py` at blob `9550f0126c4fe959d0ad979a096c03bcbc9f0199`.

DEC-169 itself dispatches nothing. Replacement-run authorization, promotion, shadow/demo execution, broker mutation, live order, real-money action, and trading authorization remain false. After merge and green repository checks, a read-only clean-main operator plan must be inspected before any separately authorized first dispatch.

## DEC-170 — Phase 8A EXP-052 read-only operator plan runner

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY READ-ONLY RUNNER; NO EXP-052 DISPATCH

DEC-170 adds a repository-hosted read-only plan runner around the merged DEC-169 operator. It binds DEC-168 authorization merge `673b96906002b898dd09ff913a0efe6b9be369e3`, DEC-169 operator merge `6288eea1308186db20202e5662ca1665b17f65f6`, operator-core blob `9e57fa87215d8e7ca373d226f8e2fec873a0fd10`, public-CLI blob `1c4c212e3bcc16c1e241efeb9ef5986d0bc5b24d`, and focused operator-test blob `9550f0126c4fe959d0ad979a096c03bcbc9f0199`.

The workflow `.github/workflows/phase8a-exp052-operator-plan.yml` at blob `12f1d64b0cd97897864d90ef5f914d296e2788c2` triggers only when that workflow file itself is introduced or changed on `main`. It has read-only contents/Actions permissions and contains no manual dispatch trigger, schedule, pull-request trigger, `advance`, `advance --execute`, or direct model-workflow dispatch path.

DEC-170 incorporates the clean-worktree lessons from EXP-051: it sets `PYTHONPATH` to the checked-out source tree, installs only `requirements/exp052-model-run.txt` without editable installation, asserts the worktree is still clean, and writes `operator-plan.json` only under `RUNNER_TEMP`.

The runner executes exactly `python scripts/phase8a_exp052_operator.py next`. A successful plan must prove `operator_decision = DEC-169`, `read_only = true`, no run present, `run_state = MISSING`, and stage `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`, with the exact frozen dispatch command present only as plan evidence. The four DEC-168 outer historical-run flags must remain true while replacement/promotion/shadow/demo/broker/live/real-money/trading locks remain false.

Focused tests are `tests/test_phase8a_exp052_operator_plan_runner.py` at blob `ec653df6782c5f442c94eb973b13759712a1cc5d`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp052-operator-plan-runner.md` at blob `73debedab093bf8803fc59293f2d4d0060f49a91`.

DEC-170 changes no model-run authorization and consumes no run slot. After merge, the automatic read-only plan must succeed before any separate environment-specific executor may invoke the existing DEC-169 `advance --execute` path.

## DEC-171 — Phase 8A EXP-052 one-shot operator executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; EXECUTION ONLY THROUGH DEC-169

DEC-170 merged at `07afb1194442320f730e53b5c5d5825b053ee1a5`. Its automatic read-only plan run `36114078121` completed successfully on attempt 1 and persisted artifact `10853944005`, named `exp052-dec169-read-only-operator-plan-07afb1194442320f730e53b5c5d5825b053ee1a5`, with digest `sha256:1059a88f7e8cf00f965974edb3d3be203f5501a67ec8966068ac1ab9e348fcb9`. The plan proved the exact merged DEC-169 state was read-only, `MISSING`, and `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`, with the DEC-168 outer historical-run flags true and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

DEC-171 adds exactly one repository-hosted executor whose only execution action is `python scripts/phase8a_exp052_operator.py advance --execute`. The executor contains no direct `gh workflow run phase8a-exp052-fit-temporal-support-utility-model-training.yml` command and no model-workflow dispatch REST endpoint. All live dispatch logic remains inside DEC-169, including clean-main validation, live zero-run selection, first and second `next` plans, parsed-plan equality, frozen-command equality, and fail-closed refusal if any run appears.

The executor workflow is `.github/workflows/phase8a-exp052-operator-execute.yml` at blob `f31c5e5cfab8d00fe3e4ed6c86d92fcf87b36fff`. It triggers only when that workflow file itself is introduced or changed on `main`, has `contents: read` and `actions: write`, installs the pinned runtime without mutating the checkout, requires a clean worktree, independently revalidates the exact successful DEC-170 plan run/artifact including the artifact digest, and writes its execution receipt under `RUNNER_TEMP`.

The receipt is accepted only when DEC-169 reports `advance_execute_requested = true`, `advance_dispatchable = true`, `dispatch_submitted = true`, `result_claimed = false`, and the original live state was `MISSING` / `RUN_DISPATCH_REQUIRED`. It must also keep replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

Focused tests are `tests/test_phase8a_exp052_operator_executor.py` at blob `2c06ee1be92e2e6ba5d108bbcf11e07ed96fe2c8`. The detailed executor record is `docs/superpowers/specs/2026-09-25-phase8a-exp052-operator-executor.md` at blob `32fe44604594497c454b73239f176d4f291e1f30`.

DEC-171 does not alter the research protocol and authorizes no retry, replacement, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading. After merge, the executor's automatic push run is the only new action; if DEC-169 submits the model workflow, that resulting manual-main EXP-052 run becomes the consumed DEC-168 attempt 1 and must be observed to terminal state and reviewed through DEC-167 without rerun.

## DEC-172 — Phase 8A EXP-052 reviewed fit-temporal-support utility model result

**Date:** 2026-09-25
**Status:** REVIEWED; NO STABLE CHALLENGER; RUN SLOT CLOSED

The single DEC-168-authorized EXP-052 historical workflow run `36114617377` completed successfully on attempt 1 at execution commit `d477555cf116f07fa195de1b4a4c0d2f3b2838c5`. All 11 DEC-167-required jobs completed successfully: authorization preflight, nine pair/timeframe matrix jobs, and aggregate-model-evidence. The run produced all nine expected cell artifacts plus aggregate artifact `10855585092`, named `exp052-fit-temporal-support-utility-model-result-evidence-d477555cf116f07fa195de1b4a4c0d2f3b2838c5-from-feature-35867307338-outcome-35876715434`, with GitHub artifact digest `sha256:c7a593b2ded1f44aee447dd352d20101b54febb65be0c5f3e8a5791a1db4d263`. The downloaded ZIP independently hashes to the same value and contains exactly one `model-result-evidence.json`.

The DEC-165 aggregate evidence validates 18 cells, 108 regressors, 108 pooled calibration references, and 432 fit-temporal-support references. The stored evidence fingerprint `34e397e027a069db9344d56546b654f00bd34aff73240e5bca1d55e7b3dab7eb` recomputes exactly, and all 18 individual cell-result fingerprints also recompute exactly.

The aggregate summary records zero selected cells, 18 no-stable-challenger cells, one aggregate-selection-pass variant, zero stable-selection-pass variants, 26 unavailable budget variants, 26,392 utility-eligible selection rows, zero validation-pass cells, and zero retrospective-holdout-pass cells.

The sole aggregate pass is USDJPY 5m / 60m at budget 250 with support/pooled/raw cutoffs approximately `0.9924051599114572 / 0.9967413248462105 / 6.412340537481511`, 250 selected candidates, 248 LONG / 2 SHORT, and `1247.500000000025` total net pips. Temporal stability still rejects: 2021 H1, 2021 H2, and 2022 H1 each contain zero selected candidates; all 250 candidates occur in 2022 H2, where the variant earns the full `1247.500000000025` net pips.

The reviewed-result source is `src/fmp/market_learning/model_successor_fit_temporal_support_utility_result_decision.py` at Git blob `c9983c33792a8b143989b928a9c2af0c4ecda1e5`. Focused tests are `tests/test_phase8a_exp052_model_result_decision.py` at blob `b33dd4d825509785dc879913c81696b1d6294f3d`. The detailed reviewed-result spec is `docs/superpowers/specs/2026-09-25-phase8a-exp052-reviewed-model-result.md` at blob `6b128c2e16c32f882a775e4212900f70cee41687`.

DEC-172 closes the consumed EXP-052 run slot. Model-run dispatch, replacement run, authoritative result execution, protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization are all false. No second EXP-052 run is authorized. The next gate is a separate post-result diagnostic over immutable EXP-050/051/052 evidence before any later successor protocol is considered.

## DEC-173 — Phase 8A EXP-052 post-result diagnostics

**Date:** 2026-09-25
**Status:** APPROVED POST-RESULT DIAGNOSTIC / SUCCESSOR SOURCE DESIGN MAY OPEN

DEC-173 compares immutable reviewed EXP-050, EXP-051, and EXP-052 evidence after DEC-172 closes the consumed EXP-052 run slot. It binds DEC-172 merge `c06eb90953d1e38bd4db11ec6d7fc0d49ad0310c`, DEC-172 result-decision blob `c9983c33792a8b143989b928a9c2af0c4ecda1e5`, DEC-162 merge `3d8453c544fc4b06c691d1068828ec6da9fc7110`, DEC-162 diagnostic blob `00b9cbb5b0c95bd161d429d1f973d1e807f02a48`, and the exact EXP-050/051/052 reviewed evidence fingerprints.

All three experiments preserve 26,392 utility-eligible selection rows, 28 available variants, and 26 unavailable variants. Aggregate passes are 3 / 1 / 1 for EXP-050 / EXP-051 / EXP-052, while stable passes remain zero in all three. Every aggregate pass remains confined to USDJPY 5m / 60m.

At budget 250, realized total net pips are `612.8999999999933`, `1288.1000000000117`, and `1247.500000000025` for EXP-050/051/052. EXP-052 is `40.59999999998672` pips below EXP-051 but `634.6000000000317` above EXP-050. Candidate identity changes in every experiment.

Temporal support does not improve. Budget-250 selection-window candidate counts are `[0,0,0,250]` in EXP-050, `[0,0,3,247]` in EXP-051, and `[0,0,0,250]` in EXP-052. The fit-half-year support-first rank removes the only three 2022-H1 candidates introduced by EXP-051 and again places the entire 250-candidate aggregate-pass set in 2022 H2.

Broader ranking improves at budget 500 relative to EXP-051, from `-766.5999999999894` to `-31.50000000000273`, but still fails the aggregate gate. Budget 1000 remains unchanged at `-3.200000000010732` and also fails. EXP-050 remains the only experiment with aggregate passes at budgets 500 and 1000.

DEC-173 therefore classifies the result as `FIT_TEMPORAL_SUPPORT_DID_NOT_TRANSFER_TO_SELECTION_TIME_AND_TOP250_FINANCIAL_QUALITY_SLIGHTLY_DECLINED`. Fit-period temporal-support percentiles changed row identity but did not demonstrate transfer into selection-period temporal support.

The diagnostic source is `src/fmp/market_learning/model_successor_fit_temporal_support_utility_post_result_diagnostics.py` at blob `af57f0eb6c00e18bb587203dc81530702e657e87`. Focused tests are `tests/test_phase8a_exp052_post_result_diagnostics.py` at blob `e2850ede0f072b7739c6ce3e48e8d574df3a79de`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp052-post-result-diagnostics.md` at blob `0b27c546fb2da53a0ca9d3d570167f60a8490345`.

DEC-173 keeps EXP-052 rerun/replacement, stability-gate relaxation, removal of early windows, selection-window recalibration, selection-outcome ranking, selection-window quotas, successor result execution, successor fitting, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading false. Only successor protocol source design may open.

## DEC-174 — Phase 8A EXP-053 fit-temporal feature-support utility protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY PROTOCOL / NO EXP-053 FIT

DEC-174 opens EXP-053 as a narrow source-only successor to DEC-173. It binds DEC-173 merge `da3eb522f4178b635a261fe9ec6022d3cf94cbc8`, DEC-173 diagnostic blob `af57f0eb6c00e18bb587203dc81530702e657e87`, DEC-172 result-decision blob `c9983c33792a8b143989b928a9c2af0c4ecda1e5`, predecessor EXP-052 protocol blob `01d5080560ec5d41653694b4df086ff2f10e770d`, and predecessor result-evidence fingerprint `34e397e027a069db9344d56546b654f00bd34aff73240e5bca1d55e7b3dab7eb`.

EXP-053 preserves the complete EXP-052 utility pipeline: three jackknife views, six HGB utility regressors, positive-utility unanimous direction eligibility, six pooled excluded-regime utility references, 24 fit-half-year utility-support references, the 250/500/1000 budget anchors, unchanged aggregate financial gate, unchanged four-window temporal-stability gate, validation/holdout chronology, and no-refit forward semantics.

The sole new protocol signal is fit-temporal feature support. For each jackknife view and each of its four excluded-regime fit half-years, the already-fitted view preprocessor transforms fit-only feature rows. A frozen half-year feature reference records per-dimension center/scale over positive-scale dimensions and the sorted mean-squared standardized reference distances. There are exactly four references per view and 12 feature-support references per cell. No realized outcome and no selection, validation, or holdout row enters any feature-support reference.

A scored row is transformed through each frozen view preprocessor. Its feature support against each view-by-half-year reference is the survival percentile `count(reference_distance >= row_distance) / reference_count`. Robust fit-temporal feature support is the minimum across all 12 references.

Selection ranking becomes: robust fit-temporal feature support descending, EXP-052 robust fit-temporal utility support descending, pooled calibrated utility descending, robust raw utility descending, then row identity. The budget-th row freezes a feature-support / utility-support / pooled / raw cutoff quadruple, reused unchanged in validation and holdout.

DEC-174 explicitly forbids selection-window calibration, selection-window quotas, selection-outcome ranking, gate relaxation, feature-set changes, target changes, model-topology changes, and per-window tuning. Model-protocol result production, model fit, historical result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization remain false.

The protocol source is `src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_protocol.py` at blob `11ae3fc8e68687cc04957ed9243d8c5969227fb8`. Focused tests are `tests/test_phase8a_exp053_fit_temporal_feature_support_utility_protocol.py` at blob `42dd04bdabe791deaf0d58c42b2f5a6d5181ac30`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-fit-temporal-feature-support-utility-protocol.md` at blob `56ee7b7c12d62184615195c323ca62630ac94fae`.

The next gate is a deterministic in-memory EXP-053 training/evaluation core against this exact protocol source. That core must remain source-only and must not load accepted historical artifacts or authorize authoritative fitting/result execution.

## DEC-175 — Phase 8A EXP-053 deterministic fit-temporal feature-support training core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY IN-MEMORY CORE / NO EXP-053 HISTORICAL FIT

DEC-175 implements the deterministic in-memory EXP-053 training/evaluation core against the exact DEC-174 protocol. It binds DEC-174 merge `9687eb8ea3920e87d6681adf7366a3ce0bba7154`, DEC-174 protocol blob `11ae3fc8e68687cc04957ed9243d8c5969227fb8`, and predecessor EXP-052 training-core blob `fe5664438752a161134bbed6f55d9985f1c1470a`. The predecessor source-level model-fit and result-execution locks remain false.

The core preserves the complete EXP-052 utility pipeline: three jackknife views, six HGB utility regressors, six pooled excluded-regime calibration references, 24 fit-half-year utility-support references, unchanged positive-utility unanimous direction eligibility, 250/500/1000 budget anchors, the unchanged aggregate financial gate, the unchanged four-window temporal-stability gate, validation/holdout chronology, and no-refit forward semantics.

The only new model-selection signal is fit-temporal feature support. For each jackknife view and each of the four half-years in its excluded fit regime, the already-fitted view preprocessor transforms fit-only feature rows. The core freezes per-dimension center/scale, excludes only zero-scale dimensions from distance calculation, fails closed if no active dimension remains, computes mean-squared standardized reference distances, sorts those distances, and persists deterministic center/scale/mask/reference-distance digests. Exactly 12 feature-support references are produced per cell.

For every scored row, feature support against a reference is `count(reference_distance >= row_distance) / reference_count`, ties included. Robust fit-temporal feature support is the minimum across all 12 references. EXP-052 direction eligibility remains unchanged.

Selection ranking is frozen as feature support descending, fit-temporal utility support descending, pooled calibrated utility descending, raw utility descending, then row identity. Every available budget freezes the exact feature-support / utility-support / pooled / raw cutoff quadruple. Forward validation and holdout reuse the exact regressors, all 42 utility/feature references, and the exact selection-derived quadruple without refit or rebuilt references.

The training-core source is `src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_training.py` at Git blob `4fd0e48302f97e188a8124e1543bde0ffdb43b6f`. Focused tests are `tests/test_phase8a_exp053_fit_temporal_feature_support_utility_training.py` at blob `1be3ea372782fb3f7c133304a44304f96e9fbe25`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-fit-temporal-feature-support-utility-training-core.md`.

DEC-175 authorizes no accepted historical artifact loading, authoritative result execution, model fit, workflow dispatch, replacement run, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading. The next gate is a separate artifact/evidence contract that must independently validate 18 cells, 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, the four-part cutoff, and the unchanged forward-status chain while remaining non-executable.

## DEC-176 — Phase 8A EXP-053 artifact-backed result-evidence contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-176 freezes the artifact-backed runner and aggregate evidence contract for EXP-053. It binds DEC-174 merge `9687eb8ea3920e87d6681adf7366a3ce0bba7154`, DEC-174 protocol blob `11ae3fc8e68687cc04957ed9243d8c5969227fb8`, DEC-175 merge `60abce7c2674f9c25e4132037c9eb24cab1baf22`, DEC-175 training-core blob `4fd0e48302f97e188a8124e1543bde0ffdb43b6f`, predecessor EXP-052 training-core blob `fe5664438752a161134bbed6f55d9985f1c1470a`, predecessor EXP-052 artifact-validator blob `ae06184b9a84405119b6ed434a8973139d8ae006`, and accepted historical artifact-loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`.

For unchanged EXP-052 evidence, DEC-176 delegates to the exact frozen DEC-165 validators after normalizing only the explicit DEC-174 suffix on forbidden/excluded status labels. The predecessor validators continue to enforce the exact jackknife topology, six regressors, six pooled references, 24 utility-support references, unchanged budgets, financial gates, temporal-stability gates, scenario inventory, and forward chronology.

DEC-176 independently validates the EXP-053 feature layer: exactly four excluded-regime half-year feature references per view, 12 per cell, and 216 across the 18-cell aggregate. Every reference must prove exact window identity, positive row/dimension counts, positive active dimensions bounded by total transformed dimensions, reused preprocessor fingerprint, center/scale/active-mask/sorted-distance digests, and finite non-negative ordered distance summaries.

Selection and unlocked forward evidence must carry finite feature-support bounds within `[0,1]`, the exact feature-support reference count, and the frozen feature-support / utility-support / pooled / raw cutoff quadruple. A selected result must match exactly one stable persisted variant by budget plus all four cutoffs. Cell and aggregate fingerprints are recomputed canonically.

A complete aggregate must independently validate exactly 18 cells, 108 regressors, 108 pooled references, 432 fit-temporal utility-support references, and 216 fit-temporal feature-support references.

The artifact source is `src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_artifacts.py` at blob `431c879bf26d88e33bdf0f0965ec62566b1a3e22`. Focused tests are `tests/test_phase8a_exp053_fit_temporal_feature_support_utility_artifacts.py` at blob `6e442423d8d85467ff4f07b23584b0f04767b61f`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-fit-temporal-feature-support-utility-artifact-contract.md`.

The authoritative bundle checks its DEC-176 execution flag before source validation, readiness validation, historical artifact loading, fitting, or result compilation. That flag remains false. Model fit, workflow dispatch, replacement run, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading authorization remain false.

The next gate is a separate manual-main, input-free workflow/CLI/pinned-runtime/exact-source source freeze. That later workflow must still keep dispatch/result/fit authorization false until terminal review and one-run authorization are separately frozen.

## DEC-177 — Phase 8A EXP-053 manual-main workflow source freeze

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-177 freezes the manual-main, input-free EXP-053 workflow source, public CLI, pinned numerical runtime, and exact-source execution gate. It binds DEC-174 merge `9687eb8ea3920e87d6681adf7366a3ce0bba7154` / protocol blob `11ae3fc8e68687cc04957ed9243d8c5969227fb8`, DEC-175 merge `60abce7c2674f9c25e4132037c9eb24cab1baf22` / training-core blob `4fd0e48302f97e188a8124e1543bde0ffdb43b6f`, DEC-176 merge `a37462015ada9499fccf7ebb0a9f515e74bff1b6` / artifact-contract blob `431c879bf26d88e33bdf0f0965ec62566b1a3e22`, and the accepted historical artifact-loader blob `27c0848d16722a22b4762f5842396c2aebc92bec`.

The workflow is `.github/workflows/phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml` at blob `0a6704f75e83b06b7555dbb9dc912cda31443bbc`. It has only an input-free `workflow_dispatch` trigger, read-only contents/Actions permissions, exact merged-main checks, the frozen nine-dataset matrix, 60/240-minute horizons, max-parallel 3, exact accepted feature/outcome/readiness artifact identities, durable partial cell evidence, and deterministic aggregate evidence naming.

DEC-177 intentionally adds **no first-run guard**. Terminal review must be frozen first; only then may a separate decision verify zero prior manual-main EXP-053 runs, add a first-run rejection guard, and consider one outer result-producing authorization.

The public CLI is `scripts/phase8a_exp053_model_run.py` at blob `dbd146100d81be6ffc492de448d8dc4e0a2f4e73`. It exposes only `status`, `require-execution`, `run-cell`, and `aggregate`, checks the execution gate before readiness/artifact/model/aggregate work, binds `--code-commit` to checkout HEAD, and contains no direct GitHub workflow dispatch.

The numerical runtime is `requirements/exp053-model-run.txt` at blob `d25ab16056b9f5df283147d67b8f401f60ae7520`, with Python 3.12.14 and the same pinned numerical package set as EXP-052.

The execution gate is `src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_execution_gate.py` at blob `600ea84946fe908d143f3fbe2082b3505733cdf5`. The focused tests are `tests/test_phase8a_exp053_model_workflow.py` at blob `8a9e93f1a8dede52ec4689550327f5b0e8292928`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-fit-temporal-feature-support-utility-workflow-source.md` at blob `b317e1553015915e4cb593dbc3285f076060f154`.

DEC-177 keeps workflow dispatch, authoritative result execution, protocol-result production, model fit, replacement run, promotion, shadow/demo execution, broker mutation, live order, real-money action, and trading false. The next gate is a separately frozen attempt-1 terminal-review contract.

## DEC-178 — Phase 8A EXP-053 predeclared terminal-result review

**Date:** 2026-09-25
**Status:** APPROVED BEFORE ANY EXP-053 HISTORICAL RUN AUTHORIZATION

DEC-178 freezes the exact attempt-1 terminal-review contract for EXP-053 before any result-producing authorization exists. It binds DEC-177 merge `7faa5e765f08a47062444ebce3756bf9435ef1d4`, workflow blob `0a6704f75e83b06b7555dbb9dc912cda31443bbc`, CLI blob `dbd146100d81be6ffc492de448d8dc4e0a2f4e73`, and execution-gate blob `600ea84946fe908d143f3fbe2082b3505733cdf5`.

Only an attempt-1 manual-main run of the exact EXP-053 workflow is reviewable. The terminal job inventory must contain exactly one authorization preflight, nine completed matrix jobs, and one aggregate job. Rerun attempts are rejected.

A successful run requires all 11 jobs successful, all nine exact pair/timeframe cell artifacts, the exact aggregate artifact, and supplied aggregate evidence that passes DEC-176 validation against the run head commit. That evidence must independently prove 18 cells, 108 regressors, 108 pooled references, 432 fit-temporal utility-support references, 216 fit-temporal feature-support references, exact four-part cutoff evidence, unchanged financial/stability gates, forward chronology, and canonical fingerprints.

A non-success attempt may preserve valid partial cell artifacts but cannot claim an aggregate artifact or aggregate result evidence. The review records preflight/matrix outcomes and persisted cell-artifact count. No terminal outcome authorizes rerun or replacement.

The review source is `src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_result_review.py` at blob `c1586f8ddf48ad1125adaed7d8d8f0a476862beb`. Focused tests are `tests/test_phase8a_exp053_model_result_review.py` at blob `8a13c038afe0c73ba353f7fc645aa4279bd42b6a`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-fit-temporal-feature-support-utility-result-review.md` at blob `30fad8b0f30e7bf9fbbb70fe095478c0295994f2`.

DEC-178 authorizes no dispatch, model fit, historical result execution, replacement run, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading. The next gate is a separate zero-run verification plus first-run guard and at-most-one outer run authorization.
## DEC-179 — Phase 8A EXP-053 single guarded historical model-run authorization

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; NO EXP-053 RUN DISPATCHED BY THIS DECISION

DEC-179 independently verifies that zero prior manual-main EXP-053 workflow runs exist, hardens the DEC-177 workflow with a first-run rejection guard, binds the pre-authorization DEC-177 workflow/CLI/gate identities plus DEC-178 terminal-review identity, and opens at most one outer historical result-producing authorization.

The zero-run verification inspected the latest 100 repository Actions runs, covering `2026-09-25T00:16:23Z` through the DEC-178 merge. The EXP-053 workflow entered `main` at `2026-09-25T10:06:50Z`; across its complete possible lifetime, zero runs matched the exact workflow path, `workflow_dispatch`, and branch `main`.

The hardened workflow is `.github/workflows/phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml` at blob `4cebdc134bd4fd0edc72c4baeccee4c8185e3e1b`. Its authorization preflight now fetches the current run, verifies the exact workflow identity, lists manual-main runs for that workflow, excludes only the current run id, and fails if any prior manual-main EXP-053 run exists. The guard runs before pinned-runtime installation and before execution authorization.

The authorization gate is `src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_execution_gate.py` at blob `e26693a573237bae93e5cacbba2624904362be75`. It records authorization decision `DEC-179`, binds DEC-177 merge `7faa5e765f08a47062444ebce3756bf9435ef1d4`, pre-authorization workflow blob `0a6704f75e83b06b7555dbb9dc912cda31443bbc`, CLI blob `dbd146100d81be6ffc492de448d8dc4e0a2f4e73`, pre-authorization gate blob `600ea84946fe908d143f3fbe2082b3505733cdf5`, DEC-178 merge `132fa1621771f9fd072ba6b3a396a70e55c6883b`, and review blob `c1586f8ddf48ad1125adaed7d8d8f0a476862beb`.

Only the outer historical-run flags are opened: workflow dispatch, authoritative result execution, protocol-result production, and model fit. The underlying DEC-174 protocol, DEC-175 training core, and DEC-176 artifact-runner execution/fit locks remain false and are validated as frozen dependencies.

The first manual-main EXP-053 attempt consumes the slot on any terminal outcome. No retry, GitHub rerun, replacement run, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading is authorized. Every terminal outcome must route through DEC-178; success must revalidate the complete DEC-176 aggregate evidence including 18 cells, 108 regressors, 108 pooled references, 432 fit-temporal utility-support references, 216 fit-temporal feature-support references, and the four-part cutoff evidence.

Focused tests are `tests/test_phase8a_exp053_model_workflow.py` at blob `f7737e966592a1ae1c356d3e44b89df815fc7348`. The detailed authorization spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-single-model-run-authorization.md` at blob `0b4c1ecac60631a70e231efa8eeb25472389b9d2`.

DEC-179 itself dispatches nothing. The next gate is a clean-main, double-plan, one-way EXP-053 operator that may expose exactly one dispatch while no run exists and must route terminal evidence through DEC-178.
## DEC-180 — Phase 8A EXP-053 clean-main one-way operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY OPERATOR; NO EXP-053 RUN DISPATCHED BY THIS DECISION

DEC-180 freezes a fail-closed clean-main operator around the single historical EXP-053 attempt authorized by DEC-179. It binds DEC-179 merge `7711a726cde6fc3e827259bf9f8a0878e28eb5b4`, execution-gate decision `DEC-177`, execution-authorization decision `DEC-179`, the DEC-174 through DEC-178 source metadata returned by the gate, the hardened EXP-053 workflow/CLI identities, and the DEC-178 terminal-review contract.

The operator permits exactly three live run states: `MISSING`, `IN_PROGRESS`, and `TERMINAL`. Only `MISSING` may expose the frozen command `gh workflow run phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml --ref main -R Dtwosam/FMP`. Once any manual-main EXP-053 run exists, active or terminal, the operator exposes no second dispatch. More than one matching run is a fail-closed error.

Before reporting or dispatching, the public operator requires local branch `main`, a clean worktree, local HEAD exactly equal to freshly fetched `origin/main`, and an origin URL identifying exactly `Dtwosam/FMP`. `advance` is dry by default. `advance --execute` obtains a read-only `next` plan twice and stops if the parsed reports or frozen dispatch commands differ.

Terminal runs are routed through DEC-178. For a successful run, the operator fetches the exact run/jobs/artifact payloads, requires the exact non-expired aggregate artifact name, safely extracts exactly one `model-result-evidence.json`, loads it through the DEC-176 evidence loader against the run head SHA, and supplies the aggregate evidence to DEC-178. Non-success terminal runs are reviewed without aggregate evidence. No retry, rerun, or replacement command exists.

The operator core is `src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_operator.py` at Git blob `47455c4be8cae5e65c2157000c05f514d551ad32`. The public CLI is `scripts/phase8a_exp053_operator.py` at blob `04bad97e1c9b215b7ac8b699ddc2cb6c329331b3`. Focused tests are `tests/test_phase8a_exp053_operator.py` at blob `685feea42865fc198ce70fb27dcce0903673b79b`. The detailed operator spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-single-step-operator.md` at blob `021e21cd81e887938622a8a4f7e6fa6573e073ba`.

DEC-180 itself dispatches nothing. Replacement-run authorization, promotion, shadow/demo execution, broker mutation, live order, real-money action, and trading authorization remain false. After merge and green repository checks, a read-only clean-main operator plan must be inspected before any separately authorized first dispatch.
## DEC-181 — Phase 8A EXP-053 read-only operator plan runner

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY READ-ONLY RUNNER; NO EXP-053 DISPATCH

DEC-181 adds a repository-hosted read-only plan runner around the merged DEC-180 operator. It binds DEC-179 authorization merge `7711a726cde6fc3e827259bf9f8a0878e28eb5b4`, DEC-180 operator merge `459cca3f046c7bc143941bb0d42e4810ad3625dd`, operator-core blob `47455c4be8cae5e65c2157000c05f514d551ad32`, public-CLI blob `04bad97e1c9b215b7ac8b699ddc2cb6c329331b3`, and focused operator-test blob `685feea42865fc198ce70fb27dcce0903673b79b`.

The workflow `.github/workflows/phase8a-exp053-operator-plan.yml` at blob `ae9fac8c80758a81773f865077ad6c3e15640645` triggers only when that workflow file itself is introduced or changed on `main`. It has read-only contents/Actions permissions and contains no manual dispatch trigger, schedule, pull-request trigger, `advance`, `advance --execute`, or direct model-workflow dispatch path.

The runner preserves DEC-180's clean-worktree gate by setting `PYTHONPATH` to the checked-out source tree, installing only `requirements/exp053-model-run.txt` without editable installation, asserting the worktree remains clean, and writing `operator-plan.json` only under `RUNNER_TEMP`.

The runner executes exactly `python scripts/phase8a_exp053_operator.py next`. A successful plan must prove `operator_decision = DEC-180`, `read_only = true`, no run present, `run_state = MISSING`, and stage `FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`, with the exact frozen dispatch command present only as plan evidence. The four DEC-179 outer historical-run flags must remain true while replacement/promotion/shadow/demo/broker/live/real-money/trading locks remain false.

Focused tests are `tests/test_phase8a_exp053_operator_plan_runner.py` at blob `433744641b5767242404e85b09000bee15665aab`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-operator-plan-runner.md` at blob `13117a2885fe424db9d2c9b53cc3326342213e2c`.

DEC-181 changes no model-run authorization and consumes no run slot. After merge, the automatic read-only plan must succeed before any separate one-shot executor may invoke the existing DEC-180 `advance --execute` path.

## DEC-182 — Phase 8A EXP-053 one-shot operator executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE

DEC-182 binds the successful DEC-181 read-only plan proof before permitting any execution source. Plan run `36126977702` completed successfully on attempt 1 at `7e5d042ab7cc46c18de0f72bd4302ec9dd676e84` and persisted non-expired artifact `10860591486`, named `exp053-dec180-read-only-operator-plan-7e5d042ab7cc46c18de0f72bd4302ec9dd676e84`, with digest `sha256:9ca87fe6ec7c0ff8193ee4eef943e82053721c3fd762e5e69d7fa711471f6066`. The persisted JSON proves DEC-180, clean current main, no manual-main run, `MISSING`, `RUN_DISPATCH_REQUIRED`, the exact frozen dispatch command as plan evidence, the four DEC-179 historical-run flags true, and all replacement/promotion/trading locks false.

The executor workflow is `.github/workflows/phase8a-exp053-operator-execute.yml` at blob `d02a17528436427a8906247480615c880f9724d9`. It is path-scoped to its own introduction/change on `main`, has no manual/scheduled/PR trigger, and has only read-only contents plus Actions write permission. It independently revalidates exact DEC-181 run/artifact identity before execution.

Its sole execution-capable line is `python scripts/phase8a_exp053_operator.py advance --execute`. It contains no direct `gh workflow run` command for the EXP-053 model workflow, no dispatch REST endpoint, no retry, no GitHub rerun, and no replacement path. All live zero-run checks, clean-main checks, double planning, frozen command derivation, and actual dispatch remain inside DEC-180.

The executor accepts only a dispatch receipt proving `operator_decision = DEC-180`, explicit execute requested, dispatchable true, dispatch submitted true, result claimed false, original state `MISSING`, original stage `FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`, and all downstream locks false. The receipt is stored outside the checkout and uploaded immutably.

Focused tests are `tests/test_phase8a_exp053_operator_executor.py` at blob `7cb0ffefcffb50eade46e86780cc7a98c1db636b`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-operator-executor.md`.

DEC-182 does not authorize any second executor attempt or replacement run. If its initial merged-main executor causes DEC-180 to submit the EXP-053 model workflow, that first manual-main run consumes the DEC-179 slot on any terminal outcome and must route through DEC-178. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.

## DEC-183 — Phase 8A EXP-053 reviewed historical model result

**Date:** 2026-09-25
**Status:** REVIEWED / CLOSED / NO STABLE CHALLENGER

DEC-183 closes the single DEC-179-authorized EXP-053 historical run. DEC-182 executor run `36127676468` successfully executes the DEC-180 dispatch step, creating model run `36127730584`; its later receipt-verification step fails because the captured receipt is empty/non-JSON. That post-dispatch bookkeeping failure does not undo the submitted run and does not authorize another executor, rerun, or replacement.

Model run `36127730584` completes successfully on attempt 1 at `1a6e3670215665f2aed04d28c66c674408080953`. All 11 required jobs succeed. All nine exact cell artifacts plus the aggregate artifact are non-expired.

Aggregate artifact `10860962726`, named `exp053-fit-temporal-feature-support-utility-model-result-evidence-1a6e3670215665f2aed04d28c66c674408080953-from-feature-35867307338-outcome-35876715434`, has GitHub digest `sha256:2f52fdcf2b7e3634d7f58a33f55d31d6e20ca787e0f7dfb056233a846fb47330`. The downloaded ZIP independently reproduces that digest and contains exactly one `model-result-evidence.json`.

The aggregate evidence fingerprint `cb32abc0e4ecd3df8b639d77b6770e255aa87701eb19180dfdfb25c37dfe48e1` recomputes exactly under the DEC-176 canonical serializer. All 18 cell result fingerprints also recompute exactly. DEC-176 evidence proves 18 cells, 108 regressors, 108 pooled calibration references, 432 fit-temporal utility-support references, and 216 fit-temporal feature-support references.

EXP-053 produces 10 aggregate-selection-pass variants but zero stable-selection-pass variants. Aggregate passes occur in GBPUSD 15m/240m budget 250; GBPUSD 5m/240m budgets 250/500/1000; USDJPY 15m/60m budget 250; USDJPY 15m/240m budgets 250/500/1000; USDJPY 1h/240m budget 250; and USDJPY 5m/60m budget 1000. None clears all four unchanged half-year temporal-stability windows. Failures are driven by thin/zero 2021 coverage and/or negative 2022 H1 performance, with some GBPUSD variants additionally missing the 10% 2021 share floor.

No cell is selected. Validation and retrospective holdout remain locked for all 18 cells. Accepted model candidate count is zero.

Reviewed-result source is `src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_result_decision.py` at blob `7001c2b7944bd7b75a0c70e6fb1a775ff50ba6b5`. Focused tests are `tests/test_phase8a_exp053_model_result_decision.py` at blob `d90d51497ce6adf4ebef2fafe511588f716639eb`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-reviewed-model-result.md`.

DEC-183 closes model-run dispatch, replacement, authoritative result execution, protocol-result production, model fit, promotion, shadow/demo execution, broker mutation, live order, real-money action, and trading. No second EXP-053 run is authorized. The next safe gate is a separate post-result diagnostic over immutable EXP-050 through EXP-053 evidence.

## DEC-184 — Phase 8A EXP-053 post-result diagnostics

**Date:** 2026-09-25
**Status:** APPROVED POST-RESULT DIAGNOSTIC / SUCCESSOR SOURCE DESIGN MAY OPEN

DEC-184 compares immutable reviewed EXP-050 through EXP-053 evidence after DEC-183 closes the single consumed EXP-053 run slot. It binds DEC-183 merge `6635c874973576b5acac7ec46ee2bf4fd2bbe1ba`, DEC-183 result-decision blob `7001c2b7944bd7b75a0c70e6fb1a775ff50ba6b5`, and DEC-173 diagnostic blob `af57f0eb6c00e18bb587203dc81530702e657e87`.

All four experiments preserve 54 total variants, 28 available variants, 26 unavailable variants, and 26,392 utility-eligible selection rows. Aggregate-pass counts progress from 3 (EXP-050) to 1 (EXP-051) to 1 (EXP-052) to 10 (EXP-053), while stable-pass counts remain zero in every experiment.

EXP-053 spreads its 10 aggregate passes across six cells: four GBPUSD and six USDJPY variants, with two 60-minute-horizon and eight 240-minute-horizon passes. The exact EXP-052 pass variant USDJPY 5m / 60m / budget 250 is not retained; EXP-053 instead passes budget 1000 in that cell.

The broader aggregate success does not clear the unchanged temporal gate. All 10 EXP-053 aggregate-pass variants fail the 10% candidate-share floor in at least one 2021 half-year, five have zero 2021 H1 candidates, and nine of 10 fail the 2022 H1 financial-sign criteria. Only USDJPY 15m / 60m / budget 250 is financially positive in 2022 H1, but it still fails both 2021 windows on share.

The frozen diagnostic classification is `FEATURE_SUPPORT_BROADENED_AGGREGATE_PASSES_BUT_DID_NOT_CLEAR_TEMPORAL_STABILITY`. Feature support changed candidate identity and created some earlier-period candidates, but did not demonstrate stable transfer across the full selection chronology.

Diagnostic source is `src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_post_result_diagnostics.py` at blob `a2fce33c15422abeb8323a6e3014ebf5a3a52794`. Focused tests are `tests/test_phase8a_exp053_post_result_diagnostics.py` at blob `2029970d4f48f7667c73f123a65e9c3a5945fb81`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp053-post-result-diagnostics.md`.

DEC-184 keeps false EXP-053 rerun/replacement, stability-share/financial relaxation, removal of early windows, selection-window recalibration, selection-outcome ranking, selection-window quotas, successor result execution, successor model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading. Only a later successor protocol source design may open.

## DEC-185 — Phase 8A EXP-054 fit-temporal residual-bound utility protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-185 opens EXP-054 from the exact DEC-184 diagnostic, which proves that EXP-053 broadened aggregate financial passes to 10 across six cells but still produced zero stable challengers because every aggregate pass missed the 2021 share floor somewhere and nine of ten failed 2022 H1 financially.

EXP-054 preserves the entire EXP-053 model/eligibility/gate pipeline and adds one source-only mechanism: 24 target-specific out-of-fit residual references per cell, built from the three frozen jackknife views, four excluded-regime fit half-years per view, and two frozen LONG/SHORT utility targets. Each reference scores an excluded fit half-year with the view model, freezes residuals as realized fit-period target minus prediction, and records a fixed lower-quartile downside residual at zero-based index floor(0.25*(n-1)) with no interpolation.

For an already EXP-053-eligible row and its unanimous direction, DEC-185 forms 12 downside-adjusted lower-bound utilities by adding the appropriate frozen residual to each view prediction across its four excluded half-years. The minimum is the robust fit-temporal residual-bound utility. This score becomes the primary selection ranking signal, followed by feature support, utility support, pooled calibrated utility, raw utility, and row identity. Eligibility itself does not change.

Selection freezes a five-part residual-bound/feature-support/utility-support/pooled/raw cutoff. Validation and holdout, if ever unlocked, must reuse the exact six regressors, six pooled references, 24 utility-support references, 12 feature-support references, 24 residual references, and exact selection-derived quintuple with no refit or recalibration.

The protocol binds DEC-184 merge `f40f4b8c7d88cc2eb6c571956021ecc10b7a38a3`, DEC-184 diagnostic blob `a2fce33c15422abeb8323a6e3014ebf5a3a52794`, DEC-183 result-decision blob `7001c2b7944bd7b75a0c70e6fb1a775ff50ba6b5`, EXP-053 protocol blob `11ae3fc8e68687cc04957ed9243d8c5969227fb8`, and EXP-053 reviewed evidence fingerprint `cb32abc0e4ecd3df8b639d77b6770e255aa87701eb19180dfdfb25c37dfe48e1`.

Protocol source is `src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_protocol.py` at blob `3ffac844f9ed5308512dc3313e850cc84fb6d144`. Focused tests are `tests/test_phase8a_exp054_fit_temporal_residual_bound_utility_protocol.py` at blob `9216230ca6e3c05ab352acd4ebd87f1354ab9f70`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp054-fit-temporal-residual-bound-utility-protocol.md`.

DEC-185 explicitly keeps model protocol result production, model fitting, historical result execution, rerun/replacement behavior, selection-window calibration, selection-outcome ranking, selection-window quotas, gate relaxation, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading false. The next gate is a separate deterministic in-memory training/evaluation core.



## DEC-186 — Phase 8A EXP-054 residual-bound training primitives

**Date:** 2026-09-25
**Status:** MERGED SOURCE-ONLY / SUPERSEDED BY DEC-188 COMPLETION

DEC-186 merged at `0fc2192152824ca2c3411517dff192d240ea9cd2` and bound DEC-185 while adding deterministic residual-reference construction, exact lower-quartile residual extraction, twelve-bound robust utility scoring, and five-part lexicographic cutoff primitives. The merged training source blob was `672e5ca6003181c831ab51259dee7176f0962f6e`.

DEC-186 did not authorize model fit, authoritative result execution, workflow dispatch, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. Subsequent review found that the source did not yet expose the complete cell-level selection/validation/holdout runner required before a historical workflow could be frozen. DEC-188 therefore supersedes DEC-186 as the complete EXP-054 in-memory training/evaluation core rather than treating the missing runner as implicitly authorized behavior.

## DEC-187 — Phase 8A EXP-054 initial artifact evidence contract

**Date:** 2026-09-25
**Status:** MERGED SOURCE-ONLY / REBOUND BY DEC-188

DEC-187 merged at `1c56ec7241d5795791ac83f1b58ac875b74e9645`. It introduced the non-executable EXP-054 artifact/evidence contract, requiring 24 target-specific residual references per cell and 432 across the 18-cell universe, exact view/target/window identity, finite downside residuals, digest binding, five-part cutoff validation, deterministic evidence fingerprinting, and a fail-closed authoritative bundle entry point.

The initial artifact source was bound to the DEC-186 training blob and kept authoritative result execution and model fitting false. Because DEC-188 completes the previously missing cell runner, DEC-188 also rebinds and strengthens the artifact contract to the completed training blob. DEC-187 itself opened no historical result-producing slot.

## DEC-188 — Phase 8A EXP-054 completed deterministic core and evidence rebind

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-188 completes the EXP-054 deterministic in-memory training/evaluation core before any workflow source is permitted to open. It preserves the exact DEC-185 model family, chronological splits, six jackknife regressors, pooled calibration references, fit-temporal utility-support references, fit-temporal feature-support references, budgets, financial gates, temporal-stability windows, and no-refit forward semantics.

The completed core adds the missing end-to-end cell path: it fits only the frozen jackknife regressors, builds the 24 target-specific residual references from excluded fit half-years, scores the unchanged EXP-053 unanimous positive-utility eligibility, computes robust residual-bound utility from twelve downside-adjusted bounds, derives the frozen residual-bound/feature-support/utility-support/pooled/raw cutoff quintuple, evaluates the unchanged aggregate and temporal-stability gates, and only if selection passes applies the exact frozen models/references/cutoff to validation and retrospective holdout without refit or recalibration.

The completed training source is `src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_training.py` at blob `4f3f189c104d41352433397421f021896c03a5e9`. The amended artifact contract is version `fmp-exp054-fit-temporal-residual-bound-utility-artifact-contract-v2`, binds that exact training blob, validates exact residual window dates as well as identities/digests, and remains fail-closed before any artifact loading or authoritative model execution.

DEC-188 keeps model protocol result production, model fitting authority, historical result execution, workflow dispatch, rerun/replacement behavior, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading false. The next safe gate, only after DEC-188 source and tests are green and merged, is a separate manual-main workflow/CLI/runtime source freeze with execution still closed.


## DEC-189 — Phase 8A EXP-054 model workflow source freeze

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED

DEC-189 binds merged DEC-188 commit `9ed9adcb4c01c2281323418b1f8468ddc6ce2993`, completed training-core blob `4f3f189c104d41352433397421f021896c03a5e9`, amended artifact-contract blob `37a5cd982e0a5b6634d5dc036c44cef706d487f3`, and DEC-185 protocol blob `3ffac844f9ed5308512dc3313e850cc84fb6d144`.

It freezes a manual-main, input-free EXP-054 workflow, public CLI, and pinned Python 3.12.14 numerical runtime. The workflow preserves the exact accepted feature/outcome/readiness artifact identities used by EXP-053, covers all nine pair/timeframe datasets and both 60m/240m horizons, preserves partial cell evidence on failure, and defines deterministic aggregate evidence assembly.

DEC-189 deliberately contains no first-run guard and does not open an outer historical-run slot. The workflow source can exist on main, but its authorization preflight fails closed because model-run dispatch, authoritative result execution, model protocol result production, and model fitting remain false. A later separate terminal-review decision must be frozen before any later authorization decision may consider one guarded EXP-054 historical result-producing attempt.

Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.


## DEC-190 — Phase 8A EXP-054 predeclared terminal review

**Date:** 2026-09-25
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED

DEC-190 predeclares the exact terminal review for any later separately authorized first EXP-054 historical model-result attempt. It binds DEC-189 merge `53896a567bfce34a274398756ef96051ed7a12d9`, workflow blob `f8b8f863e6993e8da6f0a0fdabe443dd3b9a6dd8`, CLI blob `3224836570952741a83cda057da4fff7ebc78d97`, and execution-gate blob `41572a295466f7d92b03732d8899fa4c3f6a172f`.

A successful terminal review requires the exact manual-main EXP-054 workflow, attempt 1 only, all 11 required jobs completed successfully, all nine pair/timeframe cell artifacts present and non-expired, the aggregate artifact present and non-expired, and aggregate evidence that exactly reproduces under the DEC-188 deterministic evidence compiler for the reviewed head commit. Complete evidence must cover all 18 model cells and 432 fit-temporal residual references.

A terminal non-success may preserve only the cell artifacts actually produced. It cannot claim aggregate result evidence or an aggregate artifact, and it does not open a retry, rerun, or replacement attempt. The terminal outcome must route through this review before any later result decision.

DEC-190 does not authorize workflow dispatch, authoritative result execution, model-protocol result production, model fitting, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. After DEC-190 is merged and green, the next safe gate is a separate proof that no prior manual-main EXP-054 model run exists, followed by a first-run guard and at most one explicitly bounded outer historical-result slot. No run is dispatched by DEC-190.


## DEC-191 — Phase 8A EXP-054 first-run authorization gate

**Date:** 2026-09-25
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED

Before DEC-191 source was opened, repository-wide GitHub Actions history was queried for manual-main workflow dispatches. The repository reported 25 such runs and zero runs whose workflow name/path matched the EXP-054 model workflow `phase8a-exp054-fit-temporal-residual-bound-utility-model-training` / `.github/workflows/phase8a-exp054-fit-temporal-residual-bound-utility-model-training.yml`. No EXP-054 historical model-result attempt had therefore consumed the first-run slot.

DEC-191 binds merged DEC-190 commit `3aa05c66a90d4300917f277fe47637bfc483f44e` and review blob `8902699599b3e2343c8095107bc41959d2f707cf`, while preserving the DEC-189 workflow/CLI/execution-gate source identities. It hardens the manual-main workflow with a first-run rejection guard: the running workflow verifies its own identity and rejects execution if any other manual-main EXP-054 model-workflow run already exists.

Only the outer historical-result slot is opened. The execution gate may expose model-run dispatch, authoritative historical result production, model-protocol result production, and model fitting for at most one guarded attempt after this source is merged. DEC-191 itself does not dispatch the workflow, execute a model run, retry or rerun any attempt, or create a replacement path. The first manual-main attempt consumes the slot on any terminal outcome and must route through the predeclared DEC-190 terminal review.

Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate clean-main, one-way operator that can prove the exact zero-run state and derive at most one workflow-dispatch action; that operator must not itself be conflated with this authorization source.


## DEC-192 — Phase 8A EXP-054 clean-main one-way operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED

DEC-192 binds the DEC-191 one-slot authorization merged at `70925fdc418c76ab378a56235a766435fe6aedb6` and adds a clean-main, double-plan, one-way operator for the exact EXP-054 manual-main workflow. The operator verifies the local repository is on clean `main`, exactly matches fetched `origin/main`, and points at `Dtwosam/FMP` before deriving any action.

The operator classifies the exact EXP-054 manual-main workflow state as `MISSING`, `IN_PROGRESS`, or `TERMINAL`. Only `MISSING` may expose the single frozen `gh workflow run phase8a-exp054-fit-temporal-residual-bound-utility-model-training.yml --ref main -R Dtwosam/FMP` command. Before execution the public CLI recomputes the plan and requires byte-for-byte-equivalent structured state; any drift fails closed. Existing or terminal runs never expose a replacement dispatch. Terminal evidence routes through the frozen DEC-190 review contract.

DEC-192 does not itself dispatch the EXP-054 workflow, consume the DEC-191 slot, authorize a retry/rerun/replacement, or authorize promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. The next safe gate after this source and its tests are green and merged is a separate repository-hosted read-only plan runner that proves the live zero-run state without containing a dispatch path.


## DEC-193 — Phase 8A EXP-054 repository-hosted read-only plan runner

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED

DEC-193 binds merged DEC-192 commit `c93f8ef5a524c6366af24d65276b808eb152e9f7` and adds a repository-hosted read-only GitHub Actions runner for the exact DEC-192 `next` plan. The workflow is path-scoped to its own introduction or change on `main`, has no manual, scheduled, or pull-request trigger, and grants only read permissions for repository contents and Actions state.

The runner checks out exact merged `main`, requires local HEAD to equal fetched `origin/main`, installs the pinned EXP-054 numerical runtime without editable installation, proves the worktree remains clean, and writes the plan only under `RUNNER_TEMP`. It invokes only `python scripts/phase8a_exp054_operator.py next`; it contains no `advance` or `advance --execute` call and has no direct dispatch endpoint or rerun path.

A successful DEC-193 plan artifact must prove `operator_decision = DEC-192`, `run_present = false`, `run_state = MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RUN_DISPATCH_REQUIRED` stage, the frozen one-shot dispatch command as plan evidence, the four historical-run authorization fields true, and replacement/promotion/shadow/demo/broker/live/real-money/trading fields false.

DEC-193 changes no model-run authorization and consumes no run slot. Only after the merged-main read-only plan succeeds may a separate one-shot executor gate be considered. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.


## DEC-194 — Phase 8A EXP-054 read-only plan runner correction

**Date:** 2026-09-25
**Status:** APPROVED CORRECTIVE SOURCE / READ-ONLY / NOT DISPATCHED

DEC-194 records the failed first DEC-193 merged-main proof run `36147095990`. The run remained read-only and failed while importing the DEC-192 operator CLI, before any workflow-dispatch-capable action. The copied EXP-053 operator expected a dedicated artifact loader, but the frozen EXP-054 DEC-188 artifact contract exposes deterministic compile/write validation and intentionally has no `load_fit_temporal_residual_bound_utility_model_result_evidence` export.

DEC-194 removes that nonexistent import. The operator now parses the downloaded aggregate JSON locally, requires an object and exact reviewed `code_commit`, then passes the evidence to the unchanged DEC-190 terminal-review contract, which deterministically recompiles and compares the complete evidence before accepting a successful terminal result. The DEC-188 artifact-contract source and its bound blob remain unchanged.

The DEC-193 workflow trigger is also widened to its own workflow file, the EXP-054 operator CLI, and the EXP-054 operator module so future operator-source corrections automatically rerun the read-only proof on merged `main`. The workflow still has read-only permissions and invokes only DEC-192 `next`; it contains no advance, execute, direct model-workflow dispatch, retry, rerun, or replacement path.

DEC-194 consumes no DEC-191 historical-run slot and does not authorize model-workflow dispatch, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. A successful corrected merged-main DEC-193 read-only proof remains required before any one-shot executor source may open.


## DEC-195 — Phase 8A EXP-054 one-shot operator executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE

DEC-195 binds the successful corrected DEC-193 read-only proof after DEC-194. Plan run `36151472585` completed successfully on attempt 1 at `c4746803f116af2727bbbd73d5d58ed031b9adf8` and persisted non-expired artifact `10871223861`, named `exp054-dec192-read-only-operator-plan-c4746803f116af2727bbbd73d5d58ed031b9adf8`, with digest `sha256:83508d99b1fbf9be621ea309fa7012451977a0146a02cbba520b0edf9dab9c72`.

The proof establishes DEC-192 on clean current main, no existing manual-main EXP-054 run, `MISSING`, `FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`, the exact frozen dispatch command as plan evidence, the four DEC-191 historical-run fields true, and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

DEC-195 adds exactly one main-push/path-scoped executor. Its only execution-capable line is `python scripts/phase8a_exp054_operator.py advance --execute`. It contains no direct model-workflow dispatch command, no dispatch REST endpoint, no retry, no GitHub rerun, and no replacement path. Before execution it independently revalidates the exact successful plan run and artifact identity/digest, then relies on DEC-192 to perform fresh clean-main zero-run checks and double planning immediately before any dispatch.

The executor workflow is `.github/workflows/phase8a-exp054-operator-execute.yml` at blob `b051668d47c249fb42c3d27ecf5bdf9159f88279`. Focused tests are `tests/test_phase8a_exp054_operator_executor.py` at blob `b0a2cfbe22e0162ea41b65a60d50bc882730efa3`.

DEC-195 authorizes no second executor attempt and no replacement model run. If its initial merged-main executor causes DEC-192 to submit the EXP-054 model workflow, that first manual-main run consumes the DEC-191 slot on any terminal outcome and must route through DEC-190. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.


## DEC-196 — Phase 8A EXP-054 reviewed historical model result

**Date:** 2026-09-25
**Status:** REVIEWED / CLOSED / NO STABLE CHALLENGER

DEC-195 merged at `5ca369a87f8a761c3232b75f95a701043721fd36`. Executor run `36152291368` successfully submits the sole DEC-191-authorized EXP-054 historical model workflow before its receipt-verification step fails because the captured operator receipt is empty/non-JSON. That post-dispatch bookkeeping failure does not undo the submitted model run and does not authorize another executor, rerun, retry, or replacement.

Model run `36152351767` completes successfully on attempt 1 at `5ca369a87f8a761c3232b75f95a701043721fd36`. All 11 DEC-190-required jobs succeed: authorization preflight, all nine pair/timeframe model-cell jobs, and aggregate-model-evidence. All nine exact cell artifacts plus the aggregate artifact are present and non-expired.

Aggregate artifact `10873466808`, named `exp054-fit-temporal-residual-bound-utility-model-result-evidence-5ca369a87f8a761c3232b75f95a701043721fd36-from-feature-35867307338-outcome-35876715434`, has GitHub digest `sha256:d9adb29cb1bc4d9c6b2bbc65e80c168d90a7d0df909d0c1fb1377347b2ee223b`. The downloaded ZIP independently reproduces that digest and contains exactly one `model-result-evidence.json`.

The aggregate evidence fingerprint `307b576f06c6aa2fb01a267232a0de553bfa79c1bdbe6bf5d55b2bfc3b40787c` recomputes exactly under the frozen canonical serializer. All 18 cell result fingerprints also recompute exactly. Complete reviewed evidence contains 18 cells, 108 regressors, 108 pooled calibration references, 432 fit-temporal utility-support references, 216 fit-temporal feature-support references, and 432 fit-temporal residual references.

Across 54 budget variants, 28 are available and 26 unavailable. The unchanged eligibility pipeline yields 26,392 utility-eligible selection rows. EXP-054 produces exactly two aggregate-selection-pass variants: USDJPY 5m / 60m / budget 250 and USDJPY 5m / 60m / budget 1000. Both fail the unchanged temporal-stability gate. Stable-selection-pass count is zero, selected-cell count is zero, validation and retrospective holdout remain locked for all 18 cells, and accepted model candidate count is zero.

Reviewed-result source is `src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_result_decision.py` at blob `17235435604bc5c0bd8950037bd8c49a0c6fb81a`. Focused tests are `tests/test_phase8a_exp054_model_result_decision.py` at blob `4f773a996455f12652b653a29cf554dbb9a3401e`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp054-reviewed-model-result.md`.

DEC-196 closes model-run dispatch, replacement, authoritative result execution, model-protocol result production, and model fit. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. No second EXP-054 run is authorized. The next safe gate is a separate post-result diagnostic over immutable EXP-053 and EXP-054 reviewed evidence.


## DEC-197 — Phase 8A EXP-054 post-result diagnostics

**Date:** 2026-09-25
**Status:** APPROVED POST-RESULT DIAGNOSTIC / SUCCESSOR SOURCE DESIGN MAY OPEN

DEC-197 binds reviewed DEC-196 merge `fe84544b7acd3ce3a2e322b68b1ca723c216ce45`, DEC-196 result-decision blob `17235435604bc5c0bd8950037bd8c49a0c6fb81a`, and DEC-184 diagnostic blob `a2fce33c15422abeb8323a6e3014ebf5a3a52794`. It compares immutable EXP-050 through EXP-054 outcomes under unchanged 54-variant / 28-available / 26-unavailable / 26,392-eligible-row accounting.

Aggregate-pass counts progress `3 -> 1 -> 1 -> 10 -> 2` from EXP-050 through EXP-054 while stable-pass counts remain `0 -> 0 -> 0 -> 0 -> 0`. EXP-054's two aggregate passes are both USDJPY 5m / 60m, budgets 250 and 1000, reducing the EXP-053 aggregate-pass breadth from six cells to one.

In the common USDJPY 5m / 60m cell, EXP-054 changes aggregate total net pips from EXP-053 `[-352.0, -108.6, +485.2]` at budgets 250/500/1000 to approximately `[+644.3, -7.7, +302.3]`. The restored budget-250 pass is temporally concentrated entirely in 2022 H2 with candidate counts `[0,0,0,250]`. At budget 1000, EXP-053 candidate counts/net pips `[0,3,130,867]` / `[0.0,+21.2,-67.2,+531.2]` become EXP-054 `[0,3,72,925]` / `[0.0,+21.2,+510.5,-229.4]`: 2022 H1 financial sign improves, but candidate share falls from 13% to 7.2% and 2022 H2 financial quality turns negative.

The frozen diagnostic classification is `RESIDUAL_BOUND_NARROWED_AGGREGATE_PASSES_AND_IMPROVED_SOME_DOWNSIDE_WINDOWS_BUT_DID_NOT_CREATE_TEMPORAL_BREADTH`. Residual-bound ranking changes candidate identity and improves selected downside behavior in some windows, but it does not create broad chronological support or a stable challenger.

Diagnostic source is `src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_post_result_diagnostics.py` at blob `3f53e79b52d3a2e4de1e7f61e142ecc55197aa87`. Focused tests are `tests/test_phase8a_exp054_post_result_diagnostics.py` at blob `a3509469a83d2a32adf8717a6a646671f2019f29`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp054-post-result-diagnostics.md`.

DEC-197 keeps false EXP-054 rerun/replacement, stability-share/financial relaxation, removal of early stability windows, selection-window recalibration, selection-outcome ranking, selection-window quotas, successor result execution, successor model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading. Only a later successor protocol source design may open.


## DEC-198 — Phase 8A EXP-055 fit-temporal residual-breadth utility protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-198 binds merged DEC-197 commit `81271caa2ed3c2acc3257169c2f47572461cfc46`, DEC-197 diagnostic blob `3f53e79b52d3a2e4de1e7f61e142ecc55197aa87`, DEC-196 reviewed-result blob `17235435604bc5c0bd8950037bd8c49a0c6fb81a`, EXP-054 protocol blob `3ffac844f9ed5308512dc3313e850cc84fb6d144`, and EXP-054 evidence fingerprint `307b576f06c6aa2fb01a267232a0de553bfa79c1bdbe6bf5d55b2bfc3b40787c`.

DEC-197 classifies EXP-054 as `RESIDUAL_BOUND_NARROWED_AGGREGATE_PASSES_AND_IMPROVED_SOME_DOWNSIDE_WINDOWS_BUT_DID_NOT_CREATE_TEMPORAL_BREADTH`. EXP-055 addresses only that fit-period breadth question. It preserves EXP-054 row eligibility, six regressors, pooled calibration, 24 utility-support references, 12 feature-support references, 24 residual references, q=0.25 downside residuals, budgets, chronology, aggregate financial gates, four selection-period temporal-stability windows, 10% per-window share floor, per-window financial requirements, and no-refit forward semantics.

For each already eligible row and agreed direction, EXP-055 reuses the twelve EXP-054 downside-adjusted lower-bound utilities and defines `fit_temporal_residual_breadth` as the number strictly greater than zero divided by 12. No new reference vector is created and no selection, validation, or holdout outcome enters this score. The score is ranking-only and does not change eligibility.

Ranking becomes residual breadth descending, residual-bound utility descending, feature support descending, utility support descending, pooled calibrated utility descending, raw utility descending, then row identity ascending. Each budget freezes the corresponding six-part cutoff, and validation/holdout may only reuse the exact frozen models, references, breadth rule, and selection-derived cutoff without refit, recalibration, quota, or window-specific tuning.

Protocol source is `src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_protocol.py` at blob `0ef3f932cade1a62e1faf946e9a9b87cf9c98744`. Focused tests are `tests/test_phase8a_exp055_fit_temporal_residual_breadth_utility_protocol.py` at blob `b5bb56110eb15f2280749bbe2355153baa17e906`. The detailed protocol spec is `docs/superpowers/specs/2026-09-25-phase8a-exp055-fit-temporal-residual-breadth-utility-protocol.md`.

DEC-198 keeps model protocol result production, model fitting, historical result execution, EXP-054 residual-bound rule changes, stability relaxation, selection-window calibration, selection-window quotas, realized selection-outcome ranking, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading false. The next safe gate is a separate deterministic in-memory EXP-055 training/evaluation core against this exact protocol.


## DEC-199 — Phase 8A EXP-055 deterministic residual-breadth training core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-199 binds DEC-198 merge `670f5d615b837b9268f8fb807aa198e7d14d0f1a`, protocol blob `0ef3f932cade1a62e1faf946e9a9b87cf9c98744`, and frozen DEC-188 predecessor training-core blob `4f3f189c104d41352433397421f021896c03a5e9`.

The implementation delegates unchanged EXP-054 fitting, calibration, utility-support, feature-support, residual-reference, financial-gate, temporal-stability, and forward chronology mechanics to the predecessor core. It adds only the DEC-198 breadth calculation, breadth-aware consensus digest, breadth-first six-part cutoff, breadth-aware stability application, and breadth-aware forward evaluation.

For each already eligible row, the core reuses the exact twelve EXP-054 downside-adjusted lower bounds and computes fit-temporal residual breadth as the fraction strictly greater than zero. No new reference vectors are created. Candidate ranking is breadth, residual-bound utility, feature support, utility support, pooled calibrated utility, raw utility, then row identity. Budgets and all stability/financial gates remain unchanged.

The completed source exposes `run_fit_temporal_residual_breadth_utility_model_cell_core`, so DEC-199 is a full deterministic in-memory cell core rather than a partial helper gate. Source is `src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_training.py` at blob `c9517b7516940c78621448088c3933aa1c57e281`. Focused tests are `tests/test_phase8a_exp055_fit_temporal_residual_breadth_utility_training.py` at blob `cb2f4173fcefcb1a282300eb04374c0b8f468dbf`.

DEC-199 contains no artifact loading, readiness execution, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading path. All such authorizations remain false. The next safe gate after merge is a separate non-executable EXP-055 artifact/evidence contract bound to this exact core.


## DEC-200 — Phase 8A EXP-055 artifact/evidence contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-200 binds DEC-199 merge `aaa80ce43a4dbd38e52e418dd16b61642d22b2b5`, DEC-199 training-core blob `c9517b7516940c78621448088c3933aa1c57e281`, and predecessor EXP-054 artifact-contract blob `37a5cd982e0a5b6634d5dc036c44cef706d487f3`.

The contract validates complete EXP-055 cell evidence before aggregate compilation. Each cell must bind the exact experiment/protocol/training decisions, deterministic cell fingerprint, six regressors, six pooled references, 24 utility-support references, 12 feature-support references, 24 exact residual references, the twelve-bound residual-breadth inventory, breadth-aware consensus diagnostics/digest, and the three frozen budget variants. Available variants require a finite breadth/residual-bound/feature-support/utility-support/pooled/raw cutoff sextuple; unavailable budgets expose no cutoff and cannot pass selection.

Complete aggregate evidence requires all 18 exact cells and verifies 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, and the fixed twelve-bound breadth inventory. Aggregate evidence receives a deterministic fingerprint under the frozen canonical serializer.

Artifact-contract source is `src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_artifacts.py` at blob `65ca27a20d4e4fadd73c22b0b5693dc9d7ebeafb`. Focused tests are `tests/test_phase8a_exp055_fit_temporal_residual_breadth_utility_artifacts.py` at blob `ff57999b49a916efe6f6e10a2f8b8d3f8bb244fd`.

DEC-200 remains non-executable: authoritative result execution, model fit, workflow dispatch, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate after merge is a separate manual-main workflow/CLI/runtime source freeze with execution still closed.


## DEC-201 — Phase 8A EXP-055 model workflow source freeze

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED

DEC-201 binds DEC-198 merge `670f5d615b837b9268f8fb807aa198e7d14d0f1a`, DEC-199 merge `aaa80ce43a4dbd38e52e418dd16b61642d22b2b5`, DEC-200 merge `879d4a6c038277e6f69a2db971710b5ce1eaf103`, protocol blob `0ef3f932cade1a62e1faf946e9a9b87cf9c98744`, core blob `c9517b7516940c78621448088c3933aa1c57e281`, and artifact-contract blob `65ca27a20d4e4fadd73c22b0b5693dc9d7ebeafb`.

It freezes a manual-main, input-free EXP-055 workflow, public CLI, Python 3.12.14 pinned runtime, and exact-source gate. The workflow preserves the same accepted feature/outcome/readiness artifact identities as the predecessor path, covers all nine pair/timeframe datasets and both horizons, preserves partial cell evidence, and defines deterministic 18-cell aggregate compilation through DEC-200.

Workflow blob is `da5b498deb7c8d15993eaeb686127f138ce9f161`; CLI blob is `41eeb09fe0730f5184e71a9f7413a3bc5f568e63`; runtime requirements blob is `d25ab16056b9f5df283147d67b8f401f60ae7520`; execution-gate blob is `e252f0550ca1c0bdc2ea16d32bc0b6a854b1c39c`; focused workflow-test blob is `05dc61310e480e16e0376bfba4c196c2297ac660`.

DEC-201 deliberately contains no first-run guard and opens no outer historical-run slot. Model-run dispatch, authoritative result execution, model-protocol result production, and model fitting all remain false, so `require-execution` fails closed before readiness or artifact loading. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.

The next safe gate is a separate predeclared attempt-1 terminal-review contract. Only after that review is frozen may a later decision prove zero prior EXP-055 runs, add a first-run rejection guard, and consider one explicitly bounded historical-result slot.


## DEC-202 — Phase 8A EXP-055 predeclared terminal review

**Date:** 2026-09-25
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED

DEC-202 binds merged DEC-201 commit `a5825ec8008cbb9bf9783b15135faed1d7f5fb73`, workflow blob `da5b498deb7c8d15993eaeb686127f138ce9f161`, CLI blob `41eeb09fe0730f5184e71a9f7413a3bc5f568e63`, and execution-gate blob `e252f0550ca1c0bdc2ea16d32bc0b6a854b1c39c`.

The review accepts only the exact manual-main EXP-055 workflow on attempt 1. A successful terminal review requires exactly 11 completed successful jobs, all nine expected non-expired pair/timeframe cell artifacts, the exact non-expired aggregate artifact, and aggregate evidence that deterministically recompiles under DEC-200 for the reviewed head commit.

Successful aggregate revalidation verifies 18 cells, 108 regressors, 108 pooled calibration references, 432 utility-support references, 216 feature-support references, 432 residual references, the fixed twelve-bound residual-breadth inventory, and the exact evidence fingerprint. Non-success outcomes may preserve only produced cell artifacts; they cannot claim aggregate evidence/artifact and open no rerun, retry, or replacement path.

Terminal-review source is `src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_result_review.py` at blob `341d228b2521441c7d4b32d92349bc001cc78a91`. Focused tests are `tests/test_phase8a_exp055_model_result_review.py` at blob `37cf99ae72c5e444d077c98c8e2f8d8221c9b8c3`.

DEC-202 does not authorize workflow dispatch, authoritative result execution, model-protocol result production, model fitting, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. The next safe gate is a separate zero-prior-run proof plus first-run guard and, at most, one bounded outer historical-result slot.


## DEC-203 — Phase 8A EXP-055 first-run authorization gate

**Date:** 2026-09-25
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED

Before DEC-203 source was completed, the latest 100 repository GitHub Actions runs were queried. That set contained one manual-main workflow-dispatch run and zero runs whose exact workflow name/path matched `phase8a-exp055-fit-temporal-residual-breadth-utility-model-training` / `.github/workflows/phase8a-exp055-fit-temporal-residual-breadth-utility-model-training.yml`. No EXP-055 historical model-result attempt had consumed the first-run slot.

DEC-203 binds DEC-201 merge `a5825ec8008cbb9bf9783b15135faed1d7f5fb73`, DEC-201 workflow blob `da5b498deb7c8d15993eaeb686127f138ce9f161`, DEC-201 CLI blob `41eeb09fe0730f5184e71a9f7413a3bc5f568e63`, DEC-201 execution-gate blob `e252f0550ca1c0bdc2ea16d32bc0b6a854b1c39c`, DEC-202 merge `2f5be5d1f7aea4f69f6979e90a0784408b349d3f`, and DEC-202 terminal-review blob `341d228b2521441c7d4b32d92349bc001cc78a91`.

The manual-main workflow now contains a first-run rejection guard before execution authorization. The guard verifies its own exact run identity and fails closed if any other manual-main EXP-055 workflow run already exists. The guarded workflow blob is `f38e792dde45a977b19d1790bdfe94543d99eb36`.

Only the outer historical-result slot is opened. The DEC-203 execution gate may expose workflow dispatch, authoritative historical-result execution, model-protocol result production, and model fitting for at most one guarded attempt. The underlying DEC-198/199/200 protocol/core/artifact authorization constants remain false. Execution-gate blob is `ed86be7f49e57b957dd256dc99cc4d5b7b301479`; focused workflow-test blob is `31a194fa69cdd21a695edd6a46d2a934d1917c85`.

DEC-203 itself does not dispatch the workflow. The first manual-main EXP-055 attempt consumes the slot on any terminal outcome and must route through DEC-202. No rerun, retry, or replacement attempt is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate clean-main double-plan one-way operator that may derive at most one dispatch only while the exact EXP-055 workflow state remains missing.


## DEC-204 — Phase 8A EXP-055 clean-main one-way operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED

DEC-204 binds DEC-203 merge `420861c171e327d0363ed684ce57d8e8f3126d60` and freezes a clean-main, one-way EXP-055 operator. Before planning, the operator requires local `main`, clean worktree, exact equality between local HEAD and fetched `origin/main`, and an origin remote that resolves exactly to `Dtwosam/FMP`.

The operator accepts at most one exact manual-main EXP-055 workflow run and classifies live state as `MISSING`, `IN_PROGRESS`, or `TERMINAL`. Only `MISSING` may expose the exact frozen dispatch command `gh workflow run phase8a-exp055-fit-temporal-residual-breadth-utility-model-training.yml --ref main -R Dtwosam/FMP`. In-progress and terminal states never expose a dispatch or replacement action; terminal evidence routes through DEC-202.

The public CLI supports read-only `next`, non-executing `advance`, and a double-plan `advance --execute` path. Any state drift between the first and second plan fails closed. No rerun or replacement command exists.

Operator source is `src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_operator.py` at blob `5d7ee9fea71626fc370bfec81f9747d8af79b5b0`. Public CLI is `scripts/phase8a_exp055_operator.py` at blob `c8ca1f558b1f89b6db15d294145d116ac7441ac0`. Focused tests are `tests/test_phase8a_exp055_operator.py` at blob `394cde7441ecb0a14f4044898280c4cdecbbfd82`.

DEC-204 does not itself dispatch the model workflow or consume the DEC-203 slot. Replacement model runs, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a repository-hosted read-only plan runner that invokes only `next`.


## DEC-205 — Phase 8A EXP-055 repository-hosted read-only plan runner

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED

DEC-205 binds DEC-204 merge `a4a7ff734846f6444f34dcde762f41578b0cf38b` and adds a repository-hosted read-only proof for the exact DEC-204 `next` plan. Workflow `.github/workflows/phase8a-exp055-operator-plan.yml` is main-push/path scoped, grants only `contents: read` and `actions: read`, has no manual/scheduled/PR trigger, and invokes only `python scripts/phase8a_exp055_operator.py next`.

The runner checks out exact merged `main`, requires local HEAD to equal `origin/main`, installs the pinned EXP-055 numerical runtime without editable installation, proves the worktree remains clean, and writes plan output only to `RUNNER_TEMP`.

A successful DEC-205 plan must prove `operator_decision = DEC-204`, `run_present = false`, `run_state = MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RUN_DISPATCH_REQUIRED` stage, and the frozen dispatch command as read-only plan evidence. The four bounded DEC-203 historical-run fields remain true in the plan; replacement/promotion/shadow/demo/broker/live/real-money/trading fields remain false.

Workflow blob is `43f7c06aee4d551abc9e098186c8d1d75b740828`; focused test blob is `3b934e99e0b499946fb4372b27eaf3cdc06851c3`. DEC-205 changes no authorization, contains no `advance` or direct dispatch path, and consumes no historical slot. Only after the merged-main read-only proof succeeds may a separate one-shot executor be considered.


## DEC-206 — Phase 8A EXP-055 one-shot operator executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE

DEC-206 binds successful DEC-205 read-only proof run `36162871611` at merged-main commit `e91594cec316412336e04361b6032a09229af0ab`. That run completed successfully on attempt 1 and persisted non-expired artifact `10875772980`, named `exp055-dec204-read-only-operator-plan-e91594cec316412336e04361b6032a09229af0ab`, with digest `sha256:16b6f8e573b30873d4b4599da6d5bda1b12eacbb06fc322e9659e474662d0f75`.

The proof establishes DEC-204 on clean current main, no existing manual-main EXP-055 run, `MISSING`, `FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`, the exact frozen dispatch command as plan evidence, the four bounded DEC-203 historical-run fields true, and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

DEC-206 adds exactly one main-push/path-scoped executor. Its sole execution-capable action is `python scripts/phase8a_exp055_operator.py advance --execute`. It contains no direct model-workflow dispatch command, no dispatch REST endpoint, no retry, no GitHub rerun, and no replacement path. Before execution it independently revalidates the exact successful plan run and artifact identity/digest, then relies on DEC-204 to perform fresh clean-main zero-run checks and double planning immediately before any dispatch.

Executor workflow blob is `ca9e6e06a945fc6e2866ea1ea85532767fecd155`; focused test blob is `9f43afacf5a10be00c4220a4b439e34cf0929e52`.

DEC-206 authorizes no second executor attempt and no replacement model run. If its initial merged-main executor causes DEC-204 to submit the EXP-055 model workflow, that first manual-main run consumes the DEC-203 slot on any terminal outcome and must route through DEC-202. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.


## DEC-207 — Phase 8A EXP-055 reviewed historical model result

**Date:** 2026-09-25
**Status:** REVIEWED / CLOSED / NO STABLE CHALLENGER

DEC-206 merged at `fa3f90709fa71f3b49f43985c505707da3c524af`. Executor run `36163408366` successfully submitted the sole DEC-203-authorized EXP-055 historical model workflow before its receipt-verification step failed because the captured operator receipt was empty/non-JSON. That post-dispatch bookkeeping failure does not undo the submitted model run and does not authorize another executor, rerun, retry, or replacement.

Model run `36163466744` completed successfully on attempt 1 at `fa3f90709fa71f3b49f43985c505707da3c524af`. All 11 DEC-202-required jobs succeeded: authorization preflight, all nine pair/timeframe model-cell jobs, and aggregate-model-evidence. All nine exact cell artifacts plus the aggregate artifact are present and non-expired.

Aggregate artifact `10878066267`, named `exp055-fit-temporal-residual-breadth-utility-model-result-evidence-fa3f90709fa71f3b49f43985c505707da3c524af-from-feature-35867307338-outcome-35876715434`, has digest `sha256:146e07d58b7dbd1086bd2aec63abdfc50dcd4427f382ae576a27c4ac732c27ba`. The downloaded ZIP independently reproduces that digest and contains exactly one `model-result-evidence.json`.

The aggregate evidence fingerprint `f3a386dad7f23ac9d6867d030ac90e0884f3ab658c9ffecce8647048037d2510` recomputes exactly under the frozen canonical serializer. All 18 cell result fingerprints also recompute exactly. Complete reviewed evidence contains 18 cells, 108 regressors, 108 pooled calibration references, 432 fit-temporal utility-support references, 216 fit-temporal feature-support references, 432 fit-temporal residual references, and the fixed twelve-bound residual-breadth inventory.

Across 54 budget variants, 28 are available and 26 unavailable. The unchanged eligibility pipeline yields 26,392 utility-eligible selection rows. EXP-055 produces exactly two aggregate-selection-pass variants: USDJPY 5m / 60m / budget 250 and USDJPY 5m / 60m / budget 1000. Their directional-candidate counts across 2021 H1 / 2021 H2 / 2022 H1 / 2022 H2 are respectively `0 / 0 / 0 / 251` and `0 / 1 / 83 / 916`. Neither clears the unchanged temporal-stability gate. Stable-selection-pass count is zero, selected-cell count is zero, validation and retrospective holdout remain locked for all 18 cells, and accepted model candidate count is zero.

Reviewed-result source is `src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_result_decision.py` at blob `e2226117ebf10b762557d43549390c46c243bbae`. Focused tests are `tests/test_phase8a_exp055_model_result_decision.py` at blob `f9910692694e651810e6feede8945488232d2933`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp055-reviewed-model-result.md`.

DEC-207 closes model-run dispatch, replacement, authoritative result execution, model-protocol result production, and model fit. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. No second EXP-055 run is authorized. The next safe gate is a separate post-result diagnostic over immutable EXP-054 and EXP-055 reviewed evidence.


## DEC-208 — Phase 8A EXP-055 post-result diagnostic

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC

DEC-208 binds DEC-207 merge `78b1081aec39f8b79fe751ba2935ef49a1cb5ad1`, DEC-207 result-decision blob `e2226117ebf10b762557d43549390c46c243bbae`, DEC-197 diagnostic blob `3f53e79b52d3a2e4de1e7f61e142ecc55197aa87`, EXP-054 evidence fingerprint `307b576f06c6aa2fb01a267232a0de553bfa79c1bdbe6bf5d55b2bfc3b40787c`, and EXP-055 evidence fingerprint `f3a386dad7f23ac9d6867d030ac90e0884f3ab658c9ffecce8647048037d2510`.

EXP-054 and EXP-055 preserve the same 54 total variants, 28 available variants, 26 unavailable variants, and 26,392 eligible rows. They also preserve the same two aggregate-pass identities: USDJPY 5m / 60m at budgets 250 and 1000. Stable-pass count remains zero in both experiments.

For budget 250, EXP-054 produces 644.3 aggregate net pips with window counts 0/0/0/250, while EXP-055 produces 576.6 with counts 0/0/0/251 despite a residual-breadth cutoff of 10/12. High fit-period breadth therefore does not translate into selection-period chronological breadth.

For budget 1000, EXP-054 produces 302.3 aggregate net pips with counts 0/3/72/925 and window net pips 0.0/21.2/510.5/-229.4. EXP-055 produces 40.5 aggregate net pips with counts 0/1/83/916 and window net pips 0.0/-2.8/464.3/-421.0. The 2022 H1 share increases only from 7.2% to 8.3%, still below the unchanged 10% stability floor, while 2021 H2 and 2022 H2 financial quality worsen.

Across the same 28 available variants, aggregate 0.5-pip total net pips improve in 7, worsen in 16, and are unchanged in 5. This is a diagnostic comparison of overlapping variants, not an independent portfolio statistic.

DEC-208 classifies the result as `FIT_RESIDUAL_BREADTH_DID_NOT_TRANSFER_TO_SELECTION_TEMPORAL_BREADTH_AND_WEAKENED_PASS_VARIANT_FINANCIALS`. It opens successor protocol source design only. EXP-055 rerun/replacement, stability relaxation, removal of early windows, realized selection-outcome ranking, selection-window recalibration/quotas, breadth retuning on selection outcomes, successor result execution, successor model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.

Diagnostic source is `src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_post_result_diagnostics.py` at blob `5ff61be317b225d9d7ec656b4789c4561d52b522`. Focused tests are `tests/test_phase8a_exp055_post_result_diagnostics.py` at blob `ed25527485617b0e4e3e4e0119f2692907234f1f`.


## DEC-209 — Phase 8A EXP-056 fit-temporal residual lower-tail utility protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-209 binds merged DEC-208 commit `9efc720149fea77ab60e50ac0222f6ed1c458195`, DEC-208 diagnostic blob `5ff61be317b225d9d7ec656b4789c4561d52b522`, DEC-207 reviewed-result blob `e2226117ebf10b762557d43549390c46c243bbae`, EXP-055 protocol blob `0ef3f932cade1a62e1faf946e9a9b87cf9c98744`, and EXP-055 evidence fingerprint `f3a386dad7f23ac9d6867d030ac90e0884f3ab658c9ffecce8647048037d2510`.

DEC-208 classifies EXP-055 as `FIT_RESIDUAL_BREADTH_DID_NOT_TRANSFER_TO_SELECTION_TEMPORAL_BREADTH_AND_WEAKENED_PASS_VARIANT_FINANCIALS`. EXP-056 addresses only the lost continuous lower-tail margin. It preserves EXP-055 eligibility, twelve lower-bound construction, residual breadth, residual-bound utility, all support/calibration scores, budgets, chronology, aggregate financial gates, four selection-period temporal-stability windows, 10% per-window share floor, per-window financial requirements, and no-refit forward semantics.

For each already eligible row and agreed direction, EXP-056 reuses the exact twelve EXP-055 downside-adjusted lower bounds, sorts them ascending, and defines `fit_temporal_residual_lower_tail_mean` as the arithmetic mean of the three smallest values. Three is fixed because 0.25 × 12 = 3. There is no interpolation, trimming, winsorization, new reference vector, or selection/validation/holdout outcome input.

Ranking becomes lower-tail mean descending, residual breadth descending, residual-bound utility descending, feature support descending, utility support descending, pooled calibrated utility descending, raw utility descending, then row identity ascending. Each budget freezes the corresponding seven-part cutoff, and validation/holdout may only reuse the exact frozen models, references, twelve lower bounds, tail rule, breadth rule, and selection-derived cutoff without refit, recalibration, quota, or window-specific tuning.

Protocol source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_protocol.py` at blob `14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d`. Focused tests are `tests/test_phase8a_exp056_fit_temporal_residual_lower_tail_utility_protocol.py` at blob `683bc8f424f01d6e8cbb1f9478ea0140cfcdeb81`.

DEC-209 keeps model protocol result production, model fitting, historical result execution, residual-bound/breadth rule changes, stability relaxation, selection-window calibration, selection-window quotas, realized selection-outcome ranking, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading false. The next safe gate is a separate deterministic in-memory EXP-056 training/evaluation core against this exact protocol.


## DEC-210 — Phase 8A EXP-056 deterministic residual lower-tail training core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-210 binds DEC-209 merge `d2e1aabba6c0f283da6802fe315a5a29b22b503c`, protocol blob `14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d`, and frozen DEC-199 EXP-055 training-core blob `c9517b7516940c78621448088c3933aa1c57e281`.

The implementation reuses unchanged predecessor fitting, calibration, utility-support, feature-support, residual-reference, residual-bound, residual-breadth, financial-gate, temporal-stability, and forward chronology mechanics. It adds only the DEC-209 worst-three lower-tail mean, lower-tail-aware consensus digest, lower-tail-first seven-part cutoff, lower-tail-aware stability application, and matching forward evaluation.

For each already eligible row, the core reuses the exact twelve EXP-055 downside-adjusted lower bounds, sorts them ascending, and computes the arithmetic mean of the three smallest values. No new reference vectors are created. Candidate ranking is lower-tail mean, breadth, residual-bound utility, feature support, utility support, pooled calibrated utility, raw utility, then row identity. Budgets and all stability/financial gates remain unchanged.

The completed source exposes `run_fit_temporal_residual_lower_tail_utility_model_cell_core`, so DEC-210 is a full deterministic in-memory cell core rather than a partial helper gate. Source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_training.py` at blob `c472ed48e7b79d22056d43deb0fe09166ccf34c9`. Focused tests are `tests/test_phase8a_exp056_fit_temporal_residual_lower_tail_utility_training.py` at blob `abe1866e0b014591cbfe9dc19afb97d48318b31c`.

DEC-210 contains no artifact loading, readiness execution, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading path. All such authorizations remain false. The next safe gate after merge is a separate non-executable EXP-056 artifact/evidence contract bound to this exact core.


## DEC-211 — Phase 8A EXP-056 artifact/evidence contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-211 binds DEC-210 merge `029159999fae7eaa67811f8b3d8bf2bf8834e491`, DEC-210 training-core blob `c472ed48e7b79d22056d43deb0fe09166ccf34c9`, and predecessor EXP-055 artifact-contract blob `65ca27a20d4e4fadd73c22b0b5693dc9d7ebeafb`.

The contract validates complete EXP-056 cell evidence before aggregate compilation. Each cell must bind the exact experiment/protocol/training decisions, deterministic cell fingerprint, six regressors, six pooled references, 24 utility-support references, 12 feature-support references, 24 exact residual references, the twelve-bound residual-breadth inventory, the twelve-bound residual lower-tail source inventory, fixed worst-three lower-tail count, lower-tail-aware consensus diagnostics/digest, and the three frozen budget variants. Available variants require a finite lower-tail/breadth/residual-bound/feature-support/utility-support/pooled/raw cutoff septuple; unavailable budgets expose no cutoff and cannot pass selection.

Complete aggregate evidence requires all 18 exact cells and verifies 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, 12 residual-breadth bounds per eligible row, 12 lower-tail source bounds per eligible row, and a fixed lower-tail count of 3. Aggregate evidence receives a deterministic fingerprint under the frozen canonical serializer.

Artifact-contract source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_artifacts.py` at blob `f554011c092f5c4ec5d3f9b8e2330bfc974376f8`. Focused tests are `tests/test_phase8a_exp056_fit_temporal_residual_lower_tail_utility_artifacts.py` at blob `6ece494a68757f67b664bfcf0967ab2dbda41fb8`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp056-artifact-evidence-contract.md`.

DEC-211 remains non-executable: authoritative result execution, model fit, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate after merge is a separate manual-main workflow/CLI/runtime source freeze with execution still closed.


## DEC-212 — Phase 8A EXP-056 model workflow source freeze

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED

DEC-212 binds DEC-209 merge `d2e1aabba6c0f283da6802fe315a5a29b22b503c`, DEC-210 merge `029159999fae7eaa67811f8b3d8bf2bf8834e491`, DEC-211 merge `193312de6d03dc8286956f7594602f67688b1d23`, protocol blob `14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d`, training-core blob `c472ed48e7b79d22056d43deb0fe09166ccf34c9`, and artifact-contract blob `f554011c092f5c4ec5d3f9b8e2330bfc974376f8`.

It freezes a manual-main, input-free EXP-056 workflow, public CLI, Python 3.12.14 pinned runtime, and exact-source gate. The workflow preserves the same accepted feature/outcome/readiness artifact identities as the predecessor path, covers all nine pair/timeframe datasets and both horizons, preserves partial cell evidence, and defines deterministic 18-cell aggregate compilation through DEC-211.

Workflow blob is `83e5434c065167294b854b58308fec6d39d800db`; CLI blob is `30e79ef7ef20d12d75fc97103b9411b7b467ecef`; runtime requirements blob is `d25ab16056b9f5df283147d67b8f401f60ae7520`; execution-gate blob is `a81f746c8b19abc63f1bb83da0c32f1023644b94`; focused workflow-test blob is `938f2abd2f1488affcb3ce0e7a3d64c2ec0f0165`.

DEC-212 deliberately contains no first-run guard and opens no outer historical-run slot. Model-run dispatch, authoritative result execution, model-protocol result production, and model fitting all remain false, so `require-execution` fails closed before readiness or artifact loading. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.

The next safe gate is a separate predeclared attempt-1 terminal-review contract. Only after that review is frozen may a later decision prove zero prior EXP-056 runs, add a first-run rejection guard, and consider one explicitly bounded historical-result slot.


## DEC-213 — Phase 8A EXP-056 predeclared terminal review

**Date:** 2026-09-25
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED

DEC-213 binds merged DEC-212 commit `3da30377a5d358471e79a32466f93fd80cf3a02f`, workflow blob `83e5434c065167294b854b58308fec6d39d800db`, CLI blob `30e79ef7ef20d12d75fc97103b9411b7b467ecef`, and execution-gate blob `a81f746c8b19abc63f1bb83da0c32f1023644b94`.

The review accepts only the exact manual-main EXP-056 workflow on attempt 1. A successful terminal review requires exactly 11 completed successful jobs, all nine expected non-expired pair/timeframe cell artifacts, the exact non-expired aggregate artifact, and aggregate evidence that deterministically recompiles under DEC-211 for the reviewed head commit.

Successful aggregate revalidation verifies 18 cells, 108 regressors, 108 pooled calibration references, 432 utility-support references, 216 feature-support references, 432 residual references, the inherited twelve-bound residual-breadth inventory, the twelve-bound residual lower-tail source inventory, the fixed lower-tail count of 3, and the exact evidence fingerprint. Non-success outcomes may preserve only produced cell artifacts; they cannot claim aggregate evidence/artifact and open no rerun, retry, or replacement path.

Terminal-review source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_result_review.py` at blob `0bfc50d39d04d82e95c731b7284c7be143191efd`. Focused tests are `tests/test_phase8a_exp056_model_result_review.py` at blob `bf1494a3995eb40a5af9ea2210a8cbc0c20add0b`. The detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp056-terminal-review.md`.

DEC-213 does not authorize workflow dispatch, authoritative result execution, model-protocol result production, model fitting, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. The next safe gate is a separate zero-prior-run proof plus first-run guard and, at most, one bounded outer historical-result slot.


## DEC-214 — Phase 8A EXP-056 first-run authorization gate

**Date:** 2026-09-25
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED

Before DEC-214 source was completed, the latest 100 repository GitHub Actions runs were queried. That set contained one manual-main workflow-dispatch run and zero runs whose exact workflow name/path matched `phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training` / `.github/workflows/phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml`. No EXP-056 historical model-result attempt had consumed the first-run slot.

DEC-214 binds DEC-212 merge `3da30377a5d358471e79a32466f93fd80cf3a02f`, DEC-212 workflow blob `83e5434c065167294b854b58308fec6d39d800db`, DEC-212 CLI blob `30e79ef7ef20d12d75fc97103b9411b7b467ecef`, DEC-212 execution-gate blob `a81f746c8b19abc63f1bb83da0c32f1023644b94`, DEC-213 merge `af6083303e1fac29265c7ffc59eb355a313d892d`, and DEC-213 terminal-review blob `0bfc50d39d04d82e95c731b7284c7be143191efd`.

The exact manual-main workflow now contains a first-run rejection guard before execution authorization. The guard verifies its own exact run identity and fails closed if any other manual-main EXP-056 workflow run already exists. The guarded workflow blob is `cf9585ebdfea689c7b0e3ca82ac4c43488559b2a`.

Only the outer historical-result slot is opened. The DEC-214 execution gate may expose workflow dispatch, authoritative historical-result execution, model-protocol result production, and model fitting for at most one guarded attempt. The underlying DEC-209/210/211 protocol/core/artifact authorization constants remain false. Execution-gate blob is `ad3c5f8cc176952c8c8a2fcf2a626c30a5be307c`; focused workflow-test blob is `1c47614e30be29f5f1d14d0ce58dae7aa69c4674`.

DEC-214 itself does not dispatch the workflow. The first manual-main EXP-056 attempt consumes the slot on any terminal outcome and must route through DEC-213. No rerun, retry, or replacement attempt is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate clean-main double-plan one-way operator that may derive at most one dispatch only while the exact EXP-056 workflow state remains missing.


## DEC-215 — Phase 8A EXP-056 clean-main one-way operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED

DEC-215 binds DEC-214 merge `9a46e2b8e708e298691d22dcda88f4865c0289bb` and freezes a clean-main, one-way EXP-056 operator. Before planning, the operator requires local `main`, clean worktree, exact equality between local HEAD and fetched `origin/main`, and an origin remote that resolves exactly to `Dtwosam/FMP`.

The operator accepts at most one exact manual-main EXP-056 workflow run and classifies live state as `MISSING`, `IN_PROGRESS`, or `TERMINAL`. Only `MISSING` may expose the exact frozen dispatch command `gh workflow run phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml --ref main -R Dtwosam/FMP`. In-progress and terminal states never expose a dispatch or replacement action; terminal evidence routes through DEC-213.

The public CLI supports read-only `next`, non-executing `advance`, and a double-plan `advance --execute` path. Any state drift between the first and second plan fails closed. No rerun or replacement command exists.

Operator source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_operator.py` at blob `de7e4134ba29c619d9d12c9f372bfee96fc1c902`. Public CLI is `scripts/phase8a_exp056_operator.py` at blob `db626a1703cb2238948d4f832ce6e8db093880f4`. Focused tests are `tests/test_phase8a_exp056_operator.py` at blob `e20ae3068c9d7e24c49fb0fbb8057d597db9addf`.

DEC-215 does not itself dispatch the model workflow or consume the DEC-214 slot. Replacement model runs, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a repository-hosted read-only plan runner that invokes only `next`.


## DEC-216 — Phase 8A EXP-056 repository-hosted read-only operator plan

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED

DEC-216 binds DEC-215 merge `328a42ebe2248ca8200bf5d8f50d37fd28186d87` and adds a repository-hosted read-only proof for the exact DEC-215 EXP-056 `next` plan. The workflow is main-push/path scoped, grants only `contents: read` and `actions: read`, has no manual/scheduled/PR trigger, preserves a clean checkout, installs the pinned EXP-056 runtime without editable installation, writes plan output only under `RUNNER_TEMP`, and invokes only `python scripts/phase8a_exp056_operator.py next`.

A successful proof must establish `operator_decision = DEC-215`, `read_only = true`, no existing manual-main EXP-056 run, `run_state = MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RUN_DISPATCH_REQUIRED` stage, and the frozen dispatch command as plan evidence only. The four bounded DEC-214 historical-run authorization fields remain true in the plan while replacement/promotion/shadow/demo/broker/live/real-money/trading remain false.

Workflow `.github/workflows/phase8a-exp056-operator-plan.yml` is blob `921c4a93aa271b4db3816f8e4e2adb178a0a0318`. Focused tests `tests/test_phase8a_exp056_operator_plan_runner.py` are blob `1c864a53dcbadd7d87f28f96f060a5963e3c4e78`.

DEC-216 cannot invoke `advance`, `advance --execute`, a direct workflow dispatch, rerun, retry, replacement, or model-result claim. It consumes no historical slot. Only after a successful merged-main proof and exact artifact binding may a separate one-shot executor be considered.


## DEC-217 — Phase 8A EXP-056 one-shot operator executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE

DEC-217 binds successful DEC-216 read-only proof run `36175134738` at merged-main commit `8345129a80822f91f42681846f5f3a0eb63c8218`. The run completed successfully on attempt 1 and persisted non-expired artifact `10882710327`, named `exp056-dec215-read-only-operator-plan-8345129a80822f91f42681846f5f3a0eb63c8218`, with digest `sha256:dfbf6ffc5c2201e2f4a6f7e6118048d416ca6cc9f56e78cde36fae7361ccc9d3`.

The proof artifact independently confirms DEC-215 on clean current main, no existing manual-main EXP-056 run, `MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RUN_DISPATCH_REQUIRED` stage, the exact frozen dispatch command as read-only plan evidence, the four bounded DEC-214 historical-run fields true, and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

DEC-217 adds exactly one main-push/path-scoped executor. Its sole execution-capable action is `python scripts/phase8a_exp056_operator.py advance --execute`. It contains no independent model-workflow dispatch command, dispatch REST endpoint, GitHub rerun command, retry, or replacement path. Before execution it revalidates the exact DEC-216 run/artifact metadata, downloads and rehashes the plan ZIP, rechecks `operator-plan.json`, and relies on DEC-215 for fresh clean-main/live-state double planning.

After operator submission, the executor independently queries the exact EXP-056 workflow listing and requires exactly one manual-main run at the executor merge SHA on attempt 1. This observation loop does not redispatch or rerun anything.

Executor workflow `.github/workflows/phase8a-exp056-operator-execute.yml` is blob `4c3d34059692b646d36f41d1353edf8e58e662ca`. Focused tests `tests/test_phase8a_exp056_operator_executor.py` are blob `10a4cd1355fc9ee068ea32097b3f3aa7ea6fc2ef`.

DEC-217 authorizes no second executor attempt and no replacement model run. If the initial merged-main executor submits the EXP-056 historical workflow, that first attempt consumes the DEC-214 slot on any terminal outcome and must route through DEC-213. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.


## DEC-218 — Phase 8A EXP-056 reviewed failed historical result

**Date:** 2026-09-25
**Status:** REVIEWED FAILED ATTEMPT / NO MODEL RESULT

DEC-217 merged at `3ce20d7445f6837cae067c0c561002215b05b2f9`. Executor run `36175790573` completed successfully and submitted the sole DEC-214-authorized EXP-056 historical workflow. Model run `36175841645` then completed on attempt 1 with conclusion `failure`, so the EXP-056 slot is consumed.

DEC-213 non-success review applies exactly: authorization-preflight succeeded, all nine matrix jobs failed, aggregate-model-evidence was skipped, zero cell artifacts persisted, no aggregate artifact exists, and no aggregate result evidence is claimed. No replacement run is authorized.

All nine matrix failures are implementation dependency/export errors in the EXP-056 lower-tail training core's delegation through `model_successor_fit_temporal_residual_breadth_utility_training`. Eight jobs terminate because that predecessor module has no exported `MIN_STABILITY_WINDOW_CANDIDATE_SHARE`; one job reaches a later path and terminates because it has no exported `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`. DEC-218 classifies the failure as `IMPLEMENTATION_DEPENDENCY_EXPORT_DRIFT_PREVENTED_ALL_EXP056_CELL_RESULTS`.

Because no cell result artifact exists, EXP-056 has no model-selection result, aggregate financial result, evidence fingerprint, selected variant, validation result, holdout result, or accepted candidate. This failure must not be interpreted as evidence for or against the intended lower-tail ranking.

Reviewed failed-result source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_result_decision.py` at blob `75fc25ae97c03730ab75a3036059f761d8234630`. Focused tests are `tests/test_phase8a_exp056_failed_result_decision.py` at blob `9062d2aa990786e87cc6162e4c1f99b54bcc2d4a`. Detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp056-reviewed-failed-result.md`.

DEC-218 closes model-run dispatch, replacement, authoritative result execution, model-protocol result production, and model fit. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. No second EXP-056 attempt is authorized. The next safe gate is a separate source-only implementation-defect diagnostic only.


## DEC-219 — Phase 8A EXP-056 implementation-failure diagnostic

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC

DEC-219 binds DEC-218 merge `2f2171f0166f22c19482a905d6906d1cfd672275`, DEC-218 result-decision blob `75fc25ae97c03730ab75a3036059f761d8234630`, EXP-056 training-core blob `c472ed48e7b79d22056d43deb0fe09166ccf34c9`, EXP-055 predecessor training-core blob `c9517b7516940c78621448088c3933aa1c57e281`, and EXP-054 base training-core blob `4f3f189c104d41352433397421f021896c03a5e9`.

The diagnostic performs a deterministic AST audit of every direct EXP-056 `_predecessor` and `_base` dereference against the actual top-level names exported by the frozen sources. It identifies exactly seven invalid EXP-056 accesses to inherited EXP-054 constants/rules through the intermediate EXP-055 module: `FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE`, `FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL`, `FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL`, `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`, `MIN_STABILITY_WINDOW_CANDIDATE_SHARE`, `ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE`, and `ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE`. All seven exist on the frozen EXP-054 `_base` module.

The failed historical attempt directly observed two members of that seven-name set: missing `MIN_STABILITY_WINDOW_CANDIDATE_SHARE` in eight matrix jobs and missing `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL` in one later path. The other five are latent invalid dereferences not reached by the failed run.

DEC-219 classifies the failure as `EXP056_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_INTERMEDIATE_PREDECESSOR_EXPORT_DRIFT`. The exact future repair boundary is implementation-only: for a new successor experiment, replace those seven `_predecessor.<name>` accesses with `_base.<name>`, retain legitimate EXP-055 breadth-specific accesses on `_predecessor`, and change no protocol semantics, data identity, model family, chronology, ranking, budgets, financial gates, temporal-stability gates, validation, or holdout rules.

Diagnostic source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_failure_diagnostics.py` at blob `d94fb02c5037aec4c2cd2a1b020aa1317193d862`. Focused tests are `tests/test_phase8a_exp056_implementation_failure_diagnostics.py` at blob `71d3fb31e21f2873423375358ecc05097c36370d`.

DEC-219 keeps EXP-056 rerun/replacement, successor model fit, successor historical result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading false. It opens successor protocol source design only, under a new experiment identity.


## DEC-220 — Phase 8A EXP-057 implementation-repair protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-220 binds DEC-219 merge `acc0fab2219b76af061d602863c257b335a32d05`, DEC-219 diagnostic blob `d94fb02c5037aec4c2cd2a1b020aa1317193d862`, DEC-218 result-decision blob `75fc25ae97c03730ab75a3036059f761d8234630`, EXP-056 protocol blob `14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d`, and failed EXP-056 training-core blob `c472ed48e7b79d22056d43deb0fe09166ccf34c9`.

EXP-057 uses a new experiment identity because the EXP-056 historical slot is consumed, but it preserves EXP-056 model semantics exactly. The same features, targets, chronology, HGB configuration, jackknife views, eligibility, calibration/support references, residual-bound utility, residual breadth, fixed worst-three lower-tail mean, budgets, lower-tail-first seven-part ranking/cutoff, aggregate financial gates, four-window temporal stability, validation/holdout chronology, and no-refit semantics are retained.

The only newly authorized implementation change is the DEC-219 seven-name dependency-boundary repair: replace the invalid EXP-056 `_predecessor.<name>` accesses with `_base.<name>` for `FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE`, `FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL`, `FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL`, `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`, `MIN_STABILITY_WINDOW_CANDIDATE_SHARE`, `ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE`, and `ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE`. Legitimate EXP-055 breadth-specific accesses remain on `_predecessor`.

Protocol source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_protocol.py` at blob `2f355526476a4d41967bb46e1bfad6aa525cbfa9`. Focused tests are `tests/test_phase8a_exp057_implementation_repair_protocol.py` at blob `272b3683b1f21e76a0a3b0d2c5904d1604ae2efa`.

DEC-220 keeps protocol semantic changes, model-protocol result production, model fitting, historical result execution, all model/data/chronology/ranking/gate changes, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading false. The next safe gate is a source-only deterministic EXP-057 training/evaluation core implementing exactly the seven authorized dependency-root changes.


## DEC-221 — Phase 8A EXP-057 deterministic implementation-repair training core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-221 binds DEC-220 merge `865ab1569a0765078ed099008a5722f8a6d310b4`, DEC-220 protocol blob `2f355526476a4d41967bb46e1bfad6aa525cbfa9`, failed EXP-056 training-core blob `c472ed48e7b79d22056d43deb0fe09166ccf34c9`, and EXP-055 predecessor training-core blob `c9517b7516940c78621448088c3933aa1c57e281`.

The new EXP-057 core retains the complete EXP-056 model/data/chronology/ranking/gate/forward pipeline and applies exactly the seven DEC-219 dependency-root repairs. The invalid direct `_predecessor` accesses for `FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE`, `FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL`, `FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL`, `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`, `MIN_STABILITY_WINDOW_CANDIDATE_SHARE`, `ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE`, and `ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE` are absent; those inherited EXP-054 names resolve through `_base`. Legitimate EXP-055 breadth-specific accesses remain on `_predecessor`.

The implementation exposes the full deterministic `run_fit_temporal_residual_lower_tail_utility_model_cell_core`, preserving six-regressor jackknife fitting, pooled calibration, utility/feature/residual references, residual-bound utility, residual breadth, fixed worst-three lower-tail mean, lower-tail-first seven-part ranking/cutoffs, aggregate financial gates, four temporal-stability windows, validation/holdout, and no-refit semantics.

Training core is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_training.py` at blob `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`. Focused tests are `tests/test_phase8a_exp057_implementation_repair_training.py` at blob `c5bfc3cb94cc3b03523063ad19b571328854dc4c`.

DEC-221 remains non-executable. Result execution, artifact loading, readiness execution, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate non-executable EXP-057 artifact/evidence contract bound to this exact repaired core.


## DEC-222 — Phase 8A EXP-057 artifact/evidence contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-222 binds DEC-221 merge `6ea34dd3c62f72c55376e891eeb44d96ad5de54b`, repaired training-core blob `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`, and predecessor EXP-056 artifact-contract blob `f554011c092f5c4ec5d3f9b8e2330bfc974376f8`.

Every EXP-057 cell must bind the exact DEC-220/221 repair provenance, including DEC-220 merge `865ab1569a0765078ed099008a5722f8a6d310b4`, repair-protocol blob `2f355526476a4d41967bb46e1bfad6aa525cbfa9`, failed EXP-056 core blob `c472ed48e7b79d22056d43deb0fe09166ccf34c9`, and EXP-055 predecessor-core blob `c9517b7516940c78621448088c3933aa1c57e281`.

The contract preserves the inherited complete-evidence requirements: 18 exact cells, 108 regressors, 108 pooled calibration references, 432 utility-support references, 216 feature-support references, 432 residual references, 12 residual-breadth bounds per eligible row, 12 lower-tail source bounds per eligible row, fixed lower-tail count 3, the three frozen budgets, seven-part lower-tail cutoffs, deterministic cell fingerprints, and deterministic aggregate fingerprinting.

Artifact-contract source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_artifacts.py` at blob `d69eb668ade480b66faf992190b3a4929f414960`. Focused tests are `tests/test_phase8a_exp057_implementation_repair_artifacts.py` at blob `616bb6d8e1ab68336fdff4f04fb4018f36b51ffb`. Detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp057-artifact-evidence-contract.md`.

DEC-222 remains non-executable: authoritative result execution, model fit, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate manual-main EXP-057 workflow/CLI/runtime source freeze with execution still closed.


## DEC-223 — Phase 8A EXP-057 workflow/CLI/runtime source freeze

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED

DEC-223 binds DEC-220 merge `865ab1569a0765078ed099008a5722f8a6d310b4` and repair-protocol blob `2f355526476a4d41967bb46e1bfad6aa525cbfa9`, DEC-221 merge `6ea34dd3c62f72c55376e891eeb44d96ad5de54b` and repaired training-core blob `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`, and DEC-222 merge `51e9ccde9feaada7932384fc4547b721c1341588` and artifact-contract blob `d69eb668ade480b66faf992190b3a4929f414960`.

The frozen manual-main/input-free workflow is `.github/workflows/phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml` at blob `db9d8ccaa7da674124963acc6ab4e65e6c2ad83f`. It retains read-only permissions, Python 3.12.14, the exact nine pair/timeframe datasets, 60m/240m horizons, frozen feature/outcome/readiness artifacts, partial cell evidence, and deterministic aggregate evidence.

Public CLI `scripts/phase8a_exp057_model_run.py` is blob `889b2daa4e44175e0479377d6c8ea39846da596d`; runtime lock `requirements/exp057-model-run.txt` is blob `d25ab16056b9f5df283147d67b8f401f60ae7520`. The CLI requires execution authorization before readiness/artifact loading, calls the repaired DEC-222 aggregate compiler/writer and repaired DEC-221 training module, binds the actual exported deterministic cell runner, and contains no direct workflow-dispatch path.

Exact-source execution gate `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_execution_gate.py` is blob `07c7db8bc7fc29cf595aa617f1d66ec4f77e4879`. Focused tests are `tests/test_phase8a_exp057_model_workflow.py` at blob `63d12da6af913bd981081002b11e6ce3393cdb7e`.

DEC-223 intentionally has no first-run guard and opens no historical slot. Model-run dispatch, authoritative result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate predeclared attempt-1 terminal-review contract.


## DEC-224 — Phase 8A EXP-057 predeclared terminal review

**Date:** 2026-09-25
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED

DEC-224 binds merged DEC-223 commit `160c618352739a1ae12b86c80be9573e4c2f234a`, workflow blob `db9d8ccaa7da674124963acc6ab4e65e6c2ad83f`, CLI blob `889b2daa4e44175e0479377d6c8ea39846da596d`, and execution-gate blob `07c7db8bc7fc29cf595aa617f1d66ec4f77e4879`.

The review accepts only the exact manual-main EXP-057 workflow on attempt 1. A successful terminal review requires exactly 11 completed successful jobs, all nine expected non-expired pair/timeframe cell artifacts, the exact non-expired aggregate artifact, and aggregate evidence that deterministically recompiles under DEC-222 for the reviewed head commit.

Successful aggregate revalidation verifies 18 cells, 108 regressors, 108 pooled calibration references, 432 utility-support references, 216 feature-support references, 432 residual references, the inherited twelve-bound residual-breadth inventory, the twelve-bound residual lower-tail source inventory, fixed lower-tail count 3, and the exact aggregate evidence fingerprint.

Non-success outcomes may preserve only produced expected cell artifacts; they cannot claim aggregate evidence or aggregate artifact and open no rerun, retry, or replacement path. Any run attempt greater than 1 is rejected.

Terminal-review source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_result_review.py` at blob `1a5f3e86b4d445ba4a77f3496f81de2b16b333cd`. Focused tests are `tests/test_phase8a_exp057_model_result_review.py` at blob `7eeb1c27d81cacf7aa7aacbcf485aeaf97409b41`. Detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp057-terminal-review.md`.

DEC-224 does not authorize workflow dispatch, authoritative result execution, model-protocol result production, model fitting, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. The next safe gate is a separate zero-prior-run proof plus first-run guard and at most one bounded outer historical-result slot.


## DEC-225 — Phase 8A EXP-057 first-run authorization gate

**Date:** 2026-09-25
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED

Immediately before DEC-225 was frozen, the latest 100 repository Actions runs contained one manual-main workflow-dispatch run and zero runs matching the exact EXP-057 workflow name/path. No EXP-057 historical model-result attempt had consumed the first-run slot.

DEC-225 binds DEC-223 merge `160c618352739a1ae12b86c80be9573e4c2f234a`, DEC-223 workflow blob `db9d8ccaa7da674124963acc6ab4e65e6c2ad83f`, DEC-223 CLI blob `889b2daa4e44175e0479377d6c8ea39846da596d`, DEC-223 execution-gate blob `07c7db8bc7fc29cf595aa617f1d66ec4f77e4879`, DEC-224 merge `e0f2328334d6da6b52cad53f23c9a3b05eeb72cd`, and DEC-224 terminal-review blob `1a5f3e86b4d445ba4a77f3496f81de2b16b333cd`.

The exact manual-main workflow now contains a first-run rejection guard before execution authorization. The guard verifies its own exact run identity and fails closed if any other manual-main EXP-057 workflow run already exists. Guarded workflow blob is `2f28eea9f1e9cb941a91553bd6a7dc93245da7f8`.

Only the outer historical-result slot is opened. The DEC-225 execution gate may expose workflow dispatch, authoritative historical-result execution, model-protocol result production, and model fitting for at most one guarded attempt. The underlying DEC-220/221/222 protocol/core/artifact authorization constants remain false. Execution-gate blob is `2eaedc5fdde2e622f0e3394ea78ae5435b8d5347`; focused workflow-test blob is `0ff23cf161b3681f87023105cfa6f20ef3871127`.

DEC-225 itself does not dispatch the workflow. The first manual-main EXP-057 attempt consumes the slot on any terminal outcome and must route through DEC-224. No rerun, retry, or replacement attempt is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate clean-main double-plan one-way operator.


## DEC-226 — Phase 8A EXP-057 clean-main one-way operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED

DEC-226 binds DEC-225 merge `6ab3bff41b072b2a322ed1d89a3df852c8bef812` and freezes a clean-main, one-way EXP-057 operator. Before planning, the operator requires local `main`, clean worktree, exact equality between local HEAD and fetched `origin/main`, and an origin remote resolving exactly to `Dtwosam/FMP`.

The operator accepts at most one exact manual-main EXP-057 workflow run and classifies live state as `MISSING`, `IN_PROGRESS`, or `TERMINAL`. Only `MISSING` may expose the exact frozen dispatch command `gh workflow run phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml --ref main -R Dtwosam/FMP`. In-progress and terminal states never expose a dispatch or replacement action; terminal evidence routes through DEC-224.

The operator metadata binds the repaired DEC-223 gate, DEC-225 authorization, DEC-220/221/222/223/224 provenance blobs, and the guarded EXP-057 workflow/CLI identities. The public CLI supports read-only `next`, non-executing `advance`, and a double-plan `advance --execute` path. Any state drift between the first and second plans fails closed. No rerun or replacement command exists.

Operator source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_operator.py` at blob `58d0002e4d74a75fec77d3074249e505857b8603`. Public CLI is `scripts/phase8a_exp057_operator.py` at blob `2ba08d3f4411a84ff3708cc338d26f3d90bbaad4`. Focused tests are `tests/test_phase8a_exp057_operator.py` at blob `3bad42c0a55df7fe32028636a5681837e185a253`.

DEC-226 does not itself dispatch the model workflow or consume the DEC-225 slot. Replacement model runs, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a repository-hosted read-only plan runner invoking only `next`.


## DEC-227 — Phase 8A EXP-057 repository-hosted read-only operator plan

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED

DEC-227 binds DEC-226 merge `158afdc948ca5bdbb985bcc313ba420aa9da48fa` and adds a repository-hosted read-only proof for the exact DEC-226 EXP-057 `next` plan. The workflow is main-push/path scoped, grants only `contents: read` and `actions: read`, has no manual/scheduled/PR trigger, preserves a clean checkout, installs the pinned EXP-057 runtime without editable installation, writes plan output only under `RUNNER_TEMP`, and invokes only `python scripts/phase8a_exp057_operator.py next`.

A successful proof must establish `operator_decision = DEC-226`, `read_only = true`, no existing manual-main EXP-057 run, `run_state = MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RUN_DISPATCH_REQUIRED` stage, and the frozen dispatch command as plan evidence only. The four bounded DEC-225 historical-run authorization fields remain true in the plan while replacement/promotion/shadow/demo/broker/live/real-money/trading remain false.

Workflow `.github/workflows/phase8a-exp057-operator-plan.yml` is blob `c69af21d6d2c6c3b4ba0412a9668dd1f0d0a20ad`. Focused tests `tests/test_phase8a_exp057_operator_plan_runner.py` are blob `0d88c76dd6023c9f147068b7bdd512e085441b3f`. The bound operator source is blob `58d0002e4d74a75fec77d3074249e505857b8603`; the public operator CLI is blob `2ba08d3f4411a84ff3708cc338d26f3d90bbaad4`.

DEC-227 cannot invoke `advance`, `advance --execute`, a direct workflow dispatch, rerun, retry, replacement, or model-result claim. It consumes no historical slot. Only after a successful merged-main proof and exact artifact binding may a separate one-shot executor be considered.


## DEC-228 — Phase 8A EXP-057 one-shot operator executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE

DEC-228 binds successful DEC-227 read-only proof run `36192020278` at merged-main commit `7fc1396bbe983070dcbed410f43ce779f286986d`. The run completed successfully on attempt 1 and persisted non-expired artifact `10888591924`, named `exp057-dec226-read-only-operator-plan-7fc1396bbe983070dcbed410f43ce779f286986d`, with digest `sha256:92904a1e937494fcb065c414ac70fef9e4d4907bc86510d4bfaa98943982b9cf`.

The proof artifact independently confirms DEC-226 on clean current main, no existing manual-main EXP-057 run, `MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RUN_DISPATCH_REQUIRED` stage, the exact frozen dispatch command as read-only plan evidence, the four bounded DEC-225 historical-run fields true, and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

DEC-228 adds exactly one main-push/path-scoped executor. Its sole execution-capable action is `python scripts/phase8a_exp057_operator.py advance --execute`. It contains no independent model-workflow dispatch command, dispatch REST endpoint, GitHub rerun command, retry, or replacement path. Before execution it revalidates the exact DEC-227 run/artifact metadata, downloads and rehashes the plan ZIP, rechecks `operator-plan.json`, and relies on DEC-226 for fresh clean-main/live-state double planning.

After operator submission, the executor independently queries the exact EXP-057 workflow listing and requires exactly one manual-main run at the executor merge SHA on attempt 1. This observation loop does not redispatch or rerun anything.

Executor workflow `.github/workflows/phase8a-exp057-operator-execute.yml` is blob `600e428e4af0f13f56c69144e218bf5c998402a1`. Focused tests `tests/test_phase8a_exp057_operator_executor.py` are blob `b526852eff3254bbd54c6afc43cb62f8f7c706a8`.

DEC-228 authorizes no second executor attempt and no replacement model run. If the initial merged-main executor submits the EXP-057 historical workflow, that first attempt consumes the DEC-225 slot on any terminal outcome and must route through DEC-224. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.


## DEC-229 — Phase 8A EXP-057 reviewed historical result

**Date:** 2026-09-25
**Status:** REVIEWED SUCCESSFUL RUN / NO STABLE MODEL CHALLENGER

DEC-228 merged at `491a2e2715b4da7013737ecaebc65a58ac3417f9`. Executor run `36192533986` completed successfully and submitted the sole DEC-225-authorized EXP-057 historical workflow. Model run `36192572271` completed on attempt 1 with conclusion `success`, so the EXP-057 slot is consumed.

DEC-224 successful terminal review applies exactly: all 11 jobs completed successfully, all nine expected cell artifacts plus the aggregate artifact are non-expired, and the aggregate evidence deterministically recompiles under DEC-222. Reviewed aggregate artifact `10890155292` has digest `sha256:6aeeb1efa22bc515907f05c2c48bc234da2bc3d40a44117f1c0fb1d3824de3fe`; aggregate evidence fingerprint is `4bf67108e0df38d4f213d08898fadd338285ac7a2ce56920b61e4dba0f3eec4c`.

Reviewed evidence contains 18 cells, 108 regressors, 108 pooled calibration references, 432 utility-support references, 216 feature-support references, 432 residual references, 12 residual-breadth bounds, 12 residual lower-tail source bounds, fixed lower-tail count 3, 54 budget variants, 28 available variants, 26 unavailable variants, and 26,392 utility-eligible selection rows.

Exactly three variants pass the aggregate selection gate: USDJPY 5m / 60m at budgets 250, 500, and 1000. Their four temporal-window candidate counts are respectively `0/0/0/250`, `0/0/3/497`, and `0/1/73/926`. All three fail temporal stability. Consequently there are zero stable selection passes, zero selected cells, zero validation passes, zero holdout passes, and zero accepted model candidates.

DEC-229 therefore records `FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`. The EXP-057 implementation repair completed successfully and eliminated the EXP-056 dependency-export execution failure, but it did not produce a stable challenger.

Reviewed result-decision source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_result_decision.py` at blob `185e2cdf089cb6f1a12619af58fd32860366498f`. Focused tests are `tests/test_phase8a_exp057_model_result_decision.py` at blob `a1fd0bdd1a8ce87538460351630053efabda6ce3`. Detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp057-reviewed-result.md`.

DEC-229 closes model-run dispatch, replacement, authoritative result execution, model-protocol result production, and model fit. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. No second EXP-057 attempt is authorized. The next safe gate is post-result diagnostic analysis only.


## DEC-230 — Phase 8A EXP-057 post-result diagnostic

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC

DEC-230 binds DEC-229 merge `7a2c53712a85f69e106a707dc1245e664c68bcbb`, DEC-229 result-decision blob `185e2cdf089cb6f1a12619af58fd32860366498f`, DEC-208 diagnostic blob `5ff61be317b225d9d7ec656b4789c4561d52b522`, and DEC-207 EXP-055 result-decision blob `e2226117ebf10b762557d43549390c46c243bbae`.

EXP-055 is used as the nearest prior successful model-result baseline because EXP-056 failed before producing model evidence. EXP-055 and EXP-057 retain identical 54-variant accounting, 28 available variants, 26 unavailable variants, 26,392 utility-eligible selection rows, zero stable passes, and zero accepted model candidates.

EXP-057 retains the EXP-055 USDJPY 5m / 60m aggregate passes at budgets 250 and 1000 and adds budget 500, increasing aggregate-pass count from 2 to 3 without increasing stable-pass count. Across the same 28 available variants, aggregate 0.5-pip total net pips improve on 15 variants and worsen on 13, with none unchanged.

In the common USDJPY 5m / 60m cell, aggregate total net pips move from 576.6 to 301.4 at budget 250, from -470.8 to 89.0 at budget 500, and from 40.5 to 362.1 at budget 1000. The new budget-500 pass remains concentrated `0/0/3/497` across the four temporal windows. Budget 250 remains fully concentrated in 2022 H2 at `0/0/0/250`. Budget 1000 changes from `0/1/83/916` to `0/1/73/926`, increasing late-window concentration and leaving the 2022 H1 share below the unchanged 10% floor.

DEC-230 classifies the result as `LOWER_TAIL_RANKING_CHANGED_CANDIDATE_FINANCIAL_MIX_AND_ADDED_AGGREGATE_PASS_BUT_DID_NOT_CREATE_TEMPORAL_STABILITY`. The lower-tail ranking changes candidate identity and aggregate financial outcomes but still does not transfer fit-time information into selection-time chronological breadth.

Diagnostic source is `src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_post_result_diagnostics.py` at blob `09e88b85a51b858296a3af7d146251606f1d5533`. Focused tests are `tests/test_phase8a_exp057_post_result_diagnostics.py` at blob `c3486a0b9b5daf43fdf5cc66b6ddc6546d12b0cd`. Detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp057-post-result-diagnostic.md`.

DEC-230 keeps EXP-057 rerun/replacement, all temporal-gate relaxation, selection-window ranking/recalibration/quota tuning, successor fit/result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading false. Only successor protocol source design is open.


## DEC-231 — Phase 8A EXP-058 fit-temporal residual regime-floor utility protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-231 binds DEC-230 merge `b3877047fabc779b7fcc88dde847c02b5a6f5b98`, DEC-230 diagnostic blob `09e88b85a51b858296a3af7d146251606f1d5533`, DEC-229 result-decision blob `185e2cdf089cb6f1a12619af58fd32860366498f`, EXP-057 protocol blob `2f355526476a4d41967bb46e1bfad6aa525cbfa9`, and EXP-057 evidence fingerprint `4bf67108e0df38d4f213d08898fadd338285ac7a2ce56920b61e4dba0f3eec4c`.

EXP-058 preserves EXP-057 eligibility, features, targets, chronology, HGB configuration, three jackknife views, calibration/support/residual reference families, residual-bound utility, residual breadth, lower-tail mean, budgets, aggregate financial gates, four-window temporal stability, validation/holdout chronology, and no-refit semantics. It adds one fit-only ranking score derived from the existing twelve downside-adjusted lower bounds: within each jackknife view, average the four bounds belonging to that view's excluded two-year fit regime; then take the minimum of the three regime means. No new reference vector is created.

Eligible rows rank by regime-floor utility first, followed by the existing EXP-057 lower-tail, breadth, residual-bound, feature-support, utility-support, pooled-calibrated, and raw-utility stack, then row identity. Each budget freezes an eight-part numeric cutoff; exact eight-part ties may exceed budget. Forward validation/holdout reuse frozen models/references, the three derived fit-regime means, and the exact selection-derived cutoff without refit or recalibration.

Selection-window outcomes, recalibration, quotas, per-window cutoff tuning, gate relaxation, removal of early windows, validation/holdout outcome ranking, model fit, historical result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.

Protocol source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_protocol.py` at blob `8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2`. Focused tests are `tests/test_phase8a_exp058_fit_regime_floor_protocol.py` at blob `ddd14530237faa164202362bf24886c7c03cba0a`. Detailed spec is `docs/superpowers/specs/2026-09-25-phase8a-exp058-fit-regime-floor-protocol.md`.

The next safe gate is a deterministic in-memory EXP-058 training/evaluation core only.


## DEC-232 — Phase 8A EXP-058 deterministic residual regime-floor training core

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-232 binds DEC-231 merge `a6926703d787a7fe0e2ba34261d14c4c4d362df2`, DEC-231 protocol blob `8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2`, and predecessor DEC-221 repaired lower-tail training-core blob `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`.

The implementation reuses the repaired EXP-057 fit/reference/financial/stability/forward machinery and adds only the DEC-231 regime-floor score and its eight-part cutoff. For each already eligible row and agreed direction, the exact twelve frozen downside-adjusted residual bounds are grouped by the three jackknife views. Each view contributes four bounds from the excluded two-year fit regime; the core computes the arithmetic mean of each four-bound group and defines the regime-floor utility as the minimum of the three means. No new reference vector is created and no selection, validation, or holdout outcome enters the score.

Eligible rows rank by regime-floor utility, residual lower-tail mean, residual breadth, residual-bound utility, feature support, utility support, pooled calibrated utility, raw utility, then row identity. Each 250/500/1000 budget freezes the corresponding eight-part cutoff. Aggregate financial gates, the four temporal-stability windows, the 10% candidate-share floor, validation/holdout chronology, and no-refit semantics remain unchanged.

The completed source exposes `run_fit_temporal_residual_regime_floor_utility_model_cell_core`, plus regime-floor-aware forward and temporal-stability evaluators. Training core source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_training.py` at blob `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`. Focused tests are `tests/test_phase8a_exp058_fit_regime_floor_training.py` at blob `8eebe590bd9125b8d778136e654c83442de62436`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp058-regime-floor-training-core.md`.

DEC-232 contains no artifact loading, readiness execution, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading path. All such authorizations remain false. The next safe gate after merge is a separate non-executable EXP-058 artifact/evidence contract bound to this exact core.


## DEC-233 — Phase 8A EXP-058 artifact/evidence contract

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-233 binds DEC-232 merge `24cb20bb0b1e3aa25f1ea87e1cfbba22587a0ae6`, DEC-232 training-core blob `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`, and predecessor EXP-057 artifact-contract blob `d69eb668ade480b66faf992190b3a4929f414960`.

The contract validates complete EXP-058 cell evidence before aggregate compilation. Each cell must bind the exact experiment/protocol/training decisions, deterministic cell fingerprint, six regressors, six pooled references, 24 utility-support references, 12 feature-support references, 24 exact residual references, the twelve-bound residual-breadth inventory, the twelve-bound lower-tail source inventory, fixed lower-tail count of 3, exactly three residual fit regimes with four windows each, the twelve-bound regime-floor source inventory, regime-floor-aware consensus diagnostics/digest, and the three frozen budget variants. Available variants require a finite regime-floor/lower-tail/breadth/residual-bound/feature-support/utility-support/pooled/raw cutoff octuple; unavailable budgets expose no cutoff and cannot pass selection.

Complete aggregate evidence requires all 18 exact cells and verifies 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, 12 breadth bounds per eligible row, 12 lower-tail source bounds per eligible row, lower-tail count 3, regime count 3, four windows per regime, and 12 regime-floor source bounds per eligible row. Aggregate evidence receives a deterministic fingerprint under the frozen canonical serializer.

Artifact-contract source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_artifacts.py` at blob `5a34f354b68e14bb7116c79f15f9cfebe149a811`. Focused tests are `tests/test_phase8a_exp058_regime_floor_artifacts.py` at blob `7338dd5cba39e98c9e56a1b352444a543a1e227c`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp058-artifact-evidence-contract.md`.

DEC-233 remains non-executable: authoritative result execution, model fit, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate after merge is a separate manual-main workflow/CLI/runtime source freeze with execution still closed.


## DEC-234 — Phase 8A EXP-058 workflow/CLI/runtime source freeze

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED

DEC-234 binds DEC-231 merge `a6926703d787a7fe0e2ba34261d14c4c4d362df2` and protocol blob `8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2`, DEC-232 merge `24cb20bb0b1e3aa25f1ea87e1cfbba22587a0ae6` and training-core blob `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`, and DEC-233 merge `5425184a53b2bd5241291f9d561f47b69ca4d134` and artifact-contract blob `5a34f354b68e14bb7116c79f15f9cfebe149a811`.

The frozen manual-main/input-free workflow is `.github/workflows/phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training.yml` at blob `78e9bf66ade5f6fb42ebe27e28b7ba24f36741b8`. It retains read-only permissions, Python 3.12.14, the exact nine pair/timeframe datasets, 60m/240m horizons, frozen feature/outcome/readiness artifacts, partial cell evidence, and deterministic aggregate evidence.

Public CLI `scripts/phase8a_exp058_model_run.py` is blob `e35a6ee0ff11bd3928b3bf05bf19f3572f64952c`; runtime lock `requirements/exp058-model-run.txt` is blob `d25ab16056b9f5df283147d67b8f401f60ae7520`. The CLI requires execution authorization before readiness/artifact loading, calls the regime-floor DEC-232 cell core and DEC-233 aggregate compiler/writer, and contains no direct workflow-dispatch path.

Exact-source execution gate `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_execution_gate.py` is blob `74881c0fee21392872ffd3df1378639bb04fea4a`. Focused tests are `tests/test_phase8a_exp058_model_workflow.py` at blob `ba3e43ffc121fa6eae4b46148622a3f01c1e4e84`.

DEC-234 intentionally has no first-run guard and opens no historical slot. Model-run dispatch, authoritative result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate predeclared attempt-1 terminal-review contract.


## DEC-235 — Phase 8A EXP-058 predeclared terminal review

**Date:** 2026-09-26
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED

DEC-235 binds merged DEC-234 commit `365093ea81fdaf871680b42b02d67ebce3768d34`, workflow blob `78e9bf66ade5f6fb42ebe27e28b7ba24f36741b8`, CLI blob `e35a6ee0ff11bd3928b3bf05bf19f3572f64952c`, and execution-gate blob `74881c0fee21392872ffd3df1378639bb04fea4a`.

The review accepts only the exact manual-main EXP-058 regime-floor workflow on attempt 1. A successful terminal review requires exactly 11 completed successful jobs, all nine expected non-expired pair/timeframe cell artifacts, the exact non-expired aggregate artifact, and aggregate evidence that deterministically recompiles under DEC-233 for the reviewed head commit.

Successful aggregate revalidation verifies 18 cells, 108 regressors, 108 pooled calibration references, 432 utility-support references, 216 feature-support references, 432 residual references, the inherited twelve-bound residual-breadth inventory, the twelve-bound residual lower-tail source inventory, fixed lower-tail count 3, three residual fit regimes, four residual windows per regime, twelve regime-floor source bounds per eligible row, and the exact aggregate evidence fingerprint.

Non-success outcomes may preserve only produced expected cell artifacts; they cannot claim aggregate evidence or aggregate artifact and open no rerun, retry, or replacement path. Any run attempt greater than 1 is rejected.

Terminal-review source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_result_review.py` at blob `76ba5de3ef92c02a8139213040dc3cf4d8efd75c`. Focused tests are `tests/test_phase8a_exp058_model_result_review.py` at blob `3a71fde170622be55f43261625b5fabf20a178eb`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp058-terminal-review.md`.

DEC-235 does not authorize workflow dispatch, authoritative result execution, model-protocol result production, model fitting, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. The next safe gate is a separate zero-prior-run proof plus first-run guard and at most one bounded outer historical-result slot.


## DEC-236 — Phase 8A EXP-058 first-run authorization gate

**Date:** 2026-09-26
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED

Immediately before DEC-236 was frozen, the latest 100 repository Actions runs contained zero exact manual-main workflow-dispatch runs matching the EXP-058 regime-floor workflow name/path. No EXP-058 historical model-result attempt had consumed the first-run slot.

DEC-236 binds DEC-234 merge `365093ea81fdaf871680b42b02d67ebce3768d34`, DEC-234 workflow blob `78e9bf66ade5f6fb42ebe27e28b7ba24f36741b8`, DEC-234 CLI blob `e35a6ee0ff11bd3928b3bf05bf19f3572f64952c`, DEC-234 execution-gate blob `74881c0fee21392872ffd3df1378639bb04fea4a`, DEC-235 merge `a2e8614a87358763a838d8b02728f7c8216bc9d5`, and DEC-235 terminal-review blob `76ba5de3ef92c02a8139213040dc3cf4d8efd75c`.

The exact manual-main workflow now contains a first-run rejection guard before execution authorization. The guard verifies its own exact run identity and fails closed if any other manual-main EXP-058 workflow run already exists. Guarded workflow blob is `9de995c0471e40539be679077db4ebc8fe33590c`.

Only the outer historical-result slot is opened. The DEC-236 execution gate may expose workflow dispatch, authoritative historical-result execution, model-protocol result production, and model fitting for at most one guarded attempt. The underlying DEC-231/232/233 protocol/core/artifact authorization constants remain false. Execution-gate blob is `bd950a0091843c7630249a3ea7a6c1867f2b11ff`; focused workflow-test blob is `a0defef100102b23be330142a3430b4549e77495`.

DEC-236 itself does not dispatch the workflow. The first manual-main EXP-058 attempt consumes the slot on any terminal outcome and must route through DEC-235. No rerun, retry, or replacement attempt is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate clean-main double-plan one-way operator.


## DEC-237 — Phase 8A EXP-058 clean-main one-way operator

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED

DEC-237 binds DEC-236 merge `680359f2d4d03519952e84f257c9d16559b4e251` and freezes a clean-main, one-way EXP-058 operator. Before planning, the operator requires local `main`, clean worktree, exact equality between local HEAD and fetched `origin/main`, and an origin remote resolving exactly to `Dtwosam/FMP`.

The operator accepts at most one exact manual-main EXP-058 workflow run and classifies live state as `MISSING`, `IN_PROGRESS`, or `TERMINAL`. Only `MISSING` may expose the exact frozen dispatch command `gh workflow run phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training.yml --ref main -R Dtwosam/FMP`. In-progress and terminal states never expose a dispatch or replacement action; terminal evidence routes through DEC-235.

The operator metadata binds DEC-234 execution-gate identity, DEC-236 authorization, DEC-231/232/233/234/235 provenance, and the guarded EXP-058 workflow/CLI identities. The public CLI supports read-only `next`, non-executing `advance`, and a double-plan `advance --execute` path. Any live-state or plan drift between the first and second plans fails closed. No rerun, retry, or replacement command exists.

Operator source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_operator.py` at blob `ffda686bf6c632f3c13bfaed8eafb23e8e565795`. Public CLI is `scripts/phase8a_exp058_operator.py` at blob `aca3a47d79a0c32ae6590db3019557bea6bb6e89`. Focused tests are `tests/test_phase8a_exp058_operator.py` at blob `d1fbe9a7f5db6318be53870a149584c5bb02ecf6`.

DEC-237 does not itself dispatch the model workflow or consume the DEC-236 slot. Replacement model runs, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a repository-hosted read-only `next` plan runner only.


## DEC-238 — Phase 8A EXP-058 repository-hosted read-only operator plan

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED

DEC-238 binds DEC-237 merge `516d000897ee870b6b8d32ccc790494635e2533c` and adds a repository-hosted read-only proof for the exact DEC-237 EXP-058 `next` plan. The workflow is main-push/path scoped, grants only `contents: read` and `actions: read`, has no manual/scheduled/PR trigger, preserves a clean checkout, installs the pinned EXP-058 runtime without editable installation, writes plan output only under `RUNNER_TEMP`, and invokes only `python scripts/phase8a_exp058_operator.py next`.

A successful proof must establish `operator_decision = DEC-237`, `read_only = true`, no existing manual-main EXP-058 run, `run_state = MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_DISPATCH_REQUIRED` stage, and the frozen dispatch command as plan evidence only. The four bounded DEC-236 historical-run authorization fields remain true in the plan while replacement/promotion/shadow/demo/broker/live/real-money/trading remain false.

Workflow `.github/workflows/phase8a-exp058-operator-plan.yml` is blob `436364fbc003be335a9801ab2569f7a7ed7cbe50`. Focused tests `tests/test_phase8a_exp058_operator_plan_runner.py` are blob `ab97b2c61170e9947f4942b6dccdfaa35263c0a1`. The bound operator source is blob `ffda686bf6c632f3c13bfaed8eafb23e8e565795`; the public operator CLI is blob `aca3a47d79a0c32ae6590db3019557bea6bb6e89`.

DEC-238 cannot invoke `advance`, `advance --execute`, a direct workflow dispatch, rerun, retry, replacement, or model-result claim. It consumes no historical slot. Only after a successful merged-main proof and exact artifact binding may a separate one-shot executor be considered.


## DEC-239 — Phase 8A EXP-058 one-shot operator executor

**Date:** 2026-09-26
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE

DEC-239 binds successful DEC-238 read-only proof run `36206173161` at merged-main commit `c25efaff4a0bb9ad4c8e3b51eee55da0f7991d0e`. The run completed successfully on attempt 1 and persisted non-expired artifact `10894115135`, named `exp058-dec237-read-only-operator-plan-c25efaff4a0bb9ad4c8e3b51eee55da0f7991d0e`, with digest `sha256:5f75874e78a04db86f6f839a08a1fec581e9854ca26c4f363459dba5ffa69857`.

The proof artifact independently confirms DEC-237 on clean current main, no existing manual-main EXP-058 run, `MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_DISPATCH_REQUIRED` stage, the exact frozen dispatch command as read-only plan evidence, the four bounded DEC-236 historical-run fields true, and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

DEC-239 adds exactly one main-push/path-scoped executor. Its sole execution-capable action is `python scripts/phase8a_exp058_operator.py advance --execute`. It contains no independent model-workflow dispatch command, dispatch REST endpoint, GitHub rerun command, retry, or replacement path. Before execution it revalidates the exact DEC-238 run/artifact metadata, downloads and rehashes the plan ZIP, rechecks `operator-plan.json`, and relies on DEC-237 for fresh clean-main/live-state double planning.

After operator submission, the executor independently queries the exact EXP-058 workflow listing and requires exactly one manual-main run at the executor merge SHA on attempt 1. This observation loop does not redispatch or rerun anything.

Executor workflow `.github/workflows/phase8a-exp058-operator-execute.yml` is blob `5241ea0b4d8b23dff3ef0f190240bb08d248218c`. Focused tests `tests/test_phase8a_exp058_operator_executor.py` are blob `5fc16bec72a7dd04d2bf3380c85213cbe3ffd7c6`.

DEC-239 authorizes no second executor attempt and no replacement model run. If the initial merged-main executor submits the EXP-058 historical workflow, that first attempt consumes the DEC-236 slot on any terminal outcome and must route through DEC-235. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.


## DEC-240 — Phase 8A EXP-058 reviewed historical model result

**Date:** 2026-09-26
**Status:** REVIEWED RESULT / NO STABLE CHALLENGER

DEC-240 freezes the sole DEC-236-authorized EXP-058 historical workflow run `36207673978` at merged-main commit `2339762cda013322c8704cee12218ec4f4fb8c36`. The run completed successfully on attempt 1; authorization-preflight, all nine matrix jobs, and aggregate-model-evidence all succeeded. All nine expected cell artifacts plus aggregate artifact `10895236824` are present and non-expired.

The aggregate artifact digest is `sha256:0e4efa5602410a58fa754dfcd44745d69f4e2905d6ce0dd2062030e791808c3a`. Aggregate evidence fingerprint `7e5019f0e00ada90a8f9c111d2b6fdb4ba41908f86a47203258b333439c8c8ee` independently recomputes under the frozen canonical serializer.

Verified evidence contains 18 cells, 108 regressors, 108 pooled calibration references, 432 fit-temporal utility-support references, 216 feature-support references, 432 residual references, 12 residual-breadth bounds per eligible row, 12 lower-tail source bounds per eligible row, lower-tail count 3, three residual fit regimes, four residual windows per regime, and 12 regime-floor source bounds per eligible row.

Of 54 budget variants, 28 are available and 26 unavailable. Utility-eligible selection rows total 26,392. Exactly three USDJPY 5m / 60m variants at budgets 250, 500, and 1000 pass the aggregate selection gate, with four-window directional candidate counts `0/0/0/250`, `0/0/7/493`, and `0/3/72/925`. All three fail the unchanged temporal-stability gate. Stable-pass count is zero; all 18 cells report `NO_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_STABLE_MODEL_CHALLENGER`; validation and holdout remain locked; accepted model candidate count is zero.

Reviewed-result source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_result_decision.py` at blob `f5a5f7e49b7088f4af9b35a9143e486c3fba3d1a`. Focused tests are `tests/test_phase8a_exp058_model_result_decision.py` at blob `b07289e842649910eb2c098e23d3ce120365f511`.

DEC-240 closes the consumed EXP-058 slot. Rerun, retry, replacement model run, further model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is source-only post-result diagnostic analysis.


## DEC-241 — Phase 8A EXP-058 post-result diagnostic

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC

DEC-241 binds DEC-240 merge `d691c8e12f40cf4baf3fc93f598b24d23b8435f4`, DEC-240 result-decision blob `f5a5f7e49b7088f4af9b35a9143e486c3fba3d1a`, DEC-229 result-decision blob `185e2cdf089cb6f1a12619af58fd32860366498f`, and DEC-230 diagnostic blob `09e88b85a51b858296a3af7d146251606f1d5533`.

Variant accounting is unchanged between EXP-057 and EXP-058: 54 total variants, 28 available, 26 unavailable, and 26,392 utility-eligible selection rows. Aggregate-pass identity is unchanged at USDJPY 5m / 60m budgets 250, 500, and 1000; stable-pass count remains zero in both experiments.

The fit-regime-floor layer changes candidate identity in 27 of 28 available variants. Aggregate 0.5-pip total net pips improve in 14 variants, worsen in 13, and remain unchanged in one. In the common USDJPY 5m / 60m cell, budgets 250 and 500 improve financially while budget 1000 worsens. Selection-window candidate counts remain chronologically concentrated at `0/0/0/250`, `0/0/7/493`, and `0/3/72/925`, so the unchanged 10% per-window share floor still rejects all three aggregate-pass variants.

DEC-241 classifies the result as `REGIME_FLOOR_RANKING_CHANGED_CANDIDATE_MIX_AND_FINANCIALS_BUT_DID_NOT_CREATE_TEMPORAL_STABILITY`. Diagnostic source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_post_result_diagnostics.py` at blob `c0717252dabd625bd6a65b78f9acb5217ed44c84`. Focused tests are `tests/test_phase8a_exp058_post_result_diagnostics.py` at blob `b3a1f930d088e279dbc17c86d4b4bd3b6c60fe83`.

EXP-058 rerun/replacement, stability-gate relaxation, early-window removal, selection-outcome ranking, selection-window recalibration/quotas, regime-floor retuning, successor model fit/result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. Only successor protocol source design is open.


## DEC-242 — Phase 8A EXP-059 fit-regime balance protocol

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-242 binds DEC-241 merge `761696ac8619841efde494ff4c827c4c91e8895c`, DEC-241 diagnostic blob `c0717252dabd625bd6a65b78f9acb5217ed44c84`, DEC-240 result-decision blob `f5a5f7e49b7088f4af9b35a9143e486c3fba3d1a`, predecessor EXP-058 protocol blob `8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2`, and predecessor evidence fingerprint `7e5019f0e00ada90a8f9c111d2b6fdb4ba41908f86a47203258b333439c8c8ee`.

EXP-059 adds one fit-only regime-balance score from the exact three frozen EXP-058 fit-regime means. For means `m1,m2,m3`, score = arithmetic mean minus exactly 1.0 times `max-min`. No new reference vector, fit regime, jackknife view, selection-window statistic, validation outcome, or holdout outcome enters the score.

Eligible rows rank by regime-balance utility, regime-floor utility, residual lower-tail mean, residual breadth, robust residual-bound utility, feature support, utility support, pooled calibrated utility, raw utility, then row identity. Each 250/500/1000 budget freezes the corresponding nine-part numeric cutoff. Validation and holdout reuse the exact fitted models/references, three regime means, regime-floor score, regime-balance score, and frozen cutoff with no refit/recalibration/tuning.

Protocol source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_protocol.py` at blob `cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc`. Focused tests are `tests/test_phase8a_exp059_regime_balance_protocol.py` at blob `42277506ffb39c0a9969b0253127a0cf10b79fd9`.

DEC-242 changes no eligibility, budget, financial gate, temporal-stability window/share floor, chronology, feature, target, HGB, or jackknife rule. Model result production, model fit, historical execution, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a deterministic in-memory EXP-059 training/evaluation core only.


## DEC-243 — Phase 8A EXP-059 deterministic regime-balance training core

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-243 binds DEC-242 merge `a14afb226722d168c3d899d7079776388161a52d`, DEC-242 protocol blob `cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc`, and predecessor DEC-232 regime-floor training-core blob `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`.

The implementation reuses the frozen EXP-058 fit/reference/financial/stability/forward machinery and adds only the DEC-242 regime-balance score and its nine-part cutoff. For each already eligible row, the core recomputes the same three fit-regime means from the same twelve frozen downside-adjusted residual bounds, requires the retained regime-floor minimum to match the predecessor score exactly, and computes regime-balance utility as the arithmetic mean of the three regime means minus exactly 1.0 times their max-minus-min spread. No new reference vector is created and no selection, validation, or holdout outcome enters the score.

Eligible rows rank by regime-balance utility, regime-floor utility, residual lower-tail mean, residual breadth, robust residual-bound utility, feature support, utility support, pooled calibrated utility, raw utility, then row identity. Each 250/500/1000 budget freezes the corresponding nine-part numeric cutoff. Aggregate financial gates, the four temporal-stability windows, the 10% candidate-share floor, validation/holdout chronology, and no-refit semantics remain unchanged.

The completed source exposes `run_fit_temporal_residual_regime_balance_utility_model_cell_core`, plus regime-balance-aware forward and temporal-stability evaluators. Training-core source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_training.py` at blob `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`. Focused tests are `tests/test_phase8a_exp059_regime_balance_training.py` at blob `4f5a2222da5aab5e60558b3594f64e02f511838b`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp059-regime-balance-training-core.md`.

DEC-243 contains no artifact loading, readiness execution, workflow dispatch, model-result execution, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading path. All such authorizations remain false. The next safe gate after merge is a separate non-executable EXP-059 artifact/evidence contract bound to this exact core.


## DEC-244 — Phase 8A EXP-059 artifact/evidence contract

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-244 binds DEC-243 merge `9f427f06f315288bd9b132de19901beb5a5ddfc8`, DEC-243 training-core blob `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`, and predecessor DEC-233 artifact-contract blob `5a34f354b68e14bb7116c79f15f9cfebe149a811`.

The contract validates complete EXP-059 cell evidence before aggregate compilation. Each cell must bind the exact experiment/protocol/training decisions, deterministic cell fingerprint, six regressors, six pooled references, 24 utility-support references, 12 feature-support references, 24 exact residual references, the twelve-bound residual-breadth inventory, twelve-bound residual lower-tail source inventory, lower-tail count 3, three fit regimes, four residual windows per regime, twelve regime-floor source bounds, three regime-balance source regimes, twelve regime-balance source bounds, penalty multiplier 1.0, regime-balance-aware consensus diagnostics/digest, and the three frozen budget variants.

Available variants require a finite nine-part cutoff: regime-balance utility, regime-floor utility, lower-tail mean, residual breadth, residual-bound utility, feature support, fit-temporal utility support, pooled calibration, and raw utility. Unavailable budgets expose all nine cutoff fields as null and cannot pass selection.

Complete aggregate evidence requires all 18 exact cells and verifies 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, 12 residual-breadth bounds per eligible row, 12 lower-tail source bounds per eligible row, lower-tail count 3, three residual regimes, four residual windows per regime, 12 regime-floor source bounds, three regime-balance source regimes, 12 regime-balance source bounds, and penalty multiplier 1.0. Aggregate evidence receives a deterministic fingerprint under the frozen canonical serializer.

Artifact-contract source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_artifacts.py` at blob `a993d8a0a98b181c7810e4f0931be330352437b4`. Focused tests are `tests/test_phase8a_exp059_regime_balance_artifacts.py` at blob `12ee1e63d2bfc0cae1ee272290f866e1de021520`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp059-regime-balance-artifact-contract.md`.

DEC-244 remains non-executable: authoritative result execution, model fit, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate after merge is a separate manual-main EXP-059 workflow/CLI/runtime source freeze with execution still closed.


## DEC-245 — Phase 8A EXP-059 workflow/CLI/runtime source freeze

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED

DEC-245 binds DEC-242 merge `a14afb226722d168c3d899d7079776388161a52d` and protocol blob `cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc`, DEC-243 merge `9f427f06f315288bd9b132de19901beb5a5ddfc8` and training-core blob `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`, and DEC-244 merge `b539c48cd62fb8e510ecaa15ce507c114f9401bb` and artifact-contract blob `a993d8a0a98b181c7810e4f0931be330352437b4`.

The frozen manual-main/input-free workflow is `.github/workflows/phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml` at blob `d416c43c9e582f49cd60314c6ee736925e8185e8`. It retains read-only permissions, Python 3.12.14, the exact nine pair/timeframe datasets, 60m/240m horizons, frozen feature/outcome/readiness artifacts, partial cell evidence, and deterministic aggregate evidence.

Public CLI `scripts/phase8a_exp059_model_run.py` is blob `44c084c226c62c30ddf16741027593a4a835605f`; runtime lock `requirements/exp059-model-run.txt` is blob `d25ab16056b9f5df283147d67b8f401f60ae7520`. The CLI requires execution authorization before readiness/artifact loading, regime-balance model-core execution, or aggregate compilation and contains no direct workflow-dispatch path.

Exact-source execution gate `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_execution_gate.py` is blob `d6556cf3bc3a1189c2ee6648c1870ec307a2178f`. Focused tests are `tests/test_phase8a_exp059_model_workflow.py` at blob `e75663b17d334fc73b3fc905779988f5807e7e6d`.

DEC-245 intentionally has no first-run guard and opens no historical slot. Model-run dispatch, authoritative result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate predeclared attempt-1 terminal-review contract.


## DEC-246 — Phase 8A EXP-059 predeclared terminal review

**Date:** 2026-09-26
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED

DEC-246 binds merged DEC-245 commit `d33e2f1e6e7f39c12811dbc07c5cd960f8e2442f`, workflow blob `d416c43c9e582f49cd60314c6ee736925e8185e8`, CLI blob `44c084c226c62c30ddf16741027593a4a835605f`, and execution-gate blob `d6556cf3bc3a1189c2ee6648c1870ec307a2178f`.

The review accepts only the exact manual-main EXP-059 regime-balance workflow on attempt 1. A successful terminal review requires exactly 11 completed successful jobs, all nine expected non-expired pair/timeframe cell artifacts, the exact non-expired aggregate artifact, and aggregate evidence that deterministically recompiles under DEC-244 for the reviewed head commit.

Successful aggregate revalidation verifies 18 cells, 108 regressors, 108 pooled calibration references, 432 utility-support references, 216 feature-support references, 432 residual references, the inherited twelve-bound residual-breadth inventory, the twelve-bound residual lower-tail source inventory, lower-tail count 3, three residual fit regimes, four residual windows per regime, twelve regime-floor source bounds per eligible row, three regime-balance source regimes, twelve regime-balance source bounds per eligible row, penalty multiplier 1.0, and the exact aggregate evidence fingerprint.

Non-success outcomes may preserve only produced expected cell artifacts; they cannot claim aggregate evidence or aggregate artifact and open no rerun, retry, or replacement path. Any run attempt greater than 1 is rejected.

Terminal-review source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_result_review.py` at blob `5adc6ad72b2dfab1de1cca09a9bb2bc09663bfc5`. Focused tests are `tests/test_phase8a_exp059_model_result_review.py` at blob `e3d2abfe369a4a92510adce9c7b1d110bc363a28`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp059-terminal-review.md`.

DEC-246 does not authorize workflow dispatch, authoritative result execution, model-protocol result production, model fitting, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. The next safe gate is a separate zero-prior-run proof plus first-run guard and at most one bounded outer historical slot.


## DEC-247 — Phase 8A EXP-059 first-run authorization gate

**Date:** 2026-09-26
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED

Immediately after DEC-246 merged, the latest 100 repository GitHub Actions runs were queried. That set contained one manual-main workflow-dispatch run and zero runs whose exact workflow name/path matched `phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training` / `.github/workflows/phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml`. No EXP-059 historical model-result attempt had consumed the first-run slot.

DEC-247 binds DEC-245 merge `d33e2f1e6e7f39c12811dbc07c5cd960f8e2442f`, DEC-245 workflow blob `d416c43c9e582f49cd60314c6ee736925e8185e8`, DEC-245 CLI blob `44c084c226c62c30ddf16741027593a4a835605f`, DEC-245 execution-gate blob `d6556cf3bc3a1189c2ee6648c1870ec307a2178f`, DEC-246 merge `018c8cb223c3553ad4db4ba5b33b339a9a8fa918`, and DEC-246 terminal-review blob `5adc6ad72b2dfab1de1cca09a9bb2bc09663bfc5`.

The manual-main workflow now contains a first-run rejection guard before execution authorization. The guard verifies its own exact run identity and fails closed if any other manual-main EXP-059 workflow run already exists. The guarded workflow blob is `6c3e516be8d6eaed834fb1955efccf43f414318f`.

Only the outer historical-result slot is opened. The DEC-247 execution gate may expose workflow dispatch, authoritative historical-result execution, model-protocol result production, and model fitting for at most one guarded attempt. The underlying DEC-242/243/244 protocol/core/artifact authorization constants remain false. Execution-gate blob is `7e6d07c1d7f24bb69912227906990e59abc7be0d`; focused workflow-test blob is `d1fa6a2c1cd2169b1dc40f1904010a9293cfb9fb`.

DEC-247 itself does not dispatch the workflow. The first manual-main EXP-059 attempt consumes the slot on any terminal outcome and must route through DEC-246. No rerun, retry, or replacement attempt is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate clean-main double-plan one-way operator only.


## DEC-248 — Phase 8A EXP-059 clean-main one-way operator

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED

DEC-248 binds merged DEC-247 commit `41975d1ddbabcc31f490b8b36def2a491010c277` and freezes a clean-main, one-way operator for the already bounded EXP-059 historical-result slot.

The operator requires local branch `main`, local HEAD equal to freshly fetched `origin/main`, a clean working tree, and exact Dtwosam/FMP origin identity. It permits at most one exact manual-main EXP-059 workflow run and classifies the live state as `MISSING`, `IN_PROGRESS`, or `TERMINAL`. More than one manual-main run fails closed.

Only `MISSING` may expose the exact frozen dispatch command. `IN_PROGRESS` and `TERMINAL` never expose dispatch/replacement actions; terminal state routes through DEC-246.

Public CLI `scripts/phase8a_exp059_operator.py` is blob `720bab7054ecd55fd90a1ef6dbae8b00ceb5dabd`. It exposes read-only `next`, non-executing `advance`, and double-plan `advance --execute`; the execution path recomputes the live `next` plan immediately before submission and fails closed on any state drift.

Operator source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_operator.py` at blob `12a4fcce685e2136aea6a9d0e3e27ba39b320f1e`. Focused tests are `tests/test_phase8a_exp059_operator.py` at blob `b80a3233dda65573fe2d51f31fc14b3e97f13ba3`.

DEC-248 itself does not dispatch or consume the DEC-247 slot. Replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a repository-hosted read-only `next` plan runner only.


## DEC-249 — Phase 8A EXP-059 repository-hosted read-only operator plan

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED

DEC-249 binds DEC-248 merge `67942688e417debf413e63b99555743eea2122ff` and adds a repository-hosted read-only proof for the exact DEC-248 EXP-059 `next` plan. The workflow is main-push/path scoped, grants only `contents: read` and `actions: read`, has no manual/scheduled/PR trigger, preserves a clean checkout, installs the pinned EXP-059 runtime without editable installation, writes plan output only under `RUNNER_TEMP`, and invokes only `python scripts/phase8a_exp059_operator.py next`.

A successful proof must establish `operator_decision = DEC-248`, `read_only = true`, no existing manual-main EXP-059 run, `run_state = MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RUN_DISPATCH_REQUIRED` stage, and the frozen dispatch command as plan evidence only. The four bounded DEC-247 historical-run authorization fields remain true in the plan while replacement/promotion/shadow/demo/broker/live/real-money/trading remain false.

Workflow `.github/workflows/phase8a-exp059-operator-plan.yml` is blob `160b5aee27d63443862e32137e3b4fe75997d3d9`. Focused tests `tests/test_phase8a_exp059_operator_plan_runner.py` are blob `05766f40bbe9fbda01f96fa1eb5d4acef3c5f443`. The bound operator source is blob `12a4fcce685e2136aea6a9d0e3e27ba39b320f1e`; the public operator CLI is blob `720bab7054ecd55fd90a1ef6dbae8b00ceb5dabd`.

DEC-249 cannot invoke `advance`, `advance --execute`, a direct workflow dispatch, rerun, retry, replacement, or model-result claim. It consumes no historical slot. Only after a successful merged-main proof and exact artifact binding may a separate one-shot executor be considered.


## DEC-250 — Phase 8A EXP-059 one-shot operator executor

**Date:** 2026-09-26
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE

DEC-250 binds successful DEC-249 read-only proof run `36238966706` at merged-main commit `adb5e127b92feedff2653a1b9ba24de4621246da`. The run completed successfully on attempt 1 and persisted non-expired artifact `10904883676`, named `exp059-dec248-read-only-operator-plan-adb5e127b92feedff2653a1b9ba24de4621246da`, with digest `sha256:3fba24ae0101e20c5c98751134b956076fc3d0ecb38af25f59377802c7b2d6d4`.

The proof artifact independently confirms DEC-248 on clean current main, no existing manual-main EXP-059 run, `MISSING`, the exact `FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RUN_DISPATCH_REQUIRED` stage, the exact frozen dispatch command as read-only plan evidence, the four bounded DEC-247 historical-run fields true, and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

DEC-250 adds exactly one main-push/path-scoped executor. Its sole execution-capable action is `python scripts/phase8a_exp059_operator.py advance --execute`. It contains no independent model-workflow dispatch command, dispatch REST endpoint, GitHub rerun command, retry, or replacement path. Before execution it revalidates the exact DEC-249 run/artifact metadata, downloads and rehashes the plan ZIP, rechecks `operator-plan.json`, and relies on DEC-248 for fresh clean-main/live-state double planning.

After operator submission, the executor independently queries the exact EXP-059 workflow listing and requires exactly one manual-main run at the executor merge SHA on attempt 1. This observation loop does not redispatch or rerun anything.

Executor workflow `.github/workflows/phase8a-exp059-operator-execute.yml` is blob `d207314d107e30ead9b5f77582bf8a7990625067`. Focused tests `tests/test_phase8a_exp059_operator_executor.py` are blob `f9da2b1e1e5bfb1fbc2f260dc98b7d5da18104c6`.

DEC-250 authorizes no second executor attempt and no replacement model run. If the initial merged-main executor submits the EXP-059 historical workflow, that first attempt consumes the DEC-247 slot on any terminal outcome and must route through DEC-246. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.


## DEC-251 — Phase 8A EXP-059 reviewed failed historical result

**Date:** 2026-09-26
**Status:** REVIEWED FAILED ATTEMPT / NO MODEL RESULT

DEC-250 merged at `8b47a025598feea1b9a382c4f0c35ac644512acc` and its executor submitted the sole DEC-247-authorized EXP-059 historical workflow. Model run `36239443323` completed on attempt 1 with conclusion `failure`, so the EXP-059 slot is consumed.

DEC-246 non-success review applies exactly: authorization-preflight succeeded, all nine matrix jobs failed, aggregate-model-evidence was skipped, zero cell artifacts persisted, no aggregate artifact exists, and no aggregate result evidence is claimed. No replacement run is authorized.

All nine matrix failures share one implementation dependency/export-depth error. The EXP-059 regime-balance training core attempts to read `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE` from `model_successor_fit_temporal_residual_lower_tail_utility_repair_training`, where that symbol is not exported. DEC-251 classifies the failure as `IMPLEMENTATION_DEPENDENCY_EXPORT_DEPTH_DRIFT_PREVENTED_ALL_EXP059_CELL_RESULTS`.

Because no cell result artifact exists, EXP-059 has no model-selection result, aggregate financial result, evidence fingerprint, selected variant, validation result, holdout result, or accepted candidate. This failure must not be interpreted as evidence for or against the intended regime-balance ranking.

Reviewed failed-result source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_result_decision.py` at blob `c8ca7143e687494b81205556af7e317ec69937fd`. Focused tests are `tests/test_phase8a_exp059_failed_result_decision.py` at blob `4b10d137160c7fcbc6b570940db7b2cccfd6b6e7`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp059-reviewed-failed-result.md`.

DEC-251 closes model-run dispatch, replacement, authoritative result execution, model-protocol result production, and model fit. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. No second EXP-059 attempt is authorized. The next safe gate is a separate source-only implementation-defect diagnostic only.


## DEC-252 — Phase 8A EXP-059 implementation-failure diagnostic

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC

DEC-252 binds DEC-251 merge `639fa26f841d0d3bb4c8577372a8539a0c0fd38f`, DEC-251 result-decision blob `c8ca7143e687494b81205556af7e317ec69937fd`, EXP-059 regime-balance training-core blob `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`, EXP-058 regime-floor training-core blob `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`, EXP-057 lower-tail-repair training-core blob `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`, and EXP-055 breadth training-core blob `c9517b7516940c78621448088c3933aa1c57e281`.

The diagnostic performs a deterministic AST audit of the frozen predecessor chain. EXP-059 currently uses four breadth metadata accesses at `_predecessor._predecessor.<name>`, which resolves to the EXP-057 lower-tail-repair training module. That module does not export those names. The EXP-055 breadth training module one level deeper does export all four: `FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW`, `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE`, `RESIDUAL_BREADTH_ELIGIBILITY_RULE`, and `RESIDUAL_BREADTH_POSITIVITY_RULE`.

The failed historical attempt directly observed missing `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE` in all nine matrix jobs. DEC-252 classifies the failure as `EXP059_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_PREDECESSOR_DEPTH_DRIFT`.

The exact future repair boundary is implementation-only: under a new successor experiment identity, replace those four `_predecessor._predecessor.<name>` accesses with `_predecessor._predecessor._predecessor.<name>`. No regime-balance protocol semantics, math, data identity, model family, chronology, ranking, cutoff, candidate budget, financial gate, temporal-stability gate, validation, or holdout rule may change.

Diagnostic source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_failure_diagnostics.py` at blob `d73008c7faf236f915685110d6cf59988d6fc27f`. Focused tests are `tests/test_phase8a_exp059_implementation_failure_diagnostics.py` at blob `3432d5ffb6799eb3adf4d25780cfc00141ba038e`.

DEC-252 keeps EXP-059 rerun/replacement, successor model fit, successor historical result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading false. It opens successor protocol source design only, under a new experiment identity.


## DEC-253 — Phase 8A EXP-060 regime-balance implementation-repair protocol

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-253 binds DEC-252 merge `fffe7311bfb0c14bf6936657b81ffe8a38c66414`, DEC-252 diagnostic blob `d73008c7faf236f915685110d6cf59988d6fc27f`, DEC-251 result-decision blob `c8ca7143e687494b81205556af7e317ec69937fd`, EXP-059 regime-balance protocol blob `cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc`, and EXP-059 training-core blob `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`.

EXP-060 preserves EXP-059 regime-balance semantics exactly: chronology, model family, jackknife views, unanimous positive-utility eligibility, all frozen reference families, residual-bound/breadth/lower-tail/regime-floor/regime-balance scores, penalty multiplier 1.0, budgets 250/500/1000, nine-part ranking/cutoff, four temporal-stability windows, 0.10 minimum directional candidate share, financial gates, validation, holdout, and no-refit/no-recalibration forward application.

The only authorized implementation change is the four-name predecessor-depth repair from `_predecessor._predecessor.<name>` to `_predecessor._predecessor._predecessor.<name>` for `FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW`, `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE`, `RESIDUAL_BREADTH_ELIGIBILITY_RULE`, and `RESIDUAL_BREADTH_POSITIVITY_RULE`.

Protocol source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_protocol.py` at blob `82d336250e2cdd9894afa5554c6b422e0de6b1fe`. Focused tests are `tests/test_phase8a_exp060_implementation_repair_protocol.py` at blob `0aa76c5d88e6d3a894d1d19bb6241c24ade1b18f`.

DEC-253 authorizes implementation-repair source design only. Protocol semantic change, model-protocol result production, model fit, historical result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a deterministic in-memory EXP-060 training/evaluation core only.


## DEC-254 — Phase 8A EXP-060 deterministic regime-balance repair training core

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-254 binds DEC-253 merge `7e5b399cb7960d385d956b33e5d96cea85bb2c28`, DEC-253 repair-protocol blob `82d336250e2cdd9894afa5554c6b422e0de6b1fe`, failed EXP-059 regime-balance training-core blob `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`, and unchanged EXP-058 regime-floor training-core blob `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`.

The implementation preserves the complete EXP-059 regime-balance model/evaluation semantics. The only source repair is the DEC-253-authorized four-name depth correction for breadth metadata: `_predecessor._predecessor.<name>` becomes `_predecessor._predecessor._predecessor.<name>` for `FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW`, `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE`, `RESIDUAL_BREADTH_ELIGIBILITY_RULE`, and `RESIDUAL_BREADTH_POSITIVITY_RULE`.

All chronology, HGB/jackknife mechanics, calibration/support/residual references, residual-bound/breadth/lower-tail/regime-floor/regime-balance scores, 1.0 balance penalty, budgets 250/500/1000, nine-part lexicographic cutoff, four stability windows, 0.10 minimum directional share, financial gates, validation, holdout, and forward no-refit/no-recalibration rules remain unchanged. The full cell runner remains `run_fit_temporal_residual_regime_balance_utility_model_cell_core`.

Training-core source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_training.py` at blob `202dcaa8ba4ad25324fbe53d00e812c60fbb37dd`. Focused tests are `tests/test_phase8a_exp060_implementation_repair_training.py` at blob `b651a35a3e54a9dd909ee6061662550b2b84dc43`.

DEC-254 remains non-executable: historical result execution, model fit outside the deterministic in-memory core, artifact loading, readiness execution, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate after merge is a separate non-executable EXP-060 artifact/evidence contract bound to this exact repaired core.


## DEC-255 — Phase 8A EXP-060 artifact/evidence contract

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE

DEC-255 binds DEC-254 merge `c8cac108bc098dbceda4b8903f5a56ac7f62bf47`, repaired training-core blob `202dcaa8ba4ad25324fbe53d00e812c60fbb37dd`, and predecessor EXP-059 regime-balance artifact-contract blob `a993d8a0a98b181c7810e4f0931be330352437b4`.

Each EXP-060 cell must bind experiment `EXP-20260926-060`, protocol DEC-253, training core DEC-254, DEC-253 merge/protocol source identity, failed EXP-059 training-core blob `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`, unchanged EXP-058 semantic-predecessor training-core blob `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`, exact EXP-060 protocol version/fingerprint, and deterministic cell result fingerprint.

The contract preserves the full regime-balance evidence inventory: 6 regressors, 6 pooled references, 24 utility-support references, 12 feature-support references, 24 residual references, 12 residual-breadth bounds, 12 lower-tail source bounds with lower-tail count 3, three residual regimes, four residual windows per regime, 12 regime-floor source bounds, three regime-balance source regimes, 12 regime-balance source bounds, penalty multiplier 1.0, and the unchanged nine-part cutoff. Complete aggregate evidence requires all 18 exact cells and verifies totals 108/108/432/216/432 plus the fixed per-row regime inventories before deterministic fingerprinting.

Artifact-contract source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_artifacts.py` at blob `2a6c550dcafac2e7013136fcbbef95b13c2e7d18`. Focused tests are `tests/test_phase8a_exp060_regime_balance_repair_artifacts.py` at blob `d3ddef1ea784eedd04be73deb495b93df2559049`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp060-artifact-evidence-contract.md`.

DEC-255 remains non-executable: authoritative result execution, model fit, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate after merge is a separate manual-main EXP-060 workflow/CLI/runtime source freeze with execution still closed.

## DEC-256 — Phase 8A EXP-060 workflow/CLI/runtime source freeze

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED

DEC-256 binds DEC-253 merge `7e5b399cb7960d385d956b33e5d96cea85bb2c28` and repair-protocol blob `82d336250e2cdd9894afa5554c6b422e0de6b1fe`, DEC-254 merge `c8cac108bc098dbceda4b8903f5a56ac7f62bf47` and repaired training-core blob `202dcaa8ba4ad25324fbe53d00e812c60fbb37dd`, and DEC-255 merge `d3a52722c178c96eb865791be096661007d16dd5` and repaired artifact-contract blob `2a6c550dcafac2e7013136fcbbef95b13c2e7d18`.

The frozen manual-main/input-free workflow is `.github/workflows/phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml` at blob `20af1bf2f9057274a8c50d5b48becbf5f683ef86`. It retains read-only permissions, Python 3.12.14, the exact nine pair/timeframe datasets, 60m/240m horizons, frozen feature/outcome/readiness artifacts, partial cell evidence, and deterministic aggregate evidence.

Public CLI `scripts/phase8a_exp060_model_run.py` is blob `90c6bc9e893c813d394e3a9c4adc5a155e938af0`; runtime lock `requirements/exp060-model-run.txt` is blob `d25ab16056b9f5df283147d67b8f401f60ae7520`. The CLI requires execution authorization before readiness/artifact loading, repaired regime-balance model-core execution, or repaired aggregate compilation and contains no direct workflow-dispatch path.

Exact-source execution gate `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_execution_gate.py` is blob `82f51bf85ccb1793b3a980b2884f3e122a03c8db`. Focused tests are `tests/test_phase8a_exp060_model_workflow.py` at blob `e530e2122ac0ac59f1c02345d890f55c94bfec97`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp060-workflow-source-freeze.md`.

DEC-256 intentionally has no first-run guard and opens no historical slot. Model-run dispatch, authoritative result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a separate predeclared attempt-1 terminal-review contract.

## DEC-257 — Phase 8A EXP-060 predeclared terminal review

**Date:** 2026-09-26
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED

DEC-257 binds merged DEC-256 commit `cef9f6d201bf2b025f08c924a11c84e9684b9ba0`, workflow blob `20af1bf2f9057274a8c50d5b48becbf5f683ef86`, CLI blob `90c6bc9e893c813d394e3a9c4adc5a155e938af0`, and execution-gate blob `82f51bf85ccb1793b3a980b2884f3e122a03c8db`.

The review accepts only the exact manual-main EXP-060 repaired regime-balance workflow on attempt 1. A successful terminal review requires exactly 11 completed successful jobs, all nine expected non-expired pair/timeframe cell artifacts, the exact non-expired aggregate artifact, and aggregate evidence that deterministically recompiles under DEC-255 for the reviewed head commit.

Successful aggregate revalidation verifies 18 cells, 108 regressors, 108 pooled calibration references, 432 utility-support references, 216 feature-support references, 432 residual references, the inherited twelve-bound residual-breadth inventory, the twelve-bound residual lower-tail source inventory, lower-tail count 3, three residual fit regimes, four residual windows per regime, twelve regime-floor source bounds per eligible row, three regime-balance source regimes, twelve regime-balance source bounds per eligible row, penalty multiplier 1.0, and the exact aggregate evidence fingerprint.

Non-success outcomes may preserve only produced expected cell artifacts; they cannot claim aggregate evidence or aggregate artifact and open no rerun, retry, or replacement path. Any run attempt greater than 1 is rejected.

Terminal-review source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_result_review.py` at blob `989ebc7b0cc33e5076f83ea94337fe6581c321e3`. Focused tests are `tests/test_phase8a_exp060_model_result_review.py` at blob `a9679622fd5a7ca9328dbcb44be073ffabd21240`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp060-terminal-review.md`.

DEC-257 does not authorize workflow dispatch, authoritative result execution, model-protocol result production, model fitting, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading. The next safe gate is a separate zero-prior-run proof plus first-run guard and at most one bounded outer historical slot.

## DEC-258 — Phase 8A EXP-060 first-run authorization

**Date:** 2026-09-26
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED

Immediately after DEC-257 merged, the exact GitHub Actions page for `phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training` reported `0 workflow runs` and `This workflow has no runs yet.` No EXP-060 historical attempt had consumed the slot.

DEC-258 binds DEC-256 merge `cef9f6d201bf2b025f08c924a11c84e9684b9ba0`, its pre-authorization workflow blob `20af1bf2f9057274a8c50d5b48becbf5f683ef86`, CLI blob `90c6bc9e893c813d394e3a9c4adc5a155e938af0`, execution-gate blob `82f51bf85ccb1793b3a980b2884f3e122a03c8db`, DEC-257 merge `5998292b80c0986bdcc0b9f2a91cb024ef92158a`, and terminal-review blob `989ebc7b0cc33e5076f83ea94337fe6581c321e3`.

The manual-main workflow is hardened by a first-run rejection guard before execution authorization. It validates exact run identity, requires `run_attempt == 1`, lists manual-main runs for the exact EXP-060 workflow, excludes only the current run id, and fails closed if any prior run exists. The guarded workflow blob is `91a5bb720ca10b261533409e36f6143994afcca3`.

DEC-258 opens only the outer bounded historical-result slot: run dispatch, authoritative historical result execution, model-protocol result production, and model fitting may be true for the first guarded attempt. The underlying DEC-253/254/255 repair protocol, repaired core, and repaired artifact-contract execution/fit constants remain false. Execution-gate blob is `3a6bb23d237ab8d74896e06821d0189ed689e169`; focused workflow test blob is `ad305ccf0d2dde2e2074ae069735743d5033cbdf`.

DEC-258 does not dispatch the workflow. A second dispatch is blocked by prior-run detection; a rerun of the same GitHub run is blocked by `run_attempt == 1`. Retry, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain unauthorized. The next safe gate is a clean-main, double-plan, one-way operator that can derive at most one dispatch action while the exact EXP-060 workflow state is still `MISSING`.

## DEC-259 — Phase 8A EXP-060 clean-main one-way operator

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED

DEC-259 binds merged DEC-258 commit `c6aefd21b2deadd834248e69cf7117081ea58497` and freezes a clean-main, fail-closed operator for the single guarded EXP-060 historical-result slot.

The operator requires local branch `main`, local HEAD exactly equal to freshly fetched `origin/main`, a clean working tree, and an origin remote matching `Dtwosam/FMP`. It consumes the exact DEC-256 execution-gate decision, DEC-258 execution-authorization decision, DEC-253/254/255 repair identities, DEC-256 workflow/CLI/gate identities, and DEC-257 terminal-review identity.

Live workflow state is one-way: `MISSING`, `IN_PROGRESS`, or `TERMINAL`. More than one manual-main EXP-060 workflow run fails closed, and any `run_attempt != 1` is rejected as an unauthorized rerun. Only `MISSING` may expose the exact dispatch command; `IN_PROGRESS` and `TERMINAL` expose no dispatch or replacement action. Terminal state routes through DEC-257.

Operator source `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_operator.py` is blob `54f1c5c7d856eb4bf0eb5366cf43ae38a3f25d2c`. Public CLI `scripts/phase8a_exp060_operator.py` is blob `16c553d2dc959fe1e24796a95019163d1967e836`. Focused tests `tests/test_phase8a_exp060_operator.py` are blob `a260433870c1fcf3b855d5b5cec6b432093dd5fe` and include an integration check against the real DEC-258 source gate.

The CLI exposes read-only `next`, non-executing `advance`, and a guarded `advance --execute` path that requires two identical fresh plans immediately before submission. DEC-259 itself does not dispatch and does not consume the slot. Rerun, retry, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain unauthorized.

The next safe gate is a repository-hosted read-only `next` plan runner. Only a successful merged-main proof of that planner may be bound by a later separate one-shot executor source.

## DEC-260 — Phase 8A EXP-060 repository-hosted read-only operator plan

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED

DEC-260 binds merged DEC-259 commit `cf2efadd1bbf457eb20357dfa74d6c2ea7278823`, operator source blob `54f1c5c7d856eb4bf0eb5366cf43ae38a3f25d2c`, and operator CLI blob `16c553d2dc959fe1e24796a95019163d1967e836`.

Repository-hosted workflow `.github/workflows/phase8a-exp060-operator-plan.yml` is blob `88ee067dfcf77dd7d6c2456d3b202c12aaa76dda`. It is push-to-main only for the proof workflow/operator source paths, grants only `contents: read` and `actions: read`, checks out exact merged main, preserves a clean worktree, and invokes only `python scripts/phase8a_exp060_operator.py next`.

A successful proof must show DEC-259, `read_only=true`, no existing EXP-060 manual-main run, `run_state=MISSING`, no run id, and stage `FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RUN_DISPATCH_REQUIRED`. The exact dispatch command may appear only as plan evidence. Replacement, promotion, shadow/demo, broker mutation, live orders, real-money action, and trading remain false.

Focused tests are `tests/test_phase8a_exp060_operator_plan_runner.py` at blob `b1df3c05ba69e2e2afdde8d8fd43d4588d75bb30`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp060-read-only-operator-plan.md` at blob `bd4dbf64f63b2635f8fe64a2c68bfa3c65406942`.

DEC-260 cannot dispatch, rerun, retry, replace, or claim a model result. Only after this workflow succeeds on merged main and its exact non-expired artifact is independently bound may a separate one-shot executor source be considered.

## DEC-261 — Phase 8A EXP-060 one-shot operator executor

**Date:** 2026-09-26
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE

DEC-261 binds successful merged-main DEC-260 proof run `36258921030` at head `0339c58f59206b6e70fb5019be403ee9ffdd1a34`, event `push`, branch `main`, attempt `1`, conclusion `success`. It binds the single non-expired artifact `10911029039`, named `exp060-dec259-read-only-operator-plan-0339c58f59206b6e70fb5019be403ee9ffdd1a34`, with digest `sha256:b51e691984368757138913d646c4561150b02e6afd437773a3758e5559f3748f`.

Executor workflow `.github/workflows/phase8a-exp060-operator-execute.yml` is blob `e614736b287655c6b529799e2b5aaec052dd8c52`. It runs only on a push to `main` that changes the executor workflow, grants `contents: read` and `actions: write`, checks out exact merged main, preserves a clean worktree, independently revalidates the exact DEC-260 proof run/artifact metadata and ZIP digest/content, and invokes only `python scripts/phase8a_exp060_operator.py advance --execute`.

The executor contains no independent direct model-workflow dispatch endpoint, rerun, retry, or replacement path. DEC-259 remains solely responsible for the one permitted dispatch decision and performs two fresh identical plans before submission. After submission, DEC-261 independently requires exactly one manual-main EXP-060 model run, exact executor merge head, and `run_attempt == 1`, then preserves immutable executor evidence outside the checkout.

Focused tests are `tests/test_phase8a_exp060_operator_executor.py` at blob `0e601be70e0cf2c7ac15355e969f2f50226c3c9f`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp060-one-shot-executor.md` at blob `11e57b4f078c6f08cb84ca855198d0e668e6b30c`.

If merged-main execution submits the guarded workflow, that first manual-main EXP-060 attempt consumes the DEC-258 slot regardless of terminal outcome. No second executor attempt, model rerun, retry, or replacement is authorized. Any terminal result must route through DEC-257. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain unauthorized.

## DEC-262 — Phase 8A EXP-060 reviewed historical model result

**Date:** 2026-09-26
**Status:** REVIEWED RESULT / NO STABLE CHALLENGER

The sole DEC-258-authorized EXP-060 attempt is run `36260155597`, event `workflow_dispatch`, branch `main`, head `0062546fda38bfc768122cf03b9a4d69d1b8e0b7`, attempt `1`, conclusion `success`. DEC-261 executor run `36260093042` succeeded and independently verified exactly one submitted run. The first-run slot is consumed and no rerun, retry, or replacement is authorized.

DEC-257 terminal review is satisfied: authorization preflight, all nine matrix jobs, and aggregate evidence all completed successfully; all nine cell artifacts and the aggregate artifact are present and non-expired. Aggregate artifact `10912798284` is named `exp060-fit-temporal-residual-regime-balance-utility-model-result-evidence-0062546fda38bfc768122cf03b9a4d69d1b8e0b7-from-feature-35867307338-outcome-35876715434` with digest `sha256:9090a1a1c7849c703eaa38e5571a36a65f5a47f250c6c0e3a7e21777367b8bc9`; independent ZIP hashing matches. Aggregate evidence fingerprint is `52a840d0919992e1fe9ef3342ddefe46cfb1ad8ccd23c8dfe55963d4c1669b37`.

The evidence verifies 18 cells, 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, 12 breadth bounds, 12 lower-tail bounds, lower-tail count 3, three residual regimes, four residual windows per regime, 12 regime-floor bounds, three regime-balance source regimes, 12 regime-balance source bounds, and penalty multiplier 1.0.

Across 54 budget variants, 28 are available and 26 budget-unavailable over 26,392 utility-eligible selection rows. Exactly two variants pass the aggregate selection gate: USDJPY/5m/60m at budgets 500 and 1000. Their four directional-candidate counts are `0/0/27/473` and `0/3/105/892`; both fail temporal stability. All 18 cells therefore report `NO_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_STABLE_MODEL_CHALLENGER`, with zero selected cells, zero validation passes, zero holdout passes, and zero accepted model candidates.

Reviewed-result source is `src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_result_decision.py` at blob `2684419f983a04d1771443126104a8e7059cc03b`. Focused tests are `tests/test_phase8a_exp060_model_result_decision.py` at blob `dd6eb6424a97d9f743df0ff0bf8790d4505372b6`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp060-reviewed-model-result.md` at blob `c7f41722dec57224444156cf95711664ac16c9fd`.

DEC-262 closes EXP-060 execution/model-fit authority and retains promotion, shadow/demo, broker mutation, live orders, real-money action, and trading as false. The next safe gate after green merge is a source-only Phase 8A post-result assessment; it may not reopen EXP-060 or begin Phase 8B.

## DEC-263 — Phase 8A post-EXP-060 assessment

**Date:** 2026-09-26
**Status:** SOURCE-ONLY ASSESSMENT / PHASE 8A REMAINS ACTIVE

DEC-263 binds merged DEC-262 commit `6d6c88426960b40293aa4b3f1f42d2e02911b375` and records the Phase 8A state after the sole EXP-060 historical result is frozen. EXP-060 run `36260155597` completed successfully but selected no stable model challenger. Its exact aggregate artifact is `10912798284`, digest `sha256:9090a1a1c7849c703eaa38e5571a36a65f5a47f250c6c0e3a7e21777367b8bc9`, with evidence fingerprint `52a840d0919992e1fe9ef3342ddefe46cfb1ad8ccd23c8dfe55963d4c1669b37`. The direct market-learning question is therefore answered through the credible-rejection branch of the Phase 8A acceptance criteria; EXP-060 remains closed with no rerun, retry, replacement, or post-result rescue.

Phase 8A is not complete because DEC-043 / EXP-20260922-015 rule-based challenger discovery remains historically unexecuted. The frozen Stage A/B/C workflow blobs are `e32e04c3afd8a8929dc60defd109788d4e7aa989`, `50a5a32c7beb99df1fbbb8db89e88edae958ee7c`, and `abc946fb7684dec6174b2cdf9075092856b14f86`. Stage A has 12 preserved source-development failure runs on branch `phase8a/exp015-stage-a`, but no authoritative manual-main Stage A historical attempt. Stage B and Stage C have zero workflow runs.

Because no EXP-015 final shortlist exists, DEC-042 portfolio selection and DEC-045 Phase 8A acceptance remain blocked. Phase 8B therefore remains locked and no shadow candidate is frozen.

The next safe gate is source-only modernization of EXP-015 Stage A execution governance: predeclare attempt-1 terminal review, prove zero prior authoritative manual-main Stage A attempts while preserving development-run history, add exact first-run/`run_attempt == 1` rejection guards, and open at most one bounded Stage A historical-result slot. DEC-263 itself authorizes no Stage A dispatch and no Stage B/C, portfolio-selection, shadow, demo, broker, live-order, real-money, or trading action.

Detailed assessment: `docs/superpowers/specs/2026-09-26-phase8a-post-exp060-assessment.md` at blob `0e57b7ad31d83bf1c34bbcb8a8a040dfb95d9ee6`.

## DEC-264 — EXP-015 Stage A first-run governance and terminal review

**Date:** 2026-09-26
**Status:** SOURCE-ONLY FIRST-RUN GOVERNANCE / ONE BOUNDED SLOT OPEN / NOT DISPATCHED

DEC-264 binds merged DEC-263 commit `46512e56abb097bd8e7f1a9503f762e3d18b3715` and modernizes only the execution boundary for the already-frozen DEC-043/044 EXP-015 Stage A research protocol.

Historical audit is preserved exactly: `.github/workflows/phase8a-exp015-stage-a.yml` has 12 old failed `push` runs on branch `phase8a/exp015-stage-a`, and zero authoritative `workflow_dispatch` attempts from `main`. Stage B and Stage C have zero runs. The 12 development failures remain immutable historical CI evidence and do not count as the future authoritative Stage A attempt.

The guarded Stage A workflow is blob `ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930`. Before catalog/data work it requires exact workflow name/path, `workflow_dispatch`, branch `main`, exact current main head, current run identity, and `run_attempt == 1`; it lists only manual-main Stage A runs and fails closed if any prior authoritative attempt exists. DEC-043/044 research semantics remain unchanged: 567 identities, nine symbol/timeframe cells, six families, 2015-01-01 through 2018-12-31, frozen 0.2/0.5/1.0-pip scenarios, unchanged profitability/PF/DD/trade gates, at most two survivors per family cell, 54 ranking cells, and maximum 108 Stage A survivors.

DEC-264 also predeclares terminal review in `src/fmp/portfolio/exp015_stage_a_terminal_review.py` at blob `751c886f2d00e46d3c0a20fabbe0db4231db0d5d`. A successful attempt requires exactly 11 successful jobs and all 11 expected non-expired artifacts, then independently verifies the final authorization against the result-producing commit: exact catalog/source identities, nine cells, 54 ranking cells, 567 strategies, complete cell/family/gate coverage, survivor accounting, and the Stage B source-open flag. A non-success may preserve only produced expected catalog/cell artifacts and may not claim final authorization evidence.

Focused tests are `tests/test_phase8a_exp015_stage_a_first_run_governance.py` at blob `1ea17ac6329fa798c33c51b59c44ce437e0b739e`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp015-stage-a-first-run-governance.md` at blob `ff0e20a0aed84621392561218f4bd3db1117017d`.

DEC-264 itself dispatches nothing. Stage A retry/replacement, Stage B/C execution, DEC-042 selection, DEC-045 acceptance, Phase 8B, demo, broker mutation, live orders, real-money action, and trading remain unauthorized. The next safe gate is a clean-main one-way Stage A operator that can classify missing/in-progress/terminal state but does not dispatch in its initial source-only decision.

## DEC-265 — EXP-015 Stage A clean-main one-way operator

**Date:** 2026-09-26
**Status:** SOURCE-ONLY / READ-ONLY / NOT DISPATCHED

DEC-265 binds merged DEC-264 commit `92ef2668b1a0cb416e7f772a8a061d2f280005a1`, guarded Stage A workflow blob `ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930`, and terminal-review blob `751c886f2d00e46d3c0a20fabbe0db4231db0d5d`. It adds a clean-main one-way operator for the sole bounded EXP-015 Stage A historical slot without changing any DEC-043/044 research semantics.

The operator source is `src/fmp/portfolio/exp015_stage_a_operator.py` at blob `3f2bca609ab6c1cd324f95c47be99584b11d9d90`. It requires local `main`, exact fetched `origin/main`, a clean worktree, and the exact `Dtwosam/FMP` origin. It queries only `phase8a-exp015-stage-a.yml` runs filtered to `branch=main&event=workflow_dispatch`, ignores the 12 preserved source-development push failures, rejects more than one authoritative run, and rejects any selected run with `run_attempt != 1`.

Live state is classified only as `MISSING`, `IN_PROGRESS`, or `TERMINAL`. For `MISSING`, the operator exposes `gh workflow run phase8a-exp015-stage-a.yml --ref main -R Dtwosam/FMP` only as plan evidence and requires a later repository-hosted read-only proof; `stage_a_dispatch_authorized` and `stage_a_executor_authorized` remain false. `IN_PROGRESS` exposes no dispatch plan. `TERMINAL` exposes no dispatch plan and routes back to the frozen DEC-264 terminal-review contract with no retry, rerun, or replacement authority.

Public CLI is `scripts/phase8a_exp015_stage_a_operator.py` at blob `11010d32842b0f0ab829e0cc20d4654a7d5dcf2e`. It exposes only `next`; there is no `advance`, `--execute`, workflow-dispatch endpoint, rerun, or replacement path. Focused tests are `tests/test_phase8a_exp015_stage_a_operator.py` at blob `126449be29e0c61a726bd358501cc05ea16d2663`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp015-stage-a-one-way-operator.md` at blob `32aa46252aeacf2992c481458897e2d87bd17d9e`.

DEC-265 dispatches nothing and consumes no historical slot. Stage A dispatch/executor/retry/replacement, Stage B/C execution, DEC-042 selection, DEC-045 acceptance, Phase 8B, demo, broker mutation, live orders, real-money action, and trading all remain unauthorized. The next safe gate is a repository-hosted read-only proof of the exact DEC-265 `next` plan on merged `main`; only after that proof succeeds may a separately reviewed one-shot executor source be considered.

## DEC-266 — EXP-015 Stage A repository-hosted read-only plan proof

**Date:** 2026-09-26
**Status:** SOURCE-ONLY / READ-ONLY / NOT DISPATCHED

DEC-266 binds merged DEC-265 commit `ed4373a7a0da36850a5f08971e9e12bd63cf1554`, operator blob `3f2bca609ab6c1cd324f95c47be99584b11d9d90`, CLI blob `11010d32842b0f0ab829e0cc20d4654a7d5dcf2e`, DEC-264 guarded Stage A workflow blob `ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930`, and DEC-264 terminal-review blob `751c886f2d00e46d3c0a20fabbe0db4231db0d5d`.

The repository-hosted proof workflow is `.github/workflows/phase8a-exp015-stage-a-operator-plan.yml` at blob `be3a370dc538214d1758733c0b500ee3c7921609`. It is push-to-main only, grants only `contents: read` and `actions: read`, verifies the frozen DEC-264/265 Git blobs, requires local HEAD and `origin/main` to equal the triggering `GITHUB_SHA`, requires merged DEC-265 commit `ed4373a7a0da36850a5f08971e9e12bd63cf1554` to be an ancestor of that SHA, installs only `requirements/exp015-stage-a-operator.txt` at blob `1ff32214dee10d877a067e750cd69ffad96d5fe5`, proves the worktree remains clean, invokes only `python scripts/phase8a_exp015_stage_a_operator.py next`, requires the emitted plan head SHA to equal the trigger SHA, and persists the resulting plan outside the checkout as an immutable artifact.

A successful DEC-266 proof must report DEC-265, read-only mode, zero authoritative manual-main Stage A runs, `MISSING` state, no run id, stage `EXP015_STAGE_A_READ_ONLY_PROOF_REQUIRED`, the sole authoritative slot still available, and the exact future Stage A command only as plan evidence. Stage A dispatch/executor/retry/replacement, Stage B/C, DEC-042 selection, DEC-045 acceptance, Phase 8B, demo, broker mutation, live orders, real-money action, and trading must all remain false.

Focused tests are `tests/test_phase8a_exp015_stage_a_operator_plan_runner.py` at blob `8745125bec5ae27694ddb1e0c69ffc4ec865451b`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp015-stage-a-read-only-plan.md` at blob `3fe15737641e718a364eee6bca5b8478b8586921`.

DEC-266 itself dispatches nothing and consumes no historical slot. The next safe gate is to merge DEC-266, require the merged-main proof workflow to succeed, bind that exact successful run plus its non-expired plan artifact and digest, and only then consider a separately reviewed one-shot Stage A executor source.

## DEC-267 — EXP-015 Stage A one-shot executor

**Date:** 2026-09-26
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE

DEC-267 binds successful merged-main DEC-266 proof run `36277672941` at head `82a90af8edbf156e89df3a63f2003da71d4473d3`, event `push`, branch `main`, attempt `1`, conclusion `success`. It binds the single non-expired artifact `10917841059`, named `exp015-dec265-stage-a-read-only-plan-82a90af8edbf156e89df3a63f2003da71d4473d3`, with digest `sha256:b5cc74574518bc0db4a9229e1b55117fa99ec2b17264f7ee42a538df0adc3cf3`.

Fresh-plan validator source `src/fmp/portfolio/exp015_stage_a_executor.py` is blob `840659456732b21cae1520060ab0539c9636066c`. Public executor CLI `scripts/phase8a_exp015_stage_a_executor.py` is blob `201609db2d7ed2796dd492d97a75bdee57bcc0ee`. The validator reuses DEC-265 fail-closed report validation and additionally binds DEC-265 identity, exact executor head, MISSING state, unused slot, proof-required stage, and the exact frozen Stage A dispatch tuple. The CLI requires push/main/attempt-1 environment, obtains and validates two identical fresh DEC-265 plans immediately before submission, and executes only that tuple.

Executor workflow `.github/workflows/phase8a-exp015-stage-a-operator-execute.yml` is blob `fd7c45bb6f47dcb5d441312bb58981589a7f1850`. It is push-to-main only for the executor workflow/CLI/validator paths, grants `contents: read` and `actions: write`, requires local HEAD and `origin/main` to equal the trigger SHA, requires the DEC-266 merge commit to be an ancestor, re-hashes the frozen DEC-264/265 Stage A workflow/reviewer/operator/CLI/runtime identities before any write, rejects reruns and any prior different main/push executor run, preserves a clean checkout, independently revalidates the exact DEC-266 run/artifact metadata plus ZIP digest/content, and requires zero Stage A manual-main runs immediately before execution. It invokes only the DEC-267 executor CLI; afterward it requires exactly one Stage A manual-main run with exact workflow name/path, executor merge head, and `run_attempt == 1`, then uploads immutable executor evidence.

Focused validator/CLI tests are `tests/test_phase8a_exp015_stage_a_executor.py` at blob `0b352ce29753ed747cd6fed9f98dbac2a95172e6`. Focused workflow tests are `tests/test_phase8a_exp015_stage_a_operator_executor.py` at blob `c58ad493ef3914882e5d3106a5f91f83d056c0f7`. Detailed spec is `docs/superpowers/specs/2026-09-26-phase8a-exp015-stage-a-one-shot-executor.md` at blob `f6624bd62b9fc6880bf55166232f7a1ae867e9f7`.

If the merged-main executor submits Stage A, that first manual-main run consumes the DEC-264 slot on any terminal outcome. No second executor attempt, Stage A rerun, retry, or replacement is authorized. Any terminal Stage A result must route through DEC-264. Stage B/C, DEC-042 selection, DEC-045 acceptance, Phase 8B, demo, broker mutation, live orders, real-money action, and trading remain unauthorized.

## DEC-268 — Phase 8A discovery-first strategy research and iterative demo learning

**Date:** 2026-09-27
**Status:** APPROVED SOURCE-OF-TRUTH AMENDMENT / NO TRADING AUTHORIZATION

DEC-268 changes the default future Phase 8A strategy-research direction from baseline-family-first candidate generation to discovery-first market-pattern research.

The six historical rule families and all prior experiments remain immutable evidence and useful controls. They are not deleted or relabeled, but they are no longer the required or complete strategy universe for new research. Future discovery may derive repeated behaviours directly from leakage-safe historical measurements across direction/trend, sideways/range, volatility, momentum/structure, session/time, spread, and fixed future outcomes before translating selected patterns into exact strategy/model versions.

Because broad discovery increases overfitting and multiple-comparison risk, every serious discovery run must freeze its discovery range, measurements/features, future-outcome definitions/horizons, minimum support, bounded search method/budget, transaction-cost treatment, duplicate handling, search-volume accounting, candidate-freeze rule, and later chronological validation procedure before its results are used for promotion. Validation data may test a frozen discovered candidate; it may not redesign the candidate.

DEC-268 also formalizes demo trading as an iterative learning source. A registered demo campaign runs an immutable version. Completed demo observations may later motivate or train a new challenger, but once those observations influence that challenger they become research/training evidence for it and cannot also count as fresh validation. Every materially changed challenger receives a new immutable identity and must prove itself on a later fresh prospective shadow/demo window. No self-modification, hot-swapping, martingale, leverage escalation, emergency post-loss tuning, or outcome-aware threshold relaxation is permitted.

The already-dispatched EXP-015 Stage A run `36279397331` at head `500f12ca5cb6e611f93b5d3a9eb52fb678e7774f`, attempt 1, has consumed the sole DEC-264 Stage A slot. It may finish once and must be reviewed as historical evidence. DEC-268 authorizes no retry, rerun, replacement, and no automatic continuation into EXP-015 Stage B/C even if Stage A contains survivors.

Detailed amendment: `docs/superpowers/specs/2026-09-27-phase8a-discovery-first-amendment.md`.

Phase 8B, demo-order submission, broker mutation, live orders, real-money action, and trading remain locked. The next new Phase 8A implementation should be a bounded discovery-first protocol across the three V1 pairs; DEC-268 itself executes no research run and opens no broker path.

## DEC-269 — EXP-015 Stage A reviewed failure freeze

**Date:** 2026-09-27
**Status:** REVIEWED / CLOSED / FAILED / NO RETRY

DEC-269 closes the sole authoritative EXP-015 Stage A attempt, run `36279397331`, workflow `phase8a-exp015-stage-a`, main head `500f12ca5cb6e611f93b5d3a9eb52fb678e7774f`, attempt 1, terminal conclusion `failure`.

The catalog job succeeded. Eight of nine matrix cells completed successfully and persisted non-expired artifacts. USDJPY 1h job `108508311714` failed inside the frozen Stage A computation with the exact terminal signature `ValueError: daily start equity must be finite and positive`. The reporting guard therefore failed closed instead of emitting ordinary metrics from an invalid account-equity state. The final `stage-a-authorize` job `108538985395` was skipped, no authorization artifact exists, and no authoritative aggregate Stage A survivor set was produced.

DEC-269 binds the exact catalog artifact plus the eight successful cell artifact ids/digests. The USDJPY 1h cell artifact is absent by construction.

The predeclared DEC-264 terminal reviewer also contains a result-review compatibility defect: it requires short matrix job names such as `stage-a-cell (USDJPY, 1h)`, while GitHub persisted expanded/truncated matrix-value names for the real run. DEC-269 does not alter the guarded Stage A workflow or reinterpret the result. Instead it binds this exact already-completed run through immutable run id, head, attempt, exact job ids/conclusions, exact artifact ids/digests, the absent failed-cell/authorization artifacts, and the exact failure signature.

Result-decision source is `src/fmp/portfolio/exp015_stage_a_failure_result_decision.py` at blob `dbf9a34fc8a22c92b06e0b40ac5e97a5cf041029`. Focused tests are `tests/test_phase8a_exp015_stage_a_failure_result_decision.py` at blob `35d4adaaf66b7e8f4e85e51e2baaa3afbf977aec`. Detailed evidence contract is `docs/superpowers/specs/2026-09-27-phase8a-exp015-stage-a-failure-freeze.md`.

The one Stage A slot remains consumed permanently. Stage A retry/replacement, Stage B source-open, Stage B/C execution, portfolio selection, Phase 8A acceptance, Phase 8B, demo orders, broker mutation, live orders, real-money action, and trading are all false.

EXP-015 is closed as pre-DEC-268 historical evidence. The next research work proceeds under DEC-268 discovery-first market-pattern research rather than rescuing or retuning EXP-015.

## DEC-270 — EXP-061 discovery-first market-state pattern protocol

**Date:** 2026-09-27
**Status:** APPROVED SOURCE-ONLY PROTOCOL / RESULT EXECUTION LOCKED

DEC-270 opens EXP-20260927-061 as the first bounded implementation of DEC-268 discovery-first research. It does not start from the six historical strategy families.

EXP-061 freezes exactly EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m outcomes. It derives market states from exactly 20 existing leakage-safe feature values plus one deterministic mutually exclusive session dimension. Continuous states are LOW/MID/HIGH using exact 2015-2017 empirical tertile order statistics; tied cutpoints skip that dimension rather than being repaired.

Patterns may contain one or two distinct dimensions only. The maximum search universe is 65 atomic states, 2,075 admissible state patterns per cell/horizon, 4,150 directional LONG/SHORT hypotheses per cell/horizon, and 74,700 directional hypotheses globally. Search volume must be recorded. No third predicate, added feature, alternate binning, extra horizon, extra pair, or result-driven feature invention is allowed inside EXP-061.

Chronology is exact: 2015-2017 discovery; 2018 pass/fail confirmation; 2019-2022 frozen validation; 2023-01-01 through 2026-08-20 inclusive remains closed to EXP-061 and reserved for a later compiled-strategy robustness experiment. Every fixed-horizon outcome must also exit strictly before its current window end; cross-boundary outcomes are purged.

The discovery gate requires at least 300 total observations, at least 75 per discovery year, aggregate 0.5-pip mean net pips >= 0.25, positive 0.5-pip mean in every discovery year, and positive aggregate 1.0-pip stress mean. Near-duplicates at discovery-event Jaccard >= 0.90 are removed by immutable discovery rank. At most 10 per cell/horizon reach 2018 confirmation, for at most 180. Confirmation does not rerank; among passers, original discovery rank freezes at most 3 per cell/horizon, for at most 54 validation hypotheses.

2019-2022 validation requires at least 200 total observations, at least 40 per year, positive aggregate 0.5-pip mean, and positive yearly mean in at least 3 of 4 years. Validation cannot redefine a pattern.

A surviving EXP-061 object is a pattern hypothesis, not an executable strategy. Entry/stop/target/overlap/risk/portfolio semantics require a later candidate-compilation decision before the reserved block can be opened.

Frozen source: `src/fmp/discovery/pattern_protocol.py` blob `63b3f0121d6a50eb9e8e62ab666d70eb91791621`. Focused tests: `tests/test_phase8a_exp061_pattern_protocol.py` blob `b15a7bc19cc9523166d4b92e8c75f5784bf50fa1`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-discovery-first-pattern-protocol.md`.

Historical source access, discovery execution/result production, candidate compilation, reserved-block access, promotion, Phase 8B, demo orders, broker mutation, live orders, real-money action, and trading remain false. The next safe gate is a deterministic in-memory miner core only.

## DEC-271 — EXP-061 deterministic in-memory pattern miner core

**Date:** 2026-09-27
**Status:** SOURCE-ONLY CORE / HISTORICAL EXECUTION LOCKED

DEC-271 implements the deterministic in-memory core for the DEC-270 / EXP-20260927-061 discovery-first pattern protocol.

The core defines strict feature and directional-outcome row contracts, calibrates empirical-tertile cutpoints from 2015-2017 only, enumerates every admissible one/two-dimension pattern under the frozen bound, evaluates LONG/SHORT economics, applies exact support/economic gates, uses the immutable discovery ranking, removes same-direction Jaccard-near-duplicates, and returns at most the frozen discovery shortlist.

2018 confirmation evaluates the shortlist in original discovery order, is pass/fail only, and freezes at most the first three passers per cell/horizon without reranking. 2019-2022 validation applies the frozen support/profitability/positive-year gate without altering a pattern.

The core scopes every step to DEC-270 windows. Focused tests inject catastrophic 2023 rows and require the complete in-memory result to remain unchanged, proving the reserved 2023-2026 block cannot leak into EXP-061 mechanics.

Focused synthetic evidence also proves that a data-derived `return_1h=HIGH` condition can be found without naming a strategy family, that an event-equivalent two-predicate version is removed by Jaccard deduplication, and that the frozen single-state hypothesis proceeds through confirmation and validation mechanically. This synthetic case is a software proof only, not market evidence.

Core source: `src/fmp/discovery/pattern_miner.py` blob `495a67699eb5014e52129f0238a2737049fe38e6`. Focused tests: `tests/test_phase8a_exp061_pattern_miner.py` blob `9694a4185906c48dc5222722723ac28810cd2340`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-in-memory-pattern-miner-core.md`.

Historical source access, historical discovery execution, reserved-block access, candidate compilation, promotion, Phase 8B, demo orders, broker mutation, live orders, real-money action, and trading remain false.

The next safe gate is a non-executable artifact/evidence contract plus deterministic adapter from already-approved market-learning feature/outcome artifacts into the DEC-271 row contracts. No historical result-producing run is authorized by DEC-271.

## DEC-272 — EXP-061 market-learning adapter and cell evidence contract

**Date:** 2026-09-27
**Status:** SOURCE-ONLY ADAPTER / HISTORICAL EXECUTION LOCKED

DEC-474 binds merged DEC-473 commit
`f3fd12018ff9602dbc233b0b5c99bf6764489ea8`.

DEC-272 reuses the already-approved EXP-044 market-learning feature/outcome schemas as the sole input vocabulary for DEC-271 rather than creating another historical data pipeline.

The adapter converts verified Polars feature/outcome frames into immutable EXP-061 feature/outcome observations using a deterministic identity over symbol, timeframe, bar start, availability time, feature-set version, and processed Phase 2 manifest SHA-256. It requires exact symbol/timeframe, exact feature/outcome set identities, singular matching processed-manifest SHA-256, supported horizons, exact retrospective evidence labeling, and unique row identities.

The accepted adapter range is 2015-01-01 through 2022-12-31. Feature rows at or after 2023-01-01 are rejected. Outcome rows whose observation is outside that range or whose fixed-horizon target reaches 2023-01-01 or later are rejected. This prevents the reserved 2023-2026 robustness target data from being presented to EXP-061.

DEC-272 also defines canonical per-cell evidence containing protocol/code/source identities, the exact feature-manifest and outcome-manifest SHA-256s, state cutpoints, discovery search counts/shortlist, confirmation evaluations/frozen fingerprints, validation evaluations/validated fingerprints, and explicit false downstream authorizations. Evidence is canonical-JSON fingerprinted and tamper-checked. The validator also rechecks nested cell/state/search identities, pattern fingerprints, discovery gates/rank order, confirmation freeze semantics, and validation acceptance semantics, so a semantically inconsistent result cannot pass by merely recomputing the outer evidence hash.

Source: `src/fmp/discovery/market_learning_adapter.py` blob `978a33554fad7e9d78b002778c4896be0af3333a`. Focused tests: `tests/test_phase8a_exp061_market_learning_adapter.py` blob `0fffb06e772c8bee82208c598f75d29b3804b781`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-market-learning-adapter-evidence.md`.

DEC-272 does not load artifacts and does not authorize historical source access, historical discovery execution, reserved-block access, candidate compilation, promotion, Phase 8B, demo orders, broker mutation, live orders, real-money action, or trading.

The next safe gate is a verified range-limited artifact loader for existing EXP-044 feature/outcome evidence, with historical result execution still separately locked.

## DEC-273 — EXP-061 verified range-limited artifact loader

**Date:** 2026-09-27
**Status:** SOURCE-ONLY LOADER / HISTORICAL EXECUTION LOCKED

DEC-473 binds merged DEC-472 commit
`310d31183802a2c29aad3f20ad6a6aa4990d579d`.

DEC-273 adds the verified artifact-loader boundary for EXP-20260927-061.

The loader recomputes supplied EXP-044 feature/outcome aggregate evidence fingerprints, requires exact outcome-to-feature evidence binding, exact requested cell manifests, a shared Phase 2 processed-manifest SHA-256, and exact outcome-manifest binding to the feature-manifest SHA-256.

Only the frozen 96 monthly partitions from 2015-01 through 2022-12 are selected for each requested feature and outcome cell. No 2023-01 or later monthly partition is selected or opened. Every selected artifact is checked for safe path containment, current file presence, exact size, SHA-256, Parquet schema, and row count. Outcome rows whose fixed-horizon exit reaches 2023-01-01 are filtered before DEC-272 adaptation.

The output is a verified feature/outcome frame pair plus exact manifest/evidence identities and selected artifact paths. It is still only source plumbing: DEC-273 does not invoke DEC-271 mining and does not produce a historical discovery result.

Loader source: `src/fmp/discovery/range_limited_loader.py` blob `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`. Focused tests: `tests/test_phase8a_exp061_range_limited_loader.py` blob `f6ec2d8846491fb2cbc06d7eea064c0e72af45ee`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-range-limited-loader.md`.

Historical discovery execution, discovery-result production, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo orders, broker mutation, live orders, real-money action, and trading remain false.

The next safe gate is a non-executing 18-cell EXP-061 run/evidence contract that composes DEC-273 -> DEC-272 -> DEC-271 -> DEC-272 evidence without opening workflow dispatch.

## DEC-274 — EXP-061 non-executing 18-cell run contract

**Date:** 2026-09-27
**Status:** SOURCE-ONLY RUN CONTRACT / WORKFLOW AND HISTORICAL EXECUTION LOCKED

DEC-274 freezes the exact result shape required for any later authorized EXP-20260927-061 historical discovery run.

The reserved future workflow identity is `phase8a-exp061-discovery` at `.github/workflows/phase8a-exp061-discovery.yml`, manual `workflow_dispatch`, branch `main`, authoritative run attempt 1. DEC-274 itself creates no workflow and authorizes no dispatch.

The exact run inventory is 20 jobs: `exp061-preflight`, 18 explicit cell jobs named `exp061-cell-<symbol>-<timeframe>-<horizon>m`, and `exp061-aggregate`. Explicit names avoid GitHub implicit matrix-name ambiguity. A successful future run requires exactly 20 non-expired artifacts: one preflight, 18 commit-scoped cell artifacts, and one aggregate artifact.

Every cell evidence object must pass DEC-272's hardened semantic validator and bind the exact Phase 2 source SHA, feature manifest SHA, outcome manifest SHA, feature evidence fingerprint, and outcome evidence fingerprint. The aggregate compiler requires all 18 cells, one code commit, exact accepted source identities, one global feature-evidence fingerprint, one global outcome-evidence fingerprint, cross-horizon manifest consistency per symbol/timeframe, and the frozen 180/54 global pattern caps.

The aggregate validator independently rechecks cell order, source/manifests, fingerprint inventories/subset relations, count reconciliation, global caps, and downstream locks. Re-fingerprinted but semantically inconsistent aggregate evidence fails closed.

A later separately authorized non-success would consume that run slot and defaults to no rerun, retry, or replacement. Partial expected cell evidence may be retained diagnostically. A success still opens no reserved 2023-2026 data, candidate compilation, Phase 8B, demo, broker/live, real-money, or trading path.

Run-contract source: `src/fmp/discovery/run_contract.py` blob `260eb6930673427266463517546969635188b143`. Focused tests: `tests/test_phase8a_exp061_run_contract.py` blob `820a616fe98d08dc7a15973ccec4246a64f2b30a`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-run-contract.md`.

All workflow source/dispatch, historical discovery/result execution, rerun/retry/replacement, reserved-block access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading authorizations remain false.

The next safe gate is workflow/CLI source freeze only, still with execution locked and no dispatch path.

## DEC-275 — EXP-061 dormant workflow and CLI source freeze

**Date:** 2026-09-27
**Status:** DORMANT SOURCE FROZEN / NOT INSTALLED / HISTORICAL EXECUTION LOCKED

DEC-275 freezes the future EXP-061 workflow/CLI source while deliberately keeping it outside GitHub's active workflow directory.

The dormant template lives at `docs/superpowers/templates/phase8a-exp061-discovery.yml.disabled`; the reserved active path `.github/workflows/phase8a-exp061-discovery.yml` remains absent. Template installation, dispatch, historical discovery execution, and result production remain false.

The source pins the exact accepted EXP-044 data-preparation lineage: feature run `35867307338` at `b71912e254d2a597c0ef55b5e1b3b87b052039ea`, outcome run `35876715434` at `edeb43bb4de88923e3349caa8ace36350839ccb8`, exact aggregate feature/outcome evidence artifact ids/digests, and all nine feature plus nine outcome cell artifact ids/digests. No runtime input may substitute another upstream run.

The dormant template preserves the DEC-274 topology: one preflight job, an 18-entry matrix whose explicit name expression renders the exact `exp061-cell-<symbol>-<timeframe>-<horizon>m` names, and one aggregate job. It pins Python `3.12.14`, `polars==1.44.2`, and `polars-runtime-32==1.44.2`.

The preflight may perform only read-only source-metadata validation. It then invokes the hard DEC-275 execution gate. Every cell and the aggregate path recheck the same gate. The CLI `cell` command invokes that gate before opening any feature/outcome/evidence path, and `aggregate` invokes it before opening any cell-result file. Under DEC-275 the gate always raises `PermissionError`.

If a later successor explicitly authorizes execution, the frozen cell source is already composed as DEC-273 loader -> DEC-272 adapter -> DEC-271 miner -> DEC-272 cell evidence, and aggregate source is DEC-274 aggregate compilation/revalidation. DEC-275 itself activates none of those historical paths.

Frozen identities: workflow-source contract `src/fmp/discovery/workflow_source.py` blob `68566fc86ff3470cc8b6ebef606becaff9f3450b`; CLI `scripts/phase8a_exp061.py` blob `bd40f17566f4c03e623215fe9e615b00b2fc9039`; dormant template blob `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`; focused tests blob `4c8266b07c0fe9912691da298cc4963e28a2a66a`; runtime requirements blob `1ff32214dee10d877a067e750cd69ffad96d5fe5`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-dormant-workflow-source.md`.

Active workflow installation, dispatch, historical discovery/result execution, rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo orders, broker mutation, live orders, real-money action, and trading remain false.

The next safe gate is installation of the exact reviewed dormant template at the reserved active workflow path while retaining the execution gate false, followed by merged-main proof that it cannot progress past authorization preflight.

## DEC-276 — EXP-061 locked active-workflow installation

**Date:** 2026-09-27
**Status:** ACTIVE WORKFLOW INSTALLED / EXECUTION AND PROOF DISPATCH LOCKED

DEC-276 installs the exact DEC-275 dormant workflow source at `.github/workflows/phase8a-exp061-discovery.yml` without changing any execution semantics.

The active workflow blob and the dormant template blob are both `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`. Any byte-level drift invalidates the installation review.

The workflow remains fail-closed. Preflight may perform only read-only metadata checks against the already-completed EXP-044 feature/outcome runs before invoking `python scripts/phase8a_exp061.py require-execution --code-commit "$GITHUB_SHA"`. Under DEC-276 that gate remains false. The 18 cell jobs depend on successful preflight and independently recheck the same gate before any historical feature/outcome artifact download. Aggregate compilation also rechecks the gate before reading cell evidence.

DEC-276 distinguishes workflow presence from authorization. Ordinary workflow dispatch, proof dispatch, historical-result dispatch, historical discovery/result execution, rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading all remain false.

Installation validator source: `src/fmp/discovery/workflow_install.py` blob `e959a782fdbb6bf5b578e60e44f5e015b50086a6`. Focused tests: `tests/test_phase8a_exp061_locked_workflow_install.py` blob `7996c2c1565352984ecd1bbff3ca538beda5b616`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-locked-workflow-install.md`.

The next safe gate is a separately predeclared one-shot proof-only manual-main dispatch whose expected terminal outcome is a fail-closed stop at the DEC-275 execution gate after read-only preflight. That proof may not consume the future historical result slot and may not authorize cell or aggregate execution.

## DEC-277 — EXP-061 gate-proof terminal contract

**Date:** 2026-09-27
**Status:** SOURCE-ONLY PROOF CONTRACT / NO DISPATCH AUTHORIZED

DEC-277 freezes the terminal review semantics for a future proof-only run of the installed EXP-061 workflow. It authorizes no dispatch.

A later proof authorization must bind an exact merged-main head. The proof run must be the reserved workflow on manual `main`, attempt 1, terminal `failure`. The preflight job must fail at the DEC-275 execution gate. Any downstream cell or aggregate job that GitHub materializes must be terminal `skipped`; DEC-277 intentionally does not require GitHub to materialize every skipped matrix child.

Exactly one non-expired preflight artifact is allowed. No cell artifact and no aggregate artifact may exist. The preflight JSON must cross-bind the exact proof commit, the deterministic DEC-275 workflow-source payload, accepted EXP-044 source identities, intact source fingerprint, `source_ready=true`, and all historical/result/trading permissions false.

A valid proof consumes no historical-result slot and opens no historical discovery/result execution, reserved 2023-2026 data, candidate compilation, Phase 8B, demo, broker/live, real-money, or trading path.

Proof-contract source: `src/fmp/discovery/proof_contract.py` blob `1a2b6c404cba4e1f6e9b28d46a0671a6a318e48a`. Focused tests: `tests/test_phase8a_exp061_gate_proof_contract.py` blob `bd4f837c99090bcabc1ef8932b39653dc1d137e5`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-gate-proof-contract.md`.

The next safe gate is a separate exact-head proof authorization after DEC-276/277 are merged green. That later decision may authorize one proof-only dispatch but must keep historical discovery/result execution false.

## DEC-278 — EXP-061 read-only gate-proof operator

**Date:** 2026-09-27
**Status:** SOURCE-ONLY OPERATOR / NO EXECUTE MODE / NO DISPATCH AUTHORIZED

DEC-278 adds a read-only planner for the future EXP-061 gate proof. It requires current main metadata, workflow-run history, and an exact caller-supplied expected head. Main must equal that head.

When no matching manual-main EXP-061 run exists, the operator reports `EXP061_PROOF_DISPATCH_AUTHORIZATION_REQUIRED` and exposes only `gh workflow run phase8a-exp061-discovery.yml --ref main`. The report still records proof dispatch authorization false and execute mode unavailable.

Once any matching manual-main EXP-061 run exists, the operator reports `EXP061_PROOF_RUN_PRESENT_REVIEW_REQUIRED` and removes the dispatch command. It cannot plan a second proof automatically.

The CLI `scripts/phase8a_exp061_proof_operator.py` has only a `plan` command. It has no execute/dispatch/advance/retry mode.

Operator source: `src/fmp/discovery/proof_operator.py` blob `b8af93555656d4da57ead8fc4b66ae66e62a2de7`. CLI blob: `4f074f5abecd006d032f9897a1e527aa694a233d`. Focused tests blob: `9f4a678e4a3ed6d37216387796d00da28620cd30`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-proof-operator.md`.

Proof dispatch, historical-result dispatch/execution, discovery-result production, reserved-block access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is an exact merged-main-head proof authorization after two identical fresh read-only plans.

## DEC-279 — EXP-061 one-shot proof-only executor

**Date:** 2026-09-27
**Status:** APPROVED SOURCE / ONE PROOF DISPATCH AFTER MERGE ONLY

DEC-279 authorizes exactly one proof-only dispatch of the installed EXP-061 workflow after the DEC-279 executor merges to main. The proof is expected to fail at the still-locked DEC-275 execution gate. It is not a historical discovery run and does not consume the future historical-result slot.

Immediately before submission the executor reads live main/workflow-run metadata twice through the DEC-278 read-only operator. Both plans must be identical, bind the exact executor main head, show zero matching manual-main EXP-061 runs, expose the exact frozen proof command, and keep DEC-278 proof dispatch/execute plus every historical/result/trading authority false. DEC-279 supplies only the single proof-dispatch authority.

Validator source: `src/fmp/discovery/proof_executor.py` blob `0558b5d6b5db41e252cfb0e1cc3bc46ef489b0d0`. CLI: `scripts/phase8a_exp061_proof_executor.py` blob `db3fdb6d283ce33a71a6dd57eebfef70874fd40a`. One-shot workflow: `.github/workflows/phase8a-exp061-proof-one-shot-execute.yml` blob `7e9b31d3dc521b05ed5dedaafa57afef57222ef2`. Focused tests: `tests/test_phase8a_exp061_proof_executor.py` blob `a331da912f06cd9f34ba510c1e86ba726ab6c0fd`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-proof-one-shot-executor.md`.

The executor workflow pins the active EXP-061 workflow, DEC-275 workflow-source contract, DEC-277 proof contract, DEC-278 operator/CLI, DEC-279 validator/CLI, and pinned runtime before any GitHub write. It requires no prior DEC-279 executor run and no prior target proof run, then polls only until exactly one proof run is visible at the DEC-279 merged-main head.

Historical-result dispatch, historical discovery execution, discovery-result production, proof retry/rerun/replacement, reserved-block access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is terminal review of the one proof run through DEC-277, followed by a DEC-280 reviewed-proof freeze.

## DEC-280 — EXP-061 reviewed gate-proof freeze

**Date:** 2026-09-27
**Status:** REVIEWED / EXPECTED FAIL-CLOSED PROOF / HISTORICAL RUN STILL LOCKED

DEC-280 freezes the exact terminal evidence from the sole DEC-279 proof-only dispatch. Executor run `36319870713` completed successfully at merged main `041b7b2f5aac8821156fab346df8ab30f4be2a7b` and submitted exactly one target proof run, `36319888985`, at the same head. The proof completed `failure` by design: `exp061-preflight` failed only at the separately-authorized-execution gate, while the materialized matrix dependency and `exp061-aggregate` were both skipped. No historical cell or aggregate result executed.

GitHub materialized the skipped matrix dependency as the literal unexpanded job-name expression `exp061-cell-${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-${{ matrix.dataset.horizon }}m`. DEC-277 allowed skipped matrix children to be elided but required any materialized downstream name to be one of the concrete DEC-274 names, so its generic terminal validator does not accept this GitHub API representation. DEC-280 does not rewrite DEC-277 or rerun the proof. It binds the exact immutable three-job shape, requires the placeholder to remain skipped, and preserves the predeclared fail-closed meaning.

Exactly one preflight artifact exists: id `10932485842`, digest `sha256:0dfbf4c76874bb2b056a835ff0d7fdf2199ddda279e40a60924128a7ff29573d`. DEC-280 revalidates the DEC-275 preflight source fingerprint, exact proof head, deterministic workflow-source payload, accepted EXP-044 source identities, nine verified pair/timeframe sources, and all historical/result/trading permissions false. Cell-result and aggregate-result artifact counts are zero. The future historical-result slot remains unconsumed and unopened.

Reviewed-proof source: `src/fmp/discovery/proof_result_decision.py` blob `fbed3788ab0c1c1e00dccfe0f84a293ff04f6ccd`. Focused tests: `tests/test_phase8a_exp061_reviewed_gate_proof.py` blob `06b9801ac006ae9a5054327071fc4193ebfafc40`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-reviewed-gate-proof.md`.

Proof rerun/retry/replacement, historical-result dispatch/execution, discovery-result production, reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is a separate source-only historical-run authorization contract for at most one bounded 2015-2022 EXP-061 discovery-result attempt. DEC-280 itself authorizes no historical dispatch or execution.


## DEC-281 — EXP-061 historical-run authorization contract

**Date:** 2026-09-27
**Status:** SOURCE-ONLY ONE-SLOT AUTHORIZATION / DISPATCH + EXECUTION STILL LOCKED

DEC-281 freezes the source-only contract for at most one bounded EXP-061 historical discovery-result attempt. Immediately after DEC-280 merged, the exact manual-main workflow history contains one EXP-061 run only: proof run `36319888985`, attempt 1, terminal failure at proof head `041b7b2f5aac8821156fab346df8ab30f4be2a7b`. DEC-281 excludes exactly that frozen proof from the historical-result slot. No historical discovery-result attempt exists yet.

The contract binds DEC-280 merge `da40f1cf3b45b111bb87099353ec79d5f2b95918`, reviewed-proof blob `fbed3788ab0c1c1e00dccfe0f84a293ff04f6ccd`, the unchanged active workflow/CLI/runtime, DEC-274 run contract, DEC-275 workflow source, DEC-276 locked install, DEC-277 proof contract, and the DEC-270 through DEC-273 discovery implementation blobs. Every pre-existing dispatch/execution/result/rerun/retry/replacement/reserved-data/downstream trading authorization in those layers must remain false.

DEC-281 opens only the outer source-governance slot: `historical_result_slot_source_authorized=true`. Actual historical-result dispatch, historical discovery execution, discovery-result production, rerun, retry, replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain false.

The first later non-proof manual-main EXP-061 run consumes the slot immediately regardless of queued/running/terminal state or terminal outcome. A second historical attempt is invalid. A GitHub rerun with `run_attempt != 1` is invalid. The frozen proof itself never consumes the slot.

Historical-run authorization source: `src/fmp/discovery/historical_run_authorization.py` blob `1eab1cee2fc81441cf1c3168cc73275cd29addf5`. Focused tests: `tests/test_phase8a_exp061_historical_run_authorization.py` blob `07886d2fde86e75eb1c92509733909c58c95c8ee`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-historical-run-authorization.md`.

The next safe gate is a clean-main read-only operator that may expose the single historical dispatch command only while the exact DEC-281 inventory remains slot-available. DEC-281 provides no execute mode and does not dispatch or execute the workflow.


## DEC-282 — EXP-061 read-only historical-slot operator

**Date:** 2026-09-27
**Status:** SOURCE-ONLY READ-ONLY OPERATOR / NO EXECUTE MODE

DEC-282 adds the read-only operator for the single DEC-281 source-authorized EXP-061 historical-result slot. It requires current `main` metadata, current EXP-061 workflow-run history, and an exact caller-supplied expected main head. Any main-head mismatch fails closed.

The operator delegates slot classification to DEC-281. While the exact DEC-280 proof run remains the only manual-main EXP-061 run, it reports `EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE` and exposes only the future command `gh workflow run phase8a-exp061-discovery.yml --ref main` as plan evidence. The report still keeps historical-result dispatch authorization false and execute mode unavailable.

Once any later historical-result run exists, the operator reports `EXP061_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED`, marks the slot consumed through DEC-281, removes the command, and cannot plan a second run.

Operator source: `src/fmp/discovery/historical_operator.py` blob `1ffef37d94b04a8206f665c375dc0b2642c4caa9`. CLI: `scripts/phase8a_exp061_historical_operator.py` blob `4d667d05ef2a5bd672cb9d98a81f13dd2ba9370c`. Focused tests: `tests/test_phase8a_exp061_historical_operator.py` blob `16399b4602fbd94b875d00abe706ae6fc815e802`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-historical-operator.md`.

Historical-result dispatch/execution, discovery-result production, rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is a repository-hosted read-only proof of the exact DEC-282 slot-available plan on merged main. That proof may capture immutable plan evidence but must not dispatch the historical workflow.


## DEC-283 — EXP-061 repository-hosted historical plan proof

**Date:** 2026-09-27
**Status:** SOURCE-ONLY READ-ONLY PROOF / NOT DISPATCHED

DEC-283 adds a repository-hosted read-only proof for the exact DEC-282 historical-slot plan on merged `main`. The workflow is push-to-main only, grants `contents: read` and `actions: read`, has no manual dispatch or schedule, installs the pinned runtime without editable checkout, requires a clean worktree, and invokes only the DEC-282 `plan` command.

Before planning it pins the exact DEC-280 reviewed-proof source, DEC-281 historical authorization source, DEC-282 operator/CLI, active locked EXP-061 workflow, and pinned runtime requirement blobs. It then reads current main metadata and exact EXP-061 manual-main workflow history through read-only GitHub API calls.

A successful merged-main proof must show frozen proof run `36319888985` exactly once, zero historical-result attempts, an unconsumed slot, stage `EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE`, and the exact future `gh workflow run phase8a-exp061-discovery.yml --ref main` command as plan evidence only. Historical-result dispatch and execute mode remain false.

Read-only proof workflow: `.github/workflows/phase8a-exp061-historical-plan.yml` blob `7c2d7409d1a05ce287cc36f5371a85273a6a027b`. Focused tests: `tests/test_phase8a_exp061_historical_plan_proof.py` blob `e25e8cbb435a106ca22e29d2e810e9c23cc25892`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-historical-plan-proof.md`.

DEC-283 cannot call the target workflow, cannot execute/advance/retry/rerun/replace, cannot open historical cell artifacts, and cannot claim a discovery result. It consumes no historical-result slot. Reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading remain locked.

Only after the DEC-283 merged-main proof succeeds and its exact non-expired plan artifact is independently bound may a separate one-shot historical executor source be considered.


## DEC-284 — EXP-061 reviewed historical-plan proof

**Date:** 2026-09-27
**Status:** REVIEWED / HISTORICAL SLOT VERIFIED AVAILABLE / EXECUTION STILL LOCKED

DEC-284 freezes the exact successful DEC-283 merged-main read-only plan proof. DEC-283 merged at `7fd3a9e878bf2760850037548e93dc1e8173c0c1`; proof run `36323674455` completed `success`, attempt 1, on the same head. Every step passed, including exact-main/source binding, clean-worktree proof, live run-inventory fetch, DEC-282 plan execution, slot-available validation, and immutable artifact upload.

Exactly one plan artifact exists: id `10932743232`, name `exp061-dec283-historical-plan-7fd3a9e878bf2760850037548e93dc1e8173c0c1`, digest `sha256:a71585da8c7e858d7ed309cf52965c5a0fbb7ef42b65e28a18933792eeb9460a`, non-expired. The downloaded ZIP independently matches that digest and contains exactly one `historical-plan.json`. Raw plan SHA-256 is `7cbe58c3ec256ff0973c9baa86e109486f0c2e37eaa973bf053fa1337cc1849e`; canonical plan SHA-256 is `605af14b35bdf132217340e7701263bfaf24d6280d6e45edbb43d2d1debc35de`.

The frozen plan proves DEC-282/DEC-281 identity, exact frozen proof run `36319888985`, zero historical-result attempts, an unconsumed slot, stage `EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE`, and the future `gh workflow run phase8a-exp061-discovery.yml --ref main` command as evidence only. Historical-result dispatch/execution, discovery-result production, rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading all remain false.

Reviewed-plan source: `src/fmp/discovery/historical_plan_result_decision.py` blob `14d9c559eaa33e5cb217baaf3ed2597091735b18`. Focused tests: `tests/test_phase8a_exp061_reviewed_historical_plan_proof.py` blob `7cf308e67232b441530230555fe19230d89b0304`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-reviewed-historical-plan-proof.md`.

The next safe gate is a separate source-only historical execution-authorization transition that binds DEC-284 before changing the runtime gate. It must keep the one-attempt rule, 2015-2022-only history, closed 2023-2026 robustness block, and all downstream trading paths locked.


## DEC-285 — EXP-061 historical execution authorization

**Date:** 2026-09-27
**Status:** SOURCE-ONLY RUNTIME AUTHORIZATION / HISTORICAL DISPATCH STILL LOCKED

DEC-285 is the first transition that permits the frozen EXP-061 historical workflow runtime to pass its execution gate for exactly one later historical-result attempt. It binds reviewed DEC-284 source blob `14d9c559eaa33e5cb217baaf3ed2597091735b18`, keeps the active workflow byte-for-byte unchanged at blob `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`, and preserves the frozen DEC-275 workflow-source execution flag as false.

The public `scripts/phase8a_exp061.py` CLI now routes `require-execution`, cell, and aggregate gates through the new DEC-285 runtime authorization. Activated CLI blob: `477aa9e8de4452e6444d1ee4361218aca445180d`. The gate still executes before any historical loader call or historical result read, and preflight evidence now carries an explicit DEC-285 execution-authorization payload.

The prior fail-closed proof run `36319888985` is confirmed as workflow run number 1, attempt 1. DEC-285 accepts runtime execution only for `phase8a-exp061-discovery` on `Dtwosam/FMP`, manual main dispatch, exact runtime SHA binding, workflow run number 2, and run attempt 1. Run number 1 is the frozen proof; run number 3+ is rejected; any rerun of run 2 is rejected through `GITHUB_RUN_ATTEMPT != 1`. The runtime run id must be positive and distinct from the proof run id, and the proof head cannot be reused.

DEC-285 sets historical execution source authorization, exact-runtime historical discovery execution, and discovery-result production true. It keeps historical-result dispatch, rerun, retry, replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker mutation, live orders, real-money action, and trading false.

Authorization source: `src/fmp/discovery/historical_execution_authorization.py` blob `30258e076f6a786c977fac8c588ac2b22aeed66e`. Focused tests: `tests/test_phase8a_exp061_historical_execution_authorization.py` blob `2636ae1daa6e90607bc86fde454bfb5b32b53f34`. DEC-281 current-source tests are updated to record the intentional activated-CLI supersession while preserving its run-inventory semantics.

The next safe gate is a separate read-only historical execution operator. It may prove the live inventory is still proof-run-only and expose the single future dispatch command as plan evidence, but must provide no execute mode.


## DEC-286 — EXP-061 read-only historical execution operator

**Date:** 2026-09-27
**Status:** SOURCE-ONLY READ-ONLY OPERATOR / NO EXECUTE MODE

DEC-286 adds the read-only planner for the DEC-285 one-shot historical runtime. It binds DEC-285 source blob `30258e076f6a786c977fac8c588ac2b22aeed66e`, requires current `main` to equal the caller-supplied expected head, validates the exact DEC-285 source stack, and reads current EXP-061 workflow-run history without dispatching anything.

The frozen proof must remain run id `36319888985`, workflow run number 1, attempt 1. While no later historical attempt exists, DEC-286 reports `EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE`, freezes the future target identity as workflow run number 2 / attempt 1, and exposes `gh workflow run phase8a-exp061-discovery.yml --ref main` as plan evidence only.

If a later historical attempt exists, it must be exactly workflow run number 2 / attempt 1. The operator then reports `EXP061_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED`, marks the slot consumed through the DEC-281 classifier, and removes the command. Any run number 3+, rerun attempt, second historical attempt, proof-run-number drift, or main-head drift fails closed.

Operator source: `src/fmp/discovery/historical_execution_operator.py` blob `a711b14fb613f1c9952f5b2a6bf85d892bd2c4a5`. CLI: `scripts/phase8a_exp061_historical_execution_operator.py` blob `1f43e1218072918d2ebb33b2c312ba8e950881f9`. Focused tests: `tests/test_phase8a_exp061_historical_execution_operator.py` blob `42523ca36927e85a8c14566bf597d666a7ec1d20`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-historical-execution-operator.md`.

DEC-286 has no execute mode. Historical-result dispatch remains false. DEC-285 runtime execution/result authorization remains true only for the exact run #2 / attempt #1 identity. Retry, replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is a repository-hosted read-only proof of the exact DEC-286 slot-available execution plan on merged main. That proof may persist the future command and target run identity as immutable evidence, but must not dispatch EXP-061.


## DEC-287 — EXP-061 repository-hosted historical execution plan proof

**Date:** 2026-09-27
**Status:** SOURCE-ONLY READ-ONLY PROOF / NOT DISPATCHED

DEC-287 adds a repository-hosted read-only proof for the exact DEC-286 historical execution plan on merged `main`. It pins DEC-284 reviewed-plan source blob `14d9c559eaa33e5cb217baaf3ed2597091735b18`, DEC-285 authorization blob `30258e076f6a786c977fac8c588ac2b22aeed66e`, activated CLI blob `477aa9e8de4452e6444d1ee4361218aca445180d`, DEC-286 operator blob `a711b14fb613f1c9952f5b2a6bf85d892bd2c4a5`, DEC-286 CLI blob `1f43e1218072918d2ebb33b2c312ba8e950881f9`, the unchanged active discovery workflow, and the pinned runtime requirements.

The proof workflow is push-to-main only, read-only, and invokes only the DEC-286 `plan` command. A successful proof must show frozen proof run `36319888985` as workflow run #1, zero historical-result attempts, an unconsumed slot, target workflow run #2 / attempt #1, and the future `gh workflow run phase8a-exp061-discovery.yml --ref main` command as plan evidence only. Historical execution/result authorization remains true inside the DEC-285 target runtime, while dispatch and execute mode remain false.

Proof workflow: `.github/workflows/phase8a-exp061-historical-execution-plan.yml` blob `6f4b6a04291465f0f32f1f8e9276ff4a62417ec2`. Focused tests: `tests/test_phase8a_exp061_historical_execution_plan_proof.py` blob `95a4bb6dbcab6cef3fdec3cbac7bef09bb952311`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-historical-execution-plan-proof.md`.

DEC-287 cannot dispatch, execute, retry, rerun, replace, download historical discovery inputs, create cell/aggregate discovery-result artifacts, or claim a historical result. Reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain locked.

Only after the merged-main DEC-287 proof succeeds may its exact non-expired plan artifact be frozen by a later reviewed-proof decision. A one-shot historical executor may be considered only after that reviewed proof is merged.


## DEC-288 — EXP-061 reviewed historical execution plan proof

**Date:** 2026-09-27
**Status:** REVIEWED / RUN-2 SLOT VERIFIED AVAILABLE / DISPATCH STILL LOCKED

DEC-288 freezes the exact successful DEC-287 merged-main read-only execution-plan proof. DEC-287 merged at `958a0b830bb867d1c11e2a82be7fc301a6a75474`; proof run `36329787371` completed `success`, workflow run number 1, attempt 1, on that exact head. Every proof step passed, including exact-main/source binding, clean-worktree proof, live EXP-061 inventory fetch, DEC-286 plan execution, run-#2 target validation, and immutable artifact upload.

Exactly one execution-plan artifact exists: id `10935233025`, name `exp061-dec287-historical-execution-plan-958a0b830bb867d1c11e2a82be7fc301a6a75474`, digest `sha256:bb81bd8f0cb1adfc0054db4f5c16f13808793c520d443a0f05a89a90f92a415d`, non-expired. The downloaded ZIP independently matches that digest and contains exactly one `historical-execution-plan.json`. Raw plan SHA-256 is `2ca76921e17096b444202573a950825244e07c27e0f476cecfb510ad5e0a95e5`; canonical plan SHA-256 is `86b37433e183bfd9199822da0212b79fe11950461206335fc53e6f783210a74e`.

The frozen plan proves DEC-286/DEC-285 identity, exact fail-closed proof run `36319888985` as workflow run #1, zero historical-result attempts, an unconsumed slot, and the only future target as workflow run #2 / attempt #1. Historical execution/result production is authorized only inside that exact future runtime identity. The future `gh workflow run phase8a-exp061-discovery.yml --ref main` command remains evidence only; historical-result dispatch and execute mode remain false.

Reviewed execution-plan source: `src/fmp/discovery/historical_execution_plan_result_decision.py` blob `b01ee28b7ab636cb6729423504ff8e2038ce4375`. Focused tests: `tests/test_phase8a_exp061_reviewed_historical_execution_plan_proof.py` blob `54b24c60063032ccae3abe6cda897031edcf24e4`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-reviewed-historical-execution-plan-proof.md`.

DEC-288 keeps historical-result dispatch, execute mode, rerun, retry, replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading false. No historical-result slot is consumed.

The next safe gate is a separate one-shot historical executor source that binds DEC-288, rechecks the live inventory immediately before write, and can submit at most the sole run-#2 manual-main dispatch. The resulting historical run must be reviewed separately before any downstream gate opens.


## DEC-289 — EXP-061 one-shot historical executor

**Date:** 2026-09-27
**Status:** SOURCE-ONLY ONE-SHOT EXECUTOR / MERGE TRIGGERS SOLE HISTORICAL DISPATCH

DEC-289 adds the one-shot executor for the single historical-result attempt reviewed through DEC-288. Merging this decision to `main` activates a push-only workflow that may submit exactly one `phase8a-exp061-discovery.yml` manual-main dispatch if every predecessor, artifact, source, and live-inventory check still passes.

At runtime the executor re-downloads DEC-287 proof artifact `10935233025`, independently verifies its ZIP and plan SHA-256 identities, re-runs the DEC-288 reviewed-proof freeze against the current checkout, then builds two identical fresh DEC-286 live plans immediately before any write. Both plans must show exactly the frozen proof run `36319888985` as workflow run #1, zero historical-result attempts, an unconsumed slot, and target workflow run #2 / attempt #1.

The executor workflow requires itself to be workflow run #1 and the first and only DEC-289 main-push executor run, requires `GITHUB_RUN_ATTEMPT=1`, pins the exact DEC-288/285/286/active-workflow/CLI/runtime/executor source identities, and rechecks the discovery workflow inventory immediately before invoking the CLI. Any existing historical run blocks dispatch.

After submission, the workflow waits until exactly two matching EXP-061 manual-main runs exist and requires the sole non-proof run to be workflow run #2, attempt 1, at the DEC-289 merged-main head. The first later historical run consumes the slot immediately, regardless of terminal outcome. No executor rerun, historical rerun, retry, or replacement is authorized.

Executor core: `src/fmp/discovery/historical_executor.py` blob `82dbec289ed69e7333a90fd28ce430b024a99936`. CLI: `scripts/phase8a_exp061_historical_executor.py` blob `a899b71c1054e4ccd5639f4487dad038b2e1f55f`. Workflow: `.github/workflows/phase8a-exp061-historical-one-shot-execute.yml` blob `4efb80cf9eee3f7073de28531babc269d3c7a8cc`. Focused tests: `tests/test_phase8a_exp061_historical_executor.py` blob `62b40b4577462d32deb0b341a778cb87ba7d2cba`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-historical-one-shot-executor.md`.

DEC-289 authorizes only the one historical-result dispatch. Target historical discovery/result execution is allowed only under the existing DEC-285 run #2 / attempt #1 runtime gate. Reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker mutation, live orders, real-money action, and trading remain false.

After run #2 is submitted, no further historical dispatch is authorized. The next gate is terminal review of that exact run and its artifacts with no retry/replacement.


## DEC-290 — EXP-061 historical terminal review contract

**Date:** 2026-09-27
**Status:** SOURCE-ONLY PREDECLARED TERMINAL REVIEW / NO RESULT YET

DEC-290 predeclares how the sole EXP-061 historical workflow run #2 will be judged after it becomes terminal. The criteria are frozen before the result exists.

A reviewable run must be the exact `phase8a-exp061-discovery` manual-main workflow, workflow run number 2, attempt 1, at the caller-supplied DEC-289 merged-main head, terminal `completed`, and distinct from proof run `36319888985`.

Success is accepted only with the exact DEC-274 20-job / 20-artifact shape: preflight + all 18 expanded cells + aggregate, every job successful, every expected commit-scoped artifact present and non-expired, and no unexpanded matrix placeholder. Such a run is classified `EXP061_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED`; aggregate/cell contents still require separate review and candidate compilation remains locked.

Any terminal non-success is classified `EXP061_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED`. The slot is consumed permanently; only expected partial evidence may be preserved; rerun/retry/replacement remain false.

DEC-290 also predeclares the exact GitHub compatibility shape learned in DEC-280: one literal unexpanded skipped matrix job template is allowed only for a non-success run, only when skipped, and only when no expanded cell jobs coexist with it. A successful run can never use that shape.

Terminal-review source: `src/fmp/discovery/historical_result_review_contract.py` blob `2df4caa00aa683b8d627d061ae806178fbd5cd9c`. Focused tests: `tests/test_phase8a_exp061_historical_terminal_review_contract.py` blob `f6a166f425c2a00b17a2063e71e801f0bc64739d`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-historical-terminal-review-contract.md`.

DEC-290 opens no dispatch, rerun, retry, replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, or trading path.

The next gate is to require both DEC-289 and DEC-290 to pass CI before the one-shot historical dispatch is allowed to reach main.


## DEC-292 — EXP-061 historical failure freeze

**Date:** 2026-09-27
**Status:** TERMINAL FAILURE FROZEN / NO RETRY

The combined DEC-289/290 merge landed at `a7b3bc2d0b196da2631b64c19331efb3af12c98e`. One-shot executor run `36335739823` succeeded and submitted the sole EXP-061 historical attempt, workflow run `36335879839`, run number 2, attempt 1, at that exact head.

Run #2 is terminal `failure`. Preflight succeeded. All 18 discovery cell jobs failed at the frozen cell execution step. Aggregate was skipped. Exactly one run artifact persisted: preflight artifact `10937316246`, digest `sha256:e9a898df51317250944ad0a111d01d96d2081d708ea80872ed11b5cee48d356f`. No cell evidence and no aggregate evidence exist.

The DEC-289 executor evidence artifact is `10936194549`, digest `sha256:e7ffe1f08ce358eca210ef41397165196cb64bee31696a180c7fd02af8c68f1c`. Independently downloaded evidence matches that ZIP digest and binds the slot transition from zero/unconsumed to one submitted/consumed.

Representative EURUSD, GBPUSD, and USDJPY logs all fail inside `market_learning_adapter.adapt_feature_frame` while constructing `FeatureObservation`. Observed signatures include `EXP-061 continuous feature realized_vol_1h must be finite or null` and `EXP-061 continuous feature realized_vol_8h must be finite or null`.

The Phase-5 feature dictionary explicitly defines warm-up, missing cadence, incomplete required bars, non-finite required values, and invalid denominators as null. DEC-272's adapter instead passed raw Polars row values through unchanged, allowing IEEE NaN to reach the stricter observation validator. DEC-292 classifies the failure as `NONFINITE_FEATURE_WARMUP_NOT_NORMALIZED`.

This is an implementation/input-normalization failure, not a negative market-pattern result. EXP-061 produced no valid discovery cell evidence and no candidate evidence. Its sole historical slot is consumed permanently; rerun, retry, and replacement are all false.

Failure-freeze source: `src/fmp/discovery/historical_failure_result_decision.py` blob `676116f34693f9a5a8f8403aaa93f28ac1c5bb46`. Focused tests: `tests/test_phase8a_exp061_historical_failure_freeze.py` blob `f8f89536886a9ea9d80cebf755691bcba853117e`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp061-historical-failure-freeze.md`.

The next research identity must be new. EXP-062 may preserve DEC-270 discovery semantics and the same historical source range while narrowly repairing the adapter's non-finite continuous-feature missing-value normalization. Reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain locked.


## DEC-293 — EXP-062 non-finite feature normalization repair

**Date:** 2026-09-27
**Status:** SOURCE-ONLY IMPLEMENTATION REPAIR / HISTORICAL EXECUTION LOCKED

DEC-293 opens EXP-20260927-062 as a new experiment identity solely to repair the implementation defect frozen by DEC-292. EXP-061 is closed and is not retried. The frozen EXP-061 adapter remains unchanged at blob `978a33554fad7e9d78b002778c4896be0af3333a`; EXP-062 uses a separate repair module.

The research semantics remain the DEC-270 discovery-first protocol: same three pairs, three timeframes, 60m/240m horizons, 2015-2017 discovery, 2018 confirmation, 2019-2022 validation, same state vocabulary/search bounds/economic gates, and the same closed 2023-2026 robustness block.

The repair is limited to the feature-adapter representation boundary. For continuous feature values, existing null stays null, finite numeric values remain unchanged, and numeric NaN/+inf/-inf become `None`. Boolean and non-numeric values are not coerced. Session flags remain strict booleans. Outcome values remain unchanged and finite-only. No forward fill, backfill, clipping, zero-fill, or imputation is introduced.

This matches the frozen Phase-5 feature dictionary, which defines warm-up, missing cadence, incomplete required bars, non-finite required values, and invalid denominators as null feature values.

Repaired adapter: `src/fmp/discovery/exp062_nonfinite_feature_adapter.py` blob `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`. Focused EXP-062 tests: `tests/test_phase8a_exp062_nonfinite_feature_normalization.py` blob `b9acdf3cda666ae9dae84e80cf3381471cccf358`. DEC-292 failure freeze remains bound at blob `676116f34693f9a5a8f8403aaa93f28ac1c5bb46`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp062-nonfinite-feature-normalization-repair.md`.

DEC-293 authorizes no historical slot or dispatch. Before EXP-062 can execute, a later gate must prove the repaired adapter against the exact accepted EXP-044 historical source artifacts. Reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain locked.


## DEC-294 — EXP-062 real-data adapter proof

**Date:** 2026-09-27
**Status:** SOURCE-ONLY READ-ONLY REAL-DATA PROOF / NO DISCOVERY RESULT

DEC-294 adds a repository-hosted proof of the isolated DEC-293 repair against the exact accepted EXP-044 historical feature/outcome artifacts before any EXP-062 historical discovery slot may open.

The proof runs exactly nine pair/timeframe adapter probes (EURUSD/GBPUSD/USDJPY × 5m/15m/1h). Each probe reuses DEC-273 to verify and load exactly 96 feature months and 96 outcome months from 2015-01 through 2022-12, counts raw numeric non-finite values across the 20 continuous feature columns, and executes the EXP-062 adapter. Feature/outcome row counts must exactly match adapted observation counts.

The frozen EXP-061 adapter remains unchanged at blob `978a33554fad7e9d78b002778c4896be0af3333a`. The isolated EXP-062 repair is `src/fmp/discovery/exp062_nonfinite_feature_adapter.py` blob `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`.

The aggregate requires exactly nine unique probes and requires total raw non-finite count > 0 so the merged-main proof must actually exercise the repaired condition on real accepted data.

DEC-294 does not call the pattern miner, the EXP-061 cell command, or any workflow dispatch. It cannot produce discovery/confirmation/validation evidence or a candidate.

Probe source: `src/fmp/discovery/exp062_adapter_probe.py` blob `96eac8ed71f6691f7aff6dad12288e3448688c83`. CLI: `scripts/phase8a_exp062_adapter_probe.py` blob `40e0c90c41fd53cb8ce42416af8c7c5f2b60d138`. Workflow: `.github/workflows/phase8a-exp062-adapter-proof.yml` blob `4fbeb7836ef775b14918b49ed24da8c86928610c`. Focused tests: `tests/test_phase8a_exp062_adapter_probe.py` blob `a471c827040750d7b3c6b4697d1d08e54363a3d9`; workflow tests blob `b80390f24c2d7632fa133c8c5e740dfa28aeafc2`.

Historical discovery execution/result production, reserved robustness, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain false. The next gate is the merged-main DEC-294 proof result and its immutable artifact review.


## DEC-295 — EXP-062 adapter proof review contract

**Date:** 2026-09-27
**Status:** SOURCE-ONLY PREDECLARED REVIEW / NO PROOF RESULT YET

DEC-295 predeclares the terminal review for DEC-294 before its merged-main proof runs. Success requires exact push-main attempt-1 identity, all nine named pair/timeframe probe jobs plus aggregate (10 jobs total) successful, and exactly nine cell probe artifacts plus one aggregate proof artifact (10 total), all non-expired and commit-scoped.

Unexpected jobs/artifacts fail closed. A non-success proof cannot authorize discovery execution.

Review source: `src/fmp/discovery/exp062_adapter_proof_review.py` blob `d3f1283cffae4e7aa6c6a9bd2b8403743cc3709d`; tests: `tests/test_phase8a_exp062_adapter_proof_review.py` blob `3ce8157054e04ef88b47624404c31b9a187fe6fa`. Bound DEC-294 workflow blob: `4fbeb7836ef775b14918b49ed24da8c86928610c`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp062-adapter-proof-review-contract.md`.

Historical discovery/result execution, reserved data, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading remain locked.


## DEC-296 — EXP-062 adapter proof content review

**Date:** 2026-09-27
**Status:** SOURCE-ONLY PREDECLARED CONTENT REVIEW / NO PROOF RESULT YET

DEC-296 defines JSON-content review for a complete successful DEC-294 proof. It requires DEC-295's exact success-complete terminal classification, exactly nine validated cell probe objects at the proof head, and deterministic equality between the persisted aggregate proof and a fresh recompilation from those nine cells.

A verified content review must still show all nine probes successful and total real raw non-finite values > 0. DEC-296 also reconciles per-feature and per-cell raw non-finite counts for diagnostics.

A successful review is classified `EXP062_ADAPTER_REPAIR_REAL_DATA_PROOF_VERIFIED` with meaning `NONFINITE_MISSING_VALUES_NORMALIZED_WITHOUT_MINING`. It is proof of the adapter repair only; it is not a market-pattern or strategy result.

Review source: `src/fmp/discovery/exp062_adapter_proof_content_review.py` blob `26529be12229953070f5dbf929699e7e86a2a9bb`. Focused tests: `tests/test_phase8a_exp062_adapter_proof_content_review.py` blob `0fa4c87457c49500268f577f35ee9b27729f742b`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp062-adapter-proof-content-review.md`.

Historical discovery/result execution, reserved data, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading remain locked.


## DEC-297 — EXP-062 adapter proof result freeze

**Date:** 2026-09-27
**Status:** VERIFIED REAL-DATA REPAIR PROOF / HISTORICAL DISCOVERY STILL LOCKED

DEC-297 freezes the successful clean DEC-294 merged-main real-data adapter proof. Proof run `36348366166` completed `success`, workflow run #1 / attempt 1, at head `5e235938dc7e8eb467f59ca85ae4b6e1d5179475`.

The run has the exact DEC-295 success shape: nine pair/timeframe adapter probes plus aggregate, all 10 jobs successful, with exactly 10 non-expired commit-scoped artifacts. DEC-296 deterministic content review verifies the downloaded nine cell probes exactly equal the aggregate cells and that the aggregate recompiles from those cells without drift.

Verified real-data totals are 3,576,519 feature rows, 7,152,783 outcome rows, and 6,763 raw numeric non-finite continuous-feature values normalized by the isolated EXP-062 adapter: `realized_vol_1h=2683`, `realized_vol_8h=4070`, `realized_vol_24h=10`, all other continuous features zero. All nine cells preserve exact feature/outcome adaptation row parity.

Aggregate artifact `10941770676` has digest `sha256:ce22fba00e711ba91f29c797dba19814aea9b9c907df66e8bfd75aefdcc08e5b` and raw `adapter-proof.json` SHA-256 `8f11806a4d2ffc4fb00a62360b35fc132efbb7f4e1ab44ea03a2244003dec056`. DEC-297 binds all nine cell artifact ids/digests/raw JSON hashes as well.

Result-freeze source: `src/fmp/discovery/exp062_adapter_proof_result_decision.py` blob `18b7dde7eadf0f051a09fda04e648650bb270eb7`. Focused tests: `tests/test_phase8a_exp062_adapter_proof_result_freeze.py` blob `90a9104dd0069c9c010b3517d2baa27336ff86bd`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp062-adapter-proof-result-freeze.md`.

Verified meaning is `NONFINITE_MISSING_VALUES_NORMALIZED_WITHOUT_MINING`. This is not a market-pattern, candidate, or strategy result.

Historical discovery execution/result production, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading remain locked. A later decision may design a new EXP-062 historical slot only after DEC-295/296/297 are green and merged.


## DEC-298 — EXP-062 run and evidence contract

**Date:** 2026-09-27
**Status:** SOURCE-ONLY / NON-EXECUTING

DEC-298 freezes the exact future EXP-062 result/evidence contract after DEC-297 verified the non-finite-value repair on accepted real data.

The contract preserves the DEC-270 research semantics and the exact 18-cell universe while giving EXP-062 distinct job, artifact, cell-evidence, aggregate-evidence, and protocol identities. It reserves the future workflow identity `phase8a-exp062-discovery` but does not create, install, or dispatch that workflow.

EXP-062 cell evidence wraps the exact frozen EXP-061 cell evidence, stores the predecessor fingerprint and repair/proof identities, and marks `nonfinite_to_null_repair_applied=true`. Validation reverses the wrapper, reconstructs the exact predecessor fingerprint, and reruns the frozen EXP-061 validator. Aggregate evidence performs the same reversible wrapping over the frozen EXP-061 aggregate and stores all 18 outer EXP-062 cell fingerprints.

The exact future success inventory remains 18 cells, 20 jobs, and 20 artifacts. Rerun/retry/replacement remain false if a later slot is authorized.

Run/evidence contract: `src/fmp/discovery/exp062_run_contract.py` blob `d304c8fafcff64f967f6777b1c494819f69d4a03`. Focused tests: `tests/test_phase8a_exp062_run_evidence_contract.py` blob `f951f67f438b61b78d7b1b8327d1946f1dc413a1`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp062-run-evidence-contract.md`.

DEC-298 authorizes no workflow source, dispatch, historical discovery execution, result production, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo/live, real-money, or trading.

The next safe gate is dormant EXP-062 workflow/CLI source using the verified repaired adapter, frozen miner/loader semantics, and DEC-298 evidence wrappers, with a hard execution gate before any historical artifact read.


## DEC-299 — EXP-062 dormant workflow / CLI source freeze

**Date:** 2026-09-27
**Status:** DORMANT SOURCE FROZEN / NOT INSTALLED / HISTORICAL EXECUTION LOCKED

DEC-299 freezes the future EXP-062 discovery workflow/CLI source after the repaired adapter was verified on accepted real data and DEC-298 froze distinct EXP-062 evidence identities.

The future cell path is DEC-273 verified loader -> DEC-293 repaired adapter -> frozen DEC-271 miner -> DEC-298 EXP-062 cell evidence. Aggregate compilation uses DEC-298 wrappers over the exact frozen EXP-061 aggregate semantics.

The dormant workflow remains outside `.github/workflows` at `docs/superpowers/templates/phase8a-exp062-discovery.yml.disabled`; the reserved active path `.github/workflows/phase8a-exp062-discovery.yml` remains absent. The CLI execution gate is called before any historical feature/outcome/evidence read and always raises under DEC-299.

Source contract: `src/fmp/discovery/exp062_workflow_source.py` blob `e20ded13de24f99e8ea6cfdc6cb0d1309d984f24`. CLI: `scripts/phase8a_exp062.py` blob `e6a94c1733f952a8edc01584a198ead1816f4410`. Dormant template: `docs/superpowers/templates/phase8a-exp062-discovery.yml.disabled` blob `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`. Focused tests: `tests/test_phase8a_exp062_dormant_workflow_source.py` blob `15c054c305b57e6da7f73c24bdaab02235fa4a26`.

Workflow installation/dispatch, historical discovery/result execution, rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is exact active-workflow installation with the execution gate still false, followed by a merged-main fail-closed proof before any historical-result slot is opened.


## DEC-300 — EXP-062 locked active workflow installation

**Date:** 2026-09-27
**Status:** ACTIVE WORKFLOW INSTALLED / PROOF + HISTORICAL DISPATCH LOCKED

DEC-300 installs the exact DEC-299 dormant template at `.github/workflows/phase8a-exp062-discovery.yml` without changing a byte. Dormant and active workflow blobs are both `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`.

The workflow remains manual-only and retains the DEC-299 execution gate before any historical cell source use or aggregate evidence read. Workflow dispatch, proof dispatch, historical-result dispatch, historical discovery execution, and discovery-result production all remain false.

Installation source: `src/fmp/discovery/exp062_workflow_install.py` blob `febb2bc00342364c67a75c69439136079eba0a2c`. Focused tests: `tests/test_phase8a_exp062_locked_workflow_install.py` blob `fbf18f73d4a660dbd4d33bdfb95dc6c8f416ec0a`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp062-locked-workflow-installation.md`.

Rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain locked.

The next safe gate is a proof-only terminal contract and read-only proof operator that can demonstrate the merged workflow fails closed before any discovery cell executes. Proof dispatch must remain separate from historical-result dispatch.


## DEC-301 — EXP-062 gate-proof terminal contract

**Date:** 2026-09-27
**Status:** SOURCE-ONLY PREDECLARED PROOF REVIEW / NO PROOF DISPATCH

DEC-301 predeclares the first EXP-062 proof-only manual-main run before it exists. The proof must be workflow run #1 / attempt 1, fail after source-ready preflight at the still-locked DEC-299 execution gate, materialize no successful downstream work, and persist exactly one preflight artifact with zero cell/aggregate artifacts.

The contract explicitly accepts GitHub's known skipped literal matrix-template representation on early failure, but only when skipped and never alongside expanded cell jobs. The proof consumes no historical-result slot.

Proof-contract source: `src/fmp/discovery/exp062_proof_contract.py` blob `dcc513d1918e95e2bc0bc02a04774291c6b340c0`. Focused tests: `tests/test_phase8a_exp062_gate_proof_contract.py` blob `7022c0a821144c63daf2a74c4aca6871c384dd27`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp062-gate-proof-contract.md`.

Proof dispatch, historical-result dispatch/execution, rerun/retry/replacement, reserved data, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading remain false.

The next safe gate is a read-only exact-main proof planner with no execute mode.


## DEC-302 — EXP-062 read-only gate-proof operator

**Date:** 2026-09-27
**Status:** SOURCE-ONLY READ-ONLY PLANNER / NO EXECUTE MODE

DEC-302 adds the exact-main read-only planner for the DEC-301 proof-only EXP-062 gate run. With zero matching manual-main runs it reports `EXP062_PROOF_DISPATCH_AUTHORIZATION_REQUIRED` and exposes `gh workflow run phase8a-exp062-discovery.yml --ref main` as plan evidence only. Once any matching run exists, the command is removed and review is required.

The first matching run must remain workflow run #1 / attempt 1. Multiple matching runs, duplicate ids, run-number/attempt drift, or main-head drift fail closed.

Operator: `src/fmp/discovery/exp062_proof_operator.py` blob `bc33c377ee9865766613a3ad64ddd9fd751d88fa`. CLI: `scripts/phase8a_exp062_proof_operator.py` blob `1b3525d8424a83bd02f46439eeab19956686b1c9`. Tests: `tests/test_phase8a_exp062_proof_operator.py` blob `f3e1f1acc4263a534e679d254ae0b23d95365737`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp062-readonly-proof-operator.md`.

Proof dispatch, proof execute mode, historical-result dispatch/execution, rerun/retry/replacement, reserved data, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading remain false.

The next safe gate is a separately reviewed one-shot proof executor that can submit only a fresh DEC-302 proof command and still cannot authorize historical discovery.


## DEC-303 — EXP-062 one-shot gate-proof executor

**Date:** 2026-09-27
**Status:** SOURCE-ONLY PROOF EXECUTOR / HISTORICAL RESULT STILL LOCKED

DEC-303 adds the sole one-shot executor for the proof-only EXP-062 gate run. It requires executor workflow run #1 / attempt 1, zero existing EXP-062 manual-main runs, two identical fresh DEC-302 plans at exact merged main, and may submit only `gh workflow run phase8a-exp062-discovery.yml --ref main`.

The submitted proof must become workflow run #1 / attempt 1 on the executor head. Proof submission consumes no historical-result slot and claims no historical result.

Executor source: `src/fmp/discovery/exp062_proof_executor.py` blob `b5963636901b5caba1730f8a969dd3f9a1bf1979`. CLI: `scripts/phase8a_exp062_proof_executor.py` blob `1ff34425b4240312324ae2513fa6d747c0579982`. Workflow: `.github/workflows/phase8a-exp062-proof-one-shot-execute.yml` blob `45cfc626f82b4a05ed619d9eeffdb6bd2fa0e04a`. Tests: `tests/test_phase8a_exp062_proof_executor.py` blob `022fe0ce6fb0f34bbeb1f2fd61ce24e9c4b503d5`.

Historical-result dispatch/execution, rerun/retry/replacement, reserved data, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading remain false.

The next gate after the proof is submitted is DEC-301 terminal review and immutable proof-result freeze before any historical-result slot can open.


## DEC-304 — EXP-062 gate-proof result review

**Date:** 2026-09-27
**Status:** SOURCE-ONLY READ-ONLY REVIEW / HISTORICAL SLOT STILL CLOSED

DEC-304 adds the read-only result reviewer for the DEC-301/303 fail-closed EXP-062 gate proof. It requires the proof terminal to validate through DEC-301 and the matching dispatch evidence to validate as DEC-303 at the same exact head.

A valid review records workflow run #1 / attempt 1, failure at the locked execution gate, one preflight artifact, zero cell/aggregate result artifacts, and no historical discovery execution. It also requires DEC-303 to prove that two identical zero-run DEC-302 plans preceded the one proof submission and that the submission did not consume or claim a historical-result slot.

Reviewer: `src/fmp/discovery/exp062_proof_result_review.py` blob `58ad68ba68e480d9af222c378dbdc1a32e2835c5`. Focused tests: `tests/test_phase8a_exp062_proof_result_review.py` blob `7a8108a4a6c506925e6a2c3f3f68e1e730210407`. Detailed spec: `docs/superpowers/specs/2026-09-27-phase8a-exp062-proof-result-review.md`.

DEC-304 opens no historical slot and keeps historical-result dispatch/execution, rerun/retry/replacement, reserved data, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading false.

The next safe gate after a real proof is an immutable proof-result freeze binding the exact proof run, preflight artifact, executor artifact, raw evidence hashes, and DEC-304 reviewed result before any historical-result slot is considered.

## DEC-305 — EXP-062 reviewed gate-proof freeze boundary

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY / RUNTIME PROOF EVIDENCE REQUIRED

DEC-305 adds a deterministic, fingerprinted freeze record for an EXP-062 proof result
only after DEC-304 has validated the actual terminal proof evidence. The freeze
revalidates the DEC-301/303 identities, exact proof head, run/artifact/job accounting,
zero historical result artifacts, and every authority-negative field.

DEC-305 does not hard-code or invent proof run IDs before GitHub produces them. It does
not open the historical-result slot. Historical-result dispatch/execution, reserved
2023-2026 access, candidate compilation/promotion, Phase 8B, demo, broker/live,
real-money, and trading remain false.

The next gate after a real DEC-305 freeze is a separate source-only historical-run
authorization contract.


## DEC-306 — EXP-062 concrete runtime gate-proof freeze

**Date:** 2026-09-28  
**Status:** REVIEWED RUNTIME EVIDENCE FROZEN / HISTORICAL SLOT STILL CLOSED

DEC-306 binds the actual DEC-303 executor run `36358278933` and actual EXP-062
gate-proof run `36358289723`, both on
`f2c55ac36a1a9ba7596ec0d4559c877a66cda0fb`. The executor completed run #1 /
attempt 1 successfully and persisted dispatch-evidence artifact `10944404609`
with digest
`sha256:f1baf1e77100cb314b1e573a404508d379a569ffadea2f702bfdaebfad2c3f64`.

The proof completed run #1 / attempt 1 with the expected terminal failure at the
still-locked historical execution gate. Preflight job `108730271344` failed,
the matrix placeholder job `108730343578` and aggregate job `108730343797`
were skipped, and the only proof artifact is preflight artifact `10943489995`
with digest
`sha256:0cc405cc6d8b5941f7051e7907e2a7040a21a05411b29774ebbcd3884da9193f`.
No cell or aggregate result artifact exists.

DEC-306 additionally freezes raw and canonical SHA-256 identities for
`executor.json`, `proof-run.json`, `proof-runs.json`, and `preflight.json`,
plus the exact DEC-305 freeze fingerprint
`fadd6e512b95179fa682d05c8550c914db81e559d9c0ad8da0bedb03bb43a096`.
This closes the runtime-evidence binding gap left intentionally by generic DEC-305.

PR #448 later materialized executor run `36360111479` as run #2 / attempt 1. It
failed closed at the executor first-run guard before proof dispatch and created no
second EXP-062 proof. It is non-authoritative and consumes no historical slot.

Historical-result slot opening/dispatch/execution, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

The next safe gate is a separate source-only one-slot historical-run authorization
contract for the unchanged 2015-2022 research window.


## DEC-307 — EXP-062 historical-run source authorization

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY ONE-SLOT AUTHORIZATION / DISPATCH + EXECUTION STILL LOCKED

DEC-307 opens only the outer source-governance slot for at most one bounded EXP-062
historical discovery-result attempt. It binds the exact DEC-306 runtime proof freeze
and the unchanged DEC-293/298/299/300/301/304/305 research, workflow, and proof
sources.

The frozen proof run `36358289723`, run #1 / attempt 1, is excluded from historical
slot consumption. With that proof as the only matching manual-main EXP-062 discovery
run, the slot is available. The first later matching run must be workflow run #2 /
attempt 1 and consumes the slot immediately regardless of queued/running/terminal
state or terminal outcome. Multiple later runs, reruns, or run-number drift fail closed.

DEC-307 sets only `historical_result_slot_source_authorized=true`. Historical-result
dispatch, historical discovery execution, discovery-result production, rerun/retry/
replacement, reserved 2023-2026 access, candidate compilation/promotion, Phase 8B,
demo, broker/live, real-money, and trading remain false.

The future historical attempt remains restricted to 2015-2022 data; the 2023-01-01
through 2026-08-21 robustness block stays closed.

The next safe gate is a clean-main read-only operator for the single source-authorized
historical slot. DEC-307 itself provides no dispatch or execute mode.


## DEC-308 — EXP-062 read-only historical-slot operator

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY READ-ONLY OPERATOR / NO EXECUTE MODE

DEC-308 adds the read-only exact-main operator for the single DEC-307
source-authorized EXP-062 historical-result slot. It requires current `main` metadata,
the current EXP-062 discovery workflow-run inventory, and an exact caller-supplied
expected main head.

While the DEC-306 frozen proof is the only matching manual-main run, the operator
reports `EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE` and exposes
`gh workflow run phase8a-exp062-discovery.yml --ref main` as plan evidence only.
Historical-result dispatch remains false and execute mode does not exist.

Once run #2 exists, the operator reports
`EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED`, marks the slot consumed,
removes the command, and cannot plan a second run.

Historical execution/result production, rerun/retry/replacement, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

The next safe gate is a repository-hosted read-only merged-main proof of the exact
DEC-308 slot-available plan. That proof must not dispatch the historical workflow.


## DEC-309 — EXP-062 repository-hosted historical plan proof

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY READ-ONLY PROOF WORKFLOW / NO HISTORICAL DISPATCH

DEC-309 adds a push-to-main proof workflow for DEC-308. The workflow is first-run /
attempt-1 only, requires exact merged-main identity and frozen DEC-306/307/308 source
blobs, fetches current main plus the EXP-062 manual-main discovery inventory, and runs
only the DEC-308 read-only planner.

A successful proof must show the frozen gate proof as the sole matching run, zero
historical-result attempts, an available/unconsumed slot, and the exact future command
`gh workflow run phase8a-exp062-discovery.yml --ref main` as JSON plan evidence.
The workflow never executes that command.

DEC-309 uploads only `historical-plan.json` as
`exp062-dec309-historical-plan-<merged-main-sha>`. It has read-only contents/actions
permissions and creates no discovery cell or aggregate result artifact.

Historical dispatch/execution/result production, rerun/retry/replacement, reserved
2023-2026 access, candidate compilation/promotion, Phase 8B, demo, broker/live,
real-money, and trading remain false.

The next gate after a real successful merged-main DEC-309 run is an immutable
review/freeze of that exact proof run, artifact digest, and raw/canonical plan hashes.



## DEC-310 — EXP-062 historical-plan proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PLAN PROOF REQUIRED

DEC-310 adds a generic reviewer for a future successful DEC-309 read-only historical
plan proof. It requires the exact DEC-309 workflow, run #1 / attempt 1 on merged main,
one successful plan job, one non-expired plan artifact, and the downloaded plan bytes.

The reviewer revalidates the DEC-308 slot-available plan, binds raw and canonical
SHA-256 plan hashes, and pins DEC-306/307/308/309 source identities. It cannot dispatch
or execute the historical workflow. Reserved 2023-2026 data, candidate compilation,
Phase 8B, demo/live, real-money, and trading remain locked.

The next safe gate after actual DEC-309 evidence passes DEC-310 is an immutable concrete
historical-plan proof freeze before execution authorization is considered.

## DEC-311 — EXP-062 concrete historical-plan proof freeze

**Date:** 2026-09-28  
**Status:** REVIEWED PLAN EVIDENCE FROZEN / HISTORICAL EXECUTION STILL LOCKED

DEC-311 binds the actual successful DEC-309 read-only historical-plan proof to exact
runtime evidence. The proof is run `36403342301`, run #1 / attempt 1, on merged head
`95c193343a905acd40daf0eea5d27d55fd2537e1`; its sole successful job is
`108866149073`, and its sole artifact is `10960559187` with digest
`sha256:07679d85ea3ee0a9373bbd78363ab98eb973377ace6d68828528f91188ff3cf8`.

The independently downloaded artifact ZIP matches that SHA-256 exactly. Its sole
`historical-plan.json` has raw SHA-256
`ac34769d589dbcc18a056d1ebaf960b6881f943f221d771e80216df32d313672`
and canonical SHA-256
`d6cd04c0c29a2e82da12e687ce56ae80387f7ad3c9727b23018ee548684e62a6`.

DEC-311 re-runs DEC-310 against the raw evidence, pins the DEC-310 reviewer blob
`5c8870c10e86122342bb181cb5a15ebc709924ce`, and emits a deterministic freeze
fingerprint. The plan proves zero historical-result attempts and an unconsumed
source-authorized slot.

Historical-result dispatch, execute mode, historical execution/result production,
rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading all remain false.

The next safe gate is a separate source-only historical execution authorization
contract. It may define the exact future run #2 / attempt 1 execution identity but
must provide no dispatch path.

## DEC-312 — EXP-062 historical execution authorization

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY ONE-SHOT RUNTIME AUTHORIZATION / DISPATCH STILL LOCKED

DEC-312 binds the concrete DEC-311 historical-plan proof freeze and activates the
EXP-062 CLI execution gate only for the single future historical workflow run #2 /
attempt 1. The exact runtime must be GitHub Actions in `Dtwosam/FMP`, workflow
`phase8a-exp062-discovery`, `workflow_dispatch` on `refs/heads/main`, with
`GITHUB_SHA` equal to the CLI code commit and a distinct positive run id.

Historical discovery execution and discovery-result production are authorized only
inside that exact runtime identity. Historical-result dispatch remains false, so
DEC-312 cannot start the run itself.

The historical range remains 2015-2022. Rerun/retry/replacement, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

The next safe gate is a separate read-only exact-main historical execution operator
with no execute mode.

## DEC-313 — EXP-062 read-only historical execution operator

**Date:** 2026-09-28  
**Status:** READ-ONLY EXECUTION PLAN / NO EXECUTE MODE

DEC-313 adds an exact-main planner for the one DEC-312 historical runtime slot. While
the frozen proof remains the only matching EXP-062 manual-main discovery run, the
operator exposes `gh workflow run phase8a-exp062-discovery.yml --ref main` as plan
evidence for target workflow run #2 / attempt 1.

The operator cannot execute the command and historical-result dispatch remains false.
Once run #2 exists, the command is removed and the slot is treated as consumed.
Multiple attempts, reruns, proof/run-number drift, duplicate run ids, or main-head
drift fail closed.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

The next safe gate is a repository-hosted read-only proof of the exact DEC-313
execution plan on merged main.

## DEC-314 — EXP-062 repository-hosted historical execution-plan proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN PROOF / NO HISTORICAL DISPATCH

DEC-314 adds a push-to-main, first-run/attempt-1 proof workflow for the exact DEC-313
execution plan. It pins DEC-311/312/313 source identities, fetches current main and the
EXP-062 manual-main discovery inventory, and invokes only the read-only planner.

A valid proof must show the frozen gate proof remains run #1, zero historical-result
attempts, target run #2 / attempt 1, and the exact future discovery command as plan
evidence only. The workflow has contents/actions read permissions and never executes
that command.

Historical-result dispatch remains false. Reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading remain
locked.

The next safe gate after a real successful proof is an immutable review/freeze of that
exact runtime evidence.

## DEC-315 — EXP-062 historical execution-plan proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED

DEC-315 adds a source-only reviewer for future DEC-314 runtime evidence. It requires
the exact read-only proof workflow on merged main, run #1 / attempt 1 success, one
successful plan job, one non-expired plan artifact, and downloaded plan bytes.

The reviewer revalidates the DEC-313 execution plan, requires zero historical-result
attempts and target run #2 / attempt 1, and records raw/canonical plan SHA-256 hashes.
It pins DEC-311/312/313/314 source identities.

Historical-result dispatch and execute mode remain false. Reserved 2023-2026 access,
candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading
remain locked.

The next gate after real DEC-314 evidence passes review is an immutable concrete
execution-plan proof freeze.

## DEC-316 — EXP-062 reviewed historical execution-plan freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO HISTORICAL DISPATCH

DEC-316 adds a deterministic freeze builder for an already-valid DEC-315 review. It
requires the exact DEC-315 stage, proof/run/job/artifact identities, artifact digest,
raw/canonical plan hashes, target run #2 / attempt 1, and exact DEC-311/312/313/314
source-blob map.

DEC-316 does not invent runtime evidence. Before a real DEC-314 proof exists, the
builder has no concrete evidence to freeze.

Historical-result dispatch and execute mode remain false. Rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

The next safe gate after actual DEC-314 evidence is a concrete runtime-evidence binding
before any one-shot dispatcher is considered.

## DEC-317 — EXP-062 historical execution-plan runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / HISTORICAL DISPATCH STILL LOCKED

DEC-317 binds the actual successful DEC-314 proof on merged head
`ea69e82c9f653facba8ed6589fe4243848187ad3`: run `36414282818`, job
`108901556593`, artifact `10966632240`, artifact/ZIP SHA-256
`9299ebfd344c0bd2a66ccd6e29339e035840c8b4204cbfc16bb6d3e938a53254`,
raw plan SHA-256 `594b5bd129a93ad7b07f69e00826251dd693f1bb388e6b4dff64eda0b34a7c72`,
and canonical plan SHA-256
`152bbb90efe3941f1338c73cf24f91f10a877cda3ee5c46f08c4f556d653a12f`.

The source re-runs DEC-315 review and DEC-316 freezing and requires the exact DEC-316
fingerprint `7c7d99f4c89aac4e11d27536b9f8d2d39322672a9a0332f141d1d86f93b19be3`.

The slot remains empty and target run #2 / attempt 1 remains the only future
historical runtime. Historical-result dispatch, execute mode, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain locked.

The next safe gate is a source-only one-shot historical dispatch authorization
contract. It must still provide no dispatch path itself.

## DEC-318 — EXP-062 one-shot historical dispatch source authorization

**Date:** 2026-09-28  
**Status:** SOURCE CONTRACT AUTHORIZED / DISPATCH + EXECUTOR STILL LOCKED

DEC-318 pins the concrete DEC-317 runtime-evidence freeze and authorizes only a source
contract for one future historical dispatch. The predecessor still proves zero
historical-result attempts, an unconsumed slot, and target run #2 / attempt 1.

`one_shot_dispatch_source_authorized=true`, but
`historical_result_dispatch_authorized=false` and
`historical_executor_available=false`.

Historical discovery/result production remain authorized only inside the exact
DEC-312 target runtime. Rerun/retry/replacement, reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading remain
false.

The next safe gate is a read-only current-main dispatch operator with no execute mode.

## DEC-319 — EXP-062 read-only current-main dispatch operator

**Date:** 2026-09-28  
**Status:** READ-ONLY PLAN / NO EXECUTE MODE

DEC-319 adds a current-main planner for the DEC-318 one-shot dispatch source contract.
It pins DEC-318, rechecks the EXP-062 discovery inventory, and exposes
`gh workflow run phase8a-exp062-discovery.yml --ref main` only as plan evidence
while the historical-result slot remains empty.

Actual historical-result dispatch remains false, executor availability remains false,
and the CLI has no execute/advance mode. If run #2 exists, the command is removed and
the slot is treated as consumed.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

The next safe gate is a repository-hosted read-only dispatch-plan proof.

## DEC-320 — EXP-062 repository-hosted dispatch-plan proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN PROOF / NO HISTORICAL DISPATCH

DEC-320 adds a first-run/attempt-1 push-to-main proof of DEC-319. The workflow pins
DEC-317/318/319 source identities, fetches current main and the EXP-062 discovery
inventory through read-only API calls, and invokes only the plan-only dispatch
operator.

A valid proof requires an empty historical slot, target run #2 / attempt 1, the exact
future discovery command as JSON evidence, and all actual dispatch/executor/downstream
authority fields false.

The workflow has only `contents: read` and `actions: read` permissions and uploads
only `historical-dispatch-plan.json`.

The next safe gate is a concrete review/freeze of the real DEC-320 runtime evidence.

## DEC-321 — EXP-062 historical dispatch-plan proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED

DEC-321 adds a source-only reviewer for future DEC-320 evidence. It requires exact
run #1 / attempt 1 success, one successful read-only plan job, one non-expired artifact,
and exact DEC-319 plan semantics.

The reviewer records raw/canonical plan hashes while preserving zero historical-result
attempts and target run #2 / attempt 1. Actual dispatch, executor availability, and
execute mode remain false.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

The next safe gate after actual DEC-320 proof is an immutable concrete dispatch-plan
proof freeze.

## DEC-322 — EXP-062 reviewed historical dispatch-plan freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO HISTORICAL DISPATCH

DEC-322 adds a deterministic freeze builder for a valid DEC-321 review. It preserves
the real proof run/job/artifact identities, artifact digest, plan hashes, target run
#2 / attempt 1, and exact DEC-317/318/319/320 source map.

DEC-322 cannot invent runtime evidence. Actual historical-result dispatch, executor
availability, and execute mode remain false. Reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading remain
locked.

The next safe gate after real DEC-320 proof is concrete runtime-evidence binding before
any one-shot executor.

## DEC-323 — EXP-062 historical dispatch-plan runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / DISPATCH + EXECUTOR STILL LOCKED

DEC-323 binds the actual successful DEC-320 proof on merged head
`fee1a78168254e7e8fecc104859d1a231b727243`: run `36418793172`, job
`108916232597`, artifact `10967344018`, artifact/ZIP SHA-256
`ca0f1156fab234327bbcdd9c3150cb7904ed6def230f035019b2139c4c523adf`,
raw plan SHA-256 `a6fa5f3a7f3f45df5d64efe1661a5b17887f88fded31e1cbb1620df5b18a95d1`,
and canonical plan SHA-256
`41ca6c710d8750851350c2108b42970501a5efa14481cff61e2a66877ee90f6d`.

The source re-runs DEC-321 review and DEC-322 freezing and requires the exact DEC-322
fingerprint `b7d3e5461511c8e14dd4402028ad24daefcf431cece3b59575588ba915db510e`.

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future attempt. Actual dispatch, executor availability, execute mode, reserved
2023-2026 access, candidate compilation/promotion, Phase 8B, demo, broker/live,
real-money, and trading remain locked.

The next safe gate is a source-only one-shot historical executor contract. It must not
submit the workflow itself.

## DEC-324 — EXP-062 one-shot historical executor source contract

**Date:** 2026-09-28  
**Status:** SOURCE CONTRACT AUTHORIZED / EXECUTOR + DISPATCH STILL LOCKED

DEC-324 pins the concrete DEC-323 runtime-evidence freeze and authorizes only a source
contract for a future one-shot executor.

`one_shot_executor_source_authorized=true`, while
`historical_executor_available=false`,
`historical_result_dispatch_authorized=false`, and
`historical_execute_mode_available=false`.

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future attempt. Reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is a read-only current-main executor preflight with no submission
path.

## DEC-325 — EXP-062 read-only current-main executor preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY PREFLIGHT / NO EXECUTE MODE

DEC-325 adds a current-main preflight for the DEC-324 source-authorized one-shot
historical executor contract. It pins DEC-324, rechecks the EXP-062 discovery inventory,
and exposes the future discovery command only as evidence while the historical slot
remains empty.

Actual executor availability, dispatch, and execute mode remain false. If run #2
exists, the command is removed and the slot is treated as consumed.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

The next safe gate is a repository-hosted read-only executor-preflight proof.

## DEC-326 — EXP-062 repository-hosted executor-preflight proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN PROOF / NO HISTORICAL DISPATCH

DEC-326 adds a push-to-main, first-run/attempt-1 proof workflow for the exact DEC-325
executor preflight. It pins DEC-323/324/325 source identities, fetches current main and
the EXP-062 discovery inventory, and invokes only the read-only preflight planner.

A valid proof must show the frozen gate proof remains run #1, zero historical-result
attempts, target run #2 / attempt 1, and the exact future discovery command as evidence
only. The workflow has contents/actions read permissions and never executes that
command.

Historical executor availability, actual dispatch, execute mode, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain locked.

The next safe gate after a real successful proof is immutable runtime-evidence review
and freezing.

## DEC-327 — EXP-062 historical executor-preflight proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED

DEC-327 adds a source-only reviewer for future DEC-326 runtime evidence. It requires
the exact read-only proof workflow on merged main, run #1 / attempt 1 success, one
successful preflight job, one non-expired preflight artifact, and downloaded preflight
bytes.

The reviewer revalidates DEC-325, requires zero historical-result attempts and target
run #2 / attempt 1, and records raw/canonical preflight SHA-256 hashes. It pins
DEC-323/324/325/326 source identities.

Historical executor availability, actual dispatch, execute mode, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain locked.

The next gate after real DEC-326 evidence passes review is an immutable concrete
executor-preflight proof freeze.

## DEC-328 — EXP-062 reviewed historical executor-preflight freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO EXECUTOR

DEC-328 adds a deterministic freeze builder for an already-valid DEC-327 review. It
requires the exact DEC-327 stage, proof/run/job/artifact identities, artifact digest,
raw/canonical preflight hashes, target run #2 / attempt 1, and exact DEC-323/324/325/326
source-blob map.

DEC-328 does not invent runtime evidence. Before a real DEC-326 proof exists, the
builder has no concrete evidence to freeze.

Historical executor availability, actual dispatch, execute mode, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

The next safe gate after actual DEC-326 evidence is a concrete runtime-evidence binding
before any one-shot executor workflow is considered.

## DEC-329 — EXP-062 executor-preflight runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / EXECUTOR + DISPATCH STILL LOCKED

DEC-329 binds the actual successful DEC-326 proof on merged head
`a811aacaae82e15b18267b6e4ba659054abb0341`: run `36422936991`, job
`108929843306`, artifact `10970303347`, artifact/ZIP SHA-256
`fe116a7fff7ffdec27e787d3cd7981ac67772276efb12a5b434b04ee3855c74c`,
raw preflight SHA-256 `5dfa7800a8dcbe4537910690a0ba70b3c93467c685d7c5c99898d0b6d111f9d8`,
and canonical preflight SHA-256
`9970dcbf44241a3b9ffc6aab01d8a3bab6749813f88d0771dee101ea640aec3d`.

The source re-runs DEC-327 review and DEC-328 freezing and requires the exact DEC-328
fingerprint `2e295d03066fcfa4dcea300c3f263bcf6a67cb96d6b356410821af493b2d5675`.

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future attempt. Historical executor availability, actual dispatch, execute mode,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

The next safe gate is a source-only one-shot historical executor activation contract.

## DEC-330 — EXP-062 one-shot historical executor activation source contract

**Date:** 2026-09-28  
**Status:** SOURCE ACTIVATION CONTRACT AUTHORIZED / EXECUTOR + DISPATCH STILL LOCKED

DEC-330 pins the concrete DEC-329 runtime-evidence freeze and authorizes only a source
contract for future activation of the one-shot historical executor.

`one_shot_executor_activation_source_authorized=true`, while
`historical_executor_available=false`,
`historical_result_dispatch_authorized=false`, and
`historical_execute_mode_available=false`.

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future attempt. Reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is a read-only current-main executor activation preflight.

## DEC-331 — EXP-062 read-only executor activation preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN ACTIVATION PREFLIGHT / NO EXECUTE MODE

DEC-331 adds a current-main preflight for the DEC-330 source-authorized future
activation of the one-shot historical executor. It pins the exact DEC-330 activation
contract, rechecks the EXP-062 discovery inventory, and exposes the future discovery
command only as evidence while the historical slot remains empty.

Actual executor availability, historical-result dispatch, and execute mode remain
false. If run #2 already exists, the command is removed and the slot is treated as
consumed.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

The next safe gate is a repository-hosted read-only executor activation-preflight
proof.

## DEC-332 — EXP-062 repository-hosted executor activation-preflight proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN PROOF / NO HISTORICAL DISPATCH

DEC-332 adds a push-to-main, first-run/attempt-1 proof workflow for the exact DEC-331
executor activation preflight. It pins DEC-330/331 source identities, fetches current
main and the EXP-062 discovery inventory, and invokes only the read-only activation
preflight planner.

A valid proof must show the frozen gate proof remains run #1, zero historical-result
attempts, target run #2 / attempt 1, and the exact future discovery command as evidence
only. The workflow has contents/actions read permissions and never executes that
command.

Historical executor availability, actual dispatch, execute mode, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain locked.

The next safe gate after a real successful proof is immutable runtime-evidence review
and freezing.

## DEC-333 — EXP-062 executor activation-preflight proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED

DEC-333 adds a source-only reviewer for future DEC-332 runtime evidence. It requires
the exact read-only proof workflow on merged main, run #1 / attempt 1 success, one
successful proof job, one non-expired artifact, and downloaded activation-preflight
bytes.

The reviewer revalidates the DEC-331 activation preflight, requires zero
historical-result attempts and target run #2 / attempt 1, and records raw/canonical
preflight SHA-256 hashes. It pins DEC-329/330/331/332 source identities.

Historical executor availability, actual dispatch, execute mode, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain locked.

The next gate after real DEC-332 evidence passes review is an immutable concrete
activation-preflight proof freeze.

## DEC-334 — EXP-062 historical terminal review contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY PREDECLARED TERMINAL REVIEW / NO RESULT YET

DEC-334 freezes how the sole future EXP-062 historical workflow run #2 / attempt 1
will be judged before the run exists.

A success requires the exact DEC-298 20-job / 20-artifact shape: preflight, all 18
expanded cell jobs, aggregate, every job successful, and every expected artifact
present/non-expired. Such a run is classified
`EXP062_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED`; result contents still
require separate review and candidate compilation remains locked.

Any terminal non-success is classified
`EXP062_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED`. The slot is consumed
permanently; only partial expected evidence may be preserved. Rerun, retry, and
replacement remain false.

The GitHub unexpanded matrix placeholder is permitted only for a non-success run, only
when skipped, and only when no expanded cell jobs coexist with it.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

DEC-334 must be green before the one-shot historical executor reaches main.


## DEC-335 — EXP-062 reviewed historical executor activation-preflight freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO EXECUTOR

DEC-335 adds a deterministic freeze builder for an already-valid DEC-333 review of
the successful DEC-332 executor activation-preflight proof. It preserves the exact
proof run/job/artifact identities, artifact digest, raw/canonical activation-preflight
hashes, target run #2 / attempt 1, and the exact DEC-333 review source-blob map.

DEC-335 cannot invent runtime evidence and cannot dispatch the historical workflow.
It emits a canonical `freeze_fingerprint_sha256` so the later concrete runtime
binding can prove it replayed the same reviewed evidence.

Historical executor availability, actual dispatch, execute mode, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false. DEC-334 remains a required sibling gate before any one-shot
executor reaches main.

The next safe gate is concrete DEC-332 activation-preflight runtime-evidence binding
before any historical executor workflow is considered.


## DEC-336 — EXP-062 executor activation-preflight runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / EXECUTOR + DISPATCH STILL LOCKED

DEC-336 binds the actual successful DEC-332 activation-preflight proof on merged head
`12d11320ae302902df0a0deb7343408922deee83`: run `36431469794`, job
`108958446980`, artifact `10973597441`, artifact/ZIP SHA-256
`ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5`,
raw activation-preflight SHA-256
`775010a0c3d4afe11191adb53d8ad54e7cf0d5de85b1a0b5adcb28c470e9a4a5`,
and canonical SHA-256
`98b9180ae3b438b3c372ba34cbab9473d7f38ba5c1eb1add2dee988df4e09ad8`.

The source replays DEC-333 review and DEC-335 freezing and requires DEC-335
fingerprint `567320a598f245a8e7521281ddde3a1acaa0e3f294aebe12554688d2258f020b`.
It also pins DEC-334 terminal-review criteria before any executor source can advance.

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future attempt. Historical executor availability, actual dispatch, execute mode,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

The next safe gate is a source-only one-shot historical executor workflow before any
dispatch path is considered.


## DEC-337 — EXP-062 one-shot historical executor source contract

**Date:** 2026-09-28  
**Status:** SOURCE AUTHORIZED / RUNTIME DISPATCH LOCKED

DEC-337 adds the source-only contract for the eventual one-shot historical executor.
It requires the concrete DEC-336 runtime freeze and a fresh DEC-331 activation
preflight with zero historical-result attempts, an unconsumed slot, and target run
#2 / attempt 1.

Only source authorization becomes true. Historical executor availability, actual
dispatch, execute mode, retry/replacement, reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading remain
false.

The next safe gate is a repository-hosted proof of this source contract before any
dispatch-capable executor workflow is introduced.


## DEC-338 — EXP-062 one-shot historical executor source proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN SOURCE PROOF / NO HISTORICAL DISPATCH

DEC-338 adds a push-to-main, first-run/attempt-1 proof of the DEC-337 one-shot
historical executor source contract.

The workflow uses contents/actions read permissions only. It downloads the immutable
DEC-332 activation-preflight artifact, independently verifies its ZIP SHA-256, replays
DEC-333 / DEC-335 / DEC-336, rebuilds a fresh DEC-331 activation preflight from current
main, and evaluates DEC-337.

A valid result proves only that the one-shot executor source contract remains valid
while the historical-result slot is still empty and target run #2 / attempt 1 remains
exact. The historical workflow command is data only and is never submitted.

Historical executor availability, historical-result dispatch, execute mode,
rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate after a real successful DEC-338 proof is immutable runtime-evidence
review and freezing before any dispatch-capable executor workflow.


## DEC-339 — EXP-062 one-shot historical executor source-proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED

DEC-339 adds a source-only reviewer for future successful DEC-338 runtime evidence.

It requires the exact DEC-338 proof workflow on merged main, run #1 / attempt 1
success, one successful read-only proof job, one non-expired source-contract artifact,
and downloaded DEC-337 contract bytes.

The reviewer requires the DEC-336 runtime-freeze fingerprint, DEC-334 terminal-review
decision, zero historical-result attempts, an unconsumed verified-available slot, and
target run #2 / attempt 1. It records raw/canonical SHA-256 hashes of the contract.

Historical executor availability, actual dispatch, execute mode,
rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate after real DEC-338 evidence passes review is an immutable
source-proof freeze before any dispatch-capable executor workflow.


## DEC-340 — EXP-062 reviewed one-shot executor source-proof freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO EXECUTOR WORKFLOW

DEC-340 adds a deterministic freeze builder for an already-valid DEC-339 review of a
successful DEC-338 one-shot historical executor source proof.

It preserves the exact proof run/job/artifact identities, artifact digest,
raw/canonical DEC-337 contract hashes, target run #2 / attempt 1, DEC-336
runtime-freeze fingerprint, DEC-334 terminal-review decision, and exact DEC-339 source
map. It emits one canonical `freeze_fingerprint_sha256`.

DEC-340 cannot invent runtime evidence and cannot dispatch the historical workflow.
Historical executor availability, actual dispatch, execute mode,
rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate after real DEC-338 evidence is concrete source-proof runtime-evidence
binding before any dispatch-capable executor workflow.


## DEC-341 — EXP-062 one-shot historical executor source-proof runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / EXECUTOR + DISPATCH STILL LOCKED

DEC-341 binds the actual successful DEC-338 source proof on merged head
`e9dfbf034614b54598d31653da3868ed66aa90ba`: run `36442399041`, job
`108995955292`, artifact `10979242048`, artifact/ZIP SHA-256
`7dff775fc559cf9dbd754f45c24fbc814035b1602b59ca5eb9f82678af4e8b88`,
raw source-contract SHA-256
`484ad49fa3b3e925ae4a3576af840a8736c9b25ef439b619e8b60e8011f94d63`,
and canonical SHA-256
`cb650b81c2549bfb5bfa62f6609bec9b39e4ed118f3e54c302a48a3a27a11616`.

The source re-runs DEC-339 review and DEC-340 freezing and requires the exact DEC-340
fingerprint
`e340394fb987c68d9203a57c9cd363f255729b3424a9600ec03533ff421960a8`.
It also pins DEC-334 terminal-review criteria.

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future attempt. Historical executor availability, actual dispatch, execute mode,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

The next safe gate is a source-only one-shot historical executor workflow contract.


## DEC-342 — EXP-062 one-shot historical executor workflow contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY WORKFLOW CONTRACT / RUNTIME + DISPATCH LOCKED

DEC-342 pins the concrete DEC-341 runtime freeze and authorizes only a future
one-shot historical executor **workflow source contract**.

The sole historical-result slot remains empty and target run #2 / attempt 1 remains
exact. DEC-334 terminal-review criteria and the frozen historical command remain
preserved.

`one_shot_historical_executor_workflow_source_authorized=true`, while historical
executor availability, historical-result dispatch authorization, execute mode,
rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is a read-only current-main one-shot executor workflow preflight.


## DEC-343 — EXP-062 one-shot historical executor workflow preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN WORKFLOW PREFLIGHT / NO EXECUTE MODE

DEC-343 adds a current-main preflight for the DEC-342 source-authorized future
one-shot historical executor workflow.

It pins the exact DEC-342 workflow contract, rechecks the EXP-062 discovery inventory,
and exposes the future discovery command only as evidence while the historical slot
remains empty.

Actual executor availability, historical-result dispatch, and execute mode remain
false. If run #2 already exists, the command is removed and the slot is treated as
consumed.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

The next safe gate is a repository-hosted read-only workflow-preflight proof.


## DEC-344 — EXP-062 one-shot historical executor workflow-preflight proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN WORKFLOW PREFLIGHT PROOF / NO HISTORICAL DISPATCH

DEC-344 adds a push-to-main, first-run/attempt-1 proof of the DEC-343 one-shot
historical executor workflow preflight.

The workflow uses contents/actions read permissions only. It invokes only the
DEC-343 plan surface, fetches current main plus the exact EXP-062 run inventory, and
proves that the historical-result slot remains empty with target run #2 / attempt 1.

The historical workflow command is evidence only and is never submitted. Historical
executor availability, historical-result dispatch, execute mode,
rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate after a real successful DEC-344 proof is immutable runtime-evidence
review and freezing before any dispatch-capable executor workflow.


## DEC-345 — EXP-062 workflow-preflight proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FUTURE RUNTIME-EVIDENCE REVIEWER / NO DISPATCH

DEC-345 adds a reviewer for future successful DEC-344 merged-main evidence. It pins
the proof workflow, DEC-343 preflight/CLI, DEC-342 workflow contract, and active
discovery workflow; requires exact run #1 / attempt 1 success, one successful proof
job, one non-expired artifact, and exact slot-available preflight content; and records
raw/canonical SHA-256 hashes.

Historical executor availability, dispatch, execute mode, retries, reserved data,
candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: deterministic immutable review freeze.


## DEC-346 — EXP-062 workflow-preflight proof freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO EXECUTOR

DEC-346 freezes an already-valid DEC-345 review of future successful DEC-344 runtime
evidence. It preserves exact proof run/job/artifact identities, artifact digest,
raw/canonical preflight hashes, DEC-343/342 identities, target run #2 / attempt 1,
and the exact review source map.

The freeze emits one canonical fingerprint for later concrete runtime binding.
Executor availability, dispatch, execute mode, retries, reserved data,
candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: concrete runtime-evidence binding after real DEC-344 proof success.


## DEC-347 — EXP-062 workflow-preflight proof runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / EXECUTOR + DISPATCH STILL LOCKED

DEC-347 binds the actual successful DEC-344 merged-main proof: head
`c43a1701cadd57c25903d3b637f2af70b28d1065`, run `36455684780`, job
`109041310360`, artifact `10984953455`, artifact/ZIP SHA-256
`eec64c9bb1f6688dca010825e83e191c6a423d21bf6522396d7f650ec2db675f`,
raw preflight SHA-256
`56981ba62638129f39693239d22b76c65cb3a8e0b236741b3a80984137c2c0d7`,
and canonical SHA-256
`d6bf96a73b1377ad65887c6ba001c2c2d39812d58205e59e304c1c88e3ef22dc`.

DEC-347 re-runs DEC-345 review and DEC-346 deterministic freezing and requires the
exact DEC-346 fingerprint
`3ba4b6aba0cafab3989c1f20536ad36603786efdcef49964a31bc99b73a79988`.
DEC-334 terminal-review criteria remain pinned.

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future attempt. Historical executor availability, dispatch, execute mode,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

Next gate: source-only one-shot historical executor workflow-install contract.


## DEC-348 — EXP-062 one-shot historical executor workflow-install contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY INSTALL CONTRACT / WORKFLOW NOT INSTALLED

DEC-348 pins the concrete DEC-347 runtime freeze and authorizes only future
workflow-install source review for
`.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`.

The workflow remains absent under this decision. Historical executor availability,
historical-result dispatch, execute mode, rerun/retry/replacement, reserved
2023-2026 access, candidate compilation/promotion, Phase 8B, demo, broker/live,
real-money, and trading remain false.

The next safe gate is a read-only current-main workflow-install preflight.


## DEC-349 — EXP-062 one-shot historical executor workflow-install preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN INSTALL PREFLIGHT / NO INSTALL OR DISPATCH

DEC-349 adds a current-main preflight for the DEC-348 source-authorized future
one-shot historical executor workflow installation.

It pins the exact DEC-348 install contract, requires the expected future executor
workflow path to remain absent, rechecks the EXP-062 historical-result inventory,
and confirms target run #2 / attempt 1 remains the only future historical attempt.

Install authorization, workflow installed state, executor availability, historical
dispatch, execute mode, rerun/retry/replacement, reserved 2023-2026 access,
candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

The next safe gate is a repository-hosted read-only workflow-install preflight proof.


## DEC-350 — EXP-062 workflow-install preflight proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN INSTALL PREFLIGHT PROOF / NO INSTALL OR DISPATCH

DEC-350 adds a push-to-main, first-run/attempt-1 proof of the DEC-349 workflow-install
preflight.

The workflow pins DEC-348/349 source identities, requires the future executor workflow
path to remain absent, checks exact merged main plus the EXP-062 run inventory, and
invokes only the plan surface.

Install authorization, workflow installed state, executor availability, historical
dispatch, execute mode, rerun/retry/replacement, reserved 2023-2026 access,
candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

Next gate after real success: immutable workflow-install-preflight proof review/freeze.


## DEC-351 — EXP-062 workflow-install preflight proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FUTURE RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH

DEC-351 adds a strict reviewer for future successful DEC-350 merged-main evidence. It
pins the DEC-350 proof workflow, DEC-349 preflight/CLI, DEC-348 install contract, and
the active discovery workflow; requires run #1 / attempt 1 success, one successful
proof job, one non-expired artifact, and exact DEC-349 preflight content; and records
raw/canonical SHA-256 hashes.

The future executor workflow path must still be absent. Install authorization,
installed state, executor availability, dispatch, execute mode, retries, reserved
data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: deterministic immutable review freeze.


## DEC-352 — EXP-062 workflow-install preflight proof freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO INSTALL OR EXECUTOR

DEC-352 freezes an already-valid DEC-351 review of future successful DEC-350 runtime
evidence. It preserves exact proof run/job/artifact identities, artifact digest,
raw/canonical preflight hashes, DEC-349/348 identities, the absent future executor
workflow path, target run #2 / attempt 1, and the exact review source map.

The freeze emits one canonical fingerprint for later concrete runtime binding.
Workflow-install authorization, installed state, executor availability, dispatch,
execute mode, retries, reserved data, candidate/promotion, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: concrete runtime-evidence binding after real DEC-350 proof success.


## DEC-353 — EXP-062 workflow-install preflight proof runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED

DEC-353 binds the actual successful DEC-350 merged-main proof: head
`bef60cd8656f0db48293570c13f91e2e09fe5be8`, run `36461898040`, job
`109062250103`, artifact `10987972547`, artifact/ZIP SHA-256
`60a723a55502ee9b8145258c5482ce71b82b2331c572378536b14d78f6ef2f91`,
raw install-preflight SHA-256
`ee754581b87576c3c23228a2371b88b3b8a38fdcd9c20ebd2c222c18f7c65e0d`,
and canonical SHA-256
`5c1893ea24a627ea421f05564d6d0cc490215201c01162fbe0b6ab519a323c8b`.

DEC-353 re-runs DEC-351 review and DEC-352 deterministic freezing and requires the
exact DEC-352 fingerprint
`75fad6795f4046d83f5ae29f08475c969e29d3fe3af0e3448dde46292a959f4a`.
DEC-334 terminal-review criteria remain pinned.

The future executor workflow path remains absent. Install authorization, installed
state, executor availability, historical dispatch, execute mode, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

Next gate: source-only one-shot historical executor workflow-installation source contract.


## DEC-354 — EXP-062 one-shot historical executor workflow-installation source contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DORMANT INSTALLATION CONTRACT / ACTIVE WORKFLOW ABSENT

DEC-354 pins the concrete DEC-353 runtime freeze and authorizes only a future dormant
executor-workflow source outside `.github/workflows/`.

The dormant template path is
`docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled`;
the reserved active path is
`.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`.

The dormant template remains absent under this decision. Install authorization,
installed state, executor availability, historical dispatch, execute mode,
rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

The next safe gate is the dormant executor workflow template source itself.


## DEC-355 — EXP-062 dormant one-shot historical executor workflow source

**Date:** 2026-09-28  
**Status:** DORMANT DISABLED TEMPLATE SOURCE / ACTIVE WORKFLOW UNINSTALLED

DEC-355 adds the disabled source template for the future one-shot historical executor
workflow outside `.github/workflows/`.

The template is inert but fully encodes the future one-shot behavior: exact merged
main, executor run #1 / attempt 1, frozen discovery source, empty historical-result
slot, exactly one historical workflow dispatch, exact target run #2 / attempt 1, and
an immutable executor receipt.

The dormant template requires `actions: write` only as future source semantics; no
active workflow is installed and no dispatch occurs under DEC-355.

Install authorization, installed state, executor availability, historical dispatch,
execute mode, rerun/retry/replacement, reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading remain
false.

The next safe gate is a repository-hosted read-only proof of this dormant source.


## DEC-356 — EXP-062 dormant one-shot historical executor source proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN DORMANT SOURCE PROOF / ACTIVE EXECUTOR ABSENT

DEC-356 adds a push-to-main, first-run/attempt-1 proof of the DEC-355 dormant
one-shot historical executor workflow source.

The proof pins DEC-354/355 plus the disabled executor template and active discovery
workflow, requires the active executor workflow path to remain absent, validates the
dormant source directly, and uploads only a source JSON artifact.

No workflow installation or historical dispatch occurs. Install authorization,
installed state, executor availability, dispatch, execute mode, rerun/retry/
replacement, reserved 2023-2026 access, candidate compilation/promotion, Phase 8B,
demo, broker/live, real-money, and trading remain false.

The next safe gate after real DEC-356 success is immutable proof review/freeze.


## DEC-357 — EXP-062 dormant one-shot historical executor source-proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FUTURE RUNTIME-EVIDENCE REVIEWER / ACTIVE EXECUTOR ABSENT

DEC-357 adds a strict reviewer for future successful DEC-356 merged-main evidence. It
pins DEC-356/355/354, the dormant executor template, and active discovery workflow;
requires run #1 / attempt 1 success, one successful proof job, one non-expired
artifact, and exact DEC-355 source JSON; and records raw/canonical SHA-256 hashes.

The dormant template remains source only. Install authorization, installed state,
executor availability, historical dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

Next gate: deterministic immutable review freeze.


## DEC-358 — EXP-062 dormant one-shot historical executor source-proof freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / ACTIVE EXECUTOR UNINSTALLED

DEC-358 freezes an already-valid DEC-357 review of future successful DEC-356 runtime
evidence. It preserves exact proof run/job/artifact identities, artifact digest,
raw/canonical source hashes, DEC-355 dormant-source identity, template blob, target
run #2 / attempt 1, and the exact review source map.

The freeze emits one canonical fingerprint for later concrete runtime binding.
Active workflow installation, executor availability, historical dispatch, execute
mode, retries, reserved data, candidate/promotion, Phase 8B, demo/live, real-money,
and trading remain locked.

Next gate: concrete runtime-evidence binding after real DEC-356 proof success.


## DEC-359 — EXP-062 dormant executor source proof runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / ACTIVE INSTALL + DISPATCH STILL LOCKED

DEC-359 binds the actual successful DEC-356 merged-main proof: head
`67337de4b21efab0cbafb3c9237397f0a98d524e`, run `36473192632`, job
`109100293950`, artifact `10991479562`, artifact/ZIP SHA-256
`092e1daebf889560d27ebe57242772c3806322627dab03e64a2ff400d9b4b1d1`,
raw dormant-source SHA-256
`1dfae5078e400fc2dbf0b10ef6d4297dc4d3c0660386ebb8c46b63c6dbe69060`,
and canonical SHA-256
`4d6cf8999ecb5346a10ecb31cdc1b669736d4d466e6b31c503b3fbf1a5e633a7`.

DEC-359 re-runs DEC-357 review and DEC-358 deterministic freezing and requires the
exact DEC-358 fingerprint
`8ba4411b8c7468a1f0eecc0352490e00577452ce96a81710fca6457e779e9897`.
DEC-334 terminal-review criteria remain pinned.

The dormant executor template remains source only and the active workflow remains
uninstalled. Historical-result attempts remain zero and target run #2 / attempt 1
remains the only future attempt. Install authorization, executor availability,
dispatch, execute mode, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

Next gate: source-only active one-shot historical executor workflow install contract.


## DEC-360 — EXP-062 active one-shot historical executor workflow install contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY ACTIVE INSTALL CONTRACT / ACTIVE WORKFLOW ABSENT

DEC-360 pins the concrete DEC-359 runtime freeze and exact dormant executor template,
then authorizes only source review for a future active workflow installation.

The reserved active path remains absent. Workflow-install authorization, workflow
installed state, historical executor availability, historical-result dispatch,
execute mode, rerun/retry/replacement, reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading remain
false.

The next safe gate is a read-only current-main active workflow-install preflight.


## DEC-361 — EXP-062 active one-shot historical executor workflow install preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN ACTIVE INSTALL PREFLIGHT / NO INSTALL OR DISPATCH

DEC-361 adds a current-main preflight bound to DEC-360 and the exact dormant executor
template. It requires the active executor workflow path to remain absent, rechecks the
EXP-062 historical-result inventory, and confirms target run #2 / attempt 1 remains
the only future historical attempt.

The CLI exposes only `plan`. Install authorization, workflow installed state,
executor availability, historical dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

Next gate: repository-hosted read-only active workflow-install preflight proof.


## DEC-362 — EXP-062 active workflow install preflight proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN ACTIVE INSTALL PREFLIGHT PROOF

DEC-362 adds a push-to-main, first-run/attempt-1 proof of the DEC-361 active
workflow-install preflight.

The workflow pins DEC-360/361, the exact dormant template, active discovery workflow,
and planning runtime; requires the active executor workflow path to remain absent;
checks exact merged main plus the EXP-062 run inventory; and invokes only the plan
surface.

Install authorization, workflow installed state, executor availability, historical
dispatch, execute mode, rerun/retry/replacement, reserved 2023-2026 access,
candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

Next gate after real success: immutable active-install-preflight proof review/freeze.


## DEC-363 — EXP-062 active install preflight proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FUTURE RUNTIME-EVIDENCE REVIEWER

DEC-363 adds a strict reviewer for future successful DEC-362 merged-main evidence.
It pins the DEC-362 proof workflow, DEC-361 preflight/CLI, DEC-360 install contract,
the dormant executor template, and the active discovery workflow; requires run #1 /
attempt 1 success, one successful proof job, one non-expired artifact, and exact
DEC-361 preflight content; and records raw/canonical SHA-256 hashes.

The active executor workflow path must remain absent. Install authorization,
installed state, executor availability, dispatch, execute mode, retries, reserved
data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: deterministic immutable review freeze.


## DEC-364 — EXP-062 active workflow-install preflight proof freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO INSTALL OR EXECUTOR

DEC-364 freezes an already-valid DEC-363 review of successful DEC-362 runtime
evidence. It preserves exact proof run/job/artifact identities, artifact digest,
raw/canonical preflight hashes, DEC-361/360 identities, dormant-template identity,
active workflow-absent state, target run #2 / attempt 1, and the exact review source
map.

The freeze emits one canonical fingerprint for later concrete runtime binding.
Workflow-install authorization, installed state, executor availability, dispatch,
execute mode, retries, reserved data, candidate/promotion, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: concrete runtime-evidence binding against the real DEC-362 proof.


## DEC-365 — EXP-062 active workflow-install preflight proof runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED

DEC-365 binds the actual successful DEC-362 merged-main proof: head
`8e74ca94237963253b4fd6e42c42965cabec3ab1`, run `36478916362`, job
`109119455390`, artifact `10996155764`, artifact/ZIP SHA-256
`5554cabdf72e87c6c860746f1d76d0816a3dd3ebdf2b443b911b5027e81f070a`,
raw preflight SHA-256
`c70cbdb3f593de110a21d6501d867ed23f6be70b7815993ef1b62fea1d2477fc`,
and canonical SHA-256
`010f1bcdd595de78ebe55ad3729e641345f3c486e3a46e38a60a7072555ad30b`.

DEC-365 re-runs DEC-363 review and DEC-364 deterministic freezing and requires the
exact DEC-364 fingerprint
`2e8c36e891b20dc1811301a4b461d51c9fa46e34b098cbe5af1e3a27bc129932`.
DEC-334 terminal-review criteria remain pinned.

The active executor workflow path remains absent. Historical-result attempts remain
zero and target run #2 / attempt 1 remains the only future attempt. Workflow-install
authorization, workflow installed state, historical executor availability, dispatch,
execute mode, reserved 2023-2026 access, candidate compilation/promotion, Phase 8B,
demo, broker/live, real-money, and trading remain false.

Next gate: source-only active one-shot historical executor workflow-installation contract.


## DEC-366 — EXP-062 active one-shot historical executor workflow-installation contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY INSTALLATION CONTRACT / ACTIVE WORKFLOW STILL ABSENT

DEC-366 pins the concrete DEC-365 runtime freeze and the exact dormant executor
workflow template, then authorizes only the active workflow-installation source
contract.

The active workflow path remains absent. Workflow-install authorization, installed
state, historical executor availability, dispatch, execute mode, rerun/retry/
replacement, reserved 2023-2026 access, candidate compilation/promotion, Phase 8B,
demo, broker/live, real-money, and trading remain false.

Historical-result attempts remain zero and target run #2 / attempt 1 remains the only
future attempt.

Next gate: read-only current-main active workflow-installation preflight.


## DEC-367 — EXP-062 active workflow-installation preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH

DEC-367 adds a current-main preflight for the DEC-366 source-authorized active
workflow-installation contract.

It pins the DEC-366 contract and exact dormant template, requires exact main,
requires the active executor workflow path to remain absent, and rechecks that the
historical-result slot remains unused with target run #2 / attempt 1.

The CLI exposes plan only. Workflow-install authorization, installed state, executor
availability, dispatch, execute mode, rerun/retry/replacement, reserved data,
candidate/promotion, Phase 8B, demo/live, real-money, and trading remain false.

Next gate: repository-hosted read-only active workflow-installation preflight proof.


## DEC-368 — EXP-062 active workflow-installation preflight proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN PREFLIGHT PROOF / NO INSTALL OR DISPATCH

DEC-368 adds a push-to-main, first-run/attempt-1 proof of the DEC-367 active
workflow-installation preflight.

The workflow pins DEC-366/367 source identities, requires the active executor workflow
path to remain absent, checks exact merged main plus the EXP-062 run inventory, and
invokes only the plan surface.

Workflow-install authorization, installed state, executor availability, historical
dispatch, execute mode, rerun/retry/replacement, reserved 2023-2026 access,
candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

Next gate after real success: immutable installation-preflight proof review/freeze.


## DEC-369 — EXP-062 active workflow-installation preflight proof reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FUTURE RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH

DEC-369 adds a strict reviewer for future successful DEC-368 merged-main evidence.
It pins the DEC-368 proof workflow, DEC-367 preflight/CLI, DEC-366 installation
contract, dormant executor template, and active discovery workflow; requires run #1 /
attempt 1 success, one successful proof job, one non-expired artifact, and exact
DEC-367 preflight content; and records raw/canonical SHA-256 hashes.

The active executor workflow path must remain absent. Workflow-install authorization,
installed state, executor availability, dispatch, execute mode, retries, reserved
data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: deterministic immutable review freeze.


## DEC-370 — EXP-062 active workflow-installation preflight proof freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO INSTALL OR EXECUTOR

DEC-370 freezes an already-valid DEC-369 review of future successful DEC-368 runtime
evidence. It preserves exact proof run/job/artifact identities, artifact digest,
raw/canonical preflight hashes, DEC-367/366 identities, dormant executor-template
identity, active workflow-absent state, target run #2 / attempt 1, and the exact
review source map.

The freeze emits one canonical fingerprint for later concrete runtime binding.
Workflow-install authorization, installed state, executor availability, dispatch,
execute mode, retries, reserved data, candidate/promotion, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: concrete runtime-evidence binding after real DEC-368 proof success.


## DEC-371 — EXP-062 active workflow-installation preflight proof runtime evidence freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED

DEC-371 binds the actual successful DEC-368 merged-main proof: head
`035c0ee8190a7eb1e2c8ac80771e6eeb19d1e8e1`, run `36484309283`, job
`109137344254`, artifact `10997847720`, artifact/ZIP SHA-256
`d122e474752f1ec8127eb610b55321dbf94cc7dcb339eca43eafb7e429ef4a07`,
raw preflight SHA-256
`5bf7760c7ad36e642eeeaf9e29b5fb0e5108a4059207ff2d7d75bd4c9f6bcf3b`,
and canonical SHA-256
`30de670f8483139b23fbd51bd05444677278fd7d1ba1f1eb8f0cc33409cf3a74`.

DEC-371 re-runs DEC-369 review and DEC-370 deterministic freezing and requires the
exact DEC-370 fingerprint
`51e47a3d6d2876b52e2090714e6f89b4c2ce0ae2d869d79e5b2cd4586c774af6`.
DEC-334 terminal-review criteria remain pinned.

The active executor workflow path remains absent. Historical-result attempts remain
zero and target run #2 / attempt 1 remains the only future attempt. Workflow-install
authorization, installed state, historical executor availability, dispatch, execute
mode, reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

Next gate: source-only active one-shot historical executor workflow install-authorization contract.


## DEC-372 — EXP-062 active one-shot historical executor install-authorization contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY AUTHORIZATION CONTRACT / INSTALL STILL LOCKED

DEC-372 pins the concrete DEC-371 runtime freeze and authorizes only future
install-authorization source review for the active one-shot historical executor
workflow.

The active workflow path remains absent. Actual workflow-install authorization,
workflow installed state, historical executor availability, historical-result
dispatch, execute mode, rerun/retry/replacement, reserved 2023-2026 access,
candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

The next safe gate is a read-only current-main install-authorization preflight.


## DEC-373 — EXP-062 active workflow install-authorization preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN AUTHORIZATION PREFLIGHT / NO INSTALL OR DISPATCH

DEC-373 adds a current-main preflight for the DEC-372 source-authorized future
install-authorization decision.

It pins the exact DEC-372 contract and dormant executor template, requires the active
executor workflow path to remain absent, rechecks the EXP-062 historical-result
inventory, and confirms target run #2 / attempt 1 remains the only future historical
attempt.

Actual workflow-install authorization, workflow installed state, executor
availability, dispatch, execute mode, rerun/retry/replacement, reserved 2023-2026
access, candidate compilation/promotion, Phase 8B, demo, broker/live, real-money,
and trading remain false.

The next safe gate is a repository-hosted read-only install-authorization preflight proof.


## DEC-374 — EXP-062 install-authorization preflight proof

**Date:** 2026-09-28  
**Status:** READ-ONLY MERGED-MAIN AUTHORIZATION PREFLIGHT PROOF / NO INSTALL OR DISPATCH

DEC-374 adds a push-to-main, first-run/attempt-1 proof of the DEC-373
install-authorization preflight.

The workflow pins DEC-372/373 source identities, the dormant executor template, the
active discovery workflow, and the pinned planning runtime. It requires the active
executor workflow path to remain absent, checks exact merged main plus the EXP-062
run inventory, and invokes only the plan surface.

Actual workflow-install authorization, workflow installed state, executor
availability, historical dispatch, execute mode, rerun/retry/replacement, reserved
2023-2026 access, candidate compilation/promotion, Phase 8B, demo, broker/live,
real-money, and trading remain false.

Next gate after real success: immutable install-authorization-preflight proof review/freeze.


## DEC-375 — EXP-062 active workflow install-authorization preflight proof reviewer

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH

DEC-375 adds a strict reviewer for the successful DEC-374 merged-main proof. It pins
the DEC-374 proof workflow, DEC-373 preflight/CLI, DEC-372 install-authorization
contract, dormant executor template, and active discovery workflow; requires exact
run #1 / attempt 1 success, one successful proof job, one non-expired artifact, and
exact DEC-373 preflight content; and records raw/canonical SHA-256 hashes.

The active executor workflow path remains absent. Actual install authorization,
installed state, executor availability, dispatch, execute mode, retries, reserved
data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: deterministic immutable review freeze.


## DEC-376 — EXP-062 active install-authorization preflight proof freeze

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO INSTALL OR EXECUTOR

DEC-376 freezes an already-valid DEC-375 review of successful DEC-374 evidence. It
preserves exact proof run/job/artifact identities, artifact digest, raw/canonical
preflight hashes, DEC-373/372 identities, dormant executor-template identity, the
active workflow-absent state, target run #2 / attempt 1, and the exact review source
map.

The freeze emits one canonical fingerprint for later concrete runtime binding.
Actual install authorization, installed state, executor availability, dispatch,
execute mode, retries, reserved data, candidate/promotion, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: concrete runtime-evidence binding.


## DEC-377 — EXP-062 install-authorization preflight proof runtime evidence freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED

DEC-377 binds the successful DEC-374 merged-main proof: head
`c23ba694fcf60e2a73280f59fe0bf13d90ffa229`, run `36542684978`, job
`109321600936`, artifact `11020419084`, artifact/ZIP SHA-256
`f7829f71c481143517b918c7d54b1cb43136edcd50ea9076e3795935bd994384`,
raw preflight SHA-256
`e5de1145a6f39ca42413fb5ce1eed297d8bdcf572923e296d2b6d773e945e45f`,
and canonical SHA-256
`994b96d76cf50cfae019d21b4b478d6e0b6ffc0c99fda9efa7c7aa4bf50263dc`.

DEC-377 re-runs DEC-375 review and DEC-376 deterministic freezing and requires the
exact DEC-376 fingerprint
`fb4c445610884db868a516f9a2086c8d0a6f22d397cb7e8d39806548101c1595`.
DEC-334 terminal-review criteria remain pinned.

The active executor workflow path remains absent. Actual install authorization,
installed state, executor availability, dispatch, execute mode, reserved data, and
all downstream trading paths remain locked.

Next gate: source-only active workflow install-decision contract.


## DEC-378 — EXP-062 active executor workflow install-decision contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY INSTALL-DECISION CONTRACT / NO INSTALL OR DISPATCH

DEC-378 pins the concrete DEC-377 runtime-evidence freeze at fingerprint
`24619aed5578085ee3e2d3555e1b109817d9816042f646446dbc406b20f13593`
and the exact dormant executor template. It authorizes only the source contract for
the future workflow-install decision.

The active executor workflow path remains absent. Actual install authorization,
installed state, executor availability, historical dispatch, execute mode, reserved
data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: read-only current-main active executor workflow install-decision preflight.


## DEC-379 — EXP-062 active executor workflow install-decision preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH

DEC-379 pins the exact DEC-378 install-decision contract and dormant executor
template, requires exact current main, requires the active executor workflow path to
remain absent, and verifies the historical-result slot is unused with target run #2 /
attempt 1.

The CLI exposes only `plan`. Actual workflow-install authorization, installed
state, executor availability, historical dispatch, execute mode, reserved data, and
all downstream trading paths remain locked.

Next gate: repository-hosted read-only install-decision-preflight proof.


## DEC-380 — EXP-062 active executor workflow install-decision preflight proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / NO INSTALL OR DISPATCH

DEC-380 adds a first-run/attempt-1 push-to-main proof for DEC-379. It pins exact
DEC-378/379 source identities, the dormant executor template, active discovery
workflow, and pinned planning runtime.

The workflow uses only contents/actions read permissions, invokes only the DEC-379
`plan` surface, requires the active executor workflow path absent, and verifies zero
historical-result attempts with target run #2 / attempt 1.

A successful run uploads only the install-decision-preflight JSON. No installation,
historical dispatch, execute mode, or downstream trading authority is added.

Next gate after real successful runtime evidence: immutable proof review/freeze.


## DEC-381 — EXP-062 active workflow install-decision preflight proof reviewer

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH

DEC-381 adds a strict reviewer for successful DEC-380 merged-main proof evidence.
It pins the DEC-380 proof workflow, DEC-379 preflight/CLI, DEC-378 install-decision
contract, dormant executor template, and active discovery workflow. It requires run
#1 / attempt 1 success, one successful proof job, one non-expired artifact, and exact
DEC-379 preflight bytes.

The active executor workflow path remains absent. Install-authorization and
install-decision source contracts may be true, but actual install authorization,
installed state, executor availability, dispatch, execute mode, retries, reserved
data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain
locked.

Next gate after real successful DEC-380 evidence: deterministic immutable review
freeze.


## DEC-382 — EXP-062 active workflow install-decision preflight proof freeze

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC REVIEW FREEZE / NO INSTALL OR DISPATCH

DEC-382 adds a deterministic source-only freeze for a valid DEC-381 review. It
preserves exact runtime identities, artifact digest, DEC-379 preflight hashes,
source map, dormant-template identity, active workflow-absent state, and target
historical run #2 / attempt 1.

The freeze emits one canonical fingerprint for later concrete runtime binding. It
adds no install, dispatch, or execute surface and keeps reserved data plus all
downstream trading paths locked.

Next gate after real DEC-380 evidence: concrete proof runtime-evidence binding.


## DEC-383 — EXP-062 active workflow install-decision preflight proof runtime evidence freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED

DEC-383 binds the successful DEC-380 merged-main proof at head
`fa96bc731ed8d21cec883451f7ec5e984b74df40`, run `36553935570`, job
`109358450875`, artifact `11025737149`, and artifact/ZIP SHA-256
`f863ea57b45e2c0e12892732747094f8f4f63793cf212be018d7d6cbade6555b`.

The exact DEC-379 preflight hashes are raw
`05bb0e78cd14d22ba84a2bd46bc2fde894e088ad4e96fdd463a040ea91718ed0`
and canonical
`27e6ef7221062844b1f4b12f6fae55c9de2d933c4f606411cd676e982201487f`.
DEC-383 replays DEC-381 review plus DEC-382 deterministic freezing and requires
DEC-382 fingerprint
`be15d3ffe0a66befeec91694e5c412e0d7678818835774361258edf06b06b6f8`.

The active executor workflow path remains absent. Actual workflow-install
authorization, installed state, executor availability, historical dispatch, execute
mode, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and
trading remain locked.

Next gate: source-only workflow install-execution authorization contract.


## DEC-384 — EXP-062 workflow install-execution authorization contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY EXECUTION-AUTHORIZATION CONTRACT / INSTALL STILL LOCKED

DEC-384 consumes the concrete DEC-383 runtime freeze at source blob
`b946d5b3d390d008634d49a2a0b560211d18aa2b` and fingerprint
`e4369f71272b8fd8a3ef4104f12aaf748bd7c938e4feb648a87c6aadd14e2e19`.

It authorizes only the source contract for a later workflow-install execution
decision. The active executor workflow path remains absent. Actual workflow-install
authorization, installed state, executor availability, historical dispatch, execute
mode, rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B,
demo/live, real-money, and trading remain locked.

Next gate: read-only current-main install-execution authorization preflight.


## DEC-385 — EXP-062 workflow install-execution authorization preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH

DEC-385 pins the exact DEC-384 install-execution authorization contract and dormant
executor template, requires exact current main, requires the active executor workflow
path to remain absent, and verifies the historical-result slot is unused with target
run #2 / attempt 1.

The CLI exposes only `plan`. Install-authorization source, install-decision source,
and install-execution authorization source are all preserved as source-only gates.
Actual workflow-install authorization, installed state, executor availability,
historical dispatch, execute mode, reserved data, and all downstream trading paths
remain locked.

Next gate: repository-hosted read-only install-execution-authorization-preflight proof.


## DEC-386 — EXP-062 install-execution authorization preflight proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / NO INSTALL OR DISPATCH

DEC-386 adds a first-run/attempt-1 push-to-main proof for DEC-385. It pins exact
DEC-384/385 source identities, the dormant executor template, active discovery
workflow, and pinned planning runtime.

The workflow uses only contents/actions read permissions, invokes only the DEC-385
`plan` surface, requires the active executor workflow path absent, verifies zero
historical-result attempts with target run #2 / attempt 1, and requires the complete
three-gate source-only authorization chain.

A successful run uploads only the install-execution-authorization-preflight JSON. No
installation, historical dispatch, execute mode, or downstream trading authority is
added.

Next gate after real successful runtime evidence: immutable proof review/freeze.


## DEC-387 — EXP-062 install-execution authorization preflight proof reviewer

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH

DEC-387 adds a strict reviewer for successful DEC-386 merged-main proof evidence.
It pins the DEC-386 proof workflow, DEC-385 preflight/CLI, DEC-384 execution-
authorization contract, dormant executor template, and active discovery workflow. It
requires run #1 / attempt 1 success, one successful proof job, one non-expired
artifact, and exact DEC-385 preflight bytes.

The active executor workflow path remains absent. All three source-only gates may be
true, but actual install authorization, installed state, executor availability,
dispatch, execute mode, retries, reserved data, candidate/promotion, Phase 8B,
demo/live, real-money, and trading remain locked.

Next gate after real successful DEC-386 evidence: deterministic immutable review
freeze.


## DEC-388 — EXP-062 install-execution authorization preflight proof freeze

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC REVIEW FREEZE / NO INSTALL OR DISPATCH

DEC-388 deterministically freezes an already-valid DEC-387 review of a successful
DEC-386 install-execution-authorization-preflight proof. It preserves exact
proof run/job/artifact identities, artifact digest, DEC-385 preflight hashes,
DEC-385/384 identities, source map, dormant-template identity, active-workflow-
absent state, and target historical run #2 / attempt 1.

The freeze emits one canonical fingerprint for later concrete runtime binding.
Actual workflow-install authorization, installed state, executor availability,
historical dispatch, execute mode, reserved data, candidate/promotion, Phase 8B,
demo/live, real-money, and trading remain locked.

Next gate after real DEC-386 evidence: concrete proof runtime-evidence binding.


## DEC-389 — EXP-062 install-execution authorization preflight proof runtime evidence freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED

DEC-389 binds the successful DEC-386 merged-main proof at head
`cdbef40d1c9908650155933ae5073909ad9be24d`, run `36558750341`, job
`109374198795`, artifact `11029316948`, and artifact/ZIP SHA-256
`5908aff795243b98d8dc0f2b15b603df77ec1b1313c03d76b63452c181bf8d02`.

The exact DEC-385 preflight hashes are raw
`ff645bc0c6742cf05f1edbbb8438b2659ccbf00cd6d40edef284acf1e03c8dd2`
and canonical
`6fe2e118136351ffd4d72d6aad7093e83758905378c654a6df0eb927d7ab43e6`.
DEC-389 replays DEC-387 review plus DEC-388 deterministic freezing and requires
DEC-388 fingerprint
`594b2db3aa50b5c09d7f53a4635cea40b4e566fddd0d16a6574e1322ef8a48af`.

The active executor workflow remains absent. Actual workflow-install authorization,
installed state, executor availability, historical dispatch, execute mode, reserved
data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain
locked.

Next gate: source-only workflow install-execution contract.


## DEC-390 — EXP-062 active workflow install-execution contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY INSTALL-EXECUTION CONTRACT / NO INSTALL OR DISPATCH

DEC-390 binds the concrete DEC-389 runtime-evidence freeze at fingerprint
`3517e83d30097041e7a8a74219d6da8b6fe77cf6ae3f048bffec923913826bc1`
and the exact dormant executor template. The real predecessor proof head is
`cdbef40d1c9908650155933ae5073909ad9be24d`.

The prior source-only gates remain true and DEC-390 authorizes only the
install-execution contract source. The active executor workflow path remains absent.
Actual install authorization, installed state, executor availability, historical
dispatch, execute mode, reserved data, candidate/promotion, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: read-only current-main workflow install-execution preflight.


## DEC-391 — EXP-062 active workflow install-execution preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH

DEC-391 pins the exact DEC-390 install-execution contract and dormant executor
template, requires exact current main, requires the active executor workflow path to
remain absent, and verifies the historical-result slot is unused with target run #2 /
attempt 1.

The CLI exposes only `plan`. All four source-only gates remain true. Actual
workflow-install authorization, installed state, executor availability, historical
dispatch, execute mode, reserved data, and all downstream trading paths remain
locked.

Next gate: repository-hosted read-only workflow install-execution preflight proof.


## DEC-392 — EXP-062 workflow install-execution preflight proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / NO INSTALL OR DISPATCH

DEC-392 adds a first-run/attempt-1 push-to-main proof for DEC-391. It pins exact
DEC-390/391 source identities, the dormant executor template, active discovery
workflow, and pinned planning runtime.

The workflow uses only contents/actions read permissions, invokes only the DEC-391
`plan` surface, requires the active executor workflow path absent, and verifies zero
historical-result attempts with target run #2 / attempt 1.

A successful run uploads only the install-execution-preflight JSON. No installation,
historical dispatch, execute mode, or downstream trading authority is added.

Next gate after real successful runtime evidence: immutable proof review/freeze.


## DEC-393 — EXP-062 workflow install-execution preflight proof reviewer

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH

DEC-393 adds a strict reviewer for successful DEC-392 merged-main proof evidence.
It pins the DEC-392 proof workflow, DEC-391 preflight/CLI, DEC-390 install-execution
contract, dormant executor template, and active discovery workflow. It requires run
#1 / attempt 1 success, one successful proof job, one non-expired artifact, and exact
DEC-391 preflight bytes.

All four source-only gates may be true. The active executor workflow path remains
absent, while actual install authorization, installed state, executor availability,
dispatch, execute mode, retries, reserved data, candidate/promotion, Phase 8B,
demo/live, real-money, and trading remain locked.

Next gate after real successful DEC-392 evidence: deterministic immutable review
freeze.


## DEC-394 — EXP-062 workflow install-execution preflight proof freeze

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC REVIEW FREEZE / NO INSTALL OR DISPATCH

DEC-394 adds a deterministic source-only freeze for a valid DEC-393 review. It
preserves exact DEC-392 proof identities, artifact digest, DEC-391 preflight hashes,
source map, dormant-template identity, active workflow-absent state, and target
historical run #2 / attempt 1.

The freeze emits one canonical fingerprint for later concrete runtime binding. All
four source-only gates may remain true, but it adds no install, dispatch, or execute
surface and keeps reserved data plus all downstream trading paths locked.

Next gate after real DEC-392 evidence: concrete proof runtime-evidence binding.


## DEC-395 — EXP-062 workflow install-execution preflight proof runtime freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME-EVIDENCE BINDING / NO INSTALL OR DISPATCH

DEC-395 binds the real successful DEC-392 merged-main proof at head
`dc1a2cfd5a11595f2ad943277f79e043625bd3e9`, run `36568114050`,
job `109405007879`, and artifact `11032917944`.

It pins artifact/ZIP digest
`f8119b5845f9ba824caebaa48012d19f41668767b71773d94d305f4f78f5c103`,
raw DEC-391 preflight hash
`a9fd545df8c2dc2f05813df5e827f5e9685d5c7c6ea521ca07b6a709ca188601`,
canonical preflight hash
`bd91ae808a6ed1fdc24c4fb5b64b8744a13a53fbe3a6d58d0f5062ba26eea78b`,
and DEC-394 freeze fingerprint
`9357b1c6591a801237acacf7cb7eab1f5302608770ad7b3033566bda39cb3548`.

All four source-only gates remain true. The active executor workflow path remains
absent and actual install, executor, dispatch, execute, reserved-data, and trading
authority remain locked.

Next gate: source-only active executor workflow install-activation contract.


## DEC-396 — EXP-062 workflow install-activation contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY INSTALL-ACTIVATION CONTRACT / ACTIVE WORKFLOW ABSENT

DEC-396 consumes the corrected DEC-395 runtime freeze at fingerprint
`7b5170f7af52561cd1a7cf78683065ca0ebef59bda2fdb81f25073ef1abced6f`
and authorizes only the source contract for future activation of the executor
workflow installation path.

All four predecessor source-only gates remain true and DEC-396 adds only the
workflow install-activation source flag. Actual workflow-install authorization,
installed state, executor availability, historical dispatch, execute mode, reserved
data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain
locked.

Next gate: read-only current-main workflow install-activation preflight.


## DEC-397 — EXP-062 workflow install-activation preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN INSTALL-ACTIVATION PREFLIGHT / NO INSTALL

DEC-397 pins the exact DEC-396 workflow install-activation contract, requires exact
current main, requires the active executor workflow path to remain absent, and
rechecks the unused historical-result slot with target run #2 / attempt 1.

All five source-only gates remain true. The CLI exposes only `plan`. Actual
workflow-install authorization, installed state, executor availability, historical
dispatch, execute mode, reserved data, candidate/promotion, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: repository-hosted read-only workflow install-activation preflight proof.


## DEC-398 — EXP-062 workflow install-activation preflight proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / NO INSTALL OR DISPATCH

DEC-398 adds a first-run/attempt-1 push-to-main proof for DEC-397. It pins exact
DEC-396/397 source identities, the dormant executor template, active discovery
workflow, and pinned planning runtime.

The workflow uses only contents/actions read permissions, invokes only the DEC-397
`plan` surface, requires the active executor workflow path absent, and verifies zero
historical-result attempts with target run #2 / attempt 1.

A successful run uploads only the install-activation-preflight JSON. Actual
workflow installation, historical dispatch, execute mode, and downstream trading
authority remain locked.

Next gate after real successful runtime evidence: immutable proof review/freeze.


## DEC-399 — EXP-062 workflow install-activation preflight proof reviewer

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH

DEC-399 adds a strict reviewer for successful DEC-398 merged-main proof evidence.
It pins the DEC-398 proof workflow, DEC-397 preflight/CLI, DEC-396 install-activation
contract, dormant executor template, and active discovery workflow. It requires run
#1 / attempt 1 success, one successful proof job, one non-expired artifact, and exact
DEC-397 preflight bytes.

All five source-only gates may be true. The active executor workflow path remains
absent, while actual install authorization, installed state, executor availability,
dispatch, execute mode, retries, reserved data, candidate/promotion, Phase 8B,
demo/live, real-money, and trading remain locked.

Next gate after real successful DEC-398 evidence: deterministic immutable review
freeze.


## DEC-400 — EXP-062 workflow install-activation preflight proof freeze

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC REVIEW FREEZE / NO INSTALL OR DISPATCH

DEC-400 adds a deterministic source-only freeze for a valid DEC-399 review. It
preserves exact DEC-398 proof identities, artifact digest, DEC-397 preflight hashes,
source map, dormant-template identity, active workflow-absent state, and target
historical run #2 / attempt 1.

The freeze emits one canonical fingerprint for later concrete runtime binding. All
five source-only gates may remain true, but it adds no install, dispatch, or execute
surface and keeps reserved data plus all downstream trading paths locked.

Next gate after real DEC-398 evidence: concrete proof runtime-evidence binding.


## DEC-401 — EXP-062 workflow install-activation preflight proof runtime evidence freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED

DEC-401 binds the actual successful DEC-398 merged-main proof: head
`9dd433b406bef6dc8660d897ccab5bcb1b0da99b`, run `36579901387`, job
`109445012411`, artifact `11039017180`, artifact/ZIP SHA-256
`c19012d3e4fc794e40a930e0eac82d799773f6a9050bf56adc75a0b0f2245b85`,
raw preflight SHA-256
`8db03c11f255bcc724c4d7c18df7e5a8f539039032dbb5787291ca8810427116`,
and canonical SHA-256
`229fec80d76273f5320966acb63d0661ff7aa03c04ded8d953bb3e9e3f363ceb`.

DEC-401 re-runs DEC-399 review and DEC-400 deterministic freezing and requires
the exact DEC-400 fingerprint
`441c508902f816faee66c58768552a7d3ab05f0b145193a3e6349f18c9062808`.
DEC-334 terminal-review criteria remain pinned.

All five source-only gates remain true. The active executor workflow path remains
absent. Actual install authorization, installed state, executor availability,
historical dispatch, execute mode, reserved data, candidate/promotion, Phase 8B,
demo/live, real-money, and trading remain locked.

Next gate: source-only active executor workflow-install contract.


## DEC-402 — EXP-062 active workflow-install source contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY WORKFLOW-INSTALL CONTRACT / NO INSTALL OR DISPATCH

DEC-402 binds the concrete DEC-401 runtime-evidence freeze at fingerprint
`e2ee9e46bfe0a0fc132c5ce3f06bbad343ddb739ccaf0d22893886d1f41fbd2c`
without modifying the historical DEC-360 contract module.

The five predecessor source-only gates remain true. DEC-402 adds only the final
workflow-install source gate. The active executor workflow path remains absent.
Actual install authorization, installed state, executor availability, historical
dispatch, execute mode, reserved data, candidate/promotion, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: read-only current-main workflow-install source preflight.


## DEC-403 — EXP-062 workflow-install source preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN SOURCE PREFLIGHT / NO INSTALL OR DISPATCH

DEC-403 pins the exact DEC-402 workflow-install source contract, requires exact
current main, requires the active executor workflow path to remain absent, and
verifies the historical-result slot remains unused with target run #2 / attempt 1.

All six source-only gates remain true. The CLI exposes only `plan`. Actual
workflow-install authorization, installed state, executor availability, historical
dispatch, execute mode, reserved data, and all downstream trading paths remain
locked.

Next gate: repository-hosted read-only workflow-install source-preflight proof.


## DEC-404 — EXP-062 workflow-install source preflight proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / NO INSTALL OR DISPATCH

DEC-404 adds a first-run/attempt-1 push-to-main proof for DEC-403. It pins exact
DEC-402/403 source identities, the dormant executor template, active discovery
workflow, and pinned planning runtime.

The workflow uses only contents/actions read permissions, invokes only the DEC-403
`plan` surface, requires the active executor workflow path absent, and verifies all
six source-only gates with zero historical-result attempts and target run #2 /
attempt 1.

A successful run uploads only the workflow-install source-preflight JSON. No actual
installation, historical dispatch, execute mode, or downstream trading authority is
added.

Next gate after real successful runtime evidence: immutable proof review/freeze.


## DEC-407 — Recover failed DEC-404 workflow-install source-preflight proof

**Date:** 2026-09-29  
**Status:** EXPLICIT READ-ONLY RECOVERY / NO INSTALL OR DISPATCH

DEC-404 merged-main run #1 / attempt 1 (`36613664506`) is preserved as a real
failure. Its DEC-403 preflight step succeeded, but the wrapper verification failed
because it asserted the non-existent field
`install_source_slot_verified_available`. No immutable proof artifact was uploaded.

DEC-407 authorizes exactly workflow run #2 / attempt 1 of the same read-only proof
workflow. It pins failed run #1, head
`0db04ae49b3533778b08afa31e9ef9a26576b80c`, and job `109561121322` as
recovery provenance, removes only the invalid wrapper assertion, and keeps every
install, dispatch, reserved-data, and trading authority false.

Next gate after a successful recovery run: source-only review/freeze of the concrete
DEC-407 proof evidence.


## DEC-408 — Review successful DEC-407 recovery proof evidence

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RECOVERY REVIEW / NO INSTALL OR DISPATCH

DEC-408 reviews only a successful workflow run #2 / attempt 1 from the DEC-407
recovery workflow. It pins the corrected recovery workflow source, exact DEC-403
preflight/CLI, DEC-402 source contract, dormant executor template, and active
discovery workflow.

The failed DEC-404 run/job/head remain explicit provenance in the reviewed result.
No recovery review may reclassify run #1 as successful.

Actual workflow-install authorization, installed state, historical executor
availability, historical-result dispatch, execute mode, reserved data, and all
downstream trading authority remain false.

Next gate: deterministic immutable recovery-proof freeze.


## DEC-409 — Freeze reviewed DEC-407 recovery proof evidence

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC RECOVERY FREEZE / NO INSTALL OR DISPATCH

DEC-409 deterministically freezes a valid DEC-408 review. The frozen object keeps
failed DEC-404 run #1 and successful DEC-407 recovery run #2 in the same immutable
lineage and emits one canonical SHA-256 fingerprint.

No actual workflow-install authorization, installed state, executor availability,
historical dispatch, execute mode, reserved-data access, or trading authority is
introduced.

Next gate after real recovery evidence: concrete runtime-evidence binding.


## DEC-410 — Bind workflow-install source-preflight recovery runtime evidence

**Date:** 2026-09-29  
**Status:** CONCRETE RECOVERY-EVIDENCE BINDING / NO INSTALL OR DISPATCH

DEC-410 binds the real successful DEC-407 run #2 / attempt 1 evidence while
preserving the failed DEC-404 run #1 / attempt 1 provenance in the same immutable
lineage.

Bound recovery evidence:

- recovery head: `3ea7d3f7bfe8f1dfb3bbac612f74255da4fee432`;
- recovery run: `36616131587`;
- recovery job: `109569478100`;
- recovery artifact: `11054938805`;
- artifact/ZIP SHA-256:
  `e71ad4c19602bec2c3fa71ad6f76e41eadea53edd5ef310ea2110d251002da25`;
- raw DEC-403 preflight SHA-256:
  `aea9a6f510ee7f5147adb7aea4cba2e9662093dfc2a8465adc9b7aec61556639`;
- canonical DEC-403 preflight SHA-256:
  `4f96d9df7e7e4fba224a376b500539e4581bc34d852178f00796ee7be66f6c6b`;
- DEC-409 freeze fingerprint:
  `c0c04735c57638fde0a57122c240ea6c9aacd86fc7e43cdc532aaf8ba54cd9d3`.

The failed DEC-404 run remains recorded as run `36613664506`, head
`0db04ae49b3533778b08afa31e9ef9a26576b80c`, job `109561121322`, conclusion
`failure`.

All six source-only gates remain true. Actual workflow-install authorization,
installed state, executor availability, historical dispatch, execute mode,
reserved-data access, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: source-only final workflow-install authorization contract before install.


## DEC-411 — Final workflow-install authorization contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY FINAL AUTHORIZATION CONTRACT / NO INSTALL OR DISPATCH

DEC-411 consumes the concrete DEC-410 recovery runtime freeze and adds only a final
source-only workflow-install authorization contract.

It pins DEC-410 blob
`705c08d50a8dfcae5391a0b240d78fea5716a8de` and runtime fingerprint
`77fa5c98293226176d71a759af44f23e434987a57c66d343c13f7f727202e853`.

The six predecessor source-only gates remain true. DEC-411 adds the seventh
source-only gate:
`active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized=true`.

Actual workflow-install authorization remains false. The active workflow path
remains absent, and executor availability, historical dispatch, execute mode,
reserved-data access, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: read-only current-main final workflow-install authorization preflight.


## DEC-412 — Final workflow-install authorization preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH

DEC-412 pins the exact DEC-411 final authorization contract, requires exact current
main, requires the active executor workflow path to remain absent, and verifies the
historical-result slot remains unused with target run #2 / attempt 1.

All seven source-only gates remain true. The CLI exposes only `plan`. Actual
workflow-install authorization, installed state, executor availability, historical
dispatch, execute mode, reserved-data access, Phase 8B, demo/live, real-money, and
trading remain locked.

Next gate: repository-hosted read-only final-authorization preflight proof.


## DEC-413 — Final workflow-install authorization preflight proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / NO INSTALL OR DISPATCH

DEC-413 adds a first-run/attempt-1 push-to-main proof for DEC-412. It pins exact
DEC-411/412 source identities, the dormant executor template, active discovery
workflow, and pinned planning runtime.

The workflow uses only contents/actions read permissions, invokes only the DEC-412
`plan` surface, requires the active executor workflow path absent, and verifies all
seven source-only gates plus zero historical-result attempts.

A successful run uploads only the final-authorization-preflight JSON. No install,
historical dispatch, execute mode, or downstream trading authority is added.

Next gate after real successful runtime evidence: immutable proof review/freeze.


## DEC-414 — Final authorization preflight proof reviewer

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH

DEC-414 adds a strict reviewer for future successful DEC-413 merged-main proof
evidence. It pins the DEC-413 workflow, DEC-412 preflight/CLI, DEC-411 contract,
dormant executor template, and active discovery workflow.

A valid review requires run #1 / attempt 1 success, one successful proof job, one
non-expired artifact, exact DEC-412 preflight bytes, all seven source-only gates
true, and all actual install/dispatch/trading authority fields false.

Next gate after real DEC-413 evidence: deterministic immutable proof-review freeze.


## DEC-415 — Freeze reviewed final-authorization-preflight proof

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC REVIEW FREEZE / NO INSTALL OR DISPATCH

DEC-415 deterministically freezes a valid DEC-414 review. It preserves exact
DEC-413 proof identities, artifact digest, DEC-412 preflight hashes, source map,
active-workflow-absent state, all seven source-only gates, and target historical run
#2 / attempt 1.

The freeze emits one canonical fingerprint for later concrete runtime binding. It
adds no install, dispatch, or execute surface and keeps reserved data plus all
downstream trading paths locked.

Next gate after real DEC-413 evidence: concrete proof runtime-evidence binding.


## DEC-416 — EXP-062 final workflow-install authorization proof runtime evidence freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED

DEC-416 binds the actual successful DEC-413 merged-main proof: head
`8c7598348ade4ed8ea23458eef958add378c3e6d`, run `36622849087`, job
`109592333745`, artifact `11058592607`, artifact/ZIP SHA-256
`8303140ebc7a5e37922080051ab634bc7a6c9f13940d52f3802b1017fd658c7a`,
raw DEC-412 preflight SHA-256
`c265d3b6f1d9cc60946438d8fd7bd6d96ad4c976133293558ce0df548a09f730`,
and canonical SHA-256
`cca954fa188bf34ed308668563de0fa58226e50e242e65b0b33fac581dc5290c`.

DEC-416 re-runs DEC-414 review and DEC-415 deterministic freezing and requires
DEC-415 fingerprint
`4a71a6b29ccea4d5415ce64ca84fc0c43988a2daf98cbe912f4654868b907ffa`.
All seven source-only gates remain true.

Actual workflow-install authorization, installed state, executor availability,
historical dispatch, execute mode, reserved data, Phase 8B, demo/live, real-money,
and trading remain locked.

Next gate: source-only workflow-install action contract before repository mutation.


## DEC-417 — EXP-062 workflow-install action contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY INSTALL-ACTION CONTRACT / NO INSTALL OR DISPATCH

DEC-417 consumes the concrete DEC-416 final-authorization proof runtime freeze at
fingerprint
`3f90062e42cc36c61286b31fcd625a7e511140819c19f268e283be1807e2f0c7`
and adds only a source-level workflow-install action contract.

All seven predecessor source-only gates remain true. DEC-417 adds only
`active_one_shot_historical_executor_workflow_install_action_contract_source_authorized=true`.

The active executor workflow path remains absent. Actual workflow-install
authorization, installed state, executor availability, historical dispatch, execute
mode, reserved data, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate: read-only current-main workflow-install action preflight.


## DEC-418 — EXP-062 workflow-install action preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH

DEC-418 pins the exact DEC-417 install-action contract, requires exact current main,
requires the active executor workflow path to remain absent, and verifies the
historical-result slot remains unused with target run #2 / attempt 1.

All eight source-only gates remain true. The CLI exposes only `plan`. Actual
workflow-install authorization, installed state, executor availability, historical
dispatch, execute mode, reserved data, Phase 8B, demo/live, real-money, and trading
remain locked.

Next gate: repository-hosted read-only workflow-install action-preflight proof.


## DEC-419 — EXP-062 workflow-install action preflight proof

**Date:** 2026-09-29  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / NO INSTALL OR DISPATCH

DEC-419 adds a first-run/attempt-1 push-to-main proof for DEC-418. It pins exact
DEC-417/418 source identities, the dormant executor template, active discovery
workflow, and pinned planning runtime.

The workflow uses only contents/actions read permissions, invokes only the DEC-418
`plan` surface, requires the active executor workflow path absent, and verifies zero
historical-result attempts with target run #2 / attempt 1.

A successful run uploads only the action-preflight JSON. No workflow installation,
historical dispatch, execute mode, or downstream trading authority is added.

Next gate after real successful runtime evidence: immutable proof review/freeze.

## DEC-420 — EXP-062 workflow-install action-preflight proof reviewer

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RUNTIME-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH

DEC-420 adds a strict reviewer for successful DEC-419 merged-main proof evidence.
It pins the DEC-419 proof workflow, DEC-418 action preflight and CLI, DEC-417
install-action contract, dormant executor template, and active discovery workflow.

A valid review requires run #1 / attempt 1 success, exactly one successful proof
job, one non-expired artifact, exact DEC-418 preflight bytes, all eight source-only
gates true, and every actual install/dispatch/trading authority field false.

The successful DEC-419 proof exists at run `36634716243`, but the reviewer remains
fail-closed and derives trust from the evidence shape and pinned sources rather than
from that run ID alone.

No workflow installation, historical dispatch, execute mode, reserved-data access,
Phase 8B, demo/live, real-money, or trading authority is added.

Next gate: deterministic immutable proof-review freeze.


## DEC-421 — Freeze reviewed DEC-419 workflow-install action-preflight proof

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC REVIEW FREEZE / NO INSTALL OR DISPATCH

DEC-421 deterministically freezes a valid DEC-420 review. The frozen object keeps
exact DEC-419 proof run/job/artifact identities, artifact digest, raw/canonical
DEC-418 preflight hashes, DEC-418/417 identities, source map, active-workflow-absent
state, all eight source-only gates, and target historical run #2 / attempt 1.

The freeze emits one canonical fingerprint for later concrete runtime binding. It
does not create runtime evidence and cannot install the executor workflow or submit
historical discovery.

Actual workflow-install authorization, installed state, executor availability,
historical dispatch, execute mode, reserved-data access, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: concrete DEC-419 proof runtime-evidence binding before installation.

## DEC-422 — EXP-062 workflow-install action-preflight proof runtime evidence freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED

DEC-422 binds the successful DEC-419 merged-main proof: head
`51a49397e1eddc5b9e342d50b588f774e783a5e7`, run `36634716243`, job
`109632428957`, artifact `11063264562`, artifact/ZIP SHA-256
`1f06c7b589f46ca7a473bae5a0666b79b1b627dc6a8eaf85804211424e09f0be`,
raw DEC-418 preflight SHA-256
`567af303b2e37131b83c7f316424174632dd34854a38660f910c3072fbd893da`,
and canonical SHA-256
`66ebc48ff1e6ee8d24e19b0641c012244f93ddfb1e02baf343bec3df6a4f9c26`.

DEC-422 re-runs DEC-420 review and DEC-421 deterministic freezing and requires
DEC-421 fingerprint
`78bcceaf580672b97858ec972c590300316f8b7b369137ca96e957c39d1d9a5d`.
All eight source-only gates remain true.

Actual workflow-install authorization, installed state, executor availability,
historical dispatch, execute mode, reserved data, Phase 8B, demo/live, real-money,
and trading remain locked.

Next gate: a separate explicit repository-mutation authorization before the active
executor workflow can be installed.

## DEC-423 — EXP-062 active workflow repository-mutation authorization

**Date:** 2026-09-30  
**Status:** EXPLICIT INSTALL MUTATION AUTHORIZED / WORKFLOW STILL ABSENT

DEC-423 records explicit operator authorization to perform the repository mutation
that installs the active one-shot historical executor workflow.

The decision pins DEC-422 runtime-freeze blob
`65108857f15b6ab084bbb5f8a0358b7bbd4aaa59` and fingerprint
`cce3b8900f630ddf0e651af10ceba39311f1e00485f6bca99af28252195aae0f`,
plus the exact dormant executor template blob.

DEC-423 changes only
`historical_executor_workflow_install_authorized=true`. The active workflow path
remains absent under this decision. Installed state, executor availability,
historical dispatch, execute mode, reserved data, Phase 8B, demo/live, real-money,
and trading remain locked.

Next gate: active workflow installation as a repository mutation. No historical
dispatch is authorized by DEC-423.

## DEC-424 — EXP-062 active one-shot historical executor workflow installation

**Date:** 2026-09-30  
**Status:** ACTIVE WORKFLOW INSTALLED / DISPATCH STILL LOCKED

DEC-424 performs the repository mutation explicitly authorized by DEC-423 and
installs `.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`.

The installed workflow is byte-for-byte identical to dormant template blob
`51ce87584369be957482460d81649adb1cb9f05d`, and DEC-424 pins DEC-423 source
blob `df6a80d1f6ee6315f3e3095433ed6704666ccd33`.

Workflow-install authorization, installed state, and executor availability are now
true. Historical-result dispatch authorization and execute mode remain false.
Rerun/retry/replacement, reserved data, Phase 8B, demo/live, real-money, and trading
remain locked.

The installed workflow is manual-only via `workflow_dispatch`; DEC-424 does not
run it.

Next gate: separate explicit one-shot executor dispatch authorization before the
installed workflow may be triggered.

## DEC-425 — EXP-062 installed executor dispatch preflight

**Date:** 2026-09-30  
**Status:** READ-ONLY CURRENT-MAIN DISPATCH PREFLIGHT / NO RUN

DEC-425 adds a read-only current-main preflight for the installed one-shot
historical executor.

It pins DEC-424 receipt blob
`27e714620018413a09ceaf287fb7943bf884ee49` and the active executor workflow
blob `51ce87584369be957482460d81649adb1cb9f05d`.

A valid preflight requires the installed workflow to remain exact, zero executor
workflow runs, zero historical-result attempts, an unused historical slot, and
target run #2 / attempt 1.

Workflow installation and executor availability remain true. Historical dispatch,
execute mode, rerun/retry/replacement, reserved data, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: separate explicit one-shot executor dispatch authorization before run.

## DEC-426 — EXP-062 installed executor dispatch-preflight proof

**Date:** 2026-09-30  
**Status:** REPOSITORY-HOSTED READ-ONLY PREFLIGHT PROOF / NO RUN

DEC-426 adds a push-to-main, first-run/attempt-1 proof of DEC-425.

It pins DEC-424 receipt blob, DEC-425 preflight/CLI blobs, the active executor
workflow blob, the discovery workflow, and the pinned planning runtime. The proof
has contents/actions read permissions only and no manual dispatch trigger.

A valid run requires the active executor to remain installed, zero executor runs,
zero historical-result attempts, an unused historical slot, and target run #2 /
attempt 1. All dispatch, execute, reserved-data, and trading authorities remain
false.

Next gate after real successful merged-main evidence: strict proof review and
deterministic freeze.

## DEC-427 — EXP-062 installed executor dispatch-preflight proof review

**Date:** 2026-09-30  
**Status:** STRICT RUNTIME-EVIDENCE REVIEW / DISPATCH STILL LOCKED

DEC-427 reviews the successful merged-main DEC-426 proof at head
`f2b2a5629013749b74306201aac29d14b7124cd3`, run `36688457000`, job
`109799712311`, artifact `11085100742`.

The artifact/ZIP SHA-256 is
`a335347c3e428f8eff653bfe4a8e022b0ed939c188634a5236f2354edaff9ac9`.
The raw DEC-425 preflight SHA-256 is
`017f45bcec6633006b3d78c76f09890da0417fbd79f904743de659e614d73974`,
and canonical SHA-256 is
`26958a21f832609d2dfc57347f6637c35aaa2923c36ec14a40f9573e6a77cb02`.

The review requires exact source identities, installed executor state true, zero
executor runs, zero historical-result attempts, and all dispatch/execute/reserved-
data/trading authorities false.

Next gate: deterministic immutable proof freeze.


## DEC-428 — Freeze reviewed DEC-426 dispatch-preflight proof

**Date:** 2026-09-30  
**Status:** DETERMINISTIC PROOF FREEZE / DISPATCH STILL LOCKED

DEC-428 deterministically freezes a valid DEC-427 review, preserving exact
run/job/artifact identities, artifact/preflight hashes, source map, installed
executor state, zero executor runs, unused historical slot, and target run #2 /
attempt 1.

It emits a canonical freeze fingerprint for later concrete runtime binding.

Historical-result dispatch, execute mode, rerun/retry/replacement, reserved-data
access, Phase 8B, demo/live, real-money, and trading remain false.

Next gate: concrete DEC-426 runtime-evidence binding before any dispatch
authorization.

## DEC-429 — EXP-062 dispatch-preflight proof runtime evidence binding

**Date:** 2026-09-30  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / DISPATCH STILL LOCKED

DEC-429 binds the successful DEC-426 merged-main proof at head
`f2b2a5629013749b74306201aac29d14b7124cd3`, run `36688457000`, job
`109799712311`, and artifact `11085100742`.

It verifies artifact/ZIP SHA-256
`a335347c3e428f8eff653bfe4a8e022b0ed939c188634a5236f2354edaff9ac9`,
raw DEC-425 SHA-256
`017f45bcec6633006b3d78c76f09890da0417fbd79f904743de659e614d73974`,
canonical DEC-425 SHA-256
`26958a21f832609d2dfc57347f6637c35aaa2923c36ec14a40f9573e6a77cb02`,
and DEC-428 fingerprint
`4a9a7b3e931fd12585638430afbc38f823b5016ecc11f9f4fe7dd3533aa82454`.

The executor remains installed and available with zero executor runs. Historical
dispatch, execute mode, reserved data, Phase 8B, demo/live, real-money, and trading
remain locked.

Next gate: separate explicit one-shot executor dispatch authorization before run.

## DEC-430 — EXP-062 one-shot executor dispatch authorization

**Date:** 2026-09-30  
**Status:** ONE-SHOT DISPATCH AUTHORIZED / RUN NOT STARTED

DEC-430 records explicit operator authorization for exactly one invocation of the
installed historical executor.

It pins DEC-429 runtime-freeze blob
`98fbb04a78efeef0a9a1fc919b5e5d61093c09de`, DEC-429 fingerprint
`a561a4a66111c5c2edc3183e68a978b01ead42f9b8f8c8c061244b50fc751dac`,
and active executor workflow blob
`51ce87584369be957482460d81649adb1cb9f05d`.

The authorized scope is executor run #1 / attempt 1 producing historical result run
#2 / attempt 1. Rerun, retry, and replacement remain forbidden.

This decision authorizes the one-shot dispatch but does not trigger it. General
execute mode, reserved data, Phase 8B, demo/live, real-money, and trading remain
locked.

Next gate: read-only current-main dispatch-action preflight before run.

## DEC-431 — EXP-062 one-shot executor dispatch action preflight

**Date:** 2026-09-30  
**Status:** READ-ONLY ACTION PREFLIGHT / AUTHORIZED RUN NOT STARTED

DEC-431 adds a current-main, plan-only action preflight for DEC-430.

It pins DEC-430 and the exact active executor workflow, requires zero executor runs,
zero historical-result attempts, an unused historical slot, executor run #1 /
attempt 1, and historical result run #2 / attempt 1.

The future executor command is evidence only. No workflow is triggered by DEC-431.
Rerun/retry/replacement, reserved data, and all trading authority remain locked.

Next gate: repository-hosted read-only action-preflight proof.

## DEC-432 — EXP-062 one-shot executor dispatch action-preflight proof

**Date:** 2026-09-30  
**Status:** REPOSITORY-HOSTED READ-ONLY PROOF / AUTHORIZED RUN NOT STARTED

DEC-432 adds a push-to-main, first-run/attempt-1 read-only proof of DEC-431.

It pins DEC-430/431 and the exact executor/discovery workflow sources, requires zero
executor runs and zero historical-result attempts, and verifies the one-shot
authorization remains exact.

The proof has contents/actions read permissions only and never submits the executor
workflow.

Next gate after a successful merged-main proof: strict evidence review and
deterministic freeze before run.

## DEC-433 — EXP-062 one-shot executor dispatch action-preflight proof review

**Date:** 2026-09-30  
**Status:** STRICT PROOF REVIEW / AUTHORIZED RUN NOT STARTED

DEC-433 strictly reviews future successful merged-main DEC-432 evidence. It requires
exact run/job/artifact identity, exact DEC-431 preflight bytes, zero executor runs,
zero historical-result attempts, and exact one-shot authorization.

All rerun/retry/replacement and downstream trading authorities remain false.

Next gate: deterministic proof freeze.


## DEC-434 — Freeze reviewed DEC-432 action-preflight proof

**Date:** 2026-09-30  
**Status:** DETERMINISTIC PROOF FREEZE / AUTHORIZED RUN NOT STARTED

DEC-434 deterministically freezes a valid DEC-433 review and emits a canonical
fingerprint.

The one-shot authorization remains true, but executor run count and
historical-result attempt count remain zero. No execution occurs.

Next gate: concrete DEC-432 runtime-evidence binding before run.


## DEC-435 — EXP-062 one-shot executor dispatch action-preflight proof runtime evidence binding

**Date:** 2026-09-30  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / AUTHORIZED RUN NOT STARTED

The successful merged-main DEC-432 proof is now concretely bound through the
DEC-433 strict review and DEC-434 deterministic freeze.

Bound evidence: head `7b4f9fe713e546efdb445a8f4e9982e1b8f219aa`, run
`36695220474`, job `109821445046`, artifact `11087821283`, artifact/ZIP
SHA-256 `16984f3cac059bb725c29953466131ffb710bbfc621ec8f35428bf2036e8cd63`,
raw preflight SHA-256
`fd512c6dc5c03248e0cd75b328ed32a81dc76564b94ab85436d6f5d8764746d9`,
canonical preflight SHA-256
`33daef766b6a2e91b20adef386d2fc44f3b2aff03eeb3a08792f1e49da2d667d`,
and DEC-434 freeze fingerprint
`9a59f7329cb5abe0786511b91d7b6d8e33d4df8f027271a7387830f8fbf11c8a`.

The explicit DEC-430 authorization still covers only executor run #1 / attempt 1,
targeting historical result run #2 / attempt 1. Executor run count and historical
result attempt count remain zero. General execute mode, rerun/retry/replacement,
reserved data, Phase 8B, demo/live, real-money, and trading remain locked.

Next safe gate: submit only the already-authorized executor run #1 / attempt 1.


## DEC-436 — Recover failed one-shot historical executor dispatch

**Date:** 2026-09-30  
**Status:** EXPLICIT FAIL-CLOSED RECOVERY AUTHORIZATION / HISTORICAL RESULT NOT STARTED

Original executor run `36702494195` failed at the exact-run guard because GitHub
assigned run #2 / attempt 1 while DEC-430/435 authorized run #1 / attempt 1.

The failed run is preserved at head
`59b55d519449e20cf396d70ed9a5722b989d933a`, job `109844958600`,
conclusion `failure`. The historical dispatch, receipt, and artifact steps were
all skipped, so discovery run #2 remains unused.

DEC-436 leaves the original executor workflow byte-for-byte frozen and introduces a
separate manual-only recovery workflow with its own run counter. Only recovery run
#1 / attempt 1 may proceed, and only after re-verifying the failed provenance,
DEC-435 source identity, unchanged executor/discovery workflow blobs, and the empty
historical-result slot.

Generic rerun, retry, and replacement authorization remain false. General execute
mode, reserved data, Phase 8B, demo/live, real-money, and trading remain locked.

Next gate after green merge: manually submit exactly the DEC-436 recovery workflow
run #1 / attempt 1. Do not rerun the failed original executor.


## DEC-437 — Review successful DEC-436 recovery receipt

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY RECOVERY RECEIPT REVIEW

DEC-437 adds a strict reviewer for a future successful DEC-436 recovery workflow
run #1 / attempt 1.

The reviewer pins the DEC-436 recovery workflow and authorization, the unchanged
original executor workflow, and the active discovery workflow. It requires one
successful recovery job and one non-expired recovery receipt artifact.

The receipt must preserve failed original executor run `36702494195` / job
`109844958600`, bind discovery run #2 / attempt 1 to the exact recovery head, and
keep rerun/retry/replacement, reserved-data, Phase 8B, demo/live, real-money, and
trading authority false.

Next gate: deterministic recovery receipt freeze.

## DEC-438 — Freeze reviewed DEC-436 recovery receipt

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY DETERMINISTIC RECOVERY RECEIPT FREEZE

DEC-438 deterministically freezes a valid DEC-437 review and emits one canonical
SHA-256 fingerprint.

The freeze preserves exact recovery run/job/artifact identities, raw/canonical
receipt hashes, failed original executor provenance, discovery run #2 / attempt 1,
and exact recovery/discovery head equality.

It adds no dispatch or execute surface. All broad authority locks remain false.

Next gate after a real successful DEC-436 recovery: concrete runtime-evidence
binding while historical discovery run #2 completes.


## DEC-439 — Recover failed DEC-436 executor recovery with pinned runtime

**Date:** 2026-09-30  
**Status:** EXPLICIT SECOND FAIL-CLOSED RECOVERY AUTHORIZATION / HISTORICAL RESULT NOT STARTED

DEC-436 recovery run `36707978889` / job `109862691026` is preserved as a real
failure. It was exact run #1 / attempt 1, passed its run/provenance/source guards,
then failed before historical-slot inspection because importing
`fmp.discovery` raised `ModuleNotFoundError: No module named 'polars'`.

No historical dispatch occurred and no receipt artifact was created. Discovery
run #2 remains unused.

DEC-439 introduces a separate manual-only recovery-v2 workflow with a fresh
run #1 / attempt 1. It installs the exact pinned runtime from
`requirements/exp061-discovery-run.txt` before importing FMP, pins both prior
failures plus all relevant workflow/source identities, rechecks the empty discovery
slot, and only then may dispatch discovery run #2 / attempt 1 on the same head.

Generic rerun/retry/replacement, reserved data, Phase 8B, demo/live, real-money,
and trading authority remain false.

Next gate after green merge: one manual DEC-439 recovery-v2 run #1 / attempt 1.

## DEC-440 — Review successful EXP-062 historical result content

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY ACTUAL RESULT REVIEW / NO DOWNSTREAM AUTHORIZATION

DEC-440 binds the sole successful EXP-062 historical workflow result at run
`36714210992`, run #2 / attempt 1, head
`013395092804de6b0ef51537081ab8443b8b91be`.

The run must first satisfy the frozen DEC-334 terminal contract as an exact
20-job / 20-artifact success. DEC-440 then pins aggregate artifact
`11096592737`, artifact digest
`sha256:077535bc6e9d9a1d6e8693f873b7552cf8028d793ef79eab175dbbd9970430bc`,
exact aggregate JSON SHA-256
`bfdf9787e9ee32c30ff29aa70594d7404bc7fc2cb573a60068802d2aacbaa6f3`,
and aggregate evidence fingerprint
`b8019226fb7fce14c6711834fe16cdbb52795d9ca8996b1ed98ede7ecfba9506`.

The reviewed aggregate contains 18/18 verified cells, 67 discovery-shortlist
entries, 11 confirmation-frozen candidates, and 0 validation-accepted candidates.
Its evidence label remains `RETROSPECTIVE_ALREADY_SEEN`, `untouched_oos=false`,
and reserved robustness data remains unopened.

The historical-result slot is permanently consumed. Rerun/retry/replacement,
reserved-data access, candidate compilation, promotion, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: deterministic immutable DEC-441 historical-result review freeze.

## DEC-441 — Freeze reviewed EXP-062 historical result

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY DETERMINISTIC RESULT FREEZE / NO DOWNSTREAM AUTHORIZATION

DEC-441 deterministically freezes the DEC-440 reviewed EXP-062 historical result.
It pins DEC-440 source blob
`17facb0f77f6419de5f8a74f80019bb7289fe984` and preserves the exact
historical run `36714210992`, run #2 / attempt 1, head
`013395092804de6b0ef51537081ab8443b8b91be`.

The freeze also preserves aggregate artifact `11096592737`, artifact digest
`sha256:077535bc6e9d9a1d6e8693f873b7552cf8028d793ef79eab175dbbd9970430bc`,
aggregate JSON SHA-256
`bfdf9787e9ee32c30ff29aa70594d7404bc7fc2cb573a60068802d2aacbaa6f3`,
aggregate evidence fingerprint
`b8019226fb7fce14c6711834fe16cdbb52795d9ca8996b1ed98ede7ecfba9506`,
and the reviewed 18 verified cells / 67 shortlist / 11 confirmation-frozen /
0 validation-accepted counts.

The canonical frozen object receives one `freeze_fingerprint_sha256` for any
later post-EXP-062 research-direction decision.

The historical-result slot remains consumed. Rerun/retry/replacement,
reserved-data access, candidate compilation, promotion, Phase 8B, demo/live,
real-money, and trading remain locked.

Next gate: a separate explicit post-EXP-062 research-direction decision. Zero
validation-accepted candidates do not themselves authorize threshold changes,
additional mining, Phase 8B, or promotion.

## DEC-442 — Diagnose EXP-062 post-result validation failure

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY POST-RESULT DIAGNOSTIC / NO SUCCESSOR AUTHORIZATION

DEC-442 binds the merged DEC-441 freeze at
`d5e8ad7cd98ec1511742d1b266e6779852155c96`, source blob
`ae0353fce77e9ff03536f2323820804dbda7241c`, historical run
`36714210992`, historical head
`013395092804de6b0ef51537081ab8443b8b91be`, and aggregate evidence
fingerprint
`b8019226fb7fce14c6711834fe16cdbb52795d9ca8996b1ed98ede7ecfba9506`.

All 11 confirmation-frozen patterns are 240-minute-horizon patterns across EURUSD
and GBPUSD. There are no USDJPY confirmation survivors and no 60-minute-horizon
confirmation survivors.

All 11 still satisfy the frozen confirmation gate. In the 2019-2022 validation
window, all 11 have non-positive aggregate mean net pips at the 0.5-pip cost
assumption and all 11 have fewer than the required three positive validation years.
Only one candidate, GBPUSD 1h / 240m, additionally falls below the minimum
per-year support requirement, with minimum yearly support 29 versus the frozen
minimum 40.

DEC-442 therefore classifies the evidence as
`CONFIRMATION_EDGE_DID_NOT_PERSIST_THROUGH_2019_2022_VALIDATION`.
The dominant rejection is temporal/economic non-persistence rather than a broad
sample-size shortage or a runtime/adapter failure.

Rerun/retry/replacement, threshold relaxation, pattern redefinition, reserved-data
access, successor protocol source opening, successor execution, candidate
compilation, promotion, Phase 8B, demo/live, real-money, and trading remain false.

Next gate: a separate explicit post-EXP-062 research-direction decision after this
diagnostic is merged.

## DEC-443 — Open EXP-063 persistence-first research direction

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY RESEARCH-DIRECTION DECISION / SUCCESSOR EXECUTION LOCKED

DEC-443 binds merged DEC-442 commit
`4e9bc6ea384f4bcf40444567a9585be24787d71b` and DEC-442 diagnostic source blob
`2eac2cd32edf151a3eeca806a65a34af914cbea4`.

DEC-442 showed that all 11 EXP-062 confirmation-frozen patterns later failed the
2019-2022 validation gate: all 11 had non-positive aggregate validation mean at
0.5-pip cost and fewer than three positive validation years. Only one additionally
failed minimum yearly support. The evidence therefore supports temporal/economic
non-persistence rather than broad sample-size shortage or a runtime/adapter defect.

DEC-443 opens new successor identity `EXP-20260930-063` for source design only.
The successor direction is persistence-first: temporal persistence and retrospective
year balance must become first-class selection properties, and one strong period
must not dominate selection. The exact persistence statistic and exact internal
chronology are deferred to a separate protocol decision.

The V1 universe remains bounded to EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m.
DEC-443 authorizes no new feature, symbol, timeframe, horizon, threshold relaxation,
or EXP-062 pattern rescue.

Because 2019-2022 outcomes were inspected and directly informed DEC-442/443,
2015-2022 is now `ALREADY_SEEN_DESIGN_EVIDENCE` for EXP-063 and 2019-2022 may not
be described as fresh validation. The reserved 2023-01-01 through 2026-08-20 block
remains closed.

EXP-062 rerun/retry/replacement, reserved-data access, successor execution,
historical result production, candidate compilation, promotion, Phase 8B,
demo/live, real-money, and trading remain false.

Next gate: a source-only EXP-063 persistence-first protocol freezing the exact
retrospective chronology, persistence metric, ranking/gating semantics, search
budget, duplicate handling, and reserved-block boundary.

## DEC-444 — Freeze EXP-063 persistence-first pattern protocol

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY PROTOCOL / HISTORICAL EXECUTION LOCKED

DEC-444 binds merged DEC-443 commit
`2ff960cf51d614c8c446d5f7f4c85569312bfec8`, DEC-443 direction source blob
`e32fe0da11e01e463a8c5110201b0b1ed223f85e`, and the frozen EXP-061/062 base
pattern-protocol blob `63b3f0121d6a50eb9e8e62ab666d70eb91791621`.

EXP-063 preserves the exact EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m universe,
the same 20 leakage-safe continuous features, five session states, one/two-dimension
patterns, LONG/SHORT directions, and the exact 74,700 maximum directional-hypothesis
search volume. No new feature, pair, timeframe, horizon, or third predicate is
authorized.

State cutpoints remain calibrated from 2015-2017 only and are then applied unchanged
through 2022. All eight years 2015-2022 are already-seen design evidence and are
evaluated as equal-status annual persistence slices. The fixed two-year blocks are
2015-2016, 2017-2018, 2019-2020, and 2021-2022. The 2023-01-01 through 2026-08-20
robustness block remains closed.

The persistence gate requires total support >=600, support >=75 in every year,
aggregate 0.5-pip mean >=0.25, positive aggregate 1.0-pip stress mean, at least
6 of 8 positive annual 0.5-pip means, positive arithmetic mean across the four
weakest annual means, and a positive equal-year mean in every fixed two-year block.

Passing patterns rank persistence-first by lower-half annual mean, minimum two-year
block mean, positive-year count, worst annual mean, aggregate 0.5-pip mean,
aggregate 1.0-pip mean, total support, pattern depth, and fingerprint. Existing
same-cell/horizon/direction Jaccard >=0.90 deduplication is retained. The shortlist
remains capped at 10 per cell/horizon / 180 global, and the frozen set remains
capped at 3 per cell/horizon / 54 global.

A frozen EXP-063 result is
`RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED`; it is not an
executable strategy or validated candidate.

Source access, historical execution/result production, reserved-data access,
candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading
remain false.

Next gate: a deterministic source-only EXP-063 in-memory miner core implementing
this exact protocol and proving 2023-2026 rows cannot influence results.

## DEC-445 — Implement EXP-063 deterministic persistence miner core

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY CORE / HISTORICAL EXECUTION LOCKED

DEC-445 binds merged DEC-444 commit
`86d16d06444e56a1c6615f18e2906e8ecdaadbdf`, DEC-444 protocol source blob
`2c781dd2811b66d2d88f008007bf5c8bcf99f14f`, and predecessor deterministic
miner blob `495a67699eb5014e52129f0238a2737049fe38e6`.

The new source
`src/fmp/discovery/exp063_persistence_miner.py` at blob
`40c49a372b35dbc113dbfb71374b1ae5fc7acc45` reuses the frozen feature/outcome
contracts, 2015-2017 state calibration, state encoder, and one/two-dimension bounded
enumerator while applying the DEC-444 persistence gate across the already-seen
2015-2022 design years.

For each pattern, the core forms one 2015-2022 event set and evaluates LONG/SHORT
independently. Passing hypotheses retain exact annual support/net-pip statistics,
lower-half annual mean, fixed two-year-block means, and all other DEC-444
persistence metrics. Ranking follows the exact DEC-444 nine-field order, then
same-direction event-Jaccard >=0.90 deduplication. The shortlist remains capped at
10 per cell/horizon and frozen output at 3 per cell/horizon.

Rows whose fixed horizon crosses an annual boundary are purged. Rows dated
2023-2026 never enter event sets, scoring, ranking, deduplication, shortlist, or
frozen output. Focused tests inject catastrophic reserved-period rows and require
the entire in-memory result to remain exactly unchanged.

Every frozen output remains
`RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED`. It is not an
executable or independently validated strategy.

Source-data access, historical execution/result production, reserved robustness
access, candidate compilation, promotion, Phase 8B, demo/live, real-money, and
trading remain false.

Next gate: a separate source-only EXP-063 artifact/evidence contract bound to this
exact deterministic core, with historical execution still closed.

## DEC-446 — Freeze EXP-063 artifact/evidence contract

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY EVIDENCE CONTRACT / HISTORICAL EXECUTION LOCKED

DEC-446 binds merged DEC-445 commit
`f13988c78470ae00e3c3b9944a774bf2fed42f59`, DEC-445 miner source blob
`40c49a372b35dbc113dbfb71374b1ae5fc7acc45`, and DEC-444 protocol source blob
`2c781dd2811b66d2d88f008007bf5c8bcf99f14f`.

The new contract source
`src/fmp/discovery/exp063_evidence_contract.py` at blob
`e8614beb156d24584b82611db47afb8c00ece71c` defines deterministic canonical
cell and aggregate evidence for EXP-063. Compilation is self-validating: both cell
and aggregate objects are passed through the same fail-closed semantic validators
before being returned.

Each cell evidence object binds the exact code commit, processed/feature/outcome
manifest SHA-256 identities, feature/outcome evidence fingerprints, state-model
cutpoints, bounded search counts, complete persistence shortlist, exact first-up-to-
three frozen fingerprint inventory, and all DEC-444 persistence statistics. The
validator reconstructs all eight annual 2015-2022 stats, re-runs the DEC-444
persistence gate, recomputes metrics, EXP-063 pattern fingerprints, ranking keys,
rank order, and frozen inventory.

Aggregate evidence requires exactly the 18
EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m cells. It validates every cell first,
requires one code commit, exact Phase 2 symbol source manifests, equal
feature/outcome manifest pairs across horizons for each symbol/timeframe, singular
feature/outcome evidence fingerprints, sorted unique cells, global shortlist <=180,
and global frozen count <=54.

EXP-063 aggregate evidence intentionally contains no validation-accepted count.
Every frozen object remains
`RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED`. Evidence remains
`RETROSPECTIVE_ALREADY_SEEN`, `untouched_oos=false`, and reserved robustness
remains unopened.

Source-data access, historical execution/result authorization, reserved robustness
access, candidate compilation, promotion, Phase 8B, demo/live, real-money, and
trading remain false.

Focused tests are `tests/test_phase8a_exp063_evidence_contract.py` at blob `18785c0710d61d21afba6c7d266862966e8f937d`.\n\nNext gate: a separate source-only EXP-063 workflow/CLI/runtime source freeze;
dispatch and any historical execution slot remain closed.

## DEC-447 — Install locked EXP-063 runtime wiring

**Date:** 2026-09-30  
**Status:** ACTIVE WORKFLOW INSTALLED / HISTORICAL EXECUTION LOCKED

DEC-447 consolidates the EXP-063 run contract, runtime CLI, dormant workflow source,
and locked active-workflow installation into one source-only milestone.

It binds DEC-446 evidence contract blob
`e8614beb156d24584b82611db47afb8c00ece71c`, DEC-445 persistence miner blob
`40c49a372b35dbc113dbfb71374b1ae5fc7acc45`, DEC-444 protocol blob
`2c781dd2811b66d2d88f008007bf5c8bcf99f14f`, EXP-062 repaired adapter blob
`491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`, EXP-062 source-contract blob
`e20ded13de24f99e8ea6cfdc6cb0d1309d984f24`, EXP-061 range-limited loader blob
`df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`, and runtime requirements blob
`1ff32214dee10d877a067e750cd69ffad96d5fe5`.

Runtime source is
`src/fmp/discovery/exp063_runtime_source.py` blob
`6e7804a037fd386016fd45145be73b8dc00563f2`. CLI is
`scripts/phase8a_exp063.py` blob
`1b969668f79b37bc68f701da103b3a2bb53b13c1`. The dormant template and active
workflow are byte-identical at blob
`1038beb4b704ddead4e5841a6f799858732189e6`. Focused tests are blob
`e75e30c648f166862e555422ac76c6d9033485ec`.

The installed workflow `phase8a-exp063-persistence` has exactly 20 jobs and a
20-artifact success shape: one preflight, 18 explicit
EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m cells, and one aggregate.

EXP-063 reuses only the exact frozen EXP-044 source lineage already reviewed for
EXP-061/062 and explicitly inherits the EXP-062 non-finite→null feature repair. If
a later decision authorizes execution, each cell is wired as frozen loader ->
repaired adapter -> DEC-445 persistence miner -> DEC-446 evidence contract.

Historical execution remains hard-locked. Preflight may read and validate only the
exact source-run metadata, after which
`python scripts/phase8a_exp063.py require-execution` raises before any cell job can
download historical feature/outcome artifacts. The CLI independently gates cell
artifact reads and aggregate result reads.

Workflow source and installation state are true. Workflow-dispatch authorization,
historical execution/result authorization, rerun/retry/replacement, reserved
2023-2026 access, candidate compilation, promotion, Phase 8B, demo/live,
real-money, and trading remain false.

Next gate: one explicit EXP-063 one-shot historical execution authorization bound to
the exact merged DEC-447 runtime. DEC-447 itself provides no execute mode and does
not dispatch EXP-063.

## DEC-448 — Open EXP-063 one-shot historical-result slot

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY ONE-SHOT SLOT AUTHORIZATION / DISPATCH LOCKED

DEC-448 binds merged DEC-447 commit
`cbd7f5adce4cae062ba427bf61c3239e77dc5b72`, runtime source blob
`6e7804a037fd386016fd45145be73b8dc00563f2`, active workflow blob
`1038beb4b704ddead4e5841a6f799858732189e6`, CLI blob
`1b969668f79b37bc68f701da103b3a2bb53b13c1`, DEC-446 evidence-contract blob
`e8614beb156d24584b82611db47afb8c00ece71c`, DEC-445 miner blob
`40c49a372b35dbc113dbfb71374b1ae5fc7acc45`, and DEC-444 protocol blob
`2c781dd2811b66d2d88f008007bf5c8bcf99f14f`.

The authorization source
`src/fmp/discovery/exp063_historical_run_authorization.py` at blob
`f6070b1ecc8951338767b24dac1f0ff9ec7a24ae` opens only the outer
`historical_result_slot_source_authorized=true` state. Focused tests are
`tests/test_phase8a_exp063_historical_run_authorization.py` at blob
`5642d7f91092e7f23f271444df5a40b25d8a1db7`.

At DEC-448 creation, the installed `phase8a-exp063-persistence` workflow has zero
manual-main runs. Therefore the first future matching `workflow_dispatch` run is
the one and only historical-result attempt. The slot is consumed immediately when
that run exists, including while queued or running and regardless of terminal
success/failure/cancellation.

The expected first run remains run number 1, attempt 1. A second matching run or any
GitHub rerun with `run_attempt != 1` is invalid. Failure does not authorize rerun,
retry, or replacement.

Historical-result dispatch, historical execution/result production, reserved
2023-2026 robustness access, candidate compilation, promotion, Phase 8B, demo/live,
real-money, and trading remain false.

Next gate: a separate bounded runtime activation / one-shot dispatch decision that
must reverify the exact merged runtime and the still-unused slot immediately before
any dispatch. DEC-448 itself provides no dispatch or execution path.

## DEC-449 — Activate EXP-063 one-shot historical runtime

**Date:** 2026-09-30  
**Status:** ONE-SHOT HISTORICAL RUNTIME AUTHORIZED / NOT DISPATCHED

DEC-449 is the final pre-run activation for EXP-063. It binds merged DEC-448 commit
`ee38ea4224345e2ed0a2c4a4baa9913b0589c8a0`, the DEC-448 one-shot slot source
blob `f6070b1ecc8951338767b24dac1f0ff9ec7a24ae`, unchanged active workflow blob
`1038beb4b704ddead4e5841a6f799858732189e6`, DEC-446 evidence-contract blob
`e8614beb156d24584b82611db47afb8c00ece71c`, DEC-445 miner blob
`40c49a372b35dbc113dbfb71374b1ae5fc7acc45`, DEC-444 protocol blob
`2c781dd2811b66d2d88f008007bf5c8bcf99f14f`, repaired-adapter blob
`491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`, loader blob
`df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`, and runtime requirements blob
`1ff32214dee10d877a067e750cd69ffad96d5fe5`.

The live EXP-063 CLI is activated at blob
`1ed4616af6de156fc1f832bf63b1a97c4caac8e9`. Runtime authorization source is
`src/fmp/discovery/exp063_historical_execution_authorization.py` at blob
`fd87ab32eafa43e2cffb305680a1747314f4f3e5`. The read-only dispatch operator is
`src/fmp/discovery/exp063_historical_dispatch_operator.py` at blob
`e05b502a495451efb1678034a0405855f4d199e8`. Focused activation tests are
`tests/test_phase8a_exp063_historical_runtime_activation.py` at blob
`ba2b3ebb81bd83accb047b29798ef757eb257800`.

DEC-447 and DEC-448 remain immutable pre-activation records. Their frozen modules
continue to report their historical locked state; DEC-449 becomes the live-current
CLI/runtime authority. The active workflow itself remains byte-identical to the
DEC-447 frozen workflow.

Runtime authorization now requires GitHub Actions, repository `Dtwosam/FMP`,
workflow `phase8a-exp063-persistence`, event `workflow_dispatch`, ref
`refs/heads/main`, run number 1, run attempt 1, a positive run id, and exact
`GITHUB_SHA == code_commit`, plus all pinned source blobs. Run number 2, attempt 2,
local execution, repository/workflow/ref drift, or SHA drift fail closed.

Historical-result dispatch, historical execution, and historical result production
are now authorized for this single slot. Rerun, retry, replacement, reserved
2023-2026 access, candidate compilation, promotion, Phase 8B, demo/live orders,
real-money action, and trading remain false.

The DEC-449 dispatch operator is read-only and has no execute mode. It emits
`gh workflow run phase8a-exp063-persistence.yml --ref main` only when current main
matches the expected head and the DEC-448 run inventory is still empty. Once any
matching run exists, no second command is emitted and the slot is permanently
consumed.

DEC-449 itself does not dispatch EXP-063. After merge, dispatch requires an immediate
read-only main-head and run-inventory check. The first created run consumes the slot
regardless of success, failure, or cancellation.

Next gate: one explicit manual dispatch of the authorized EXP-063 workflow, followed
by immutable run/result review. No rerun/retry/replacement is authorized.

## DEC-450 — Freeze EXP-063 historical result: no persistence hypotheses

**Date:** 2026-09-30  
**Status:** HISTORICAL RESULT REVIEWED AND FROZEN / NO PERSISTENCE HYPOTHESES

DEC-450 freezes the only EXP-063 historical run, GitHub Actions run
`36773288493`, workflow `phase8a-exp063-persistence`, head
`6b106e4514f6ca3f06c677aab66fb04eb37ad881`, run number 1, attempt 1,
completed successfully.

Exactly 20 jobs completed successfully and exactly 20 artifacts are present and
non-expired. Aggregate artifact id `11127203563` is
`phase8a-exp063-aggregate-6b106e4514f6ca3f06c677aab66fb04eb37ad881`
with artifact digest
`sha256:4d730f2dfdb6e6ef7201eb2d9ce48678f29882df8075a396254f5051425611d3`.

The downloaded aggregate JSON SHA-256 is
`c012740e856b351320cb95c06583d8db2c3120cce8d14e26e091594a505f24ad`.
Its canonical evidence fingerprint is
`d0562d29da38c8ee4c0d3b28c35b3de7c9c42a5157910eef319a91b67ca4be42`,
and independent recomputation matched exactly.

All 18 cell evidence artifacts were inspected. Every cell enumerated 2,075
patterns / 4,150 directional hypotheses and reported zero qualifying directional
hypotheses, zero deduplicated hypotheses, an empty persistence shortlist, and an
empty frozen inventory. Across the frozen 18-cell universe this is 37,350
enumerated patterns and 74,700 directional hypotheses with zero passing the
DEC-444 persistence gate.

Classification:
`NO_DIRECTIONAL_HYPOTHESIS_PASSED_FROZEN_PERSISTENCE_GATE`.

This is a negative result for the exact frozen EXP-063 universe and protocol. It is
not a claim that no market edge exists outside that universe, and it is not a
ranking/dedup failure: qualification itself is zero.

Evidence remains `RETROSPECTIVE_ALREADY_SEEN`, `untouched_oos=false`, with zero
shortlist and zero frozen hypotheses. The reserved 2023-01-01 through 2026-08-20
robustness block remains unopened and unauthorized.

The one-shot slot is consumed permanently. Rerun, retry, replacement, reserved
robustness access, candidate compilation, promotion, Phase 8B, demo/live orders,
real-money action, and trading remain false.

Review source
`src/fmp/discovery/exp063_historical_result_review.py` is blob
`b572dbf4801c211b72285049654ebf4d96744cf1`; focused tests
`tests/test_phase8a_exp063_historical_result_review.py` are blob
`f9afb8d81658a55af1b044525ac1ee5654c3bcfe`.

Next gate: `EXPLICIT_POST_EXP063_RESEARCH_DIRECTION_DECISION`. Any successor
research must treat 2015-2022 EXP-063 outcomes as already-seen evidence and may not
retroactively redefine or rerun EXP-063.

## DEC-451 — Open EXP-064 continuous-stability research direction

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY SUCCESSOR DIRECTION OPEN

DEC-451 binds merged DEC-450 commit
`839af1e85b526c3c2a11b228e4aa8d3865589f06`, DEC-450 result-review source blob
`b572dbf4801c211b72285049654ebf4d96744cf1`, EXP-063 historical run
`36773288493`, and aggregate evidence fingerprint
`d0562d29da38c8ee4c0d3b28c35b3de7c9c42a5157910eef319a91b67ca4be42`.

The frozen EXP-063 result was 37,350 enumerated patterns / 74,700 directional
hypotheses with zero qualifying directional hypotheses, zero shortlist, and zero
frozen hypotheses. Combined with EXP-062's confirmation survivors failing to persist
through its already-seen validation years, DEC-451 closes the LOW/MID/HIGH
one/two-predicate atomic-state family rather than relaxing persistence requirements.

The new source-only successor identity is `EXP-20261001-064`.

EXP-064 keeps the exact EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m market
universe and the same 20 leakage-safe continuous feature columns. No new raw
features, symbols, timeframes, horizons, or alternative data are authorized.

The successor direction permits source-only design of deterministic transforms of
the existing continuous features and simple continuous/rank-based effect forms.
Exact normalization/rank method, estimator, annual-stability gate, interaction
policy, search-volume bound, cost treatment, ranking/deduplication, and freeze caps
remain deferred to the next protocol decision and must be frozen before execution.

2015-2022 remains `ALREADY_SEEN_DESIGN_EVIDENCE` and may not be called fresh
validation. The reserved 2023-01-01 through 2026-08-20 block remains closed.

EXP-063 rerun/retry/replacement, threshold relaxation, pattern redefinition/rescue,
successor execution/result production, reserved robustness access, candidate
compilation, promotion, Phase 8B, demo/live orders, real-money action, and trading
remain false.

Research-direction source
`src/fmp/discovery/exp064_research_direction.py` is blob
`6a7de1e93515fd3771e3763641ee6a07e425ee8a`; focused tests
`tests/test_phase8a_exp064_research_direction.py` are blob
`0f7924c553f49813007e845e7d7b3d26b8832172`.

Next gate: `SOURCE_ONLY_EXP064_CONTINUOUS_STABILITY_PROTOCOL`.

## DEC-452 — Freeze EXP-064 continuous-stability protocol

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY PROTOCOL FROZEN / EXECUTION LOCKED

DEC-452 binds merged DEC-451 commit
`e55df61f766ae49c72f04ac6259928252ae113dc` and DEC-451 research-direction
source blob `6a7de1e93515fd3771e3763641ee6a07e425ee8a`.

The new protocol source
`src/fmp/discovery/exp064_continuous_stability_protocol.py` at blob
`c108ea047c7bfb3e588bfbac33993180066c28ad` freezes EXP-064 before any
historical execution. Focused tests are
`tests/test_phase8a_exp064_continuous_stability_protocol.py` at blob
`ff09cc2f4a489e08cd682627c4422ceb8772edb2`.

EXP-064 keeps the exact EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m market
universe and the same 20 leakage-safe continuous features. It introduces no new raw
features, symbols, timeframes, horizons, or alternative data.

The frozen transform is a full-design 2015-2022 empirical midrank CDF per
symbol/timeframe/feature, requiring at least 600 finite rows and 20 distinct values.
No reserved 2023-2026 row may affect calibration.

Each hypothesis is exactly one feature × one market direction × one effect polarity
(INCREASING or DECREASING). Interactions are forbidden. The exact search volume is
80 hypotheses per cell and 1,440 globally.

The primary annual effect is the polarity-signed OLS slope of 0.5-pip net outcome on
centered rank. The economic subset is predeclared as the upper quartile for
INCREASING effects and lower quartile for DECREASING effects. That selected tail is
also measured at 0.5-pip design cost and 1.0-pip stress.

Qualification requires total selected-tail support >=600; >=75 per year; at least
6/8 positive slope years; at least 6/8 positive selected-tail years; equal-year
signed slope >=0.25; equal-year selected-tail 0.5-pip mean >=0.25; positive
lower-half slope; positive lower-half selected-tail mean; positive slope and
selected-tail mean in every fixed two-year block; and positive equal-year
selected-tail mean at 1.0-pip stress.

Ranking is frozen by lower-half and worst-block economic performance first, then
lower-half/worst-block signed slope, positive-year counts, stress performance,
support, feature/direction/polarity identity, and fingerprint. Shortlist cap is 5 per
cell/horizon / 90 global; frozen cap is 2 per cell/horizon / 36 global.
Near-duplicate selected-tail event sets use same-direction Jaccard >=0.95.

All 2015-2022 evidence remains `RETROSPECTIVE_ALREADY_SEEN` with
`untouched_oos=false`. Output kind is
`RETROSPECTIVE_CONTINUOUS_STABILITY_HYPOTHESIS_NOT_VALIDATED`.

Source access, historical execution/result production, reserved robustness access,
candidate compilation, promotion, Phase 8B, demo/live orders, real-money action,
and trading remain false.

Next gate: deterministic source-only EXP-064 in-memory miner core implementing this
exact protocol.

## DEC-453 — Add EXP-064 continuous-stability miner core

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY MINER CORE / EXECUTION LOCKED

DEC-453 binds merged DEC-452 commit
`b44af18b7cc5f3fa67d2f938529151f74d9deceb`, DEC-452 protocol blob
`c108ea047c7bfb3e588bfbac33993180066c28ad`, and predecessor observation-model
blob `495a67699eb5014e52129f0238a2737049fe38e6`.

The deterministic in-memory miner is
`src/fmp/discovery/exp064_continuous_stability_miner.py` at blob
`b0d799ec1afaf43b0441290c97a9f39c37ecd2fd`. Focused tests are
`tests/test_phase8a_exp064_continuous_stability_miner.py` at blob
`64c70118c00b594ba638ae38176f85ffc5a44406`.

The miner scopes all calibration/effect work to 2015-2022 before any ranking. Each
feature uses the DEC-452 empirical-midrank calibration contract; inactive/tied
features are skipped rather than repaired. The report retains the frozen 80
hypotheses-per-cell bound, while only evaluable active-feature direction/polarity
combinations can qualify.

Annual statistics use exact same-year fixed-horizon outcomes and compute the frozen
polarity-signed rank slope plus deterministic selected-tail means at 0.5-pip and
1.0-pip cost. The miner delegates qualification directly to DEC-452, materializes
exact EXP-064 fingerprints/metrics, applies the frozen 12-field rank order, and
deduplicates same-direction selected-tail event sets at Jaccard >=0.95.

Shortlist remains capped at 5 per cell/horizon and frozen retrospective hypotheses
at 2 per cell/horizon. Frozen does not mean validated or executable.

Focused tests prove the exact 80-hypothesis cell bound, stable monotone effect
selection, Jaccard deduplication, weak-block rejection, duplicate-identity failure,
and exact equality of the complete result after catastrophic 2023-2026 rows are
appended. Reserved data therefore cannot affect the in-memory result.

Source access, historical execution/result production, reserved robustness access,
candidate compilation, promotion, Phase 8B, demo/live orders, real-money action,
and trading remain false.

Next gate: separate source-only EXP-064 artifact/evidence contract bound to the
exact DEC-453 miner.

## DEC-454 — Freeze EXP-064 evidence contract

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY EVIDENCE CONTRACT / EXECUTION LOCKED

DEC-454 binds merged DEC-453 commit
`bda820585a568cefca52487d4aefad77be109387`, DEC-453 miner blob
`b0d799ec1afaf43b0441290c97a9f39c37ecd2fd`, and DEC-452 protocol blob
`c108ea047c7bfb3e588bfbac33993180066c28ad`.

The evidence contract is
`src/fmp/discovery/exp064_evidence_contract.py` at blob
`9aee3f9e273e20329c9de5a7079ed924ffee0a9a`. Focused tests are
`tests/test_phase8a_exp064_evidence_contract.py` at blob
`9cda7c7018d962511ab1819c3cc9fd4b67dac5f6`.

Cell and aggregate evidence use deterministic canonical JSON with sorted keys,
compact separators, `allow_nan=false`, a trailing newline, and SHA-256
fingerprints. Both compilers self-validate.

Each cell binds exact source manifests/evidence identities, cell identity, compact
rank-calibration identities, frozen 80-hypothesis search counts, complete shortlist
annual statistics/metrics, and the first up to two shortlist fingerprints as the
frozen retrospective inventory. Calibration identity records feature, count,
distinct count, range, and SHA-256 of the complete sorted calibration-value array
without embedding that potentially large array.

The validator reconstructs all eight annual continuous-effect statistics for every
shortlisted hypothesis, re-runs the DEC-452 gate, recomputes every persisted
continuous-stability metric, recomputes the hypothesis fingerprint and exact 12-field rank
key, verifies shortlist order, and verifies the frozen shortlist prefix.

Aggregate evidence requires the exact sorted 18-cell inventory, exact Phase 2
processed source manifests, identical feature/outcome manifest pairs across
horizons per symbol/timeframe, singular upstream feature/outcome evidence
fingerprints, unique cell fingerprints, shortlist <=90 globally, and frozen <=36
globally.

All evidence remains `RETROSPECTIVE_ALREADY_SEEN` with `untouched_oos=false`,
`reserved_robustness_opened=false`, and output kind
`RETROSPECTIVE_CONTINUOUS_STABILITY_HYPOTHESIS_NOT_VALIDATED`.

Source access, historical execution/result production, reserved robustness access,
candidate compilation, promotion, Phase 8B, demo/live orders, real-money action,
and trading remain false.

Next gate: locked EXP-064 runtime wiring with a hard execution gate before any
historical artifact download.

## DEC-455 — Install locked EXP-064 runtime wiring

**Date:** 2026-10-01  
**Status:** ACTIVE WORKFLOW INSTALLED / HISTORICAL EXECUTION LOCKED

DEC-455 binds merged DEC-454 commit
`e13cad5fe00cc50af80147e0fbe2de500ad38436`, final DEC-454 evidence-contract
blob `9aee3f9e273e20329c9de5a7079ed924ffee0a9a`, DEC-453 continuous-stability
miner blob `b0d799ec1afaf43b0441290c97a9f39c37ecd2fd`, and DEC-452 protocol blob
`c108ea047c7bfb3e588bfbac33993180066c28ad`.

The runtime reuses the exact accepted EXP-044 feature/outcome artifacts and the
frozen EXP-062 source/loader/non-finite→null path. No new historical input,
symbol, timeframe, horizon, feature, or repair path is introduced.

Runtime source is `src/fmp/discovery/exp064_runtime_source.py` at blob
`07e5ccebb6416c04621aa54e170cd4eb1e0a2a04`. Public locked CLI is
`scripts/phase8a_exp064.py` at blob
`a44aed6d890e25a781b7b92d7efb3dabe06f9047`.

The dormant template
`docs/superpowers/templates/phase8a-exp064-continuous-stability.yml.disabled`
and installed active workflow
`.github/workflows/phase8a-exp064-continuous-stability.yml` are byte-identical
at Git blob `caca62672ad9796764c18be6b8da9785b98c9733`.

The frozen manual-main run topology is exactly 20 jobs and 20 artifacts:
one preflight, the 18 EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m cells,
and one aggregate. Each cell is composed only from the exact EXP-044 loader,
EXP-062 non-finite→null adapter, DEC-453 miner, and DEC-454 evidence contract.

A hard `require-execution` gate precedes every historical artifact download in
the workflow and precedes every historical artifact/result read in the CLI.
Under DEC-455, workflow dispatch authorization, historical execution, historical
result production, rerun, retry, replacement, reserved 2023-2026 robustness
access, candidate compilation, promotion, Phase 8B, demo/live orders,
broker mutation, real-money action, and trading all remain false.

Focused tests are
`tests/test_phase8a_exp064_locked_runtime_wiring.py` at blob
`12cfb8b833c46465e0f8646c0cd0d7ab59ddb1fd`. They pin DEC-452/453/454
runtime lineage, exact source snapshots, the 18-cell/20-job topology,
byte-identical dormant/active workflow installation, gate ordering before reads,
and the closed execution boundary.

Next gate: a separate explicit one-shot EXP-064 historical execution
authorization bound to the exact merged DEC-455 runtime. DEC-455 itself provides
no execute mode and does not dispatch EXP-064.

## DEC-456 — Open EXP-064 one-shot historical slot

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY ONE-SHOT SLOT AUTHORIZATION / DISPATCH LOCKED

DEC-456 binds merged DEC-455 commit
`c388def44d251c96832572f07de43d9dc6a909ee`, DEC-455 runtime source blob
`07e5ccebb6416c04621aa54e170cd4eb1e0a2a04`, active EXP-064 workflow blob
`caca62672ad9796764c18be6b8da9785b98c9733`, locked CLI blob
`a44aed6d890e25a781b7b92d7efb3dabe06f9047`, DEC-454 evidence-contract blob
`9aee3f9e273e20329c9de5a7079ed924ffee0a9a`, DEC-453 continuous-stability
miner blob `b0d799ec1afaf43b0441290c97a9f39c37ecd2fd`, and DEC-452 protocol blob
`c108ea047c7bfb3e588bfbac33993180066c28ad`.

At DEC-456 creation, the newly installed
`phase8a-exp064-continuous-stability` workflow has zero matching manual-main
`workflow_dispatch` runs. DEC-456 therefore opens exactly one source-authorized
historical-result slot: the first exact manual-main run, run number 1 / attempt 1.
The slot is consumed immediately when that run exists, including queued or running
state, and remains consumed on every terminal outcome including failure or
cancellation.

Authorization source is
`src/fmp/discovery/exp064_historical_run_authorization.py` at blob
`0668910a69a87fad06be73af98e5f403436fe7fb`. Focused tests are
`tests/test_phase8a_exp064_historical_run_authorization.py` at blob
`08f9181bc0fd8d70959c7f1e595dda43ce96ccf7`.

Only `historical_result_slot_source_authorized=true` is opened. Workflow
dispatch authorization, historical execution, historical result production,
rerun, retry, replacement, reserved 2023-2026 robustness access, candidate
compilation, promotion, Phase 8B, demo/live orders, broker mutation, real-money
action, and trading remain false.

The data boundary remains 2015-01-01 through 2022-12-31 already-seen design
evidence only. Reserved robustness remains closed from 2023-01-01 through
2026-08-20.

Next gate: a separate bounded runtime activation / one-shot dispatch decision that
revalidates the exact merged DEC-455 runtime and still-unused DEC-456 slot
immediately before any dispatch. DEC-456 itself provides no dispatch or execution
path.

## DEC-457 — Activate one-shot EXP-064 runtime

**Date:** 2026-10-01  
**Status:** ONE-SHOT HISTORICAL RUNTIME AUTHORIZED / NOT DISPATCHED

DEC-457 binds merged DEC-456 commit
`ef6c40d3e8148e52256917576423a8e6f53e8cfb`, DEC-456 one-shot authorization
blob `0668910a69a87fad06be73af98e5f403436fe7fb`, DEC-455 runtime source blob
`07e5ccebb6416c04621aa54e170cd4eb1e0a2a04`, unchanged active workflow blob
`caca62672ad9796764c18be6b8da9785b98c9733`, DEC-454 evidence-contract blob
`9aee3f9e273e20329c9de5a7079ed924ffee0a9a`, DEC-453 continuous-stability
miner blob `b0d799ec1afaf43b0441290c97a9f39c37ecd2fd`, and DEC-452 protocol blob
`c108ea047c7bfb3e588bfbac33993180066c28ad`.

The live EXP-064 CLI is activated at
`scripts/phase8a_exp064.py` blob
`29fce0ac43adf6743448d5936b00f7e6755df2b4`. Runtime authorization source is
`src/fmp/discovery/exp064_historical_execution_authorization.py` at blob
`5d5c0e8ceeeef4b0b2d45167c47a682937ef8121`. The read-only dispatch planner is
`src/fmp/discovery/exp064_historical_dispatch_operator.py` at blob
`469551d56332644e53741b5aeeb8314ba934b662`. Focused activation tests are
`tests/test_phase8a_exp064_historical_runtime_activation.py` at blob
`af3c8b4aabd9503ab6f50ffaa99eea976bb75bb6`.

The runtime gate authorizes only GitHub Actions execution in repository
`Dtwosam/FMP`, workflow `phase8a-exp064-continuous-stability`, event
`workflow_dispatch`, ref `refs/heads/main`, run number 1, run attempt 1,
positive run id, exact supplied commit SHA, and exact pinned source blobs. Run
number 2, attempt 2, local execution, repository/workflow/ref drift, SHA drift,
or source drift fail closed.

The read-only planner has no execute mode and invokes no subprocess. It emits only
the plan command
`gh workflow run phase8a-exp064-continuous-stability.yml --ref main`
when current main exactly matches the expected head and DEC-456 reports an unused
slot. If any matching run already exists, no command is emitted and the slot is
reported consumed.

DEC-457 opens historical execution source authorization, historical-result
dispatch authorization, historical execution authorization, and historical
result production authorization only for this single 2015-2022 already-seen
research run. Rerun, retry, replacement, reserved 2023-2026 robustness access,
candidate compilation, promotion, Phase 8B, demo/live orders, broker mutation,
real-money action, and trading remain false.

DEC-457 itself does not dispatch EXP-064. After green merge, the next action is an
immediate read-only main-head plus run-inventory check. Only if main is unchanged,
the slot remains empty, and the planner reports
`EXP064_ONE_SHOT_DISPATCH_READY` may the single manual dispatch be performed.
The first created run consumes the slot regardless of outcome.

## DEC-458 — Freeze EXP-064 historical result: no continuous-stability hypotheses

**Date:** 2026-10-01  
**Status:** HISTORICAL RESULT REVIEWED AND FROZEN / NO CONTINUOUS-STABILITY HYPOTHESES

DEC-458 freezes the only EXP-064 historical run, GitHub Actions run
`36853290904`, workflow `phase8a-exp064-continuous-stability`, head
`b13f89f4d6bef8b1ab4a2fa12c6b01d0e5067506`, run number 1, attempt 1,
completed successfully.

Exactly 20 jobs completed successfully and exactly 20 artifacts are present and
non-expired. Aggregate artifact id `11158816828` is
`phase8a-exp064-aggregate-b13f89f4d6bef8b1ab4a2fa12c6b01d0e5067506`
with artifact digest
`sha256:a404c053a5dd6989cf0efb2adba2cb276fec9a66a448a8617e7dac7da50c577f`.

The downloaded aggregate JSON SHA-256 is
`b971340204ec2a6136559dc467f84f1e6b69f1c58fe3c5cca01e437ba6c80284`.
Its canonical evidence fingerprint is
`832e8c814ac578b614764d37cba15e64569e2f841dfa6f72f2c9cd9a8fdbcbb1`,
and independent recomputation matched exactly.

All 18 cell evidence artifacts were inspected. Every cell contains exactly 80
frozen hypotheses / 80 evaluable hypotheses and reports zero qualifying
hypotheses, zero deduplicated hypotheses, an empty continuous-stability shortlist,
and an empty frozen inventory. Across the frozen 18-cell universe this is 1,440
hypotheses and 1,440 evaluable hypotheses with zero passing the DEC-452
continuous-stability gate. Every cell evidence fingerprint recomputed and matched
the aggregate inventory.

Classification:
`NO_CONTINUOUS_STABILITY_HYPOTHESIS_PASSED_FROZEN_GATE`.

This is a negative result for the exact frozen EXP-064 universe and protocol. It is
not a claim that no market edge exists outside that universe, and it is not a
ranking/dedup failure: qualification itself is zero.

Evidence remains `RETROSPECTIVE_ALREADY_SEEN`, `untouched_oos=false`, with
zero shortlist and zero frozen hypotheses. The reserved 2023-01-01 through
2026-08-20 robustness block remains unopened and unauthorized.

The one-shot slot is consumed permanently. Rerun, retry, replacement, reserved
robustness access, candidate compilation, promotion, Phase 8B, demo/live orders,
real-money action, and trading remain false.

Review source
`src/fmp/discovery/exp064_historical_result_review.py` is blob
`c5878685950e14a632b4eb8d2616d9540afb12d2`; focused tests
`tests/test_phase8a_exp064_historical_result_review.py` are blob
`258aa9fbe71fae63b805d08a0112aef229cb205f`.

Next gate: `EXPLICIT_POST_EXP064_RESEARCH_DIRECTION_DECISION`. Any successor
research must treat 2015-2022 EXP-064 outcomes as already-seen evidence and may not
retroactively redefine or rerun EXP-064.

## DEC-459 — Open EXP-065 bounded pairwise-interaction research direction

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY SUCCESSOR DIRECTION OPEN

DEC-459 binds merged DEC-458 commit
`e3c2a7a1dbb6592a8438f3949ffa83177e31f4e6`, DEC-458 result-review source blob
`c5878685950e14a632b4eb8d2616d9540afb12d2`, EXP-064 historical run
`36853290904`, and aggregate evidence fingerprint
`832e8c814ac578b614764d37cba15e64569e2f841dfa6f72f2c9cd9a8fdbcbb1`.

The frozen EXP-064 result is 1,440 hypotheses / 1,440 evaluable hypotheses with
zero qualifying hypotheses, zero deduplicated hypotheses, zero continuous-stability
shortlist, and zero frozen hypotheses under the DEC-452 single-feature
continuous/rank protocol.

Combined with EXP-063's zero persistence qualifiers for the frozen discrete
one/two-predicate atomic-state family, DEC-459 changes representation again rather
than relaxing any predecessor threshold. The new source-only successor identity is
`EXP-20261001-065`.

EXP-065 keeps the exact EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m market
universe and the same 20 leakage-safe continuous features. No new raw features,
symbols, timeframes, horizons, alternative data, or repair paths are authorized.

The successor direction permits source-only design of exactly-two-feature
interactions. Three-or-more-feature combinations remain forbidden. Exact
feature-pair construction, interaction transform, estimator, main-effect control,
interaction incrementality test, search-volume bound, annual-stability gate,
cost-stress gate, ranking/deduplication, and shortlist/freeze caps are deferred to
the next protocol decision and must be frozen before execution.

A future pairwise protocol must include a deterministic interaction-incrementality
requirement so a pair cannot qualify merely because one constituent feature carries
the effect.

2015-2022 remains `ALREADY_SEEN_DESIGN_EVIDENCE` and may not be called fresh
validation. The reserved 2023-01-01 through 2026-08-20 block remains closed.

EXP-064 rerun/retry/replacement, threshold relaxation, protocol redefinition,
hypothesis rescue, successor execution/result production, reserved robustness
access, candidate compilation, promotion, Phase 8B, demo/live orders, real-money
action, and trading remain false.

Research-direction source
`src/fmp/discovery/exp065_pairwise_interaction_research_direction.py` is blob
`7d9350f714bfec7cc39ebf76b2e6e313261e9a68`; focused tests
`tests/test_phase8a_exp065_pairwise_interaction_research_direction.py` are blob
`b177a0aa1244e3f7b7c186dbcf5169b78e76b82a`.

Next gate: `SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_PROTOCOL`.

## DEC-460 — Freeze EXP-065 pairwise-interaction protocol

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY PROTOCOL FROZEN / EXECUTION LOCKED

DEC-460 binds merged DEC-459 commit
`c0d8ba052cc0cd662149aa787722874c7207ce4a`, DEC-459 pairwise-direction source
blob `7d9350f714bfec7cc39ebf76b2e6e313261e9a68`, and the DEC-452
continuous-rank protocol blob
`c108ea047c7bfb3e588bfbac33993180066c28ad`.

The frozen successor identity is `EXP-20261001-065`. It keeps the exact
EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m market universe and the same 20
leakage-safe continuous features. No new raw features, symbols, timeframes,
horizons, alternative data, or repair paths are authorized.

EXP-065 enumerates the exact 190 unordered pairs from the 20-feature list. Each
hypothesis is one pair × one direction (LONG/SHORT) × one interaction polarity
(INCREASING/DECREASING), for exactly 760 hypotheses per cell/horizon and 13,680
globally. Same-feature pairs and all 3+ feature interactions are forbidden.

Each constituent feature retains the DEC-452 full-design 2015-2022 empirical
midrank CDF. Pair interaction raw score is exactly
`2 * (p_a - 0.5) * (p_b - 0.5)`; each symbol/timeframe/pair raw-score series is
then itself calibrated by a full-design empirical-midrank CDF. Pair calibration
requires at least 600 finite rows and 20 distinct values.

The primary annual interaction effect is the polarity-signed OLS coefficient on
centered interaction rank in
`net_pips_0p5 ~ 1 + centered_rank(feature_a) + centered_rank(feature_b) + centered_rank(interaction)`.
This makes the interaction statistic incremental to the two constituent linear
rank main effects. Singular designs fail closed at the frozen `1e-12` tolerance.

An additional main-effects-only annual model
`net_pips_0p5 ~ 1 + centered_rank(feature_a) + centered_rank(feature_b)`
produces residuals. The selected interaction tail must retain positive raw
economics and positive mean main-effect residual, preventing qualification based
solely on a constituent main effect.

The stability gate keeps all eight 2015-2022 years and requires >=600 total
selected-tail support, >=75 each year, at least 6/8 positive years for partial
interaction slope/raw selected-tail mean/incremental residual mean, equal-year
partial slope >=0.25, equal-year raw selected-tail mean >=0.25, positive
equal-year incremental residual mean, positive lower-half metrics for all three,
positive metrics in every fixed two-year block for all three, and positive
equal-year raw selected-tail mean at the 1.0-pip stress cost.

Ranking prioritizes incremental residual stability before raw economics and partial
slope stability. Selected-tail event sets at Jaccard >=0.95 are near-duplicates.
Because the search volume is larger than EXP-064, the retrospective carry-forward
caps are tightened to 3 shortlist / 1 frozen per cell-horizon, or 54 shortlist /
18 frozen globally.

All evidence remains `RETROSPECTIVE_ALREADY_SEEN` with
`untouched_oos=false` and output kind
`RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED`. The reserved
2023-01-01 through 2026-08-20 block remains closed.

Protocol source
`src/fmp/discovery/exp065_pairwise_interaction_protocol.py` is blob
`5ed8b86207076264096d5e6ac5aaf25472172407`; focused tests
`tests/test_phase8a_exp065_pairwise_interaction_protocol.py` are blob
`b50d3f62d5ee25e260403bc323317cf84a4b4d01`.

Historical execution/result production, reserved robustness access, candidate
compilation, promotion, Phase 8B, demo/live orders, broker mutation, real-money
action, and trading remain false.

Next gate: `SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_MINER`.

## DEC-461 — Repair EXP-065 pairwise protocol helper composition

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY PROTOCOL REPAIR / EXECUTION LOCKED

DEC-461 binds merged DEC-460 commit
`fd04cea05179bed6b33941635a60dfb8fb76ad60` and repairs two implementation
defects in the EXP-065 pairwise-interaction protocol before any miner/runtime may
depend on it.

The originally merged DEC-460 protocol blob
`5ed8b86207076264096d5e6ac5aaf25472172407` wrapped the frozen DEC-452
`empirical_midrank_percentile(calibration, value)` helper with reversed
arguments in `interaction_percentile(...)`. DEC-461 corrects only that adapter
ordering; the empirical-midrank formula, tie policy, calibration scope, and
interaction thresholds do not change.

DEC-452 `rank_calibration_values(...)` also returns `None` when the frozen
calibration minimum is not met. The DEC-460 pair-calibration adapter attempted
`len(None)` in that state. DEC-461 makes the boundary explicit and fail-closed
with a protocol `ValueError`. The existing minimums remain exactly 600 finite
rows and 20 distinct values; no deficient calibration is repaired or relaxed.

All DEC-460 mathematical/governance semantics remain unchanged: 20 features,
190 unordered distinct pairs, 760 hypotheses per cell/horizon, 13,680 globally,
the same pair interaction transform, main-effect-controlled annual interaction
OLS, incremental selected-tail residual requirement, eight-year support/stability
and cost-stress gate, Jaccard >=0.95 deduplication, 3/54 shortlist caps, 1/18
frozen caps, `RETROSPECTIVE_ALREADY_SEEN`, `untouched_oos=false`, and the
closed 2023-01-01 through 2026-08-20 reserve.

Repaired protocol source
`src/fmp/discovery/exp065_pairwise_interaction_protocol.py` is blob
`b54267d790667659749a96123ad23a491ff50dfa`; focused tests
`tests/test_phase8a_exp065_pairwise_interaction_protocol.py` are blob
`08ea27be5b859073b9387187e6e0c55b8cdd0ffb`.

Historical source access/execution/result production, reserved robustness access,
candidate compilation, promotion, Phase 8B, demo/live orders, broker mutation,
real-money action, and trading remain false. No workflow, CLI, runtime, dispatch,
or artifact path is added.

Next gate: `SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_MINER`. Any miner must bind
the repaired DEC-461 protocol blob rather than the superseded DEC-460 source blob.

## DEC-462 — Freeze source-only EXP-065 pairwise-interaction miner

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY MINER FROZEN / EXECUTION LOCKED

DEC-462 binds merged DEC-461 commit
`2a8127b505c9b0d9e1adb562bd18a5cafc171df6`, repaired EXP-065 protocol blob
`b54267d790667659749a96123ad23a491ff50dfa`, and base feature/outcome
observation-model blob `495a67699eb5014e52129f0238a2737049fe38e6`.

The miner is deterministic and in-memory only. It introduces no historical source
adapter, file/database/network reader, workflow, CLI, artifact writer, dispatch
path, or result-production authority.

For each cell/horizon it preserves the nominal frozen universe of exactly 760
hypotheses: 190 canonical unordered feature pairs × 2 directions × 2 interaction
polarities. The report separately counts evaluable hypotheses; unavailable,
insufficient-calibration, or singular pairs fail closed and do not redefine the
nominal search count.

Constituent features retain the DEC-452 full-design 2015-2022 empirical-midrank
calibration. Each usable pair is calibrated under the repaired DEC-461 interaction
helper using exactly
`2 * (p_a - 0.5) * (p_b - 0.5)` followed by full-design empirical midranking.

For every evaluable pair/direction/polarity, the miner constructs exact annual
2015-2022 statistics using the frozen main-effect-controlled interaction OLS,
main-effects-only residuals, raw selected-tail economics at 0.5/1.0 pip, and
selected-tail residual incrementality. Singular annual designs or missing selected
tails make the hypothesis non-evaluable; no regularization or rescue path exists.

Qualification delegates to the repaired frozen
`pairwise_interaction_gate_passes(...)` protocol function. Ranking follows the
frozen DEC-460 order exactly. Near-duplicate selected-tail observation-id sets use
Jaccard >=0.95 and retain the higher-ranked hypothesis. Per-cell carry-forward caps
remain 3 shortlist / 1 frozen, with the existing global 54 / 18 caps preserved for
later aggregation.

Rows from 2023 onward are filtered before calibration or evaluation; the
2023-01-01 through 2026-08-20 reserved block remains closed and cannot affect any
miner output.

Miner source
`src/fmp/discovery/exp065_pairwise_interaction_miner.py` is blob
`7dac382838d2b8fcc4df5d02c4949ad65c17635b`; focused tests
`tests/test_phase8a_exp065_pairwise_interaction_miner.py` are blob
`f97bf2ec31c92e9866eb771ce5f526045e2ed482`.

Historical source access/execution/result production, reserved robustness access,
candidate compilation, promotion, Phase 8B, demo/live orders, broker mutation,
real-money action, and trading remain false.

Next gate:
`SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_EVIDENCE_CONTRACT`.

## DEC-463 — Freeze EXP-065 pairwise-interaction evidence contract

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY EVIDENCE CONTRACT FROZEN / EXECUTION LOCKED

DEC-463 binds merged DEC-462 commit
`735418cd455055a5102de6fb0d621355c4e85592`, DEC-462 pairwise miner blob
`7dac382838d2b8fcc4df5d02c4949ad65c17635b`, and repaired DEC-461 protocol
blob `b54267d790667659749a96123ad23a491ff50dfa`.

The evidence contract freezes deterministic cell and aggregate payloads before any
historical runtime is considered. It adds no loader, database/file/network source,
workflow, CLI, artifact writer, dispatch path, historical result authority, or
reserved-data access.

Each of the exact 18 expected cells freezes its code commit, processed source
manifest, feature/outcome manifests, feature/outcome evidence fingerprints,
constituent rank-calibration summaries/fingerprints, pair interaction-calibration
summaries/fingerprints, nominal/evaluable/qualifying/deduplicated hypothesis
counts, deterministic shortlist, frozen fingerprint inventory, and output kind.

Every cell must retain the nominal `hypothesis_count = 760`; concrete data
availability may reduce only the separate evaluable count. Evaluable hypotheses
cannot exceed active canonical pair count × 2 directions × 2 polarities.
Qualifying cannot exceed evaluable and deduplicated cannot exceed qualifying.

Shortlist rows are not trusted merely because the outer evidence fingerprint is
valid. DEC-463 reconstructs all eight annual
`AnnualPairwiseInteractionStat` rows, reruns the frozen pairwise interaction gate,
recomputes all support/sign/equal-year/lower-half/two-year-block metrics,
recomputes exact pair hypothesis fingerprints, and enforces the frozen rank order.

Constituent calibration evidence requires at least 600 rows and 20 distinct values.
Pair calibration evidence independently requires at least 600 rows and 20 distinct
interaction values. Canonical feature and pair ordering is mandatory.

Cell caps remain 3 shortlist / 1 frozen. Aggregate caps remain 54 shortlist / 18
frozen. Frozen fingerprints must equal the leading ranked shortlist inventory under
the per-cell cap.

Aggregate evidence requires exactly one cell for every
EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m identity, deterministic cell order,
symbol-specific frozen Phase 2 source manifests, cross-horizon feature/outcome
manifest identity per symbol/timeframe, and one common feature-evidence and
outcome-evidence fingerprint across all cells.

All evidence remains `RETROSPECTIVE_ALREADY_SEEN`,
`untouched_oos=false`, `reserved_robustness_opened=false`, with output kind
`RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED`. The
2023-01-01 through 2026-08-20 reserve remains closed.

Evidence-contract source `src/fmp/discovery/exp065_evidence_contract.py` is blob
`ca68622ddfc9866f00569d558b2ab927be23686d`; focused tests
`tests/test_phase8a_exp065_evidence_contract.py` are blob
`41930e892cf38e37160a9c7edbfc369d9fec679f`.

Historical source access/execution/result production, reserved robustness access,
candidate compilation, promotion, Phase 8B, demo/live orders, broker mutation,
real-money action, and trading remain false.

Next gate:
`SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_RUNTIME_WIRING`.

## DEC-464 — Install locked EXP-065 pairwise runtime wiring

**Date:** 2026-10-01  
**Status:** ACTIVE WORKFLOW INSTALLED / HISTORICAL EXECUTION LOCKED

DEC-464 binds merged DEC-463 commit
`c8c2c8d2dd5be5ff73655b09730d9eb18f9c3737`, DEC-463 evidence-contract
blob `ca68622ddfc9866f00569d558b2ab927be23686d`, DEC-462 pairwise miner
blob `7dac382838d2b8fcc4df5d02c4949ad65c17635b`, and repaired DEC-461
protocol blob `b54267d790667659749a96123ad23a491ff50dfa`.

The runtime reuses the exact accepted EXP-044 feature/outcome artifacts and the
frozen EXP-062 source/non-finite-to-null path plus EXP-061 range-limited loader.
No new historical input, symbol, timeframe, horizon, feature, repair path, or
reserved-data path is introduced.

Runtime source is
`src/fmp/discovery/exp065_runtime_source.py` at blob
`717b43e3bfd656b51e22819cf948f8cd6485f334`.
Locked CLI is `scripts/phase8a_exp065.py` at blob
`38e3eb9a5c2733655c845291d6bc3160e5fa0291`.

Dormant template
`docs/superpowers/templates/phase8a-exp065-pairwise-interaction.yml.disabled`
and installed active workflow
`.github/workflows/phase8a-exp065-pairwise-interaction.yml`
are byte-identical at Git blob
`75d0e4df56d5c4ced5aff614e236cf0e1bb078e1`.

The frozen manual-main topology is exactly 20 jobs and 20 artifacts: one
preflight, the 18 EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m cells, and one
aggregate. Each cell is composed only from the exact frozen source loader/adapter,
DEC-462 pairwise miner, and DEC-463 evidence contract.

A hard `require-execution` gate precedes every historical artifact download in
the workflow and every historical artifact/result read in the CLI. The workflow
validator also rejects predecessor cell/aggregate CLIs through EXP-064.

Under DEC-464, workflow source authorization and workflow installation are true.
Workflow dispatch authorization, historical execution, historical result
production, rerun, retry, replacement, reserved 2023-2026 robustness access,
candidate compilation, promotion, Phase 8B, demo/live orders, broker mutation,
real-money action, and trading remain false.

Focused tests are
`tests/test_phase8a_exp065_locked_runtime_wiring.py` at blob
`aecd7003d93d6de43565a5b22a663121cf2ccb68`.
They pin the exact DEC-463/462/461 lineage, source snapshots, 18-cell/20-job
topology, byte-identical workflow installation, exact CLI, gate ordering before
historical reads, predecessor-CLI rejection, and the closed execution boundary.

Next gate: a separate source-only one-shot EXP-065 historical-result slot
authorization bound to the exact merged DEC-464 runtime. DEC-464 itself provides
no execute mode and does not dispatch EXP-065.

## DEC-465 — Open source-only EXP-065 one-shot historical-result slot

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY SLOT AUTHORIZATION / DISPATCH LOCKED

DEC-465 binds merged DEC-464 commit
`698e3e21d7dd0cbe83c3ed7d15f5544cf9c096e9` and opens exactly one
source-level historical-result slot for EXP-065 while keeping dispatch, historical
execution, historical result production, rerun, retry, replacement, reserve
access, candidate compilation, promotion, Phase 8B, broker/order activity,
real-money action, and trading false.

The slot contract pins the exact DEC-464 runtime source
`717b43e3bfd656b51e22819cf948f8cd6485f334`, active workflow and dormant
template `75d0e4df56d5c4ced5aff614e236cf0e1bb078e1`, locked CLI
`38e3eb9a5c2733655c845291d6bc3160e5fa0291`, DEC-463 evidence contract
`ca68622ddfc9866f00569d558b2ab927be23686d`, DEC-462 miner
`7dac382838d2b8fcc4df5d02c4949ad65c17635b`, and repaired DEC-461 protocol
`b54267d790667659749a96123ad23a491ff50dfa`.

Only a manual `workflow_dispatch` run of
`phase8a-exp065-pairwise-interaction` from `main` can consume the slot. The
target must remain run number 1 and run attempt 1. The first matching queued,
running, successful, failed, or cancelled run consumes the slot permanently.
Multiple matching runs, run number >1, run attempt >1, or malformed run state fail
closed. No rerun, retry, or replacement path is exposed.

The historical window remains 2015-01-01 through 2022-12-31 inclusive. The
2023-01-01 through 2026-08-20 reserved robustness block remains closed.

Authorization source
`src/fmp/discovery/exp065_historical_run_authorization.py` is blob
`96aac63a75d7873e6b6508d34b983d0742858a02`; focused tests
`tests/test_phase8a_exp065_historical_run_authorization.py` are blob
`6de234057d06dc5485e2159dcf017fe3c01a25d2`.

Next gate: a separate source-only one-shot EXP-065 historical execution/runtime
authorization bound to merged DEC-465. DEC-465 itself provides no dispatch command
and performs no historical execution.



## DEC-466 — Activate one-shot EXP-065 historical runtime without dispatch

**Date:** 2026-10-01  
**Status:** ONE-SHOT HISTORICAL RUNTIME AUTHORIZED / NOT DISPATCHED

DEC-466 binds merged DEC-465 commit
`c44d787eff659838f904955ccf95dc69a43a852d` and activates the already
installed EXP-065 pairwise-interaction runtime for exactly one historical
2015-2022 manual-main run. The decision does not itself dispatch the workflow.

The activation pins DEC-465 one-shot authorization
`96aac63a75d7873e6b6508d34b983d0742858a02`, DEC-464 runtime source
`717b43e3bfd656b51e22819cf948f8cd6485f334`, unchanged workflow/template
`75d0e4df56d5c4ced5aff614e236cf0e1bb078e1`, DEC-463 evidence contract
`ca68622ddfc9866f00569d558b2ab927be23686d`, DEC-462 miner
`7dac382838d2b8fcc4df5d02c4949ad65c17635b`, repaired DEC-461 protocol
`b54267d790667659749a96123ad23a491ff50dfa`, the frozen non-finite adapter
`491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`, range-limited loader
`df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`, and runtime requirements
`1ff32214dee10d877a067e750cd69ffad96d5fe5`.

The live CLI is activated at blob
`4448d1bf43ce1ddb9dba9c4d38bb18829b95ae38`. Runtime authorization source
`src/fmp/discovery/exp065_historical_execution_authorization.py` is blob
`ccc99179a51145534e1b48b8520b2f743580c217`; read-only dispatch operator
`src/fmp/discovery/exp065_historical_dispatch_operator.py` is blob
`6a386c556e121d959ec1ea8bbb56dbb49b42dde2`; focused activation tests are
blob `332bd77b57f0fa5f6b5fb5f3bb9810fbde0c2eb2`.

Runtime authorization requires GitHub Actions, repository `Dtwosam/FMP`, workflow
`phase8a-exp065-pairwise-interaction`, event `workflow_dispatch`, ref
`refs/heads/main`, run number 1, run attempt 1, exact workflow SHA identity, a
positive run id, and all pinned source blobs. Run number >1, attempt >1, local
execution, repository/workflow/ref drift, or SHA drift fails closed.

The read-only operator has no execute mode. It can emit only
`gh workflow run phase8a-exp065-pairwise-interaction.yml --ref main` when main
matches the expected head and DEC-465 reports zero matching manual-main runs. Any
matching run consumes the slot immediately and permanently removes the planned
command.

Historical-result dispatch, execution, and result-production authority are opened
only for this one-shot run surface. Rerun, retry, replacement, reserved 2023-2026
robustness access, candidate compilation, promotion, Phase 8B, demo/live orders,
broker mutation, real-money action, and trading remain false.

A generic source-only continuation does not dispatch EXP-065. Any actual dispatch
requires a separate explicit governance decision plus an immediate read-only proof
that main is still the selected DEC-466 merge head and the slot remains unused.

Next gate: `EXPLICIT_EXP065_ONE_SHOT_HISTORICAL_DISPATCH_DECISION`.


## DEC-467 — Predeclare EXP-065 historical result review contract

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY REVIEW CONTRACT PREDECLARED / RUN IN PROGRESS

DEC-467 binds the only authorized EXP-065 historical run, GitHub Actions run
`36905224184`, workflow `phase8a-exp065-pairwise-interaction`, head
`5faa733572576aa5a1c56176ac27c415eaaf6416`, run number 1, attempt 1.

The contract is intentionally result-agnostic while the run is active. It does
not predeclare aggregate artifact id/digest, raw aggregate JSON hash, evidence
fingerprints, evaluable/qualifying/deduplicated counts, shortlist contents, or
frozen hypotheses.

A successful terminal run must have exactly 20 successful jobs and exactly 20
non-expired artifacts with the frozen preflight + 18 cells + aggregate
inventories. Artifact ids must be positive and artifact digests must be valid
SHA-256 values. A non-success terminal conclusion still consumes the slot and
does not reopen rerun, retry, or replacement authority.

Successful result evidence must first pass the existing DEC-463 cell and
aggregate validators. DEC-467 additionally cross-checks aggregate summaries
against all 18 supplied cell evidence objects, keeps the exact 760 nominal
hypotheses per cell / 13,680 globally, and preserves the 54 global shortlist /
18 global frozen caps.

Evidence remains `RETROSPECTIVE_ALREADY_SEEN`, `untouched_oos=false`, with
`reserved_robustness_opened=false`. Result-state labels are descriptive only:
zero qualifiers, qualifiers without frozen carry-forward, or frozen retrospective
carry-forward present. None constitutes validation, promotion, or trading
authority.

DEC-467 binds merged DEC-466
`5faa733572576aa5a1c56176ac27c415eaaf6416`, runtime-authorization blob
`ccc99179a51145534e1b48b8520b2f743580c217`, read-only dispatch-operator blob
`6a386c556e121d959ec1ea8bbb56dbb49b42dde2`, and DEC-463 evidence-contract
blob `ca68622ddfc9866f00569d558b2ab927be23686d`.

Review-contract source
`src/fmp/discovery/exp065_historical_result_review_contract.py` is blob
`d10bade3857beaec6e977525b651e66156dce87e`; focused tests
`tests/test_phase8a_exp065_historical_result_review_contract.py` are blob
`eb4a43906a24b7b6301df732f108110895c6755d`.

Rerun, retry, replacement, reserved 2023-2026 robustness access, candidate
compilation, promotion, Phase 8B, demo/live orders, broker mutation, real-money
action, and trading remain false.

Next gate: `FREEZE_EXP065_HISTORICAL_RESULT_AFTER_TERMINAL_RUN`.
## DEC-468 — Freeze EXP-065 historical result

**Date:** 2026-10-02  
**Status:** HISTORICAL RESULT REVIEWED AND FROZEN / NO PAIRWISE-INTERACTION QUALIFIERS

DEC-468 freezes the sole authorized EXP-065 historical run, GitHub Actions run
`36905224184`, workflow `phase8a-exp065-pairwise-interaction`, head
`5faa733572576aa5a1c56176ac27c415eaaf6416`, run number 1, attempt 1, as the
terminal one-shot result.

Exactly 20 jobs completed successfully and exactly 20 artifacts are present and
non-expired. Aggregate artifact id `11202316160` is
`phase8a-exp065-aggregate-5faa733572576aa5a1c56176ac27c415eaaf6416`
with artifact digest
`sha256:55e3a725127a1195a23159a6f8f8e187d90443f6e4df1be213a143c8e8868214`.

The downloaded aggregate JSON SHA-256 is
`080d9e36c572d570f7890b51d543cb00821ba25f76164a6c6d289d9b6ccb8a62`.
Its canonical evidence fingerprint is
`be0822560c0c4ec5a7dfc90e85c65d963621e04a4bd238ea078a4ac4d7a99682`,
and independent recomputation matched exactly.

All 18 cell evidence artifacts were independently inspected and recomputed. Every
cell contains 760 nominal hypotheses / 760 evaluable hypotheses and reports zero
qualifying hypotheses, zero deduplicated hypotheses, an empty pairwise-interaction
shortlist, and an empty frozen inventory. Across the frozen 18-cell universe this
is 13,680 hypotheses / 13,680 evaluable, with zero qualifying, zero deduplicated,
zero shortlisted, and zero frozen. Every cell evidence fingerprint recomputed and
matched the aggregate inventory.

Classification:
`NO_PAIRWISE_INTERACTION_HYPOTHESIS_PASSED_FROZEN_GATE`.

This negative result applies only to the exact frozen EXP-065 pairwise-interaction
representation and protocol. EXP-065 is one bounded sub-experiment inside the
governing DEC-268 discovery-first market-pattern research framework; this result
does not reject that framework, establish that no market edge exists, or exhaust
other market-behaviour representations.

Evidence remains `RETROSPECTIVE_ALREADY_SEEN`, `untouched_oos=false`, with
`reserved_robustness_opened=false`. The reserved 2023-01-01 through 2026-08-20
block remains unopened and unauthorized.

The one-shot slot is consumed permanently. Rerun, retry, replacement, reserved
robustness access, candidate compilation, promotion, Phase 8B, demo/live orders,
broker mutation, real-money action, and trading remain false.

Review source
`src/fmp/discovery/exp065_historical_result_review.py` is blob
`12580fe033a29d4d25b61140a4cf53a7126547ea`; focused tests
`tests/test_phase8a_exp065_historical_result_review.py` are blob
`c895d49ef6e25dfabf8a03e53c7fc10143f7eea7`.

Next gate: `EXPLICIT_POST_EXP065_DISCOVERY_FIRST_RESEARCH_DIRECTION_DECISION`.
Any successor direction must satisfy `docs/research-method-operating-guardrail.md`
and map back to the broader discovery-first workflow; there is no automatic
authorization for another transform, model family, historical run, or reserved-data
access.

## DEC-469 — Make annual pattern catalogues the governing discovery workflow

**Date:** 2026-10-02  
**Status:** GOVERNING RESEARCH-METHOD AMENDMENT / EXECUTION LOCKED

DEC-469 binds the operator's clarified research method after frozen EXP-065
DEC-468 evidence and supersedes the idea that the next narrow mathematical
representation should become the main research direction.

The governing workflow is now:

`historical collection -> year-by-year pattern catalogues -> freeze each annual
catalogue -> cross-year pattern comparison -> Strategy V1 synthesis -> freeze
Strategy V1 -> robustness/backtest -> prospective shadow -> fixed-version demo ->
completed demo evidence review -> new immutable challenger -> fresh prospective
evidence`.

“Every pattern” means every pattern surfaced by a predeclared bounded discovery
grammar for the annual segment. Annual catalogues must preserve qualifiers,
non-qualifiers, negative/failed patterns, support, after-cost outcomes, context,
and effective search volume. The project may not retain only profitable winners.

Each annual catalogue must be frozen before cross-year synthesis. Cross-year
comparison must use canonical pattern identities and inspect recurrence, support,
effect direction/magnitude, after-cost economics, pair/timeframe/horizon context,
failure years, sign reversals, and concentration. One spectacular year cannot
define Strategy V1.

State transitions, pairwise interactions, clustering/statistical estimators, model
families, and named rule families are now explicitly pattern types/tools inside the
annual catalogue. None is the governing method by itself.

Strategy V1 may be synthesized only under a later explicit gate from frozen
cross-year catalogue evidence. It must receive an immutable version identity and
freeze exact LONG/SHORT/NO TRADE, applicability, conflict, entry/exit, cost, and
risk semantics before prospective evidence.

The improvement loop preserves fixed-version evidence. Strategy V1 first goes
through prospective shadow and then fixed-version demo. Completed shadow/demo
evidence may be analysed to build Strategy V2, but Strategy V1 cannot self-modify
or hot-swap while running. Once demo evidence influences Strategy V2, that evidence
is research/training evidence for V2 and V2 must later prove itself on fresh
prospective evidence.

The historical collection spans full years 2015-2025 plus partial 2026 through
2026-08-20. DEC-469 does not silently open protected 2023-2026 history. At this
gate 2015-2022 remains the already-open retrospective block; a separate explicit
decision is required before 2023-2026 joins the annual catalogue. Any historical
year used to build Strategy V1 becomes retrospective research/training evidence
and cannot later be called fresh validation for Strategy V1.

PR #617 (`phase8a-exp066-temporal-transition-direction`) was closed unmerged
before DEC-469 landed. Its proposed temporal-transition direction has no
source-of-truth authority; temporal transitions remain only a possible pattern type
inside the annual catalogue.

Method source
`src/fmp/discovery/annual_pattern_catalogue_method.py` is blob
`d7486296c2e953d6b4e7602c753c5529ccf5eef2`; focused tests
`tests/test_phase8a_annual_pattern_catalogue_method.py` are blob
`293159fa6e38cd7111a721ba808e8e958efac340`; governing amendment spec
`docs/superpowers/specs/2026-10-02-phase8a-annual-pattern-catalogue-method.md`
is blob `f1436b4c155b99c31477a392acbf89ba9e6e2998`.

Historical annual-catalogue execution, protected 2023-2026 access, Strategy V1
synthesis, candidate compilation, promotion, Phase 8B, demo/live orders, broker
mutation, real-money action, and trading remain false.

Next gate:
`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_PROTOCOL_AND_PROTECTED_HISTORY_ACCESS_DECISION`.

## DEC-470 — Freeze annual pattern catalogue protocol and full-collection research scope

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY PROTOCOL FROZEN / HISTORICAL EXECUTION LOCKED

DEC-470 binds merged DEC-469 commit
`248ee27036d54c2ce3ad3ad051dcc8b0cbbbcfd1` and turns the annual-first
method into a fixed Catalogue V1 protocol before any annual catalogue is run.

The full accepted historical collection is now authorized for this research path:
full years 2015-2025 plus partial 2026 through 2026-08-20. The 2023-2026 block
that EXP-061 through EXP-065 kept closed is repurposed only for DEC-469 annual
catalogue / Strategy V1 research. This does not reopen or rerun those experiments.
It also removes any future claim that 2023-2026 is untouched OOS for Strategy V1
once catalogue evidence from those years is used. Fresh Strategy V1 evidence starts
only after the exact Strategy V1 version is frozen.

Catalogue V1 reuses the accepted three pairs, three timeframes, two fixed horizons,
20 continuous measurements, deterministic session state, and existing full-history
market-feature/outcome materialization. No new raw data, feature, symbol,
timeframe, horizon, or alternative data source is authorized.

Continuous state encoding is strict prior-only expanding empirical tertiles within
the same annual segment. At T, only rows with `available_at_utc < T` may
calibrate the state, with at least 300 finite prior values. Future rows in the year
cannot affect an earlier state.

The bounded grammar is exactly:

- 65 snapshot single-state conditions;
- 2,010 two-dimension snapshot conditions;
- 410 same-dimension prior-state -> current-state transitions at exact 60m/240m lags.

Total = 2,485 conditions, 4,970 LONG/SHORT hypotheses per cell/horizon,
89,460 directional hypotheses per annual segment, and 1,073,520 nominal annual
directional records across 12 annual segments. The canonical cross-year universe is
89,460 hypotheses because year is excluded from the canonical pattern identity.

Every annual pattern record is preserved. Support below 75 is labeled insufficient
but is not deleted. Evaluable records retain support, base/stress means, medians,
and base-cost win rate. Annual catalogues do not select or rerank winners.

Before results exist, DEC-470 also freezes the cross-year carry-forward gate:
minimum 9 evaluable segments; at least 80% base-positive years; at least 2/3
stress-positive years; median annual base mean >= 0.10 pips; pooled base mean
>= 0.25 pips; pooled stress mean > 0; and at most 3 chronological sign flips.
Ranking, Jaccard 0.90 within-cell/family/direction deduplication, and a cap of
5 per cell/family / 270 globally are fixed in the protocol. A carry-forward row is
still pattern evidence, not Strategy V1.

Protocol source
`src/fmp/discovery/annual_pattern_catalogue_protocol.py` is blob
`5ddd987cc480e6e31c0cd45328eba16cf690dee9`; focused tests
`tests/test_phase8a_annual_pattern_catalogue_protocol.py` are blob
`5b7dfe896fd2f84135a0bf927189c129a928dafd`; protocol spec
`docs/superpowers/specs/2026-10-02-phase8a-annual-pattern-catalogue-protocol.md`
is blob `d90ab2522b37bd340e9a3d5a536a7dd7d55d7d1f`.

Historical artifact reads, annual catalogue execution/result production, cross-year
result production, Strategy V1 synthesis, candidate compilation, promotion,
Phase 8B, demo/live orders, broker mutation, real-money action, and trading remain
false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_MINER`.

## DEC-471 — Implement source-only annual pattern catalogue miner

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY MINER / HISTORICAL EXECUTION LOCKED

DEC-471 binds merged DEC-470 commit
`e5b20a2d8b45e5eda54673060060fbb9f480f545` and exact protocol blob
`5ddd987cc480e6e31c0cd45328eba16cf690dee9`.

It implements the frozen Catalogue V1 grammar in memory for one annual segment ×
symbol × timeframe × horizon at a time. No artifact loader, workflow, historical
execution surface, or result authority is added.

Continuous states are computed with a deterministic order-statistic structure using
only finite same-year observations strictly earlier than the current timestamp.
A state remains unavailable until 300 prior finite observations exist. The current
row is inserted only after its state is encoded, so later annual rows cannot alter
earlier states.

Session state retains the accepted deterministic precedence. Snapshot singles and
pairs use exact state-event sets. Same-dimension transitions require an observation
at the exact frozen T-60m or T-240m timestamp; nearby rows cannot substitute.

Both the current observation and its fixed-horizon exit must remain inside the same
annual segment. Outcomes crossing into the next annual segment are excluded from
that year's catalogue.

For every one of the 2,485 frozen conditions, DEC-471 emits both LONG and SHORT,
so each annual cell/horizon result contains exactly 4,970 directional records.
Weak, negative, insufficient-support, and zero-support records remain present.
Support below 75 is non-evaluable but not deleted. Supported rows retain base/stress
means and medians, base-cost win rate, canonical cross-year identity, annual record
identity, and deterministic event-set fingerprint.

The miner deliberately contains no winner selection, reranking, cross-year gate,
Strategy V1 synthesis, candidate compilation, or promotion logic.

Miner source
`src/fmp/discovery/annual_pattern_catalogue_miner.py` is blob
`2f4c9327a2b9600aceaa1e272dc613dfd4e7d0b7`; focused tests
`tests/test_phase8a_annual_pattern_catalogue_miner.py` are blob
`9942d5d1a87825541cd0dc0a96d44c204c8e11d0`; source spec
`docs/superpowers/specs/2026-10-02-phase8a-annual-pattern-catalogue-miner.md`
is blob `654eac134dea4648f2ba0a0e19ce39c416c4cbcc`.

Historical artifact reads, catalogue execution/result production, cross-year result
production, Strategy V1 synthesis, candidate compilation, promotion, Phase 8B,
demo/live orders, broker mutation, real-money action, and trading remain false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_EVIDENCE_CONTRACT`.

## DEC-472 — Freeze annual pattern catalogue evidence contract

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY EVIDENCE CONTRACT / HISTORICAL EXECUTION LOCKED

DEC-472 binds merged DEC-471 commit
`3926daa8b64ca18c69d5a95a7b31b960dddde27b` and exact miner blob
`2f4c9327a2b9600aceaa1e272dc613dfd4e7d0b7`.

Each annual cell payload serializes the complete DEC-471 result: one annual segment ×
symbol × timeframe × horizon with all 4,970 directional records. Canonical JSON
bytes receive an exact SHA-256 and byte-length binding.

The validator does not trust the outer hash alone. After hash verification it
reconstructs the full DEC-470 pattern/direction universe in frozen order and checks
every annual record identity, canonical cross-year fingerprint, family, dimensions,
states, lag, event fingerprint, support/evaluable relation, and all base/stress
statistics. LONG/SHORT rows for the same pattern must bind the same event set.
Therefore a nested-record tamper remains invalid even if the payload and outer
evidence hashes are recomputed.

Cell evidence also binds the exact code commit, processed source manifest, feature
and outcome manifests, aggregate feature/outcome evidence fingerprints, protocol
fingerprint, DEC-471 miner blob, row counts, and summary counts. All runtime and
strategy/trading authority flags remain false.

The full-collection aggregate is exactly 12 annual segments × 18
symbol/timeframe/horizon cells = 216 annual cells. Every cell has exactly 4,970
directional records, so the aggregate nominal inventory is exactly 1,073,520
directional records. Missing/duplicate cells, ordering drift, code-commit mismatch,
segment-summary mismatch, record-count drift, and downstream authority drift all
fail closed.

Full aggregate replay must use summaries created only after full cell-payload
semantic validation; aggregate hashing never substitutes for validating the
underlying cell catalogue bytes.

Evidence source
`src/fmp/discovery/annual_pattern_catalogue_evidence.py` is blob
`c2565dc35e5bf43e1f1730a84c922a9aed5a9b3b`; focused tests
`tests/test_phase8a_annual_pattern_catalogue_evidence.py` are blob
`8711b5f310422abfcb53ab7a4f2f3897803d0ded`; spec
`docs/superpowers/specs/2026-10-02-phase8a-annual-pattern-catalogue-evidence.md`
is blob `59c257fafe49b729d9157a4094c7600c89f0b1be`.

Historical artifact reads, annual catalogue execution/result production, cross-year
result production, Strategy V1 synthesis, candidate compilation, promotion,
Phase 8B, demo/live orders, broker mutation, real-money action, and trading remain
false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_FULL_HISTORY_LOADER`.

## DEC-473 — Freeze source-only annual catalogue full-history loader

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY LOADER / HISTORICAL EXECUTION LOCKED

DEC-473 binds merged DEC-472 commit
`310d31183802a2c29aad3f20ad6a6aa4990d579d`.

DEC-473 opens no historical run. It defines the verified loader boundary from the
already accepted EXP-044 full-history feature/outcome materialization into the
DEC-470/471 year-by-year catalogue.

The loader covers exactly 140 monthly partitions from 2015-01 through 2026-08 and
exposes only the 12 DEC-469 annual segments. Each call is scoped to one annual
segment × symbol × timeframe. Selected feature/outcome files are verified against
their accepted manifests for path containment, byte size, SHA-256, exact schema,
and row count.

EXP-044 aggregate feature/outcome evidence fingerprints are recomputed and checked;
the requested cell manifests must match those evidence indexes, preserve the same
processed-source identity, and retain the outcome-to-feature bindings.

Annual isolation is fail-closed at the loader boundary: feature availability must
remain inside the requested segment, and outcome availability plus fixed-horizon
exit must remain inside the same segment. The 2026 partial segment ends at
2026-08-20 inclusive.

Loader source
`src/fmp/discovery/annual_pattern_catalogue_loader.py` is blob
`6be734930dd7758932c664439b6149a7a84902d6`; focused tests
`tests/test_phase8a_annual_pattern_catalogue_loader.py` are blob
`63c5b3b4a819a4b5e0fbb29fe721576fd640651b`; spec
`docs/superpowers/specs/2026-10-02-phase8a-annual-pattern-catalogue-full-history-loader.md`
is blob `6e079fca5115bf1753c4491474578b9b79669b40`.

New data acquisition, feature/outcome materialization, historical artifact-read
authorization, catalogue execution/result production, cross-year results, Strategy
V1 synthesis, candidate compilation, promotion, Phase 8B, demo/live, broker
mutation, real-money action, and trading remain false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_SEGMENT_ADAPTER`.

## DEC-474 — Freeze source-only annual catalogue segment adapter

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY ADAPTER / HISTORICAL EXECUTION LOCKED

DEC-474 converts only a verified DEC-473 annual-segment bundle into the exact
`FeatureObservation` and `OutcomeObservation` types consumed by DEC-471. The
public adapter does not accept arbitrary raw frames, so the processed-source,
feature/outcome manifest, aggregate evidence, and selected-artifact identities
remain attached to the adapted input bundle.

The adapter removes the obsolete EXP-061 2015-2022 range restriction without
weakening annual isolation. Feature/outcome availability must remain inside the
requested DEC-469 segment, outcome exits must remain strictly before that segment's
end, and every outcome observation identity must match an adapted feature identity.

Observation IDs preserve the accepted canonical EXP-044/EXP-061 identity projection.
Feature availability must equal bar start plus the exact timeframe. Outcome
`OutcomeObservation` construction additionally enforces the exact 60m/240m horizon
exit identity.

Non-finite continuous feature values are normalized to null before
`FeatureObservation` construction, preserving the accepted DEC-293 behavior and
DEC-471 unavailable-state semantics.

Adapter source
`src/fmp/discovery/annual_pattern_catalogue_adapter.py` is blob
`6fa40df869df179852145bd8b06ace26bfbd6aa7`; focused tests
`tests/test_phase8a_annual_pattern_catalogue_adapter.py` are blob
`666b2fc8a3df4e4cd5d0eeb90ce613dcb4336388`; spec
`docs/superpowers/specs/2026-10-02-phase8a-annual-pattern-catalogue-segment-adapter.md`
is blob `431668a7cfac9c26ba4fd942744d0ea0c922ee85`.

Historical artifact reads, annual catalogue execution/result production, cross-year
results, Strategy V1 synthesis, candidate compilation, promotion, Phase 8B,
demo/live orders, broker mutation, real-money action, and trading remain false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_RUNTIME_WIRING`.

## DEC-475 — Freeze source-only locked annual catalogue runtime wiring

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY LOCKED RUNTIME / HISTORICAL EXECUTION LOCKED

DEC-475 binds merged DEC-474 commit
`d88d5bb2f5d1f76278c4d588136bbcc5e65731a7`.

DEC-475 composes the frozen annual-catalogue source path in the exact order
authorization gate -> DEC-473 loader -> DEC-474 adapter -> DEC-471 miner -> DEC-472
cell evidence compiler.

The unit of work remains one annual segment × symbol × timeframe × horizon.
`run_locked_annual_catalogue_cell` calls the authorization gate before the
filesystem-backed loader. The gate requires historical artifact-read, catalogue
execution, and historical result-production authority. All three remain false, so
the runtime cannot currently reach any historical evidence index, manifest, or
Parquet partition.

No workflow, workflow dispatch, CLI execution surface, cross-year aggregation, or
Strategy V1 synthesis is installed by this decision.

Runtime source
`src/fmp/discovery/annual_pattern_catalogue_runtime.py` is blob
`0044c19575ec005a31ab98beefccfc57fe9e72da`; focused tests
`tests/test_phase8a_annual_pattern_catalogue_runtime.py` are blob
`b495272bc0302cb6bec3f142778332b96e2abac7`; spec
`docs/superpowers/specs/2026-10-02-phase8a-annual-pattern-catalogue-runtime-wiring.md`
is blob `a0f9e58063e4ec1c0c98071fe766c23811ebb684`.

Historical artifact reads, annual catalogue execution/result production, cross-year
results, Strategy V1 synthesis, candidate compilation, promotion, Phase 8B,
demo/live orders, broker mutation, real-money action, and trading remain false.
Workflow installed and workflow dispatch authority are also false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_PLAN`.

## DEC-476 — Freeze annual catalogue workflow plan

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY WORKFLOW PLAN / NO WORKFLOW INSTALLED

DEC-476 binds merged DEC-475 commit
`db8285dab5a0311abbbb77c60c958771b17074a5`.

DEC-476 freezes the future annual-catalogue execution shape without installing a
workflow. The run unit is one annual segment, not the full 216-cell collection.

Each future annual-segment run is exactly one preflight job + 18 cell jobs
(3 symbols × 3 timeframes × 2 horizons) + one annual freeze job = 20 jobs. The
freeze job depends on all 18 same-year cells.

The full collection remains exactly 12 segments × 18 cells = 216 cells, but the
required operating sequence is 2015, 2016, ..., 2025, then
`2026_YTD_TO_2026_08_20`, with each annual segment frozen before the next becomes
authoritative. A single 216-cell execution is explicitly forbidden.

Cross-year comparison cannot begin until all required annual freezes exist. DEC-476
adds no ranking, deduplication, Strategy V1 synthesis, or result authority.

Workflow-plan source
`src/fmp/discovery/annual_pattern_catalogue_workflow_plan.py` is blob
`2c3755d5cc344971a64d61937314b0f3bef0674d`; focused tests
`tests/test_phase8a_annual_pattern_catalogue_workflow_plan.py` are blob
`56281cafd839f035f04bd57c2726ba7764786eea`; spec
`docs/superpowers/specs/2026-10-02-phase8a-annual-pattern-catalogue-workflow-plan.md`
is blob `0ee1328d78d8818abce2c02820b2ece7b51df108`.

Workflow source authorization, installation, dispatch, historical artifact reads,
catalogue execution/results, cross-year results, Strategy V1 synthesis, promotion,
Phase 8B, demo/live, broker mutation, real-money action, and trading remain false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_SEGMENT_FREEZE_CONTRACT`.

## DEC-477 — Freeze annual segment evidence contract

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY ANNUAL FREEZE CONTRACT / HISTORICAL EXECUTION LOCKED

DEC-477 binds merged DEC-476 commit
`23ca37a74296a8ad0ac5e4cd1775c3b76714f698`.

DEC-477 defines the independently verifiable freeze for one complete annual
catalogue segment before any later segment can become authoritative.

The freeze accepts exactly 18 validated DEC-472 cell summaries for one year:
3 symbols × 3 timeframes × 2 horizons. Since every validated cell binds 4,970
directional records, one annual freeze binds exactly 89,460 directional records.

Missing, duplicate, cross-year, or mixed-code-commit cells fail closed. Input order
is canonicalized into the frozen cell order before fingerprinting. Aggregate annual
counts are recomputed from the bound cell summaries, so rehashed outer-total
tampering still fails validation.

A valid DEC-477 freeze does not authorize the next year. It also does not authorize
cross-year comparison or Strategy V1 synthesis. Those remain separate later gates.

Freeze source
`src/fmp/discovery/annual_pattern_catalogue_segment_evidence.py` is blob
`1b14279864f01a1284c5be31552eee9bb3a2220c`; focused tests
`tests/test_phase8a_annual_pattern_catalogue_segment_evidence.py` are blob
`51dbf4e1a5be898f0a44d25f7bb1bd0c7696d112`; spec
`docs/superpowers/specs/2026-10-02-phase8a-annual-pattern-catalogue-segment-freeze.md`
is blob `6aa367c29705fbba3ab8774548add6c05ef7b557`.

Historical artifact reads, annual catalogue execution/result production,
next-segment execution, cross-year results, Strategy V1 synthesis, promotion,
Phase 8B, demo/live, broker mutation, real-money action, and trading remain false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_SOURCE`.

## DEC-478 — Freeze dormant annual catalogue workflow source

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY DORMANT WORKFLOW / NOT INSTALLED

DEC-478 freezes a disabled annual-catalogue workflow source without creating the
reserved active workflow path.

The future run input is exactly one of the 12 DEC-469 annual segments. The CLI
validates the same segment set independently.

Each future segment run contains one preflight job, 18 cell jobs, and one annual
freeze job. Every cell emits both DEC-472 cell evidence and the complete catalogue
payload; the freeze job downloads the same-segment artifact pattern and compiles
one DEC-477 annual freeze. There is no full-collection aggregate or cross-year job.

The source now also enforces the DEC-476 sequential-year boundary: 2015 requires no predecessor, while every later segment must supply the immediately prior successful annual-catalogue run and a semantically valid DEC-477 freeze whose code commit equals that run head. The execution gate remains before any prior-freeze artifact download.

The dormant source reuses only the accepted EXP-044 feature/outcome runs, evidence
artifacts, and nine pair/timeframe source artifacts. Each cell rechecks the locked
execution gate before any accepted historical artifact ZIP is downloaded, and the
freeze job rechecks the gate before any historical cell-result artifact is opened.

Source contract
`src/fmp/discovery/annual_pattern_catalogue_workflow_source.py` is blob
`6276e8a86cd1af4b2e4f0d9795ed8ec531800fde`; dormant CLI
`scripts/phase8a_annual_pattern_catalogue.py` is blob
`ec5ea311b6c46d71cbdac9bf2bfb76d66fcce0f3`; disabled template
`docs/superpowers/templates/phase8a-annual-pattern-catalogue.yml.disabled` is blob
`31633e87b79551f5b7dfa6b0deb76a82eb070129`; focused tests are blob
`68d96c90899d8b98ba887f808d112d21455f52bd`; spec is blob
`74d49027bf175c60682268b9349d91cac77a84e3`.

The active workflow path remains absent. Template installation, workflow
installation/dispatch, historical artifact reads, catalogue execution/result
production, next-segment execution, cross-year results, Strategy V1 synthesis,
promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading
remain false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_CONTRACT`.

## DEC-479 — Freeze annual catalogue workflow installation contract

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY INSTALL CONTRACT / REPOSITORY MUTATION LOCKED

DEC-479 binds the merged DEC-478 authority
`aaf4ea66b2b5b908228102dfa387aae7d03ea4d9`.

DEC-479 freezes the exact future repository mutation required to install the
disabled DEC-478 annual-catalogue workflow source, but does not perform it.

The contract binds exact Git blobs for the DEC-478 workflow source module, dormant
CLI, and disabled workflow template. The reserved active workflow path must remain
absent. Source drift or a pre-existing target path fails closed.

The only allowed future mutation is creation of
`.github/workflows/phase8a-annual-pattern-catalogue.yml` from the exact bytes of
`docs/superpowers/templates/phase8a-annual-pattern-catalogue.yml.disabled`.
The dormant template, CLI, and workflow-source contract are forbidden from changing
during that install action, and post-install active bytes must equal the frozen
source bytes exactly.

DEC-479 now also semantically validates the complete install-action payload, including the nested source-blob map, exact source/target paths, allowed/forbidden file sets, and every false authority field. A nested mutation cannot be legitimized by wrapping it in a new outer fingerprint later.

Install-contract source
`src/fmp/discovery/annual_pattern_catalogue_workflow_install_contract.py` is blob
`f9ac5dc517ec3efbb50057ade66c5b5aab2f52b3`; focused tests are blob
`19068defbf5edb0149677ee8f941c9176e14a6dd`; spec is blob
`430f567e6c293615b919313c3ec4366899f91853`.

Repository mutation authorization remains false. Workflow install/dispatch,
historical reads, catalogue execution/results, next-segment execution, cross-year
results, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation,
real-money action, and trading remain false.

Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT`.
## DEC-480 — Freeze read-only annual workflow installation preflight

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY READ-ONLY PREFLIGHT / REPOSITORY MUTATION LOCKED

DEC-480 binds the merged DEC-479 authority
`95750234d3bce325563f15c605c2312756562ee6`.

DEC-480 freezes the read-only preflight for the future DEC-479 annual-catalogue
workflow installation action.

The preflight verifies the exact DEC-479 install-contract Git blob, all transitive
DEC-478 dormant source bindings, exact `main` branch metadata, and continued
absence of the reserved active workflow path. Any source drift or main-head drift
fails closed.

DEC-480 embeds the complete DEC-479 install-action payload and fingerprints it.
The validator recomputes both the outer preflight fingerprint and the embedded
install-action fingerprint, then semantically rechecks every authority field so a
rehashed authority escalation still fails.

The embedded DEC-479 action is also passed through DEC-479's semantic validator, so rehashing a changed nested target path, source blob, or file-mutation set still fails.

The separately reported `install_sources` evidence must also exactly match that validated DEC-479 source-validation payload, so rehashing substituted source evidence fails closed.

The preflight CLI exposes only a `plan` command. There is no install, execute,
dispatch, or advance surface.

Preflight source
`src/fmp/discovery/annual_pattern_catalogue_workflow_install_preflight.py` is blob
`654a51a7bd647afe4664d9ecab81926044c2b824`; focused tests are blob
`9d3ba4f7f0d2824b334a9cddfaa54e7e5211a2a7`; read-only CLI is blob
`f7bb6cdc62511d3dcc907d856f55f06f6302e640`; spec is blob
`0d592089ac3ccd1f92e173fbd6bfe9ba7a63b8ff`.

Repository mutation, workflow installation/dispatch, historical artifact reads,
annual catalogue execution/result production, next-segment execution, cross-year
results, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation,
real-money action, and trading remain false.

Next gate:
`REPOSITORY_HOSTED_READ_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF`.

## DEC-481 — Freeze repository-hosted install-preflight proof contract

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY PROOF CONTRACT / REPOSITORY MUTATION LOCKED

DEC-481 defines the exact evidence contract for a future repository-hosted,
read-only proof of DEC-480.

The proof accepts only a fully validated DEC-480 preflight and binds its preflight
fingerprint plus embedded install-action fingerprint. The supplied main branch and
proof run must resolve to one identical commit.

The future proof run must be an exact successful manual run of the frozen proof
workflow on `main`, run attempt 1, with the exact caller-supplied positive run ID.
Different workflow identity, branch, head SHA, failed conclusion, or rerun fails
closed.

The proof receives a canonical fingerprint, and authority fields remain
semantically checked after fingerprint validation.

The frozen proof itself retains the exact run event, branch, head SHA, attempt, completed status, and successful conclusion. These fields are semantically revalidated after fingerprint verification, so rehashing altered run provenance fails closed.

Proof-contract source
`src/fmp/discovery/annual_pattern_catalogue_workflow_install_preflight_proof.py`
is blob `fb9ea8d4a17734ee91225d48012a0a5b0088d415`; focused tests are blob
`9da2080ccbd82c6c4ffc93358d200cd26b8ecd59`; spec is blob
`f826f4152697c53029e20ad46b41b1b3cc72bebc`.

Repository mutation, annual workflow installation/dispatch, historical artifact
reads, annual catalogue execution/result production, next-segment execution,
cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker
mutation, real-money action, and trading remain false.

Next gate:
`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_SOURCE`.

## DEC-482 — Freeze dormant install-preflight proof workflow source

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY DORMANT PROOF WORKFLOW / NOT INSTALLED

DEC-482 freezes the disabled read-only workflow source needed to generate the
DEC-480 preflight artifact used by the future DEC-481 repository-hosted proof.

The workflow source only checks exact merged-main manual dispatch, fetches read-only
main-branch metadata, runs the DEC-480 plan-only CLI with `GITHUB_SHA` as the
expected head, and uploads `preflight.json`.

It deliberately does not compile DEC-481 proof evidence inside the same run,
because DEC-481 requires completed-success run metadata. A later read-only post-run
gate must bind the completed run identity to the uploaded preflight.

The dormant template contains no annual-cell/freeze execution, `gh workflow run`,
direct locked-runtime call, or repository mutation authorization. The template itself
is pinned to exact Git blob `0d6c93e2af04501f9ac2589fd24d6672b2b41910`,
so any byte drift fails closed before structural validation is accepted.

Workflow-source module
`src/fmp/discovery/annual_pattern_catalogue_workflow_install_preflight_proof_workflow_source.py`
is blob `625c311a8f19633b3ee05459175d640d30762ecc`; focused tests are blob
`2adb9dd755a8fd0665551771b2a912a4b8052239`; disabled template is blob
`0d6c93e2af04501f9ac2589fd24d6672b2b41910`; spec is blob
`b1de031402012bca461d93f7397c5c3f31a4b138`.

Proof-workflow installation/dispatch, annual-workflow installation/dispatch,
historical reads, catalogue execution/results, next-segment execution, cross-year
results, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation,
real-money action, and trading remain false.

Next gate:
`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT`.

## DEC-483 — Freeze proof-workflow installation contract

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY INSTALL CONTRACT / REPOSITORY MUTATION LOCKED

DEC-483 freezes the exact future repository mutation required to install the
disabled read-only DEC-482 proof workflow, but does not perform it.

It binds merged DEC-482 authority
`532ab82a6c028c4f4cdf47d9515f18ef83457c45`, proof-workflow source blob
`625c311a8f19633b3ee05459175d640d30762ecc`, and dormant-template blob
`0d6c93e2af04501f9ac2589fd24d6672b2b41910`.

The DEC-482 source validator must still prove the exact DEC-481 proof-contract and
DEC-480 plan-only CLI dependencies, and the reserved active proof-workflow path
must remain absent.

The only allowed future mutation is creation of
`.github/workflows/phase8a-annual-catalogue-workflow-install-preflight-proof.yml`
from the exact bytes of
`docs/superpowers/templates/phase8a-annual-pattern-catalogue-workflow-install-preflight-proof.yml.disabled`.

The install-action contract uses an exact top-level key set and semantically
validates nested source and mutation evidence. The source template, DEC-482 source
module, DEC-481 proof contract, and DEC-480 preflight CLI are all forbidden from
changing during that future action.

Install-contract source
`src/fmp/discovery/annual_pattern_catalogue_workflow_install_preflight_proof_workflow_install_contract.py`
is blob `91c25b0d80ac05f28f20234a01717bf0af49f4f8`; focused tests are blob
`211c3114b6d9e4168f792202a0419c38e473b8c5`; spec is blob
`652112e80b9ae80c2e4c798d3ccaa7a9830e6b4a`.

Repository mutation, proof-workflow installation/dispatch, annual-workflow
installation/dispatch, historical reads, catalogue execution/results, next-segment
execution, cross-year results, Strategy V1 synthesis, promotion, Phase 8B,
demo/live, broker mutation, real-money action, and trading remain false.

Next gate:
`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_INSTALL_PREFLIGHT`.
## DEC-484 — Freeze read-only proof-workflow installation preflight

**Date:** 2026-10-02  
**Status:** SOURCE-ONLY READ-ONLY PREFLIGHT / REPOSITORY MUTATION LOCKED

DEC-484 freezes the read-only preflight for the future DEC-483 proof-workflow
installation action.

It binds the merged DEC-483 authority
`dedbe26106bbc791e8d13dea49656fcad14bc121` and exact install-contract blob
`91c25b0d80ac05f28f20234a01717bf0af49f4f8`.

The preflight requires exact current-main metadata, the reserved active proof
workflow path to remain absent, the full semantically validated DEC-483 source
report, and the exact one-action install plan.

It fingerprints both the complete preflight and embedded DEC-483 install action,
requires an exact top-level key set, revalidates the nested action semantically, and
requires the separately reported install-source evidence to equal the validated
action evidence. Rehashed authority changes, nested target/source changes,
source-report substitution, or extra fields fail closed.

The CLI exposes only `plan`; there is no install, execute, dispatch, or advance
surface.

DEC-484 terminates proof-workflow installation recursion. A read-only proof workflow
must not require another proof workflow to prove installation of the workflow that
would produce that proof. The preflight therefore records
`proof_workflow_install_operator_authorization_required = true` while every actual
install, dispatch, historical-execution, and trading authority remains false.

The unopened provisional DEC-485 and DEC-486 recursive-bootstrap branches are
superseded by this decision and are non-authoritative. They must not be opened or
merged.

Preflight source
`src/fmp/discovery/annual_pattern_catalogue_workflow_install_preflight_proof_workflow_install_preflight.py`
is blob `ab434212007f3777fa4436a51268438ea44be6dd`; plan-only CLI is blob
`68b2dd39c9d08ff6e0c9568b5017a6c4c76273e7`; focused tests are blob
`1184567227c93fe1bbc523a257c2d68ccb07e22d`; spec is blob
`92ab149f1818d32953d2f5ddd40bea6738add386`.

Repository mutation, proof-workflow installation/dispatch, annual-workflow
installation/dispatch, historical reads, catalogue execution/results, next-segment
execution, cross-year results, Strategy V1 synthesis, promotion, Phase 8B,
demo/live, broker mutation, real-money action, and trading remain false.

Next gate:
`EXPLICIT_OPERATOR_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_INSTALL_AUTHORIZATION`.
## DEC-485 — Annual catalogue preflight proof workflow installed

**Date:** 2026-10-03  
**Status:** PROOF WORKFLOW INSTALLED / DISPATCH LOCKED

DEC-485 records completion of the single exact repository mutation authorized
after DEC-484.

The active proof workflow is installed at
`.github/workflows/phase8a-annual-catalogue-workflow-install-preflight-proof.yml`
and is byte-for-byte identical to dormant template blob
`0d6c93e2af04501f9ac2589fd24d6672b2b41910`.

The receipt pins DEC-484 preflight source blob
`ab434212007f3777fa4436a51268438ea44be6dd` and records the authorization
basis as explicit operator authorization. That one-file installation authorization
is consumed; future repository mutation is locked again.

The installed proof workflow remains manual-only via `workflow_dispatch` with
`contents: read` and `actions: read` permissions. Proof-workflow dispatch,
annual-workflow installation/dispatch, historical artifact reads/execution/results,
next-segment execution, cross-year result production, Strategy V1 synthesis,
promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading
remain false.

Next gate:
`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_BEFORE_RUN`.
## DEC-486 — Annual catalogue proof-workflow dispatch preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY CURRENT-MAIN DISPATCH PREFLIGHT / NO RUN

DEC-486 adds a read-only preflight for the installed annual-catalogue
install-preflight proof workflow.

It pins DEC-485 install-receipt source blob
`638c988524ccf8ada27067c2b0bdb3403823a6f5` and active proof-workflow blob
`0d6c93e2af04501f9ac2589fd24d6672b2b41910`.

A valid preflight requires exact current-main metadata, the exact active workflow,
DEC-485 installed/available state, dispatch authority still false, and zero
proof-workflow runs.

The CLI exposes only `plan`; it has no dispatch, execute, run, install, or advance
surface.

Proof-workflow dispatch, annual-workflow installation/dispatch, historical
reads/execution/results, next-segment execution, cross-year results, Strategy V1
synthesis, promotion, Phase 8B, demo/live, broker mutation, real-money action, and
trading remain false.

Next gate:
`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_BEFORE_RUN`.
## DEC-487 — Annual catalogue proof-workflow first dispatch authorization

**Date:** 2026-10-03  
**Status:** FIRST PROOF DISPATCH AUTHORIZED / RUN NOT STARTED

DEC-487 records explicit operator authorization for exactly one first invocation of
the installed annual-catalogue proof workflow.

It pins DEC-486 dispatch-preflight source blob
`9f5d4b2abbfdb02280b0011a5d61e189be1d6fed` and active workflow blob
`0d6c93e2af04501f9ac2589fd24d6672b2b41910`.

The scope is proof-workflow run #1 / attempt 1 only. Rerun, retry, and replacement
remain forbidden.

This decision authorizes the dispatch but does not trigger it. Repository mutation,
annual-workflow installation/dispatch, historical reads/execution/results,
next-segment execution, cross-year results, Strategy V1 synthesis, promotion,
Phase 8B, demo/live, broker mutation, real-money action, and trading remain false.

Next gate:
`EXACT_FIRST_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`.
## DEC-488 — Annual catalogue proof-workflow run reviewer

**Date:** 2026-10-03  
**Status:** SOURCE-ONLY FUTURE RUN REVIEWER / NO DISPATCH

DEC-488 defines the strict read-only reviewer for the future first successful
annual-catalogue proof-workflow run.

It pins DEC-487 dispatch-authorization source blob
`5efc30607cf30426f099fd8b69bd8d4b8a2a0c9d`, DEC-481 proof-contract blob
`fb9ea8d4a17734ee91225d48012a0a5b0088d415`, and active proof-workflow blob
`0d6c93e2af04501f9ac2589fd24d6672b2b41910`.

A valid review requires proof run #1 / attempt 1, exact current-main identity,
successful proof run and job, an unexpired correctly named artifact, and a
preflight JSON payload that passes the existing DEC-480/481 semantic proof
contract. Raw and canonical payload SHA-256 identities are recorded.

DEC-488 does not trigger anything and cannot claim runtime evidence before it
exists. Repository mutation, further proof dispatch, annual-workflow
installation/dispatch, historical execution/results, Strategy V1 synthesis,
Phase 8B, demo/live, broker mutation, real-money action, and trading remain false.

Next gate after a real proof run:
`CONCRETE_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_RUNTIME_EVIDENCE_FREEZE`.
## DEC-489 — Annual catalogue proof-workflow runtime evidence freeze

**Date:** 2026-10-03  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO RUNTIME EVIDENCE CLAIM

DEC-489 defines the deterministic freeze over a valid DEC-488 review of the first
annual-catalogue proof-workflow run.

It pins DEC-488 run-review source blob
`ec92323d910785d342028c5896528fa1dcf1cc96`.

The freeze preserves exact run/job/artifact identities, raw/canonical preflight
hashes, repository-hosted proof fingerprint, preflight fingerprint, install-action
fingerprint, and the consumed one-shot dispatch authorization. It emits one
canonical `freeze_fingerprint_sha256`.

The source may exist before the real run, but it cannot claim evidence until a
valid DEC-488 review is supplied.

Repository mutation, further proof dispatch, annual-workflow installation/dispatch,
historical execution/results, Strategy V1 synthesis, Phase 8B, demo/live, broker
mutation, real-money action, and trading remain false.

Next gate after real reviewed evidence:
`CONCRETE_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_RUNTIME_EVIDENCE_BINDING`.
## DEC-490 — Annual catalogue proof-workflow concrete runtime evidence binding

**Date:** 2026-10-03  
**Status:** CONCRETE FIRST-RUN RUNTIME EVIDENCE BOUND

DEC-490 binds the exact successful first proof-workflow run:
run `37120635769` / #1 / attempt 1 on main
`6ee059cb451e7c6d2235b7744542dc194acc014e`, proof job
`111195887975`, and artifact `11273008137`.

The artifact ZIP digest is
`3b242f14e89950eb828c614bf1b021dd51d9fc43b9045c2efccc6a1f7bcd8e32`.
The raw/canonical preflight hashes are
`70f6aaaca16fbb5de9e481e135cd8ec85d6dc7c6df524fcf328e23fd0d8de3d3`
and
`f151fcbd487b40be35b54356f7b3002ba416812ec4ece2ea4bd7868cf5c0a163`.

DEC-480/481/489 fingerprints recompute and are pinned; the DEC-490 canonical
binding fingerprint is
`e45d7f3d88ea93e989da32d6f98c22837dfbe5937e7c1fa37260aadd88b256e3`.

The one-shot proof-dispatch authorization is consumed. Further proof dispatch,
repository mutation, annual-workflow installation/dispatch, historical execution,
Strategy V1 synthesis, Phase 8B, demo/live, broker mutation, real-money action,
and trading remain false.

Next gate:
`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_AUTHORIZATION_BEFORE_MUTATION`.
## DEC-491 — Annual catalogue workflow install receipt

**Date:** 2026-10-03  
**Status:** ANNUAL WORKFLOW INSTALLED / EXECUTION LOCKED

DEC-491 records the consumed explicit operator authorization and installed state
for the annual-pattern-catalogue workflow.

It pins DEC-490 runtime-evidence-binding source blob
`ed6eccd796a6c35f9ed768a4bc1ce2d4ae78f830`, DEC-479 install-contract source blob
`f9ac5dc517ec3efbb50057ade66c5b5aab2f52b3`, and exact dormant/active workflow
blob `31633e87b79551f5b7dfa6b0deb76a82eb070129`.

The active workflow is byte-identical to the frozen dormant template, remains
manual-dispatch only with read-only repository/action permissions, and retains
three separate execution gates.

The install authorization is consumed. Further repository mutation,
annual-workflow dispatch, historical artifact reads, annual catalogue execution,
result production, cross-year results, Strategy V1 synthesis, promotion, Phase 8B,
demo/live, broker mutation, real-money action, and trading remain false.

Next gate:
`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_EXECUTION_AUTHORIZATION_BEFORE_RUN`.
## DEC-492 — 2015 annual catalogue execution preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY FIRST-RUN PREFLIGHT / EXECUTION LOCKED

DEC-492 defines the read-only preflight for the first 2015 annual-pattern-catalogue
run after DEC-491 installed the exact workflow.

It pins DEC-491 install-receipt source blob
`970ab466dfa5f87c6955ad65da4653a993e9d6fd`, DEC-475 runtime source blob
`0044c19575ec005a31ab98beefccfc57fe9e72da`, and active workflow blob
`31633e87b79551f5b7dfa6b0deb76a82eb070129`.

The preflight requires exact current main, zero annual-workflow runs, expected
first run #1 / attempt 1, annual segment 2015, and no predecessor evidence.

It exposes only a plan command and keeps workflow dispatch, historical artifact
reads, annual catalogue execution/results, next-segment execution, Strategy V1,
promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading
false.

Next gate:
`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_EXECUTION_AUTHORIZATION_BEFORE_RUN`.
## DEC-493 — First 2015 annual catalogue execution authorization

**Date:** 2026-10-03  
**Status:** FIRST 2015 RUN AUTHORIZED / NOT STARTED

DEC-493 records explicit operator authorization for exactly annual segment
`2015`, workflow run #1, attempt 1.

It pins DEC-492 execution-preflight source blob
`d36343a6f2c69ccc2f942e537f5599cbc92b263b`, DEC-491 install-receipt source blob
`970ab466dfa5f87c6955ad65da4653a993e9d6fd`, and active annual workflow blob
`31633e87b79551f5b7dfa6b0deb76a82eb070129`.

The runtime gate now recognizes only that exact 2015 first-run identity from the
workflow-dispatch event and GitHub run-number/attempt metadata. The default DEC-475
path remains locked.

Rerun, retry, replacement, 2016+, next-segment execution, cross-year results,
Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation,
real-money action, and trading remain false.

Next gate:
`EXACT_FIRST_2015_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`.
## DEC-494 — First 2015 annual catalogue dispatch preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY FIRST DISPATCH PREFLIGHT

DEC-494 defines the final read-only preflight before the explicitly authorized
first 2015 annual-pattern-catalogue workflow dispatch.

It pins DEC-493 authorization source blob
`b5f394f7921d78f73636e28892575cbf4b64a95c`, DEC-493 runtime blob
`4f23996b90b4253af06774d0330003179264c8ee`, and active workflow blob
`31633e87b79551f5b7dfa6b0deb76a82eb070129`.

It requires exact current main, zero annual-workflow runs, segment 2015, empty
previous-freeze input, and expected run #1 / attempt 1.

The CLI is plan-only and contains no dispatch surface. Rerun, retry, replacement,
2016+, Strategy V1, promotion, Phase 8B, demo/live, broker mutation, real-money
action, and trading remain false.

Next gate:
`EXACT_FIRST_2015_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`.

## DEC-495 — First 2015 annual catalogue run failure receipt

**Date:** 2026-10-03  
**Status:** FIRST RUN CONSUMED / FAILED BEFORE CELL EXECUTION

The first authorized 2015 workflow invocation is bound as run
`37126711695`, run #1 / attempt 1, on
`fd85a886d07234ad584dcca08692b37e6af54b2e`.

The preflight job `111213380390` passed source validation, 2015 execution
authorization, and the no-predecessor check, then failed only at
`Upload annual catalogue preflight evidence`.

Root cause: `actions/upload-artifact@v6` defaults
`include-hidden-files: false` while the workflow used `.preflight`.

No annual cells ran and no catalogue/freeze results were produced. The first-run
authorization is consumed. Rerun, retry, and replacement-run authority remain false.

## DEC-496 — Annual catalogue hidden-artifact upload repair

**Date:** 2026-10-03  
**Status:** UPLOAD PACKAGING REPAIRED / REPLACEMENT EXECUTION LOCKED

The annual workflow now sets `include-hidden-files: true` on exactly its three
artifact upload steps for `.preflight`, `.result`, and
`.annual-freeze/annual-freeze.json`.

The pre-repair workflow remains frozen at blob
`31633e87b79551f5b7dfa6b0deb76a82eb070129`; the repaired workflow is
`f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

No replacement execution is authorized by the repair.

Next gate:
`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_REPLACEMENT_RUN_AUTHORIZATION_BEFORE_DISPATCH`.

## DEC-497 — 2015 replacement-run dispatch preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY REPLACEMENT PREFLIGHT / AUTHORIZATION LOCKED

DEC-497 defines the read-only preflight for a possible replacement 2015 annual-pattern-catalogue run.

It requires exact current main, exactly one prior annual workflow run, and that run
must be the consumed failed run `37126711695` / #1 / attempt 1 on
`fd85a886d07234ad584dcca08692b37e6af54b2e`.

It pins DEC-495 failure-receipt source blob
`1ae96e83dc5d895dce1c5f981f1c785401de22f5`, DEC-496 repair source blob
`adfa75b352a561667b8c23efbcfb07af804d1131`, and repaired workflow blob
`f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

Expected replacement identity is run #2 / attempt 1. The CLI is plan-only.
Replacement execution remains unauthorized.

Next gate:
`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_REPLACEMENT_RUN_AUTHORIZATION_BEFORE_DISPATCH`.

## DEC-498 — 2015 replacement execution authorization

**Date:** 2026-10-03  
**Status:** REPLACEMENT RUN #2 / ATTEMPT 1 AUTHORIZED / NOT STARTED

DEC-498 records standing operator authorization to continue the annual-catalogue
build chain autonomously through exactly one repaired 2015 replacement run.

It pins DEC-497 replacement-preflight source blob
`c69f8a9bf1130ae776b06670fba0c63c935afdc1`, DEC-495 failure receipt blob
`1ae96e83dc5d895dce1c5f981f1c785401de22f5`, DEC-496 repair blob
`adfa75b352a561667b8c23efbcfb07af804d1131`, and repaired workflow blob
`f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

The authorized runtime identity is annual segment 2015, run #2, attempt 1 only.
The live runtime now recognizes that identity separately from the consumed run #1
authorization. The old DEC-493 runtime remains preserved as a frozen snapshot.

Rerun of failed run #1, attempt-2 retry, run #3+, 2016+, Strategy V1, promotion,
Phase 8B, demo/live, broker mutation, real-money action, and trading remain false.

Next gate:
`EXACT_2015_REPLACEMENT_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`.

## DEC-499 — Final 2015 replacement dispatch action preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY REPLACEMENT DISPATCH READY

DEC-499 is the final read-only preflight before the single authorized repaired 2015
replacement dispatch.

It pins DEC-498 authorization source blob
`c63fc9f72ad34fa6fd903f2dde8e85570521c9b9`, live replacement runtime blob
`ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b`, and repaired workflow blob
`f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

The live inventory must contain exactly one prior annual run: failed run
`37126711695`, #1 / attempt 1. Expected replacement identity is #2 / attempt 1.

The CLI remains plan-only and contains no dispatch action.

Failed-run retry, run #3+, 2016+, Strategy V1, promotion, Phase 8B, demo/live,
broker mutation, real-money action, and trading remain false.

Next gate:
`EXACT_2015_REPLACEMENT_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`.

## DEC-500 — 2015 replacement-run runtime reviewer

**Date:** 2026-10-03  
**Status:** SOURCE-READY SEMANTIC RUNTIME REVIEW

DEC-500 defines the semantic reviewer for the successful repaired 2015
replacement annual-catalogue run.

It requires run #2 / attempt 1 on exact expected main, exactly 20 successful jobs,
exactly 20 unexpired artifacts, a matching freeze ZIP digest, and a semantically
valid DEC-477 annual-freeze payload for segment 2015 with exactly 18 cells and
89,460 directional records.

The reviewer binds run/job/artifact identities, the annual-freeze evidence
fingerprint, and a canonical review fingerprint.

2016+, cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live,
broker mutation, real-money action, and trading remain false.

Next gate:
`DETERMINISTIC_2015_REPLACEMENT_RUNTIME_EVIDENCE_FREEZE`.

## DEC-501 — 2015 replacement-run runtime evidence freeze

**Date:** 2026-10-03  
**Status:** SOURCE-READY DETERMINISTIC RUNTIME FREEZE

DEC-501 deterministically freezes a valid DEC-500 review of the successful
repaired 2015 replacement annual-catalogue run.

It pins DEC-500 reviewer source blob
`883f82c85d2738c46284d3675278dc061f4ca07c` and preserves the exact run/job/
artifact identities, freeze ZIP SHA-256, canonical annual-freeze payload SHA-256,
DEC-477 evidence fingerprint, annual totals, and DEC-500 review fingerprint.

The output has one canonical `freeze_fingerprint_sha256`.

2016+, cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live,
broker mutation, real-money action, and trading remain false.

Next gate:
`CONCRETE_2015_ANNUAL_PATTERN_CATALOGUE_RUNTIME_EVIDENCE_BINDING`.

## DEC-502 — 2015 concrete runtime evidence binding

**Date:** 2026-10-03  
**Status:** SOURCE-READY CONCRETE RUNTIME BINDING

DEC-502 binds a semantically valid DEC-501 freeze into one canonical 2015 runtime-evidence receipt.

It pins DEC-501 freeze source blob
`8e2a6ab27b4941e3ee12b5463247999200d33e69`, DEC-500 reviewer source blob
`883f82c85d2738c46284d3675278dc061f4ca07c`, and repaired workflow blob
`f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

The binding requires concrete run #2 / attempt 1 success, one preflight job, one
freeze job, exactly 18 cell jobs, exactly 20 artifacts total, matching freeze ZIP
digest, DEC-500/501 fingerprints, 18 annual cells, and 89,460 directional records.

It emits one canonical `binding_fingerprint_sha256`.

2016+, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation,
real-money action, and trading remain false.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_PREFLIGHT`.

## DEC-503 — 2016 annual catalogue execution preflight

**Date:** 2026-10-03  
**Status:** SOURCE-READY READ-ONLY 2016 PREFLIGHT

DEC-503 defines the first 2016 annual-pattern-catalogue preflight over a concrete
DEC-502 2015 runtime binding.

It requires exact current main, exactly the two prior 2015 workflow runs, target
segment 2016, predecessor segment 2015, and the successful 2015 replacement run id
as the required previous annual freeze run.

Expected next workflow identity is run #3 / attempt 1.

The CLI is plan-only. Annual workflow dispatch, historical reads/execution/results,
cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker
mutation, real-money action, and trading remain false.

Next gate:
`ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_AUTHORIZATION_BEFORE_RUN`.

## DEC-504 — 2016 execution authorization contract

**Date:** 2026-10-03  
**Status:** SOURCE-ONLY AUTHORIZATION / RUNTIME INACTIVE

DEC-504 converts a valid DEC-503 preflight into a canonical 2016 execution-authorization receipt under the standing autonomous-build instruction.

It scopes authorization to annual segment 2016, predecessor 2015, the concrete previous annual freeze run id, and expected workflow run #3 / attempt 1.

The authorization contract may mark dispatch, historical reads, catalogue execution, and result production true for that exact scope, but it also requires `runtime_authorization_installed = false` and `runtime_gate_active = false`.

Therefore DEC-504 does not change the live runtime.

2017+, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading remain false.

Next gate:
`INSTALL_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_AFTER_CONCRETE_PREFLIGHT`.

## DEC-505 — Dormant 2016 runtime authorization plan

**Date:** 2026-10-03  
**Status:** DORMANT ACTIVATION PLAN / LIVE RUNTIME UNCHANGED

DEC-505 freezes the exact future 2016 runtime activation without applying it.

It pins DEC-504 authorization source blob
`19d95a11e3ae1684d28ab17020f78bea39003bc8`, DEC-503 preflight source blob
`00b0df00f15e1d983c799e8991a88e03e010d2e3`, current runtime blob
`ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b`, active workflow blob
`f7e65ee95f472918e390bceedd7cf2f38bbf7e92`, dormant 2016 gate blob
`87c00381c5c12a0593378f565e6be4bad003514f`, and dormant target runtime blob
`d7d3713cb3259e793c448153fd75ca043f511389`.

The future gate is limited to segment 2016, run #3 / attempt 1, and requires a
positive previous annual-freeze run id. Nothing is installed by DEC-505.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC504`.

## DEC-506 — Read-only 2016 runtime authorization install preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY INSTALL PREFLIGHT / LIVE RUNTIME UNCHANGED

DEC-506 validates a canonical DEC-504 authorization receipt against exact current
main and the DEC-505 dormant two-file activation plan.

It requires segment `2016`, expected workflow run #3 / attempt 1, a positive
previous annual-freeze run id, inactive DEC-504 runtime state, an absent active
2016 gate source, and the exact pre-2016 runtime blob.

The future activation is exactly two files: create the frozen 2016 gate source and
replace the runtime with the frozen 2016-wired target. DEC-506 itself is plan-only
and authorizes no repository mutation.

Next gate:
`EXACT_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_MUTATION`.

## DEC-507 — Exact 2016 runtime authorization install action

**Date:** 2026-10-03  
**Status:** SOURCE-ONLY EXACT MUTATION ACTION / LIVE RUNTIME UNCHANGED

DEC-507 compiles a current-main-sensitive two-file activation action from a valid
DEC-506 receipt.

The action creates the frozen 2016 gate source and replaces the pre-2016 runtime
with the frozen 2016-wired target. Any main-head drift invalidates the action.

Standing autonomous-build authorization is bound only to those two exact mutations.
DEC-507 itself does not apply them and leaves runtime activation, dispatch/execution,
2017+, Strategy V1, promotion, and trading false.

Next gate:
`APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION`.

## DEC-508 — Future 2016 runtime authorization install receipt

**Date:** 2026-10-03  
**Status:** FUTURE POST-INSTALL RECEIPT / DISPATCH LOCKED

DEC-508 reviews the exact two-file result of the DEC-507 activation action.
It requires exactly the planned changed files, gate blob
`87c00381c5c12a0593378f565e6be4bad003514f`, runtime blob
`d7d3713cb3259e793c448153fd75ca043f511389`, and a concrete install commit.

A valid receipt marks the install action consumed and the 2016 runtime gate
installed/active, while workflow dispatch and all later research/trading authority
remain false.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_PREFLIGHT`.

## DEC-509 — Read-only 2016 dispatch preflight

**Date:** 2026-10-03  
**Status:** SOURCE-ONLY READ-ONLY PREFLIGHT / DISPATCH AUTHORIZATION LOCKED

DEC-509 binds the future exact DEC-508 runtime-install receipt to the concrete DEC-502
2015 runtime evidence, the exact two-run annual workflow inventory, the repaired active
workflow, and current main.

The current main head must equal the DEC-508 install commit, and the same successful
2015 replacement run must be named by both the install receipt and runtime binding.

The preflight records installed/active 2016 runtime authorization but remains read-only:
workflow dispatch, historical read/execution/result production, 2017+, Strategy V1,
promotion, broker mutation, demo/live orders, real-money action, and trading remain false.

Next gate:
`ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_AUTHORIZATION_BEFORE_RUN`.

## DEC-510 — Source-only 2016 dispatch authorization

**Date:** 2026-10-03  
**Status:** SOURCE-ONLY AUTHORIZATION / DISPATCH NOT EXECUTED

DEC-510 consumes a valid DEC-509 preflight and authorizes exactly the future 2016
annual-catalogue workflow run 3, attempt 1.

The contract preserves the exact current-main/install-commit binding, installed runtime
gate state, repaired workflow identity, and concrete 2015 predecessor freeze. It marks
workflow dispatch plus historical read/execution/result production authorized for that
one run, but contains and executes no dispatch command.

Reruns, retries, run 4+, 2017+, Strategy V1, promotion, broker mutation, demo/live
orders, real-money action, and trading remain false.

Next gate:
\`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT\`.

## DEC-511 — Final read-only 2016 dispatch-action preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY FINAL PREFLIGHT / DISPATCH NOT EXECUTED

DEC-511 consumes the exact DEC-510 authorization and rechecks current main, the repaired
annual workflow, and the complete two-run predecessor inventory immediately before any
future 2016 dispatch.

The successful 2015 replacement run is bound by both run ID and head SHA. The dispatch
parameters are frozen to \`main\`, annual segment \`2016\`, and that exact predecessor run ID.

No dispatch command is present or executed. Reruns, retries, run 4+, later years,
Strategy V1, promotion, broker mutation, demo/live orders, real-money action, and trading
remain locked.

Next gate:
\`EXACT_2016_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN\`.

## DEC-512 — Repository-hosted one-shot 2015 replacement executor

**Date:** 2026-10-03  
**Status:** EXECUTION-CAPABLE ONE-SHOT / 2015 REPLACEMENT ONLY

DEC-512 closes the live operational gap after the failed first 2015 annual-catalogue
run. A main-push/path-scoped executor re-runs DEC-499 against the exact merged head and
live annual workflow inventory before it can submit anything.

The executor requires exactly failed run \`37126711695\` / run 1 / attempt 1, pins the
repaired workflow/runtime and DEC-498/499 sources, and submits exactly one
\`annual_segment_label=2015\` dispatch. It then resolves exactly run 2 / attempt 1 at
the same main SHA and rejects any observed run 3+.

The receipt claims only that the replacement dispatch was submitted. It grants no retry,
rerun, 2016+, Strategy V1, promotion, broker mutation, demo/live order, real-money, or
trading authority.

Next gate:
\`REVIEW_2015_REPLACEMENT_RUN_WITH_DEC_500\`.

## DEC-513 — Automated concrete 2015 replacement runtime evidence

**Date:** 2026-10-03  
**Status:** READ-ONLY WORKFLOW-RUN REVIEW / CONCRETE BINDING

DEC-513 installs a read-only \`workflow_run\` reviewer for annual workflow run 2.
It requires attempt 1, successful completion on main, the exact DEC-512 executor at the
same head, and byte-exact DEC-500/501/502 sources.

The reviewer downloads the exact annual-freeze artifact, verifies its ZIP SHA-256 against
GitHub's artifact digest, runs DEC-500 review, DEC-501 freeze, and DEC-502 binding in
order, and uploads the canonical concrete 2015 runtime binding.

The workflow has no Actions write permission and cannot dispatch, retry, rerun, mutate the
repository, authorize 2016 execution, promote strategies, access a broker, place orders,
use real money, or trade.

Next gate:
\`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_PREFLIGHT\`.

## DEC-514 — Automated read-only 2016 activation plan

**Date:** 2026-10-03  
**Status:** READ-ONLY POST-BINDING PLAN / MUTATION NOT EXECUTED

DEC-514 consumes the successful DEC-513 concrete 2015 runtime-binding artifact only
when the reviewer head still equals current main. It then runs the already-frozen
DEC-503, DEC-504, DEC-506, and DEC-507 chain in order.

The final output is the exact two-file 2016 runtime-install action: create the frozen
2016 authorization gate and replace the runtime with the frozen 2016-wired target.

The workflow has only contents/actions read permission. It does not apply the mutation,
commit, push, dispatch or rerun workflows, authorize later years, access a broker, place
orders, use real money, or trade.

Next gate:
\`APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION\`.

## DEC-517 — 2015 replacement executor recovery

**Date:** 2026-10-03  
**Status:** ONE-SHOT RECOVERY / TARGET RUN-2 SLOT UNCONSUMED

The initial DEC-512 executor run `37149151549` failed before its dispatch step because
the workflow omitted the pinned annual-catalogue Python dependency install. GitHub still
reports exactly one annual `workflow_dispatch` run: failed 2015 run #1.

DEC-517 adds a separate one-shot recovery workflow rather than weakening or rerunning the
failed executor. It verifies that exact failure, installs the pinned runtime, rebuilds
DEC-499 on exact current main, and may submit exactly 2015 run #2 / attempt 1.

DEC-513 is rebound to accept evidence only when that run is tied to the successful
DEC-517 recovery executor at the same head.

Retry/rerun, run 3+, 2016+ execution, promotion, broker mutation, orders, real-money
action, and trading remain locked.

Next gate:
`SUCCESSFUL_2015_REPLACEMENT_RUN_2_THEN_DEC_513_CONCRETE_BINDING`.

## DEC-518 — Recovered exact 2016 runtime install executor

**Date:** 2026-10-03  
**Status:** BOUNDED REPOSITORY MUTATION / NO WORKFLOW DISPATCH

DEC-518 is installed together with DEC-517 so the workflow-run successor already exists
before the recovered 2015 evidence chain can reach DEC-514.

It accepts only a successful recovered DEC-514 plan artifact, verifies the exact DEC-507
two-file action and concrete DEC-502 binding, requires current main to remain unchanged,
copies only the frozen 2016 gate/runtime templates, verifies their result blobs, and
creates one normal fast-forward commit.

The executor then builds the concrete DEC-508 post-install receipt. Annual workflow
dispatch, rerun/retry, broker mutation, order placement, real-money action, and trading
remain outside DEC-518.

Next gate:
`READ_ONLY_POST_INSTALL_2016_DISPATCH_PLAN_ON_DEC_518_RECEIPT`.

## DEC-519 — Folded read-only post-install 2016 dispatch plan

**Date:** 2026-10-03  
**Status:** READ-ONLY SECOND JOB / DISPATCH NOT EXECUTED

To stay within GitHub's `workflow_run` chain-depth limit, DEC-519 is implemented as a
second job inside the DEC-518 workflow rather than as another workflow-run successor.

After the exact two-file install succeeds, this job drops to contents/actions read,
downloads the DEC-518 evidence from the same run, validates the concrete DEC-508 receipt
and DEC-502 predecessor binding on installed main, then rebuilds DEC-509 → DEC-510 →
DEC-511.

The resulting artifact freezes only the exact future 2016 run #3 / attempt 1 parameters.
No workflow dispatch, repository mutation, rerun/retry, broker access, order placement,
real-money action, or trading occurs.

Next gate:
`EXACT_2016_ANNUAL_PATTERN_CATALOGUE_RUN3_ONE_SHOT_DISPATCH`.

## DEC-520 — Annual workflow validity and run-identity recovery

**Date:** 2026-10-03  
**Status:** WORKFLOW REPAIRED / EXACT RUN IDENTITIES REBOUND

The DEC-496 workflow blob was invalid because three duplicate `include-hidden-files` keys
were concentrated in one YAML mapping. GitHub recorded no-job push failures for that
workflow and advanced its global run number through 375 without creating another manual
annual dispatch.

DEC-520 replaces the live annual workflow with corrected blob
`09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`: each of the three upload steps has exactly
one hidden-file flag. The prior malformed blob remains frozen as historical evidence.

The replacement authorization/review/binding chain is rebound to exact GitHub workflow
run 376 / attempt 1, and the 2016 execution/install/dispatch chain to exact run 377 /
attempt 1. The preflight inventory still requires the sole prior manual dispatch to be
failed run 1, so an unexpected intervening dispatch fails closed.

DEC-520 authorizes no new dispatch, retry, rerun, later-year execution, broker mutation,
order placement, real-money action, or trading.

## DEC-521 — Exact 2016 run-377 one-shot dispatch

**Date:** 2026-10-03  
**Status:** BOUNDED RESEARCH DISPATCH / RESULT NOT CLAIMED

DEC-521 is folded into the recovered DEC-518 workflow as a third job after the exact
runtime install and DEC-519 read-only plan. This preserves DEC-509/511's exact-current-main
binding: no separate repository merge occurs between the plan and dispatch.

The job requires installed main to remain the DEC-508 install commit, verifies the exact
installed gate/runtime blobs, consumes the concrete DEC-502 predecessor and DEC-519
DEC-509→510→511 bundle, and requires the annual global run counter to still end at
successful run 376 with no run 377+ present.

It then submits exactly one `2016` dispatch with the concrete predecessor run ID and
resolves exact run 377 / attempt 1. The receipt claims only submission, not a result.

Rerun/retry, run 378+, 2017+, Strategy V1, promotion, broker mutation, demo/live orders,
real-money action, and trading remain false.

Next gate:
`REVIEW_2016_RUN_377_BEFORE_ANY_2017_EXECUTION`.

## DEC-522 — Read-only 2016 run-377 evidence binding

**Date:** 2026-10-03  
**Status:** SOURCE-READY READ-ONLY REVIEW / 2017 LOCKED

DEC-522 binds only a completed successful annual-catalogue run 377 / attempt 1 whose run
ID and head are also named by the exact DEC-521 dispatch receipt.

The reviewer requires the exact 20-job and 20-artifact 2016 inventory, verifies the
freeze ZIP against GitHub's SHA-256 artifact digest, and validates the embedded DEC-477
2016 annual freeze before producing a concrete runtime-evidence binding.

The reviewer has contents/actions read permission only. It performs no workflow dispatch,
repository mutation, rerun/retry, 2017 execution, broker action, order placement,
real-money action, or trading.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_EXECUTION_PREFLIGHT`.

## 2026-10-04 — DEC-517 recovery implementation repair

Recovery workflow run `37190929052` on merge `5417fddc015be92ed843de40be097381367b2c24` failed before dispatch at the post-install clean-checkout guard. The annual catalogue still has only failed manual run 1, so global run 376 remains unconsumed. The v2 implementation keeps the same recovery workflow identity, requires exact workflow run 2 / attempt 1, proves the failed run-1 provenance, replaces editable installs with dependency-only installs across the complete live successor chain, preserves every clean-checkout guard, and repins downstream workflow/source hashes through DEC-522. No later-year, broker, order, real-money, or trading authority is added.

## 2026-10-04 — DEC-526/527/528 post-run376 recovery

Annual catalogue run `37191637168` consumed global run 376 / attempt 1 and failed in the 2015 preflight before cell execution because the historical DEC-491 installed-workflow validator still required the pre-DEC-520 workflow blob. DEC-526 freezes that failure without retry authority. A corrected installed-state validator preserves historical DEC-491 evidence while validating the DEC-520 active workflow. DEC-527 authorizes only a fresh 2015 run 377 / attempt 1; DEC-528 is the exact repository-hosted dispatch receipt. The complete 2016 source/runtime/dispatch/evidence chain is rebound from run 377 to run 378. Run 376 cannot be retried or rerun, and run 379+, 2017+, broker/order/real-money/trading authority remain locked.

## 2026-10-04 — DEC-529 explicit successor recovery

Annual run 377 / attempt 1 (`37198002653`) completed successfully on `a89db974be9a94481e7ed0990476bc661012f1e4` with the full 20-job/20-artifact 2015 catalogue, but its DEC-513 `workflow_run` successor did not start. DEC-529 adds exact manual-recovery inputs to DEC-513, DEC-514, DEC-518→521, and DEC-522 plus a one-shot path-scoped orchestrator. The orchestrator cannot directly dispatch the annual workflow; it can only recover the existing successor contracts in order, wait for exact run 378 success, and recover DEC-522 if its automatic completion trigger is also absent. Run 379+, 2017+, strategy promotion, broker mutation, order placement, real-money action, and trading remain locked.

## 2026-10-04 — DEC-530 explicit successor installer recovery

DEC-529 reached successful manual DEC-513 and DEC-514 successors, but installer workflow run `37200408776` failed before commit because `git diff --name-only` omitted the newly created untracked runtime gate. Annual run 378 remains unconsumed. DEC-530 changes the mutation inventory to tracked-plus-untracked paths, requires exact fresh installer workflow run 2 / attempt 1 from a fresh DEC-514 run 2, rebinds DEC-522 to one unique successful normal-or-explicit installer, and resumes the same path-scoped orchestrator only as run 2 after proving the prior failure chain. No rerun/retry, 379+, 2017+, broker, order, real-money, or trading authority is added.

## 2026-10-04 — DEC-531 / DEC-532 post-install 2016 recovery

Installer run `37205170186` successfully applied, committed, and pushed the exact two-file DEC-518 install, advancing main to `525386dd68955e9f02909f9692987968ab15e516`, then failed constructing DEC-508 because the installed DEC-505 gate imported DEC-504 at module load time and completed a circular import through DEC-503 and the annual runtime. DEC-531 repairs only the active gate by making that DEC-504 import lazy and freezes the exact failed-installer provenance. DEC-532 reconstructs DEC-508 from the immutable DEC-514 run-2 artifact and may dispatch only fresh annual run 378 / attempt 1 after proving main, predecessor binding, and the exact {1,376,377} annual inventory. Run 379+, 2017+, strategy, broker, order, real-money, and trading authority remain locked.

## 2026-10-04 — DEC-533 run-378 evidence successor recovery

Annual run `37206992367` completed successfully as exact run 378 / attempt 1 with the full 20-job/20-artifact 2016 catalogue, but the automatic DEC-522 reviewer did not start. DEC-533 adds a one-shot path-scoped recovery that proves exact DEC-532 provenance, requires zero prior DEC-522 reviewer runs, dispatches only the existing read-only DEC-522 reviewer, and verifies the resulting concrete 2016 runtime-binding artifact. It cannot dispatch the annual catalogue or mutate repository contents. Run 379+, 2017 execution, strategy promotion, broker/order, real-money, and trading authority remain locked.

## 2026-10-04 — DEC-534 concrete 2017 execution preflight

DEC-522 is now concrete from reviewer run `37208993431`, artifact
`11305284883`, binding fingerprint
`c95d28505fab6a8c55c9889ba5da6565be3b63cb98321eea58d26196b60a2b40`,
and successful 2016 annual run 378.

DEC-534 supersedes the unmerged stale DEC-523 draft and validates the actual
four-run annual history: failed run 1, failed run 376, successful 2015 run 377,
and successful 2016 run 378. It freezes only the read-only 2017 preflight for
expected run 379 / attempt 1. The next annual execution remains locked.

Next gate:
`ANNUAL_PATTERN_CATALOGUE_2017_EXECUTION_AUTHORIZATION_BEFORE_RUN`.

## 2026-10-04 — DEC-534 bootstrap recovery

The first repository-hosted DEC-534 preflight run (`37209674158`) passed its
evidence and annual-history checks, then failed before preflight construction
because the workflow did not export `PYTHONPATH=src`.

No repository or annual-workflow mutation occurred. The recovery keeps the same
DEC-534 contract, requires exact workflow run 2 / attempt 1, proves failed run 1
before continuing, and adds only the missing source-path environment.

## 2026-10-04 — DEC-535 concrete 2017 execution authorization

Successful DEC-534 workflow run `37210041270` produced immutable preflight artifact `11306121033` with digest `sha256:531c468e36ac80f6c0c24620c14b78d2b2faad869d53be098efe7a2b31425e04`. DEC-535 binds only that concrete preflight and authorizes annual segment 2017 as exact workflow run 379 / attempt 1. The contract turns on only the historical read/execution/result and annual-workflow-dispatch authority needed by that future research run. The 2017 runtime gate is not installed, no dispatch command exists or executes, and run 380+, 2018+, strategy promotion, broker/order, real-money, and trading authority remain locked. Next gate: `READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN`.

## 2026-10-04 — DEC-535 bootstrap recovery

Repository-hosted DEC-535 workflow run `37213060816` passed exact DEC-534 artifact provenance and the unconsumed run-379 inventory, then failed before authorization construction because the research Python dependencies were not installed. No mutation or dispatch occurred. The recovery keeps the same workflow identity, permits only run 2 / attempt 1 after proving the failed run-1 identity, installs the pinned runtime dependencies without an editable project install, preserves the clean-checkout guard, and rebuilds the same source-only DEC-535 artifact. Run 379 remains unconsumed and all later-year/trading surfaces remain locked.

## 2026-10-04 — DEC-536 concrete 2017 runtime-authorization plan

Successful DEC-535 authorization run `37213629059` and artifact `11307204031`
are now the sole concrete source for the 2017 runtime-authorization plan. The plan
pins the current runtime, corrected annual workflow, dormant 2017 gate, and dormant
runtime target; rechecks that annual run 379 is absent; and remains read-only. No
runtime installation, repository mutation, annual dispatch, run 380+, later-year,
strategy, broker/order, real-money, or trading authority is opened.

## 2026-10-04 — DEC-537 concrete 2017 runtime install preflight

Successful DEC-536 workflow run `37215086807` / artifact `11307494750`
is now the sole concrete source for the 2017 runtime-install preflight. DEC-537
pins the exact two dormant target blobs, rechecks the current runtime/main and
annual history, and remains read-only. Repository mutation, runtime activation,
annual dispatch, run 380+, 2018+, strategy, broker/order, real-money, and trading
authority remain false.

## 2026-10-04 — DEC-538 exact 2017 runtime install action

Successful DEC-537 workflow run `37215789401` / artifact `11308490990`
now anchors the exact two-file 2017 runtime-install action. The action contract
authorizes only creation of the frozen 2017 runtime gate and replacement of the
current annual runtime with the frozen 2017-aware target. The repository-hosted
DEC-538 builder remains read-only and does not apply either action. Annual run
379 remains absent; dispatch, run 380+, later-year, strategy, broker/order,
real-money, and trading authority remain locked.

## 2026-10-04 — DEC-539 exact 2017 runtime authorization install

Concrete DEC-538 workflow run `37219170862` produced artifact `11310165235` (digest `e210042872cbe191f4383fcba4a6ac9305fbdeb96acaed32d46e034acff1681d`). DEC-539 is the bounded repository mutation that may create only the frozen 2017 gate blob `c1853eee...` and update the annual runtime from `b564f5a2...` to `e9cbc76d...`. The executor rechecks unchanged main and the unconsumed run-379 slot before mutation and before push, proves the installed run-379 gate imports, and emits a concrete install receipt. It cannot dispatch the annual workflow and grants no run-380+, 2018+, strategy, broker/order, real-money, or trading authority.

## 2026-10-04 — DEC-540 read-only 2017 dispatch preflight

DEC-539 installer run `37219929487` successfully installed the frozen 2017 runtime authorization at commit `dcdf7210b0039077efa3a23c65c2ed8fa41e2427` and produced artifact `11309927463` (digest `6672b0642a763424541d971d84b273f8c2fde5089fcd736e6152fe8dc9a7e32e`). DEC-540 binds that exact receipt, installed gate/runtime blobs, and annual history `{1 failure, 376 failure, 377 success, 378 success}`, then freezes only future run 379 / attempt 1 with predecessor `37206992367`. It is read-only and contains no dispatch command. Run 380+, 2018+, strategy, broker/order, real-money, and trading authority remain locked.

## 2026-10-04 — DEC-541 concrete 2017 dispatch authorization

DEC-540 completed successfully as workflow run `37223000759` at head `f7983f960ae141f15c83b3cc05f6d6030140c802`, producing artifact `11311031268` with digest `sha256:a54675bd49ef6bb17d32f44b1d21a4adb10b541e3a248f583b05293505ef498d` and preflight fingerprint `7329cf4238c1aa8b608d7b4e41eaaaf643f78c3fb99f7ae399f6db303a75ffad`. DEC-541 binds that evidence and freezes source-only authorization for 2017 run 379 / attempt 1 with predecessor `37206992367`. No next-run command is present and all later scopes remain disabled.

## 2026-10-04 — DEC-542 read-only 2017 dispatch-action preflight

DEC-541 is concrete from workflow run `37223700484` and artifact `11310658984` (digest `97ee57fdb892b7041276bcd6c56da7ab06422e719c8b74aa322e35be80d243a3`), with authorization fingerprint `16d42cb2552df761b80e0b32a23de5378f143c004946cfe2c816f280b17d8e8e`. DEC-542 binds that exact authorization to the unchanged annual history `{1 failure, 376 failure, 377 success/2015, 378 success/2016}`, exact predecessor run `37206992367`, and expected 2017 run 379 / attempt 1. The workflow is contents/actions read-only, freezes the dispatch parameters, contains no dispatch command, and rejects any existing run 379+. Run 380+, 2018+, strategy, promotion, broker/order, real-money, and trading authority remain locked. Next gate: `EXACT_2017_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`.

## 2026-10-04 — DEC-543 / DEC-544 exact 2017 run-379 dispatch and evidence binding

DEC-542 is concrete from workflow run `37226222971` on `edbbfd0ba3d33ecb61aa3ba6604bd954e98a83f1`, artifact `11311294443` (digest `d26a3d27a026546568dccab7305f44facdbfcbc749d2aac5f9233f43f86b61ea`), preflight fingerprint `ef31f7ea8c5e50dacee9cd2462b701d17e422f1507b2eb048db781c764d4b2db`. DEC-543 is the exact one-shot executor for annual segment 2017, run 379 / attempt 1, predecessor `37206992367`; it rechecks the exact four-run history and rejects run 380+. DEC-544 is installed atomically in the same merge and binds only a successful run 379 to the exact DEC-543 receipt, 20-job/20-artifact inventory, digest-verified freeze, and valid 2017 annual freeze. DEC-544 is read-only and includes a manual recovery path that never reruns research. Run 380+, 2018+, strategy, promotion, broker/order, real-money, and trading authority remain locked. Next gate after concrete DEC-544 evidence: `READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_EXECUTION_PREFLIGHT`.

## 2026-10-04 — DEC-544 run-379 evidence recovery

Annual run `37227536041` (global run 379 / attempt 1) completed successfully on `7b4c1ef8573e280c067443b72f1534d9091d5b7f`, but the installed DEC-544 workflow-run reviewer did not start. A separate path-scoped, read-only recovery workflow is added to bind only that completed run using exact DEC-543 dispatcher artifact `11313110298` and exact 2017 freeze artifact `11312736203`. It requires annual history through 379 exactly, requires no run 380+, performs no annual dispatch/rerun/retry, and preserves all later execution/trading authority as false.

## 2026-10-04 — DEC-545 concrete 2018 execution preflight

Concrete recovered DEC-544 evidence now exists from workflow run `37228767187`, artifact `11313481023`, digest `sha256:f48dd73bbae1587bf8c6e97408295ab94761ab4536c7124532ef5b6f55c2d1d1`, and binding fingerprint `a454e3eef8a51260cc07f9103a7de0208f5408a18686bb1249ad05e349edd9ae`. DEC-545 binds that exact predecessor, requires annual history `{1 failure, 376 failure, 377 success, 378 success, 379 success}`, freezes 2018 at expected run 380 / attempt 1 with predecessor run `37227536041`, and remains fully read-only. No run-380 dispatch or later/trading authority is added.

## 2026-10-04 — DEC-546 source-only 2018 execution authorization

DEC-546 consumes concrete DEC-545 workflow run `37229319220`, artifact `11313083318`, digest `sha256:36f76bba9cd3cef5fd1b3236f3bc80ad62029edf9c493ce10d946b7bcadf18a4`, and preflight fingerprint `55b9378a78f54a99a9055da1ac0294e73c5e02434fc4ad17d38acea7ac5c6315`. It authorizes only the exact 2018 research contract for run 380 / attempt 1 while requiring the current runtime to have no 2018 route or gate. Runtime installation, dispatch execution, run 381+, strategy/promotion, broker/order, real-money, and trading remain locked.

## 2026-10-04 — DEC-547 concrete 2018 runtime-authorization plan

Successful DEC-546 workflow run `37229862532` and artifact `11313482812` (digest `sha256:79e9bd2485160dd59fbb88a2d50f32a52b6cfd573f80555a8716fde4ea18c71e`, authorization fingerprint `34fe76b3bd30d054853b43f660f996757e8bdb30793c03ad6937cc3078b427a0`) are now the sole concrete source for the 2018 runtime-authorization plan. DEC-547 pins the current runtime `e9cbc76d...`, corrected annual workflow, dormant 2018 gate blob `cd50f501...`, and dormant runtime target `410180c3...`; rechecks annual history exactly through successful run 379; and rejects any run 380+. The plan is read-only and source-only. No runtime installation, repository mutation, annual dispatch, run 381+, 2019+, strategy, broker/order, real-money, or trading authority is opened. Next gate: `READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC547`.

## 2026-10-04 — DEC-548 concrete 2018 runtime install preflight

Successful DEC-547 workflow run `37231060551` on `1c61ad18d07d6fbc034c20610d7a130e09630a66` produced artifact `11314500352` with digest `sha256:633476f0bab6a5e1f3165cab44be176c05c01f955569ff0018cae957006ab56c`. DEC-548 binds that exact plan plus the embedded DEC-546 authorization, freezes a future two-file installation (2018 gate blob `cd50f501...`, runtime target blob `410180c3...`), and requires the current runtime to remain `e9cbc76d...`. The preflight is read-only, requires annual history exactly through successful run 379, rejects run 380+, and performs no repository mutation or dispatch. Next gate: `EXACT_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC548`.

## 2026-10-04 — DEC-549 exact 2018 runtime install action

Successful DEC-548 workflow run `37231591329` produced artifact `11314511176` with digest `sha256:993afb2809aa675ee2df789a402cc736a5f4992f906394a2f9161ba66675887c`. DEC-549 compiles exactly two future mutations: create the 2018 runtime gate from blob `cd50f501...` and replace current runtime `e9cbc76d...` with target `410180c3...`. The repository-hosted builder is read-only and applies nothing. Annual run 380 remains absent and dispatch/later-year/trading authority remains locked. Next gate: `APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC549`.

## 2026-10-04 — DEC-550 exact 2018 runtime authorization install

Concrete DEC-549 workflow run `37232388248` on `3cfd1b38217c97bbd590214394f171075d2d0f54` produced artifact `11313752760` (digest `sha256:94c9ce6e08f013cb9ff8f662c78b3fafc0ba902fa590e5b27e89751ddd9069a3`). DEC-550 is the bounded repository mutation that may create only the frozen 2018 gate blob `cd50f501...` and update the annual runtime from `e9cbc76d...` to `410180c3...`. The executor rechecks unchanged main and the unconsumed run-380 slot before mutation and before push, proves the installed run-380 gate and preserved run-379 route, and emits a concrete install receipt. It cannot dispatch the annual workflow and grants no run-381+, 2019+, strategy, broker/order, real-money, or trading authority.

## 2026-10-04 — DEC-551 read-only 2018 dispatch preflight

DEC-550 completed as installer workflow run `37233054691` and produced artifact `11314488545` (digest `sha256:8b9732b24a5ef6163d8ab54f34d058eecd9e1c4ce1a68c79a88306178933df2d`), with exact install commit `1fc73dfc1e102996cecd5b9ffcb75d3ab4fa3ade`. DEC-551 binds that receipt, installed 2018 gate blob `cd50f501...`, runtime blob `410180c3...`, and the exact annual history through successful run 379. It freezes only future 2018 run 380 / attempt 1 with predecessor `37227536041`. The preflight remains read-only and grants no dispatch, run-381+, 2019+, strategy, broker/order, real-money, or trading authority.

## 2026-10-04 — DEC-552 source-only 2018 dispatch authorization

Concrete DEC-551 workflow run `37233894381` on `35263ec4c59bae4733507c53b080f3ea07ff1325` produced artifact `11314757055` (digest `sha256:7a7ba8c4c008e6e1d6ce144eb8c2df17f506a18894d1487f044fef9533fcd9d7`) with preflight fingerprint `f756088f404f77220b366eaffdfd36cfe805f9fcd91a274ef7c5a364994893c8`. DEC-552 authorizes only the exact 2018 run-380 / attempt-1 research contract with predecessor `37227536041`. It is source-only: no dispatch command/action is present, and run 381+, 2019+, strategy, broker/order, real-money, and trading remain locked.

## 2026-10-04 — DEC-553 final read-only 2018 dispatch preflight

Bound concrete DEC-552 workflow run `37234867097`, artifact `11314579371`, and authorization fingerprint `eb0089103203b334c12800643f74cc838e8e9e140b4b7868f48ba74793d1d043` into the final non-mutating 2018 dispatch-action preflight. DEC-553 requires exact annual history through successful run 379 and freezes only segment 2018 / run 380 / attempt 1 / predecessor `37227536041`. No dispatch is executed and all run 381+/later-year/trading scopes remain locked.

## 2026-10-04 — DEC-554 / DEC-555 exact 2018 run-380 dispatch and evidence binding

Concrete DEC-553 workflow run `37235949110` produced artifact `11315522989` with digest `sha256:e4d9b6c8661442c1a1debebac843f2dabf07bca6e36054dc7d2ed43a74f1375e` and preflight fingerprint `ba609f06481c1b08e10d16dc772290cd0f3988de9ba32eaa56c13b5561ab86c2`. DEC-554 may dispatch only 2018 annual run 380 / attempt 1 with predecessor `37227536041`, after rechecking exact annual history through successful run 379 and rejecting run 380+. DEC-555 is installed atomically and binds only a successful run 380 to the exact DEC-554 receipt, 20-job/20-artifact inventory, digest-verified freeze, and valid 2018 annual freeze. DEC-555 remains read-only and includes only a manual missed-successor recovery path. Run 381+, 2019+, strategy/promotion, broker/order, real-money, and trading authority remain locked.

## 2026-10-04 — DEC-555 read-only recovery for successful 2018 run 380

Annual run `37237817538` completed successfully as run 380 / attempt 1 on `30971a996f514670a6f836d8e45cf80137197a4f`, with all 20 jobs and 20 artifacts successful. Freeze artifact `11315584379` has digest `sha256:ce2cdb7b4aa5fa9a0c7130e444b067463f333c0324942d57166d60b0af42e2c1`. DEC-554 dispatcher run `37237807553` and receipt artifact `11316382138` are successful, but GitHub emitted no DEC-555 successor run. A separate path-scoped, read-only recovery now performs the exact DEC-555 evidence review directly. It has no Actions write permission and no annual dispatch/rerun surface. Run 381+, 2019+, strategy/promotion, broker/order, real-money, and trading remain locked.

## 2026-10-04 — DEC-556 concrete 2019 execution preflight

Recovered DEC-555 evidence is concrete from workflow run `37240186365`, artifact `11317140969`, binding fingerprint `09950f6bfb577c4abe17a2466e466a08585fbcd05359ad5fa6c4bad16cce5fda`, and freeze fingerprint `355a1e5ca9282300a7a38e24dd3009ebe8470d1f029e62c38860bf710ac80559`. DEC-556 freezes only a read-only 2019 preflight against exact annual history through successful run 380. It expects future run 381 / attempt 1 with predecessor run `37237817538`. No dispatch, execution authorization, runtime mutation, run 382+, strategy, broker/order, real-money, or trading authority is added.

## 2026-10-04 — DEC-557 source-only 2019 execution authorization

Concrete DEC-556 preflight evidence is bound from workflow run `37240728378`, artifact `11317461212`, digest `sha256:09be3f1d11e77ab6da407a67346a6ff4d4ce631f4acb6265575da6db64eeb202`, and preflight fingerprint `3d311b8d8d387aca00f079bdab6b0531cf17aefc36913165cfb5eb265ad50421`. DEC-557 authorizes only the exact 2019/run381/attempt1 execution contract. Runtime installation, runtime gate activation, dispatch action, rerun/retry/replacement, run382+, later-year execution, strategy/promotion, broker/order, real-money, and trading remain false.

## 2026-10-04 — DEC-557 builder recovery v2

Repository-hosted DEC-557 builder run `37241492509` failed after verifying DEC-556 but before authorization construction because the annual-history Python block contained a literal `\\n` between run 379 and run 380. No annual dispatch occurred and run 381 remains unconsumed. The repaired workflow permits only its run 2 / attempt 1 and first binds the exact failed run-1 provenance. Authority is unchanged.

## 2026-10-05 — DEC-558 2019 runtime authorization plan

Concrete DEC-557 recovery run `37241812968` produced artifact `11317224241` with digest `sha256:ecdbb57924cf74945e9e8bba12dcaae2d869ef264813ef012d21ba175c5ef52e` and authorization fingerprint `c785127b20f57210e60ebd681d7b0e48a66f419fa8fbbbdd9cdd8fa560b464f9`. DEC-558 freezes a dormant 2019 gate (`d87fe85a...`) and 2019-aware runtime target (`07ddfe7a...`) for exact annual run 381 / attempt 1 with predecessor `37237817538`. The current runtime remains `410180c3...`, run 381 remains absent, and the plan is read-only with no repository mutation, dispatch, later-year, strategy, broker/order, real-money, or trading authority.

## 2026-10-05 — DEC-559 2019 runtime install preflight

Concrete DEC-558 workflow run `37294642532` produced plan artifact `11337484835` with digest `sha256:7ee0dbfd168a8a63664419cce85e41a65fde46f9e492dbee65868386d74975a8` and canonical plan SHA `5e35a860916137118e6a1ca9d751045373c59ad9e5e0ac373545b20740ccd074`. DEC-559 validates only the future two-file activation from current runtime `410180c3...` to dormant 2019 gate `d87fe85a...` plus runtime target `07ddfe7a...`. It remains read-only; run 381 and all mutation/dispatch/later-year/trading authority remain locked.

## 2026-10-05 — DEC-560 exact 2019 runtime install action

Concrete DEC-559 workflow run `37295798286` on `bb1c7901d1b5859bec97a381716166e9024a6022` produced artifact `11338796649` with digest `sha256:3d8b6933a1949c77a4e6b29df5bd86896a140d0011ba6859187d412df24cc8f9` and preflight fingerprint `1c585ad2a2a0bdf3a0fc811376d1fa5701b293b2fd888abca30ea5c13fcf3861`. DEC-560 freezes only the exact two-file 2019 runtime mutation: create gate blob `d87fe85a...` and update runtime from `410180c3...` to `07ddfe7a...`. The repository-hosted builder is read-only and only emits the action artifact. Run 381 remains unconsumed; runtime installation, dispatch, run 382+, later-year execution, strategy, broker/order, real-money, and trading remain locked.

## 2026-10-05 — DEC-561 exact 2019 runtime authorization install

Concrete DEC-560 workflow run `37299664787` on `bacb20c1d1541ac0b46076cef8ca9fe898559339` produced artifact `11341025756` with digest `sha256:dcd16ee2ddbdf9c5b17acfe6e79b54f1dbf6a38a839362ecc91a896f41520354` and action fingerprint `c68df812693da1edfc5ab568afef50b2e70797a04b4c44cf22de7c3fc15bea35`. DEC-561 is the bounded repository mutation that may create only the frozen 2019 gate blob `d87fe85a...` and update the annual runtime from `410180c3...` to `07ddfe7a...`. The executor rechecks unchanged main and the unconsumed run-381 slot before mutation and before push, proves the installed run-381 gate and preserved run-380 route, and emits a concrete install receipt. It cannot dispatch the annual workflow and grants no run-382+, 2020+, strategy, broker/order, real-money, or trading authority.

## 2026-10-05 — DEC-562 concrete 2019 dispatch preflight

DEC-561 installer run `37304310188` completed successfully and advanced main to exact install commit `ea3d63b5181fc592039c0c26d6decb358e43f7cc`. Artifact `11342593171` (digest `sha256:9739dda98fe654435c9e58053b934cfba4f1cf8747ab79dcd7dcbe9e27e6492b`) carries install-receipt fingerprint `098d2d24fbce40943ccff16a9ae1374e77facc0804365fedbb15eb128b3ca7be`. DEC-562 is read-only and freezes only 2019 run 381 / attempt 1 with predecessor `37237817538`; run 381 remains absent and all run382+/2020+/strategy/broker/order/real-money/trading authority remains locked.

## 2026-10-05 — DEC-563 source-only 2019 dispatch authorization

Concrete DEC-562 preflight run `37305622078` produced artifact `11344155034` (digest `sha256:b7245744efdd4cd646b8eac6f094e9198e0f4d0cd2d36883c70685fa0feffbb7`) with fingerprint `b02c7c68f682f9706e3f9e4a6e4ade7826e1abb47d01330f543279221063fe45`. DEC-563 authorizes only the source contract for 2019 / run 381 / attempt 1 / predecessor `37237817538`; it contains no dispatch command and executes no action. Run382+, 2020+, strategy/promotion, broker/order, real-money, and trading authority remain locked.

## 2026-10-05 — DEC-564 final read-only 2019 dispatch-action preflight

Concrete DEC-563 authorization run `37306565277` succeeded on
`c9b93843c2b853fc23d78cdbcebdbf51a3cc390e` and produced artifact
`11344330424` with digest
`sha256:06b72e13349a47106e36ce631713da55e51407fdeeb6dd26518c8115191bf520`
and authorization fingerprint
`fd554fbfd2ca556b0e4a6e65ddb00ec805809eda70d80a1e1a401edfeb71fcf8`.

DEC-564 freezes only main / 2019 / predecessor run `37237817538` / annual run
381 attempt 1 after revalidating exact annual history
`{1 failure, 376 failure, 377–380 success}`. It rejects run 381+ if already
present, performs no dispatch or repository mutation, and leaves rerun/retry,
run 382+, 2020+, strategy/promotion, broker/order, real-money, and trading
authority false.

Next gate:
`EXACT_2019_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`.

## 2026-10-05 — DEC-565/566 exact 2019 run381 dispatch and evidence binding

Concrete DEC-564 workflow run `37309216521` succeeded on
`79bffed4149cdeee1f74b8c02efdec42cb05c800`, producing artifact
`11344423884` with digest
`sha256:2d828fa08459a23172057722e8befc69d89891734e95980a4241be5121ac0db4`
and preflight fingerprint
`33ea75e1f34b2d643617be37e254644193506dea7fd959772c9eb00115088709`.

DEC-565 is the exact one-shot dispatcher for 2019 / predecessor
`37237817538` / global annual run 381 attempt 1. DEC-566 is installed
atomically before dispatch and binds only a successful exact run381 result,
20-job/20-artifact inventory, valid freeze digest, and DEC-565 receipt.
DEC-565 claims submission only; DEC-566 remains read-only. Run 382+, 2020+,
strategy/promotion, broker/order, real-money, and trading authority remain
false.

Next gate after successful DEC-566 evidence:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_EXECUTION_PREFLIGHT`.

## 2026-10-05 — DEC-566 run381 evidence recovery

Annual run `37310525635` completed successfully as run 381 / attempt 1 on `8bcee3a7a834743f08bd9ad73109bfc09609a2fe`, but GitHub did not create the automatic DEC-566 workflow-run successor. The exact DEC-565 dispatcher run is `37310506796`; its receipt artifact is `11345118826` with digest `sha256:ab1f031f0b986521b64c2667029b48a8052c5f936bb0633aff536770fb64646f`. The exact 2019 freeze artifact is `11345931866` with digest `sha256:cc3f5100c276e30df87d721a15843ff56b533354a5adaba6699d716a2daa8178`. A one-shot read-only recovery reuses the frozen DEC-566 reviewer and produces only the missing runtime binding; no run 382+, 2020 execution, strategy, broker, order, real-money, or trading authority is added.

## 2026-10-05 — DEC-567 concrete 2020 execution preflight

DEC-567 now binds the recovered DEC-566 runtime evidence exactly: recovery run `37312368068` on `ae724ba3e59c17440a8cf222242316a9462bf98f`, artifact `11345528676` with digest `sha256:800e06ce5026efa517853db32edf424ade527dc3fa7f2b95d9d2edd128237700`, binding fingerprint `a7063417dfb917f9b9019eb97c9a2803f50b4163ea524ea52c64b28a387720a2`, and freeze fingerprint `6935506f20d6d46054fabed5200ba6cec33ea4f10b00d839cc1cfc7f1b92b918`. The one-shot repository workflow remains read-only and freezes only 2020 run 382 / attempt 1. No dispatch, execution, result, strategy, promotion, broker, order, real-money, or trading authority is added.

## 2026-10-05 — DEC-568 source-only 2020 execution authorization

DEC-568 consumes only concrete DEC-567 workflow run `37313687059`, artifact `11346985812` (`sha256:182be0b68d721e3267a84bab37c5a3bcb5c25b84b546ba9565c20b6c2ee1f1b0`), and preflight fingerprint `bfccf190a7abad8464bafbf96a039305a8034f754fdc7cd05f5825c65398204f`. It authorizes the bounded 2020 research contract for run 382 / attempt 1 at source level only. The runtime gate remains uninstalled/inactive and no dispatch command or action exists. Run 383+, next-year execution, cross-year synthesis, strategy promotion, broker/order/real-money/trading authority remain false.

## 2026-10-05 — DEC-569 read-only 2020 runtime authorization plan

DEC-569 binds concrete DEC-568 workflow run `37315889656`, artifact `11346849851` (`sha256:a03cd0d85672e8ae760b8490982fe93f541738c68b733860f10bb16caf968308`), and authorization fingerprint `cfd43db91d2703e743132e61540ed95acec11fc9d4f6f89d8a8c011345a95f55`. It freezes dormant 2020 gate blob `695a50b418da752e1bd37d6302f209033ab611f5` and 2020-aware runtime target blob `4e124365430672fa63825b272001937c60151644` for exact annual run 382 / attempt 1 with predecessor run `37310525635`. No repository mutation, runtime installation, workflow dispatch, run 383+, 2021+, strategy, promotion, broker, order, real-money, or trading authority is added.

## 2026-10-05 — DEC-569 next-gate implementation repair

Concrete DEC-569 builder run `37317772668` completed successfully on `9a421918550ad3b7114ac9074c1de07fc807281d`, but its immutable artifact `11348625984` (`sha256:7dd8e882f729f8a1fb76edea15e2987b2c548585918e6761eed93620b01c186d`) exposed a stale inherited next-gate label ending in `AFTER_CONCRETE_DEC558`. The plan remained dormant and non-authorizing. This implementation repair changes only that provenance label to `AFTER_CONCRETE_DEC569`, pins the prior run-1 artifact as repair evidence, and permits only workflow run 2 / attempt 1 to regenerate DEC-569. Annual run 382 remains absent and no runtime mutation, dispatch, later-year, strategy, broker, order, real-money, or trading authority is added.

## 2026-10-05 — DEC-570 read-only 2020 runtime install preflight

DEC-570 binds corrected DEC-569 workflow run `37318488687` and artifact `11349042014` (`sha256:855375a850fe4e90475f5f5b9dd4d4721fba5bbac6ce8162d3c9d6d3854bbc7f`, canonical plan SHA-256 `794ea5631bee374ec7a2e05c5efcb33e35f008d188114c879f7d2e68be72a7b0`). It validates only a future two-file 2020 runtime installation from installed runtime `07ddfe7a968de10cd1d4f8592760cc9eb9e6300e` to gate `695a50b418da752e1bd37d6302f209033ab611f5` plus runtime target `4e124365430672fa63825b272001937c60151644`. The preflight performs no mutation or dispatch; run 382, later years, strategy, broker, order, real-money, and trading authority remain locked.

## 2026-10-05 — DEC-571 exact 2020 runtime install action

DEC-571 binds successful DEC-570 workflow run `37321690650`, artifact `11350136423` (`sha256:97eee3d49aec78ebbc1f3aa7190159d4dfba62c861f221163bd03c2699fdad7c`), and preflight fingerprint `367ec514057b011711ab9734a839f8cf03d1334125db336c947e979d923cab36`. It freezes only the two-file future mutation that creates the 2020 runtime gate from blob `695a50b418da752e1bd37d6302f209033ab611f5` and updates runtime `07ddfe7a968de10cd1d4f8592760cc9eb9e6300e` to `4e124365430672fa63825b272001937c60151644`. The builder is read-only and performs no mutation or dispatch. Run 382, later-year execution, strategy/promotion, broker mutation, orders, real-money action, and trading remain locked.

## 2026-10-05 — DEC-572 exact 2020 runtime installation

Concrete DEC-571 evidence is fixed at workflow run `37327905209`, artifact `11352259131`, digest `sha256:082c09ed64042f2c63252676be1d63aab6553c3cd92e3995256498ac4744b423`, and action fingerprint `0d617a5261a25d1fbdcc661fcc9518be63081ca442fb2ac068a2206f875e6939`. DEC-572 authorizes only the exact two-file 2020 runtime installation: create gate blob `695a50b418da752e1bd37d6302f209033ab611f5` and replace runtime `07ddfe7a968de10cd1d4f8592760cc9eb9e6300e` with `4e124365430672fa63825b272001937c60151644`. The installer requires annual run 382 to remain absent and performs no annual dispatch.

## 2026-10-05 — DEC-572 executor run-1 provenance failure

DEC-572 executor run `37360538726` failed before applying or staging either runtime file. The downloaded DEC-571 action was valid and carried the correct 2020 DEC-570 provenance (`37321690650`, artifact `11350136423`), while the executor still asserted inherited 2019 DEC-559 IDs. Run 382 remained unconsumed. The bounded repair requires exact DEC-572 workflow run 2 / attempt 1, proves the failed run-1 identity, and corrects only the two stale provenance assertions. Mutation scope and all later-year/trading locks are unchanged.

## 2026-10-05 — DEC-573 read-only 2020 dispatch preflight

Concrete DEC-572 evidence is bound to installer run `37361230835`, artifact `11367191085`, install commit `3ee648808bc2982c02dd1cb10fd45911f6379dcb`, and receipt fingerprint `1f77559f7aadfb83e338e467148d86b2a99850d69909e689f04604fa19c3e7b4`. DEC-573 freezes only future 2020 run 382 / attempt 1 with predecessor run `37310525635`, requires the exact seven-run annual history, and rejects run 382+. It performs no dispatch or repository mutation and leaves all later-year, strategy, broker/order, real-money, and trading authority false.

## 2026-10-08 — DEC-610 read-only protected 2023 dispatch-action preflight

**Status:** SOURCE-READY, PENDING EXACT-HEAD CI / MAIN LANDING / CONCRETE ARTIFACT. This entry documents a bounded read-only verification step; it does not independently grant workflow execution or trading permissions.

DEC-469 remains the mandatory annual-pattern-catalogue method; DEC-470 makes the accepted 2023 historical collection eligible for retrospective catalogue research, not automatic execution. The 2023 runtime gate was installed under DEC-607 (gate blob `cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191`, runtime blob `0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3`). DEC-608's read-only 2023 preflight succeeded at main landing `d9194944f53d311a9030deaf3ee37bff465634ed`, run `37766405383` / attempt 1, artifact `11544233443` / digest `sha256:7750c5d3b68b21dc7a4199e97ee3ce2fd8fdcb53fb6170c5270a78f695a512fc`.

DEC-609, the **source-only** run-specific authorization, landed on main at `7d40ccaf79270162dd96a8a1e7024dd94c3a72b7`. Its first-push workflow run `37770601661` / attempt 1 completed successfully, producing artifact `11547430955` / digest `sha256:8e33ab04cf87e0f2fe6b6b05fec53531dd0c9ff33fcc16abde920667ad154132`, authorization fingerprint `af91a248811f0cf291aea1fd94f4fff72eddd7e016b8d2fce2afc543bccb88fe`, and canonical JSON SHA-256 `044f7ec28570660fa04fb886e6ab194c4a986427b8df86754241b44e6efbf3ad`. That source contract permits only prospective submission of **protected 2023 annual catalogue run 385 / attempt 1**, with predecessor successful 2022 run 384 (`37663157285`); it does not itself dispatch or execute the workflow.

DEC-610 is a path-scoped, first-main-push, `contents:read` / `actions:read` only final action-preflight **builder**, not a dispatcher. It must independently download and authenticate the exact DEC-609 run/artifact/ZIP/canonical JSON/fingerprint, verify the unchanged 2023 runtime and workflow sources, require `main` to equal its own landing SHA, and validate the exact completed annual history `{1 failure, 376 failure, 377–384 success}` with no run 385+. It freezes `dispatch_ref=main`, segment `2023`, predecessor ID `37663157285`, expected run number `385` and attempt `1`, and emits immutable read-only preflight evidence only after all checks succeed.

DEC-610 carries forward DEC-609's **source** protected-catalogue authority as provenance but has `protected_history_access_authorized=false` at its own preflight layer, `dispatch_command_present=false`, `dispatch_action_executed=false`, and `preflight_read_only=true`. There is no direct dispatch, historical data read, historical result production, repository mutation, retry, rerun, replacement, run 386+ authority, cross-year result/analysis permission, strategy synthesis or promotion, Phase 8B, broker mutation, demo/live order, real-money action, or trading. A later separate, exact-evidence-bound action gate is required before any annual run-385 dispatch. Phase 8A acceptance and all further research/promotion/safety gates remain unchanged.

Next gate **only after successful concrete DEC-610 evidence:** `EXACT_2023_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`. No actual dispatch is authorized by the DEC-610 *preflight artifact* alone.

## 2026-10-08 — DEC-611 read-only 2023 dispatch immutability safety audit

**Status:** SOURCE-READY, PENDING CI/MAIN LANDING; **DISPATCH BLOCKED**.

DEC-469/470 remain the governing annual discovery method and accepted full-history protocol. DEC-607's exact protected 2023 runtime is installed, and DEC-608/609/610 supply concrete sequential preflight and source-only authorization for no more than the **future** 2023 catalogue run 385 / attempt 1 (predecessor successful 2022 run `37663157285`). DEC-610 landed at `58d17adbaf2238b6b774cb69f0434259984d1cb7`, with first-push run `37773291427` / attempt 1 / success and artifact `11547739610`, ZIP SHA-256 `e093274fc52e8e5abdb1bd08455f0fcdb2374bab15f3d507abfea59b91a60143`, preflight fingerprint `07f391338fe3d20c5e823f72a14cecdf454aec87a6e7638bdd8774f3c9b4b063`, canonical JSON SHA-256 `176cadda04eac41454d401bbabeeadc91e701307bbdd94054890ae89bf65689e`. No annual run 385 has been submitted.

**Rejected action design:** Original PR #777 proposed a one-shot GitHub `workflow_dispatch` on `--ref main`. Its P1 review demonstrated a check/dispatch race: GitHub resolves the mutable branch after the prior local SHA check, potentially consuming unique run number 385 on an unvetted commit. Repository `main` is currently unprotected and there are no effective repository rulesets. PR #777 was closed **without merge or dispatch**. The repository's no-retry/no-replacement constraint makes post-submission identity detection insufficient.

**Approved scope of the replacement DEC-611 source proposal:** Create a path-scoped read-only audit on its first main push. It must verify the exact DEC-610 workflow-run identity/artifact ZIP digest/canonical JSON/fingerprint, pinned DEC-607/609/610 runtime and workflow sources, current main SHA, and complete ten-run annual inventory; then emit an immutable **blocked** receipt. Neither an unprotected main nor a generic `protected=true` flag can prove a fully exclusive branch lock (including authorized bypass). The evidence may report the branch's reported protection state but **always** records `main_exclusive_lock_proven=false`, `dispatch_atomic_to_vetted_sha=false`, `dispatch_blocked=true`, `annual_workflow_dispatch_authorized=false` at the DEC-611 audit layer, `dispatch_command_present=false`, and `dispatch_action_executed=false`. This read-only audit does not withdraw the earlier narrowly scoped DEC-609/610 source authority; it prevents using that authority unsafely.

No rerun, retry, replacement, run 386+, 2024+ catalogue execution, cross-year analysis/results, Strategy V1 synthesis/promotion, Phase 8B, broker mutation, demo/live orders, real-money action, or trading is authorized. A future **separate** decision must establish a provable exclusive main lock lasting throughout the dispatch request or reauthorize an immutable-ref design with retested workflow/runtime and renewed source-of-truth provenance. Mere branch protection cannot automatically unblock this audit.

Next gate: `EXCLUSIVE_MAIN_LOCK_OR_REAUTHORIZED_IMMUTABLE_REF_DESIGN`. No submission, lock change, or broker action is part of DEC-611.

## 2026-10-08 — DEC-612 read-only GitHub main-lock readiness and candidate-witness report

**Status:** SOURCE-READY, pending independent PR CI, review, merge and concrete artifact. **No research execution permission or branch administration is granted.**

The governing method remains annual-first catalogue discovery under DEC-469 and the protected full-history protocol under DEC-470. DEC-607 installed the protected 2023 runtime; DEC-609 produced **source-only** authority for prospective run 385 / attempt 1; DEC-610 issued an immutable **read-only** action preflight. DEC-611's first proposal to dispatch on mutable `--ref main` was rejected and closed as unsafe (PR #777). The replacement **read-only** DEC-611 audit merged at `329e467a924ec00956505355f6cc1da7a589207c`, first-push run `37778086874` / attempt 1 success, immutable artifact `11550716769`, ZIP SHA-256 `3a9412e93cabd68eb5f19e73bf2769fa610c081ea10ce5fa370fa2ba59bf1e93`, audit fingerprint `f1842fd06bdba200be7ab521ed2735a9429df4836408a18297888d9c3d6416a5`, and canonical SHA-256 `5de4c3b87b64795c14f84211c838c9d9e1400c4c32b06d46946cb10a00e3a026`. The audit records `dispatch_blocked=true` and reports `main` unprotected; it is not a new dispatch authorization.

**DEC-612 authorizes only a read-only readiness assessor, not an action controller.** It verifies the DEC-611 exact run, artifact ZIP, canonical hash, audit fingerprint, current main SHA, installed 2023 runtime/authorization/annual workflow source SHA pins, and exact prior ten-run annual history with successful 2022 predecessor run `37663157285` and no 385+. It queries GitHub branch protection, effective branch rules and repository/inherited rulesets **with read-only token scopes**. Inaccessible or malformed control evidence is a fail-closed *visibility gap*. Any candidate readiness requires reported protected main, visible branch-protection details and effective rules, `lock_branch.enabled=true`, `enforce_admins.enabled=true`, disabled force pushes/deletions/fork sync, and visible rulesets with no reported bypass actors. Even this candidate is **not** proof of a continuously locked branch during a future GitHub `workflow_dispatch` API call, nor does it authorize changes to repository administration.

The path-scoped first-push audit may be run again manually as an **audit-only** GitHub Actions workflow after an independently approved admin setting change. The optional `workflow_dispatch` on the DEC-612 *assessment* cannot submit the annual-catalogue workflow: it has `contents:read`, `actions:read`, no annual dispatch command, no POST, and no repository mutation. Its evidence always preserves `main_exclusive_lock_proven=false`, `dispatch_atomic_to_vetted_sha=false`, `annual_workflow_dispatch_authorized=false` at this layer, `dispatch_action_executed=false`, `dispatch_blocked=true`, and all cross-year research, strategy synthesis/promotion, Phase 8B, broker/order, real-money and trading locks.

Next gate **after independently examined main-lock evidence and separate source-of-truth authorization**: `HUMAN_REVIEW_EXCLUSIVE_MAIN_LOCK_AND_SEPARATE_RUN385_AUTHORIZATION`. An incomplete/unknown lock remains blocked. The existing no-rerun/no-retry/no-replacement conditions are unchanged, and annual run 385 remains unconsumed.

**DEC-612 Administration-read credential correction (still read-only):** The default GitHub Actions `GITHUB_TOKEN` cannot read the branch-protection endpoint requiring Administration (read). The optional `FMP_GITHUB_ADMIN_READ_TOKEN` secret must be provisioned separately by an authorized repository administrator as a **read-only** App token or fine-grained credential. The workflow uses it solely for GET requests that inspect branch-protection and effective/inherited rules and never uploads or prints its value. When absent/underprivileged, all unavailable policy snapshots become `null`, the candidate cannot pass, and `dispatch_blocked=true` remains mandatory. The read-only default job permissions (`contents:read`, `actions:read`), no-dispatch, no-retry, no-promotion and trading locks are unchanged. Provisioning this secret alone **never authorizes** or automatically triggers run 385.

## 2026-10-08 — DEC-613 source-controlled offline 2023 main-lock administrator handoff

**Status:** SOURCE-READY / PENDING CI, REVIEW AND MAIN LANDING. No action controller, lock change, protected data read, or annual workflow dispatch is authorized.

The governing method remains DEC-469 annual-first catalogue discovery under DEC-470 full-history protocol. DEC-607 installed the 2023 runtime, while DEC-609/610 provided narrowly scoped source-only/read-only prospective authorization evidence for 2023 run 385 / attempt 1. Original PR #777's automatic dispatcher was closed without merge because mutable main can move between a local ref check and GitHub's server-side dispatch. DEC-611 proved and immutably recorded that blocker. DEC-612 completed as a read-only GitHub main-lock assessment at main 895b9ad311bd5159b2591dcfc8da714191574d00; first-main-push workflow run 37791444781 / attempt 1 succeeded and published artifact 11555414803, ZIP SHA-256 48b4512002af76c4fe88a256cff8ddc558d185d18411f2f9d8fd9b32fba80bf3, canonical JSON SHA-256 cc89cf90e820341a48d41cdd5518105dd99f3c867c9ec43b8c7d989a2535d0c5, readiness fingerprint d9555c20a7d7a5a2d4bc79f9dd621e7a6d73e1ac9340cfec81348dc4e5f6a787. Its concrete report says MAIN_UNPROTECTED, fails all administrative policy visibility/lock checks and explicitly blocks dispatch. No run 385 is consumed.

DEC-613 permits offline, read-only lock-administrator evidence handoff preparation only. The validator/CLI pins the concrete DEC-612 main/runs/artifact/ZIP/canonical JSON/fingerprint/source blob, validates its report contract, requires the actual current main identity and complete ten-run annual history ending at successful 2022 run 384 (37663157285), and produces a deterministic fingerprinted immutable-provenance packet containing the missing independent human/admin proofs. A protected=true report does not lift the block. It always emits human_proof_required=true, admin_evidence_gathered_by_this_packet=false, main_exclusive_lock_proven=false, dispatch_atomic_to_vetted_sha=false, annual_workflow_dispatch_authorized=false, dispatch_action_executed=false, dispatch_blocked=true, and trading_authorized=false. No repo-admin API writes, no GitHub workflow trigger, no dispatch, no broker mutation, no market data reads, and no order/trading control exist in DEC-613.

The source-controlled runbook docs/phase8a-2023-run385-admin-lock-handoff.md describes exact immutable upstream evidence, required read-only GitHub administrative observations, secret-handling constraints and a future independently authorized operating sequence. Neither the handoff packet, an optional admin-read token, a branch-protection flag, a candidate lock snapshot, nor GitHub issue #779 grants authority to submit the unique annual catalogue run.

**Next gate remains external and separate:** HUMAN_ADMIN_EXCLUSIVE_MAIN_LOCK_WITNESS_AND_SEPARATE_DISPATCH_DECISION. Any annual run 385 attempt, retry, replacement, later-year run, cross-year synthesis/promotion, Phase 8B, broker/demo/live order, real-money action or trading is unauthorized by DEC-613.

## 2026-10-08 — DEC-614 first-main-push read-only 2023 administrator handoff artifact freeze

**Status:** SOURCE-READY / AWAITING EXACT-HEAD CI, REVIEW, MAIN LANDING AND AUDIT ARTIFACT. Strictly an evidence-producing read-only workflow for DEC-613; no branch administration, historical catalogue execution, orders, trading or real-money actions.

DEC-469/470 govern the annual-first catalogue research method. The protected 2023 runtime installed by DEC-607 remains frozen. DEC-609/610 source-only/read-only evidence was narrowed to prospective 2023 annual run 385 / attempt 1 with predecessor successful 2022 run 384 (37663157285), without overriding the mutable-main dispatch blocker. Original action PR #777 was closed unmerged after identifying the main-ref race. DEC-611/612 successfully recorded main unprotected and blocked. DEC-613 merged source, CLI and runbook as PR #781 at 29a47639d80caf5e02fe33586c1fa5718603c614 after full tests, compilation and acceptance. DEC-613 source blob 6de695a5ea0c27f4fb16b5eae3289c0014155e3b; CLI blob cb17f4fba2eccd19077a8a057d5781bf81950759.

DEC-614 authorizes only a path-scoped push-to-main workflow (run 1 / attempt 1 only) with contents:read and actions:read permissions. It checks exact landing SHA, unchanged DEC-613 code and installed runtime workflow/gate blobs, and an exact five-file landing delta from the DEC-613 merge. It authenticates completed/successful DEC-612 first-push run 37791444781, head 895b9ad311bd5159b2591dcfc8da714191574d00, and immutable artifact 11555414803, ZIP digest sha256:48b4512002af76c4fe88a256cff8ddc558d185d18411f2f9d8fd9b32fba80bf3, canonical JSON SHA-256 cc89cf90e820341a48d41cdd5518105dd99f3c867c9ec43b8c7d989a2535d0c5, readiness fingerprint d9555c20a7d7a5a2d4bc79f9dd621e7a6d73e1ac9340cfec81348dc4e5f6a787. It freshly reads main and complete prior annual run inventory, requires no run 385+, then runs only the already-tested DEC-613 offline CLI and uploads its fingerprinted administrator handoff JSON.

No annual-workflow dispatch command, actions-write/admin permission, branch protection mutation, annual retry/replacement/cancellation or claimed research result is permitted. The handoff always records human_proof_required=true, admin_evidence_gathered_by_this_packet=false, main_exclusive_lock_proven=false, dispatch_blocked=true, annual_workflow_dispatch_authorized=false, dispatch_action_executed=false and trading_authorized=false. It cannot authorize run 386+, next-year catalogue, cross-year research, Strategy V1 synthesis/promotion, Phase 8B, broker/demo/live orders or real money. A completed artifact confirms the administrative requirements are documented, NOT met.

Next gate: HUMAN_ADMIN_EXCLUSIVE_MAIN_LOCK_WITNESS_AND_SEPARATE_DISPATCH_DECISION (issue #779). No dispatch, branch-lock change or trading is authorized by DEC-614.

### 2026-10-08 — DEC-614 concrete first-push artifact attestation (no action authorization)

**Status: PASSED as a read-only evidence freeze only.** PR #782 merged on 2026-10-08 at SHA ab7c5b34889e666ce14b8a00d572bcd0a07fb2cf after exact-head full general/historical regression, compilation, Phase 3, focused workflow tests and review. First-main-push workflow phase8a-annual-catalogue-2023-admin-handoff-freeze run 37799674451, run number 1, attempt 1, event push, head ab7c5b34889e666ce14b8a00d572bcd0a07fb2cf, completed success. Artifact 11559788794, immutable archive digest sha256:52f2c02a3ac8002c2f8b7d043080bcf47292e36f9574e9d37bcce2fb93d4f11d. Extracted DEC-613 administrator handoff JSON had canonical SHA-256 7e470b83d4b9a04017955835ff412aa07a0a7dc91b2193b350354bbbf659a267 and verified content fingerprint 6376c28695301ff68e44d2c353c47421c5f2a0b1574310ccf39e5508ae5ca3c0. The archive and internal fingerprints were independently recalculated, not inferred from a workflow outcome alone.

The packet binds the ten exact annual predecessor runs, ends at successful 2022 run 384 / id 37663157285 and expects only future 2023 run 385 / attempt 1. It reports human_proof_required=true, admin_evidence_gathered_by_this_packet=false, main_exclusive_lock_proven=false, dispatch_atomic_to_vetted_sha=false, annual_workflow_dispatch_authorized=false, dispatch_blocked=true, dispatch_action_executed=false, trading_authorized=false. A separate live check reconfirmed main at the exact merge SHA, unprotected, with no 385+ record. The first-main-push success does not retroactively allow a dispatch or resolve issue #779.

**Next gate remains HUMAN_ADMIN_EXCLUSIVE_MAIN_LOCK_WITNESS_AND_SEPARATE_DISPATCH_DECISION.** No retry, replacement, run 386+, later-year execution, cross-year results, Strategy V1 synthesis/promotion, Phase 8B, broker mutation, demo/live order, real money or trading is approved.

## 2026-10-08 — DEC-615 read-only immutable-tag dispatch feasibility analysis

**Status:** SOURCE-READY / PENDING INDEPENDENT CI, REVIEW AND LANDING. No protected research execution, branch/tag mutation, runtime amendment, broker action or trading authority is granted.

DEC-469/470 govern the annual-first research method; successful 2022 run 384 / id 37663157285 is the latest frozen catalogue. Prospective protected 2023 run 385 / attempt 1 is unconsumed. Original automatic dispatcher PR #777 closed unmerged after the mutable-main check/dispatch race. DEC-611/612 proved main unprotected and blocked, DEC-613/614 produced read-only administrator handoff. DEC-614 merged at ab7c5b34889e666ce14b8a00d572bcd0a07fb2cf; successful first-push run 37799674451 / attempt 1 produced artifact 11559788794, ZIP SHA-256 52f2c02a3ac8002c2f8b7d043080bcf47292e36f9574e9d37bcce2fb93d4f11d. Internal handoff canonical SHA-256 7e470b83d4b9a04017955835ff412aa07a0a7dc91b2193b350354bbbf659a267 and fingerprint 6376c28695301ff68e44d2c353c47421c5f2a0b1574310ccf39e5508ae5ca3c0 are verified. PR #783 merged the read-only attestation at main b588025b3dd57cfeb575d9ebbd09adb9775f8e9b.

GitHub workflow-dispatch accepts a branch or tag ref (not a raw commit SHA), and tag GITHUB_REF is refs/tags/... instead of refs/heads/main. The frozen annual workflow blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1 requires refs/heads/main in each job annual_preflight, annual_cell and annual_freeze. The protected 2023 gate blob cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191 and runtime blob 0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3 remain unchanged. Dispatching the existing workflow on a tag is therefore incompatible, even if that tag is proven immutable.

DEC-615 authorizes ONLY offline static feasibility assessment. It must validate the exact DEC-614 handoff fingerprint/canonical SHA, frozen active workflow/gate/runtime blob pins, current main SHA and complete ten-run annual inventory; locate all three main-ref shell guards; and report tag_path_compatible_with_current_workflow=false, immutable_tag_proven=false, alternate_ref_execution_authorized=false, annual_workflow_dispatch_authorized=false, dispatch_blocked=true, dispatch_action_executed=false, trading_authorized=false. No GitHub token, Actions trigger, tag write, workflow execution or mutation is part of this decision. Passing tests are evidence of current tag infeasibility, not permission for a workaround.

A separately authorized future tag design requires verified immutable-tag object/commit and ruleset/bypass proof, separately reviewed workflow/runtime amendments, renewed provenance and a specific one-shot action decision. The original exclusive main-lock path remains available only with equivalent administrator proof spanning the entire dispatch request (issue #779). No retries, replacements, 2024+, cross-year results, Strategy V1 synthesis/promotion, Phase 8B, broker/demo/live orders, real-money or trading authority is conferred.

Design document: docs/phase8a-2023-run385-immutable-tag-feasibility.md. GitHub semantics: https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event and https://docs.github.com/en/actions/reference/workflows-and-actions/variables.

## 2026-10-08 — DEC-616 offline tag-ruleset evidence-shape review (no execution authority)

**Status:** SOURCE-ONLY / PENDING EXACT-HEAD CI, INDEPENDENT REVIEW AND LANDING. DEC-615 PR #784 merged at main d2123d505d1cb8065a3e5afe9f74e28d4b1d2f0e. Original annual run 385 / attempt 1 is still reserved after successful 2022 run 384 / id 37663157285. The first main-lock dispatch design failed its mutable-ref race review and the DEC-615 feasibility review proved the three original annual workflow jobs reject refs/tags/... under frozen workflow blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1. Admin exclusive-main lock and protected-tag alternatives remain unapproved execution options under issue #779.

DEC-616 implements only a fail-closed, offline, stdlib-only advisory checker over caller-supplied tag-ref and REST-shaped tag-ruleset JSON. It requires an exact proposed namespace refs/tags/fmp/phase8a/2023/run385/, exact lightweight ref object matching the independently reviewed commit SHA, claimed complete inherited-ruleset visibility, and at least one exact-ref actively enforced tag ruleset restricting both update and deletion with no bypass actors. Wildcard scopes, missing inherited visibility, evaluation mode, bypass actors, retargeting and absent restrictions cannot satisfy the static candidate check. Negative tests also forbid re-fingerprinted authority escalation.

DEC-616 is **NOT** an admin witness or a sound proof of immutability. A static_ruleset_candidate=true assertion refers only to untrusted supplied JSON, never server state. Every report retains snapshot_authenticated=false, ruleset_enforcement_witnessed=false, bypass_permissions_independently_reviewed=false, immutable_tag_proven=false, annual_workflow_tag_compatible=false, annual_workflow_dispatch_authorized=false, dispatch_blocked=true, dispatch_action_executed=false and trading_authorized=false. No code to create a tag, edit rules, amend the protected workflow/runtime or call workflow_dispatch is present.

Future tag execution needs a **separately authorized source/runtime amendment**, enforced tag rules independently witnessed without usable bypass and spanning the complete server-side dispatch transaction, complete 10-run inventory and exact run 385 availability verification, and a **new explicit one-shot execution decision**. The exclusive-main lock route remains separate and equally requires authenticated admin proof. No run 385 dispatch/retry/rerun/replacement, 2024+, cross-year comparison, Strategy V1 synthesis/promotion, Phase 8B, broker/demo/live order, real money or trading is authorized.

Source-controlled design: docs/phase8a-2023-run385-tag-ruleset-static-review.md.

## 2026-10-08 — DEC-617 inert tag-ref/commit one-shot guard rehearsal (no live workflow change)

**Status:** SOURCE-ONLY / PENDING EXACT-HEAD CI AND INDEPENDENT REVIEW. DEC-616 PR #785 merged on main at 4144f9ba783511fdde51456bbe81f45a40b5e8ca, passing full regression, compilation, focused tests and Phase 3. The 2023 annual run 385/attempt 1 remains reserved and unconsumed, following successful 2022 run 384/id 37663157285. The server-side main-ref race remains under issue #779.

DEC-617 only checks the exact frozen active annual workflow blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1 and the ref/event guard order before pinned dependency installation and protected artifact reads in annual_preflight, annual_cell and annual_freeze. Its synthetic offline predicate rehearses exact workflow_dispatch event, proposed tag ref in the DEC-616 namespace, reviewed commit SHA equality, 2023 segment, run number 385, attempt 1 and predecessor 37663157285. Rejected negative examples include branch substitution, ref/SHA drift, wrong year, run number 386, retry attempt 2 and mismatched predecessor. This is **not** an executable runtime gate or an immutable-tag verification.

The installed 2023 runtime gate cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191 validates code_commit format and run identity but does not itself bind the code SHA to a specific hypothetical reviewed tag; therefore a separately authorized workflow/runtime amendment must review both the three YAML guards and runtime SHA/ref binding. DEC-617 installs no such amendment and changes no active annual workflow, 2023 authorization, broker code, branch settings or tags.

Every report preserves candidate_guard_installed=false, active_workflow_tag_compatible=false, workflow_amendment_authorized=false, runtime_amendment_authorized=false, immutable_tag_proven=false, annual_workflow_dispatch_authorized=false, dispatch_blocked=true, dispatch_action_executed=false and trading_authorized=false. No run 385 dispatch or retry, 2024+, cross-year synthesis, promotion, Phase 8B, broker/demo/live order or real-money action is authorized. Future release requires independent admin no-bypass witness spanning dispatch, reviewed workflow/runtime amendment and a fresh explicit one-shot decision. The exclusive-main lock path remains an alternative subject to the same independent immutability proof.

Companion source-only design: docs/phase8a-2023-run385-tag-ref-guard-rehearsal.md.

## 2026-10-08 — DEC-618 source-only disarmed annual tag amendment preview

**Status:** SOURCE-ONLY / PENDING EXACT-HEAD CI AND INDEPENDENT REVIEW. DEC-617 PR #786 merged at a2a767d5a09a32282722bfb24b98dad96ef27c9c after passing full historical/general regression, compilation, focused tests and Phase 3. Reserved annual 2023 run 385 / attempt 1 remains unconsumed, following successful 2022 run 384/id 37663157285. Main remains unprotected and effective no-bypass tag proof is absent (issue #779).

DEC-618 generates **only a local JSON/disarmed unified diff preview** of the three active annual workflow main-ref guards, using pinned original workflow blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1 and DEC-617 job/event/ref ordering verification. The proposed synthetic ref refs/tags/fmp/phase8a/2023/run385/dec618-not-authorized is deliberately not approved; each proposed job adds an unconditional exit 1 hard stop. Original workflow bytes are required to reconstruct exactly after reversing the in-memory substitutions. The active workflow file is never written or installed.

DEC-618 does not install a new runtime SHA/ref identity binding, authenticate tag immutability, provide an operator lock witness, change branch/tag/rulesets, create a workflow dispatcher, or permit historical execution. Its reports always set candidate_workflow_installed=false, runtime_amendment_installed=false, workflow_tag_execution_compatible=false, immutable_tag_proven=false, annual_workflow_dispatch_authorized=false, dispatch_blocked=true, dispatch_action_executed=false and trading_authorized=false. An affirmative source-only preview is not a release gate.

Future tag execution still needs a separately authorized and independently tested three-job workflow+2023 runtime amendment, continuous authoritative admin proof of exact tag immutability/no bypass during the server-side request, renewed annual inventory and a distinct one-shot run 385 action decision. Exclusive-main lock remains a separate similarly gated alternative. No retries, 2024+, cross-year synthesis, promotion, Phase 8B, broker, demo/live, real money or trading.

Design: docs/phase8a-2023-run385-disarmed-tag-amendment-preview.md.

## 2026-10-08 — DEC-619 read-only exhaustive dispatch-ref interleaving model

**Status:** SOURCE-ONLY / PENDING EXACT-HEAD CI AND INDEPENDENT REVIEW. DEC-618 merged as PR #787 at exact main `68c8ac7d83ba5bc0b5ee70551dfb2b96192d2169` after full regression, focused preview tests, package compilation and Phase 3. All existing run-385 action restrictions remain in force.

Issue #779 remains open because checking a reviewed main SHA before GitHub handles a workflow_dispatch request cannot rule out a concurrent ref change before GitHub resolves that mutable ref; post-submission mismatch detection is too late to recover the unique annual 2023 run 385 / attempt 1. DEC-619 adds a deterministic, stdlib-only, source-pinned **non-executing** interleaving model enumerating the four valid event orders (client verify, independent ref mutation, GitHub server ref resolution, post-dispatch result check). A mutable ref produces one synthetic wrong-SHA run-consumption witness; an assumed exclusive lock produces zero but provides **no** authenticated admin lock witness. The same issue arises for tags whose rules can be bypassed or deleted/recreated. Even a nominally immutable-tag model is incompatible with the installed main-only annual workflow.

The original annual workflow blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1 remains unchanged in all three jobs. The offline JSON report deliberately uses fake fixture SHAs, records real run-385 inventory as unverified, refuses in-checkout output, and validates its complete source-derived schedule content rather than trusting recomputed fingerprints. No live workflow/runtime amendments, administrative ruleset/branch/tag changes, GitHub API requests, dispatches, protected historical reads or trading code are included. Every report refuses claims of effective admin proofs, one-shot dispatch, runtime amendment approval, retries, future research, broker or trading. Issue #779 still requires independent administrator evidence and a fresh separately authorized one-shot action decision. See docs/phase8a-2023-run385-ref-race-interleaving-model.md.

## 2026-10-08 — DEC-620 read-only admin lock interval gap report

**Status:** SOURCE-ONLY / UNDER REVIEW; NOT AUTHORIZED FOR RESEARCH EXECUTION. Built on pending DEC-619 head 733ce93c9d809263dc9f86821a1cdb2df6aaab19. DEC-619 models the failure of local SHA checks to atomically bind mutable GitHub ref resolution to the one-shot 2023 annual run 385 / attempt 1. DEC-620 adds an **offline, untrusted-claims** continuity checklist over the four intervals from local reviewed-SHA check through dispatch submission, server resolution, run creation and post-dispatch audit.

For each interval, an input file must assert an exact reviewed ref SHA, effective lock, update/deletion/recreation blocking, no bypass and full inherited restriction visibility. Missing interval/negative claims/SHA drift surface a gap, with strict type and unknown-field rejection. Complete positive claims are **not independently authenticated proof**: there is no live admin API, ruleset edit, ref mutation, timing witness or server-side request in DEC-620. Source is pinned to the exact unchanged main-only annual workflow Git blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1, and a full report recomputation validator prevents re-fingerprinted authorization escalation.

Reports always deny real exclusive main/tag lock proof, effective admin witness, runtime/workflow amendment approval, live run 385 consumption verification, dispatch/run authorization and trading. A positive hypothetical tag case remains incompatible with installed annual workflow main ref checks. The assess-only CLI cannot write inside the checkout or contact GitHub. No annual dispatch, retries, 2024+ research, strategy synthesis/promotion, Phase 8B, broker mutation or trading is allowed. The sole next action gate remains a separately authenticated continuous no-bypass admin witness (issue #779), separately reviewed tag workflow+runtime changes if needed, and a distinct explicit run-385 one-shot decision. See docs/phase8a-2023-run385-lock-witness-coverage.md.

## 2026-10-08 — DEC-621 offline ambiguous annual dispatch terminal hold

**Status:** SOURCE-ONLY / INDEPENDENT REVIEW REQUIRED / NO DISPATCH. Based on DEC-620 PR #789 head 6f7c0a74c1e5dda0ea3a9f19186e1933dde4e8fc; DEC-619 landed on main at af98428b6d03f8a455f28105a834900b233e0f5d. DEC-620 focused tests and Phase 3 passed while final full historical regression and compilation were pending when DEC-621 was drafted. No step in this decision weakens predecessor gates.

DEC-621 models the one-shot operational response boundary *after a hypothetical attempted* GitHub workflow_dispatch request. HTTP errors, transport loss, timeout, an HTTP acceptance without a verifiable run record, contradictory run observations and wrong-SHA/run/attempt/predecessor results all lead to an unconditional terminal hold. Even a single exact **synthetic** run-385/attempt-1 observation requires independent evidence; it does not prove actual run consumption, lock enforcement or authorize retries. The model accepts no live GitHub network data and cannot issue a submission or retry.

The deterministic stdlib module sources the exact frozen annual workflow blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1 and validates original three-job main-only guards, strict local JSON schema and recursive duplicate-key rejection, workflow/run/ref SHA identity, and type-sensitive source-bound report integrity. The assess-only CLI forbids checkout output and has no network, source workflow mutation, GitHub API, tag/ruleset settings, broker or trading path. Every output forces live_annual_run_inventory_authenticated=false, effective_main_or_tag_lock_proven=false, annual_dispatch_authorized_by_report=false, second_dispatch_authorized=false, retry_authorized=false, rerun_authorized=false, replacement_run_authorized=false, dispatch_blocked=true, terminal_one_shot_hold=true and trading_authorized=false.

The active annual research target stays 2023/run385/attempt1, predecessor run 37663157285, unconsumed at last authenticated inventory. Real execution remains blocked under issue #779 until independently witnessed effective no-bypass lock throughout the server transaction, reviewed workflow/runtime amendment for tag path, renewed inventory and a separate one-shot authorization. An ambiguous request must never be retried by extrapolating from a client error. Companion: docs/phase8a-2023-run385-ambiguous-dispatch-hold.md.

### DEC-621 follow-up — DEC-620 predecessor has now landed

DEC-620 source-only PR #789 merged at `c756ecb884bc1cae47dff0ed0c881455fa0d460f` after exact-head focused tests, historical/general regression, compilation and Phase 3 all passed. The DEC-621 branch was subsequently retargeted to that verified main; its synthetic observed-run identity now also requires the exact installed annual workflow path and annual_segment_label `2023`, closing automated review P2 around same-name unrelated workflow or another year. DEC-621 still does **not** attest live run 385, authorize retry or dispatch, authenticate admin locks, alter protected workflow/runtime or trade.

## 2026-10-08 — DEC-622 inert 2023 runtime tag/workflow-ref and SHA binding contract

**Status:** SOURCE-ONLY / NOT INSTALLED / NOT AUTHORIZED FOR ANNUAL DISPATCH. DEC-621 merged via PR #790 to main `8515c66f27c1b5aa433a922954ed254038a6aa95` after exact-head focused, historical/general regression, compilation, Phase 3 and review checks all passed. Run 385 remains unconsumed; main remains unprotected, repository rulesets empty, and no independent administrative lock witness exists (issue #779).

The exact pinned annual workflow `.github/workflows/phase8a-annual-pattern-catalogue.yml` blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` still requires main in each preflight/cell/freeze job. The exact pinned 2023 runtime authorization source blob `cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191` checks the code commit SHA *format* but does not compare the GitHub server-resolved ref and SHA to an independently reviewed immutable approved tuple. DEC-622 implements **only an inert, synthetic negative-test contract** for a prospective SHA/ref gate, requiring exact workflow_dispatch event, tag ref/type, GITHUB_SHA, repository, workflow display name **and GITHUB_WORKFLOW_REF path@ref**, year 2023, run number 385, attempt 1 and previous 2022 freeze id 37663157285.

The sole positive fixture is deliberately unapproved and invented; 22 adverse/missing/forged context cases must be rejected. The offline report's complete content is reconstructed from the pinned original annual workflow and runtime gate and compared type-sensitively, so a recomputed hash cannot turn on any installation, dispatch, retry, broker or trading flag. The assess-only CLI refuses to write inside the repository and never contacts GitHub or changes code outside its source-only preview.

DEC-622 does not install a new runtime gate, alter three active workflow ref guards, approve or create a tag, authenticate rulesets, open historical data, dispatch/retry research, or trade. An eventual immutable-tag path requires distinct approval and installation of actual three-job workflow+2023 runtime source amendment, independent continuous authenticated no-bypass ref enforcement, renewed annual-run evidence and separate explicit one-shot run 385 action authorization. See docs/phase8a-2023-run385-runtime-tag-sha-binding-preview.md.

## 2026-10-08 — DEC-623 inert three-job pre-evidence runtime identity placement audit

**Status:** SOURCE-ONLY; not installed; no live workflow/runtime amendment, tag, dispatch or trade. DEC-622 merged in PR #791 at exact main `4060419eb2d3172da8d403b5ae7a0ac725d2ebb7`, after focused tests, historical/general regression, compilation, Phase 3 and code review passed.

An exact static inspection of the original unchanged annual workflow Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` exposed a placement distinction important to any proposed tag/SHA path: preflight currently performs GitHub API **metadata** requests for accepted EXP-044 feature/outcome runs and artifacts *before* the existing `require-execution` step, whereas annual_cell and annual_freeze run their execution checks before historical/cell artifact downloads. DEC-623 models a fabricated pre-access tag/SHA identity check label in all three job step-name lists and requires it to precede each job's first known evidence access. Nine synthetic missing/late/duplicated step checks fail. The model does not generate executable workflow YAML, edit live source, call GitHub, fetch historical data, or create authority.

A rebuilt, type-sensitive, pinned-source report rejects re-fingerprinted permissions; its CLI is assess-only and confines output outside checkout. This is a design topology audit, not a verified GitHub execution guard. Actual run 385 remains blocked by issue #779 pending independently authenticated continuous no-bypass admin/tag lock evidence, separately approved and tested *installed* three-job workflow plus 2023 runtime SHA/ref amendment, fresh run-number inventory, and a distinct explicit one-shot action approval. An ambiguous dispatch response is terminal without retry; no order or trading scope.

## 2026-10-08 — DEC-624 inert three-layer 2023 tag SHA/ref job admission and preinstall guard model

**Status:** SOURCE-ONLY / independently reviewed in PR #793, retargeted to verified DEC-623 main after PR #792 merged / NO LIVE AMENDMENT OR DISPATCH AUTHORIZATION. DEC-623 identified preflight metadata API access before the existing runtime execution check. DEC-624 identifies an earlier separate code-execution boundary: annual_preflight, annual_cell and annual_freeze all checkout the selected ref **before** their existing main-only manual-dispatch shell guard, and install the Python runtime after that main-only guard. A future tag-path workflow cannot rely on a post-install runtime identity test to protect setup or package installation; a step after checkout also cannot prevent checkout itself.

The source-pinned offline model stages an in-memory **job-level admission marker before checkout**, a fabricated exact-tag/workflow-ref/SHA identity check label **before setup and runtime installation**, and a fabricated postinstall binding check label **before first external evidence access**. All three labels/markers are synthetic; no executable YAML or active gate is generated or installed. Eighteen adverse missing/retyped/late scenarios must fail, and a complete pinned-source canonical report validator rejects rehashed permission or type changes.

Any real design still requires independently authenticated continuous administrator-enforced no-bypass tag immutability, an independently reviewed expectation tuple (never trust `GITHUB_SHA` as its own approval), separately approved and tested actual three-job workflow and 2023 runtime amendment, fresh 385 history, and explicit one-shot action approval. Issue #779 stays OPEN. No tag/ruleset mutation, workflow dispatch, retries, protected-history downloads, brokerage or trading.

### DEC-624 follow-up — exact DEC-623 merge verified, PR #793 now targets main

DEC-623 PR #792 merged at `eeadf2d44475ba2a1765327b2630939b13564f64` after full exact-head checks (focused unit suite, historical/general regression, compile and Phase 3 acceptance) and clean code review. PR #793's base moved from DEC-623 feature branch to this independently verified `main`; its source-only three-layer predicate remains uninstalled. A new exact-head test and review gate is required before DEC-624 merge. The workflow blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` is unchanged. No annual dispatch, tag creation, historical read, retry, trading or authorization occurs, and issue #779 remains OPEN.

## 2026-10-09 — DEC-625 uninstalled independent reviewed identity versus GitHub runner context boundary

**Status:** SOURCE-ONLY / inert synthetic fixture / no real immutable ref, workflow or runtime amendment, administrative grant, research dispatch or trading authority. DEC-625 follows the verified DEC-624 landing at `433505888275e049067c2914d6fb7e05694cdc6d`.

DEC-622 modeled exact runtime event, tag, workflow-ref and SHA comparisons; DEC-624 staged synthetic precheckout, preinstall and pre-evidence gate placements. DEC-625 closes an additional trust-model omission: **the expected reviewed ref/SHA cannot be derived from the same untrusted `github.ref`, `github.sha`, `github.workflow_ref` or `github.workflow_sha` values being checked.** A purported `reviewed` field inside the runner is not independently authenticated review evidence.

The source-only fixture pins the unchanged annual workflow and 2023 runtime Git blobs, tests independent-source-vs-observed tuple matching, and rejects 25 manipulated inputs including coordinated self-attested SHA and tag changes on **both** sides of the comparison. Exact source-bound canonical report regeneration rejects a rehashed forged authorization, and all live execution/broker/trading permissions remain false. A positive fixture means synthetic equality only—not immutable ref proof, external review or a workflow command.

Issue #779 remains OPEN: independently authenticated continuous no-bypass admin ref enforcement, separately reviewed real installed three-job and 2023 runtime gates using an external approved identity, fresh run-385 inventory and an explicit single action remain absent. The 2023 annual workflow dispatch slot must not be consumed; no retries, historical protected reads, phase promotions, future years or trading are authorized.

## 2026-10-09 — DEC-626 inert precheckout three-job if-expression preview

**Status:** source-only / stacked on DEC-625 PR #794 / **NOT INSTALLED**, no real tag, admin rule, annual dispatch or trading. DEC-624 established a synthetic job-admission-before-checkout topology; DEC-625 separated a fixed reviewed expected identity fixture from untrusted runner context. DEC-626 renders a literal candidate `jobs.<job>.if` expression for all three annual jobs in a report-only JSON object, using DEC-625's deliberately unapproved fixture and pinning existing untouched annual workflow/2023 runtime blobs.

The candidate compares exact `workflow_dispatch`, repository, tag ref/type, SHA, workflow ref and workflow SHA, year, previous freeze run, run number and attempt. Twenty-four negative variants reject missing/moved/softened job guards, removal of workflow SHA, self-attested `github.sha == github.sha`, wrong tag, run-type confusion and injected permission fields. The report SHA-256 is an integrity checksum, not external approval or cryptographic authentication; source-bound canonical regeneration rejects forged permission flags. No YAML modification or actual GitHub job gate is produced.

A GitHub job-level condition runs before job *steps* but not before the workflow definition is loaded. A full release still requires independently authenticated continuously enforced administrator tag lock with no bypass, a genuinely approved expected ref/SHA tuple from outside runner observations, separately reviewed and installed three-job/preinstall/preaccess workflow and 2023 runtime gates, fresh run385 inventory, and explicit one-shot dispatch decision. Issue #779 stays OPEN. No historical protected read, retry, future year, brokerage, demo/live, real money or trading is allowed.

## 2026-10-09 — DEC-627 read-only assess CLI bytecode side-effect containment

**Status:** SOURCE-ONLY / stacked after DEC-625 and DEC-626 / NO ANNUAL DISPATCH OR TRADING AUTHORIZATION. The independent DEC-625 review found that a top-level `fmp` Python import can write `__pycache__` under the checkout even if a later CLI output-path guard denies `--out` inside checkout. DEC-625/626 adopt early `sys.dont_write_bytecode = True` with execution tests; DEC-627 applies this same pre-import guard to 11 older assess-only annual research security audit CLIs (main-lock readiness, immutable-tag feasibility, tag-ruleset static review, tag-ref guard rehearsal, disarmed tag amendment, ref race, lock witness coverage, ambiguous dispatch hold, runtime ref/SHA binding, preaccess topology and three-layer job admission).

A dedicated focused CI test runs all eleven scripts' `--help` in real subprocesses from a clean copied checkout with `PYTHONDONTWRITEBYTECODE` and `PYTHONPYCACHEPREFIX` unset. It also runs actual offline `assess --out` processes for the self-contained DEC-618, DEC-622, DEC-623 and DEC-624 scripts, verifies report decision identity and `dispatch_blocked=true`/`trading_authorized=false`, and requires outputs outside checkout, unchanged checkout filename inventory and zero generated `.pyc` files. This repairs import-time audit side effects only; it does not authenticate a GitHub context, prove ref immutability, install workflow/runtime amendments, open research access or authorize dispatch or trading. Issue #779 stays OPEN and 2023 run385 remains unconsumed.

### DEC-627 review/landing handoff (2026-10-09)

DEC-625 PR #794 independently reviewed and merged at `5bbd7e2094571458ee2dfa65245beeb4bcc78ffa`; DEC-626 PR #795 independently reviewed and merged at `53e203133bbc141b2f48c7b8b8241d56b35166a3`. DEC-627 PR #796 was retargeted to that exact verified main and is not merged. Its first exact-head full CI and Phase 3 succeeded, but an independent Codex review failed to start because its usage quota was reached; **absence of a review must never be treated as approval**. The new expanded real-assess test must pass fresh exact-head CI and receive acceptable independent review before PR #796 can land. Live annual workflow, 2023 runtime, no-bypass administrator/ref settings, research dispatch and trading remain unchanged. Issue #779 stays OPEN.
