# Phase 8B — Campaign Start Authorization

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
**Decision:** DEC-048
**Experiment:** EXP-20260922-019
**Scope:** start-boundary authorization only; no live-shadow capture command

## 1. Purpose

DEC-047 permits an immutable Phase 8B campaign registration after all required
multi-symbol demo feeds qualify, but deliberately keeps
`campaign_start_authorized = false`.

DEC-048 freezes the final boundary immediately before prospective capture. It
proves that the currently visible bridge sessions are still exactly the
registered sessions, freezes the campaign start timestamp and first London
date, and establishes a no-backfill reader boundary.

DEC-048 does not implement or execute a live-shadow capture loop. A later
separately frozen decision must implement the capture/runtime/replay/acceptance
surface and may start only from an exact DEC-048 authorization artifact.

## 2. Required registration

Start authorization requires exactly one valid
`fmp-phase8b-campaign-registration-v1` artifact from DEC-047.

The registration must validate deterministically and retain:

- experiment `EXP-20260922-018`;
- exact design and qualification SHA-256 identities;
- exact registration fingerprint;
- exact champion-set ID/fingerprint;
- exact immutable strategy identities/fingerprints;
- exact required symbols/timeframes;
- fixed provider/transport/connector protocol;
- fixed per-symbol FILE_COMMON mapping;
- common DEMO account fingerprint and approved server;
- exact registered bridge-session ID for every required symbol;
- 15-second liveness thresholds;
- 5-second quote deadline;
- 0.2 / 0.5 / 1.0-pip scenarios;
- all order/broker/real-money/Phase-9 authorization flags false.

The SHA-256 of the exact registration bytes is bound into DEC-048 evidence.

## 3. Current bridge-session revalidation

Before authorization, one active `Phase8BBridgeFileTail` is opened for every
required symbol using only the fixed DEC-046 path discovery.

For each required symbol, the current file's first `BRIDGE_START` must match
the registration exactly on:

- symbol;
- connector protocol;
- bridge session ID;
- account fingerprint;
- approved server.

Required-symbol coverage must be exact. Missing, extra, duplicated, mismatched,
truncated, or malformed feeds fail closed.

If any bridge session changed since qualification/registration, DEC-048 refuses
authorization. The operator must requalify and create a new registration rather
than silently rebind a campaign.

## 4. No-backfill reader boundary

`Phase8BBridgeFileTail` initializes its read offset at the current end of each
validated bridge file.

Therefore all bridge records that existed before the DEC-048 reader started are
excluded from future prospective campaign evidence.

The authorization records:

- `reader_start_semantics = "TAIL_AT_EOF_NO_BACKFILL"`;
- exact fixed bridge-file mapping;
- exact registered/current bridge-session IDs;
- exact UTC authorization timestamp.

No MT5 candles, Dukascopy history, reconstructed ticks, interpolation, alternate
provider, or pre-reader file content may be inserted into a later campaign.

## 5. Frozen campaign start boundary

DEC-048 freezes:

- `campaign_start_utc` from an explicit UTC timestamp;
- `first_london_date` derived with `Europe/London`;
- start-authorization code commit;
- registration SHA-256/fingerprint;
- champion-set fingerprint;
- immutable strategy fingerprints;
- required symbol/timeframe sets;
- common demo account/server;
- per-symbol bridge-session IDs;
- liveness/quote/cost contract.

The start boundary cannot be moved after observing subsequent market results.

A later capture runtime must treat restart/disconnect/session replacement after
this boundary as explicit prospective continuity evidence, never hidden
continuation.

## 6. Start authorization outcome

A valid artifact uses protocol:

`fmp-phase8b-campaign-start-v1`

and experiment:

`EXP-20260922-019`

Only a fully valid artifact sets:

- `campaign_start_authorized = true`;
- `prospective_capture_authorized = true`.

It still keeps all of these false:

- `promotion_authorized`;
- `demo_order_authorized`;
- `live_order_authorized`;
- `broker_mutation_authorized`;
- `real_money_authorized`;
- `phase9_authorized`.

The artifact receives a deterministic
`start_authorization_fingerprint` over the canonical immutable payload.

## 7. Exactly-once write

Within one campaign directory, the DEC-048 start artifact is written exactly
once:

- `start-authorization.json`;
- `start-authorization-manifest.json`.

An existing start artifact is never overwritten. A changed identity requires a
different campaign directory/registration.

## 8. CLI boundary

DEC-048 extends `scripts/phase8b_shadow.py` only with:

- `authorize-start`.

It deliberately does not expose:

- `run`;
- `start`;
- `capture`;
- `review`;
- order/demo/live execution commands.

The command reads the exact existing campaign registration, discovers only the
fixed required-symbol bridge files, opens tails at EOF, verifies their
`BRIDGE_START` identities, freezes the current UTC start boundary, and writes
the authorization exactly once.

## 9. Future capture requirement

A future Phase 8B capture implementation must independently revalidate:

- registration;
- DEC-048 authorization;
- authorization SHA-256/fingerprint;
- current bridge sessions against the frozen identities;
- structural no-order boundary.

It must inherit DEC-038 liveness separation and the established prospective
minimum/acceptance gates. DEC-048 itself does not claim that those gates are
satisfied.

## 10. Safety boundary

Throughout DEC-048:

- MT5 AutoTrading remains OFF;
- bridge remains quote-only;
- no demo order placement;
- no live order placement;
- no broker mutation;
- no real-money trading;
- no Phase 9;
- no legacy EXP-011 runtime/evidence mutation.

Possible EXP-019 outcomes are:

- `PHASE8B_CAMPAIGN_START_AUTHORIZED`;
- `PROTOCOL_FAILURE`.

No live-shadow segment is started by DEC-048 itself.
