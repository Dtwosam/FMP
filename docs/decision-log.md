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
