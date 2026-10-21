# DEC-2046 — Signed financing aggregate metrics in exact source reports

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact dependent parent PR #2294 at `9e406feaa739d17b14379e5dfab2a0c892d41e79`.

The installed source's custom financing interface permits signed debit/credit amounts; built-in zero-financing remains separately constrained. The source writer sums reported financing costs as signed values and includes them in total explicit costs and net PnL. DEC-2034 requires source-version aggregate metrics to match canonical trade evidence exactly, while DEC-2043 established canonical rehashed testing for permitted generic metric tolerance.

This test/docs-only draft adds three source-defined methods:
- Accept correctly modeled one-trade source reports with full net, slip, commission, financing and total-cost metrics for both a USD 1.25 financing **credit** and a USD 1.25 **debit**.
- Reject a manifest-rehashed, writer-canonical near-equal `financing_cost_usd` aggregate claim (1e-9 drift) for the source version while individual trade economics stay unchanged.
- Accept that same near-equal metric difference in the generic synthetic report when the manifest is correctly rehashed, without relaxing the installed source's exact aggregate checks.

**7,256 cumulative proposed source-defined methods** (+3). No production changes. Own exact-head Phase3/full historical-general suites required; earlier failed checks remain failed and pending suites remain unconfirmed. These synthetic custom financing examples do not establish actual broker charging or earned returns.

Phase8A #779/#820/#821 plus eight independent external security proof packages remain blocked. No protected annual research, installed workflows/refs/runners, merges, strategy promotion, broker orders or real capital.
