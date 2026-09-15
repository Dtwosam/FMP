# Phase 7 Walk-Forward Evaluation Design

**Status:** APPROVED DESIGN — pending source-of-truth decision record and implementation plan  
**Date:** 2026-09-15  
**Repository:** `Dtwosam/FMP`  
**Phase:** 7 — Walk-forward evaluation  
**Proposed experiment:** `EXP-20260915-008`  
**Proposed decision:** `DEC-033`  
**Checkpoint target:** `fmp-v1-phase7-walk-forward`

## 1. Purpose

Phase 7 determines whether the two frozen Phase 4 rule-based research candidates survive one untouched out-of-sample promotion gate and then repeated forward evaluation without parameter retuning, ML overlays, or look-ahead.

The phase must preserve the evidence ordering required by the master specification and research-testing standard:

`historical research -> realistic backtest -> untouched OOS -> walk-forward -> shadow`

The design therefore separates Phase 7 into two irreversible stages:

1. a one-shot 2024 untouched out-of-sample gate; and
2. quarterly walk-forward evaluation from 2025-01-01 through the accepted data endpoint 2026-08-20 inclusive.

Phase 7 does not authorize broker integration, live quotes, demo trading, order submission, or real-money trading.

## 2. Approved candidates

Only the two frozen rule-based candidates retained at the end of Phase 6 are eligible.

### 2.1 Session breakout

- strategy ID: `session_breakout`
- symbol: `USDJPY`
- signal timeframe: `15m`
- buffer: `5` pips
- target: `1.5` times the session range
- strategy version: existing frozen Phase 4 implementation
- ML overlay: none

### 2.2 Rolling volatility breakout

- strategy ID: `volatility_breakout`
- symbol: `USDJPY`
- signal timeframe: `1h`
- rolling reference: existing frozen `8h` reference from Phase 4
- range multiplier: `2.0`
- target: `1.0R`
- strategy version: existing frozen Phase 4 implementation
- ML overlay: none

No other pair, timeframe, strategy family, parameter point, feature subset, model, or threshold may enter `EXP-20260915-008`.

## 3. Frozen behavior and immutable inputs carried forward

Phase 7 reuses the accepted Phase 3 simulator and the frozen Phase 4 strategy semantics. It does not create a second execution model.

The following remain unchanged:

- historical BID/ASK execution;
- conservative intrabar ambiguity handling;
- adverse slippage applied exactly once;
- zero commission and zero financing for these mandatory-intraday-flat strategies;
- requested risk per trade: `0.25%` equity;
- hard maximum risk per trade: `0.50%` equity;
- maximum simultaneous open risk: `1.00%` equity;
- maximum daily realized loss before halt: `1.50%` of UTC day-start realized risk equity;
- deterministic decision ordering and Phase 3 lifecycle semantics;
- frozen candidate parameters above.

Phase 6 concluded that no ML challenger was promoted. Phase 7 therefore evaluates the frozen rule baselines only. There is no model fitting, probability filtering, score cutoff, feature selection, or ML refit in this phase.

The immutable upstream identities for `EXP-20260915-008` are:

- Phase 6 checkpoint: `fmp-v1-phase6-models`;
- Phase 6 checkpoint commit: `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`;
- accepted Phase 2 USDJPY artifact ID: `10327600628`;
- accepted Phase 2 USDJPY artifact ZIP SHA-256: `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`;
- accepted Phase 2 USDJPY processed-manifest SHA-256: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`;
- accepted canonical schema identity: the existing Phase 2 canonical schema version referenced by that processed manifest.

A mismatch in any immutable upstream identity fails closed.

## 4. Data partition architecture

The Phase 4 source-of-truth previously defined one untouched period from `2024-01-01` through `2026-08-20` inclusive. Phase 7 partitions that still-unseen history once, before reading any Phase 7 result:

- **one-shot OOS gate:** `2024-01-01 <= T < 2025-01-01`
- **walk-forward horizon:** `2025-01-01 <= T < 2026-08-21`

This partition does not weaken any existing loader. Normal Phase 4 and Phase 6 tooling must continue to reject required source coverage reaching `2024-01-01` or later.

All Phase 7 access occurs through a new, promotion-only module and workflow whose allowed ranges are explicit constants and whose guards run before manifest or Parquet I/O.

### 4.1 Accepted data endpoint

The frozen Phase 1/2 history ends on `2026-08-20` inclusive. All Phase 7 half-open intervals therefore use `2026-08-21` as the maximum `end_exclusive` boundary.

### 4.2 No post-result repartitioning

Once `DEC-033` is recorded, the date boundaries in this document are frozen for `EXP-20260915-008`. They may not be shortened, widened, shifted, or regrouped after seeing results.

## 5. Stage 1 — one-shot 2024 untouched OOS gate

### 5.1 Access rule

The Stage 1 evaluator may score trades only when the signal/execution belongs to:

`2024-01-01 <= T < 2025-01-01`

It may not open, inspect, summarize, checksum-select, or otherwise derive evidence from a required 2025 or 2026 processed partition.

### 5.2 Warm-up rule

A bounded pre-window warm-up is allowed only to reconstruct strategy state needed for the first eligible 2024 decisions.

- maximum warm-up: seven calendar days immediately preceding `2024-01-01`;
- earliest allowed warm-up timestamp: `2023-12-25T00:00:00Z`;
- warm-up data is input context only;
- no warm-up signal may become a scored Phase 7 candidate, decision, trade, or metric observation;
- no PnL from warm-up may enter starting equity or Phase 7 metrics;
- the Stage 1 account starts at exactly `$100,000` at `2024-01-01T00:00:00Z`.

The implementation must prove by test that warm-up context cannot itself create a scored pre-boundary trade and that the first scored decision uses only state legitimately knowable at or before its decision time.

### 5.3 Cost scenarios

Each candidate is evaluated independently at exactly:

- `0.2` pips adverse slippage per fill;
- `0.5` pips adverse slippage per fill;
- `1.0` pip adverse slippage per fill.

The `0.2` and `0.5` scenarios are gating. The `1.0` scenario is diagnostic only and must still be preserved in evidence.

### 5.4 Stage 1 candidate gate

A candidate advances to Stage 2 only if **all** of the following are true at both `0.2` and `0.5` pip slippage:

- net return is strictly positive;
- expectancy per completed trade is strictly positive;
- profit factor is strictly greater than `1.0`;
- maximum drawdown fraction is less than or equal to `0.05`.

In addition, the `0.2`-pip baseline scenario must contain at least `40` completed trades. The trade-count requirement is deliberately baseline-only and is not redefined after results are observed.

There is no cross-candidate ranking. Each candidate passes or fails independently against the frozen gate.

### 5.5 Stage 1 fail-closed behavior

If neither candidate passes:

- `EXP-20260915-008` records a Phase 7 rejection outcome;
- Stage 2 is not authorized;
- no required 2025/2026 partition may be opened by Phase 7 tooling;
- Phase 8 remains locked;
- all 2024 negative evidence is retained.

If exactly one candidate passes, only that candidate enters Stage 2. If both pass, both enter Stage 2 independently.

No failed candidate may be repaired, retuned, swapped for a neighboring parameter point, or replaced by an ML variant inside this experiment.

## 6. Stage 2 — walk-forward evaluation

### 6.1 Forward windows

Stage 2 uses exactly seven non-overlapping forward windows:

1. `2025-Q1`: `2025-01-01 <= T < 2025-04-01`
2. `2025-Q2`: `2025-04-01 <= T < 2025-07-01`
3. `2025-Q3`: `2025-07-01 <= T < 2025-10-01`
4. `2025-Q4`: `2025-10-01 <= T < 2026-01-01`
5. `2026-Q1`: `2026-01-01 <= T < 2026-04-01`
6. `2026-Q2`: `2026-04-01 <= T < 2026-07-01`
7. `2026-partial-Q3`: `2026-07-01 <= T < 2026-08-21`

All seven windows are evaluated for every Stage 1 survivor. A losing intermediate window does not stop later windows; this prevents early-stop cherry-picking.

### 6.2 Fixed-rule refit status

The promoted candidates are fixed rule systems, not fitted statistical models. Therefore each Stage 2 window must record:

`refit_status = NOT_APPLICABLE_FIXED_RULE`

No parameter, feature, threshold, or strategy state is optimized from previous forward-window outcomes.

### 6.3 Window state, warm-up, and account semantics

Each forward window is an independent evaluation unit with:

- starting equity exactly `$100,000`;
- unchanged Phase 3 risk settings;
- only that window's scored decisions and trades contributing to window metrics;
- up to seven calendar days of context immediately preceding the window start.

For Stage 2, a warm-up interval may overlap the preceding forward window because it is historical context for the new window. Rows in that overlap may have been scored in the earlier window, but they are context-only for the new window and cannot be scored a second time in the new window. No warm-up PnL carries into the new window's starting equity.

Independent window equity prevents the outcome of an earlier forward window from mechanically changing dollar position size in a later window. Aggregate Phase 7 metrics are computed from normalized per-window returns/trade records rather than by chaining capital across windows.

### 6.4 Cost scenarios

Each Stage 2 window is evaluated at the same exact slippage scenarios:

- `0.2` pips;
- `0.5` pips;
- `1.0` pip.

The first two are gating; `1.0` pip remains diagnostic.

## 7. Stage 2 aggregate promotion gate

A candidate passes Phase 7 for promotion to Phase 8 design only if all of the following are satisfied.

### 7.1 Aggregate financial gate at 0.2 pips

Across all seven windows combined:

- aggregate net return is strictly positive;
- aggregate expectancy per completed trade is strictly positive;
- aggregate profit factor is strictly greater than `1.0`;
- total completed trade count is at least `100`;
- aggregate maximum drawdown fraction is less than or equal to `0.05`.

### 7.2 Aggregate financial gate at 0.5 pips

Across all seven windows combined:

- aggregate net return is strictly positive;
- aggregate expectancy per completed trade is strictly positive;
- aggregate profit factor is strictly greater than `1.0`;
- aggregate maximum drawdown fraction is less than or equal to `0.05`.

### 7.3 Window stability gate

At `0.2` pips:

- at least four of the seven forward windows must have strictly positive net PnL;
- let `positive_window_pnl` be the sum of positive net PnL across all positive windows;
- when `positive_window_pnl > 0`, no single positive window may contribute more than `50%` of `positive_window_pnl`.

The concentration test is evaluated on USD PnL because each window starts from the same `$100,000`, making window contributions directly comparable.

### 7.4 Diagnostic 1.0-pip evidence

The `1.0`-pip aggregate and per-window metrics are recorded but do not independently determine PASS/FAIL. They remain part of the evidence package for later shadow-design risk review.

## 8. Aggregate metric construction

Phase 7 must not create misleading aggregate statistics by naively concatenating independently reset equity curves.

For each candidate and cost scenario:

- aggregate net return = arithmetic sum of the seven independent window net returns;
- aggregate completed trade count = sum of window completed trade counts;
- aggregate net PnL = sum of window net PnL in USD;
- aggregate expectancy = aggregate net PnL divided by aggregate completed trade count;
- aggregate profit factor = total gross profit across all windows divided by absolute total gross loss across all windows, using the existing Phase 3 convention for a zero-loss denominator;
- aggregate maximum drawdown = maximum of the seven independently measured window maximum-drawdown fractions, not a synthetic chained-equity drawdown.

The evidence must also preserve each window's native Phase 3/research metrics without replacement by aggregate summaries.

## 9. New module boundary

Phase 7 introduces a dedicated package:

`src/fmp/walkforward/`

It owns only Phase 7 promotion evaluation and evidence assembly.

Expected responsibilities:

- `contracts.py` — frozen Stage 1/Stage 2 date contracts, candidate identities, cost scenarios, upstream identities, and gate constants;
- `data.py` — promotion-only processed-data loader with pre-I/O range guards and exact partition accounting;
- `evaluation.py` — single-candidate/single-window execution over existing strategy generators and Phase 3 backtester;
- `gates.py` — pure Stage 1 and Stage 2 gate functions;
- `artifacts.py` — deterministic JSON evidence and manifest generation;
- `cli.py` — explicit Stage 1 and Stage 2 entry points.

A thin script under `scripts/` may call the package CLI. Strategy logic remains in the existing strategy modules; Phase 7 must not duplicate it.

## 10. Isolation from existing research loaders

The existing Phase 4/6 loaders intentionally fail closed before I/O for any split that reaches `2024-01-01` or later. Those guards are security/research controls and must remain unchanged.

Phase 7 therefore must not:

- add `final` to the normal `allowed_split()` path;
- relax `_FINAL_TEST_START` guards in `fmp.research.data`;
- relax Phase 6 `FINAL_START` guards;
- add a generic flag such as `allow_final=True` to existing development/validation tooling;
- expose arbitrary user-provided 2024+ date ranges.

Only the new Phase 7 contracts may enumerate the exact approved ranges.

## 11. Workflow separation

Phase 7 uses two manual GitHub Actions workflows with read-only repository/action permissions.

### 11.1 Stage 1 workflow

Proposed name: `phase7-final-gate`

Responsibilities:

1. checkout exact implementation commit;
2. install the package;
3. download and checksum-verify accepted Phase 2 USDJPY artifact `10327600628`;
4. verify the artifact ZIP SHA-256 and processed-manifest SHA-256 against the immutable values in Section 3;
5. execute each frozen candidate twice for Stage 1;
6. require byte-identical deterministic evidence across repeats;
7. verify the evidence contains only approved Stage 1 scored coverage plus bounded pre-2024 warm-up;
8. upload one evidence artifact per candidate.

The workflow must not download Phase 5 feature artifacts because Phase 7 uses no ML overlay.

### 11.2 Stage 2 workflow

Proposed name: `phase7-walk-forward`

Stage 2 must not be runnable as an unguarded generic historical evaluator. Before opening required 2025/2026 data it must receive and verify a recorded Stage 1 PASS identity for the candidate, including:

- experiment ID;
- candidate ID/configuration;
- Stage 1 implementation commit;
- accepted Phase 2 processed-manifest SHA-256;
- Stage 1 evidence digest;
- Stage 1 PASS decision status.

Its responsibilities then mirror Stage 1: execute twice, compare deterministic evidence, verify exact allowed windows, and upload final Phase 7 evidence.

## 12. Evidence contract

Each candidate evidence package must include at minimum:

- `manifest.json`;
- `stage1.json` for the 2024 gate;
- `windows.json` for Stage 2 survivors;
- `result.json` with final Phase 7 decision;
- deterministic SHA-256 identities for constituent files.

### 12.1 Required identity fields

Evidence records must identify:

- `experiment_id = EXP-20260915-008`;
- exact code commit;
- Phase 6 checkpoint tag and exact checkpoint SHA from Section 3;
- accepted Phase 2 artifact ID, ZIP SHA-256, and processed-manifest SHA-256 from Section 3;
- canonical schema version;
- candidate strategy ID/version;
- symbol and timeframe;
- frozen parameter mapping;
- requested risk fraction and risk-policy identity;
- slippage scenarios;
- commission/financing identity;
- every scored range;
- every warm-up range actually opened;
- every processed monthly partition actually opened;
- candidate/trade counts;
- Stage 1 gate criteria;
- per-window Stage 2 metrics and criteria;
- aggregate Stage 2 metrics and criteria;
- final decision status.

### 12.2 Determinism

Repeating the same candidate/stage on the same code/data/config must produce byte-identical evidence files. Runtime clocks, hostnames, UUIDs, temporary paths, and nondeterministic ordering are forbidden from evidence content.

## 13. Fail-closed behavior

Phase 7 must fail before data I/O when any of the following occurs:

- a requested scored range differs from an approved Stage 1/Stage 2 range;
- a warm-up range exceeds seven calendar days;
- a warm-up range extends beyond the immediately preceding interval;
- a Stage 1 run attempts to reach `2025-01-01` or later;
- a Stage 2 run lacks an approved Stage 1 PASS identity for that candidate;
- a candidate identity or parameters differ from the frozen contract;
- the Phase 6 checkpoint identity differs from Section 3;
- the Phase 2 artifact or processed-manifest identity differs from Section 3;
- required data is missing or duplicate;
- a required opened partition lies outside the exact approved scored/warm-up ranges;
- deterministic repeat evidence differs.

Failures remain evidence. A failed orchestration run does not silently become a successful research result after partial outputs are inspected.

## 14. Testing requirements

Implementation must be test-first and include at minimum:

### 14.1 Contract tests

- exact Stage 1 and seven Stage 2 boundaries;
- accepted end-exclusive `2026-08-21`;
- invalid arbitrary date range rejected;
- frozen candidate identities/parameters cannot be mutated;
- exact upstream checkpoint/data identities;
- exact cost scenarios and gate constants.

### 14.2 Data-isolation tests

- Stage 1 rejects any required `2025-*` or `2026-*` partition before file read;
- Stage 2 rejects access without Stage 1 PASS proof before file read;
- normal Phase 4/6 loaders still reject 2024+ after Phase 7 is added;
- warm-up is at most seven calendar days and immediately precedes its scored window;
- warm-up rows never become scored trades or metrics for the current window;
- a Stage 2 warm-up overlap with the prior window is not double-scored in the new window;
- monthly partition accounting is exact and deterministic;
- path traversal or missing artifact paths fail closed.

### 14.3 Strategy/execution parity tests

For synthetic bars that fit inside pre-2024 dates, the Phase 7 wrapper must reproduce the same candidate/decision/trade outcomes as the existing frozen Phase 4 strategy plus Phase 3 simulator for equivalent configuration.

### 14.4 Gate tests

Cover exact boundary behavior for:

- zero versus positive return/expectancy;
- profit factor exactly `1.0` versus greater than `1.0`;
- `39` versus `40` Stage 1 baseline trades;
- drawdown exactly `5%` versus above `5%`;
- `99` versus `100` aggregate Stage 2 trades;
- three versus four positive windows;
- positive-window concentration exactly `50%` versus greater than `50%`.

### 14.5 Determinism tests

- stable JSON key/order serialization;
- stable candidate/window ordering;
- identical repeated artifact bytes;
- evidence manifest digests match recomputation.

### 14.6 Regression tests

Before Phase 7 acceptance:

- full repository tests pass;
- workflow YAML validation passes;
- package compile passes;
- Phase 3 acceptance remains green;
- source-capable Phase 1 workflows remain skipped for source-free Phase 7 documentation/code merges unless deliberately dispatched under their own rules.

## 15. Source-of-truth updates before implementation

Before Phase 7 implementation begins, the approved written spec must be accompanied by a source-of-truth decision entry `DEC-033` that freezes this protocol and explicitly records the one-time partition of the previously untouched period.

The same change must update `docs/project-state.md` so that:

- Phase 6 remains closed PASS at `fmp-v1-phase6-models`;
- Phase 7 becomes ACTIVE for test-first implementation of `EXP-20260915-008`;
- 2024+ data remains unopened until the Stage 1 workflow is deliberately dispatched after implementation verification;
- Phase 8 remains UNSTARTED;
- broker/live/demo integration and real-money trading remain locked.

## 16. Acceptance and terminal outcomes

Phase 7 has two legitimate terminal outcomes.

### 16.1 PASS / eligible for Phase 8 shadow design

At least one candidate:

1. passes the Stage 1 2024 untouched OOS gate; and
2. completes all seven Stage 2 forward windows; and
3. passes every Stage 2 aggregate/stability condition.

That candidate is then eligible only for Phase 8 shadow-mode design. No broker/demo/live permission follows automatically.

### 16.2 COMPLETE / REJECT

Phase 7 completes with a rejection outcome, not a promotion PASS, when:

- neither candidate passes Stage 1; or
- Stage 1 survivor(s) complete all seven forward windows and none passes the Stage 2 promotion gate.

All negative evidence must be retained. Phase 8 remains locked unless the source-of-truth is explicitly amended with a justified next research direction.

The phase checkpoint `fmp-v1-phase7-walk-forward` is created only after the experiment outcome is recorded, fresh merged-main verification passes, and Phase 7 acceptance evidence is complete. The checkpoint records the frozen outcome whether that outcome is promotion PASS or completed rejection.

## 17. Explicit non-goals

`EXP-20260915-008` does not authorize:

- parameter retuning;
- neighboring-parameter rescue experiments;
- a new strategy family;
- pair/timeframe expansion;
- ML reintroduction;
- feature engineering or feature selection;
- probability-based sizing;
- portfolio optimization;
- correlated multi-position changes;
- new risk limits;
- tick-data research;
- live quote ingestion;
- broker adapters;
- shadow execution implementation;
- demo trading;
- real-money execution.

Any such work requires a later phase or a separately approved source-of-truth amendment.

## 18. Rationale for quarterly windows

Quarterly windows are chosen before result access because they balance two competing requirements:

- monthly windows would create many low-sample observations for these relatively low-frequency candidates;
- semiannual windows would yield too few repeated forward observations across the remaining history.

Seven non-overlapping quarterly/partial-quarter windows provide repeated chronology while keeping each interval large enough to produce interpretable strategy evidence. The final partial quarter is unavoidable because the frozen accepted dataset ends on 2026-08-20 and must not be padded with unaccepted future history.

## 19. Review checklist

Before this design is translated into an implementation plan, review must confirm:

- no placeholder or unresolved parameter remains;
- all Phase 7 data ranges are exact;
- immutable Phase 6/Phase 2 identities are exact;
- existing Phase 4/6 final-test locks remain unchanged;
- Stage 2 cannot access 2025+ without Stage 1 PASS proof;
- both candidates remain frozen exactly as accepted;
- no ML or broker path is introduced;
- all gating thresholds are predeclared;
- deterministic evidence requirements are explicit;
- promotion PASS and completed rejection are distinct outcomes;
- Phase 8 and real-money paths remain locked.
