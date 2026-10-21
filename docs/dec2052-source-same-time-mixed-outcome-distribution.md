# DEC-2052 — Same-timestamp mixed-outcome source distribution witnesses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2300 at `e83f014633c62dbfe4ca638f894e3ba21df86c2f`.

Source-engine equity checkpoints preserve the order in which trades actually realize, while canonical artifact trade rows sort equal close timestamps by trade ID. The source witness realizes a profitable Z-WIN before a losing A-LOSS at the same UTC instant; the artifact publishes A-LOSS before Z-WIN. Both outcomes must still enter the denominator. Win rate is 0.5, the longest streak of either sign is one, and profit factor is finite and positive because both profit and loss exist.

Four source-defined test methods verify the valid reverse-publication report, reject a forged/rehashed 100% win rate, reject a fabricated two-win streak across a loss, and reject a forged null profit factor when a real losing denominator exists. Each manipulated canonical metrics file passes manifest digest verification before the independent read-only semantic audit rejects its false interpretation. No source engine/report writer changes and no authenticated market/broker assertion.

**7,279 cumulative proposed methods** (+4). Own exact-head Phase3 and full historical/general suite required. Earlier failed results remain failed; pending suites do not count as green. Phase8A blockers #779/#820/#821 and eight independent security proof packages remain unresolved. No protected history, workflow/ref/runner changes, merges, strategy promotion, orders, brokers, or real money.
