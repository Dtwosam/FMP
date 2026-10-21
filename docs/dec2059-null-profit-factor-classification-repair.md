# DEC-2059 — Null-profit-factor error classification assertion repair

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2307 `5e459b1687221d630901cfa272627b249da16862`.

Full historical/general regression for #2300 exact source commit `e83f014633c62dbfe4ca638f894e3ba21df86c2f`, run [39633489195](https://github.com/Dtwosam/FMP/actions/runs/39633489195), finished **FAILED** with one assertion mismatch among 12,170 executed tests (714 skipped). The source audit correctly rejected a manifest-rehashed null `profit_factor` on an actual loss-only ledger. It raised `artifact report metric profit_factor must be finite numeric` because a positive gross-loss denominator makes the expected metric numeric zero; the added DEC-2051 assertion instead expected `metric profit_factor conflicts with trade ledger`.

This repair updates only that test's expected error class/message to match the established source contract. It does **not** relax evidence validation, reclassify the historical failure, change any production engine/reporting source, or add test methods. Valid loss-only profit factor remains numeric zero; valid all-win and no-trade profit factors remain null under their separate witnesses. Failure logs remain permanently failed.

**7,304 cumulative proposed test methods** (no change). Require own exact-head Phase3 and full historical/general run before any repair-green claim. All prior #2300–#2307 regression outcomes remain their recorded historical state. Phase8A #779/#820/#821 and eight independent external security proof packages BLOCKED; no protected history, installed workflows/refs/runners, merges, trading promotion, broker orders or real capital.
