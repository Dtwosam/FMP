# Phase 9 — Demo Execution Arm Artifact Source Contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-060
**Experiment:** EXP-20260922-031
**Depends on:** DEC-055 through DEC-059
**Scope:** source-only construction, validation, and create-only persistence of one exact demo-execution arm package; DEC-058 execution source lock remains false

## 1. Purpose

DEC-059 freezes the one-request, one-order demo-session contract but deliberately
creates no real arm artifact and leaves the DEC-058 source lock false.

DEC-060 may implement the artifact contract that a future operator-approved
demo execution decision would consume.

DEC-060 does not change:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

It does not submit an order, access MetaTrader5, expose a broker-connected CLI,
or create a real arm during repository verification.

## 2. Arm-package protocol

The source-only execution-arm package is:

`fmp-phase9-demo-execution-arm-v1`.

It binds exactly:

- DEC-055 demo-design fingerprint;
- DEC-056 request fingerprint;
- DEC-056 client-order ID;
- DEC-059 session-arm fingerprint;
- DEC-059 session-ready fingerprint;
- champion-set fingerprint;
- strategy fingerprint;
- symbol;
- accepted DEMO account fingerprint;
- accepted demo server;
- UTC not-before and expiry;
- operator approval reference;
- maximum new orders = 1;
- execution-arm builder code commit;
- deterministic arm fingerprint.

No caller may override the bound strategy, symbol, account, server, units,
reserved risk, stop, target, client ID, or risk-day window.

## 3. Required source state

A DEC-060 package may be built only when:

- the exact DEC-059 session arm validates;
- the exact DEC-059 session-ready artifact validates;
- session-ready binds the same arm/design/request;
- startup reconciliation was healthy;
- daily halt was inactive at readiness;
- new-order attempt count was zero;
- the one-order cap is exactly one;
- the DEC-058 source constant remains false.

If the source execution gate is already true, DEC-060 construction fails
closed because source verification may not run in an already armed tree.

## 4. Time window

The execution-arm package copies the exact DEC-059 not-before and expiry values.

It may not widen, move, or recreate the window.

The window remains inside one UTC civil date.

DEC-060 source construction does not require wall-clock time to be inside the
window; future activation must perform that check again immediately before any
broker access.

## 5. Approval reference

DEC-060 copies the exact operator-approval reference from DEC-059.

It does not invent or auto-generate approval.

The approval reference is evidence identity only and is not a credential.

No password, token, terminal login, API key, or secret may appear in the arm
artifact.

## 6. Authorization semantics

A valid DEC-060 package means only:

- `demo_execution_arm_artifact_ready=true`.

It must keep:

- `demo_execution_source_armed=false`;
- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

The artifact is therefore not sufficient to call the mutation adapter.

## 7. Create-only persistence

DEC-060 defines create-only artifacts:

- `execution-arm.json`;
- `manifest.json`.

Existing paths fail closed.

The manifest binds the exact execution-arm fingerprint and byte SHA-256.

No repository test or CI workflow writes an operator arm into a persistent
campaign directory.

## 8. Offline handoff check

DEC-060 may validate an execution-arm package against exact design/request,
session-arm, and session-ready inputs.

The validator must detect:

- identity substitution;
- approval-reference substitution;
- widened time window;
- changed order cap;
- changed account/server;
- changed source-gate flags;
- fingerprint tampering.

## 9. CLI boundary

DEC-060 adds no arming, execution, broker, or order-capable CLI command.

The Phase 9 CLI remains design-only.

A later separately approved decision is required before an operator command may
materialize a real arm or before any source gate can change.

## 10. Safety and next gate

Possible EXP-031 source outcomes:

- `PHASE9_DEMO_EXECUTION_ARM_CONTRACT_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome places or authorizes an order.

A later separately approved decision is mandatory before:

- a real arm artifact is created for an operator session;
- `DEMO_EXECUTION_SOURCE_ARMED` can become true;
- an operator execution command exists;
- the first real practice-account order can be sent.
