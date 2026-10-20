# DEC-1895 — Separate invalid input amount from risk-reservation aggregate overflow

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2143 at `eda80f52f6cc5036ad4166bf81527a54a1d64cb3`.

The exact-head full historical/general CI for PRs #2140–#2143 **FAILED** in `test_risk_reservation_rejects_invalid_amount_before_mutation` for a huge integer `10**400`. The risk reservation code correctly rejected the input without touching risk state, but its shared `try/except OverflowError` classified `math.isfinite(10**400)` as an **aggregate** overflow, contrary to the stable input-validation contract requiring a `risk amount` ValueError. This error message is important for distinguishing an invalid submitted position size from otherwise valid positions whose sum overflows.

Separate two precise validation stages: reject invalid/overflowing `amount_usd` as `reserved risk amount must be finite and positive`, then only classify overflow when adding it to the existing aggregate as `reserved risk aggregate must remain finite`. Existing finite sum check and mutation-after-validation order are unchanged. Two additional tests reinforce the classification and atomicity. Cumulative proposed source-defined test methods increase from 6,855 to **6,857**.

No protected 2023/run385/attempt1 research dispatch, installed workflow/ref/ruleset/runner modifications, broker/demo/live orders, capital or demonstrated profitability. External blockers #779/#820/#821 and all eight independently reviewed proofs still MISSING/BLOCKED. The repair is an **unmerged source-only draft** requiring own exact-head Phase3/full CI and independent scoped risk review; old #2140–#2143 full FAIL remains part of the historical record.
