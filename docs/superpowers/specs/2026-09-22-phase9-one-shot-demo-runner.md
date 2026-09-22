# Phase 9 — Permit-Aware One-Shot Demo Runner Source

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-065
**Experiment:** EXP-20260922-036
**Depends on:** DEC-055 through DEC-064
**Scope:** source-only one-shot runner orchestration behind the unchanged DEC-058 execution gate; no real demo order and no execution CLI

## 1. Purpose

DEC-064 defines an immutable one-shot execution permit but deliberately exposes
no execution runner.

DEC-065 may implement the orchestration source that a later separately approved
first-demo-order decision would use.

DEC-065 does not change:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

Repository verification may patch the gate only in unit tests with in-memory
fake backends. No repository workflow or operator command may send a real order.

## 2. Exact inputs

One runner instance binds exact valid:

- DEC-055 demo design;
- DEC-056 demo order request;
- DEC-059 session arm and session-ready evidence;
- DEC-060 execution arm;
- DEC-062 runtime-authority evidence;
- DEC-063 launch preflight;
- DEC-064 execution permit;
- current DEC-059 journal prefix.

All identities must agree.

The runner accepts no semantic override for symbol, side, units/volume,
protective stop, target, account, server, provider, client-order ID, arm
window, approval reference, or order count.

## 3. Backend boundary

DEC-065 defines a narrow mutation backend protocol exposing only:

- `order_send(mt5_request)`;
- `broker_orders()`;
- `broker_positions()`.

The runner does not call account/symbol/tick reads or `order_check` after the
DEC-064 permit has been constructed.

It submits only the exact checked MT5 request already bound by DEC-063/064.

## 4. Immediate execution revalidation

Before any journal mutation or backend call, the runner must verify:

- exact DEC-064 permit validation succeeds;
- current UTC is inside the exact arm window;
- current UTC is not before launch-preflight time;
- daily halt is inactive;
- journal prefix validates and exactly matches the launch-preflight/permit
  journal count and tip;
- journal contains zero `SEND_ATTEMPTED`;
- permit allows exactly one new order;
- permit is practice-only;
- exact checked MT5 request SHA-256 equals the permit binding;
- `DEMO_EXECUTION_SOURCE_ARMED is True`.

With the repository's DEC-058 source value still false, execution fails before
journal mutation and before backend access.

## 5. Durable one-shot spend

When and only when the source gate is true, the runner must durably append
`SEND_ATTEMPTED` to the DEC-059 journal before calling `order_send`.

That event binds:

- exact order-check request fingerprint;
- exact order-check fingerprint;
- exact checked MT5 request SHA-256;
- exact execution-permit fingerprint.

The existing DEC-059 journal flush + fsync behavior is authoritative.

After `SEND_ATTEMPTED` is durable, the arm is spent regardless of broker
outcome. The runner must never retry `order_send`.

## 6. Exact send payload

The runner sends the exact canonical DEC-063 checked MT5 request object.

It may not rebuild, refresh, resize, round, alter, or repair:

- volume;
- side;
- price;
- stop;
- target;
- filling mode;
- time-in-force;
- client comment.

A mismatch with the permit fails before `SEND_ATTEMPTED`.

## 7. Send result

If `order_send` returns normally, DEC-065 must normalize it through the exact
DEC-058 `build_phase9_mt5_send_result` and validate the result.

The runner then durably appends one `SEND_RESULT` event.

A full successful send requires the existing DEC-058 definition:
`TRADE_RETCODE_DONE` plus exact expected volume.

Any rejection, partial volume, or other returned non-completed result spends
the arm and is terminal for that one-shot session.

## 8. Ambiguous send exception

If `order_send` raises after `SEND_ATTEMPTED` is durable:

- the runner must not retry;
- the arm remains spent;
- one `SESSION_HALTED` event is appended when journal writing remains
  available;
- the runner must attempt one broker-state reconciliation;
- ambiguity remains explicit even if reconciliation is healthy.

No automatic order repair, cancellation, close, or second send is permitted.

## 9. Post-send reconciliation

After any attempted send, the runner performs at most one read of active broker
orders and positions and runs the exact DEC-056 reconciliation against the
single approved local request.

It durably appends exactly one of:

- `POST_SEND_RECONCILIATION_OK`;
- `POST_SEND_RECONCILIATION_FAILED`.

For a completed send, a healthy reconciliation is required for successful
session completion.

No automatic repair is allowed.

## 10. Runner evidence

DEC-065 defines:

`fmp-phase9-demo-one-shot-run-v1`.

The source result binds:

- execution-permit fingerprint;
- request/client identity;
- exact checked MT5 request SHA-256;
- send-attempt journal event fingerprint;
- optional DEC-058 send-result fingerprint;
- post-send reconciliation fingerprint when available;
- final journal event count/tip;
- one attempt count;
- runner outcome;
- deterministic runner fingerprint.

Allowed source outcomes:

- `PHASE9_DEMO_ONE_SHOT_COMPLETED`;
- `PHASE9_DEMO_ONE_SHOT_NOT_COMPLETED`;
- `PHASE9_DEMO_ONE_SHOT_AMBIGUOUS`.

All outcomes are terminal for the one-shot arm.

## 11. Authorization semantics

DEC-065 source implementation may set only:

- `demo_one_shot_runner_source_ready=true`.

It must keep:

- `DEMO_EXECUTION_SOURCE_ARMED=false` in repository source;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

DEC-065 does not create a real permit, activate a real arm, or send a real demo
order.

## 12. CLI boundary

DEC-065 adds no command.

The Phase 9 CLI remains:

- `design-demo`;
- `materialize-arm`.

No `run-demo`, `submit-order`, `order-send`, `trade`, `broker`,
`cancel`, `modify`, or `close-position` command is introduced.

## 13. Safety and next gate

Repository tests must use only fake in-memory mutation backends.

A later separately approved decision is mandatory before:

- the source gate can be true in an operator build/runtime;
- a broker-connected runner command can exist;
- a real DEC-064 permit may be consumed;
- the first practice-account order can be sent.
