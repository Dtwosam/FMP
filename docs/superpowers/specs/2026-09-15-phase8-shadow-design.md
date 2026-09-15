# Phase 8 Live Shadow Mode Design

**Status:** APPROVED DESIGN — pending written-spec review, Phase 7 checkpoint creation, source-of-truth activation, and implementation plan  
**Date:** 2026-09-15  
**Repository:** `Dtwosam/FMP`  
**Phase:** 8 — Live shadow mode  
**Proposed experiment:** `EXP-20260915-009`  
**Proposed decision:** `DEC-036`  
**Checkpoint target:** `fmp-v1-phase8-shadow`

## 1. Purpose and phase boundary

Phase 8 tests whether the sole Phase 7 survivor can operate against real-time forex quotes while preserving the research strategy, timing, decision, risk, and cost semantics closely enough to justify later demo-trading design.

The promotion path remains:

`historical research -> realistic backtest -> untouched OOS -> walk-forward -> shadow -> demo`

Shadow mode is observational and simulated only. It must be structurally unable to submit an order. Phase 8 does not authorize practice/demo order placement, production/live order placement, broker position mutation, or real-money trading. `DEC-008` remains unchanged.

Phase 8 has three sequential gates:

1. **connector qualification** — prove the chosen free Practice quote source is available and behaves as expected;
2. **implementation verification** — prove quote normalization, live-bar construction, strategy/risk parity, deterministic replay, and the structural no-order boundary;
3. **live shadow campaign** — collect enough real-time evidence to compare spreads, timing, operational reliability, and hypothetical outcomes with research assumptions.

Implementation completion is not Phase 8 PASS. Phase 8 PASS requires a completed live campaign satisfying Section 19.

## 2. Hard prerequisite: Phase 7 checkpoint

No Phase 8 runtime implementation may be merged or treated as an active protocol until lightweight tag:

`fmp-v1-phase7-walk-forward`

exists and resolves exactly to verified Phase 7 acceptance-closure commit:

`b6fb0176555b071fef6d1070edf3407b03cd60c9`

That SHA remains the Phase 7 checkpoint target even if later source-free bookkeeping commits exist on `main`.

This design may be reviewed before tag creation. Runtime implementation remains blocked until the tag is verifiably present at the exact SHA above.

## 3. Sole eligible strategy

Only the strategy promoted by `DEC-035` may enter Phase 8:

- strategy ID: `session_breakout`
- symbol: `USDJPY`
- provider instrument: `USD_JPY`
- signal timeframe: `15m`
- existing frozen London session semantics
- buffer: `5` pips
- target: `1.5` times the frozen session range
- exact flat time: existing `16:00 Europe/London` rule
- existing Phase 4 strategy implementation
- ML overlay: none

`volatility_breakout` is excluded because Phase 7 rejected it at Stage 1. No other pair, timeframe, parameter point, strategy, model, feature subset, or threshold may enter `EXP-20260915-009`.

## 4. Immutable upstream identity

Phase 8 evidence binds to:

- Phase 7 checkpoint target `fmp-v1-phase7-walk-forward` at `b6fb0176555b071fef6d1070edf3407b03cd60c9`;
- Phase 7 experiment `EXP-20260915-008` — PASS / PROMOTE;
- authoritative Phase 7 Stage 2 run `35015277625`;
- survivor USDJPY 15m `session_breakout`, buffer 5 pips, target 1.5x range;
- Phase 6 checkpoint `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`;
- accepted Phase 2 USDJPY artifact `10327600628`;
- accepted USDJPY artifact ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`;
- accepted USDJPY processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.

Any mismatch fails closed. No alternate historical artifact, strategy checkpoint, or data identity may be silently substituted.

## 5. Connector decision

### 5.1 Preferred connector: OANDA Practice pricing stream

The first connector candidate is the OANDA v20 **fxTrade Practice pricing stream**.

Official documentation reverified on 2026-09-15:

- `https://developer.oanda.com/rest-live-v20/development-guide/`
- `https://developer.oanda.com/rest-live-v20/pricing-ep/`
- `https://developer.oanda.com/rest-live-v20/authentication/`

The documentation distinguishes Practice and production hosts. The Practice streaming host is:

`https://stream-fxpractice.oanda.com`

The pricing stream is a `GET` endpoint whose response is newline-delimited JSON over a chunked stream. It emits `PRICE` and `HEARTBEAT` objects, documents five-second heartbeats, and provides at most four prices per second per requested instrument.

OANDA personal access tokens are not documented as quote-only credentials and may authorize broader account API access. Credential scope is therefore **not** the Phase 8 safety boundary. FMP's transport surface must make mutation paths unavailable.

### 5.2 Why MT5 is deferred

MetaTrader 5 remains a possible later integration, but its official Python package exposes both quote reads such as `symbol_info_tick()` and trading functions such as `order_send()`.

Reverified documentation:

- `https://www.mql5.com/en/docs/python_metatrader5`
- `https://www.mql5.com/en/docs/python_metatrader5/mt5symbolinfotick_py`
- `https://www.mql5.com/en/docs/python_metatrader5/mt5ordersend_py`

That API shape weakens the Phase 8 structural no-order proof. MT5 is not part of the initial implementation.

### 5.3 No provider fallback

If OANDA Practice is unavailable to the operator, incompatible with account jurisdiction, or fails qualification, Phase 8 records `CONNECTOR_UNAVAILABLE`, `INCONCLUSIVE`, or `CONNECTOR_REJECTED` as appropriate and stops.

There is no automatic fallback to MT5, OANDA production, or another vendor. A provider change requires a new approved design amendment and source-of-truth update.

## 6. Structural no-order boundary

The Phase 8 transport is a quote-source adapter, not a broker execution adapter.

Its runtime network surface supports exactly:

- method: `GET`
- host: `stream-fxpractice.oanda.com`
- path: `/v3/accounts/{account_id}/pricing/stream`
- instrument: exactly `USD_JPY`
- `snapshot=true`
- `includeHomeConversions=false`

There is:

- no caller-supplied base URL;
- no caller-supplied host;
- no caller-supplied HTTP method;
- no caller-supplied arbitrary path;
- no generic request function.

Phase 8 runtime code contains no order-placement, order-mutation, trade-close, position-mutation, or account-mutation endpoint; no `order_send`; no broker submission method; and no production OANDA host.

`stream-fxtrade.oanda.com` and `api-fxtrade.oanda.com` are forbidden in runtime code/configuration. Tests/docs may mention them only to prove rejection.

### 6.1 Secret handling

Credentials are supplied out of band through environment variables or equivalent local secret storage:

- OANDA Practice account ID;
- OANDA personal access token.

The token is never logged, persisted, committed, or included in exception text. The plain account ID is never written to durable Phase 8 evidence; evidence may store a SHA-256 account fingerprint for run binding.

Phase 8 does not call account-details, orders, trades, positions, or transaction endpoints.

## 7. Connector qualification spike

Before the full connector is frozen, a bounded qualification command validates the live interface without invoking strategy logic.

It:

- connects only to the exact Practice stream in Section 6;
- requests only `USD_JPY`;
- runs for at most ten minutes;
- may stop earlier only after at least 100 valid `PRICE` objects and 6 valid `HEARTBEAT` objects;
- records source/receive timestamps, heartbeat gaps, message counts, and bid/ask integrity diagnostics;
- records no strategy signal, decision, risk assessment, or hypothetical trade.

Qualification PASS requires:

- successful authentication/stream connection;
- at least 100 valid `PRICE` objects;
- at least 6 valid `HEARTBEAT` objects;
- only `USD_JPY` prices;
- at least one finite positive bid and ask on every accepted executable price;
- best bid <= best ask;
- UTC source timestamps that do not regress;
- no heartbeat/liveness gap greater than 15 seconds while the stream is active;
- no malformed or unknown message silently accepted;
- an audit proving the exact GET/Practice-host/path/instrument boundary.

If a market closure or low activity prevents the minimum sample without an integrity failure, the outcome is `INCONCLUSIVE`. Authentication/account availability failure is `CONNECTOR_UNAVAILABLE` unless evidence identifies an implementation defect.

## 8. Quote normalization

The parser accepts only `PRICE` and `HEARTBEAT` objects.

For each `PRICE`:

- best bid = maximum finite positive bid-ladder price;
- best ask = minimum finite positive ask-ladder price;
- ladder ordering is not trusted;
- provider source time is parsed as UTC;
- provider instrument must be `USD_JPY`.

`tradeable=true` is required for an executable/price-forming quote. A `PRICE` with `tradeable=false` may be preserved as an operational observation but cannot populate a complete bar, trigger entry/exit, or satisfy a quote deadline.

A price is invalid if either executable side is absent, non-finite, non-positive, crossed, or has the wrong instrument.

Provider liquidity, units-available fields, account state, and home conversions are not strategy inputs.

### 8.1 Ordering and receive metadata

Provider source time is authoritative for market ordering and bar labels.

Each runtime segment also records:

- `received_at_utc` for audit;
- a segment-local monotonic receive timestamp for liveness/latency measurement.

Monotonic values are never compared across process restarts.

Source-time regression fails closed for that stream segment. Exact duplicate prices may be deduplicated only when source time, instrument, best bid, best ask, and tradeable state are identical; conflicting duplicates are integrity failures.

## 9. Liveness and stale-data rules

OANDA documents five-second heartbeats. Phase 8 freezes:

- stream liveness timeout: `15` seconds since the last valid `PRICE` or `HEARTBEAT` receive event;
- entry quote deadline: `5` seconds after signal-known time;
- scheduled-exit quote deadline: `5` seconds after exact 16:00 `Europe/London` flat time.

A liveness timeout marks the stream stale, blocks new shadow entries, invalidates every bar interval crossed by the gap, and writes an operational event.

If a stale gap occurs while a hypothetical position is open, the system cannot know whether an unobserved stop/target crossing occurred. The trade becomes `OUTCOME_UNKNOWN_AFTER_GAP`, is excluded from financial acceptance metrics, and remains operational evidence.

No missing live path is reconstructed from historical candles or later quotes.

## 10. Live bars

Phase 8 creates **shadow-live** bid/ask bars from observed stream prices. They do not replace accepted historical data.

### 10.1 One-minute bars

A UTC minute bar:

- is left-labelled at minute start;
- uses observed best-bid OHLC and best-ask OHLC;
- contains only valid tradeable `PRICE` events in that minute;
- is complete only with at least one valid tradeable price and no stale interval intersecting the minute;
- is never created by forward-filling an earlier quote.

Heartbeats may advance/close elapsed buckets but never create a price observation.

### 10.2 Fifteen-minute bars

A 15-minute bar:

- is left-labelled like accepted Phase 2/4 bars;
- aggregates exactly 15 consecutive UTC one-minute bars;
- is complete only if every constituent minute is complete;
- preserves separate bid/ask OHLC;
- becomes knowable only at interval end.

This preserves the frozen timing bridge: observation label `T` represents `[T, T+15m)`, and signal-known time is `T+15m`.

### 10.3 No backfill

Phase 8 never calls OANDA candle-history endpoints to repair missing context.

If the process starts after required London-session context is missing, that London date is ineligible. The runner waits for a later fully observed date rather than backfilling, shortening windows, or fabricating bars.

## 11. Strategy, decision, and risk parity

Phase 8 calls the existing frozen `session_breakout` candidate generator with the exact Phase 7 configuration. It does not reimplement the strategy.

Existing candidate/decision contracts are reused where applicable. Risk sizing, per-trade cap, simultaneous-risk cap, UTC daily realized-loss halt, side conventions, JPY conversion rules, and adverse-slippage primitives are reused from Phase 3 rather than duplicated.

A live candidate is eligible only when:

- every required range/signal 15m bar is complete;
- it is the sole frozen USDJPY 15m configuration;
- signal-known time occurs while the stream is healthy;
- the first executable quote arrives within the five-second entry deadline.

Missing prerequisites become reasoned no-trade/invalidated-shadow events. There is no repair or retry rule that changes strategy eligibility.

## 12. Shadow-only execution simulation

Phase 8 creates a `ShadowIntent`/shadow-position record that is intentionally incompatible with a broker execution adapter.

It may carry simulation-only fields such as decision ID, direction, signal-known time, stop, target, scheduled flat time, simulated units/risk, and cost-scenario identity. It has no send/submit method.

### 12.1 Entry

The first valid tradeable `PRICE` at or after signal-known time and within five seconds is the hypothetical entry quote.

- LONG reference: best ask;
- SHORT reference: best bid;
- adverse slippage: existing Phase 3 primitive.

No valid quote by the deadline means no hypothetical position opens.

### 12.2 Stop/target

Subsequent valid prices use executable sides:

- LONG exits observe bid;
- SHORT exits observe ask.

A sampled quote gapping adversely through a stop uses the worse observed executable price subject to existing adverse-slippage semantics. A favorable jump beyond a target receives no improvement beyond the declared target.

Because OANDA's stream does not contain every market tick, missing-path inference is forbidden. Any stale gap while open invalidates the outcome.

### 12.3 Scheduled flat

At exact 16:00 `Europe/London`, the first valid tradeable quote within five seconds is the hypothetical time exit using the existing executable side and adverse-slippage semantics.

No valid quote by the deadline makes the outcome operationally invalid; the position is not silently extended.

## 13. Cost scenarios and virtual accounts

The same candidate sequence runs in parallel under:

- `0.2` pips adverse slippage/fill — gating;
- `0.5` pips/fill — gating;
- `1.0` pip/fill — diagnostic only.

Observed bid/ask spread is inherent in quote sides. Commission and financing remain zero for this mandatory-intraday-flat strategy.

Each scenario has an independent virtual account starting at exactly `$100,000` at accepted campaign start. Virtual equity carries forward within the campaign and uses unchanged Phase 3 risk policy. No virtual state connects to a broker account or real capital.

## 14. Restart behavior

Durable state is reconstructed from append-only evidence. A restart must never assume an unobserved market path.

If a restart means any required part of the current London date was missed:

- the date is invalid for new shadow entries;
- an open hypothetical position becomes `OUTCOME_UNKNOWN_AFTER_GAP`;
- capture may resume, but new candidates wait for a later fully observed London date.

Phase 8 performs no historical backfill, broker-position query, or order reconciliation.

## 15. Evidence architecture

Each live run writes append-only evidence containing:

1. accepted raw `PRICE`/`HEARTBEAT` stream objects plus receive metadata;
2. normalized quote events;
3. 1m and 15m shadow-live bars;
4. candidate/decision/no-trade/invalidation events;
5. per-cost-scenario shadow position/trade events;
6. operational connect/disconnect/stale/restart/rejection events;
7. a SHA-256 manifest binding run identity and files.

Raw evidence never includes request headers, tokens, or plain account IDs.

The manifest binds at minimum:

- code commit;
- Phase 7 checkpoint tag/SHA;
- Phase 7 experiment/outcome;
- frozen strategy config;
- connector protocol version;
- exact Practice host/path/instrument contract;
- account fingerprint;
- cost scenarios;
- Phase 3 risk identity;
- run start/end UTC;
- file SHA-256 values;
- replay-result digest.

## 16. Deterministic offline replay

Every accepted raw capture is replayable without network access.

Given identical captured provider messages and frozen configuration, replay must reproduce byte-identical derived artifacts for:

- normalized quotes;
- bars;
- candidates/decisions;
- shadow trade/outcome ledger;
- financial metrics.

Runtime receive timestamps remain operational evidence but are excluded from deterministic decision/financial serialization where they do not affect trading semantics.

Replay determinism is mandatory.

## 17. Frozen historical spread reference

Before live campaign start, Phase 8 creates one historical comparison artifact from accepted Phase 2/7 USDJPY data and the exact promoted strategy.

For each completed Phase 7 survivor trade used in the reference:

- **entry spread** = ask-open minus bid-open of the historical entry bar, converted to pips;
- **exit spread** = ask-open minus bid-open of the historical bar containing the recorded exit timestamp, converted to pips.

The reference stores trade count, median spread, 95th-percentile spread, exact upstream/code identity, and artifact SHA-256 for entry and exit distributions.

This reference is diagnostic/comparison evidence only. It cannot alter strategy parameters, timeframe, symbol, risk, or slippage scenarios. The reference method, digest, and parity thresholds are frozen before the first live campaign observation is admitted.

## 18. Campaign registration and minimum evidence

Before admitting the first scored live observation, the campaign writes a registration record containing:

- campaign start UTC and first London date;
- frozen code/reference identities;
- all acceptance thresholds in this design.

The start boundary cannot be moved after seeing results.

For operational coverage, every Monday-Friday London date from registered campaign start through acceptance-review cutoff enters the denominator, except a provider-documented full-market closure recorded before that date begins. A failed/outage date cannot be removed after observation.

Phase 8 is eligible for acceptance review only after:

- at least `40` completed financially scorable shadow trades at 0.2 pips;
- at least `8` elapsed calendar weeks between first and last accepted campaign observation;
- at least `30` London dates with complete required strategy observation coverage;
- every scored trade has a fully observed entry-to-exit path;
- all three cost scenarios cover the same candidate sequence.

If implementation is sound but these minimums are not reached, review outcome is `PHASE8_NEED_MORE_DATA`; Phase 8 remains active and Phase 9 stays locked.

## 19. Phase 8 acceptance gate

PASS requires every gate below.

### 19.1 Structural safety

- no runtime path can submit/mutate an order, trade, or position;
- exact Practice pricing-stream GET boundary is proven by tests/code inspection;
- production hosts are rejected;
- no generic method/base-URL/path surface exists;
- no token/plain account ID appears in durable artifacts;
- no demo/live execution adapter is imported/invoked.

A structural safety failure observed in acceptance evidence is `PHASE8_REJECT_SAFETY_FAILURE`.

### 19.2 Operational integrity

- connector qualification PASS;
- at least 30 fully observed London dates;
- at least `90%` of denominator dates defined in Section 18 remain valid for strategy evaluation;
- zero malformed provider messages silently accepted;
- zero stale-gap trades included in financial metrics;
- every disconnect/reconnect/stale event durably logged.

### 19.3 Timing

During scored campaign evidence:

- p99 local processing latency from accepted message receipt to completion of normalized-event durable append is <= `250 ms`;
- every scored entry quote is <= `5` seconds after signal-known time;
- every scored scheduled exit quote is <= `5` seconds after exact 16:00 `Europe/London`.

Deadline-violating trades are invalid and cannot count toward minimum sample.

### 19.4 Spread parity

Against the frozen Section 17 reference:

- live median entry spread <= historical median entry spread + `0.5` pip;
- live p95 entry spread <= historical p95 entry spread + `0.5` pip;
- live median exit spread <= historical median exit spread + `0.5` pip;
- live p95 exit spread <= historical p95 exit spread + `0.5` pip.

The 0.5-pip tolerance is an operational mismatch bound, not a strategy parameter, and cannot widen after campaign start.

### 19.5 Hypothetical financial behavior

At both 0.2 and 0.5 pips adverse slippage/fill:

- net return > 0;
- expectancy/completed trade > 0;
- profit factor > 1.0;
- maximum drawdown fraction <= 0.05.

The 0.2-pip scenario must contain at least 40 completed scorable trades.

The 1.0-pip scenario remains diagnostic and may be negative without independently reversing a PASS, matching Phase 7 treatment.

### 19.6 Replay

The accepted campaign must replay offline into byte-identical deterministic derived artifacts and identical acceptance metrics.

Replay mismatch prevents PASS and requires defect correction plus fresh valid evidence; the failed evidence remains retained.

## 20. Review outcomes

A Phase 8 review records exactly one outcome:

- `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN`
- `PHASE8_NEED_MORE_DATA`
- `PHASE8_REJECT_OPERATIONAL_MISMATCH`
- `PHASE8_REJECT_MARKET_MISMATCH`
- `PHASE8_REJECT_FINANCIAL_MISMATCH`
- `PHASE8_REJECT_SAFETY_FAILURE`

`PHASE8_NEED_MORE_DATA` is explicitly non-terminal: Phase 8 stays ACTIVE and the same frozen campaign protocol may continue accumulating evidence.

PASS makes the unchanged strategy eligible for a separate Phase 9 design only. It does not authorize demo orders.

## 21. Required tests

Implementation tests cover at least:

- exact Practice host/path/GET/instrument/query contract;
- rejection of production hosts, arbitrary URLs/methods/instruments and order/trade/position paths;
- token/account redaction;
- line-delimited `PRICE`/`HEARTBEAT` parsing;
- `tradeable=false` exclusion from executable quotes/bars;
- best-bid=max / best-ask=min independent of ladder ordering;
- invalid/missing/non-positive/crossed quote rejection;
- source-time regression and duplicate handling;
- 15-second stale timeout;
- no bar forward-fill;
- exact 1m/15m left-labelled boundaries;
- incomplete/stale constituents invalidating 15m bars;
- London DST through existing strategy/session logic;
- exact frozen session-breakout config;
- no candidate from incomplete context;
- five-second entry/exit deadlines;
- long/short executable-side rules;
- adverse stop gap and no favorable target improvement;
- stale gap invalidating open shadow outcome;
- unchanged Phase 3 risk/JPY sizing semantics;
- independent 0.2/0.5/1.0 virtual accounts;
- restart without backfill/hidden continuation;
- deterministic replay;
- evidence-manifest SHA binding;
- exact acceptance boundaries for sample size, coverage, timing, spread, profitability, PF, and drawdown;
- repository-level guard proving no Phase 8 order-submission surface.

Existing Phase 1–7 regression tests and normal historical-data locks remain green.

## 22. Operational deployment boundary

Phase 8 is an explicitly started local/authorized process using free infrastructure. It does not require paid hosting, paid data, a dashboard, or an always-on cloud service.

GitHub Actions may run source-free unit/replay tests, but the long-running live campaign is not an implicit CI side effect. Live qualification/campaign execution requires explicit credentials and operator action.

The software may be restartable; evidence exists only while the operator actually runs it. No assistant/background-service assumption is part of the protocol.

## 23. Source-of-truth activation before runtime code

After written-spec approval and after the Phase 7 checkpoint prerequisite is satisfied, activation must:

1. add `DEC-036` freezing this Phase 8 protocol;
2. add planned `EXP-20260915-009`;
3. update `docs/project-state.md` to Phase 8 ACTIVE;
4. update `docs/source-register.md` with the 2026-09-15 OANDA/MT5 reverification and selected OANDA Practice quote role;
5. preserve `DEC-008` and all demo/live/real-money locks;
6. commit source-of-truth activation before runtime implementation.

## 24. Non-goals

Phase 8 excludes:

- any OANDA order submission or mutation;
- OANDA production/live hosts;
- MT5 integration in the initial implementation;
- account/order/trade/position synchronization;
- demo or real-money trading;
- real broker fill measurement;
- REST candle backfill;
- strategy retuning or parameter search;
- other pairs/timeframes;
- portfolio/correlation expansion;
- ML/model training;
- economic-calendar filtering;
- dashboards;
- paid infrastructure/data;
- tick-perfect reconstruction;
- automatic provider failover.

## 25. Change control

Once `DEC-036` activates the protocol, changing any of the following after campaign registration requires a new decision and experiment rather than editing `EXP-20260915-009` in place:

- strategy/pair/timeframe/parameters;
- provider/environment;
- host/path/method/instrument boundary;
- stale thresholds;
- entry/exit deadlines;
- bar-completeness semantics;
- slippage/risk settings;
- historical-reference method;
- sample minimums;
- coverage/timing/spread thresholds;
- financial gates.

Negative and inconclusive evidence remains recorded.

## 26. Completion conditions

Runtime implementation may start only after:

- this written design is explicitly approved;
- `fmp-v1-phase7-walk-forward` exists at `b6fb0176555b071fef6d1070edf3407b03cd60c9`;
- an implementation plan is written from this design;
- source-of-truth activation is committed.

Phase 8 itself reaches a terminal state only with:

- `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN`, or
- one of the four `PHASE8_REJECT_*` outcomes.

`PHASE8_NEED_MORE_DATA` is non-terminal and keeps Phase 8 ACTIVE.

Only `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN` may unlock Phase 9 design. It never authorizes demo execution by itself.
