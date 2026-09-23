# Phase 8B — Prospective Campaign Progress Preview

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
**Decision:** DEC-071
**Experiment:** EXP-20260923-042
**Depends on:** DEC-051 through DEC-054 and DEC-070
**Scope:** read-only progress preview over existing closed prospective segments; no closure artifact, no acceptance decision, no Phase 9 authorization

## 1. Purpose

A real Phase 8B campaign is expected to accumulate multiple bounded DEC-052
segments over weeks. DEC-053 permits immutable closure snapshots, but creating a
closure solely to answer "how much evidence do we have?" is unnecessary.

DEC-071 adds a non-mutating progress preview over the exact DEC-053 aggregation
kernel.

## 2. Exact aggregation reuse

The progress preview must reuse the same campaign-close code paths for:

- loading/validating closed DEC-052 segment bundles;
- duplicate/overlap checks;
- continuous aggregate simulation;
- deterministic aggregate replay;
- first/last accepted observation bounds;
- London denominator/complete-date calculations;
- completed 0.2-pip trades;
- represented strategy families and pairs.

It must not implement a second accounting model.

## 3. Minimum evidence parity

Progress fields use the exact DEC-051 acceptance definitions:

- elapsed weeks = (last observation - first observation) / 7 days;
- minimum elapsed weeks = 8;
- minimum complete London dates = 30;
- minimum completed 0.2-pip trades = 40;
- minimum represented strategy families = 2;
- minimum represented pairs = 2.

For each minimum the report includes current value, required value, pass flag,
and remaining amount.

## 4. Closeability diagnostic

The preview reports whether every 0.2/0.5/1.0-pip scenario currently has zero
open and zero pending decisions.

This is diagnostic only. A non-closeable current tail does not invalidate prior
prospective evidence; it means the operator should collect more evidence before
attempting a formal DEC-053 closure.

## 5. Output and persistence

Protocol:

`fmp-phase8b-campaign-progress-v1`.

CLI:

`progress --campaign-dir <path>`.

The command prints JSON to stdout only.

It writes no:

- closure directory;
- campaign-evidence artifact;
- acceptance artifact;
- review;
- lifecycle transition;
- terminal marker.

## 6. Safety and authorization

The report must keep all of these false:

- `acceptance_authorized`;
- `promotion_authorized`;
- `shadow_validation_authorized`;
- `demo_order_authorized`;
- `live_order_authorized`;
- `broker_mutation_authorized`;
- `real_money_authorized`;
- `phase9_authorized`.

Meeting all minimums in the progress report is not Phase 8B PASS. Formal
`close-campaign` and `review-campaign` remain mandatory.

## 7. Empty campaign

A campaign with no clean closed prospective segment returns:

`PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS`.

It is not a protocol failure and authorizes nothing.

## 8. Next boundary

After DEC-071 the repository has read-only operator tooling for both
pre-capture readiness and in-campaign evidence progress.

The remaining meaningful milestone is still real prospective MT5 DEMO evidence.
