# DEC-1884 — Strict numeric types in proposed risk-fraction configuration

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2131 `450262e4dba38f7dfde92de6d28beabd3bdb35bb`.

`RiskConfig` enforces finite, positive risk fractions and the existing per-trade/simultaneous ordering constraints, but `math.isfinite(True)` succeeds because Python Booleans are integer subclasses. Nonnumeric values or unusually huge integer inputs can also raise raw errors before the configured risk rules are applied. Require built-in int/float values (excluding booleans), retain strictly positive finite bounds and normalize `OverflowError` to a controlled `ValueError`. Default quarter-percent risk, maximum half-percent per trade, one-percent simultaneous risk and existing daily-loss halt remain unchanged.

Three new source-defined Phase3 risk methods (**6,830 cumulative proposed**) test all four parameters with Boolean/nonnumeric/nonfinite/overflow inputs and normal ordered defaults. This is a proposed backtester risk-config type contract, not an approved live risk limit or capital-protection mechanism. No installed workflows, protected data reads, research dispatches, broker actions or demonstrated profit.

Accepted annual-first catalogue ends with 2022/run384. Protected 2023/run385/attempt1 and later annual research, Strategy V1, demo/live, real capital and workflow/ref/ruleset modifications remain BLOCKED. All eight external independent security/OS/provenance/inventory/human packages under #779/#820/#821 remain MISSING. Own exact-head Phase3/full CI and qualified review required.
