# Phase 9 — MT5 Demo Transport Preflight and Order-Check Foundation

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-057
**Experiment:** EXP-20260922-028
**Depends on:** DEC-055 demo design and DEC-056 locked demo-order protocol
**Scope:** source-only MT5 practice-account translation, contract validation, and non-mutating order-check foundation; no order submission

## 1. Purpose

DEC-056 freezes broker-independent post-risk demo-order requests but contains no
MT5-specific order translation.

DEC-057 may implement the deterministic MT5 adapter logic required before a
future mutation transport is considered:

- exact practice-account identity assertion;
- exact approved symbol mapping;
- read-only symbol-contract normalization;
- unit-to-volume translation without silent resizing;
- direction-aware current quote selection;
- broker stop-distance validation;
- deterministic MT5 order-check payload;
- non-mutating order-check result normalization;
- source-only preflight evidence;
- startup read/reconciliation fixture normalization.

DEC-057 does not implement, expose, call, or authorize `order_send`.

## 2. Exact inputs

Every DEC-057 preflight requires:

- one exact valid `fmp-phase9-demo-design-v1`;
- one exact valid `fmp-phase9-demo-order-request-v1`;
- one normalized practice-account snapshot;
- one normalized MT5 symbol snapshot;
- one normalized current tick;
- optional normalized `order_check` result supplied through the adapter
  backend boundary.

No caller may override provider, account fingerprint, server, approved symbol,
direction, units, stop, target, or client order ID.

## 3. Backend boundary

DEC-057 defines a read/check-only backend protocol.

It may expose:

- account snapshot;
- symbol snapshot;
- current tick;
- normalized `order_check`;
- normalized open-order and open-position reads for reconciliation.

It must expose no `order_send`, close-position, modify-position, cancel-order,
or other mutation method.

The DEC-057 adapter object must therefore be structurally incapable of broker
mutation.

## 4. Practice-account assertion

The account snapshot must state:

- account mode `DEMO`;
- exact accepted account fingerprint;
- exact accepted server;
- trading is not disabled at the account snapshot layer.

Any mismatch fails closed before payload construction.

DEC-057 does not change AutoTrading or terminal settings.

## 5. Symbol contract

The symbol snapshot must bind the exact approved broker symbol and provide:

- `trade_contract_size`;
- `volume_min`;
- `volume_step`;
- `volume_max`;
- `digits`;
- `point`;
- `trade_stops_level_points`;
- one normalized filling mode from `FOK`, `IOC`, or `RETURN`;
- trade-enabled boolean.

All numeric values must be finite and positive except
`trade_stops_level_points`, which may be zero.

## 6. Units to MT5 volume

The broker-independent Phase 3/DEC-056 request units remain authoritative.

Raw MT5 volume is:

`units / trade_contract_size`.

The adapter may not round the requested risk or units to make an order fit.

The raw volume must already be representable on the broker's
`volume_min / volume_step / volume_max` grid within deterministic decimal
precision. Otherwise preflight fails closed.

## 7. Current quote and market side

The normalized tick requires positive finite bid/ask with ask >= bid and UTC
source timestamp.

For a LONG request:

- market side = BUY;
- requested market price = current ask.

For a SHORT request:

- market side = SELL;
- requested market price = current bid.

The current tick is evidence only. It does not mutate the broker.

## 8. Protective-stop validation

The DEC-056 stop remains mandatory.

DEC-057 revalidates direction geometry against the current requested market
price and the broker's current minimum stop distance:

`trade_stops_level_points * point`.

A stop that violates direction geometry or the minimum stop distance fails
closed.

A target, when present, must also preserve direction geometry. No source path
widens, removes, or silently adjusts a stop/target.

## 9. MT5 order-check payload

DEC-057 defines:

`fmp-phase9-mt5-demo-order-check-request-v1`.

The deterministic payload binds:

- exact design/request fingerprints;
- client order ID;
- DEMO account/server identity;
- exact symbol;
- BUY/SELL side;
- exact representable volume;
- current requested market price;
- exact stop and optional target;
- fixed time-in-force = GTC;
- exact normalized broker filling mode from the symbol snapshot;
- fixed check-only deviation = 0 points;
- fixed comment derived from client order ID;
- no credential material;
- no mutation authorization.

The payload fingerprint must be deterministic.

## 10. Order-check evidence

DEC-057 defines:

`fmp-phase9-mt5-demo-order-check-v1`.

A normalized check result binds:

- exact order-check request fingerprint;
- normalized return code;
- normalized comment;
- normalized margin fields when supplied;
- `check_passed`;
- `order_send_attempted=false`;
- `broker_mutation_attempted=false`;
- `demo_order_submitted=false`;
- `live_order_submitted=false`.

Only normalized MT5 order-check `retcode=0` (`Done`) may set `check_passed=true`.
Any other return code fails the preflight. A passing check is still not execution
authorization and does not imply that a later `order_send` would succeed.

## 11. Preflight evidence

A successful source preflight writes:

`fmp-phase9-mt5-demo-preflight-v1`.

It binds exact design/request/order-check identities and all normalized
practice-account, symbol, tick, volume, stop-distance, and check evidence.

The outcome is:

`PHASE9_MT5_DEMO_PREFLIGHT_READY`.

It authorizes no order.

## 12. CLI boundary

DEC-057 adds no order-capable CLI and no broker-connected CLI.

The existing Phase 9 CLI remains `design-demo` only.

No `run-demo`, `check-order`, `submit-order`, `trade`, `broker`,
`cancel`, `close`, or mutation command is introduced.

## 13. Authorization boundary

DEC-057 may set only:

- `mt5_demo_preflight_source_ready=true`.

It must keep:

- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `live_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

## 14. Safety and next gate

Possible EXP-028 source outcomes:

- `PHASE9_MT5_DEMO_PREFLIGHT_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome can place, modify, cancel, or close an order/position.

A later separately approved decision is mandatory before an MT5 backend with
`order_send` or any broker mutation method may be implemented, wired, or
enabled.
