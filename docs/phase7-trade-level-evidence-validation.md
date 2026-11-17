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
- R equal to net PnL divided by pre-trade equity times the submission's requested risk fraction;
- the requested fraction inside `(0, 0.005]`, the existing hard maximum;
- declared trade counts and cost totals, optional expected trade ids, and overlapping windows only when both sides are marked `separate_scenario`;
- an intrabar ambiguity flag, which must use `conservative_adverse` when it is true.

Acceptance means those rows agree with each other. `original_phase7_trade_ledger_verified` is always false. Closed trades do not show simultaneous open risk or whether a daily loss halt fired. Independent windows are not one compounded account.

`synthetic_fixture` provenance must not carry a source run, artifact, or commit, and must not be labeled as the original Phase 7 result. `claims_trades_from_stage2_zip=True` is rejected because that ZIP has no trade ledger. A `separately_authorized_submission` may cite the public run id and still remains unverified.

Synthetic tests in `tests/test_trade_level_evidence.py` build their prices with `pnl_usd`. They are not Phase 7 results.

## Statistical inputs

The published Stage 2 dollars, the window-start `$250` R approximation, and a win rate are not enough for any estimand below. `assess_statistical_readiness` does not calculate a strategy probability, a confidence interval, or an account-loss distribution. `demonstrated_edge` and `leverage_optimized` stay false. `selected_scenario` stays unset.

| Estimand | Inputs required before an estimate would be defined | What this component does |
| --- | --- | --- |
| After-cost expectancy | An accepted ledger. Per-trade R uses that trade's own pre-trade equity and the requested fraction, not a fixed `$250`. Spread basis, slippage, commission, and financing reconcile as above. | Reports the descriptive sample mean of those R values. Status `DESCRIPTIVE_ONLY`. The mean is not a confirmatory expectancy. |
| Confidence interval | At least two accepted trades. Dependence declared as blocked, with an explicit block such as UTC week. An `iid` declaration is rejected. A complete predeclared family size. Data reuse `prospective` or `untouched_predeclared`. A dated cost-provenance id. | Does not compute an interval. Unknown census, `iid` dependence, `already_scored` or unknown reuse, and a missing cost provenance block it. A complete declaration that this component has not authenticated is `INPUTS_PRESENT_NOT_COMPUTED`. |
| Loss and drawdown distribution | The interval inputs, an overlap declaration (`no_overlap` or `overlaps_modeled`), and a mark-to-market equity path. Exit-only trade rows miss the path between entry and exit. | Does not build the distribution. `realized_exit_only` and an unspecified path are blocked. |
| Probability of doubling within 30 calendar days | The drawdown inputs, horizon exactly 30 days, a no-trade calendar of at least 30 days, a terminal or touch path declared on its own, and an explicit doubling barrier. | Does not compute the probability. The same blockers apply. Phase 7's scored 2024 and 2025–2026 windows are `already_scored` and cannot be reused as untouched confirmation. |
| Probability of losing at least 50% | The doubling inputs, with loss barrier `0.5` declared. | Does not compute the probability. |
| Probability of losing at least 90% | The doubling inputs, with loss barrier `0.9` declared. | Does not compute the probability. |
| Cost and frequency sensitivity | At least one other accepted cost ledger and one other accepted frequency ledger. Same provenance role. Same requested risk fraction. | Lists each scenario's descriptive mean R in the order supplied. Reports whether any scenario mean has the opposite sign from the primary mean. Selects no scenario. A different risk fraction is a leverage change and blocks the comparison. |

Dependence between trades, selection bias, reused history, and execution-cost uncertainty are part of the input list above. DEC-633 leaves the programme-wide trial count unknown, so a caller cannot treat the backfilled ledger as a complete family. DEC-628 still has no observed session spread, no live OANDA or Pepperstone swap, and no USD point value for GBPUSD or USDJPY swaps. Those gaps stay attached to any later cost provenance.

The 100%-within-30-days question remains a falsifiable research question. A simulated probability is not evidence of a trading advantage. No strategy is profitable on the strength of this component.

## Next path

The shortest path to a real evaluation is a separate owner authorization to identify whether an individual trade ledger exists outside the three-file Stage 2 ZIP, and then to supply that ledger to `validate_trade_submission` without relabeling the scored windows as untouched. A replay of run `35015277625` is a different decision and is not authorized here. Annual catalogue work stays behind issue #779.
