# Phase 9 — Demo Campaign Evidence and Acceptance Contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 9 DEMO ORDER
**Decision:** DEC-066
**Experiment:** EXP-20260922-037
**Depends on:** DEC-055 through DEC-065
**Scope:** source-only demo campaign evidence schema and deterministic acceptance compiler; no demo execution, broker mutation, or execution-gate change

## 1. Purpose

The Phase 9 source now reaches a permit-aware one-shot runner, but the project
has never frozen the amount and quality of demo evidence required before a
Phase 10 deployment review.

DEC-066 freezes that gate before any real practice-account order is sent.

It implements only:

- a canonical aggregate demo-campaign evidence contract;
- deterministic validation;
- deterministic acceptance outcomes;
- create-only acceptance artifacts.

It does not create demo observations, enable execution, access MetaTrader5, or
submit an order.

## 2. Source-of-truth basis

The master specification requires the demo stage to accumulate enough
trades/time/regimes to compare practice execution with research assumptions and
verify risk controls.

The build order requires reliable demo execution over enough trades/time to
compare actual execution costs and operational behavior with research
assumptions.

DEC-066 operationalizes those qualitative requirements before results exist.

## 3. Demo campaign evidence protocol

The aggregate evidence protocol is:

`fmp-phase9-demo-campaign-evidence-v1`.

It binds at minimum:

- exact DEC-055 demo-design fingerprint;
- exact frozen champion-set fingerprint;
- exact sorted strategy fingerprints;
- exact accepted DEMO account fingerprint and server;
- first and last accepted demo observation UTC;
- exact sorted demo-session dates;
- completed practice-trade count;
- completed-trade strategy-family representation;
- completed-trade V1-pair representation;
- order-attempt count;
- completed-send count;
- broker-returned non-completed send count;
- ambiguous-send count;
- retry-after-send-attempt count;
- duplicate-client-order count;
- unprotected-position count;
- startup/post-send reconciliation failure count;
- practice-account assertion failure count;
- daily-halt violation count;
- journal-integrity failure count;
- unauthorized broker-mutation count;
- live-order count;
- real-money access count;
- restart/recovery drill count and failure count;
- per-pair actual entry-slippage summary;
- diagnostic realized return, expectancy, profit factor, maximum drawdown, and
  equity series identity;
- exact campaign-evidence builder code commit;
- deterministic campaign-evidence fingerprint.

No financial metric is a DEC-066 PASS gate. Phase 10 remains the place where
the combined research/shadow/demo economic record is reviewed.

## 4. Minimum evidence gate

Before operational/cost acceptance is evaluated, all of these minimums are
required:

- at least **40 completed practice trades**;
- at least **8 elapsed calendar weeks** between first and last accepted demo
  observations;
- at least **30 distinct demo-session dates**;
- at least **2 strategy families** represented by completed practice trades;
- at least **2 V1 pairs** represented by completed practice trades.

These deliberately match the Phase 8B minimum evidence scale where applicable,
so Phase 9 cannot advance on a materially smaller sample after moving closer to
real execution.

If structural evidence is sound but a sample minimum is not reached, outcome is:

`PHASE9_DEMO_NEED_MORE_DATA`.

This outcome is non-terminal.

## 5. Structural safety gate

Any of the following is an immediate:

`PHASE9_DEMO_REJECT_SAFETY_FAILURE`.

PASS requires:

- exact practice-account identity for every order session;
- zero live-order events;
- zero real-money account access;
- zero unauthorized broker mutations;
- zero duplicate client-order submissions;
- zero retry after a durable `SEND_ATTEMPTED`;
- zero completed sends lacking confirmed protective-stop protection;
- zero daily-halt violations.

A broker-returned rejection is not by itself a safety failure if the one-shot
arm was correctly spent and no retry occurred.

## 6. Operational integrity gate

After minimum evidence is reached, PASS requires:

- zero journal-integrity failures;
- zero unresolved ambiguous sends;
- zero startup reconciliation failures;
- zero post-send reconciliation failures;
- at least one deliberate restart/recovery drill;
- zero restart/recovery drill failures;
- completed-send count + broker-returned non-completed send count +
  ambiguous-send count = order-attempt count;
- completed-trade count <= completed-send count;
- every completed send has exact requested-vs-fill evidence;
- all represented pairs have non-empty execution-cost samples.

Failure is:

`PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH`.

## 7. Execution-cost parity gate

Actual entry slippage is measured from the exact DEC-063 checked request price
to the confirmed DEC-058 fill price.

Per completed send:

- LONG adverse slippage pips =
  `max(0, (fill_price - checked_price) / pip_size)`;
- SHORT adverse slippage pips =
  `max(0, (checked_price - fill_price) / pip_size)`.

For every represented V1 pair, using completed sends only:

- median adverse entry slippage <= **0.5 pip**;
- nearest-rank p95 adverse entry slippage <= **1.0 pip**.

The 0.5-pip threshold is the existing adverse-slippage scenario used as the
primary realistic research comparison; 1.0 pip is the existing diagnostic
stress scenario.

A represented pair with completed sends but missing slippage evidence fails
closed.

Failure is:

`PHASE9_DEMO_REJECT_EXECUTION_COST_MISMATCH`.

## 8. Diagnostic financial evidence

DEC-066 records but does not gate on:

- demo net return;
- expectancy per completed trade;
- profit factor;
- maximum drawdown;
- win rate;
- average win/loss;
- pair/strategy concentration;
- risk-control events.

This prevents short-run demo market luck from becoming a hidden promotion rule.

Phase 10 must review these diagnostics together with historical, walk-forward,
shadow, execution-cost, tail-event, and operational evidence.

## 9. PASS outcome

A full PASS outcome is:

`PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW`.

PASS authorizes only creation of a Phase 10 deployment-review package for the
exact frozen champion/demo campaign.

PASS does not authorize:

- live trading;
- real-money trading;
- a Phase 11 execution adapter;
- a live order;
- automatic strategy promotion;
- automatic champion-set replacement.

## 10. Deterministic outcome precedence

Outcome precedence is frozen:

1. malformed/tampered input -> protocol failure;
2. structural safety failure -> `PHASE9_DEMO_REJECT_SAFETY_FAILURE`;
3. sample minimum not reached -> `PHASE9_DEMO_NEED_MORE_DATA`;
4. operational integrity failure -> `PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH`;
5. execution-cost parity failure -> `PHASE9_DEMO_REJECT_EXECUTION_COST_MISMATCH`;
6. otherwise -> `PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW`.

No threshold may be changed after demo observations are visible for the
campaign under review.

## 11. Acceptance artifact

The acceptance protocol is:

`fmp-phase9-demo-acceptance-v1`.

It binds:

- exact campaign-evidence fingerprint;
- exact champion/demo/account identity;
- every frozen threshold;
- minimum-evidence checks;
- safety checks;
- operational checks;
- execution-cost checks;
- diagnostic financial metrics;
- deterministic outcome;
- acceptance-compiler code commit;
- deterministic acceptance fingerprint.

Create-only persistence writes:

- `acceptance.json`;
- `manifest.json`.

## 12. CLI boundary

DEC-066 adds no broker-connected or order-capable CLI.

It may expose only a future source-free acceptance compilation function; no
real demo campaign exists yet, so repository verification uses fixture
evidence only.

## 13. Safety and next gate

DEC-066 keeps:

`DEMO_EXECUTION_SOURCE_ARMED = False`.

No real demo order, broker mutation, live order, real-money action, Phase 10
decision, or Phase 11 authorization occurs under this decision.

After DEC-066, a separately approved first-demo execution authorization is
still required before the first real practice-account order may be sent.
