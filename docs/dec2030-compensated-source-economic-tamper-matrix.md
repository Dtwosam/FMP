# DEC-2030 — Compensated multi-field source economic tamper witnesses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2278 at `3818492dd00949444ad00e1d4d1b2cf479969daa`.

Separate forged trade fields can be rehashed while still preserving `net_pnl = gross - slippage - commission - financing`. In an integrated installed-source model report with declared pips, fixed commission and zero financing, a paired gross/slippage increase, a paired slippage increase/commission decrease, or a paired commission increase/financing decrease can keep net PnL and realized equity unaltered. A general arithmetic audit alone therefore cannot establish whether the declared source price/cost model was followed.

This test/docs-only draft adds four synthetic source-defined methods: rehashed simultaneous gross and slippage drift must fail exact source reference gross, rehashed slippage/commission offset must fail source slipped-PnL cost, rehashed commission/financing offset must fail fixed built-in commission, and generic non-source envelopes retain permitted internal arithmetic flexibility. Each test verifies the final self-rehashed manifest before semantic auditing, with no change to production code.

**7,204 cumulative proposed source-defined test methods** (+4). Own exact-head Phase3 and full historical/general CI mandatory; #2266–#2269 historical full-suite failures remain failures, and newer full validations are separately pending. These checks do not prove authentic FX quotes, actual broker costs, or profitable/real execution.

Phase8A #779/#820/#821 and eight independent external security proof packages remain blocked. No protected annual research, installed workflows/refs/runners, strategies promoted, broker orders, mergers or real capital.
