# DEC-1764 — Phase 7 published-cost sensitivity replay, not Strategy V1

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of PR #2010, commit `bcb196d3a18b87f21bfdce15a39980ed14d4268f`. The governing Phase8A research method remains **DEC-469/DEC-268 annual-first discovery**, and blocked 2023/run385 prevents actual cross-year economics and StrategyV1 synthesis.

This is **source-only historical arithmetic**, not a new experiment or discovery search. `python scripts/dec1764_phase7_historical_cost_stress.py` reads exactly the publicly documented **Phase7 Stage2** cost table, verifies the frozen document by its Git blob SHA1, retains its authoritative run identity and reproduces the original three slippage scenarios:

| Adverse slippage | Net retrospective return | Net retrospective PnL | Profit factor | Trades |
| --- | ---: | ---: | ---: | ---: |
| 0.2 pips | +0.757266% | +$757.27 | 1.062731 | 199 |
| 0.5 pips | +0.262176% | +$262.18 | 1.021310 | 199 |
| 1.0 pips | **-0.562118%** | **-$562.12** | **0.955760** | 199 |

Pure piecewise interpolation of the reported 0.5- and 1.0-pip aggregate points gives an **illustrative return-zero crossing ≈0.659031 pips**; this is not an observed backtest at that price, a validated executable quote/slippage limit, nor a forward breakeven guarantee. The two *observed* historical intervals both have negative slopes near -1.65 percentage points per additional pip. Original DEC-033 used 1.0 pip as a *diagnostic*, not a promotion gate. The original Phase7 Stage2 authorization was for a historical USDJPY 15m `session_breakout` baseline; it is **not** prospective Strategy V1 and must never be marketed as live expected profit.

The reporter prints only nonauthorizing retrospective JSON and exits **3**, not 0. Unverified inputs exit **2** with no stdout. 10 test methods (**6427 proposed cumulative**). It reads no protected annual catalogue data, does not change approved cost parameters or experiment history, does not touch GitHub workflow/runner/ref/rulesets, and never dispatches one-shot annual run385, places a broker order or trades. #779/#820/#821 remain BLOCKED, StrategyV1 prospective economics still unknown. Own Phase3/full historical-general CI and independent qualified review required.
