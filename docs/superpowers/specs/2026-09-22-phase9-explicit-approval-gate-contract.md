# Phase 9 — Explicit Approval Record and Gate-Activation Contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-068
**Experiment:** EXP-20260922-039
**Depends on:** DEC-055 through DEC-067
**Scope:** source-only explicit approval-record schema plus source-only gate-activation contract; no real approval artifact, no execution-gate change, no runner wiring, no broker mutation

## 1. Purpose

DEC-067 freezes the exact first-demo order into a human-reviewable packet and
deterministic authorization challenge.

DEC-068 defines how a future operator approval must be recorded against that
exact challenge and how a future operator build may prove that the approval is
eligible for gate activation.

DEC-068 does not itself approve or execute anything.

Repository source remains:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

## 2. Explicit approval record

The approval protocol is:

`fmp-phase9-first-demo-explicit-approval-v1`.

A valid approval record binds:

- exact DEC-067 authorization-packet fingerprint;
- exact DEC-067 authorization-challenge fingerprint;
- exact DEC-064 execution-permit fingerprint;
- exact request fingerprint and client-order ID;
- exact DEMO account fingerprint and server;
- exact arm not-before and expiry;
- an opaque operator identity reference;
- an opaque operator approval reference;
- approval UTC;
- exact approval statement:
  `APPROVE FIRST DEMO ORDER <authorization_challenge_fingerprint>`;
- approval-record builder code commit;
- deterministic approval-record fingerprint.

The record is practice-only and one-order-only.

## 3. Human-action boundary

The source builder may validate the exact approval statement, but code cannot
authenticate that a human actually reviewed or typed it.

Therefore DEC-068 authorizes only the **schema and validator**.

Repository tests use fixture operator references and fixture approval statements.

No real approval record may be created under DEC-068.

A later explicit operator action must be attributable outside this source-only
test path before an approval record may be treated as real authority.

## 4. Approval timing

Approval UTC must:

- use UTC;
- be at or after the packet's arm not-before UTC;
- be at or after the packet's launch-preflight UTC;
- be no later than the packet's arm expiry UTC.

An approval outside that exact window is invalid.

## 5. Gate-activation contract

The activation protocol is:

`fmp-phase9-demo-gate-activation-contract-v1`.

It consumes exact valid DEC-067 packet plus exact valid DEC-068 approval record
and binds:

- packet fingerprint;
- challenge fingerprint;
- approval-record fingerprint;
- execution-permit fingerprint;
- request/client identity;
- DEMO account/server;
- activation UTC;
- activation-contract builder code commit;
- deterministic activation-contract fingerprint.

Activation UTC must be inside the same immutable arm window and must not precede
approval UTC.

## 6. Source-lock semantics

A valid gate-activation contract means only:

`operator_gate_activation_contract_ready=true`.

It must keep:

- `demo_execution_source_armed=false`;
- `runner_activation_wired=false`;
- `broker_mutation_authorized=false`;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`;
- `phase11_authorized=false`.

DEC-068 adds no setter, environment override, config hook, artifact hook, or CLI
that can change the repository source lock.

## 7. Persistence

Create-only persistence writes:

Approval package:

- `explicit-approval.json`;
- `manifest.json`.

Gate-activation package:

- `gate-activation-contract.json`;
- `manifest.json`.

All manifests preserve the non-execution semantics above.

## 8. Source isolation

DEC-068 must not:

- import MetaTrader5;
- import DEC-058 mutation transport;
- import DEC-065 runner;
- call `order_check` or `order_send`;
- append `SEND_ATTEMPTED`;
- change `execution_gate.py`;
- add an order-capable CLI.

## 9. Next gate

A later separately approved decision is mandatory before:

- a real challenge-bound approval record is created;
- an operator build can make `DEMO_EXECUTION_SOURCE_ARMED=True`;
- the DEC-065 runner is wired to consume the activation contract;
- any real practice-account order is sent.

No real Phase 8B acceptance or Phase 9 artifact chain has been executed yet, so
DEC-068 cannot create a real first-demo approval even in principle from current
repository evidence.
