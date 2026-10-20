# DEC-1975 — Recheck stored Phase3 gross profit, gross loss and profit factor

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Dependent on PR #2223 at commit `6a11f7a0d62d3cdf45674aa3a105aa9e27e7368a`.

The optional stored artifact audit now reconciles net PnL and explicit costs, but without checking optional `metrics.json` profitability fields an adversary may rewrite gross profit, gross loss or profit factor and update SHA256 and sizes to make those false numbers appear self-consistent.

Add independent summation of positive and negative stored trade net PnL; audit optional `gross_profit_usd`, `gross_loss_usd`, `profit_factor` against those values with bounded numerical tolerance for source order differences. Require null profit factor when no gross losses exist, matching the writer. Fail closed on wrong types or non-finite derived aggregates. Absent optional metric fields remain allowed.

Four source-defined test methods cover valid win/loss profitability metrics, writer-compatible null profit factor with no losers, false profit/factor claims despite recomputed manifest digests and incorrect nonnull profit factor on zero loss. Cumulative proposed inventory **7,026 methods**, not a verified CI pass count.

Review/CI: require own exact commit Phase3 and historical/general test suite. Prior full-regression #2212 remains FAILED despite #2222's repair draft. Phase8A security issues #779/#820/#821 and eight external independent proofs remain missing. Accepted annual research through 2022/run384 only. Protected 2023/run385/attempt1, strategy economics, broker, capital, merge and runner/ref workflow changes prohibited.
