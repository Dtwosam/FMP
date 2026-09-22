# Phase 8A — Acceptance Review and Shadow-Candidate Freeze

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY DEC-042 SELECTION RESULT
**Decision:** DEC-045
**Experiment:** EXP-20260922-016
**Scope:** Phase 8A acceptance review only; no new market-data search

## 1. Purpose

DEC-042 deliberately ends with `shadow_candidate_authorized = false`. A historical portfolio-selection PASS may identify a preferred multi-strategy set, but it does not itself authorize Phase 8B.

DEC-045 freezes the separate Phase 8A acceptance review required by DEC-039 step 9. The review consumes only exact, already-produced DEC-042 preflight and selection evidence. It does not open new historical data, rerun strategies, change portfolio ranking, or tune thresholds.

## 2. Required inputs

The review requires:

- one successful DEC-042 manual workflow run from `main`;
- exact `preflight.json` and `selection.json` artifacts from that run;
- SHA-256 of both artifact bytes;
- a DEC-042 result bound to the exact preflight digest;
- the exact Phase 7 baseline strategy present as the sole pre-EXP-015 control in the frozen pool;
- a complete DEC-042 set universe and set-result table that deterministically replays to the stored ranked passing sets.

Any identity, digest, ranking, gate, set-universe, lifecycle, or provenance mismatch is `PROTOCOL_FAILURE`.

## 3. Operational definition of “materially improves the economic case”

Before any DEC-042 selection result exists, DEC-045 defines “materially improves the economic case over the Phase 7 single-strategy baseline” as follows:

1. DEC-042 outcome is `PORTFOLIO_SELECTION_PASS`;
2. the selected portfolio contains at least two strategies;
3. the selected portfolio is the first set in the independently recomputed DEC-042 passing-set ranking;
4. every frozen DEC-042 mandatory gate passes for that selected set;
5. the Phase 7 baseline control is evaluated over the same 2019-01-01 inclusive through 2026-08-21 exclusive range and exact 0.2/0.5/1.0-pip cost scenarios;
6. at 0.5-pip adverse slippage, the selected portfolio's annualized compounded return is **strictly greater** than the Phase 7 baseline control's annualized compounded return.

The 0.5-pip comparison is the sole additional economic-improvement gate because 0.5-pip annualized compounded return is already DEC-042's primary ranking metric. No percentage-point hurdle, score weight, leverage change, or post-result margin may be added later.

The review records diagnostic deltas for 0.2/0.5 net return, annualized return, drawdown, profit factor, and trade count, but those diagnostics do not create extra hidden gates.

## 4. Acceptance outcomes

Exactly one outcome is emitted:

### `PHASE8A_SHADOW_CANDIDATE_ACCEPTED`

Emitted only when all DEC-045 acceptance conditions pass.

Consequences:

- selected strategy records transition exactly one lifecycle step from `HISTORICAL_QUALIFIED` to `SHADOW_CANDIDATE`;
- an immutable champion/shadow-candidate set is frozen from the exact selected fingerprints;
- `shadow_candidate_authorized = true`;
- `phase8b_design_authorized = true`;
- Phase 8B may design/capture prospective read-only shadow evidence for this exact candidate set.

This does **not** authorize demo orders, live orders, broker mutation, real-money trading, or Phase 9.

### `PHASE8A_RESEARCH_REJECTED`

Emitted when DEC-042 produced no passing portfolio or when the selected portfolio does not strictly improve the Phase 7 baseline control on the frozen 0.5-pip annualized-return comparison.

Consequences:

- no lifecycle transition;
- no shadow-candidate manifest;
- `shadow_candidate_authorized = false`;
- `phase8b_design_authorized = false`;
- Phase 8B remains locked.

Thresholds may not be relaxed retroactively.

### `PROTOCOL_FAILURE`

Emitted only by hard failure/exception when evidence cannot be verified deterministically. No candidate is authorized.

## 5. Immutable shadow-candidate manifest

For an acceptance outcome, evidence must include:

- exact DEC-042 preflight SHA-256;
- exact DEC-042 selection SHA-256;
- DEC-042 runner commit;
- exact selected strategy fingerprints;
- each selected strategy's immutable identity JSON;
- prior lifecycle/evidence ID;
- resulting `SHADOW_CANDIDATE` lifecycle/evidence ID;
- frozen champion-set ID and champion-set fingerprint;
- exact baseline-control fingerprint;
- selected and baseline 0.5-pip annualized returns;
- strict improvement delta;
- all DEC-042 selected-set gates;
- `promotion_authorized = false`;
- `demo_order_authorized = false`;
- `live_order_authorized = false`;
- `broker_mutation_authorized = false`;
- `real_money_authorized = false`.

## 6. No new historical search

DEC-045 must not:

- download or open Dukascopy source data;
- execute a strategy backtest;
- alter DEC-042 set membership;
- re-rank with new criteria;
- retune strategy parameters;
- change risk or cost assumptions;
- rescue a non-selected portfolio.

It is a deterministic evidence review only.

## 7. Repository acceptance

The acceptance workflow must run from `refs/heads/main`, verify the referenced DEC-042 run came from `main` and the exact DEC-042 workflow path, and run the repository unit/compile checks plus unchanged deterministic Phase 3 acceptance verification before writing an accepted shadow-candidate manifest.

## 8. Safety boundary

Even after `PHASE8A_SHADOW_CANDIDATE_ACCEPTED`:

- MT5 AutoTrading remains OFF;
- Phase 8B is read-only prospective shadow only;
- demo order placement remains LOCKED;
- live order placement remains LOCKED;
- broker mutation remains LOCKED;
- real-money trading remains LOCKED;
- Phase 9 remains LOCKED.

DEC-045 authorizes only Phase 8B shadow design/capture for the exact frozen candidate set.
