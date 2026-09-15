# Phase 7 Walk-Forward Evaluation Design

**Status:** APPROVED — implementation governed by `docs/superpowers/plans/2026-09-15-phase7-walk-forward.md`; source-of-truth activation remains Task 1 so RED state tests precede DEC-033/project-state edits  
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

## 3. Frozen behavior carried forward

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
- Phase 2 accepted processed-data identity;
- frozen candidate parameters above.

Phase 6 concluded that no ML challenger was promoted. Phase 7 therefore evaluates the frozen rule baselines only. There is no model fitting, probability filtering, score cutoff, feature selection, or ML refit in this phase.

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

The implementation must prove by test that changing warm-up-only candidate opportunities cannot change the scored trade ledger except through legitimate state required at or after the Stage 1 boundary.

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
- completed trade count is at least `40` in the `0.2`-pip baseline scenario;
- maximum drawdown fraction is less than or equal to `0.05`.

The trade-count condition is evaluated once at `0.2` pips because candidate generation is cost-invariant and the accepted simulator should not change eligibility solely because the configured slippage value changes.

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

### 6.3 Window state and account semantics

Each forward window is an independent evaluation unit with:

- starting equity exactly `$100,000`;
- unchanged Phase 3 risk settings;
- only that window's scored decisions and trades contributing to window metrics;
- up to seven calendar days of pre-window warm-up context under the same exclusion rules as Stage 1.

When a Stage 2 warm-up interval overlaps the immediately preceding scored window, the same historical source bars may be reopened solely as state context for the later window. They remain unscored in the later window and may not duplicate any candidate, decision, trade, PnL, or metric observation.

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

- `contracts.py` — frozen Stage 1/Stage 2 date contracts, candidate identities, cost scenarios, and gate constants;
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
3. download and checksum-verify the accepted Phase 2 USDJPY artifact;
4. execute each frozen candidate twice for Stage 1;
5. require byte-identical deterministic evidence across repeats;
6. verify the evidence contains only approved Stage 1 scored coverage plus bounded pre-2024 warm-up;
7. upload one evidence artifact per candidate.

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
- exact Phase 6 checkpoint SHA `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`;
- accepted Phase 2 USDJPY artifact ID `10327600628` and ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`;
- accepted Phase 2 processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`;
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
- the accepted-data endpoint would be exceeded;
- a candidate, symbol, timeframe, or parameter mapping differs from the frozen contract;
- the processed manifest identity differs from the accepted USDJPY Phase 2 manifest;
- the Phase 6 checkpoint identity differs from `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`;
- Stage 2 lacks a valid Stage 1 PASS authorization identity;
- a workflow attempts to make dates or strategy parameters caller-configurable.

After I/O begins, malformed schema, duplicate identities, wrong source symbol/timeframe, missing source partitions, incomplete required cadence, or nondeterministic evidence also fail closed. None of these conditions may trigger parameter repair or alternate candidate selection.

## 14. Testing requirements

The implementation must be test-first and cover at minimum:

- exact immutable contract values;
- rejection of arbitrary Phase 7 date ranges;
- fail-before-I/O behavior for invalid ranges/identities;
- unchanged normal Phase 4/6 final-test locks;
- exact Stage 1 and seven Stage 2 windows;
- bounded warm-up inclusion and scored-trade exclusion;
- overlapping previous-window warm-up bars never being rescored;
- exact frozen strategy configuration reuse;
- exact Phase 3 risk/cost/execution reuse;
- independent `$100,000` starting equity per forward window;
- `NOT_APPLICABLE_FIXED_RULE` refit status;
- every Stage 1 and Stage 2 gate boundary;
- aggregate financial arithmetic and concentration logic;
- deterministic evidence generation;
- Stage 2 authorization before source I/O;
- workflow exact artifact identities and double-run byte comparisons;
- no generic final-test escape hatch;
- Phase 8, broker, demo, live, and real-money locks.

## 15. Source-of-truth and experiment state

The approved design is now the authoritative Phase 7 design basis. `DEC-033`, project-state activation, and `EXP-20260915-008` registry activation are intentionally applied as implementation-plan Task 1 so the required failing protocol-state test exists before those source-of-truth edits.

Until Task 1 executes and later guarded implementation is merged:

- Phase 6 remains the last closed phase on `main`;
- `Final-test touched: NO` remains true;
- existing tooling remains unable to open 2024+;
- no Phase 7 workflow may be dispatched.

After DEC-033 is recorded, Phase 7 becomes ACTIVE for test-first implementation, but DEC-033 alone still does not authorize existing tooling or partially implemented code to open 2024+ data. The first authorized 2024 data access occurs only through the verified merged Stage 1 workflow described in the implementation plan.

## 16. Phase completion semantics

A valid negative result is not an implementation failure.

- If neither candidate passes Stage 1, Phase 7 is complete with a rejection outcome and Stage 2 remains forbidden.
- If Stage 1 produces survivor(s), each survivor must complete all seven Stage 2 windows.
- A candidate is eligible for Phase 8 shadow design only when every Stage 2 aggregate/stability gate passes.
- Phase 8 does not start automatically after Phase 7; it requires its own design/activation work.
- Broker/live/demo/real-money authorization is unchanged.

The target immutable Phase 7 checkpoint remains `fmp-v1-phase7-walk-forward`, created only after final evidence/state closure and fresh merged-main verification.