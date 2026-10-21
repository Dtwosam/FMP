# DEC-2014 — Installed source intrabar ambiguity stop/target witness

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2262 at `dd196133d3ed664ded407296b75b35628f54bbb9`.

`evaluate_exit` in the Phase3 installed source engine sets `intrabar_ambiguous=True` **only** when both stop and target levels are hit within the same quote bar, after the stop-gap branch has already been ruled out. Its conservative fill policy assigns `ExitReason.STOP` and `exit_reference_price = stop_price`, and this condition presupposes a non-null target. The optional artifact auditor formerly type-checked the ambiguity flag and stop/target geometry but did not reconcile these three fields for a source-engine claim.

For the exact installed `BACKTEST_ENGINE_VERSION`, refuse an ambiguous trade unless the exit reason is STOP, a target is present, and the reference exit equals its stop price. Unambiguous STOP trades may gap at a different price; no external bar/OHLC provenance is inferred. Generic and alternate-engine synthetic reports retain their historical flexibility.

Four new source-defined test methods: valid ambiguous stop exit with consistent economic ledger; checksum-verified forged ambiguity on a target exit; ambiguous stop without a target; and generic synthetic compatibility. **7,144 proposed cumulative methods** (+4). This is a source semantic assertion, not proof that both levels actually traded on any external market bar. Own exact-head Phase3 and full historical/general CI required.

Phase8A #779/#820/#821 and eight independently supplied security proof packages remain blocked. No protected research, installed workflow/ref/runner changes, brokerage/orders, real capital, strategy promotion or merge.
