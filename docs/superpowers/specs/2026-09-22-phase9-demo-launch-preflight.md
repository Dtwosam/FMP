# Phase 9 — Broker-Connected Demo Launch Preflight

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-063
**Experiment:** EXP-20260922-034
**Depends on:** DEC-055 through DEC-062
**Scope:** broker-connected read/check-only launch preflight over exact runtime-authority evidence; no order submission

## 1. Purpose

DEC-062 can accept one exact materialized arm as runtime authority while keeping
the execution source lock false.

DEC-063 may add the final fresh broker-state verification layer required before
a later first-demo-order decision:

- current practice-account assertion;
- current symbol-contract snapshot;
- current tick snapshot;
- fresh non-mutating `order_check`;
- current open-order/open-position reconciliation;
- exact runtime-authority/journal/time revalidation;
- create-only launch-preflight evidence.

DEC-063 does not change:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

It may not call `order_send`, cancel, modify, or close any broker object.

## 2. Exact upstream inputs

Every launch preflight requires exact valid:

- DEC-055 demo design;
- DEC-056 demo order request;
- DEC-059 session arm;
- DEC-059 session-ready evidence;
- DEC-060 execution arm;
- DEC-062 runtime-authority evidence;
- current DEC-059 session journal rows.

All identities must agree.

## 3. Backend boundary

DEC-063 defines a broker-connected read/check protocol exposing only:

- `account_snapshot()`;
- `symbol_snapshot(symbol)`;
- `tick_snapshot(symbol)`;
- `order_check(mt5_request)`;
- `broker_orders()`;
- `broker_positions()`.

The protocol exposes no:

- `order_send`;
- submit;
- cancel;
- modify;
- close-position;
- other mutation method.

The existing DEC-058 MetaTrader5 backend may structurally satisfy this narrower
protocol, but DEC-063 never receives or calls a mutation method.

## 4. Immediate runtime revalidation

At launch-preflight time:

- current UTC must remain inside the exact arm window;
- current UTC must not precede the DEC-062 runtime-validation time;
- daily halt must be inactive;
- DEC-059 journal must still validate;
- journal identity must still bind the exact arm/request/client ID;
- journal `SEND_ATTEMPTED` count must still be zero;
- DEC-058 source gate must still be false.

Any failure stops before broker reads.

## 5. Fresh practice-account assertion

After the runtime checks pass, DEC-063 reads the current account snapshot.

It must remain:

- DEMO;
- exact accepted account fingerprint;
- exact accepted demo server;
- trading allowed at the account snapshot layer.

Mismatch fails closed.

DEC-063 does not change AutoTrading or terminal settings.

## 6. Fresh symbol and quote validation

DEC-063 reads the exact approved symbol contract and current tick.

The existing DEC-057 rules remain authoritative:

- exact symbol mapping;
- exact no-resize units-to-volume translation;
- broker volume-grid fit;
- current BUY ask / SELL bid;
- broker price grid;
- minimum protective-stop distance;
- target geometry;
- supported filling mode.

No stop/target/volume repair is allowed.

## 7. Fresh order_check

DEC-063 rebuilds the exact DEC-057 order-check request from fresh account,
symbol, and tick state.

It then calls only non-mutating `order_check`.

Only normalized `retcode=0` is check-passed.

The exact order-check request and result fingerprints are bound into launch
evidence.

A passing check does not authorize order submission.

## 8. Fresh reconciliation

DEC-063 reads active broker orders and positions and runs the exact DEC-056
reconciliation against the one approved local request.

Launch-preflight readiness requires:

- no duplicate client-order ID;
- no unknown broker order;
- no orphan broker position;
- no missing expected protective stop;
- `healthy=true`.

DEC-063 performs no automatic broker repair.

## 9. Launch-preflight evidence

The protocol is:

`fmp-phase9-demo-launch-preflight-v1`.

It binds:

- exact DEC-062 runtime-authority fingerprint;
- exact upstream design/request/session/execution-arm fingerprints;
- launch-preflight code commit;
- current UTC;
- current journal event count/tip;
- fresh account/symbol/tick evidence;
- fresh order-check request/result fingerprints;
- fresh reconciliation fingerprint;
- `broker_reads_performed=true`;
- `order_check_performed=true`;
- `order_send_attempted=false`;
- deterministic launch-preflight fingerprint.

Successful outcome:

`PHASE9_DEMO_LAUNCH_PREFLIGHT_READY`.

## 10. Authorization semantics

A valid launch preflight may set only:

- `demo_launch_preflight_ready=true`.

It must keep:

- `demo_execution_source_armed=false`;
- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

## 11. Persistence

DEC-063 may write create-only:

- `launch-preflight.json`;
- `manifest.json`.

Existing paths fail closed.

## 12. CLI boundary

DEC-063 adds no broker-connected CLI and no order-capable CLI.

The existing Phase 9 CLI remains:

- `design-demo`;
- `materialize-arm`.

Repository tests use only fake in-memory read/check backends.

## 13. Safety and next gate

Possible EXP-034 source outcomes:

- `PHASE9_DEMO_LAUNCH_PREFLIGHT_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome submits or authorizes an order.

A later separately approved decision is mandatory before:

- `DEMO_EXECUTION_SOURCE_ARMED` can become true;
- any runner can invoke `order_send`;
- the first real practice-account order can be sent.
