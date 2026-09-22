# Phase 8B — Runtime State-Continuity Amendment

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
**Decision:** DEC-053
**Experiment:** EXP-20260922-024
**Amends:** DEC-050 runtime/replay kernel before DEC-052 campaign-close implementation
**Scope:** source-free deterministic cross-segment simulator checkpoint continuity

## 1. Reason for amendment

DEC-050 correctly freezes one shared Phase 3 virtual account per slippage
scenario inside a finite segment, but its initial implementation creates a new
$100,000 simulator whenever `compile_phase8b_segment` is called.

That behavior is valid for isolated deterministic tests but is not sufficient
for an 8-week prospective campaign that must be stored as multiple finite
segments. Resetting virtual equity, daily-halt state, pending decisions, or open
positions at a segment boundary would violate the shared-account campaign
semantics.

This defect was identified before any Phase 8B live-shadow segment or DEC-052
campaign evidence exists.

## 2. Deterministic checkpoint protocol

DEC-053 adds:

`fmp-phase8b-runtime-checkpoint-v1`

A checkpoint binds:

- exact capture-preflight fingerprint;
- exact champion-set fingerprint;
- exact slippage scenarios and Phase 3 risk config;
- one state object per slippage scenario;
- deterministic checkpoint fingerprint.

Each scenario state contains enough exact information to resume without
inference:

- risk equity;
- current UTC risk date;
- day-start equity;
- realized day PnL;
- daily-halt state and halt timestamp;
- risk reservations;
- pending directional decisions plus scheduled exits;
- open shadow positions plus scheduled exits;
- completed/terminal decision IDs needed to prevent reopening.

No broker state is queried or represented.

## 3. Segment compiler changes

`compile_phase8b_segment` gains an optional exact prior runtime checkpoint.

Without a prior checkpoint it starts at the frozen $100,000 campaign baseline.

With a prior checkpoint it:

- validates exact preflight/champion/risk identity;
- restores all three scenario states;
- refuses duplicate/reopened terminal decisions;
- processes only the new ordered capture-record sequence;
- emits only trades/outcomes/rejections produced during the new segment;
- emits one exact terminal runtime checkpoint for the next segment.

The segment evidence binds both:

- initial runtime-checkpoint fingerprint (or the literal baseline marker);
- terminal runtime-checkpoint fingerprint.

## 4. Replay

Replay receives the same prior checkpoint and must reproduce both the canonical
segment payload and terminal checkpoint byte-for-byte.

A different prior checkpoint is a different replay input and must fail identity
validation rather than silently rebase equity.

## 5. Segment boundaries and restarts

A normal evidence-file boundary is not itself a market gap and must preserve
open/pending state exactly.

A future live-tail restart/disconnect protocol must separately insert explicit
gap evidence when market path was unobserved. DEC-053 does not hide or infer a
restart gap.

## 6. DEC-052 dependency

DEC-052 campaign close may combine multiple segments only when each later
segment's initial checkpoint fingerprint equals the immediately preceding
segment's terminal checkpoint fingerprint.

Campaign close must reject any reset to the baseline after the first segment.

## 7. Safety

DEC-053 remains source-free:

- no MT5 tailing;
- no live capture command;
- no order surface;
- no demo/live orders;
- no broker mutation;
- no real-money trading;
- no Phase 9 execution.

Possible EXP-024 implementation outcomes:

- `PHASE8B_RUNTIME_CONTINUITY_READY`;
- `PROTOCOL_FAILURE`.

No live campaign is started by this amendment.
