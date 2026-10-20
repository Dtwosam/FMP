# DEC-1911 — Reject contaminated realized-risk equity before day roll

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit source/tests/docs child of #2159 at `5d1608710857e41c6a7f27d973ad7abc53f641f7`.

`RiskState` has mutable `risk_equity_usd` despite a validated initial equity. If callers contaminated that field with a string, Boolean, huge integer or nonfinite float, `roll_utc_day` could previously copy it to the next day's baseline and `record_realized_pnl` could raise an incidental TypeError. Require ordinary finite numeric risk equity before daily rollover or realized-PnL state updates. Because `assess_decision` calls the same rollover, it refuses contaminated equity before risk approval and cannot advance the day. Valid positive or finite-loss equity arithmetic and existing risk limits are unchanged.

Three synthetic source-defined methods verify nonnumeric/NaN/infinite/overflowed equity rejection in rollover, realized-PnL atomicity and directional risk assessment with reservations unchanged. **6,898 cumulative proposed source-defined methods**. Own Phase3 and full historical/general CI plus independent qualified risk review required; any earlier-head passing checks are not a replacement.

Phase8A #779/#820/#821 and eight independent administrator/ref/source/runner OS/provenance/fresh inventory/human authorization proofs remain MISSING/BLOCKED. The protected 2023/run385/attempt1 unit, future research, Strategy V1 economics, shadow/demo/Phase10/11 and live broker capital remain unauthorized. No protected data, installed GitHub workflow/ruleset/runner change, dispatch, broker order or money action.
