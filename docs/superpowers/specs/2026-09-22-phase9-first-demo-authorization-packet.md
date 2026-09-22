# Phase 9 — First Demo Authorization Packet Contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-067
**Experiment:** EXP-20260922-038
**Depends on:** DEC-055 through DEC-066
**Scope:** source-only immutable human-review packet for the exact first practice order; no execution approval, no source-gate change, no broker mutation

## 1. Purpose

DEC-064 freezes an immutable one-shot execution permit and DEC-065 implements a
permit-aware runner behind the hard DEC-058 source lock. The remaining source
gap before an explicit first-demo execution decision is a single immutable
operator-review object that presents the exact practice order in human-readable
form and binds it to one approval challenge.

DEC-067 fills only that gap.

It does not record approval and does not change:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

## 2. Exact upstream binding

The packet consumes exact valid:

- DEC-055 demo design;
- DEC-056 demo order request;
- DEC-059 session arm and session-ready evidence;
- DEC-060 execution arm;
- DEC-062 runtime authority;
- DEC-063 launch preflight;
- DEC-064 execution permit.

The packet reuses the DEC-064 validator and may not relax or reinterpret any
upstream identity.

## 3. Human-review summary

The packet must expose without semantic override:

- DEMO account fingerprint and server;
- champion-set fingerprint;
- strategy fingerprint, family, and timeframe;
- symbol and broker symbol;
- direction;
- requested units;
- MT5 volume in lots;
- reserved risk in USD;
- original reference entry price;
- fresh checked MT5 price;
- protective stop;
- optional target;
- fill mode and time-in-force;
- deterministic client-order ID;
- decision timestamp and earliest executable timestamp;
- launch-preflight timestamp;
- arm not-before and expiry;
- existing session operator reference;
- exact checked MT5 request SHA-256;
- exact execution-permit fingerprint.

No value above may be supplied separately by a caller.

## 4. Demo-campaign obligations

The packet also binds the already-frozen DEC-066 acceptance contract:

- minimum completed trades = 40;
- minimum elapsed weeks = 8;
- minimum demo-session dates = 30;
- minimum represented strategy families = 2;
- minimum represented V1 pairs = 2;
- maximum median adverse entry slippage = 0.5 pip;
- maximum nearest-rank p95 adverse entry slippage = 1.0 pip.

These are context for the operator: one first demo order cannot itself qualify
the system for Phase 10.

## 5. Approval challenge

DEC-067 defines a deterministic:

`authorization_challenge_fingerprint`.

It hashes the immutable human-review payload before any approval fields are
added.

A later separately approved decision may record explicit approval only by
binding to this exact challenge fingerprint and exact packet fingerprint.

Changing any account/order/risk/price/stop/target/window/permit detail creates a
different challenge and requires a new explicit approval.

## 6. Non-authorization semantics

A valid packet means only:

`first_demo_authorization_packet_ready=true`.

It must keep:

- `explicit_execution_approval_recorded=false`;
- `demo_execution_source_armed=false`;
- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`;
- `phase11_authorized=false`.

The DEC-065 runner must not consume this packet.

## 7. Source isolation

DEC-067 must not:

- import MetaTrader5;
- import or instantiate the DEC-058 mutation adapter;
- call `order_check` or `order_send`;
- append `SEND_ATTEMPTED`;
- create a real execution arm or permit;
- expose a broker-connected command.

Repository tests may use fixture artifacts only.

## 8. Persistence

The packet protocol is:

`fmp-phase9-first-demo-authorization-packet-v1`.

Create-only persistence writes:

- `first-demo-authorization-packet.json`;
- `manifest.json`.

The manifest binds exact packet and approval-challenge fingerprints and keeps all
execution/live/real-money authorization flags false.

## 9. CLI boundary

DEC-067 adds no execution-capable command.

The existing Phase 9 CLI remains unchanged.

## 10. Next gate

After DEC-067, a separately approved DEC-068-style decision would still be
required to record explicit human approval against the exact challenge and to
define how an operator build may enable the source gate.

DEC-067 itself cannot send the first practice order.
