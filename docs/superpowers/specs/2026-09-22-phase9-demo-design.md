# Phase 9 — Demo Design Proposal

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-055
**Experiment:** EXP-20260922-026
**Scope:** source-only demo architecture freeze after exact Phase 8B PASS; no demo order submission

## 1. Purpose

Phase 8B PASS authorizes only eligibility for a separate demo-design proposal.
DEC-055 freezes that proposal boundary.

No real Phase 8B acceptance result exists when this decision is approved.

DEC-055 may compile a design only from one exact terminal DEC-054 PASS review.
It does not implement, enable, or invoke any order bridge.

## 2. Exact prerequisites

The design command is:

`design-demo --campaign-dir <path> --review-id <sha256>`

It requires:

- exact valid DEC-049 capture preflight;
- exact DEC-054 review directory;
- exact DEC-051 acceptance artifact with
  `PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN`;
- exact DEC-054 `fmp-phase8b-shadow-validation-v1`;
- exact campaign terminal marker for the same review/outcome;
- exact unchanged champion-set fingerprint and sorted strategy fingerprints.

Any identity mismatch fails closed.

## 3. Demo execution path

DEC-055 selects the MT5 demo continuity path only when the accepted Phase 8B
preflight proves:

- provider = `FP_MARKETS_MT5_DEMO`;
- transport = `MT5_FILE_COMMON_JSONL`;
- connector protocol = the frozen Phase 8B MT5 demo quote protocol;
- one common demo account fingerprint;
- one approved demo server;
- exact required symbols.

The design does not claim that quote access itself authorizes trading.

OANDA is not selected in DEC-055 because the accepted campaign identity is MT5.
Changing execution provider requires a new separately frozen design decision.

## 4. Future order-bridge boundary

The proposed future order bridge protocol is:

`fmp-mt5-demo-order-bridge-v1`

It must be implemented only under a later decision.

The future bridge must reject any account mode other than DEMO and must bind:

- exact accepted account fingerprint;
- exact accepted demo server;
- exact required symbols;
- deterministic client order IDs;
- order request / validation / acknowledgement / fill / rejection envelopes;
- requested-vs-fill price and slippage;
- mandatory protective stop;
- optional target when supplied by strategy;
- exact decision/strategy/champion identities;
- reconciliation snapshots;
- restart/recovery state;
- daily-halt state;
- source code commit and protocol version.

## 5. Risk controls

The design reuses the unchanged Phase 3 `RiskConfig` as source-of-truth.

No Phase 9 design field may widen:

- default per-trade risk fraction;
- simultaneous reserved-risk ceiling;
- daily loss halt;
- sizing semantics.

A later demo adapter may be more conservative, but cannot exceed the frozen
Phase 3 risk configuration without a new decision.

## 6. Practice-account assertion

Any future demo order adapter must verify before every order-capable session:

- account fingerprint exactly equals the accepted Phase 8B demo account;
- server exactly equals the accepted demo server;
- account mode is DEMO;
- required symbols map exactly to approved MT5 symbols.

Mismatch disables order submission and records a protocol failure.

## 7. Protective stops and reconciliation

Every future directional demo order requires a valid stop from the accepted
decision.

The future adapter must support:

- stop attached atomically when MT5 semantics permit;
- otherwise immediate fail-closed protective-stop placement before the position
  can be considered reconciled;
- no unprotected position accepted as healthy state;
- startup reconciliation of broker positions/orders against local journal;
- duplicate-client-order prevention;
- explicit orphan/unknown-position failure state.

DEC-055 implements none of these broker actions; it freezes the required design.

## 8. Secrets

The design permits no credential or account secret in Git.

Future adapter credentials/session data must come from operator-controlled
runtime configuration and must never be serialized into evidence artifacts.

## 9. Artifact

A valid design uses:

`fmp-phase9-demo-design-v1`

and outcome:

`PHASE9_DEMO_DESIGN_FROZEN`.

It binds:

- exact review ID and acceptance/shadow-validation fingerprints;
- exact preflight/champion/strategy identities;
- selected MT5 demo provider/account/server/symbol identities;
- exact Phase 3 risk config;
- future order-bridge protocol;
- required controls;
- design code commit;
- deterministic design fingerprint.

## 10. Authorization boundary

A valid DEC-055 design may set only:

- `demo_adapter_source_authorized = true`.

It must keep:

- `demo_execution_authorized = false`;
- `demo_order_authorized = false`;
- `live_order_authorized = false`;
- `broker_mutation_authorized = false`;
- `real_money_authorized = false`;
- `phase10_authorized = false`.

No AutoTrading state is changed.

## 11. CLI boundary

DEC-055 adds only `design-demo`.

It adds no:

- `run-demo`;
- `order`;
- `trade`;
- broker mutation command;
- live execution command.

## 12. Safety

Possible EXP-026 source outcomes:

- `PHASE9_DEMO_DESIGN_FROZEN`;
- `PROTOCOL_FAILURE`.

Neither outcome submits a demo or live order.
