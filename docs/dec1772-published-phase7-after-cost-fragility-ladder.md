# DEC-1772 — Published Phase7 after-cost fragility ladder (not a new strategy)

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent source-only child of PR #2018 at `e61f8427e655e972148fd2eb34e597090c815337`.

The frozen public Phase7 Stage2 report on USDJPY 15m `session_breakout` presents three aggregate diagnostics at 0.2, 0.5 and 1.0 pips. This addition computes only **adjacent changes between published aggregates**. It checks the reported maximum independent-window drawdowns and positive-window shares as well as the existing net return/PnL, expectancy, trade counts, and profit factors.

| Published adverse slippage | Historical return | Historical profit factor | Positive windows | Max window DD |
| --- | ---: | ---: | ---: | ---: |
| 0.2 pips | +0.757266% | 1.062731 | 5 of 7 | 1.140640% |
| 0.5 pips | +0.262176% | 1.021310 | 4 of 7 | 1.170046% |
| 1.0 pips | **−0.562118%** | **0.955760** | 4 of 7 | 1.219045% |

Between 0.2 and 0.5 pips, aggregate historical return falls **0.495090 percentage points**, PnL falls **$495.09** and per-trade expectancy falls **$2.4879**. Between 0.5 and 1.0 pips it falls another **0.824294 points**, **$824.30** and **$4.1422** per trade. Under the observed aggregate data, risk concentration and drawdowns increase with these higher reported costs, and the 1.0-pip aggregate has negative return and profit factor below one. This does not establish a continuous slippage response, window-specific 0.5/1.0-pip profits, an executable threshold or a statistically independent result.

Adds **5** new tests (**6465 proposed source-defined cumulative**) to the existing immutable-source retrospective replay. The source file Git blob check, no-follow bounded path reads, no-authority exit3 and negative losing-window evidence remain unchanged. **This is NOT Phase8A StrategyV1 forward evidence or trading permission**. The protected 2023/run385 annual research, #779/#820/#821 admin/OS proof, strategy selection, broker/demo/live orders, and real-money trading stay blocked. Separate exact-head Phase3/full regression CI and qualified review required; ancestor CI failure repair #2016 is not counted as passed until its full suite completes.
