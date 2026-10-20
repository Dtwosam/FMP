# DEC-1892 — Do not accept risk fractions above 100 percent

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2140 `8dc3ee79a120a5fc29633dcb2102022b8b10bea1`.

`RiskConfig` enforces four positive finite risk-fraction settings and ordering of default/per-trade/simultaneous limits, but did not impose the mathematical definition of a fraction: all values should be at most 1. A daily-loss halt fraction greater than 1 can be especially misleading, effectively disabling ordinary halt behavior before equity goes below zero. Require `default_risk_fraction`, `max_risk_fraction`, `max_simultaneous_risk_fraction` and `daily_loss_halt_fraction` each not exceed 1.0. This preserves the project's existing default risk limits (0.25% default, 0.5% per trade, 1% simultaneous risk, 1.5% daily halt). No default change or order-execution change is proposed.

Two new Phase3 methods (**6,853 cumulative proposed source-defined**) reject over-100% values for each field and confirm the mathematically valid upper boundary under correctly ordered limits. Because a permitted 100% risk fraction is still economically dangerous, this check is a type/domain safety invariant **not** a recommendation for trading at those limits. All code remains unmerged and requires own exact-head Phase3/full historical-general CI and qualified human risk review.

Phase8A accepted annual evidence stops 2022/run384. Protected 2023/run385/attempt1, later annual/cross-year work, Strategy V1 selection, shadow/demo/live broker activity, capital and installed workflow/ref/ruleset mutation remain BLOCKED. All eight independently authenticated external security/provenance/runner/inventory/human proofs under #779/#820/#821 remain MISSING.
