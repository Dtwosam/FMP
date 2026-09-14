# Phase 4 Session High/Low Sweep-Rejection Baseline Design

**Date:** 2026-09-14  
**Status:** APPROVED IN CHAT — written-spec review pending  
**Repository:** `Dtwosam/FMP`  
**Base commit:** `91ff33830032c3de74af5d2759fa4cdff3b6ec2b`  
**Phase:** Phase 4 — Baseline Strategy Research  
**Experiment:** `EXP-20260914-006`  
**Decision:** `DEC-026` (to be formalized only after written-spec approval)

## 1. Objective

The sixth sequential Phase 4 family is a deterministic session high/low sweep-rejection baseline. It tests the opposite short-horizon hypothesis to EXP-001 while deliberately reusing EXP-001's frozen 00:00–08:00 `Europe/London` reference range: instead of asking whether a confirmed range breakout continues, EXP-006 asks whether a penetration beyond that same range boundary followed by a close back inside the range tends to revert toward the range midpoint strongly enough to overcome historical BID/ASK spread and adverse slippage under the accepted Phase 3 execution and risk model.

No profitability is assumed. A failed family is a valid research outcome and remains evidence.

This design does not modify either promoted serious Phase 4 candidate, does not reopen any rejected EXP-002/003/004 parameter surface, does not retune EXP-005, does not unlock the final-test split, does not start Phase 5, and does not authorize broker/live or real-money trading.

## 2. Governing source-of-truth decisions

This family is subordinate to the existing approved rules.

- DEC-018 remains authoritative for the chronological split, final-test isolation, left-labelled timing bridge, source-free research boundary, historical BID/ASK execution, shared cost model, and accepted Phase 3 risk controls.
- DEC-025 remains authoritative for the closed EXP-005 PASS / PROMOTE outcome and leaves both serious candidates frozen unchanged.
- DEC-008 remains unchanged: real-money trading is locked.
- The approved baseline-first family order remains session breakout, trend continuation, mean reversion, previous-day high/low rejection, volatility breakout, then session high/low sweep/rejection.

## 3. Chosen formulation and rejected alternatives

The admitted formulation is an **Asian-range sweep/rejection** using the exact 00:00–08:00 `Europe/London` range already used by EXP-001.

Two alternatives are explicitly outside EXP-006:

1. **London-morning range sweep/rejection** — rejected for this experiment because it introduces a new session boundary and weakens direct comparability with EXP-001.
2. **Multiple reference sessions in one grid** — rejected because it doubles a structural degree of freedom after five prior families and would make a fragile single-session optimum harder to interpret.

Reusing the EXP-001 range is preferred because EXP-006 then becomes a direct failed-breakout/rejection counterpart to the existing continuation hypothesis with a bounded three-point penetration grid.

## 4. Eligible universe

Pairs:

- EURUSD;
- GBPUSD;
- USDJPY.

Signal timeframes:

- 5m;
- 15m;
- 1h.

Canonical 1m remains the origin of Phase 2 derived bars but is not an eligible signal timeframe for this experiment.

Each pair/timeframe is benchmarked independently. Cross-symbol signals, portfolio optimization, and correlation-based sizing are outside EXP-006.

## 5. Chronological split and final-test lock

The frozen Phase 4 chronology is unchanged.

- **Development:** 2015-01-01 through 2020-12-31 inclusive.
- **Validation:** 2021-01-01 through 2023-12-31 inclusive.
- **Final untouched test:** 2024-01-01 through 2026-08-20 inclusive.

Normal EXP-006 tooling must reject any final-split request before loading market data.

No final-test observation is permitted under EXP-006. Final access remains reserved for a later explicit cross-family promotion gate after baseline candidate selection is materially complete.

## 6. Price series and timing contract

### 6.1 Analytical price

Signal analysis uses midpoint OHLC only:

- `mid_high = (bid_high + ask_high) / 2`;
- `mid_low = (bid_low + ask_low) / 2`;
- `mid_close = (bid_close + ask_close) / 2`.

BID/ASK values remain untouched and remain the sole executable-price source inside Phase 3.

### 6.2 Left-labelled bar timing

Phase 2 derived bars are left-labelled. For a bar labelled `T` with timeframe width `W`:

- observation label: `T`;
- signal-known time: `T + W`;
- Phase 3 decision timestamp: `T`;
- earliest executable timestamp: `T + W`.

No signal may execute on its own observation bar.

### 6.3 London-local clock

All session boundaries use the named timezone `Europe/London` with timezone-aware/DST-aware conversion. Hard-coded seasonal UTC offsets are forbidden.

## 7. Frozen reference session

For each London-local trading date, define the reference session exactly as:

`[00:00, 08:00) Europe/London`

at the tested signal timeframe.

The full session must contain every expected left-labelled bar at exact cadence and every required midpoint OHLC value must be finite. Missing, duplicate, malformed, or non-finite reference data fails closed. The reference is never shortened, interpolated, backfilled, or repaired.

Reference levels are:

- `reference_high = max(mid_high)` over the full reference session;
- `reference_low = min(mid_low)` over the full reference session;
- `reference_midpoint = (reference_high + reference_low) / 2`.

A valid reference requires finite values and `reference_high > reference_low`. Zero or negative range fails closed.

The reference high, low, and midpoint are frozen before the first eligible signal observation for that London date and never change later that date.

## 8. Signal-session completeness

Eligible current observation labels are 08:00 through 14:00 inclusive in `Europe/London`.

The exact mandatory flat timestamp is 16:00 London local time.

For a London date/configuration to be tradable:

- the frozen 00:00–08:00 reference must be complete;
- every required signal-session bar from the immediately preceding bar needed for the first 08:00 comparison through the 14:00 observation must preserve exact timeframe cadence wherever evaluated;
- the exact 16:00 exit bar must exist;
- required midpoint values must be finite.

At an 08:00 observation, the immediately preceding bar may be before the eligible signal window (for example 07:55 on 5m) and may also belong to the frozen reference session. It is used only as the previous-close state required by the rejection rule, not as an independently eligible signal.

Completeness failures fail closed with deterministic reasoned no-trade evidence wherever a valid timestamp can be represented. A complete date with no qualifying setup emits deterministic `NO_SESSION_SWEEP_REJECTION` evidence.

## 9. Frozen penetration grid

Penetration buffers are exactly:

- 0 pips;
- 2 pips;
- 5 pips.

The symbol-specific pip size is the existing accepted Phase 3/research pip definition.

These are the only strategy configurations under EXP-006. No additional buffer, percentage-of-range buffer, ATR buffer, or volatility-scaled buffer may be added after results are observed.

## 10. Sweep-rejection signal

The setup is a boundary penetration followed by a close back inside the frozen session range.

Let `b` be the configured penetration buffer in price units.

### 10.1 SHORT high sweep/rejection

SHORT requires all of:

1. immediately previous fully closed midpoint close `<= reference_high`;
2. current midpoint high `>= reference_high + b`;
3. current midpoint close `< reference_high`.

The current close must be strictly back inside the range. Merely touching the high on the close does not qualify.

### 10.2 LONG low sweep/rejection

LONG requires all of:

1. immediately previous fully closed midpoint close `>= reference_low`;
2. current midpoint low `<= reference_low - b`;
3. current midpoint close `> reference_low`.

The current close must be strictly back inside the range. Merely touching the low on the close does not qualify.

### 10.3 Zero-buffer interpretation

At 0 pips, touching or exceeding the boundary intrabar satisfies the penetration leg, but the close-back-inside leg remains strict. Therefore a bar that only closes on the boundary is not a rejection.

### 10.4 Dual-side ambiguity

A malformed or extremely wide current bar can satisfy both the LONG and SHORT sweep predicates. Such a bar fails closed as deterministic `AMBIGUOUS_DUAL_SESSION_SWEEP` evidence. Direction is never selected heuristically.

### 10.5 One signal per London date/configuration

Only the first qualifying directional sweep/rejection for a symbol/configuration on a London-local date may become a candidate.

After the first qualifying directional signal is emitted, all later signals that date for that configuration are ignored regardless of whether Phase 3 later rejects the order for geometry/risk or the trade exits by stop, target, or mandatory flat. There is no same-day retry.

## 11. Frozen stop and target geometry

Geometry is frozen from the signal bar and frozen session reference before executable entry.

### 11.1 LONG

- stop = signal-bar midpoint low;
- target = frozen `reference_midpoint`.

### 11.2 SHORT

- stop = signal-bar midpoint high;
- target = frozen `reference_midpoint`.

### 11.3 Signal-time validity

At signal time, a valid LONG requires `stop < signal_mid_close < target`. A valid SHORT requires `target < signal_mid_close < stop`.

Any signal-time violation becomes deterministic non-tradable evidence rather than a repaired order.

Actual next-bar BID/ASK entry remains authoritative. If the executable entry makes the frozen stop/target invalid, Phase 3 rejects it with existing `INVALID_STOP_TARGET` semantics. Strategy/research code must not move the stop, move the target, widen risk, chase the entry, or retry later.

The target remains the frozen session midpoint even if later price action changes the day's extrema.

## 12. Mandatory intraday exit

Every directional candidate declares the exact 16:00 `Europe/London` flat timestamp for its London date.

Execution remains owned by Phase 3. Missing exact exit data fails closed; the scheduled exit is never shifted to another bar.

Existing Phase 3 executable-side and adverse-slippage semantics remain unchanged.

## 13. Frozen parameter grid and benchmark matrix

Strategy configurations per pair/timeframe are exactly:

| Penetration buffer |
| ---: |
| 0 pips |
| 2 pips |
| 5 pips |

Cost scenarios remain exactly:

- 0.2 pips adverse slippage per fill;
- 0.5 pips adverse slippage per fill;
- 1.0 pip adverse slippage per fill.

The result-producing benchmark is fixed at:

- 3 pairs;
- 3 timeframes;
- 2 chronological splits;
- 3 penetration buffers;
- 3 cost scenarios.

Workflow cells:

`3 × 3 × 2 = 18`

Configuration rows:

`18 × 3 × 3 = 162`

For each fixed pair/timeframe/split/buffer, alpha candidates are generated exactly once. Candidate bytes, candidate count, and reason-count breakdown must be identical across all three cost scenarios.

Changing costs must not regenerate or mutate candidates.

## 14. Cost and risk assumptions

Historical BID/ASK spread remains inherent in the supplied bars and Phase 3 fills.

Commission: zero.  
Financing: zero.

Accepted Phase 3 risk settings remain unchanged:

- requested risk/trade: 0.25% of realized risk equity;
- hard maximum risk/trade: 0.50%;
- maximum simultaneous reserved open risk: 1.00%;
- daily realized-loss halt: 1.50% of UTC day-start realized risk equity.

Strategy code never sizes positions and never computes executable fills.

## 15. Experiment identity and deterministic artifacts

The experiment is `EXP-20260914-006 — Session high/low sweep-rejection baseline`.

Every result artifact must bind at least:

- experiment/protocol identity;
- exact merged-main code commit;
- accepted Phase 2 processed-manifest SHA-256;
- canonical schema version;
- pair and timeframe;
- split name and exact boundaries;
- penetration buffer;
- frozen reference-session identity;
- candidate SHA-256/count/reason counts;
- adverse slippage;
- commission/financing identity;
- unchanged Phase 3 risk configuration;
- starting equity;
- deterministic backtest run identity;
- research metrics and required breakdowns.

Artifacts and inner manifests must follow the existing deterministic Phase 4 pattern with hash/size verification. Runtime clock, hostname, UUID, process metadata, or unbound local paths remain forbidden from deterministic evidence.

## 16. Frozen promotion screen

At 0.2-pip adverse slippage, the **same penetration buffer** must satisfy all three conditions on both development and validation:

- net return > 0;
- expectancy/trade > 0;
- profit factor > 1.

Development-only or validation-only winners are not serious candidates.

Only baseline survivors proceed to the established downstream review:

- 0.5-pip cost robustness;
- neighboring-buffer stability;
- calendar-year/subperiod concentration;
- sample size appropriate to the observed frequency;
- fixed-risk maximum drawdown;
- top-winner dependence/outlier concentration;
- absence of leakage or timing defects.

The 1.0-pip scenario remains diagnostic rather than a universal mandatory promotion condition.

A narrow isolated winner without defensible robustness may be rejected, as already demonstrated by EXP-004. No post-result grid expansion or rescue rule is permitted under EXP-006.

## 17. Relationship to prior Phase 4 families

EXP-006 is deliberately constrained to preserve interpretability.

- **Versus EXP-001 session breakout:** same frozen 00:00–08:00 London range, but EXP-001 requires a close beyond the range for continuation while EXP-006 requires intrabar penetration followed by a strict close back inside for rejection toward the range midpoint.
- **Versus EXP-004 previous-day rejection:** EXP-004 uses the most recent completed New-York-close FX session as its reference and therefore tests a different temporal level structure. EXP-006 uses the same-day 00:00–08:00 London range.
- **Versus EXP-005 volatility breakout:** EXP-005 uses a moving preceding-8h rolling channel and contemporaneous range expansion. EXP-006 uses one frozen session range per London date and no volatility-expansion filter.

Results from prior families must not be used to alter the EXP-006 buffer grid, target, stop, session boundaries, signal window, or retry behavior.

## 18. Source-free and safety boundary

EXP-006 may consume only accepted Phase 2 processed artifacts through the existing read-only research path.

The implementation and benchmark must not:

- request Dukascopy or another upstream source;
- invoke Phase 1 acquisition commands;
- mutate `fmp-raw`;
- write through `fmp-raw-read`;
- modify Phase 1 gap/acquisition state;
- use Phase 1 acquisition credentials;
- access the final-test split;
- add broker/live integration;
- unlock real-money trading.

All post-Phase1 commits and PR titles retain `[phase1-no-source]`.

## 19. Intended module boundaries after written-spec approval

Implementation, only after written-spec approval and an implementation plan, should follow existing Phase 4 family boundaries.

### `fmp.strategies.session_sweep_rejection`

Owns deterministic setup logic only:

- config validation;
- London reference/session label construction;
- midpoint reference high/low/midpoint;
- completeness and finite-data checks;
- penetration/rejection classification;
- ambiguity fail-closed behavior;
- first-signal-per-date behavior;
- frozen stop/target geometry;
- deterministic `SignalCandidate` generation and metadata.

It does not load storage, size positions, apply costs, simulate fills, or write experiment conclusions.

### `fmp.research.session_sweep_rejection`

Owns research orchestration only:

- frozen development/validation split enforcement;
- accepted Phase 2 processed-artifact loading;
- deterministic candidate generation/reuse across costs;
- Phase 3 execution invocation;
- metrics, subperiod, drawdown, and winner-concentration reporting;
- deterministic artifact/manifest construction.

It must reject final-test requests before loading data.

### CLI and workflow

A dedicated source-free EXP-006 CLI/workflow should mirror the established Phase 4 matrix pattern, bind the exact merged-main SHA plus accepted processed-manifest identity, and upload one deterministic evidence artifact per pair/timeframe/split cell.

## 20. Test requirements before any result-producing benchmark

At minimum, tests must prove:

- exact 00:00–08:00 London reference labels for 5m/15m/1h;
- DST-safe London/UTC conversion;
- complete reference required; missing/malformed/non-finite data fails closed;
- reference high/low/midpoint calculations use midpoint quotes only;
- exact 0/2/5-pip buffer validation, including USDJPY pip size;
- SHORT high-sweep predicate including strict close-back-inside behavior;
- LONG low-sweep predicate including strict close-back-inside behavior;
- zero-buffer boundary-touch interpretation;
- dual-side ambiguity fails closed;
- previous-bar requirement at the 08:00 boundary;
- eligible current observations only from 08:00 through 14:00 London;
- only first qualifying signal per date/configuration is emitted;
- a later Phase 3 rejection does not permit retry;
- signal-bar extreme stop and frozen session-midpoint target;
- next-bar executable geometry is never repaired;
- exact 16:00 London mandatory flat and missing exit fails closed;
- deterministic `NO_SESSION_SWEEP_REJECTION` evidence for complete no-setup dates;
- candidate bytes are identical across 0.2/0.5/1.0-pip cost scenarios;
- benchmark grid is exactly 162 rows;
- final split is rejected before data loading;
- deterministic repeated artifact bytes/manifests;
- source-free workflow guards remain effective.

No authoritative EXP-006 benchmark may run until these requirements and the existing full unit/YAML/compile/Phase 3 verification are green on the result-producing implementation path.

## 21. Completion criteria for the design gate

This written design is complete only when the user reviews and approves this exact spec. After that approval:

1. formalize DEC-026 and the EXP-006 predeclaration on a source-free documentation change;
2. create a test-first implementation plan;
3. implement on a separate branch from then-current `main`;
4. verify full tests/YAML/compile and unchanged Phase 3 acceptance;
5. merge implementation with `[phase1-no-source]`;
6. run the authoritative 18-cell / 162-row development-and-validation benchmark only from merged `main`;
7. independently audit all artifacts before applying the frozen promotion screen;
8. record PASS/FAIL evidence without retuning;
9. keep the final-test split, Phase 5, broker/live integration, and real-money trading locked unless a later explicit gate changes them.
