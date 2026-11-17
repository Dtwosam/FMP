# Phase 7 Stage 2 trade-recovery decision

**Date:** 2026-11-17
**Status:** DECISION PACKET — NOT AN AUTHORIZATION, REPLAY, OR FRESH TEST
**Governing method:** discovery-first annual pattern catalogue (DEC-268 / DEC-469)
**Authorized annual segments:** none. Run 385 / attempt 1 stays unconsumed.
**Pattern type / tool:** none. This packet names a possible later reproduction of one frozen rule. It is not the annual catalogue.

DEC-629 and DEC-630 remain proposed and unadopted. Issues #779, #820, and #821 remain unresolved. No workflow, tag, runner, ruleset, broker, demo, live, or real-money path is opened here.

The bounded search recorded with DEC-634 did not find the 199 individual Stage 2 trades. This packet says what a later owner decision would have to authorize before anyone tries to reproduce them. It does not run that reproduction.

## What is already known

The original execution is `phase7-walk-forward` run `35015277625`, attempt 1, success, head `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`.

The original artifact is `10414817824`, name `phase7-stage2-session_breakout-a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`, ZIP SHA-256 `2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4`. Its documented members are `manifest.json`, `result.json` SHA-256 `ce7ef3f732bf2da7cd9c0df5e5d695dcdadd63e309c9428a6f572801fcb197b7`, and `windows.json` SHA-256 `66a1d35b12b68a0762dd98cd6838a2befcaf57ef9ae43bce181241fe4d23a4f0`. Those files are window aggregates. `write_stage2_evidence` does not write `run.trades`.

Phase 4 artifacts `10349341980` (USDJPY 15m development) and `10348339399` (USDJPY 15m validation) are a different experiment, `EXP-20260914-001`, on 2015–2023. They are not the 199 Stage 2 trades. This packet does not download or open them.

## Frozen reproduction identity

A later replay is the original run only if every item below is unchanged.

| Item | Required value |
| --- | --- |
| Experiment | `EXP-20260915-008` |
| Code | `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d` |
| Candidate | USDJPY 15m `session_breakout` |
| Parameters | `buffer_pips=5`, `target_range_multiple=1.5` |
| Phase 6 checkpoint | tag `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953` |
| Phase 2 USDJPY artifact | `10327600628` |
| Phase 2 ZIP SHA-256 | `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72` |
| Processed manifest SHA-256 | `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d` |
| Schema | `fmp-canonical-1m-v1` |
| Starting equity | `$100,000` at the start of every window |
| Requested risk | `0.0025`, hard maximum `0.005`, simultaneous maximum `0.01`, daily realized-loss halt `0.015` |
| Costs | `ZeroCommission`, `ZeroFinancing`, historical bid/ask spread left in the fill |
| Refit | `NOT_APPLICABLE_FIXED_RULE` |
| Warm-up | the seven calendar days before each scored window, not scored |

## Seven scored windows

Each window is half-open and starts its own `$100,000` account.

| Window | Scored start | Scored end, exclusive |
| --- | --- | --- |
| `2025-Q1` | 2025-01-01 | 2025-04-01 |
| `2025-Q2` | 2025-04-01 | 2025-07-01 |
| `2025-Q3` | 2025-07-01 | 2025-10-01 |
| `2025-Q4` | 2025-10-01 | 2026-01-01 |
| `2026-Q1` | 2026-01-01 | 2026-04-01 |
| `2026-Q2` | 2026-04-01 | 2026-07-01 |
| `2026-partial-Q3` | 2026-07-01 | 2026-08-21 |

## Three slippage scenarios

Adverse slippage per fill, in pips: `0.2`, `0.5`, and `1.0`. The 0.2 and 0.5 settings were the original promotion gate. The 1.0 setting was diagnostic and stays in the record. A recovery run evaluates all three. It does not drop the negative 1.0 result or pick a new slippage after seeing the trades.

## Reconciliation targets

The exact file targets are the original hashes above. A recovery run may be treated as a reproduction of run `35015277625` only when regenerated `result.json` and `windows.json` match those SHA-256 values byte for byte. A trade file that arrives with different aggregate bytes is a new execution.

The published numeric targets in `docs/phase7-walk-forward-evidence.md` are the human check. At 0.2 pip the seven windows are:

| Window | Net PnL | Trades |
| --- | ---: | ---: |
| 2025-Q1 | -$520.18 | 29 |
| 2025-Q2 | +$674.17 | 35 |
| 2025-Q3 | +$38.91 | 31 |
| 2025-Q4 | +$674.39 | 29 |
| 2026-Q1 | +$225.69 | 31 |
| 2026-Q2 | +$310.27 | 28 |
| 2026-partial-Q3 | -$645.98 | 16 |

Those seven counts sum to 199. The published all-window totals are:

| Adverse slippage | Net return | Net PnL | Trades | Expectancy per trade |
| --- | ---: | ---: | ---: | ---: |
| 0.2 pip | +0.757266% | +$757.27 | 199 | +$3.8054 |
| 0.5 pip | +0.262176% | +$262.18 | 199 | +$1.3175 |
| 1.0 pip | -0.562118% | -$562.12 | 199 | -$2.8247 |

Per-window rows for 0.5 and 1.0 pip are inside the original `windows.json`. This packet does not reopen that file. The hash above is their identity.

The window-start conversions of those aggregates remain +0.01522R, +0.00527R, and −0.01130R. They are not the trade-level series a recovery file would have to match one row at a time.

## How trades would be kept

`evaluate_phase7_window` calls `run_backtest`, which returns `TradeRecord` rows, and then drops them when it builds `WindowFinancialResult`. The installed workflow uploads only the directory from `write_stage2_evidence`.

A later change, if authorized, would:

1. Check out `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`.
2. Add a side writer that serializes the existing `run.trades` and `run.rejections` for each window and slippage scenario.
3. Leave fill, sizing, slippage, commission, financing, window bounds, and the three aggregate files unchanged.
4. Write the new rows to a new directory. Do not replace artifact `10414817824`, its name, or `docs/phase7-walk-forward-evidence.md`.
5. Regenerate `result.json` and `windows.json` from that same run and compare them with the SHA-256 values above before the new trade file is called a reproduction.
6. If the hashes differ, keep the difference visible and do not relabel the new rows as the original ledger.

Redispatching `.github/workflows/phase7-walk-forward.yml` does not do this. That workflow still discards the trade rows and would be a new historical execution.

## Review and access required first

This packet is not that authorization. A separate owner decision would need to allow all of the following before any command runs:

- Read Phase 2 artifact `10327600628` after its ZIP SHA-256 matches.
- Execute the frozen evaluator on that processed history.
- Write a new trade directory that is not the original artifact.
- Review the code diff so the only behavior change is retention of rows the engine already returns.

That decision would still not allow a download of the Phase 4 ZIPs, a dispatch of the installed Stage 2 workflow, an edit to a protected workflow or ruleset, a broker connection, or a demo or live order.

The recovered rows, if the hashes match, would be submitted to `validate_trade_submission` with `data_reuse=already_scored`. `original_phase7_trade_ledger_verified` stays false until a reviewer compares the new file with the hash-matched run. The reported R remains requested-risk-normalized at recorded exit equity.

## Why this is not fresh evidence

Stage 1 already scored 2024. Stage 2 already scored 2025-01-01 through 2026-08-21 exclusive and published the result. A replay reads that same scored sample again. It can restore trades the writer dropped. It cannot make 2024, 2025, or the published 2026 window into untouched validation. Prospective evidence would have to be later than 2026-08-20 under a frozen rule, and this packet does not create that sample.
