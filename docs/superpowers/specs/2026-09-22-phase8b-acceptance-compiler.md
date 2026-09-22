# Phase 8B — Acceptance Compiler and Prospective Evidence Contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
**Decision:** DEC-051
**Experiment:** EXP-20260922-022
**Scope:** source-free acceptance compiler and exact future campaign-evidence schema; no live capture command

## 1. Purpose

DEC-050 produces deterministic source-free segment/replay evidence from finite
capture-record sequences, but deliberately marks those segments as not yet
prospective campaign evidence.

DEC-051 freezes the exact evidence contract and deterministic acceptance
compiler that a future live capture runtime must satisfy before any Phase 8B
portfolio may advance from `SHADOW_CANDIDATE` to `SHADOW_VALIDATED`.

DEC-051 does not itself start capture or fabricate prospective evidence.

## 2. Required inputs

Acceptance consumes exactly:

1. one valid `fmp-phase8b-campaign-evidence-v1` artifact produced by a future
   approved live capture/close process;
2. one valid `fmp-phase8b-spread-reference-v1` artifact frozen before the
   accepted campaign observations are reviewed.

Both inputs are fingerprinted and must bind the exact champion-set fingerprint,
required symbols, cost scenarios, and DEC-049 capture-preflight fingerprint.

The campaign evidence must also bind one exact DEC-050 aggregate
`fmp-phase8b-segment-v1` fingerprint and its exact replay fingerprint, with
`replay_match = true`.

## 3. Prospective campaign-evidence contract

The future live runtime must supply, at minimum:

- `prospective_evidence = true`;
- exact campaign start and first/last accepted observation UTC timestamps;
- exact DEC-049 capture-preflight fingerprint;
- exact DEC-050 segment/replay fingerprints;
- exact champion set and strategy fingerprints;
- exact required symbol set;
- exact 0.2 / 0.5 / 1.0-pip scenarios;
- denominator London dates;
- fully observed London dates;
- completed 0.2-pip scorable trade count;
- same candidate sequence across all scenarios;
- structural no-order safety result;
- malformed-message silent-accept count;
- stale-gap trades admitted to financial metrics count;
- durable operational-event completeness result;
- p99 local processing latency in milliseconds;
- entry- and scheduled-exit deadline violation counts;
- per-scenario financial metrics;
- completed-trade strategy-family and pair representation;
- per-symbol live entry/exit spread summary.

The compiler does not infer missing fields. Missing, malformed, duplicated, or
identity-inconsistent evidence fails closed.

## 4. Minimum evidence gate

Before terminal acceptance/rejection is evaluated, all of these minimums are
required:

- at least 40 completed financially scorable 0.2-pip trades;
- at least 8 elapsed calendar weeks between first and last accepted observation;
- at least 30 fully observed London dates;
- at least two strategy families represented by completed scored trades;
- at least two V1 pairs represented by completed scored trades.

If structural/replay/integrity evidence is sound but one or more of these
sample minimums is not reached, the outcome is
`PHASE8B_NEED_MORE_DATA`.

This outcome is non-terminal and does not change lifecycle state.

## 5. Structural safety

Any structural no-order failure is:

`PHASE8B_REJECT_SAFETY_FAILURE`.

PASS requires the campaign evidence to state and fingerprint that:

- no broker order surface was available to the runtime;
- MT5 bridge role remained quote-only;
- no demo/live order was submitted;
- no broker position/order mutation occurred;
- no real-money path was invoked.

## 6. Operational integrity and timing

After minimum-evidence eligibility is reached, PASS requires:

- at least 90% of denominator London dates are fully observed;
- zero malformed provider/bridge records silently accepted;
- zero stale-gap outcomes included in financial metrics;
- every disconnect/reconnect/stale operational event durably logged;
- same candidate sequence across all three cost scenarios;
- replay match is true;
- p99 local processing latency <= 250 ms;
- zero scored entry deadline violations;
- zero scored scheduled-exit deadline violations.

Failure is `PHASE8B_REJECT_OPERATIONAL_MISMATCH`.

## 7. Spread parity

The frozen spread reference must cover the exact required symbol set.

For every required symbol with at least one scored live spread observation:

- live median entry spread <= historical median entry spread + 0.5 pip;
- live p95 entry spread <= historical p95 entry spread + 0.5 pip;
- live median exit spread <= historical median exit spread + 0.5 pip;
- live p95 exit spread <= historical p95 exit spread + 0.5 pip.

A live symbol with scored trades but missing spread samples fails closed.

Failure is `PHASE8B_REJECT_MARKET_MISMATCH`.

The 0.5-pip tolerance is frozen before any Phase 8B result and cannot widen
after observation.

## 8. Financial behavior

At both 0.2 and 0.5 pips adverse slippage/fill, PASS requires:

- net return > 0;
- expectancy per completed trade > 0;
- profit factor > 1.0;
- maximum drawdown fraction <= 0.05.

The 1.0-pip scenario remains diagnostic.

Failure is `PHASE8B_REJECT_FINANCIAL_MISMATCH`.

## 9. PASS outcome and lifecycle boundary

A full PASS outcome is:

`PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN`.

PASS may authorize only:

- exact frozen champion strategy lifecycle transition
  `SHADOW_CANDIDATE -> SHADOW_VALIDATED`;
- creation of a separate Phase 9 demo-design proposal.

PASS does not authorize:

- demo order placement;
- live order placement;
- broker mutation;
- real-money trading;
- automatic Phase 9 execution;
- champion-set hot swap.

The acceptance artifact must keep all order/broker/real-money authorization
flags false.

## 10. Deterministic outcome precedence

Outcome precedence is frozen:

1. malformed/tampered input -> protocol failure;
2. structural safety failure -> `PHASE8B_REJECT_SAFETY_FAILURE`;
3. replay/integrity defect -> `PHASE8B_REJECT_OPERATIONAL_MISMATCH`;
4. sample minimum not reached -> `PHASE8B_NEED_MORE_DATA`;
5. operational/timing gate failure -> `PHASE8B_REJECT_OPERATIONAL_MISMATCH`;
6. spread parity failure -> `PHASE8B_REJECT_MARKET_MISMATCH`;
7. financial gate failure -> `PHASE8B_REJECT_FINANCIAL_MISMATCH`;
8. otherwise -> `PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN`.

No post-result threshold change or rescue rule is allowed.

## 11. CLI boundary

DEC-051 adds no live capture command.

The acceptance compiler is a pure source-free API. A future separately frozen
live capture/close protocol must create the exact prospective campaign-evidence
artifact before review can run.

No `capture`, `run`, or broker execution command is added under DEC-051.

## 12. Safety

Throughout DEC-051:

- no Phase 8B live-shadow segment is started;
- no demo/live orders;
- no broker mutation;
- no real-money trading;
- Phase 9 execution remains locked;
- active champion mutation remains locked until an exact PASS artifact exists.

Possible EXP-022 outcomes are exactly the acceptance outcomes in Sections 4–9
or `PROTOCOL_FAILURE`.
