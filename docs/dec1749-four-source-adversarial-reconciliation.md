# DEC-1749 — Adversarial validation of four-source Phase 8A reconciliation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests/docs-only child of #1995 (`c535908c0d721d9c896dcf37495f5b103e1995fa`), not a merge or gate promotion.

Adds **44** source-defined test methods (**6254 cumulative proposed**). Mutates isolated deep copies of DEC-1726 annual, DEC-1739 economic, DEC-1742 14-node approval dependency graph and DEC-1745 unfilled StrategyV1 preregistration; each case must be refused by an actual DEC-1748 test. Covered forgeries include annual skipped years, changed run385 identity, bool/int confusion, fabricated research evidence, falsified admin/run-inventory witnesses, missing slippage/holdout requirements, fabricated 2023 freeze, skipped risk and phase gates, invented forward profitability and authority, retrospective thresholds and embedded broker/dispatch actions. Includes clean 23-method cross-source control.

These tests cannot themselves prove the 2023 one-shot is safe, that external admin/privileged OS controls exist, or that Strategy V1 has any live positive net expectancy. No protected-year read, workflow installation/dispatch/retry, strategy synthesis, shadow, demo or live operation is allowed. Issue #779 and #820/#821 remain BLOCKED. Requires exact-head Phase 3/full historical-general CI and independent qualified review.
