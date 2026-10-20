# DEC-1882 — Reject risk-equity overflow before changing state

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2129 `e0d4ce7650daa78e3ed3a551891cf957a50d678d`.

The Phase3 risk policy checked that an incoming realized `pnl_usd` was finite, but subsequently added it to `risk_equity_usd` and `day_realized_pnl_usd` without checking the sums. Two individually finite values of `1e308` can create infinite equity. A rejected malformed input also should not advance the UTC-day state.

Compute next equity and next-day realized P&L first, rejecting Boolean/non-numeric/nonfinite inputs, extreme integer overflow and nonfinite combined totals. Only then roll the UTC day and commit the two new values. Ordinary finite gains/losses and the daily-loss-halt rule continue to use the original UTC day-start basis. Three new source-defined Phase3 risk methods (**6,824 cumulative proposed**) check overflow leaves the state unchanged, malformed P&L leaves the UTC day untouched, and ordinary same-day accounting remains correct. This is a fail-closed *local backtester risk model* change, not an installed capital protection control.

No protected data, Strategy V1 economic performance evidence, live broker order, real money or one-shot run authorization. Protected 2023/run385/attempt1, later research, shadow/demo/live and ref/workflow/ruleset changes remain BLOCKED. Independent #779/#820/#821 eight external security/runner/provenance/inventory/human proof packages remain MISSING. Exact-head Phase3/full CI and qualified independent code/security review required.
