# DEC-2044 — Economic multi-fault ordering regression boundaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2292 head `23477970ddfec48e98baded30ab1e760bd794964`.

The installed source optional artifact auditor must validate independent source trade economics (reference-price gross, declared slippage, and recognized commission/financing models) before concluding that a dependent `net_pnl_usd` claim is inconsistent. DEC-2042 repaired the order after earlier full-suite failures; a valid source report with only a bad net claim must still be rejected, and source-equity continuity must still be checked after economic reconciliation.

Four source-defined test methods:
- Valid combined model with only a forged net PnL field: reject as net cost-reconciliation mismatch.
- Built-in zero-financing source claim with forged positive financing and unchanged net: reject precise source zero-financing mismatch **before** dependent net mismatch.
- Valid source net and costs with a forged realized after-equity: reject precise realized-equity mismatch.
- Generic synthetic run with material forged net PnL: retain generic net reconciliation refusal (the relaxed generic metric tolerance is not carte blanche).

All tests rehash manifest digests and confirm `verify_backtest_artifacts` before invoking opt-in structural auditing. No production change. **7,249 cumulative proposed test methods** (+4). Requires own exact-head Phase3/full historical-general checks. Earlier failed regressions remain failed. No real quote or brokerage provenance is claimed.

Phase8A #779/#820/#821 and eight independently supplied external security proofs remain blocked. No protected annual research, installed workflow/ref/runner changes, merges, strategy promotion, broker orders or real capital.
