# Phase 8B — Prospective Campaign Readiness Audit

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B PROSPECTIVE CAPTURE
**Decision:** DEC-070
**Experiment:** EXP-20260922-041
**Depends on:** DEC-046 through DEC-054 and DEC-069
**Scope:** read-only readiness inspection and current operator handoff; no live-shadow capture, no acceptance review, no Phase 9 execution

## 1. Purpose

The Phase 8B source already implements:

- immutable design and multi-symbol connector qualification;
- campaign registration;
- campaign-start authorization and capture preflight;
- retrospective spread-reference freeze;
- bounded prospective capture segments;
- multi-segment campaign close;
- acceptance review and SHADOW_VALIDATED transition.

What is missing is a current operator-facing readiness surface that verifies the
exact campaign directory and current bridge identities before the operator
chooses to invoke the first or next prospective capture segment.

DEC-070 fills that gap without creating any durable permission artifact.

## 2. Non-authoritative inspection

The readiness protocol is:

`fmp-phase8b-campaign-readiness-v1`.

The CLI command is:

`readiness --campaign-dir <path>`.

The command prints one JSON report to stdout only. It does not write into the
campaign directory.

The report is point-in-time diagnostic evidence and is never consumed by
`capture-segment` as authorization. The capture command continues to
independently revalidate the frozen artifacts and bridge identities.

## 3. Frozen artifact checks

The audit requires a valid DEC-047 registration.

It then examines the campaign directory in order:

1. registration;
2. DEC-048 start authorization;
3. DEC-049 capture preflight;
4. DEC-054 campaign-bound spread reference;
5. campaign terminal marker.

When an optional next-step artifact is absent, the report returns the exact next
operator action rather than manufacturing or repairing that artifact.

If start authorization exists without the capture preflight that
`authorize-start` must create in the same operation, the directory is an
integrity failure.

Any malformed or cross-boundary identity mismatch fails closed.

## 4. Current bridge identity audit

For every exact `required_symbols` entry in the registration, the audit:

- uses only fixed DEC-046 FILE_COMMON discovery;
- opens one `Phase8BBridgeFileTail` at current EOF;
- reads only its already-existing `BRIDGE_START` identity;
- does not consume or persist post-EOF ticks/heartbeats;
- requires exact symbol, protocol, DEMO mode, account fingerprint, server, and
  registered/current bridge-session identity.

If start/preflight artifacts exist, the current bridge sessions must match those
frozen session identities exactly.

Missing, duplicate, malformed, live-account, wrong-server, wrong-symbol, or
session-replaced bridges fail closed.

The readiness audit does not claim 15-second bridge liveness or 5-second quote
freshness from the start record alone. Those remain runtime checks.

## 5. Outcomes

Possible source outcomes are:

- `PHASE8B_READY_FOR_PROSPECTIVE_CAPTURE`
- `PHASE8B_NEEDS_START_AUTHORIZATION`
- `PHASE8B_NEEDS_SPREAD_REFERENCE`
- `PHASE8B_CAMPAIGN_TERMINAL`
- `CONNECTOR_UNAVAILABLE`
- `CONNECTOR_REJECTED`
- `PROTOCOL_FAILURE`

Only `PHASE8B_READY_FOR_PROSPECTIVE_CAPTURE` sets
`capture_prerequisites_satisfied=true`.

Even that outcome keeps:

- `live_shadow_segment_started=false`;
- `acceptance_authorized=false`;
- `promotion_authorized=false`;
- `demo_order_authorized=false`;
- `live_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `real_money_authorized=false`;
- `phase9_authorized=false`.

## 6. Next-action semantics

The report exposes one deterministic next-action string:

- `authorize-start` when registration and bridges are valid but start
  authorization does not yet exist;
- `freeze-spread-reference` when start/preflight are valid but no spread
  reference exists;
- `capture-segment` when all capture prerequisites currently align;
- `none-terminal` when a terminal campaign marker exists.

Connector/protocol failures expose no executable next action.

## 7. Multi-pair operator handoff

DEC-070 replaces the stale USDJPY-only operator handoff with the current Phase
8B portfolio workflow.

The handoff must state:

- final required symbols come from the frozen Phase 8B design and may include
  EURUSD, GBPUSD, and USDJPY;
- one read-only bridge EA is attached per required symbol;
- all required symbols must use the same accepted FP Markets DEMO account/server;
- AutoTrading remains OFF;
- the sequence is design -> qualify -> register -> authorize-start ->
  freeze-spread-reference -> readiness -> capture-segment -> close-campaign ->
  review-campaign;
- no captured gap is backfilled;
- NEED_MORE_DATA permits additional clean prospective segments;
- Phase 8B PASS permits Phase 9 design only, never an order.

## 8. Safety

DEC-070:

- performs no broker mutation;
- invokes no MT5 trading API;
- starts no prospective segment;
- writes no campaign artifact;
- changes no strategy/risk/acceptance threshold;
- changes no Phase 9 source gate;
- authorizes no demo/live/real-money action.

Repository tests use temporary fixture campaign directories and fake bridge tails
only.

## 9. Next boundary

After DEC-070, the source and operator path are ready for the first real
prospective Phase 8B campaign.

The actual `authorize-start`, spread-reference freeze, readiness audit, and
`capture-segment` commands remain explicit operator actions against the real
local MT5 demo bridge. DEC-070 itself executes none of them.
