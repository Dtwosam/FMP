# DEC-1996 — Audit built-in cost-model source identity without blocking custom models

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2244 at `3b438ae6375dcab7f053cc0e9c0d4118ea56eb6a`.

The built-in Phase3 cost models serialize explicit configurations: ZeroCommission -> `{"model":"zero_commission"}`; FixedCommissionPerMillion -> `{"model":"fixed_per_million_per_side","usd_per_million_per_side": rate>=0}`; ZeroFinancing -> `{"model":"zero_financing"}`. Arbitrary evidence may be rehashed to disguise invalid rate values or extra fields claiming zero costs. The source BacktestConfig intentionally permits independent custom CommissionModel / FinancingModel objects implementing cost_usd and to_config, so blanket rejection of all other model names would break legitimate output.

When `summary.run_identity.commission_model` or `financing_model` is present, validate it is an ordinary object; validate *recognized built-in model names* against source-specific exact fields and finite nonnegative numeric rate. Preserve custom model configurations without pretending they authenticate actual broker costs or provenance. Four synthetic tests cover valid zero/fixed models, rehashed negative/Boolean fixed rate, rehashed hidden zero-financing field and custom provider compatibility.

Cumulative **7,087 proposed source-defined tests** (+4); exact-head Phase3/full historical-general suites and review required. Previous CI failure histories remain failed, no security-trading promotion.

Phase8A #779/#820/#821 and eight independent proof packages still missing. No installed runner/ref/workflow, protected run385, annual research, strategy promotion, broker orders, capital, merges. **DRAFT NEVER MERGE NEVER PROMOTE.**
