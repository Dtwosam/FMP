# Phase 4 Trend-Continuation Baseline Design

**Date:** 2026-09-14  
**Phase:** Phase 4 — Baseline Strategy Research  
**Experiment:** `EXP-20260914-002 — Trend continuation baseline`  
**Status:** design approved in chat; implementation not started  
**Base commit:** `5ad5cac64a537107d8a1683101814bd1ce159083`

## 1. Purpose

Add the second predeclared Phase 4 baseline family, trend continuation, without changing the accepted Phase 3 execution/risk engine or the common Phase 4 research boundaries. The family tests whether a London-session pullback followed by resumption in an already established multi-hour trend can survive historical BID/ASK spread and adverse slippage.

This is a baseline research experiment, not a profitability promise and not a deployment path. The frozen session-breakout candidate remains unchanged while this family is evaluated.

## 2. Scope

### In scope

- deterministic trend-continuation candidate generation;
- development and validation research only;
- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h signal bars;
- exact predeclared trend-window and target grid;
- existing Phase 4 processed-data loader, strategy adapter, research reporting, and Phase 3 backtester/risk engine;
- source-free GitHub Actions benchmark execution from exact accepted Phase 2 artifacts;
- deterministic artifacts and experiment-log evidence.

### Out of scope

- final-test access (`2024-01-01` through `2026-08-20`);
- changes to Phase 1 acquisition, `fmp-raw`, Supabase, OIDC, or `docs/phase1-exact-gap-queue.json`;
- changes to accepted Phase 3 execution/risk semantics except bug fixes proven independently necessary;
- ML, learned features, generic feature-store work, broker APIs, shadow/demo/live execution, or real-money trading;
- post-result expansion of this experiment's parameter grid;
- modification of the frozen `EXP-20260914-001` session-breakout candidate.

## 3. Research hypothesis

> During the London trading day, a pullback that temporarily crosses a short trend average and then resumes in the direction of an established multi-hour trend may have enough continuation to overcome historical BID/ASK spread and adverse slippage under fixed-risk execution.

No profitability is assumed. A family with no robust candidate is a valid experiment result.

## 4. Data and chronology

Use the existing accepted Phase 2 processed artifacts and Phase 4 chronological split contract:

- development: `2015-01-01` through `2020-12-31` inclusive;
- validation: `2021-01-01` through `2023-12-31` inclusive;
- final untouched test: `2024-01-01` through `2026-08-20` inclusive.

The normal runner must expose only `development` and `validation`. A request for `final` must fail before any data file is opened.

The strategy consumes only complete, chronologically ordered bars from the existing Phase 4 loader. Analysis prices are midpoint OHLC values derived by the already accepted research-data conventions. BID/ASK remains the sole source of executable fills and PnL in Phase 3.

## 5. Signal timing and anti-leakage contract

The existing Phase 4 timing bridge is authoritative and must not be weakened.

For a supplied left-labelled bar with observation label `T` and width `W`:

- the bar is not fully known until `T + W`;
- the signal-known time is `T + W`;
- the earliest executable timestamp is `T + W`;
- execution occurs only on the first supplied bar whose timestamp equals that true known time;
- no signal may fill on its own observation bar.

Trend averages, pullback state, stop geometry, and target geometry may use only bars fully closed by the signal-known time.

## 6. London-session eligibility

Signal observation is limited to closed bars whose London-local observation labels are from **08:00 inclusive through 14:00 inclusive** in `Europe/London`.

Only the first qualifying continuation signal per symbol and London calendar session may become a directional candidate. Later same-session qualifying signals are ignored after the first directional candidate has been emitted.

If no qualifying directional setup occurs, the family must preserve an explicit `NO_TRADE` candidate/reason record for the session rather than silently omitting the day.

DST conversion must use `Europe/London`; fixed UTC-hour approximations are prohibited.

## 7. Trend definition

Trend is defined by simple moving averages of midpoint close over wall-clock durations. Durations are converted exactly into bar counts for the supplied signal timeframe.

The three predeclared trend-window pairs are:

| Grid ID | Fast duration | Slow duration |
| --- | ---: | ---: |
| A | 2 hours | 8 hours |
| B | 4 hours | 16 hours |
| C | 8 hours | 32 hours |

Exact bar counts:

| Timeframe | A fast/slow | B fast/slow | C fast/slow |
| --- | --- | --- | --- |
| 5m | 24 / 96 | 48 / 192 | 96 / 384 |
| 15m | 8 / 32 | 16 / 64 | 32 / 128 |
| 1h | 2 / 8 | 4 / 16 | 8 / 32 |

LONG trend context requires both:

1. current fast SMA > current slow SMA; and
2. current slow SMA > the immediately previous-bar slow SMA.

SHORT trend context is the exact inverse:

1. current fast SMA < current slow SMA; and
2. current slow SMA < the immediately previous-bar slow SMA.

Equality is neutral and produces no directional context.

Because the slow-SMA slope compares current and prior slow windows, eligibility requires enough complete history to compute both windows. Missing or incomplete cadence anywhere in the required rolling context makes the observation ineligible; the implementation may not shorten the lookback or impute missing bars.

## 8. Pullback and resumption trigger

For each eligible closed bar, use the same fast-SMA series used by the trend context.

LONG resumption requires:

- the immediately previous closed midpoint close is less than or equal to its corresponding fast SMA;
- the current closed midpoint close is strictly greater than the current fast SMA;
- the current trend context is LONG.

SHORT resumption requires:

- the immediately previous closed midpoint close is greater than or equal to its corresponding fast SMA;
- the current closed midpoint close is strictly less than the current fast SMA;
- the current trend context is SHORT.

This is a close-based pullback/resumption definition. Intrabar touches of the fast SMA without the required closed-bar relationship do not qualify.

## 9. Stop geometry

The stop is structural and has no search dimension.

For a LONG signal:

- stop price = minimum midpoint low across the current signal bar and the two immediately preceding fully closed bars.

For a SHORT signal:

- stop price = maximum midpoint high across the current signal bar and the two immediately preceding fully closed bars.

All three bars must be contiguous and complete at the signal timeframe. If not, the signal is ineligible.

The stop freezes when the signal becomes known and may not be widened, tightened, or recomputed after observing the executable next bar.

A zero or directionally invalid signal-time risk distance produces no executable directional order and must be represented deterministically as a rejected/no-trade reason rather than repaired.

## 10. Target geometry

Define signal-time midpoint risk `R` from the frozen signal midpoint close to the frozen structural stop:

- LONG: `R = signal_mid_close - stop`;
- SHORT: `R = stop - signal_mid_close`.

`R` must be strictly positive.

The two predeclared target multiples are:

- `1.0R`;
- `1.5R`.

Targets are frozen at signal-known time:

- LONG target = `signal_mid_close + target_multiple * R`;
- SHORT target = `signal_mid_close - target_multiple * R`.

Target price is not recomputed from the actual next-bar entry. This deliberately keeps strategy geometry based only on closed signal information.

## 11. Gap handling and actual-entry geometry

The actual fill remains Phase 3 BID/ASK execution with adverse slippage. Therefore the next executable bar can gap enough that a signal-time stop or target is no longer valid relative to the actual fill.

The strategy/adapter must not repair such geometry after seeing the gap.

- LONG requires frozen stop < actual executable entry < frozen target.
- SHORT requires frozen target < actual executable entry < frozen stop.

If these relations are not satisfied at the executable timestamp, the order must be rejected through the existing deterministic rejection surface before a position is opened.

No stop chasing, target moving, alternate entry, or later-bar retry is allowed under this experiment ID.

## 12. Scheduled exit

Every opened trend-continuation position must carry an exact scheduled flat timestamp of **16:00 Europe/London** on the signal's London calendar date.

The accepted Phase 3 `TIME_EXIT` behavior remains authoritative:

- LONG time exit uses executable BID side with configured adverse slippage/costs;
- SHORT time exit uses executable ASK side with configured adverse slippage/costs;
- a prior stop or target makes the scheduled exit a no-op;
- scheduled exit ordering relative to same-timestamp risk/entry events remains the accepted Phase 3 ordering.

The exact 16:00-local executable bar must exist. Missing exact scheduled-exit data fails closed for that session; the implementation must not choose the nearest later bar.

The family is therefore mandatory-intraday-flat, and zero financing remains the predeclared financing model for this baseline.

## 13. Frozen strategy grid

The search grid is exactly:

- trend window A (2h/8h) × target {1.0R, 1.5R};
- trend window B (4h/16h) × target {1.0R, 1.5R};
- trend window C (8h/32h) × target {1.0R, 1.5R}.

That is exactly **6 strategy configurations per pair/timeframe**.

There is no stop-length grid, entry-buffer grid, session-hour grid, SMA-type grid, or post-result parameter expansion under `EXP-20260914-002`.

## 14. Cost and risk assumptions

Keep the first-family assumptions unchanged so baseline families remain directly comparable.

Execution/cost model:

- historical BID/ASK spread inherent in Phase 3 fills;
- adverse slippage scenarios: `0.2`, `0.5`, `1.0` pips per fill;
- commission: zero;
- financing: zero.

Risk policy remains the accepted Phase 3 policy:

- requested risk/trade: 0.25% of current risk equity;
- hard maximum risk/trade: 0.50%;
- maximum simultaneous reserved open risk: 1.00%;
- daily realized-loss halt: 1.50% of UTC day-start equity;
- halt blocks new entries but does not force-close existing positions;
- next UTC risk day resets the halt with the accepted Phase 3 basis.

Risk requests are never silently clamped. Existing Phase 3 sizing and rejection reason semantics remain authoritative.

## 15. Experiment matrix

The merged-main benchmark matrix is fixed to:

- 3 pairs: EURUSD, GBPUSD, USDJPY;
- 3 signal timeframes: 5m, 15m, 1h;
- 2 chronological splits: development, validation;
- 6 strategy configurations;
- 3 adverse-slippage scenarios.

This produces:

- 18 workflow cells; and
- **324 benchmark configuration rows** in the complete evidence set.

Candidate generation for a given pair/timeframe/split/configuration must be reused byte-for-byte across the three cost scenarios. Costs may change fills/PnL/rejections only where execution semantics require; the alpha candidate stream itself must not depend on slippage.

## 16. Architecture and file boundaries

Reuse the existing Phase 4/Phase 3 layers rather than create a parallel stack.

### Strategy module

`src/fmp/strategies/trend_continuation.py`

Responsibilities:

- validate the six-point strategy configuration;
- convert wall-clock trend durations to exact bar counts;
- compute midpoint SMA context from complete closed bars;
- detect the first London-session pullback/resumption;
- freeze stop, target, signal-known time, and 16:00-local scheduled exit;
- emit stable `SignalCandidate` records and reason codes.

It must not perform BID/ASK fills, sizing, account state, or PnL.

### Research runner

`src/fmp/research/trend_continuation.py`

Responsibilities:

- expose the exact six-point grid and three slippage scenarios;
- load only development/validation through the existing Phase 4 loader;
- generate candidates once per strategy configuration;
- adapt them through the existing research adapter;
- run the accepted Phase 3 backtester for each cost scenario;
- produce the existing deterministic research-reporting schema.

### CLI and workflow

Add a source-free CLI script/workflow analogous to the session-breakout benchmark. It must:

- accept only the fixed pair/timeframe/split surface needed by the 18-cell matrix;
- reject final-test mode before file I/O;
- download only the accepted Phase 2 processed artifact IDs/digests;
- verify ZIP digest before extraction;
- use read-only GitHub permissions needed for checkout/artifact download;
- request no OIDC token and perform no Supabase/source/raw mutation;
- upload deterministic benchmark evidence only after identity checks succeed.

### Existing modules that remain authoritative

Do not duplicate or replace:

- `fmp.strategies.contracts`;
- `fmp.research.contracts`;
- `fmp.research.data`;
- `fmp.research.adapter`;
- `fmp.research.reporting`;
- Phase 3 execution, costs, risk, account/equity, and reporting semantics.

If implementation reveals that one of these common interfaces cannot represent the frozen design, stop and treat that as an architectural change rather than bypassing the interface.

## 17. Determinism and evidence identity

Every benchmark artifact must bind at minimum to:

- exact merged-main code SHA;
- experiment ID `EXP-20260914-002`;
- pair, timeframe, split;
- accepted processed-data manifest/schema identity;
- exact strategy configuration;
- exact slippage scenario;
- unchanged Phase 3 risk settings;
- candidate count and stable candidate/reason evidence;
- trade/rejection accounting;
- deterministic metrics and subperiod breakdowns.

Repeated execution on the same code/data/configuration must produce byte-identical candidate serialization and deterministic benchmark/manifest bytes where the existing reporting contract promises byte determinism.

The complete experiment record must retain losing, rejected, and no-trade configurations. No row may be omitted because its result is unfavorable.

## 18. Error handling and fail-closed behavior

Fail closed for at least:

- unsupported pair/timeframe/split/configuration;
- final-test request;
- missing or mismatched processed manifest/schema/symbol;
- duplicate or out-of-order retained timestamps;
- missing cadence inside required SMA or three-bar stop context;
- missing exact 16:00-local scheduled-exit bar;
- non-positive or non-finite computed price/risk geometry;
- invalid actual-entry stop/target geometry after a gap;
- candidate/accounting identity mismatch across cost scenarios;
- benchmark artifact identity/digest mismatch.

No error path may fall back to source acquisition, raw reconstruction, alternate data, or relaxed final-test access.

## 19. Test strategy

Implementation must be test-first and include focused golden tests before broad regression.

Minimum strategy tests:

1. exact duration-to-bar-count mapping for 5m, 15m, 1h;
2. LONG trend context requires fast > slow and rising slow SMA;
3. SHORT context is exact inverse;
4. equality is neutral;
5. LONG pullback/resumption close-cross rule;
6. SHORT symmetric rule;
7. intrabar touch without close-cross does not trigger;
8. first qualifying signal only per London session;
9. no qualifying signal emits deterministic `NO_TRADE`;
10. three-bar LONG stop uses minimum midpoint low;
11. three-bar SHORT stop uses maximum midpoint high;
12. 1.0R/1.5R target arithmetic is exact;
13. missing rolling-context cadence fails closed;
14. missing three-bar stop context fails closed;
15. London DST maps signal/exit windows correctly;
16. signal cannot execute before true known time;
17. missing exact 16:00-local exit bar fails closed;
18. next-bar gap that invalidates geometry becomes a deterministic rejection;
19. candidate serialization is deterministic.

Minimum research/workflow tests:

20. exact six-point strategy grid;
21. exact 0.2/0.5/1.0 slippage grid;
22. candidate stream reused across costs;
23. final split rejected before loader/I/O;
24. accepted Phase 2 artifact identities are fixed and digest-verified before extraction;
25. workflow matrix is exactly 18 cells;
26. workflow permissions are read-only/minimal and contain no OIDC/Supabase/source/raw mutation surface;
27. deterministic benchmark artifact and manifest identity;
28. full regression suite remains green;
29. Phase 3 acceptance remains unchanged;
30. Phase 1 PR source-capable guards remain skipped under `[phase1-no-source]`.

## 20. Experiment assessment rules

The experiment must be evaluated from the complete 324-row evidence set, not by selecting the highest development return.

Candidate retention should emphasize:

- development-to-validation agreement;
- positive after-cost expectancy and profit factor above 1 at baseline cost;
- survival under 0.5-pip adverse-slippage stress;
- neighboring trend-window/target stability;
- adequate trade count;
- max drawdown and recovery behavior;
- calendar-year/subperiod consistency;
- dependence on a small number of top winners;
- cross-pair/timeframe support where present.

Severe 1.0-pip stress is diagnostic rather than a mandatory universal pass threshold, but failure under it must be recorded explicitly.

Any retained candidate is only a **serious Phase 4 research candidate**. It does not authorize final-test access, Phase 4 closure, Phase 5, broker integration, or real-money trading.

## 21. Repository-state updates during implementation

Before any result-producing merged-main benchmark runs:

- predeclare `EXP-20260914-002` in `docs/experiment-log.md` with status `PLANNED` and the exact frozen protocol;
- update `docs/project-state.md` to identify trend continuation as the active next family while preserving the frozen session-breakout candidate;
- add an approved decision-log entry freezing any family-specific semantics not already covered by DEC-018;
- preserve Phase 4 as ACTIVE, Phase 5 as UNSTARTED, and final-test touched as NO.

After the full merged-main matrix is complete and independently inspected, a separate evidence/state change may record PASS/FAIL/INCONCLUSIVE and any retained serious candidate. Result evidence must not be prewritten into the predeclaration.

## 22. Safety boundaries

Every post-Phase1 commit and PR title must contain `[phase1-no-source]`.

The implementation and benchmark must not:

- intentionally trigger Phase 1 acquisition;
- call Dukascopy or another external source;
- mutate `fmp-raw`;
- modify `docs/phase1-exact-gap-queue.json`;
- request GitHub OIDC or call Supabase for this Phase 4 benchmark;
- expose final-test data through the normal research API;
- start Phase 5;
- integrate a broker/live path;
- unlock real-money execution.

## 23. Completion boundary

This design is complete when the written spec is approved and translated into an implementation plan. Implementation completion is a later gate and requires green tests plus a separately reviewed merged-main benchmark/evidence cycle.

Phase 4 remains ACTIVE throughout this slice. The Phase 4 checkpoint is not created merely because the trend-continuation family completes.