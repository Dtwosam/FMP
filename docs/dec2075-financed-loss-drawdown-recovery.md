# DEC-2075 — Source financed net loss drives checkpoint drawdown and recovery

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2323 at `ad6a0fa4a37f3d3bb6dff403f8d98aa7a5ed9be3`.

A source trade with positive execution gross PnL but net loss from a deterministic custom-financing debit must cause actual realized-equity drawdown. Computed metrics therefore have negative net return, positive maximum drawdown in USD and fraction, and a **numeric negative recovery factor** (net loss divided by positive drawdown). For the single-close fixture, recovery factor is exactly -1; it is neither null nor positive.

Six source-defined tests validate the producer-computed exact checkpoint metrics through the independent evidence writer/audit and reject digest-verified false near-equal net return, USD drawdown, fraction drawdown, null recovery, and positive recovery. Distinguish source trade gross PnL from realized net outcome; no implied actual financing economics. Production code unchanged.

**7,382 cumulative proposed test methods** (+6). Each PR needs its own exact-head Phase3 and full historical/general suite. Pending validation earns no pass credit and historical failures remain failed. Phase8A #779/#820/#821 and eight independent security proof packages BLOCKED. No protected annual research, installed workflows/refs/runners, merging, strategy promotion, brokerage orders or real capital.
