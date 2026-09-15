# Phase 7 Walk-Forward Acceptance Evidence

**Experiment:** `EXP-20260915-008`  
**Protocol:** DEC-033  
**Stage 1 outcome:** DEC-034  
**Authoritative Stage 2 workflow:** `phase7-walk-forward` run `35015277625`  
**Stage 2 code SHA:** `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`  
**Candidate:** USDJPY 15m `session_breakout`, `buffer_pips=5`, `target_range_multiple=1.5`  
**Final Stage 2 status:** `PHASE7_PROMOTE_TO_SHADOW_DESIGN`

## Authorization and immutable identities

Stage 2 was deliberately dispatched only for the sole audited Stage 1 survivor. Before any required 2025/2026 source I/O, the workflow downloaded and verified Stage 1 artifact `10414407590`, ZIP SHA-256 `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb`, and confirmed `STAGE1_PASS` for `session_breakout`. The Stage 1 inner `manifest.json` SHA-256 remained `a8ca80186708aedbfd52fd688c843c4dc06e2ce8a81f543bd7224abc0a955faa`.

The workflow then re-verified the accepted Phase 2 USDJPY artifact `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`, processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`, canonical schema `fmp-canonical-1m-v1`, and Phase 6 checkpoint `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`.

No parameter, strategy, pair, timeframe, risk rule, cost rule, window boundary, warm-up rule, or promotion threshold was changed after Stage 1 or Stage 2 observation.

## Determinism and evidence integrity

Run `35015277625` executed the complete Stage 2 evaluation twice. The workflow compared the two complete file-name sets and byte-compared every file before upload. It then independently reconstructed every frozen window and warm-up boundary, checked each exact monthly partition key, recomputed all three cost aggregates and the Stage 2 gate from the window rows, and verified the constituent artifact SHA-256 and byte sizes.

The uploaded authoritative evidence is artifact `10414817824`, named `phase7-stage2-session_breakout-a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`. Its GitHub-reported and independently recomputed ZIP SHA-256 is `2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4`.

The ZIP contains exactly three files:

- `manifest.json`
- `result.json` — 2,085 bytes, SHA-256 `ce7ef3f732bf2da7cd9c0df5e5d695dcdadd63e309c9428a6f572801fcb197b7`
- `windows.json` — 19,137 bytes, SHA-256 `66a1d35b12b68a0762dd98cd6838a2befcaf57ef9ae43bce181241fe4d23a4f0`

## Exact forward windows

Every window starts independently at $100,000, records `refit_status = NOT_APPLICABLE_FIXED_RULE`, and uses only the immediately preceding seven calendar days as non-scored warm-up context. The 0.2-pip baseline window results are:

| Window | Scored range | Net return | Net PnL | Trades | Expectancy/trade | Profit factor | Max DD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2025-Q1 | 2025-01-01 to 2025-04-01 exclusive | -0.520185% | -$520.18 | 29 | -$17.9374 | 0.779667 | 0.886125% |
| 2025-Q2 | 2025-04-01 to 2025-07-01 exclusive | +0.674172% | +$674.17 | 35 | +$19.2621 | 1.442160 | 0.527903% |
| 2025-Q3 | 2025-07-01 to 2025-10-01 exclusive | +0.038910% | +$38.91 | 31 | +$1.2551 | 1.022785 | 0.930595% |
| 2025-Q4 | 2025-10-01 to 2026-01-01 exclusive | +0.674389% | +$674.39 | 29 | +$23.2548 | 1.468793 | 0.575592% |
| 2026-Q1 | 2026-01-01 to 2026-04-01 exclusive | +0.225691% | +$225.69 | 31 | +$7.2804 | 1.137904 | 0.825067% |
| 2026-Q2 | 2026-04-01 to 2026-07-01 exclusive | +0.310265% | +$310.27 | 28 | +$11.0809 | 1.168669 | 0.567874% |
| 2026-partial-Q3 | 2026-07-01 to 2026-08-21 exclusive | -0.645978% | -$645.98 | 16 | -$40.3736 | 0.586896 | 1.140640% |

Five of seven baseline windows have positive net PnL. The largest positive window contributes 35.061843% of total positive-window PnL, below the frozen 50% concentration ceiling.

## Aggregate cost results

| Adverse slippage | Net return | Net PnL | Trades | Expectancy/trade | Profit factor | Max independent-window DD | Positive windows | Max positive-window share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.2 pips | +0.757266% | +$757.27 | 199 | +$3.8054 | 1.062731 | 1.140640% | 5 of 7 | 35.061843% |
| 0.5 pips | +0.262176% | +$262.18 | 199 | +$1.3175 | 1.021310 | 1.170046% | 4 of 7 | 39.223270% |
| 1.0 pips | -0.562118% | -$562.12 | 199 | -$2.8247 | 0.955760 | 1.219045% | 4 of 7 | 49.394868% |

The 1.0-pip diagnostic is negative and is preserved as material cost-sensitivity evidence. DEC-033 explicitly makes 1.0 pips diagnostic only; it is not a promotion gate and was not used to alter the predeclared rule.

## Gate recomputation

All frozen mandatory Stage 2 criteria are true:

- 0.2-pip aggregate net return > 0: PASS.
- 0.2-pip aggregate expectancy > 0: PASS.
- 0.2-pip aggregate profit factor > 1: PASS.
- 0.2-pip completed trades >= 100: PASS with 199.
- 0.2-pip maximum independent-window drawdown <= 5%: PASS at 1.140640%.
- 0.2-pip positive windows >= 4 of 7: PASS with 5 of 7.
- 0.2-pip maximum positive-window contribution <= 50%: PASS at 35.061843%.
- 0.5-pip aggregate net return > 0: PASS.
- 0.5-pip aggregate expectancy > 0: PASS.
- 0.5-pip aggregate profit factor > 1: PASS.
- 0.5-pip maximum independent-window drawdown <= 5%: PASS at 1.170046%.

The artifact's recorded gate and an independent recomputation from all 21 window rows agree exactly. The authoritative Stage 2 status is therefore `PHASE7_PROMOTE_TO_SHADOW_DESIGN`.

## Phase 7 outcome

`session_breakout` passes the frozen Stage 1 and Stage 2 protocol and is eligible for Phase 8 shadow design only. `volatility_breakout` remains rejected at Stage 1 and was not evaluated in Stage 2. No failed result was discarded and no rescue search or retuning is authorized under `EXP-20260915-008`.

Phase 7 is formally PASS once this closure evidence/state change is merged and freshly verified on `main`. Phase 8 remains UNSTARTED. This result does not authorize broker integration, demo trading, live trading, order placement, or real-money trading; DEC-008 remains unchanged.
