# Phase 9 — One-Shot Demo Execution Permit Contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-064
**Experiment:** EXP-20260922-035
**Depends on:** DEC-055 through DEC-063
**Scope:** source-only construction, validation, and create-only persistence of one future one-shot demo execution permit; no execution-gate change and no order runner

## 1. Purpose

DEC-063 can prove that the exact runtime-authority arm still has healthy current
practice-account, symbol, quote, order-check, and reconciliation state.

DEC-064 may define the immutable permit artifact a later separately approved
execution runner would require.

DEC-064 does not change:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

It performs no broker access and cannot call `order_send`.

## 2. Permit protocol

The protocol is:

`fmp-phase9-demo-execution-permit-v1`.

It binds exactly:

- DEC-055 demo-design fingerprint;
- DEC-056 request fingerprint and client-order ID;
- DEC-059 session-arm and session-ready fingerprints;
- DEC-060 execution-arm fingerprint;
- DEC-062 runtime-authority fingerprint;
- DEC-063 launch-preflight fingerprint;
- champion-set fingerprint;
- strategy fingerprint;
- symbol;
- accepted DEMO account fingerprint and server;
- exact arm not-before and expiry;
- operator approval reference;
- maximum new orders = 1;
- exact fresh order-check request fingerprint;
- exact fresh order-check result fingerprint;
- exact healthy reconciliation fingerprint;
- exact launch-preflight journal event count and journal-tip fingerprint;
- permit builder code commit;
- deterministic permit fingerprint.

## 3. Required launch state

Construction requires the exact DEC-063 launch preflight to validate against
the exact upstream chain and current journal snapshot.

The launch preflight must state:

- `demo_launch_preflight_ready=true`;
- `order_check_performed=true`;
- `order_send_attempted=false`;
- fresh order check passed;
- fresh reconciliation healthy;
- send-attempt count = 0;
- daily halt inactive;
- source execution gate false;
- all execution/order/mutation/live/real-money/Phase-10 authorization flags
  false.

## 4. Exact checked request

The permit binds the exact DEC-063 order-check request fingerprint and order-check
result fingerprint.

It may not alter:

- symbol;
- side;
- units/volume;
- price;
- protective stop;
- target;
- filling mode;
- client-order ID;
- account/server identity.

No post-check mutation or repair is allowed.

## 5. Window and one-shot semantics

The permit copies the exact DEC-059/060 arm window and one-order cap.

It does not widen or recreate the window.

The permit itself does not spend the arm. A future execution decision must
still durably journal `SEND_ATTEMPTED` before any mutation call, after which
the arm is spent regardless of broker outcome.

## 6. Authorization semantics

A valid DEC-064 artifact means only:

- `demo_execution_permit_artifact_ready=true`.

It must keep:

- `demo_execution_source_armed=false`;
- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

The permit is not runtime execution authority.

## 7. Persistence

DEC-064 may write create-only:

- `execution-permit.json`;
- `manifest.json`.

Existing paths fail closed.

The manifest binds the exact permit fingerprint and byte SHA-256.

## 8. CLI boundary

DEC-064 adds no command.

The Phase 9 CLI remains:

- `design-demo`;
- `materialize-arm`.

No run, submit, trade, order-send, broker, cancel, modify, or close-position
command is introduced.

## 9. Safety and next gate

Possible EXP-035 source outcomes:

- `PHASE9_DEMO_EXECUTION_PERMIT_CONTRACT_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome sends or authorizes an order.

A later separately approved decision is mandatory before:

- a real execution runner may consume the permit;
- `DEMO_EXECUTION_SOURCE_ARMED` may become true or be superseded by a
  permit-gated mutation path;
- the first real practice-account order can be sent.
