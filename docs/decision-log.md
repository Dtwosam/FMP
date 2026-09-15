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
