# DEC-1907 — Exact risk-assessment admission before UTC-day mutation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Source/tests/docs one-commit child of #2155 at `50543dba1ea51fb0d8605a2f1c78faac4f7ea531`.

The `assess_decision` entry point previously advanced the mutable risk UTC day before dereferencing `decision.direction`, `config` limits and `state` members. Malformed or hostile caller objects could cause incidental exceptions or run an attribute getter after a risk-state update. Require exact `Decision`, `RiskConfig` and `RiskState` records after existing nonfinite-price rejection but **before** `roll_utc_day`. This retains the valid directional assessment and existing invalid-entry-price rejection behavior.

Two source-defined synthetic tests ensure bad config is refused without modifying day, equity, risk reservations or daily halt; and hostile decision attribute getters and malformed state inputs cannot be evaluated. Total **6,886 cumulative proposed source-defined test methods**. Exact-head Phase3/full historical-general CI and qualified independent risk review are required; no success inherited from older SHA.

External Phase 8A blockers #779/#820/#821 and eight security proofs still MISSING/BLOCKED. Protected annual 2023/run385/attempt1, future research, Strategy V1 and shadow/demo/live deployment remain unauthorized. No installed workflow/ref/ruleset/runner or broker mutations, money, protected data or research dispatch.
