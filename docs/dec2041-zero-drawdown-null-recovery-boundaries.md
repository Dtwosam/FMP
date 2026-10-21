# DEC-2041 — Source zero drawdown and null recovery witness boundaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2289 at `e7c08604510f85a4b3ee267fde8108c4d83e4542`.

The installed source metric writer starts its realized-equity drawdown series from starting equity and returns `max_drawdown_usd=0`, `max_drawdown_fraction=0` and `recovery_factor=None` for a valid zero-trade, zero-drawdown report. DEC-2040's exact installed-source metric comparison preserves that null case while refusing arbitrarily small rehashed nonzero drawdown fractions.

This test/docs-only child adds three source-defined methods: accept a zero-trade source report with zero drawdown and null recovery; reject a manifest-rehashed 1e-13 `max_drawdown_fraction` claim despite no drawdown; and reject a nonnull `recovery_factor` when no drawdown exists. No production changes. This is source artifact consistency and does not certify live trading returns.

**7,241 cumulative proposed source-defined methods** (+3). Own exact-head Phase3 and full historical/general regression suites required; unfinished checks remain unconfirmed and historical failures remain failures.

Phase8A #779/#820/#821 and eight independent security proof packages remain blocked. No protected annual research, installed workflow/ref/runner changes, merges, broker orders, strategy promotion or real-capital activity.
