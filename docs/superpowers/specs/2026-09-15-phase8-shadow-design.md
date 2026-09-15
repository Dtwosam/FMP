# Phase 8 Live Shadow Mode Design

**Status:** APPROVED DESIGN — pending written-spec review, Phase 7 checkpoint creation, source-of-truth decision record, and implementation plan  
**Date:** 2026-09-15  
**Repository:** `Dtwosam/FMP`  
**Phase:** 8 — Live shadow mode  
**Proposed experiment:** `EXP-20260915-009`  
**Proposed decision:** `DEC-036`  
**Checkpoint target:** `fmp-v1-phase8-shadow`

## 1. Purpose

Phase 8 determines whether the sole Phase 7 survivor can operate against real-time forex quotes while preserving the research strategy, decision, risk, and cost semantics closely enough to justify later demo-trading design.

The Phase 8 promotion path remains:

`historical research -> realistic backtest -> untouched OOS -> walk-forward -> shadow -> demo`

Shadow mode is observational and simulated only. It must be structurally unable to submit an order. Phase 8 does not authorize practice/demo order placement, production/live order placement, real-money trading, broker position mutation, or any relaxation of `DEC-008`.

The phase has three sequential gates:

1. **connector qualification** — prove a free live/practice quote source is available and its read-only transport behaves as expected;
2. **shadow implementation verification** — prove quote normalization, bar construction, strategy/decision/risk parity, deterministic replay, and structural no-order safety;
3. **live shadow campaign** — collect enough real-time evidence to compare spreads, timing, hypothetical outcomes, and operational reliability with research assumptions.

Implementation completion is not Phase 8 PASS. Phase 8 PASS requires a completed live shadow campaign meeting the frozen acceptance gate in this document.

## 2. Hard prerequisite: Phase 7 checkpoint

No Phase 8 runtime implementation may be merged or treated as an active Phase 8 protocol until lightweight checkpoint tag:

`fmp-v1-phase7-walk-forward`

exists and resolves exactly to verified Phase 7 acceptance-closure commit:

`b6fb0176555b071fef6d1070edf3407b03cd60c9`

That commit is the Phase 7 acceptance boundary. Later no-op/bookkeeping commits do not replace the checkpoint target.

The design document itself may be reviewed before the tag exists. Runtime implementation remains blocked until the tag is verifiably present at the exact SHA above.

## 3. Sole eligible strategy

Only the strategy promoted by `DEC-035` may enter Phase 8:

- strategy ID: `session_breakout`
- symbol: `USDJPY`
- live-provider instrument: `USD_JPY`
- signal timeframe: `15m`
- London range: existing frozen Phase 4 session-breakout semantics
- buffer: `5` pips
- target: `1.5` times the frozen session range
- exact flat time: existing `16:00 Europe/London` rule
- strategy version: existing frozen Phase 4 implementation
- ML overlay: none

`volatility_breakout` is not eligible. It was rejected at Phase 7 Stage 1 and must not appear in Phase 8 candidate selection, fallback, rescue, or comparison logic.

No other pair, timeframe, parameter point, model, feature subset, threshold, or strategy family may enter `EXP-20260915-009`.

## 4. Immutable upstream identities

Phase 8 must bind its evidence to the accepted upstream chain:

- Phase 7 checkpoint target: `fmp-v1-phase7-walk-forward` at `b6fb0176555b071fef6d1070edf3407b03cd60c9`;
- Phase 7 experiment: `EXP-20260915-008` — PASS / PROMOTE;
- Phase 7 authoritative Stage 2 run: `35015277625`;
- Phase 7 survivor: USDJPY 15m `session_breakout`, 5-pip buffer, 1.5x target range;
- Phase 6 checkpoint: `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`;
- accepted Phase 2 USDJPY artifact ID: `10327600628`;
- accepted Phase 2 USDJPY artifact ZIP SHA-256: `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`;
- accepted USDJPY processed-manifest SHA-256: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.

A mismatch fails closed. Phase 8 must not silently substitute another historical artifact, strategy checkpoint, or data identity.

## 5. Connector choice and qualification

### 5.1 Preferred connector

The first connector candidate is **OANDA v20 fxTrade Practice pricing stream**.

Official documentation was reverified on 2026-09-15:

- development guide: `https://developer.oanda.com/rest-live-v20/development-guide/`
- pricing stream: `https://developer.oanda.com/rest-live-v20/pricing-ep/`
- authentication: `https://developer.oanda.com/rest-live-v20/authentication/`

The documentation distinguishes Practice and production REST/streaming hosts. The Practice streaming host is:

`https://stream-fxpractice.oanda.com`

The pricing stream is a `GET` endpoint, emits `PRICE` objects plus `HEARTBEAT` objects, sends heartbeats every five seconds, and provides at most four prices per second per requested instrument.

OANDA personal access tokens are not documented as quote-only credentials and may authorize broader account API access. Therefore credential scope is **not** the Phase 8 safety boundary. The FMP transport itself must make mutation paths unavailable.

### 5.2 Why MT5 is not the first connector

MetaTrader 5 remains a possible later integration, but its official Python package exposes both quote reads such as `symbol_info_tick()` and trading functions such as `order_send()`.

Official documentation reverified on 2026-09-15:

- Python integration: `https://www.mql5.com/en/docs/python_metatrader5`
- quote read: `https://www.mql5.com/en/docs/python_metatrader5/mt5symbolinfotick_py`
- order submission: `https://www.mql5.com/en/docs/python_metatrader5/mt5ordersend_py`

That API shape makes the structural no-order proof weaker than a dedicated OANDA Practice pricing-only transport. MT5 is therefore not part of the initial Phase 8 implementation.

### 5.3 No silent provider fallback

If OANDA Practice access is unavailable to the operator, incompatible with the account jurisdiction, or fails the connector qualification gate, Phase 8 records `CONNECTOR_UNAVAILABLE` or `CONNECTOR_REJECTED` and stops.

The implementation must not automatically switch to MT5, production OANDA, another broker, or another data vendor. A provider change requires a new approved design amendment and source-register/decision-log update before implementation.

## 6. Structural no-order boundary

The Phase 8 OANDA transport is a quote-source adapter, not a broker execution adapter.

Its public surface may support exactly one network operation:

- HTTP method: `GET`
- host: `stream-fxpractice.oanda.com`
- path template: `/v3/accounts/{account_id}/pricing/stream`
- instrument query: exactly `USD_JPY`
- `includeHomeConversions=false`
- no caller-supplied base URL
- no caller-supplied host
- no caller-supplied HTTP method
- no caller-supplied arbitrary path

The adapter must expose no generic request function.

The Phase 8 runtime package must contain no order-placement endpoint, order mutation endpoint, trade-close endpoint, position mutation endpoint, account mutation endpoint, `order_send`, broker `OrderIntent` submission method, or production OANDA host.

A token may have broader server-side rights, but Phase 8 code must have no route or API surface that can exercise them.

### 6.1 Forbidden production host

`stream-fxtrade.oanda.com` and `api-fxtrade.oanda.com` are forbidden in Phase 8 runtime code and configuration.

Documentation/tests may mention these strings only when proving they are rejected. No CLI/environment option may select them.

### 6.2 Secret handling

Required secrets/configuration are supplied out of band through environment variables or equivalent local secret storage:

- OANDA Practice account ID;
- OANDA personal access token.

The token must never be printed, persisted, included in artifacts, included in exception text, or committed to Git.

The plain account ID must not be written to durable Phase 8 evidence. Durable evidence may store a one-way SHA-256 fingerprint for run binding.

## 7. Connector qualification spike

Before the full OANDA adapter is frozen as the Phase 8 quote source, a bounded qualification command validates the live interface without invoking strategy logic.

### 7.1 Qualification scope

The spike:

- connects only to the exact Practice pricing stream defined above;
- requests only `USD_JPY`;
- runs for at most ten minutes;
- stops earlier after collecting at least 100 valid `PRICE` objects and at least 6 valid `HEARTBEAT` objects;
- records counts, source timestamps, receive timestamps, heartbeat gaps, and bid/ask sanity diagnostics;
- records no strategy signal, decision, risk assessment, or hypothetical trade.

### 7.2 Qualification PASS

Connector qualification is PASS only if:

- authentication and streaming connection succeed;
- at least 100 valid `PRICE` objects are observed;
- at least 6 valid `HEARTBEAT` objects are observed;
- all accepted prices are for `USD_JPY`;
- every accepted price has at least one positive bid and one positive ask;
- best bid is less than or equal to best ask;
- source timestamps parse as UTC and do not regress;
- no heartbeat gap exceeds 15 seconds while the connection is otherwise active;
- zero malformed or unexpected message types are silently accepted;
- the transport audit proves the exact host/path/method/instrument boundary.

If the market is closed or the bounded run cannot accumulate the minimum live sample without an integrity failure, the outcome is `INCONCLUSIVE`, not a fabricated PASS.

An authentication/account-availability failure is `CONNECTOR_UNAVAILABLE` unless evidence shows an implementation defect.

## 8. Live quote normalization

### 8.1 Accepted stream objects

The adapter accepts only:

- `PRICE`;
- `HEARTBEAT`.

Unknown message types fail closed for that connection and produce an operational event.

### 8.2 Best bid/ask

For each `PRICE` object:

- best bid = maximum finite positive price in the bid ladder;
- best ask = minimum finite positive price in the ask ladder.

The implementation must not depend on provider array ordering.

A price is invalid when either side is absent, non-finite, non-positive, or when best ask is below best bid.

Provider liquidity, account-unit availability, home conversions, and account trading state are not inputs to the Phase 8 strategy.

### 8.3 Timestamp rules

The provider source timestamp is authoritative for market-time ordering and bar labels.

A local monotonic receive timestamp is recorded separately for liveness and processing-latency diagnostics.

Source timestamp regression fails closed for the active stream session. Exact duplicate `PRICE` records may be deduplicated only when source timestamp, instrument, best bid, and best ask are identical; conflicting duplicates are integrity failures.

## 9. Liveness and stale-data rules

OANDA documents five-second heartbeats. Phase 8 therefore freezes:

- stream liveness timeout: `15` seconds since the last valid `PRICE` or `HEARTBEAT` receive event;
- entry quote deadline: first valid `PRICE` must arrive within `5` seconds after signal-known time;
- scheduled-exit quote deadline: first valid `PRICE` must arrive within `5` seconds after the exact 16:00 `Europe/London` flat time.

A liveness timeout marks the stream `STALE`, blocks new shadow entries, invalidates any bar interval crossed by the gap, and records an operational event.

If a stale gap occurs while a hypothetical position is open, the system cannot know whether an unobserved stop/target crossing occurred. That hypothetical trade becomes `OUTCOME_UNKNOWN_AFTER_GAP`, is excluded from financial acceptance metrics, and counts as an operationally invalidated trade.

The runner does not reconstruct a missing live path from historical candles or later quotes.

## 10. Live 1-minute and 15-minute bars

Phase 8 constructs live bid/ask bars from observed pricing-stream events. These are **shadow-live bars**, not replacements for the accepted historical canonical dataset.

### 10.1 One-minute bars

A UTC minute bar:

- is left-labelled at the minute start;
- uses observed best-bid OHLC and best-ask OHLC;
- contains only `PRICE` events whose provider timestamp falls in that minute;
- is complete only if it contains at least one valid `PRICE` event and no stale interval intersects the minute;
- is never fabricated by forward-filling the last quote into an empty minute.

Heartbeats may advance the event loop and close elapsed time buckets, but they do not create price observations.

### 10.2 Fifteen-minute bars

A 15-minute bar:

- is left-labelled exactly like the Phase 2/4 research bars;
- aggregates exactly 15 consecutive UTC one-minute bars;
- is complete only when every constituent one-minute bar is complete;
- preserves separate bid and ask OHLC;
- becomes knowable only at the interval end.

This preserves the existing Phase 4 timing bridge: observation label `T` represents `[T, T+15m)`, and true signal-known time is `T+15m`.

### 10.3 No live backfill

Phase 8 does not call OANDA candle-history endpoints to repair missing bars.

If the runner starts after required London-session context is already missing, the affected London date is ineligible. The system waits for a later date with complete observed context rather than backfilling or shortening the strategy window.

## 11. Strategy, decision, and risk parity

Phase 8 must call the existing frozen `session_breakout` candidate generator with the exact Phase 7 configuration. It must not reimplement the strategy in the shadow package.

Candidate-to-decision adaptation must reuse the existing decision contract wherever applicable. Risk sizing, risk caps, daily realized-loss halt, side conventions, JPY conversion semantics, and adverse slippage primitives must reuse Phase 3 code rather than duplicate formulas.

The Phase 8 shadow layer introduces no new alpha rule.

### 11.1 Candidate eligibility

A live candidate is eligible only when:

- every required range/signal 15-minute bar is complete;
- the candidate is from the sole frozen USDJPY 15m configuration;
- the signal-known time occurs while the stream is healthy;
- the first executable quote arrives within the five-second entry deadline.

A missing prerequisite becomes a reasoned `NO TRADE` or invalidated-shadow event, never a repaired candidate.

## 12. Shadow-only execution simulation

Phase 8 creates a `ShadowIntent`/shadow-position state that is intentionally not compatible with a broker execution adapter.

It may contain simulation fields such as:

- decision ID;
- direction;
- signal-known time;
- stop;
- target;
- scheduled flat time;
- simulated units/risk;
- cost-scenario identity.

It must not contain or expose a method that sends the intent externally.

### 12.1 Entry

For an eligible directional decision, the first valid `PRICE` at or after signal-known time and within five seconds is the hypothetical entry quote.

- LONG reference entry: best ask;
- SHORT reference entry: best bid;
- adverse slippage is applied with existing Phase 3 primitives.

If no valid quote arrives by the deadline, no hypothetical position is opened.

### 12.2 Stop and target monitoring

After entry, each subsequent valid `PRICE` is evaluated using executable sides:

- LONG stop/target observation: bid;
- SHORT stop/target observation: ask.

If a sampled quote gaps adversely through the stop, the worse observed executable price is used subject to the existing adverse-slippage convention. A favorable jump beyond the target receives no improvement beyond the declared target, matching the Phase 3 conservative target rule.

Because the pricing stream does not deliver every market tick, an unobserved path cannot be reconstructed. Any stale stream gap during an open position invalidates the outcome as specified above.

### 12.3 Scheduled flat

At the exact existing `16:00 Europe/London` flat time, the first valid quote within five seconds is used for the hypothetical time exit with the existing executable-side and adverse-slippage semantics.

A missing quote by the deadline makes the outcome operationally invalid rather than extending the position.

## 13. Cost scenarios and virtual accounts

The live candidate stream is evaluated in parallel under exactly the same Phase 7 adverse-slippage scenarios:

- `0.2` pips per fill — gating;
- `0.5` pips per fill — gating;
- `1.0` pip per fill — diagnostic only.

Historical/live observed BID/ASK spread is inherent in the corresponding quote sides. Commission and financing remain zero for the mandatory-intraday-flat strategy.

Each cost scenario maintains an independent virtual account starting at exactly `$100,000` at the start of the accepted shadow campaign. Virtual equity carries forward within the campaign, and the unchanged Phase 3 risk policy is applied to that scenario's virtual account.

No virtual state is connected to a broker account or real capital.

## 14. Runtime state and restart behavior

The shadow runner is a recoverable local process, not an always-on paid service requirement.

Durable state is reconstructed from append-only evidence. A restart must never assume an unobserved market path.

If the process restarts after missing any required part of the current London date:

- the current date is invalid for new shadow entries;
- an open hypothetical position becomes `OUTCOME_UNKNOWN_AFTER_GAP`;
- the runner resumes quote capture but waits for a later fully observed London date before allowing a new candidate.

No REST backfill, broker position query, or order reconciliation is part of Phase 8.

## 15. Evidence architecture

Each live run writes append-only evidence under a dedicated run directory. Exact filenames will be frozen in the implementation plan, but the evidence classes are:

1. raw accepted stream messages (`PRICE` / `HEARTBEAT`) plus receive metadata;
2. normalized quote events;
3. 1-minute and 15-minute shadow-live bars;
4. candidate/decision events, including reasoned no-trades and invalidations;
5. cost-scenario shadow position/trade events;
6. operational events such as connect, disconnect, stale, restart, malformed-message rejection;
7. a manifest binding file SHA-256 values and run identity.

The raw capture must not include request headers, bearer tokens, or plain account IDs.

### 15.1 Run identity

The manifest binds at minimum:

- code commit;
- Phase 7 checkpoint tag and exact SHA;
- Phase 7 experiment/outcome identity;
- frozen strategy configuration;
- connector protocol version;
- exact Practice host/path/instrument contract;
- OANDA account fingerprint, not plain account ID;
- cost scenarios;
- Phase 3 risk configuration identity;
- run start/end UTC;
- file SHA-256 values;
- replay result digest.

## 16. Deterministic replay

Every accepted raw shadow stream capture must be replayable offline without network access.

Given identical captured stream messages and identical frozen configuration, offline replay must reproduce byte-identical derived artifacts for:

- normalized quotes;
- bars;
- candidates/decisions;
- shadow trade/outcome ledger;
- financial metrics.

Runtime-only receive timestamps may remain in the raw operational capture but must not make deterministic derived artifacts differ when replaying the same capture.

Replay determinism is a mandatory Phase 8 implementation and acceptance gate.

## 17. Historical spread reference

Before the live campaign is declared started, Phase 8 creates one frozen research-reference artifact from the already accepted Phase 2/7 USDJPY historical data for the same strategy and execution points.

The reference contains, at minimum:

- historical entry spread in pips for completed Phase 7 survivor trades;
- historical scheduled-exit/actual-exit spread in pips where applicable;
- median and 95th-percentile spread summaries;
- exact upstream data identity and code identity;
- artifact SHA-256.

This artifact is comparison evidence only. It must not alter the strategy, buffer, target, timeframe, pair, risk settings, or slippage scenarios.

After the live campaign begins, the historical-reference method and thresholds are frozen for `EXP-20260915-009`.

## 18. Live shadow campaign minimum evidence

Phase 8 cannot PASS on a very small sample.

A campaign is eligible for Phase 8 acceptance review only after all of the following are true:

- at least `40` completed, financially scorable shadow trades at the `0.2`-pip scenario;
- at least `8` elapsed calendar weeks between first and last accepted campaign observations;
- at least `30` London dates with complete required strategy observation coverage;
- every financially scored trade has a fully observed path from entry through stop/target/time exit;
- all three cost scenarios have been evaluated for the same candidate sequence.

If the system is operationally correct but these minimums are not reached, the outcome is `NEED_MORE_DATA`; Phase 8 remains active and Phase 9 remains locked.

## 19. Phase 8 acceptance gate

Phase 8 PASS requires **all** structural, operational, spread, timing, replay, and financial criteria below.

### 19.1 Structural safety

- no Phase 8 runtime path can submit or mutate an order, trade, or position;
- exact Practice pricing-stream GET boundary is proven by tests and code inspection;
- production OANDA hosts are rejected;
- no generic method/base-URL/path surface exists;
- no bearer token or plain account ID appears in durable artifacts;
- no demo/live execution adapter is imported or invoked.

Any structural safety failure is an immediate Phase 8 FAIL and blocks Phase 9.

### 19.2 Operational integrity

- connector qualification is PASS;
- at least 30 fully observed London dates exist;
- at least 90% of London dates for which the campaign was intentionally running from before the required range start through 16:00 local remain valid for strategy evaluation;
- zero malformed provider messages are silently accepted;
- zero stale-gap trades are included in financial metrics;
- every disconnect/reconnect/stale event is durably logged.

The 90% operational-coverage threshold measures the implementation/runtime's ability to remain usable without pretending missing data is complete.

### 19.3 Timing

- local processing latency from accepted message receipt to durable normalized-event emission has 99th percentile less than or equal to `250 ms` during the scored campaign;
- every financially scored entry uses a valid quote no more than `5` seconds after signal-known time;
- every scheduled-time exit uses a valid quote no more than `5` seconds after 16:00 `Europe/London`.

Trades violating the quote deadlines are operationally invalid and cannot be counted toward the 40-trade minimum.

### 19.4 Spread parity

Using the frozen historical spread-reference artifact:

- live median entry spread must not exceed historical median entry spread by more than `0.5` pip;
- live 95th-percentile entry spread must not exceed historical 95th-percentile entry spread by more than `0.5` pip;
- the same two comparisons apply to financially scored exits.

The `0.5`-pip tolerance is a predeclared operational mismatch bound; it is not a strategy retuning parameter and cannot be widened after live observations begin.

### 19.5 Hypothetical financial behavior

At both `0.2` and `0.5` pips adverse slippage per fill across the accepted shadow campaign:

- net return is strictly positive;
- expectancy per completed trade is strictly positive;
- profit factor is strictly greater than `1.0`;
- maximum drawdown fraction is less than or equal to `0.05`.

The `0.2`-pip scenario must contain at least 40 completed financially scorable trades.

The `1.0`-pip scenario is preserved as diagnostic evidence only. It may be negative without independently reversing a PASS at both gating costs, matching the Phase 7 treatment of the 1.0-pip stress case.

### 19.6 Deterministic replay

The complete accepted campaign must replay offline into byte-identical derived artifacts and identical acceptance metrics.

A replay mismatch is a Phase 8 FAIL until the implementation defect is corrected and a fresh campaign/review establishes valid evidence.

## 20. Outcome states

The Phase 8 acceptance review may end in exactly one of:

- `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN`
- `PHASE8_NEED_MORE_DATA`
- `PHASE8_REJECT_OPERATIONAL_MISMATCH`
- `PHASE8_REJECT_MARKET_MISMATCH`
- `PHASE8_REJECT_FINANCIAL_MISMATCH`
- `PHASE8_REJECT_SAFETY_FAILURE`

No outcome automatically starts Phase 9 or authorizes demo orders. A PASS makes the unchanged strategy eligible for a separate Phase 9 demo-trading design only.

## 21. Testing requirements

Implementation must include tests covering at least:

- exact Practice host/path/GET/instrument contract;
- rejection of production hosts, arbitrary URLs, arbitrary methods, arbitrary instruments, and order/trade/position paths;
- token/account redaction;
- `PRICE`/`HEARTBEAT` parsing;
- best-bid/max and best-ask/min independent of ladder ordering;
- invalid/missing/non-positive/crossed quote rejection;
- source timestamp regression and duplicate handling;
- 15-second liveness timeout;
- no bar forward-fill;
- exact 1m and 15m left-labelled boundaries;
- incomplete/stale constituent bars invalidating 15m bars;
- London DST behavior through existing strategy/session logic;
- exact frozen session-breakout configuration;
- no candidate from incomplete live context;
- five-second entry and scheduled-exit deadlines;
- long/short executable-side semantics;
- adverse stop-gap and no favorable target-price-improvement behavior;
- stale gap invalidating an open hypothetical trade;
- unchanged Phase 3 risk and JPY sizing semantics;
- independent 0.2/0.5/1.0 virtual accounts;
- restart behavior with no backfill or hidden position continuation;
- deterministic replay;
- evidence manifest SHA binding;
- exact acceptance-boundary tests for sample size, coverage, timing, spread, profitability, profit factor, and drawdown;
- repository-level guard proving Phase 8 runtime has no order-submission surface.

Existing Phase 1–7 tests and normal historical-data locks must remain green.

## 22. Operational deployment boundary

Phase 8 implementation is intended to run as an explicitly started local/authorized process using free infrastructure. It does not require paid hosting, a paid data feed, a dashboard, or an always-on cloud service.

Continuous operation on a user's machine is an operational choice, not permission for the assistant to perform background work. The code may support restartable campaigns, but evidence is produced only while the operator actually runs the process.

GitHub Actions may run source-free unit/replay tests, but the long-running live shadow campaign should not be implemented as an implicit CI side effect. Live connector qualification/campaign execution requires explicit credentials and an explicit operator action.

## 23. Source-of-truth changes required before implementation

After this written spec is reviewed and approved, the Phase 8 activation change must:

1. add `DEC-036` freezing this Phase 8 protocol;
2. add planned `EXP-20260915-009` to the experiment log;
3. update `docs/project-state.md` from Phase 7 PASS / Phase 8 UNSTARTED to Phase 8 ACTIVE only after the Phase 7 checkpoint tag prerequisite is satisfied;
4. update `docs/source-register.md` with the 2026-09-15 OANDA/MT5 reverification and the selected OANDA Practice pricing-stream role;
5. preserve `DEC-008` and all demo/live/real-money locks;
6. commit these source-of-truth changes before runtime implementation proceeds.

## 24. Non-goals

Phase 8 does not include:

- OANDA order placement;
- OANDA production/live hosts;
- MT5 order or quote integration in the initial implementation;
- broker account/position/order synchronization;
- demo trading;
- real-money trading;
- broker fill measurement;
- REST candle backfill;
- strategy retuning;
- parameter search;
- another pair or timeframe;
- portfolio/correlation logic expansion;
- ML filtering or model training;
- economic-calendar filtering;
- dashboards;
- paid infrastructure or paid data;
- tick-perfect market reconstruction;
- automatic failover to another provider.

## 25. Change control

Once `DEC-036` activates this protocol, changing any of the following after live campaign observations begin requires a new decision and a new experiment rather than editing `EXP-20260915-009` in place:

- strategy/pair/timeframe/parameters;
- provider or provider environment;
- transport host/path/method/instrument boundary;
- stale thresholds;
- entry/exit quote deadlines;
- bar-completeness semantics;
- slippage scenarios;
- risk settings;
- sample-size minimums;
- operational-coverage threshold;
- timing threshold;
- spread-parity tolerance;
- financial promotion gates.

Negative and inconclusive evidence must remain recorded.

## 26. Completion condition

The implementation phase is ready to start only after all of the following are true:

- this written design has been reviewed and explicitly approved;
- `fmp-v1-phase7-walk-forward` exists at `b6fb0176555b071fef6d1070edf3407b03cd60c9`;
- the Phase 8 implementation plan is written from this design;
- source-of-truth activation records are committed before runtime code.

Phase 8 itself is complete only after a live shadow campaign reaches one of the terminal acceptance outcomes in Section 20 with auditable evidence. Only `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN` may unlock Phase 9 design work; it does not authorize demo execution by itself.
