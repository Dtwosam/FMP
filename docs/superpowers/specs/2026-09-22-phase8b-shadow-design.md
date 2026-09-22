# Phase 8B — Multi-Strategy Read-Only Shadow Design Contract

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B CAMPAIGN
**Decision:** DEC-046
**Experiment:** EXP-20260922-017
**Scope:** design/registration boundary only; no campaign launch

## 1. Purpose

Phase 8B may begin only after DEC-045 produces an exact `PHASE8A_SHADOW_CANDIDATE_ACCEPTED` artifact.

DEC-046 freezes how that accepted portfolio is converted into a read-only live-shadow design without modifying the legacy USDJPY-only Phase 8 evidence path. The old EXP-011 bridge/runtime remains preserved unchanged for historical evidence and diagnostics.

DEC-046 does not authorize a campaign launch, demo order, live order, broker mutation, real-money trading, or Phase 9.

## 2. Candidate input

The design compiler accepts exactly one DEC-045 acceptance artifact.

It must verify:

- protocol `fmp-phase8a-acceptance-v1`;
- experiment `EXP-20260922-016`;
- outcome `PHASE8A_SHADOW_CANDIDATE_ACCEPTED`;
- `shadow_candidate_authorized = true`;
- `phase8b_design_authorized = true`;
- all broker/demo/live/real-money/Phase-9 authorization flags remain false;
- acceptance artifact SHA-256;
- exact DEC-045 compiler commit;
- exact champion-set ID and champion-set fingerprint;
- at least two selected strategy versions;
- every selected record has lifecycle `SHADOW_CANDIDATE`;
- strategy identities/fingerprints replay exactly.

A rejection artifact cannot produce a Phase 8B design.

## 3. Supported live-observation universe

Phase 8B supports only the existing V1 instruments:

- EURUSD
- GBPUSD
- USDJPY

The required live symbols are exactly the sorted union of symbols referenced by the accepted champion set. No extra symbol may be observed/scored as part of the campaign design.

Supported signal timeframes remain:

- 5m
- 15m
- 1h

The design records the exact required timeframe set from the accepted strategies.

## 4. Connector topology

The Phase 8B connector is separate from the legacy USDJPY EXP-011 bridge.

Frozen intended topology:

- provider: `FP_MARKETS_MT5_DEMO`;
- transport: `MT5_FILE_COMMON_JSONL`;
- protocol: `fmp-mt5-demo-multisymbol-file-bridge-v1`;
- allowed servers:
  - `FPMarketsSC-Demo`
  - `FPMarketsSC-Demo2`;
- demo account only;
- one read-only EA instance per required symbol chart;
- every EA instance must use the same demo account fingerprint and approved server;
- AutoTrading remains OFF;
- no order/trade API surface is permitted.

Fixed per-symbol FILE_COMMON paths:

- EURUSD -> `FMP/phase8b-eurusd-feed.jsonl`
- GBPUSD -> `FMP/phase8b-gbpusd-feed.jsonl`
- USDJPY -> `FMP/phase8b-usdjpy-feed.jsonl`

No arbitrary file-path or arbitrary-symbol override is permitted.

## 5. Liveness and missing-path semantics

DEC-038 bridge/market liveness separation is retained independently for every required symbol.

For each required symbol:

- 15 seconds without a valid bridge start/tick/heartbeat is a bridge continuity failure;
- bridge continuity failure marks the affected portfolio observation path incomplete and prevents the affected London date from being financially scored as a complete portfolio date;
- 15 seconds without a market tick while valid bridge heartbeats continue is `market_quiet`, not automatically a bridge failure;
- market quiet does not synthesize ticks, candles, or prices;
- an open simulated position on the affected symbol becomes outcome-unknown after the frozen gap rule;
- missing required bar context prevents the relevant strategy decision from being scored;
- no MT5 candle backfill, interpolation, reconstructed ticks, or alternate-provider repair is allowed.

Any required-symbol bridge restart or disconnect is an explicit continuity boundary.

## 6. Qualification boundary

Before campaign registration, every required symbol feed must independently pass the future Phase 8B connector qualification.

Qualification must additionally prove:

- all required feeds bind to the same account fingerprint;
- all required feeds bind to the same approved demo server;
- each bridge session identity is distinct and valid;
- source times are UTC-aligned within the frozen quote deadline;
- no unexpected symbol feed is accepted.

DEC-046 design compilation does not itself satisfy connector qualification.

## 7. Immutable design manifest

The Phase 8B design artifact must contain:

- exact DEC-045 acceptance SHA-256;
- DEC-045 acceptance compiler commit;
- Phase 8B design compiler commit;
- champion-set ID and fingerprint;
- exact selected strategy fingerprints and identity JSON;
- exact required symbols;
- exact required timeframes;
- exact per-symbol bridge file mapping;
- provider / transport / bridge protocol;
- allowed demo servers;
- liveness timeout: 15 seconds;
- quote deadline: 5 seconds;
- adverse-slippage scenarios: 0.2 / 0.5 / 1.0 pips;
- `campaign_registration_authorized = false`;
- `campaign_start_authorized = false`;
- all broker/demo/live/real-money/Phase-9 authorization flags false.

The design fingerprint is SHA-256 over the canonical immutable design payload.

## 8. Champion immutability

The accepted champion set is immutable for any future registered Phase 8B campaign.

Research may continue separately, but no observation, new challenger, parameter change, or research result may mutate the active design/campaign. A different champion set requires a new accepted DEC-045 artifact and a new Phase 8B design identity.

## 9. Outcome

Possible EXP-017 design outcomes:

- `PHASE8B_DESIGN_FROZEN` — an exact accepted DEC-045 candidate was converted into an immutable multi-symbol shadow design;
- `PROTOCOL_FAILURE` — input identity, lifecycle, champion-set, or deterministic replay failed.

A frozen design authorizes only subsequent source-free connector/qualification/registration implementation. It does not authorize campaign registration or live shadow capture by itself.

## 10. Safety boundary

Throughout DEC-046 / EXP-017:

- MT5 AutoTrading remains OFF;
- no demo order placement;
- no live order placement;
- no broker mutation;
- no real-money trading;
- no Phase 9;
- legacy EXP-011 evidence remains unchanged.
