# Phase 7 trade-level evidence validation

**Date:** 2026-11-17  
**Status:** SOURCE-ONLY VALIDATION CONTRACT — NOT AN ACCEPTANCE GATE, STRATEGY RESULT, OR AUTHORIZATION  
**Governing method:** discovery-first annual pattern catalogue (DEC-268 / DEC-469)  
**Pattern type / tool:** none. This document and `src/fmp/research/trade_level_evidence.py` check a caller-supplied closed-trade ledger. They are not a pattern grammar and they do not replace the annual catalogue.  
**Authorized annual segments:** none. Protected 2023 run 385 / attempt 1 stays unconsumed.  
**Task stage:** evidence readiness for a future separately authorized ledger.  
**Protected boundary:** no historical artifact is opened, no workflow is dispatched, and no broker or trading path is enabled.

DEC-629 and DEC-630 remain proposed and unadopted. Issues #779, #820, and #821 remain unresolved.

## Preservation identities

These five objects stay separate. The machine-readable copy is `phase7_public_preservation_record()`.

| Object | Identity | What it contains |
| --- | --- | --- |
| Original historical run | `phase7-walk-forward` run `35015277625`, attempt 1, success, head `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d` | The historical Stage 2 execution. Metadata is not permission to dispatch it again. |
| Original artifact | `10414817824`, name `phase7-stage2-session_breakout-a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`, ZIP SHA-256 `2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4` | The GitHub artifact. Created `2026-09-15T19:43:43Z`. Expires `2026-12-14T19:43:07Z`. |
| Preserved copy | Owner-stated ChatGPT Library path `/FMP/Phase7/` | A copy the owner says was saved from that artifact. This session did not open it and did not recompute its hash. |
| Published aggregates | `docs/phase7-walk-forward-evidence.md`, experiment `EXP-20260915-008` | Seven independent windows at three slippage settings. Stage 2 states 199 trades. The ordered per-trade R series is not in that document. |
| Individual trade records | Unavailable from sources this component is allowed to read | Not in the documented ZIP, and not established anywhere else by this session. |

On 2026-11-17 the public GitHub artifact metadata was read again and the ZIP was not downloaded. The artifact was `expired=false`, digest `sha256:2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4`, and `size_in_bytes=5711`. The documented members remain `manifest.json`, `result.json`, and `windows.json`. That archive does not contain a trade-level R series. The December 14 expiry is a retention fact. It is not approval to download, extend retention, or replay the run.

The readiness audit in `docs/phase7-trade-level-evidence-readiness-audit.md` traces why the frozen Stage 2 writer saves aggregates only. This file does not repeat that trace.

## Validator

`validate_trade_submission` accepts an in-memory `TradeSubmission`. It does not take a path. A string path raises `TypeError`.

A row is checked for:

- unique trade and decision identities;
- UTC entry and exit, with exit after entry, both inside the half-open window, ordered by exit time then trade id;
- positive prices, protective stop side, and a target on the profit side when a target is present;
- gross PnL from reference prices through `pnl_usd`, execution PnL from fill prices, and slippage equal to the adverse gap only (`max(0, gross - slipped)`);
- non-negative commission, finite financing (a credit is negative financing), and a declared spread basis;
- no second spread deduction when the basis is `included_in_bid_ask_reference`;
- net PnL equal to gross minus slippage, commission, financing, and any separate spread;
- window starting equity, then equity after each trade equal to equity before plus that trade's net PnL;
- gross profit equal to the sum of positive net PnL, and gross loss equal to the Phase 3 positive magnitude `-sum(negative net PnL)`;
- R equal to net PnL divided by the recorded pre-PnL equity times the submission's requested risk fraction;
- the requested fraction inside `(0, 0.005]`, the existing hard maximum;
- declared trade counts and cost totals, optional expected trade ids, and overlapping windows only when both sides are marked `separate_scenario`;
- an intrabar ambiguity flag, which must use `conservative_adverse` when it is true.

Acceptance means those rows agree with each other. `original_phase7_trade_ledger_verified` is always false. Closed trades do not show simultaneous open risk or whether a daily loss halt fired. Independent windows are not one compounded account.

`gross_loss_usd` follows `compute_backtest_metrics` in `src/fmp/reporting/backtest.py`: losses are the negative net results, and gross loss is their sign-flipped sum. A declared negative gross loss does not match that total. Gross profit remains the sum of positive net results. Both totals are taken after slippage, commission, financing, and any separate spread, because Phase 3 builds them from `net_pnl_usd`.

## R definitions

`r_definition` is `requested_risk_normalized_at_recorded_equity`. That is the only R this component reports.

The engine in `finalize_position` stores `risk_equity_before_usd` from `state.risk_equity_usd` at exit, before that trade's own PnL is applied. `compute_research_metrics` divides net PnL by that recorded equity times the requested fraction. The validator uses the same denominator. It does not change the historical research metric.

Three quantities stay separate:

1. Requested-risk-normalized R at the recorded equity. This is `net_pnl_usd / (risk_equity_before_usd × requested_risk_fraction)`.
2. Actual initial position risk. `size_units` floors units so `units × loss_usd_per_unit(entry, stop)` can be below the requested budget. `TradeRecord` does not store that reserved amount, and this component does not invent it.
3. Net R on actual initial risk, `net_pnl_usd / actual initial position risk`. A submission that only carries the recorded equity does not contain this ratio. It is not substituted for the reported R.

Recorded equity can differ from the equity at entry when another trade realizes PnL while the position is still open. The equity chain follows exit order. An R claim that divides by the earlier entry equity fails `R_MISMATCH`.

`synthetic_fixture` provenance must not carry a source run, artifact, or commit, and must not be labeled as the original Phase 7 result. `claims_trades_from_stage2_zip=True` is rejected because that ZIP has no trade ledger. A `separately_authorized_submission` may cite the public run id and still remains unverified.

Synthetic tests in `tests/test_trade_level_evidence.py` build their prices with `pnl_usd`. They are not Phase 7 results.

## Statistical inputs

The published Stage 2 dollars, the window-start `$250` R approximation, and a win rate are not enough for any estimand below. `assess_statistical_readiness` does not calculate a strategy probability, a confidence interval, or an account-loss distribution. `demonstrated_edge` and `leverage_optimized` stay false. `selected_scenario` stays unset.

| Estimand | Inputs required before an estimate would be defined | What this component does |
| --- | --- | --- |
| After-cost expectancy | An accepted ledger. Per-trade R uses the recorded exit equity and the requested fraction, not a fixed `$250` and not the stop-distance risk. Spread basis, slippage, commission, and financing reconcile as above. | Reports the descriptive sample mean of those requested-risk R values. Status `DESCRIPTIVE_ONLY`. The mean is not a confirmatory expectancy. |
| Confidence interval | At least two accepted trades. Dependence declared as blocked, with an explicit block such as UTC week. An `iid` declaration is rejected. A complete predeclared family size. Data reuse `prospective` or `untouched_predeclared`. A dated cost-provenance id. | Does not compute an interval. Unknown census, `iid` dependence, `already_scored` or unknown reuse, and a missing cost provenance block it. A complete declaration that this component has not authenticated is `INPUTS_PRESENT_NOT_COMPUTED`. |
| Loss and drawdown distribution | The interval inputs, an overlap declaration (`no_overlap` or `overlaps_modeled`), and a mark-to-market equity path. Exit-only trade rows miss the path between entry and exit. | Does not build the distribution. `realized_exit_only` and an unspecified path are blocked. |
| Probability of doubling within 30 calendar days | The drawdown inputs, horizon exactly 30 days, a no-trade calendar of at least 30 days, a terminal or touch path declared on its own, and an explicit doubling barrier. | Does not compute the probability. The same blockers apply. Phase 7's scored 2024 and 2025–2026 windows are `already_scored` and cannot be reused as untouched confirmation. |
| Probability of losing at least 50% | The doubling inputs, with loss barrier `0.5` declared. | Does not compute the probability. |
| Probability of losing at least 90% | The doubling inputs, with loss barrier `0.9` declared. | Does not compute the probability. |
| Cost and frequency sensitivity | At least one other accepted cost ledger and one other accepted frequency ledger. Same provenance role. Same requested risk fraction. | Lists each scenario's descriptive mean R in the order supplied. Reports whether any scenario mean has the opposite sign from the primary mean. Selects no scenario. A different risk fraction is a leverage change and blocks the comparison. |

Dependence between trades, selection bias, reused history, and execution-cost uncertainty are part of the input list above. DEC-633 leaves the programme-wide trial count unknown, so a caller cannot treat the backfilled ledger as a complete family. DEC-628 still has no observed session spread, no live OANDA or Pepperstone swap, and no USD point value for GBPUSD or USDJPY swaps. Those gaps stay attached to any later cost provenance.

The 100%-within-30-days question remains a falsifiable research question. A simulated probability is not evidence of a trading advantage. No strategy is profitable on the strength of this component.

## Next path

The bounded name search did not find the 199 Stage 2 trades. DEC-636 can retain the trade and rejection rows the existing evaluator already returns, in a separate checksummed directory, and load one submission per slippage scenario into this validator. Gross loss stays the positive Phase 3 magnitude. `original_phase7_trade_ledger_verified` stays false. No authentic 199-trade series has been recovered.

The bounded reproduction procedure is in `docs/phase7-stage2-trade-recovery-decision.md`. That document does not authorize the reproduction, a download of the Phase 4 benchmark artifacts, a workflow dispatch, or a fresh out-of-sample claim. The next milestone is a formal owner decision on whether to authorize one controlled historical reproduction. Annual catalogue work stays behind issue #779.
