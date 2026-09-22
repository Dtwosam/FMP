# Phase 9 — Offline Demo Arm Materialization

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-061
**Experiment:** EXP-20260922-032
**Depends on:** DEC-055 through DEC-060
**Scope:** local-only operator materialization of one exact DEC-060 execution-arm package; no MT5 access and no execution-gate change

## 1. Purpose

DEC-060 defines the future execution-arm artifact contract but intentionally
provides no operator command that can materialize one.

DEC-061 may add one local-only command that reads already-frozen JSON artifacts,
revalidates every upstream identity, builds the exact DEC-060 arm package, and
writes it create-only.

DEC-061 still does not change:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

It does not import or instantiate the MetaTrader5 backend, perform broker reads,
run `order_check`, call `order_send`, or submit any order.

## 2. Command

DEC-061 adds only:

`materialize-arm --design <path> --request <path> --session-arm <path> --session-ready <path> --out-dir <path>`

All inputs are local JSON artifact paths.

The command exposes no semantic override for:

- symbol;
- strategy;
- units;
- reserved risk;
- stop or target;
- account fingerprint;
- server;
- provider;
- client-order ID;
- arm window;
- approval reference;
- order count.

## 3. Exact validation

The command must parse each input as one JSON object and call the exact DEC-055,
DEC-056, DEC-059, and DEC-060 validators.

The DEC-060 builder remains authoritative.

Any fingerprint mismatch, identity substitution, changed arm window, changed
approval reference, spent arm, daily-halt state, or source-gate drift fails
closed before output creation.

## 4. Output

The command writes only the DEC-060 create-only artifact set:

- `execution-arm.json`;
- `manifest.json`.

The target directory must not already contain either file.

CI and repository tests may materialize only temporary fixture artifacts.

No real operator arm is created by this decision or by repository verification.

## 5. Source isolation

The DEC-061 `src/fmp/phase9/cli.py` module and its
`materialize-arm` handler may import only local artifact/validation modules.

They may not directly import or instantiate:

- `MetaTrader5`;
- `MetaTrader5PythonDemoBackend`;
- a broker mutation adapter/backend;
- any order-send runner.

The broader `fmp.phase9` package may continue to re-export already-approved
DEC-058 source symbols, but the DEC-061 command path must not reference or call
them.

The command therefore remains usable without a trading terminal or broker
connection.

## 6. Authorization semantics

Successful materialization means only:

- `demo_execution_arm_artifact_ready=true`.

It must still report:

- `demo_execution_source_armed=false`;
- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

## 7. Existing CLI

After DEC-061 the Phase 9 CLI may expose:

- `design-demo`;
- `materialize-arm`.

It still exposes no:

- `run-demo`;
- `submit-order`;
- `trade`;
- `broker`;
- `order-send`;
- `cancel`;
- `close-position`;
- `modify-order`.

## 8. Safety and next gate

Possible EXP-032 source outcomes:

- `PHASE9_DEMO_ARM_MATERIALIZER_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome changes the execution source gate or touches a broker.

A later separately approved decision is mandatory before:

- an execution arm can be accepted as runtime authority;
- `DEMO_EXECUTION_SOURCE_ARMED` can become true;
- a broker-connected runner may exist;
- the first real practice-account order can be sent.
