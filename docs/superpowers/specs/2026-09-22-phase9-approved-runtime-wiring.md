# Phase 9 — Approval-Gated One-Shot Runtime Wiring

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-069
**Experiment:** EXP-20260922-040
**Depends on:** DEC-055 through DEC-068
**Scope:** source-only wiring from exact DEC-068 activation contract to the DEC-065 one-shot runner behind the unchanged hard source gate; no real approval, no CLI, no demo order

## 1. Purpose

DEC-068 defines a challenge-bound explicit-approval record and gate-activation
contract, but deliberately does not wire either artifact to the DEC-065 runner.

DEC-069 may implement that wiring in source only.

Repository source remains:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

No real approval, activation, or practice order is created by DEC-069.

## 2. Exact inputs

The approved runtime path consumes exact valid:

- DEC-055 demo design;
- DEC-056 demo order request;
- DEC-059 session arm/readiness and current journal;
- DEC-060 execution arm;
- DEC-062 runtime authority;
- DEC-063 launch preflight;
- DEC-064 execution permit;
- DEC-067 first-demo authorization packet;
- DEC-068 explicit approval record;
- DEC-068 gate-activation contract.

Every fingerprint and identity must agree through the full chain.

## 3. Immediate runtime checks

Before any journal mutation or backend call, DEC-069 must verify:

- DEC-068 approval and activation validators both pass;
- current UTC is inside the immutable arm window;
- current UTC is not before activation UTC;
- daily halt is inactive;
- journal validates;
- journal event count/tip still match the permit/activation lineage where bound;
- zero prior `SEND_ATTEMPTED`;
- practice-only identity remains true;
- maximum new orders remains exactly one;
- account/server/request/client-order identities remain exact;
- repository source gate is true.

With the repository value still false, runtime fails before broker access and
before journal mutation.

## 4. Delegation boundary

When and only when the source gate is true, DEC-069 delegates to the exact
DEC-065 `run_phase9_demo_one_shot`.

DEC-069 must not duplicate or reinterpret:

- checked MT5 request construction;
- `SEND_ATTEMPTED` journaling;
- send-result normalization;
- retry semantics;
- ambiguity handling;
- post-send reconciliation.

The DEC-065 runner remains authoritative for those behaviors.

## 5. One-shot semantics

DEC-069 adds no retry loop.

A successful call may cause at most one DEC-065 mutation attempt.

Any durable `SEND_ATTEMPTED` spends the arm exactly as already defined by
DEC-059/065.

## 6. Source result

DEC-069 defines:

`fmp-phase9-approved-demo-runtime-v1`.

The wrapper result binds:

- exact gate-activation contract fingerprint;
- exact explicit-approval fingerprint;
- exact authorization packet/challenge fingerprints;
- exact execution-permit fingerprint;
- exact request/client identity;
- activation UTC;
- runtime UTC;
- exact DEC-065 one-shot-run fingerprint;
- final one-shot outcome;
- deterministic approved-runtime fingerprint.

This wrapper does not redefine the one-shot outcome.

## 7. Repository safety

DEC-069 must keep:

- `DEMO_EXECUTION_SOURCE_ARMED=False` in repository source;
- no environment/config/artifact setter for that value;
- no broker-connected or order-capable CLI;
- no automatic creation of approval/activation artifacts;
- no live-order authorization;
- no real-money authorization;
- no Phase-10 or Phase-11 authorization.

Tests may patch the source gate only in-process and may use only fake in-memory
mutation backends.

## 8. No current real execution eligibility

The repository still has no real Phase 8B acceptance/SHADOW_VALIDATED chain and
no real DEC-055-through-068 artifact chain.

Therefore DEC-069 can verify only source behavior. It cannot legitimately run a
real first practice order from current repository evidence.

## 9. Next boundary

After DEC-069, source construction for the first practice-order path is complete.

A later explicit operator action must still:

1. execute the real Phase 8B prospective campaign and achieve acceptance;
2. materialize the exact Phase 9 artifact chain;
3. review the DEC-067 packet;
4. provide the exact DEC-068 approval statement against the actual challenge;
5. produce the activation contract inside the arm window;
6. use a separately approved operator build/runtime in which the source gate is
   intentionally armed.

DEC-069 itself performs none of those real-world actions.
