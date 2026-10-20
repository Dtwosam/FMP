# DEC-1870 — Reject Boolean and malformed backtest configuration scalars

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2117 at `fb56336cd8844b7afc66af6d0862cf6f121745a7`. Scoped Phase3 backtester configuration validation only; own exact-head Phase3/full historical general regression and independent cost/risk code review are mandatory.

`BacktestConfig.__post_init__` checked `math.isfinite` for starting equity and slippage pips, but Python accepts Booleans as numeric (`True == 1`), silently allowing `starting_equity_usd=True` and `slippage_pips=False`. A nonnumeric value raises a raw TypeError; an extreme integer may raise OverflowError. These are not valid declared float-like configuration inputs and may misstate hypothetical risk sizing/economics. Require exact built-in int or float, nonfinite/negative checks as before, and normalize integer-overflow into ValueError. Keep valid normal numeric settings, engine version, bar timing, all FX contracts and no-lookahead policies unchanged.

Three new source-defined Phase3 test methods bring the cumulative proposed count to **6,792**. All are synthetic configuration examples; no protected market data, live/forward trading, broker action or evidence of profitable expectancy.

The unmerged code does not authorize 2023/run385/attempt1 or any later annual Phase8A research, Strategy V1 selection, demo/live, capital or installed workflow/ref/ruleset/runner changes. Eight independently authenticated security/inventory/provenance/human prerequisites for #779/#820/#821 remain MISSING/BLOCKED.
