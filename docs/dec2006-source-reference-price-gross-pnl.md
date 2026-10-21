# DEC-2006 — Source-engine reference-price gross PnL reconciliation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2254 at `a2b98cc41415779ff0e432295feaa688fd4323bd`.

The source Phase3 engine records gross trade PnL using `pnl_usd(symbol, direction, units, entry_reference_price, exit_reference_price)`. EURUSD/GBPUSD are direct USD-quote calculations; USDJPY uses exit-price conversion to USD via Decimal arithmetic. Previous optional artifact auditing checked gross-minus-costs == net and net-realized-equity consistency but could not independently reconstruct the stored gross economics from the claimed reference prices. A self-rehashed artifact could therefore claim arbitrary gross PnL and economic totals.

When `run_identity.backtest_engine_version` exactly matches the installed `BACKTEST_ENGINE_VERSION`, calculate expected gross using the engine's *source-defined* `pnl_usd` routine and compare against stored gross with bounded floating tolerance, after preserving the older net-vs-cost semantic rejection. Do not force engine-specific PnL on generic synthetic run reports or claim authenticated external FX prices.

The previously introduced source-engine checkpoint fixture contained synthetic gross and reference prices that were mutually inconsistent; adjust its exit reference to 1.10125 so two 10,000-unit EURUSD LONG trades correspond to gross USD 12.5 each, preserving their original net PnL and checkpoints. Three synthetic test methods cover a source-compatible run, a forged/rehashed reference-price adjustment leaving gross untouched, and a source-compatible USDJPY trade requiring quote conversion.

**7,118 cumulative proposed source-defined test methods** (+3), not exact-head full CI verified. Previous #2248–#2252 full regressions remain FAIL and #2253–#2254 own CI must be independently checked. Phase8A #779/#820/#821 and eight independent external proofs still BLOCKED; no protected annual research, installed workflows/refs/runners, broker orders, merges, strategy promotion or capital.
