# DEC-1875 — Validate basic cost-model interfaces before a backtest run

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2122 `1c89da7929e6aea3e435c3f0a74f9393c3782b15`.

`BacktestConfig` declares `commission_model: CommissionModel` and `financing_model: FinancingModel` structural protocols, but their runtime objects were not checked. An accidental `None`, string, list or object lacking `cost_usd()` or `to_config()` may appear to create a valid backtest configuration, then fail after execution or when serializing the run identity. Require that both methods are callable for both model fields when the configuration is constructed. Do **not** invoke a custom model during validation or restrict it to a single concrete built-in class; a duly reviewed compatible custom model can still implement the structural protocol.

Four new Phase3 tests (6,807 cumulative proposed source-defined) cover missing models, partial protocol implementations and unchanged zero-model behavior. These checks do not prove that an arbitrary custom model is economically correct or free of side effects; comprehensive future cost-model review remains separate. The code is unmerged and requires exact-head Phase3/full historical-general regression plus human scoped review.

This draft cannot authorize protected 2023/run385/attempt1 or any subsequent annual research, Strategy V1 selection, real broker/demo/live, installed ref/workflow/ruleset/runner changes or money. Independent #779/#820/#821 security, provenance, inventory and human decision packages all remain MISSING/BLOCKED.
