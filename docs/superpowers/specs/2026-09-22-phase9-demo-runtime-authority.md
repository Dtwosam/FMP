# Phase 9 — Demo Runtime Arm Authority Contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-062
**Experiment:** EXP-20260922-033
**Depends on:** DEC-055 through DEC-061
**Scope:** source-only runtime acceptance of one exact materialized demo arm; no execution-gate change and no broker access

## 1. Purpose

DEC-061 can materialize one exact DEC-060 execution-arm package offline, but no
source currently accepts that package as runtime authority.

DEC-062 may implement only the runtime validation/evidence layer required before
a later broker-connected runner can exist.

DEC-062 does not change:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

It does not import MetaTrader5, instantiate a mutation backend, run
`order_check`, call `order_send`, or submit any order.

## 2. Runtime-authority protocol

The protocol is:

`fmp-phase9-demo-runtime-authority-v1`.

It binds exactly:

- DEC-055 demo-design fingerprint;
- DEC-056 request fingerprint and client-order ID;
- DEC-059 session-arm and session-ready fingerprints;
- DEC-060 execution-arm fingerprint;
- champion-set fingerprint;
- strategy fingerprint;
- symbol;
- accepted DEMO account fingerprint and server;
- exact arm not-before and expiry;
- operator approval reference;
- runtime validation UTC;
- current journal event count and journal-tip fingerprint;
- zero prior `SEND_ATTEMPTED` count;
- daily-halt inactive;
- maximum new orders = 1;
- deterministic runtime-authority fingerprint.

## 3. Runtime checks

Construction requires all upstream validators to pass.

Immediately at runtime-validation time:

- current UTC must be inside the exact DEC-059/060 arm window;
- daily halt must be false;
- the arm must remain practice-only;
- the arm order cap must remain exactly one;
- session readiness must still bind zero attempts;
- the supplied DEC-059 journal must validate;
- the journal must bind the same session arm, request, and client-order ID when
  it contains rows;
- journal `SEND_ATTEMPTED` count must be zero;
- DEC-058 source gate must still be false.

Any failure is protocol failure.

## 4. No time-window widening

DEC-062 copies the existing arm window exactly.

The builder accepts current UTC only to prove the arm is presently within its
existing window. It cannot move or widen the window.

## 5. Journal identity

If the journal is empty:

- event count = 0;
- journal-tip fingerprint = null;
- send-attempt count = 0.

If it is non-empty, the final row fingerprint becomes the journal-tip
fingerprint.

No journal repair, truncation, re-fingerprinting, or backfill is allowed.

## 6. Authorization semantics

A valid runtime-authority record means only:

- `demo_runtime_arm_authority_ready=true`.

It must keep:

- `demo_execution_source_armed=false`;
- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

The record is not sufficient to call the DEC-058 mutation adapter.

## 7. Create-only persistence

DEC-062 may persist:

- `runtime-authority.json`;
- `manifest.json`.

Existing paths fail closed.

The manifest binds the runtime-authority fingerprint and exact artifact
SHA-256.

## 8. CLI boundary

DEC-062 adds no broker-connected or order-capable command.

The Phase 9 CLI remains limited to:

- `design-demo`;
- `materialize-arm`.

No `run-demo`, `activate-arm`, `submit-order`, `order-send`, `trade`,
`broker`, `cancel`, `close-position`, or `modify-order` command is
introduced.

## 9. Safety and next gate

Possible EXP-033 source outcomes:

- `PHASE9_DEMO_RUNTIME_AUTHORITY_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome changes the source gate or touches a broker.

A later separately approved decision is mandatory before:

- `DEMO_EXECUTION_SOURCE_ARMED` can become true;
- a broker-connected runner may consume runtime-authority evidence;
- the first real practice-account order can be sent.
