# Phase 7 Stage 1 Final-Gate Evidence

**Experiment:** `EXP-20260915-008`  
**Protocol:** `DEC-033`  
**Outcome decision:** `DEC-034`  
**Status:** AUDITED — one Stage 1 survivor  
**Date:** 2026-09-15

## Authoritative execution

The first authorized opening of the Phase 7 final-test period was manual `phase7-final-gate` workflow run `35013047267`. It executed on the exact verified merged-main implementation SHA `e33270de1f89757d1bf2a0d12ef40b2dc36bc110` and completed `SUCCESS`.

Before dispatch, merged-main verification on the same SHA was green: tests run `35010868101` completed `SUCCESS` with 620/620 tests, workflow YAML validation, and compile all passing, and unchanged Phase 3 acceptance run `35010868091` completed `SUCCESS`.

Both Stage 1 candidate jobs completed successfully and each performed two independent executions followed by a complete byte-for-byte evidence comparison before uploading the first copy. Workflow success is treated only as execution integrity; the candidate promotion decision is recomputed from the evidence below.

## Frozen identities and scope

- Phase 6 checkpoint: `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`.
- Accepted Phase 2 USDJPY artifact: `10327600628`.
- Accepted Phase 2 USDJPY ZIP SHA-256: `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`.
- Accepted USDJPY processed-manifest SHA-256: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Canonical schema: `fmp-canonical-1m-v1`.
- Scored range: `[2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z)`.
- Warm-up context: `[2023-12-25T00:00:00Z, 2024-01-01T00:00:00Z)` only; no warm-up candidate, trade, PnL, or metric is scored.
- Starting equity: exactly `$100,000` per Stage 1 candidate evaluation.
- Slippage: exactly 0.2, 0.5, and 1.0 pips adverse per fill; 0.2 and 0.5 are gating, 1.0 is diagnostic only.
- Commission / financing: zero / zero; historical BID/ASK spread remains inherent in Phase 3 execution.
- Risk: 0.25% requested, 0.50% hard per-trade maximum, 1.00% simultaneous maximum, 1.50% UTC day-start realized-loss halt.

No 2025 or 2026 scored partition was opened by Stage 1.

## Artifact audit

| Candidate | Artifact | ZIP SHA-256 | `manifest.json` | `result.json` | `stage1.json` | Outcome |
| --- | ---: | --- | --- | --- | --- | --- |
| `session_breakout` | `10414407590` | `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb` | `a8ca80186708aedbfd52fd688c843c4dc06e2ce8a81f543bd7224abc0a955faa` | `31a42ea11b333d73df5d63ba339154dddd67f188c7483541fce048344773e66a` | `8d67fa77cac0c132fa6d317569ee9ec58970e25e3895df960fe60c5b7b671dc2` | `STAGE1_PASS` |
| `volatility_breakout` | `10414905151` | `5ee8b6b96382741f454d2b72a6ae6de04e85c9eca04c17ac846c0d594fd27d24` | `a2526d90312e85a2ab2d57ab86d5502e8644a16735aa0a677cda5626976dda35` | `51c1f929dcf7423d214821024fb96ab91c9630c8a99df6f10cc51b48dde38a39` | `c38bdc03cfec4af6cb49ba56b2586e64bdd62c23962d6f518c8e69d2183df299` | `STAGE1_REJECT` |

The GitHub-recorded artifact digests were independently recomputed from the downloaded ZIP bytes and matched exactly. Every constituent file SHA-256 and size matched the inner manifest. Code commit, experiment ID, candidate identity, Phase 2 identity, Phase 6 checkpoint identity, schema, risk/cost settings, ranges, and opened-partition accounting matched the frozen protocol.

### Opened partition accounting

`session_breakout` opened only `15m:2023-12` for bounded warm-up plus `15m:2024-01` through `15m:2024-12` for the scored period. `volatility_breakout` opened only `1h:2023-12` plus `1h:2024-01` through `1h:2024-12`. No required 2025/2026 partition appears in either Stage 1 artifact.

## Candidate results

### `session_breakout` — STAGE1_PASS

Frozen identity: USDJPY 15m, `buffer_pips=5`, `target_range_multiple=1.5`.

| Slippage | Trades | Net PnL | Net return | Expectancy/trade | Profit factor | Max drawdown |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.2 pip | 122 | $1,383.2873 | +1.383287% | $11.3384 | 1.166401 | 1.181400% |
| 0.5 pip | 122 | $1,102.5090 | +1.102509% | $9.0370 | 1.130773 | 1.305490% |
| 1.0 pip | 122 | $636.2338 | +0.636234% | $5.2150 | 1.073756 | 1.527260% |

At both mandatory gating costs, net return and expectancy are strictly positive, profit factor is above 1.0, max drawdown is below 5%, and the 0.2-pip baseline has 122 completed trades, above the minimum 40. Independent recomputation therefore agrees with the artifact: `session_breakout` passes Stage 1. The positive 1.0-pip diagnostic is retained as evidence but is not a promotion gate.

### `volatility_breakout` — STAGE1_REJECT

Frozen identity: USDJPY 1h, `range_multiplier=2.0`, `target_r=1.0`.

| Slippage | Trades | Net PnL | Net return | Expectancy/trade | Profit factor | Max drawdown |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.2 pip | 103 | -$2,603.7681 | -2.603768% | -$25.2793 | 0.720003 | 3.102796% |
| 0.5 pip | 103 | -$3,051.5582 | -3.051558% | -$29.6268 | 0.680125 | 3.484070% |
| 1.0 pip | 103 | -$3,793.3534 | -3.793353% | -$36.8287 | 0.618485 | 4.126035% |

The candidate clears the baseline trade-count and drawdown limits but fails the mandatory profitability, expectancy, and profit-factor conditions at both 0.2 and 0.5 pips. It is rejected with no rescue search or retuning.

## Stage 1 decision

- `session_breakout — STAGE1_PASS`
- `volatility_breakout — STAGE1_REJECT`

Only the exact `session_breakout` evidence package from artifact `10414407590`, ZIP SHA-256 `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb`, on code SHA `e33270de1f89757d1bf2a0d12ef40b2dc36bc110` may authorize Stage 2 for `EXP-20260915-008`.

Phase 7 remains ACTIVE until that sole survivor receives the frozen seven-window Stage 2 evaluation and audited outcome. Required 2025/2026 data remains locked until the Stage 2 workflow verifies this exact Stage 1 PASS package before source I/O. Phase 8 remains UNSTARTED; broker, demo, live, and real-money trading remain locked.
