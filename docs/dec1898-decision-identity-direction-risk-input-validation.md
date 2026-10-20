# DEC-1898 — Strict synthetic decision identity, direction, and risk fraction

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2146 `7bf0b29da67e40775d8e2d9d9768bb5c35fa27eb`.

A `Decision` accepted Boolean `requested_risk_fraction=True` (Python treats it as 1), non-enum direction strings such as `"NO_TRADE"`, and arbitrary control characters or untyped decision identifiers. Very large integer fractions raised raw OverflowError. These can create unstable backtest risk decisions and confusing provenance. Require nonempty printable ordinary string decision identifiers; an actual `Direction` enum; and strictly built-in integer/float, positive finite requested fractions (while leaving `None` as the existing default). Preserve valid directional and NO_TRADE decisions, and existing conservative `RiskConfig` limits enforced later by risk assessment.

Four additional Phase3 contract test methods bring cumulative proposed source-defined methods to **6,865**. This is an **unmerged backtester input validation proposal**, not actual market data, a validated profitable strategy or permission for protected historical research.

Issues #779, #820 and #821 remain OPEN, all eight independent real administrator/ref/runner/provenance/fresh inventory/human proofs MISSING. Accepted Phase8A annual discovery ends at 2022/run384; protected 2023/run385/attempt1, future year research, shadow/demo/live and capital remain BLOCKED. No installed GitHub workflow/ref/ruleset or broker changes; own exact-head Phase3/full regression and qualified independent review required.
