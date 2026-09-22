# Phase 9 — Demo Order Protocol and Locked Adapter Foundation

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-056
**Experiment:** EXP-20260922-027
**Depends on:** DEC-055 Phase 9 demo design
**Scope:** source-only request/journal/reconciliation contracts and structurally locked adapter; no MT5 mutation implementation

## 1. Purpose

DEC-055 freezes what a future MT5 demo adapter must look like, but intentionally
contains no order-capable source.

DEC-056 implements only the deterministic protocol boundary that sits before
any future MT5 mutation transport:

- validated post-risk demo order requests;
- deterministic client order IDs;
- protective-stop requirements;
- dry-run journal evidence;
- reconciliation snapshot contracts;
- restart/idempotency identities;
- an adapter whose submission method is structurally locked and has no broker
  transport dependency.

No demo or live order can be submitted under DEC-056.

## 2. Exact design prerequisite

Every request requires one exact valid
`fmp-phase9-demo-design-v1` artifact.

The design must still state:

- `demo_adapter_source_authorized=true`;
- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

DEC-056 must not weaken those flags.

## 3. Request source

A future demo request is built only from an existing Phase 3 `OrderIntent`
that has already passed the unchanged Phase 3 risk engine.

The request requires:

- directional LONG/SHORT intent;
- positive units;
- positive reserved-risk amount;
- required approved symbol;
- mandatory protective stop;
- optional target;
- exact decision timestamp;
- exact earliest executable timestamp;
- exact immutable strategy fingerprint from the accepted champion set.

The request may not create or alter position size itself.

## 4. Deterministic client order identity

The protocol is:

`fmp-phase9-demo-order-request-v1`.

The deterministic client order ID binds:

- exact Phase 9 demo-design fingerprint;
- exact champion-set fingerprint;
- exact strategy fingerprint;
- exact decision ID;
- symbol and direction;
- units;
- stop/target;
- decision timestamp;
- earliest executable timestamp.

The externally visible client order ID is:

`fmp9-<first-24-hex-of-request-identity-sha256>`.

The full request also carries the complete identity SHA-256.

Repeated construction of the same exact input must produce byte-identical
request payloads and the same client order ID.

## 5. Practice identity

Every request copies, never overrides:

- DEMO account mode;
- exact accepted account fingerprint;
- exact accepted demo server;
- exact approved symbol mapping;
- exact provider identity.

No caller may supply a different account/server/provider.

## 6. Protective stop

A request without a protective stop is invalid.

Stop geometry is direction-aware relative to the supplied
`reference_entry_price` used only for request validation:

- LONG stop < reference price;
- SHORT stop > reference price.

If a target exists:

- LONG target > reference price;
- SHORT target < reference price.

Reference price is not a fill and creates no broker action.

## 7. Dry-run journal

DEC-056 defines:

`fmp-phase9-demo-dry-run-v1`.

A dry-run record binds:

- exact request fingerprint and client order ID;
- exact design fingerprint;
- validation result;
- `submission_attempted=false`;
- `broker_mutation_attempted=false`;
- `demo_order_submitted=false`;
- `live_order_submitted=false`;
- deterministic dry-run fingerprint.

Dry-run evidence is create-only when written to disk.

## 8. Reconciliation snapshot schema

DEC-056 defines:

`fmp-phase9-demo-reconciliation-v1`.

The source-only snapshot can represent caller-supplied normalized broker-state
fixtures for tests and future transport integration, but DEC-056 performs no
broker read.

The snapshot binds:

- design/account/server identities;
- deterministic sorted local request/client-order IDs;
- deterministic sorted normalized broker order IDs;
- deterministic sorted normalized broker position IDs;
- duplicate client-order IDs;
- unknown broker order IDs;
- orphan broker position IDs;
- missing expected protective-stop IDs;
- `healthy=true` only when all discrepancy sets are empty;
- deterministic reconciliation fingerprint.

This schema freezes future restart/recovery behavior before a transport exists.

## 9. Structurally locked adapter

`LockedDemoOrderAdapter` has no MT5/broker transport field.

It may:

- validate a request;
- create dry-run evidence;
- create reconciliation evidence from already supplied normalized fixtures.

Its `submit` method always raises `DemoExecutionLockedError`.

There is no alternate submission method.

## 10. CLI boundary

DEC-056 adds no order-capable CLI.

No `run-demo`, `submit-order`, `trade`, broker, or mutation command is
introduced.

## 11. Authorization boundary

DEC-056 may set only:

- `demo_adapter_protocol_ready=true`.

It must keep:

- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `live_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

## 12. Safety

Possible EXP-027 source outcomes:

- `PHASE9_DEMO_ORDER_PROTOCOL_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome can submit an order.

A later separately frozen decision is mandatory before any MT5 mutation
transport can be implemented, wired, or enabled.
