# Phase 9 — MT5 Demo Mutation Transport Source Lock

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-058
**Experiment:** EXP-20260922-029
**Depends on:** DEC-055 through DEC-057
**Scope:** mutation-capable MT5 Python transport source behind a hard-disabled execution gate; no demo order execution

## 1. Purpose

DEC-057 proves the exact read/check-only MT5 preflight boundary but deliberately
contains no broker mutation method.

DEC-058 may implement the mutation-capable MT5 Python source required for a
future demo session while keeping the official FMP execution path impossible to
arm under this decision.

The implementation may include:

- normalization of the already-connected MetaTrader5 Python terminal;
- exact DEMO account identity derived from the current terminal login;
- symbol/tick/check reads;
- active-order and open-position reads;
- symbolic-to-MetaTrader5 request translation;
- normalized `order_send` result parsing;
- one gated demo-mutation adapter.

No DEC-058 command or artifact may enable that gate.

## 2. Existing identity continuity

The mutation backend must derive the same account fingerprint as the Phase 8B
quote bridge:

`sha256(str(ACCOUNT_LOGIN))`.

It must read, not accept as caller overrides:

- current terminal login;
- account trade mode;
- server;
- trade permissions;
- symbol contract;
- symbol tick;
- broker order/position state.

The exact accepted DEC-055 design and DEC-056 request remain authoritative.

## 3. MetaTrader5 module boundary

DEC-058 may wrap an already imported/connected MetaTrader5-compatible module.

The wrapper may call:

- `account_info`;
- `symbol_info`;
- `symbol_info_tick`;
- `order_check`;
- `orders_get`;
- `positions_get`;
- `order_send`.

The wrapper must not:

- accept login/password credentials;
- call terminal login functions;
- change AutoTrading;
- select a different provider/server/account;
- persist secrets.

Connection/login lifecycle remains outside DEC-058 source.

## 4. Symbol filling policy

The backend derives one deterministic market-order filling policy from actual
symbol execution properties.

- For non-Market-Execution symbols, use `RETURN`.
- For Market Execution, use FOK when allowed; otherwise IOC when allowed.
- If neither FOK nor IOC is allowed under Market Execution, fail closed.

No caller supplies a filling mode.

## 5. Send request

The send request must be the exact freshly revalidated DEC-057 MT5 request.

The existing DEC-056 client-order ID remains the request comment. DEC-058 adds
no post-check field or price/volume mutation between `order_check` and a
future `order_send`.

No mutation path may resize units, widen/remove stop, alter target, change
symbol, or replace account/server identity.

A fresh DEC-057 account/symbol/tick/order-check cycle is mandatory immediately
before any future send.

## 6. Result normalization

DEC-058 defines:

`fmp-phase9-mt5-demo-send-result-v1`.

It normalizes:

- exact request and order-check fingerprints;
- trade-server retcode;
- external retcode;
- deal ticket;
- order ticket;
- confirmed volume;
- confirmed price;
- returned bid/ask;
- broker comment;
- request ID;
- deterministic result fingerprint.

`TRADE_RETCODE_DONE = 10009` is the only DEC-058 fully-completed result.

`PLACED`, `DONE_PARTIAL`, requote, rejection, timeout, and all other codes
are non-complete and require later reconciliation; DEC-058 does not reinterpret
them as successful completed demo trades.

## 7. Hard execution gate

The official adapter contains a module-level immutable source default:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

There is no DEC-058 builder, CLI flag, environment variable, config file,
artifact, setter, or public method that can change it.

The official `GatedMT5DemoMutationAdapter.submit` checks this gate before
performing any broker read or mutation. While false it raises
`DemoExecutionLockedError`.

Therefore DEC-058 source may know how to call `order_send`, but the FMP
execution path remains disabled.

## 8. Raw backend isolation

The raw MetaTrader5 wrapper is infrastructure, not an authorized FMP execution
entry point.

It is not exposed by the Phase 9 CLI, and no script invokes its `order_send`
method.

Tests may exercise it only against fake in-memory MetaTrader5-compatible
modules.

## 9. Reconciliation

The backend may normalize `orders_get` and `positions_get` results for the
existing DEC-056 reconciliation schema.

Unknown client IDs, orphan positions, duplicate IDs, or missing protective
stops remain fail-closed conditions.

No DEC-058 source automatically closes or modifies an orphan.

## 10. CLI boundary

The Phase 9 CLI remains `design-demo` only.

DEC-058 adds no:

- `run-demo`;
- `submit-order`;
- `order-send`;
- `trade`;
- `close-position`;
- `cancel-order`;
- broker mutation command.

## 11. Authorization boundary

DEC-058 may state only:

- `mt5_mutation_source_ready=true`.

It must keep:

- `demo_execution_authorized=false`;
- `demo_order_authorized=false`;
- `live_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `real_money_authorized=false`;
- `phase10_authorized=false`.

## 12. Safety and next gate

Possible EXP-029 source outcomes:

- `PHASE9_MT5_MUTATION_SOURCE_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome may create a demo order.

A later separately approved decision must explicitly arm demo execution,
define the operator/session ceremony, freeze executable deviation/slippage
limits, and add durable order/fill/reconciliation journals before the first
real practice-account order.
