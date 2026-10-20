# DEC-1897 — Correct synthetic integer-price OHLC test fixture

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent test-only repair of #2145 `d8248fbafcfa6709529f413cec21f1b9c57792c1`.

DEC-1896's new valid numeric quote test used `replace(quote_bar(), bid_open=1)`. The original bar's `bid_low=1.099`; lowering its open to 1 violates the existing and correct `bid_low <= bid_open` OHLC invariant. This falsely fails the test despite the shared price type guard being correct. Use `replace(quote_bar(), bid_low=1)` instead; this exercises legitimate integer price acceptance while respecting bid/ask OHLC and spread relationships.

No production logic, execution permissions or test method count change (**6,861 proposed source-defined**). This is not real price data, real runner attestation, market expectancy or permission to dispatch protected run385. External #779/#820/#821 eight proofs remain MISSING/BLOCKED. All drafts unmerged; exact-head Phase3/full CI and independent code review required.
