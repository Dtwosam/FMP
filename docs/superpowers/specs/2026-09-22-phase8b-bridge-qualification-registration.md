# Phase 8B — Multi-Symbol MT5 Bridge Qualification and Registration

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B CAMPAIGN
**Decision:** DEC-047
**Experiment:** EXP-20260922-018
**Scope:** read-only connector qualification and immutable campaign registration only

## 1. Purpose

DEC-046 freezes the Phase 8B multi-symbol shadow design but deliberately leaves campaign registration/start unauthorized.

DEC-047 freezes the connector/qualification/registration boundary required before any Phase 8B live-shadow capture can begin. It preserves the legacy USDJPY EXP-011 bridge/runtime unchanged and introduces a separate Phase 8B multi-symbol read-only bridge.

Nothing in DEC-047 authorizes campaign start, demo orders, live orders, broker mutation, real-money trading, or Phase 9.

## 2. Required design input

Every DEC-047 action requires one exact DEC-046 design artifact with:

- protocol `fmp-phase8b-shadow-design-v1`;
- experiment `EXP-20260922-017`;
- outcome `PHASE8B_DESIGN_FROZEN`;
- valid design fingerprint;
- exact accepted champion-set identity;
- exact required symbol subset;
- campaign/order authorization flags still false.

The design artifact SHA-256 and Phase 8B design compiler commit are bound into qualification and registration evidence.

## 3. Phase 8B bridge protocol

New bridge protocol:

`fmp-mt5-demo-multisymbol-file-bridge-v1`

The record schema remains deliberately close to the legacy proven bridge:

Common fields:

- `record_type`
- `protocol`
- `bridge_session_id`
- `symbol`
- `server`
- `account_fingerprint`

Record types:

- `BRIDGE_START`
- `TICK`
- `BRIDGE_HEARTBEAT`

No order, position, trade, or account-mutation record exists.

Supported symbols are exactly:

- EURUSD
- GBPUSD
- USDJPY

Fixed FILE_COMMON paths remain:

- EURUSD -> `FMP/phase8b-eurusd-feed.jsonl`
- GBPUSD -> `FMP/phase8b-gbpusd-feed.jsonl`
- USDJPY -> `FMP/phase8b-usdjpy-feed.jsonl`

Each EA instance is attached to exactly one required symbol chart. The EA derives its fixed file from `_Symbol`; no arbitrary path/symbol input is allowed.

## 4. MT5 safety boundary

Each Phase 8B EA must fail initialization unless:

- account mode is DEMO;
- server is exactly `FPMarketsSC-Demo` or `FPMarketsSC-Demo2`;
- chart symbol is one of the three V1 symbols;
- the fixed FILE_COMMON transport opens successfully;
- bridge/account/session hashing succeeds.

The EA is quote-only. Source/tests must reject introduction of order/trade surfaces including `OrderSend`, `CTrade`, position-opening/modification methods, or equivalent broker mutation APIs.

AutoTrading remains OFF.

## 5. Per-symbol qualification

Qualification thresholds remain exactly the conservative legacy values for each required symbol feed:

- maximum bounded qualification duration: 600 seconds;
- minimum valid normalized price count: 100;
- minimum heartbeat count: 6;
- bridge continuity threshold: 15 seconds;
- market-liveness threshold during qualification: 15 seconds;
- source-time skew deadline: 5 seconds.

Per-symbol outcomes remain:

- `PASS`
- `INCONCLUSIVE`
- `CONNECTOR_UNAVAILABLE`
- `CONNECTOR_REJECTED`

Semantics:

- bridge silence >15 seconds after activity -> `CONNECTOR_REJECTED`;
- inactive bridge before post-start activity -> `CONNECTOR_UNAVAILABLE`;
- market no-tick gap >15 seconds during qualification -> `INCONCLUSIVE`;
- source-time skew >5 seconds -> `CONNECTOR_REJECTED`;
- malformed/conflicting/session-changing records -> `CONNECTOR_REJECTED`.

No strategy, risk, or portfolio logic runs during qualification.

## 6. Multi-symbol qualification gate

The Phase 8B qualification summary is `PASS` only if every required symbol independently returns `PASS` and all required feeds satisfy:

- same account fingerprint;
- same approved server;
- distinct bridge session IDs;
- exact required-symbol coverage with no missing or extra feed;
- bridge protocol/file mapping matches DEC-046 design.

Overall fail-closed precedence:

1. any `CONNECTOR_REJECTED` -> overall `CONNECTOR_REJECTED`;
2. else any `CONNECTOR_UNAVAILABLE` -> overall `CONNECTOR_UNAVAILABLE`;
3. else any `INCONCLUSIVE` -> overall `INCONCLUSIVE`;
4. else all PASS + cross-feed identity gates -> `PASS`.

Cross-feed account/server/session mismatch is `CONNECTOR_REJECTED`.

## 7. Qualification evidence

The deterministic qualification summary records:

- DEC-046 design SHA-256 and design fingerprint;
- qualification code commit;
- exact required symbols;
- exact per-symbol bridge file;
- each symbol's:
  - outcome
  - bridge session ID
  - account fingerprint
  - server
  - price count
  - heartbeat count
  - elapsed seconds
  - max bridge-liveness gap
  - max market-liveness gap
  - rejection codes
- common account fingerprint/server when deterministically valid;
- overall outcome;
- campaign registration authorization flag.

Only overall `PASS` sets `campaign_registration_authorized = true`.

Campaign start remains false.

## 8. Immutable campaign registration

Registration requires:

- exact validated DEC-046 design artifact;
- exact Phase 8B qualification summary;
- qualification outcome `PASS`;
- `campaign_registration_authorized = true`;
- design and qualification SHA-256 values;
- registration code commit;
- explicit UTC registration timestamp.

Registration freezes:

- design fingerprint;
- champion-set ID/fingerprint;
- exact strategy identities/fingerprints;
- exact required symbols/timeframes;
- provider/transport/protocol;
- exact bridge file mapping;
- common demo account fingerprint/server;
- per-symbol bridge session IDs from qualification;
- liveness/quote deadlines;
- 0.2/0.5/1.0-pip scenarios;
- registration timestamp;
- immutable registration fingerprint.

Registration is exactly once per campaign directory/identity.

## 9. Registration does not authorize capture

Even a valid registration keeps:

- `campaign_start_authorized = false`;
- `promotion_authorized = false`;
- `demo_order_authorized = false`;
- `live_order_authorized = false`;
- `broker_mutation_authorized = false`;
- `real_money_authorized = false`;
- `phase9_authorized = false`.

A later separately frozen Phase 8B capture/acceptance protocol must authorize actual shadow capture.

## 10. No backfill / no alternate source

Qualification and registration may not use:

- MT5 historical candles;
- Dukascopy history;
- another provider;
- reconstructed ticks;
- interpolation;
- pre-reader transport content.

Only records appended after the active reader starts count toward connector qualification.

## 11. Outcome

Possible EXP-018 outcomes:

- `PHASE8B_CONNECTOR_QUALIFIED`
- `INCONCLUSIVE`
- `CONNECTOR_UNAVAILABLE`
- `CONNECTOR_REJECTED`
- `PROTOCOL_FAILURE`

A valid registration artifact may be produced only from `PHASE8B_CONNECTOR_QUALIFIED`.

No Phase 8B live-shadow segment may start under DEC-047.
