# DEC-2007 — Reconcile source modeled slippage with trade execution prices

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2255 at `d91eb457874c007f7fbcc0e2690989fd2380bc2d`.

The Phase3 source engine records `slippage_cost_usd=max(0,gross_reference_pnl - slipped_execution_pnl)`, where both PnL quantities are computed by the source's Decimal-based `pnl_usd` routine. The previous audit already checked nonnegative slippage, adverse-only execution side and gross-minus-costs net economics, but a self-rehashed trade could still claim different execution prices while retaining the old slippage cost and net PnL. Such a row is not consistent with source execution modeling.

For artifacts explicitly declaring the installed BACKTEST_ENGINE_VERSION, independently compute slipped fill PnL from the published entry_price and exit_price and the corresponding reference gross, then compare the stored modeled slippage cost with bounded tolerance. Preserve generic synthetic evidence without this version. This checks only internal source arithmetic, not actual broker fill authenticity.

DEC-2006's source-engine synthetic fixture previously carried an impossible combination of reference gross 12.5, slipped PnL 10.0 and claimed slippage 1.5. Adjust exit execution from 1.1010 to 1.1011, making slipped PnL 11.0 and slippage 1.5 while preserving existing net PnL and equity checkpoints. Three new source-defined tests cover compatible economics and rehashed favorable adjustments to entry or exit execution still adverse to their reference but inconsistent with stored cost.

**7,121 cumulative proposed source-defined methods** (+3). Own exact-head Phase3/full historical-general suite mandatory. Earlier historical failures are preserved, #2253–#2255 full suites must be checked separately.

Phase8A #779/#820/#821 and eight external security proofs still blocked. No protected annual research, broker/demo/live orders, capital deployment, strategy promotion, installed runner/ref/workflow changes or merges.
