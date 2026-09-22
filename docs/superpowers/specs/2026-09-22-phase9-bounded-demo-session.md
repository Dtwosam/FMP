# Phase 9 — Bounded First Demo Session Contract and Journal

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-059
**Experiment:** EXP-20260922-030
**Depends on:** DEC-055 through DEC-058
**Scope:** source-only one-request practice-session authorization schema, readiness checks, durable journal contracts, and recovery semantics; DEC-058 execution gate remains false

## 1. Purpose

DEC-058 contains mutation-capable MetaTrader5 infrastructure source, but the
official FMP execution adapter remains hard-disabled.

DEC-059 freezes the first practice-session boundary before that gate can ever be
changed.

The first session is intentionally not a general demo runner. One session arm
may bind exactly one already-built DEC-056 post-risk request and may authorize
at most one new practice-account order.

DEC-059 does not create a real arm artifact, expose an arming CLI, or change
`DEMO_EXECUTION_SOURCE_ARMED = False`.

## 2. Arm protocol

The source-only arm schema is:

`fmp-phase9-demo-session-arm-v1`.

It binds:

- exact DEC-055 demo-design fingerprint;
- exact DEC-056 request fingerprint and client-order ID;
- exact champion-set fingerprint;
- exact strategy fingerprint;
- exact symbol;
- exact accepted DEMO account fingerprint;
- exact accepted demo server;
- `practice_only=true`;
- `max_new_orders=1`;
- UTC `not_before_utc`;
- UTC `expires_at_utc`;
- one explicit operator-approval reference;
- deterministic arm fingerprint.

The arm window must remain within one UTC civil date. This preserves the
existing Phase 3 daily-halt day boundary and prevents one arm from silently
crossing a risk-day reset.

No DEC-059 artifact or default arm is created by the repository.

## 3. Request immutability

The arm is valid for one exact request fingerprint only.

A session may not substitute:

- another decision ID;
- another strategy;
- another symbol;
- another unit count;
- another reserved-risk amount;
- another stop/target;
- another client-order ID;
- another account/server/provider.

A changed request requires a different future arm.

## 4. Source gate remains locked

DEC-059 does not modify the DEC-058 source constant:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

The official session controller may validate an in-memory arm fixture, perform
source-only readiness/reconciliation work, and build journal records, but any
submission path still delegates to the DEC-058
`GatedMT5DemoMutationAdapter`.

Therefore submission still raises `DemoExecutionLockedError` before any broker
read or mutation.

A later separately approved decision is required to replace the source lock with
a validated real arm.

## 5. Startup reconciliation

Before a session can become source-ready, it requires normalized existing local
request history plus current broker order/position snapshots.

The existing DEC-056 reconciliation contract is reused.

A session is not source-ready when reconciliation reports:

- duplicate client-order IDs;
- unknown broker orders;
- orphan broker positions;
- missing expected protective stops;
- any other unhealthy reconciliation state.

DEC-059 never auto-closes, cancels, or modifies an orphan.

## 6. Daily-halt and order-count guards

The source controller requires:

- `daily_halt_active=false`;
- current UTC time inside the exact arm window;
- zero prior new-order attempts for that arm;
- exact request identity match.

After one send-attempt journal event exists, the arm is spent regardless of the
eventual broker result. Retrying the same arm cannot submit another order.

This prevents ambiguous network outcomes from becoming duplicate orders.

## 7. Fresh preflight requirement

A future submission must run a fresh DEC-057 account/symbol/tick/order-check
cycle immediately before DEC-058 send.

DEC-059 source-ready evidence does not cache or substitute an earlier check.

The send payload remains exactly the freshly checked payload.

## 8. Session journal

DEC-059 defines an append-only, create-only journal:

`fmp-phase9-demo-session-journal-v1`.

Each event binds:

- session-arm fingerprint;
- exact request fingerprint/client-order ID;
- monotonically increasing local sequence number;
- UTC event time;
- event type;
- prior event fingerprint;
- event-specific payload;
- deterministic event fingerprint.

Supported event types are:

- `SESSION_OPENED`;
- `RECONCILIATION_OK`;
- `RECONCILIATION_FAILED`;
- `PREFLIGHT_OK`;
- `PREFLIGHT_FAILED`;
- `SEND_ATTEMPTED`;
- `SEND_RESULT`;
- `POST_SEND_RECONCILIATION_OK`;
- `POST_SEND_RECONCILIATION_FAILED`;
- `SESSION_HALTED`;
- `SESSION_CLOSED`.

Every on-disk append is flushed and fsynced.

A journal begins create-only. Existing paths fail closed.

## 9. Attempt-before-send ordering

Before any future `order_send`, the durable `SEND_ATTEMPTED` event must be
fsynced.

The event binds the exact DEC-057 order-check request/check fingerprints and
exact checked MT5 payload digest.

Only after that durable event may a later approved runner call the mutation
adapter.

This ordering preserves at-most-one ambiguity handling across process loss.

DEC-059 itself never reaches that broker call because the DEC-058 execution gate
remains false.

## 10. Send-result and post-send recovery

A normalized DEC-058 send result must be durably journaled before the session
can be considered closed.

Regardless of retcode, a future real session must then read and reconcile
current broker orders/positions.

- Full `TRADE_RETCODE_DONE` is not sufficient by itself to skip
  reconciliation.
- `PLACED`, partial, timeout, reject, requote, or unknown outcomes remain
  unresolved until reconciliation.
- An unresolved or unhealthy state halts the session and forbids further new
  orders under that arm.

## 11. Session-ready evidence

DEC-059 may build source-only:

`fmp-phase9-demo-session-ready-v1`.

It binds:

- exact arm;
- exact design/request identities;
- healthy startup reconciliation fingerprint;
- `daily_halt_active=false`;
- `new_order_attempt_count=0`;
- `max_new_orders=1`;
- `demo_session_contract_ready=true`;
- `demo_execution_source_armed=false`;
- all live/real-money/Phase-10 authorizations false.

This is readiness evidence only, not an execution authorization.

## 12. CLI boundary

The Phase 9 CLI remains `design-demo` only.

DEC-059 adds no:

- arm-session command;
- run-demo command;
- submit-order command;
- broker command;
- trade command;
- close/cancel/modify command.

No repository script creates a real DEC-059 arm.

## 13. Authorization boundary

DEC-059 may set only:

- `demo_session_contract_ready=true`.

It must keep:

- `demo_execution_source_armed=false`;
- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

## 14. Phase 9 evidence boundary

DEC-059 does not define Phase 9 acceptance thresholds.

A one-order first practice session cannot by itself justify Phase 10. The
project requirement remains that deployment review needs enough demo
trades/time and market regimes to understand execution cost/errors and observe
risk controls rather than relying on a short lucky streak.

## 15. Safety and next gate

Possible EXP-030 source outcomes:

- `PHASE9_DEMO_SESSION_CONTRACT_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome places an order.

A later separately approved decision is mandatory before:

- `DEMO_EXECUTION_SOURCE_ARMED` can change;
- a real arm can be created;
- an operator execution command can exist;
- the first real practice-account order can be sent.
