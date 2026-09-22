# Phase 8B — Multi-Strategy Runtime and Deterministic Replay Kernel

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
**Decision:** DEC-050
**Experiment:** EXP-20260922-021
**Scope:** source-free runtime/replay implementation; no live capture command and no acceptance decision

## 1. Purpose

DEC-049 froze the exact capture-preflight boundary and deterministic raw-record
envelope. DEC-050 freezes the deterministic market-processing, strategy-routing,
shared-risk simulation, segment-evidence, and offline-replay semantics that any
future Phase 8B live capture process must use.

DEC-050 is implementation-only. It does not read MT5 files continuously, start a
prospective segment, review a campaign, promote a strategy, or authorize any
order path.

## 2. Exact input boundary

The kernel consumes:

- one valid `fmp-phase8b-capture-preflight-v1` artifact; and
- an ordered finite sequence of valid `fmp-phase8b-capture-record-v1`
  envelopes bound to that exact preflight fingerprint.

Every record is revalidated. Required-symbol/session/account/server/protocol
identity remains immutable. `BRIDGE_START` is forbidden inside capture-record
envelopes.

Receive monotonic values must be non-decreasing in segment order. Per-symbol
bridge/source-time continuity remains governed by DEC-047/049 validation.

## 3. Deterministic quote and liveness processing

TICK records reconstruct exact normalized `Phase8BQuote` objects from their
captured bridge fields and receive metadata. HEARTBEAT records are retained as
operational evidence but do not create market prices.

Liveness is independent per required symbol:

- bridge receive gap threshold: 15 seconds;
- market/tick receive gap threshold: 15 seconds;
- bridge gap is an operational failure;
- market gap marks the affected market path stale/incomplete but is not itself a
  bridge-transport failure.

A stale market interval may never be backfilled or interpolated.

## 4. Deterministic bars

The kernel derives bid/ask OHLC bars only from captured tradeable ticks.

Canonical live-shadow timeframes are:

- 1m execution bars;
- 5m, 15m, and 1h signal bars when required by the frozen champion set.

Bars are left-labelled UTC. A one-minute bar is eligible only when:

- its whole minute lies after the capture-preflight boundary;
- it contains at least one captured TICK;
- no detected stale-market interval intersects it.

Higher-timeframe bars require every exact constituent one-minute bar. Missing or
stale constituent minutes make the larger bar absent; no forward fill is
allowed.

The final partially observed minute/window of a finite segment is not emitted.

## 5. Champion reconstruction and candidate generation

The kernel reconstructs every immutable `StrategyVersion` from the exact
`identity_json` embedded in DEC-046 through DEC-049 evidence and verifies the
recomputed strategy fingerprint.

For each champion strategy, the existing Phase 8A
`generate_strategy_candidates` implementation is reused unchanged on that
strategy's exact live-shadow timeframe bars.

Generated candidates are rebound to the immutable strategy fingerprint. Only
directional candidates enter portfolio routing. Exact candidate identities are
deduplicated and deterministically ordered.

## 6. Portfolio routing

The existing Phase 8A `route_shadow_candidates` contract is reused.

It must:

- reject non-champion candidates;
- reject strategy/symbol mismatch;
- reject failed applicability gates;
- reject same-symbol opposite-direction candidates with the same exact
  signal-known timestamp;
- calculate requested and USD-direction exposure before risk approval.

The frozen champion set may not change within the segment.

## 7. Shared-account shadow simulation

Each 0.2 / 0.5 / 1.0-pip scenario uses one shared $100,000 virtual account
across every champion strategy and required symbol.

The unchanged Phase 3 risk configuration remains authoritative.

Accepted routed decisions are registered before same-timestamp quotes.
Deterministic event order is:

1. signal-known timestamp;
2. decision registration ordered by candidate ID;
3. quote processing ordered by symbol then captured record fingerprint.

Entries require the first captured quote for that symbol at or after the exact
signal-known timestamp and no later than five seconds after it.

Scheduled exits require the first captured quote at or after the frozen exit
time and no later than five seconds after it.

Stop/target evaluation uses observed executable quote sides and existing Phase 3
cost/PnL primitives. A detected stale market interval invalidates an affected
open hypothetical position as `OUTCOME_UNKNOWN_AFTER_GAP`.

No broker object or broker execution adapter exists in this kernel.

## 8. Segment evidence

A compiled segment uses protocol:

`fmp-phase8b-segment-v1`

and experiment:

`EXP-20260922-021`.

It binds at minimum:

- exact capture-preflight fingerprint;
- segment code commit;
- exact ordered capture-record fingerprints and aggregate SHA-256;
- required symbols/timeframes and champion set;
- deterministic 1m/5m/15m/1h bars;
- generated candidates and route decisions;
- portfolio exposure snapshots;
- per-slippage completed trades, risk rejections, invalid outcomes, and metrics;
- operational bridge/market gap evidence;
- no-backfill semantics;
- all demo/live/broker/real-money/Phase-9 authorizations false.

No compiled segment alone authorizes Phase 8B acceptance.

## 9. Replay

Offline replay consumes only the exact capture preflight and exact ordered
capture-record envelopes.

Replay runs the same compiler and must reproduce the canonical segment payload
byte-for-byte. Replay evidence stores the expected and replay segment
fingerprints plus `match=true|false`.

A mismatch is retained as evidence and can never be treated as accepted
campaign evidence.

## 10. CLI boundary

DEC-050 adds no long-running live command.

The existing Phase 8B CLI remains limited to design/qualification/registration
and start authorization. There is still no `capture`, `run`, `start`, or
`review` command.

Tests and future tooling may call the finite-sequence compiler and replay APIs
directly.

## 11. Acceptance remains separate

DEC-050 does not decide the 8-week / 30-date / 40-trade gate, coverage, timing,
spread parity, profitability, drawdown, replay, or Phase 9 eligibility.

A separately frozen acceptance decision must consume only replay-verified
DEC-050 segment evidence plus the required historical spread-reference
identities.

## 12. Safety

Throughout DEC-050:

- MT5 AutoTrading remains OFF;
- no demo order placement;
- no live order placement;
- no broker mutation;
- no real-money trading;
- no Phase 9;
- no champion-set mutation;
- no live capture starts.

Possible EXP-021 implementation outcomes are:

- `PHASE8B_RUNTIME_REPLAY_KERNEL_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome starts a prospective segment.
