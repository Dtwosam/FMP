# DEC-1995 — Validate source-defined risk budget identity in stored audit

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent successor to PR #2243 at `ddfd1638a6b36942c4a435ae9f391ae335bd4869`.

The source RiskConfig.to_config() publishes exactly four positive fractions not above 100%, with default_per_trade <= max_per_trade <= max_simultaneous. A rehashed summary could previously claim malformed risk budgets while passing the audit's generic JSON source-identity checks. This change rejects missing/extra keys, Boolean/nonfinite/zero/>1 fractions, and hierarchy inversions when the optional run_identity.risk_config exists. It matches RiskConfig's source semantics without assessing whether the underlying risk inputs are externally authenticated.

Four source-defined tests: writer-compatible RiskConfig-shaped identity, rehashed zero/Boolean default fraction, inverted risk hierarchy, and missing required daily loss limit. Synthetic backtests without risk_config remain permitted. Cumulative **7,083 proposed source-defined tests** (+4). Independent exact-head Phase3 and full historical/general regression required; previous CI failures remain recorded as failures.

Phase8A security blockers #779/#820/#821 and eight external proof packages remain unsatisfied. No protected research, installed runner/ref/workflow mutation, broker/demo/live orders, strategy promotion, merges or capital.
