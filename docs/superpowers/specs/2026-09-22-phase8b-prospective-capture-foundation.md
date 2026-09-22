# Phase 8B — Prospective Capture Foundation

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
**Decision:** DEC-049
**Experiment:** EXP-20260922-020
**Scope:** source-free capture preflight and deterministic raw-record envelope only; no live capture command

## 1. Purpose

DEC-048 freezes the prospective campaign start boundary and authorizes only a
future capture implementation to proceed from that exact immutable artifact.
DEC-049 defines the source-free foundation that a later runtime/replay decision
must consume before any Phase 8B live-shadow segment can begin.

This decision deliberately does not expose a command that reads post-start
quotes continuously, starts a scored segment, runs strategy logic, reviews
performance, or changes lifecycle state.

## 2. Exact upstream inputs

The capture foundation requires both:

- exactly one valid `fmp-phase8b-campaign-registration-v1` artifact from
  DEC-047; and
- exactly one valid `fmp-phase8b-campaign-start-v1` artifact from DEC-048.

The exact UTF-8 JSON bytes of both artifacts are SHA-256 bound.

The capture preflight must reject any mismatch between registration and start
authorization for:

- registration SHA-256 and registration fingerprint;
- champion-set ID and fingerprint;
- strategy count, ordered strategy fingerprints, and immutable strategy rows;
- required symbols and timeframes;
- provider, transport, and connector protocol;
- fixed FILE_COMMON paths;
- common demo account fingerprint and approved server;
- per-symbol registered bridge-session IDs;
- liveness thresholds;
- slippage scenarios;
- all broker/demo/live/real-money/Phase-9 authorization flags.

## 3. Fresh bridge revalidation

The capture preflight opens a fresh `Phase8BBridgeFileTail` for every required
symbol using only fixed DEC-046 discovery.

Each fresh tail starts at the current EOF and its first `BRIDGE_START` identity
must still exactly match the DEC-047/048 registration on symbol, protocol,
bridge-session ID, account fingerprint, approved server, and DEMO mode.

Missing, extra, duplicate, changed, truncated, or malformed feeds fail closed.

This second revalidation is intentional. A DEC-048 authorization does not permit
a later runtime to silently attach to replacement MT5 bridge sessions.

## 4. No-backfill boundary

Every fresh tail used by the capture foundation preserves:

`TAIL_AT_EOF_NO_BACKFILL`

No record that existed before the fresh reader was created can enter future
prospective evidence. Historical MT5 file content, Dukascopy candles,
interpolation, reconstructed ticks, or any alternate provider remain forbidden.

## 5. Capture-preflight artifact

A valid preflight uses protocol:

`fmp-phase8b-capture-preflight-v1`

and experiment:

`EXP-20260922-020`.

It binds:

- exact registration SHA-256/fingerprint;
- exact DEC-048 authorization SHA-256/fingerprint;
- exact campaign start UTC and first London date;
- exact champion set and strategies;
- required symbols/timeframes;
- common demo account/server;
- registered/current bridge sessions;
- fixed bridge-file mapping;
- liveness and cost contract;
- capture-foundation code commit;
- UTC preflight timestamp;
- reader semantics.

The artifact receives a deterministic `capture_preflight_fingerprint`.

The preflight records `capture_runtime_ready = true`, but also explicitly
records that no live-shadow segment has started and no acceptance or promotion
has occurred.

## 6. Deterministic raw-record envelope

DEC-049 also defines the canonical envelope for a future runtime to persist
after the preflight boundary.

For each accepted post-preflight bridge record, the envelope must contain:

- envelope protocol;
- exact capture-preflight fingerprint;
- symbol;
- receive UTC timestamp;
- segment-local monotonic receive timestamp;
- exact parsed bridge record fields.

A `TICK` may additionally yield the existing normalized `Phase8BQuote`.
A heartbeat yields no market quote. Duplicate ticks may be deduplicated only
under the existing bridge-session validator semantics. Regressing source time,
changed session/account/server identity, malformed records, or unsupported
symbols fail closed.

DEC-049 does not yet persist these envelopes to a live segment. It freezes the
serialization and validation boundary so a later runtime can be tested against
an already approved contract.

## 7. CLI boundary

`scripts/phase8b_shadow.py` remains limited to:

- `design`;
- `qualify`;
- `register`;
- `authorize-start`.

DEC-049 adds no `capture`, `run`, `start`, `replay`, or `review` command.

A later separately approved decision must expose any live capture loop and must
also freeze append-only segment files, deterministic replay, strategy/routing
parity, acceptance aggregation, restart semantics, and campaign-close rules
before the first prospective segment is admitted.

## 8. Safety boundary

Throughout DEC-049:

- MT5 AutoTrading remains OFF;
- quote bridge remains read-only;
- no demo order placement;
- no live order placement;
- no broker mutation;
- no real-money trading;
- no Phase 9;
- no active champion-set mutation;
- no Phase 8B acceptance or promotion.

Possible EXP-020 source-free outcomes are:

- `PHASE8B_CAPTURE_FOUNDATION_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome starts a live-shadow segment.
