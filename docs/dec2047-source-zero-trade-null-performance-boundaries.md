# DEC-2047 — Zero-trade null-performance source witnesses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2295 at `fd76a9d17e8ccb596c5d868a83b1592358097a5c`, whose exact-head Phase3 and historical/general suites passed.

The installed metric writer returns `None` rather than zero for an undefined no-trade win rate, mean win, mean loss, expectancy and profit factor. When there are no trades, the zero initial checkpoint and zero streak counts remain meaningful. The optional evidence auditor already enforces these semantic distinctions; this source-only test/docs child protects them against canonically serialized, fully rehashed contradictory metrics.

Four additional source-defined methods: valid source-version zero-trade report with null performance ratios and zero streaks; canonical manifest-rehashed win rate 0 instead of null; rehashed profit factor 0 instead of null; and rehashed winning streak 1 despite no trades. Each tampering witness first passes manifest digest verification and then must fail the semantic audit.

**7,260 cumulative proposed source-defined test methods** (+4). No installed engine or production reporting code modified. Own exact-head Phase3 and full historical/general suites mandatory before counting success; historical failures remain failures. The tests prove internal artifact consistency only, not external market data, trade execution, or profitability.

Phase8A #779/#820/#821 plus eight independent security proof packages remain blocked. No protected annual research, installed workflows/refs/runners, strategy promotion, mergers, brokerage/orders or real capital.
