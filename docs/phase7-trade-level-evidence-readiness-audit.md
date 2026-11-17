# Phase 7 trade-level evidence: source-only readiness audit and owner decision brief

**Date:** 2026-11-17  
**Status:** READ-ONLY CODE/DOCUMENT AUDIT — NOT AN AUTHORIZATION, ACCEPTANCE GATE, OR RESEARCH RESULT  
**Source snapshot audited:** `156208a02854883fcd3543a1e1b661bf99553aba` (draft PR #2331)  
**Governing method:** discovery-first annual pattern catalogue (DEC-268 / DEC-469)  
**Currently authorized annual segments:** none; protected 2023 run 385/attempt 1 is blocked  
**Current task:** Phase 8A research-readiness audit, not annual catalogue execution, cross-year synthesis, promotion, or Phase 8B  
**Protected boundary:** no protected historical artifact opened, no workflow dispatched, and no prior protected annual run retried

## Executive finding

The existing backtester **creates individual `TradeRecord` objects** and the Phase 7 evaluator has them in memory while running, but **does not preserve them in its Phase 7 summary outputs**. The authoritative Stage 2 evidence described by `docs/phase7-walk-forward-evidence.md` is a ZIP containing only `manifest.json`, `result.json`, and `windows.json`. These are seven per-window aggregate summaries at each of the three frozen slippage scenarios, not a trade-level R series.

Thus, **trade-level modeling is technically supported in the engine, but the already-recorded Phase 7 evidence does not supply the per-trade inputs required for defensible 30-day terminal/touch/drawdown probabilities**. The reporting gap is identifiable from source without running a strategy. Whether any separately retained, accessible authorized individual-trade record exists *outside these documented artifacts* is **not established**. This audit did not search private/protected artifact storage.

## Exact source trace

| Source | Inspectable behavior | What it does **not** establish |
| --- | --- | --- |
| `src/fmp/contracts.py`: `TradeRecord`, `BacktestRun` | Stores trade ID, decision ID, pair/direction/units, entry/exit timestamps and prices, stop/target, gross/net PnL, slippage/commission/financing, and risk equity before/after; `BacktestRun.trades` is a tuple | That an authoritative Phase 7 trade list was retained |
| `src/fmp/backtest/engine.py`: `run_backtest` | Returns sorted individual trades in `BacktestRun` | That a public evidence ZIP contains these trades |
| `src/fmp/research/reporting.py`: `compute_research_metrics` | Computes per-trade net R internally as `trade.net_pnl_usd / (trade.risk_equity_before_usd * requested_risk_fraction)` and produces aggregate risk statistics | That the complete ordered R series was serialized |
| `src/fmp/walkforward/evaluation.py`: `evaluate_window` | Calls `run_backtest` and `compute_research_metrics`, returns `WindowFinancialResult` with counts, PnL, metrics, and run identity | `WindowFinancialResult` does not expose `run.trades` |
| `src/fmp/walkforward/artifacts.py`: `_result_row` and `write_stage2_evidence` | Writes per-window aggregate rows to `windows.json` and gate to `result.json`; manifest lists exactly those two content files | No `trades.jsonl` output is produced on this Phase 7 path |
| `.github/workflows/phase7-walk-forward.yml` | Previously uploaded the frozen Phase 7 Stage 2 evidence directory | Does not authorize a new dispatch, modified evidence, or a replay |
| `src/fmp/reporting/backtest.py`: `write_backtest_artifacts` | A **different, general backtest** writer supports `trades.jsonl` | It is not invoked by the frozen Stage 2 evidence writer |
| `docs/phase7-walk-forward-evidence.md` | Describes authoritative run `35015277625`, code `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`, Stage 2 artifact `10414817824`, and a three-file ZIP | Documents aggregate performance, not an ordered individual-trade ledger |

This trace is a source inspection only; no functions above were executed and no protected market data was loaded.

## What existing Phase 7 evidence actually says

The frozen USDJPY 15m session breakout uses `buffer_pips=5` and `target_range_multiple=1.5` under `EXP-20260915-008`. Stage 1 used 2024 for selection. Stage 2 scored seven independent equity-reset windows from 2025-01-01 through 2026-08-21 exclusive, with 199 trades and 0.25% requested risk per trade. All windows start separately at $100,000.

| Adverse slippage per fill | Stage 2 net return (sum of independent-window results) | Per-trade expectancy (USD) | Mean R using **window-start** $250 approximation |
| --- | ---: | ---: | ---: |
| 0.2 pip | +0.757266% | +3.8054 | +0.0152216R |
| 0.5 pip | +0.262176% | +1.3175 | +0.0052700R |
| 1.0 pip | -0.562118% | -2.8247 | -0.0112988R |

The published `PHASE7_PROMOTE_TO_SHADOW_DESIGN` was a **historical protocol gate** evaluated using 0.2- and 0.5-pip assumptions; 1.0 pip was diagnostic. It is not a demonstration of robust retail after-cost expectancy. The mean R column above is an aggregate conversion using a *fixed starting-equity risk unit*, **not the trade-level R values** computed by the reporting function. It must not be treated as a time-ordered R series.

The Stage 2 backtest configured `ZeroCommission()` and `ZeroFinancing()`, and included historical bid/ask fills plus specified per-fill adverse slippage. Repricing at independently sourced broker costs would be a newly specified analysis, not an already-proved historical result; never add spread twice.

The scored 2024 selection and 2025–2026 forward windows have already been examined. They cannot now be relabeled untouched holdout data.

## Evidence contract for a **future, separately authorized** individual-trade record

This is an audit checklist, **not a request to produce, read, dispatch, or re-run that record now**.

1. **Identity:** exact frozen candidate/config, original code commit, time windows, canonical source manifest/checksums, timezone, slippage scenario, risk policy, fill semantics, and protocol/run ID.
2. **One record per completed trade:** stable trade/decision ID; UTC entry and exit timestamps; side, units, entry/exit references and executions; stop/target; exit reason; net and gross PnL; slippage, spread/bid-ask basis, commission and financing attribution; pre-trade risk equity and requested risk fraction.
3. **Denominator:** compute `net_R = net_pnl_usd / (risk_equity_before_usd * requested_risk_fraction)`, with validation of positive finite per-trade starting risk. Do not divide every trade by the original $250 unless that identity is valid for that trade.
4. **Reconciliation:** unique IDs, deterministic chronological order, same 199 scored trades, exact per-window net PnL and cost totals, independently reset window equity, manifest/file hashes, source identity, no duplicates, and no look-ahead. Record any residual differences rather than discarding them.
5. **Time-series context:** preserve intertrade gaps, calendar dates, overlapping exposure, no-trade days, and cross-window resets. A seven-window independent-equity summary must not be treated as one continuous compounded account.
6. **Economic review:** attach a dated DEC-628-compatible cost provenance, observed or explicitly assumed slippage, financing uncertainty, and stress cases. Preserve the negative 1.0-pip result.
7. **Statistical review:** account for historical family selection, dependency, data reuse and limited opportunity frequency; prospective new validation requires genuinely later unseen observations. A simulated doubling rate is not an observed one.
8. **Authority:** require a separate, explicit owner/reviewer decision on data access and any historical replay, with correct provenance and applicable security checks **before** any such operation. An approval of a report format alone never authorizes an execution or protected access.

## Decision on possible evidence paths (none authorized by this document)

| Path | Current status | Appropriate next step |
| --- | --- | --- |
| A. Use current unprotected Stage 2 summary documents | **Available / insufficient** | Continue reporting aggregate expectancy and cost fragility only; do not calculate strategy-specific 30-day doubling/ruin probabilities |
| B. Identify any pre-existing independently authenticated trade ledger from historical Stage 2 | **Unknown / access not established** | Separately request a **read-only existence, classification and permission review**. Do not download artifacts, inspect private storage, or presume authorization |
| C. Re-execute the frozen Phase 7 strategy to capture individual trade records | **NOT AUTHORIZED** | Treat as a new historical data read/evaluation requiring separate review, precise reproducibility and decision; do not dispatch the old workflow, rewrite the authoritative Stage 2 evidence, or treat it as fresh OOS |
| D. Wait for genuinely new prospective data under a frozen future hypothesis | **Not yet available** | Separate project/governance decision, then prospective observation under the already-defined Phase 8A → Strategy V1 → shadow/demo order; no broker orders authorized |

No path above establishes a feasible 100%-in-30-days strategy.

## DEC-630 owner decision (still pending)

**Option 1 — maintain current policy (status quo):** do not adopt mechanism-first preregistered measurements as a separate protocol or make multiple-testing adjustment an active gate. Continue source-only tooling and the current annual-catalogue authorization boundaries.

**Option 2 — limited coexistence amendment (recommended for a *later explicit owner decision*):** permit **source-only preregistered measurement specifications** as pattern tools within DEC-469, with DEC-628 cost assumptions and the trial ledger; treat the DEC-632 BY-FDR function as optional until a verified complete family with valid p-values exists. Consider any new null-calibration or promotion gate only through another explicit amendment, before Strategy V1 synthesis. This option **does not** approve historical testing, access, workflow edits, annual dispatch, broker operations, or trading.

**Current disposition:** neither option is adopted by this draft. DEC-629 and DEC-630 remain **PROPOSED / NOT ADOPTED**. No implicit permission is inferred from a general instruction to continue source-only work.

## Separate #779 release blocker

Issue [#779](https://github.com/Dtwosam/FMP/issues/779) still documents a mutable-`main` ref resolution race: a check of `main` before GitHub server-side `workflow_dispatch` is not an exclusive lock, and a failed post-dispatch check cannot refund the unique 2023 annual **run 385**. The independently reviewed, effective exclusive lock/admission arrangement or separately approved immutable-ref design, run inventory and authorized dispatch are all still missing. Read-only review contracts in [#820](https://github.com/Dtwosam/FMP/issues/820) and [#821](https://github.com/Dtwosam/FMP/issues/821) are **not** proof of working OS isolation or a control-plane lock.

This trade-record audit does **not** solve #779 and cannot be used to authorize run 385.

## Current acceptance and next action

- **Read-only audit finding:** the Phase 7 trade-record reporting gap is identified from unprotected code and published summary documentation.
- **Trade-level series:** **UNAVAILABLE IN DOCUMENTED STAGE 2 EVIDENCE**; its existence elsewhere is unverified.
- **After-cost robust edge:** **NOT PROVEN**.
- **Strategy-specific 30-day doubling probability:** **NOT ESTIMABLE** from current aggregates.
- **Governing annual discovery / authorizations:** unchanged; no annual segment authorized.
- **Tests:** this document changes no executable files or test expectations. The previous local `unittest discover` on the PR #2331 tree failed with 145 failures and 229 errors, whereas the targeted PR #2331 GitHub checks succeeded. Do not describe the full local suite as green.

**Recommended immediate owner action:** decide only whether to approve a **future bounded, read-only existence/provenance/access review** for the original Phase 7 trade-level ledger, not its contents or a replay. Keep DEC-630 separate and unadopted pending explicit choice. Until then, FMP has sufficient measurement machinery; stop adding evidence-free strategy optimizers.
