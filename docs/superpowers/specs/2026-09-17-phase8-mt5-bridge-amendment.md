# Phase 8 MT5 Demo Quote Bridge Amendment

**Status:** DRAFT FOR WRITTEN REVIEW  
**Date:** 2026-09-17  
**Repository:** `Dtwosam/FMP`  
**Phase:** 8 — Live shadow mode  
**Amends:** `docs/superpowers/specs/2026-09-15-phase8-shadow-design.md` / DEC-036  
**Proposed decision:** DEC-037  
**Proposed experiment:** EXP-20260917-010  
**Branch:** `phase8-mt5-bridge-amendment`

## 1. Purpose

This amendment replaces the unavailable OANDA Practice quote-source path with a read-only MetaTrader 5 demo quote bridge for the same frozen Phase 8 shadow boundary.

The operator cannot open the OANDA account required by DEC-036 because OANDA does not accept new clients from the operator's country of residence. The original design explicitly requires a new approved design amendment rather than an automatic fallback when OANDA Practice is unavailable.

This amendment changes only the live quote-source transport and provider evidence identity. It does not change the promoted strategy, risk semantics, virtual execution semantics, acceptance thresholds, replay requirements, campaign minima, or phase boundary.

Phase 8 remains observational and simulated only. It must remain structurally unable to submit, modify, or cancel broker orders or positions. No practice/demo order placement, production/live order placement, broker mutation, or real-money trading is authorized. Phase 9 remains locked.

## 2. Frozen strategy and acceptance semantics remain unchanged

The only eligible strategy remains:

- strategy ID: `session_breakout`
- symbol: `USDJPY`
- signal timeframe: `15m`
- London-session/DST semantics unchanged
- breakout buffer: `5` pips
- target: `1.5` times the frozen session range
- exact flat time: `16:00 Europe/London`
- ML overlay: none

The existing Phase 8 virtual scenarios remain exactly:

- 0.2 pips adverse per fill
- 0.5 pips adverse per fill
- 1.0 pips adverse per fill
- independent $100,000 virtual starting equity per scenario
- zero commission and zero financing in the frozen simulator

All existing Phase 8 campaign gates remain unchanged, including the minimum 40 completed scorable 0.2-pip trades, 8 elapsed calendar weeks, 30 complete London dates, 90% valid-date coverage, timing thresholds, spread-parity thresholds, 0.2/0.5 financial gates, deterministic replay, and the exact review outcome vocabulary.

## 3. Provider decision

### 3.1 Selected provider path

The amended Phase 8 live quote source is the operator's FP Markets MetaTrader 5 **demo** account, consumed through a purpose-built read-only MQL5 Expert Advisor named:

`FMPPhase8QuoteBridge`

The Expert Advisor is attached only to the `USDJPY` chart in the operator's local MT5 terminal. It reads incoming quote events and appends canonical quote/heartbeat records to a local file. FMP reads that file and does not call the MetaTrader5 Python package.

The bridge is a quote-source adapter, not a broker execution adapter.

### 3.2 Why the file bridge is selected

Three implementation approaches were considered:

1. MQL5 Expert Advisor -> local append-only file -> FMP reader;
2. MQL5 Expert Advisor -> localhost socket -> FMP reader;
3. direct Python `MetaTrader5` package integration.

The file bridge is selected because it minimizes runtime surface and makes the no-order boundary easier to audit. The direct Python package is rejected because the package exposes execution functions such as `order_send()`. The socket bridge is deferred because it adds network lifecycle and transport complexity without a Phase 8 requirement for sub-file-system latency.

### 3.3 No automatic provider fallback

This amendment authorizes only the FP Markets MT5 demo bridge described here. There is no automatic fallback to OANDA production, MT5 live accounts, another broker, another symbol, cTrader, or a generic market-data vendor.

Any later provider change requires a new design amendment and source-of-truth update.

## 4. Structural no-order boundary

### 4.1 MQL5 bridge restrictions

`FMPPhase8QuoteBridge.mq5` must contain no broker mutation capability.

It must not use or reference:

- `OrderSend`
- `OrderSendAsync`
- `MqlTradeRequest`
- `MqlTradeResult`
- `CTrade`
- `PositionOpen`
- `PositionClose`
- `PositionModify`
- order create/modify/cancel helpers
- trade-library imports such as `<Trade/Trade.mqh>`

The bridge performs only account-mode validation, server/symbol validation, tick reads, timer handling, hashing/fingerprinting support if implemented locally, and file writes.

A repository-level structural guard must parse or scan the bridge source and fail if forbidden execution surfaces are introduced.

### 4.2 FMP runtime restrictions

Python runtime code under `src/fmp/shadow` must continue to import no `MetaTrader5` or `mt5` package and expose no public broker mutation method.

The current repository-level structural safety guard remains and is amended to permit the new local-file quote reader while continuing to prohibit broker execution surfaces.

### 4.3 AutoTrading remains off

The operator is instructed to keep the MT5 AutoTrading button disabled. MetaQuotes documents that `OnTick()` events continue to be generated for Expert Advisors even when AutoTrading is disabled; disabling AutoTrading prevents trade requests but does not stop EA event processing.

Official reference:

- `https://www.mql5.com/en/docs/event_handlers/ontick`

AutoTrading-off is an additional operator safety control, not the primary structural guarantee. The bridge source itself must remain incapable of submitting trades.

## 5. Account, server, and symbol binding

The bridge must fail closed during initialization unless all of the following are true:

- `AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_DEMO`;
- chart symbol is exactly `USDJPY`;
- the account server is in a compile-time allowlist of approved FP Markets demo server names;
- Bid and Ask for the symbol are finite and positive before a quote record is accepted.

The server allowlist is frozen in source, not caller-supplied input. The implementation may include the exact demo server observed by the operator plus any second FP Markets demo server explicitly documented and reviewed before merge. Live server names are forbidden.

The plain account login must never be written into Phase 8 evidence. A one-way SHA-256 account fingerprint may be used for run binding.

## 6. Bridge output protocol

### 6.1 Transport

The bridge writes to an MT5 sandbox file using `FILE_COMMON` so the operator can locate the output consistently across the Wine-backed macOS terminal.

Official references:

- `https://www.mql5.com/en/docs/files/fileopen`
- `https://www.mql5.com/en/docs/files/fileflush`

The selected file name is fixed in source:

`FMP/phase8-usdjpy-feed.jsonl`

No arbitrary output path is accepted from the operator or CLI.

### 6.2 Record types

The bridge emits exactly two record types:

- `TICK`
- `BRIDGE_HEARTBEAT`

No order, trade, position, balance, margin, transaction, or account-history records are emitted.

### 6.3 Tick record

Each `TICK` record contains only:

- protocol version
- record type `TICK`
- fixed symbol `USDJPY`
- source tick time in milliseconds from `MqlTick.time_msc`
- Bid
- Ask
- MQL5 tick flags
- demo-server identifier
- one-way account fingerprint

`MqlTick` is the authoritative source for Bid, Ask, tick time, and flags.

Official reference:

- `https://www.mql5.com/en/docs/constants/structures/mqltick`

The bridge does not emit Last price, volume, leverage, account equity, account balance, or personally identifying account fields because Phase 8 does not need them.

### 6.4 Bridge heartbeat

The bridge emits one `BRIDGE_HEARTBEAT` approximately every five seconds from an EA timer.

The heartbeat proves only that the local MT5/EA/file bridge is alive. It must never be represented as an FP Markets broker heartbeat or market-data heartbeat.

The heartbeat contains:

- protocol version
- record type `BRIDGE_HEARTBEAT`
- fixed symbol `USDJPY`
- current terminal/server time value used by the bridge
- demo-server identifier
- one-way account fingerprint

The existing 15-second Phase 8 liveness timeout remains unchanged.

## 7. Append and durability semantics

The bridge opens the fixed output file for write/read sharing and appends records rather than truncating prior evidence during an active bridge session.

Each accepted record is newline terminated and canonical enough for strict parsing. The bridge calls `FileFlush()` after each emitted record during qualification and Phase 8 capture so FMP can observe durable records promptly. The expected throughput for one USDJPY stream is low enough that this durability-first choice is acceptable for Phase 8.

FMP treats a partial final line as incomplete and waits for completion; it must not silently accept malformed JSON or a malformed record.

Bridge session start/restart is explicit evidence. FMP never reconstructs ticks missed while MT5, the EA, the Mac, or FMP was stopped.

## 8. Timestamp semantics

Provider market ordering uses the MT5 tick timestamp from `MqlTick.time_msc` for `TICK` records.

FMP records its own local UTC receive timestamp and segment-local monotonic receive timestamp when it observes each complete bridge record. These remain the timing inputs for processing-latency and stale detection evidence.

The adapter converts the millisecond epoch into an aware UTC datetime before constructing the existing `NormalizedQuote` contract.

Tick source-time regression fails closed for the current segment. Exact duplicate ticks may be deduplicated only when source time, symbol, Bid, Ask, and flags are identical. A conflicting duplicate at the same source time is an integrity failure.

`BRIDGE_HEARTBEAT` records participate in liveness only and never create price observations, bars, entries, exits, or strategy signals.

## 9. Normalization boundary

The MT5-specific parser converts bridge records into the existing provider-neutral runtime events:

- valid `TICK` -> `NormalizedQuote`
- valid `BRIDGE_HEARTBEAT` -> `HeartbeatEvent`

For a valid `TICK`:

- symbol must be exactly `USDJPY`;
- Bid and Ask must be finite and positive;
- Bid must be <= Ask;
- account fingerprint and server identity must match the segment binding;
- source timestamp must parse as UTC;
- `tradeable` is set true only for ticks admitted by the demo/server/symbol bridge boundary.

After normalization, the existing live-bar builder, frozen strategy adapter, shadow simulator, evidence writer, replay pipeline, and financial review logic are reused.

No strategy code is reimplemented for MT5.

## 10. Qualification protocol

Qualification remains an explicit operator action before any live-shadow campaign begins.

It runs for at most ten minutes and may stop early only after all of the following are observed:

- at least 100 valid `TICK` records;
- at least 6 valid `BRIDGE_HEARTBEAT` records.

Qualification PASS additionally requires:

- bridge protocol/version match;
- demo account mode proven in bridge startup metadata;
- approved FP Markets demo server identity;
- only `USDJPY` tick records;
- finite positive Bid and Ask on every accepted tick;
- Bid <= Ask;
- source timestamps do not regress;
- no bridge/file liveness gap greater than 15 seconds while qualification is active;
- no malformed or unknown record silently accepted;
- structural safety tests prove the EA and Python runtime contain no broker mutation surfaces.

Low market activity that prevents the sample minimum without an integrity failure returns `INCONCLUSIVE`.

Missing file, inactive EA, wrong account type, wrong server, wrong symbol, or inaccessible bridge returns `CONNECTOR_UNAVAILABLE` unless evidence identifies an implementation defect.

Malformed/conflicting records, source-time regression, forbidden identity mismatch, or safety violation returns `CONNECTOR_REJECTED`.

Qualification invokes no strategy logic.

## 11. Evidence protocol amendment

The existing evidence protocol hard-codes the OANDA Practice connector identity. The amended implementation therefore bumps the evidence protocol version rather than reusing OANDA-specific fields with new meanings.

Proposed values:

- evidence protocol: `fmp-phase8-shadow-evidence-v2`
- connector protocol: `fmp-mt5-demo-file-bridge-v1`
- provider: `FP_MARKETS_MT5_DEMO`
- provider instrument: `USDJPY`
- transport: `MT5_FILE_COMMON_JSONL`
- bridge file: `FMP/phase8-usdjpy-feed.jsonl`

OANDA-specific manifest fields such as HTTP method, host, path template, snapshot, and home-conversion flags are removed from new v2 segments.

New connector-bound manifest fields include:

- connector protocol
- provider
- provider instrument
- transport identity
- bridge file identity
- approved demo server identity
- account fingerprint SHA-256
- bridge source SHA-256 or repository commit binding

All existing strategy, upstream Phase 7 identity, slippage scenario, risk policy, file hashes, replay digest, run start/end, and code-commit bindings remain.

The review compiler accepts only the registered evidence protocol/connector identity for the campaign; OANDA v1 and MT5 v2 segments must not be mixed inside one registered campaign.

## 12. Campaign identity and source-of-truth transition

The OANDA connector attempt under `EXP-20260915-009` did not reach a successful connector qualification and produced no scored live-shadow campaign evidence.

The source-of-truth amendment will record the OANDA path as stopped because the required account is unavailable to the operator's jurisdiction. It is not a market, strategy, financial, or safety rejection.

A new experiment identity is proposed:

`EXP-20260917-010 — Phase 8 MT5 demo live-shadow evaluation`

Proposed decision:

`DEC-037 — Replace unavailable OANDA Practice connector with read-only FP Markets MT5 demo quote bridge`

The new campaign must be registered from scratch under the amended connector identity before the first scored observation. No prior OANDA qualification or campaign evidence may be reclassified as MT5 evidence.

Phase 8 remains ACTIVE. Phase 9 remains locked.

## 13. Operator workflow on macOS

After source-free implementation verification passes, the operator workflow is:

1. keep the FP Markets MT5 demo account logged in;
2. confirm `USDJPY` is visible and receiving changing quotes;
3. keep MT5 AutoTrading disabled;
4. install/compile `FMPPhase8QuoteBridge.mq5` in MetaEditor;
5. attach the EA to the `USDJPY` chart only;
6. verify the EA reports demo/server/symbol checks as PASS;
7. locate the fixed `FILE_COMMON` bridge file;
8. run the bounded FMP qualification command with the explicit bridge-file reader;
9. inspect qualification evidence;
10. only after PASS, build/freeze the historical spread reference and register the new campaign;
11. start each shadow segment explicitly;
12. replay each finalized segment offline.

No daemon, launch agent, cron job, auto-start service, or CI job starts MT5 or the live campaign.

## 14. Testing requirements

Implementation must use TDD and include at least:

### 14.1 MQL5 structural safety tests

Repository tests inspect the `.mq5` source and reject forbidden trading identifiers/imports.

Tests also require explicit checks for:

- demo account mode;
- exact USDJPY symbol;
- approved FP Markets demo server allowlist;
- fixed output file identity;
- fixed protocol version.

### 14.2 Python bridge parser tests

Cover:

- valid tick parsing;
- valid heartbeat parsing;
- malformed/unknown record rejection;
- wrong symbol rejection;
- wrong server rejection;
- account fingerprint mismatch rejection;
- crossed/non-finite/non-positive price rejection;
- source-time regression;
- exact duplicate handling;
- conflicting duplicate rejection;
- partial-line handling;
- no silent malformed acceptance.

### 14.3 Qualification tests

Cover PASS, INCONCLUSIVE, CONNECTOR_UNAVAILABLE, and CONNECTOR_REJECTED with injected clocks and temporary bridge files.

### 14.4 Runner and replay parity tests

Prove that MT5 bridge input reaches the same existing normalization -> bars -> strategy -> simulator pipeline and that deterministic replay reproduces derived evidence from captured bridge records.

### 14.5 Evidence/campaign tests

Prove v2 manifest identity, no OANDA-specific connector fields in v2 segments, no mixed connector protocols in one campaign, secret/account redaction, and unchanged acceptance thresholds.

### 14.6 Full regression

Before merge:

- all Phase 8 tests PASS;
- full Python test suite PASS;
- workflow YAML validation PASS;
- Python compile PASS;
- Phase 3 deterministic acceptance remains PASS;
- no Phase 1 acquisition path runs;
- no live MT5 qualification is run in CI.

## 15. Failure handling

The bridge and FMP fail closed.

Examples:

- EA detached or terminal closes -> liveness timeout, current date becomes ineligible, open shadow outcomes become unknown after gap;
- bridge file cannot be read -> connector unavailable/rejection evidence, no strategy continuation;
- wrong/demo-to-live account change -> EA stops writing valid ticks and qualification/runtime rejects the segment;
- wrong server or symbol -> bridge initialization failure;
- malformed record -> durable rejection and segment failure;
- source-time regression/conflicting duplicate -> integrity failure;
- restart -> no reconstruction/backfill; current London date is handled under existing restart rules.

No historical MT5 candles, broker order history, positions, account state, or reconstructed tick path may be used to repair a live gap.

## 16. Security and privacy

No broker password is required by FMP.

The EA runs inside the already authenticated local MT5 terminal. The bridge file contains no password, no token, no account name, and no plain account login.

Durable FMP evidence stores only the approved provider/server identity and a one-way account fingerprint for run binding.

The user must never paste broker passwords or secrets into repository files, GitHub, CI variables, or chat for this workflow.

## 17. Non-goals

This amendment does not authorize or implement:

- demo order placement;
- live order placement;
- real-money trading;
- MT5 Python execution integration;
- generic broker adapters;
- multi-symbol support;
- alternate strategies/timeframes;
- automatic provider fallback;
- historical MT5 backfill;
- broker position reconciliation;
- autonomous background campaign start;
- Phase 9 demo execution.

## 18. Acceptance of this amendment

This design becomes active only after:

1. this written spec is reviewed and explicitly approved;
2. source-of-truth decision/experiment/project-state records are updated on the feature branch;
3. the implementation plan derived from this spec is reviewed;
4. implementation and source-free verification pass and merge to `main`.

Only then may the operator perform the amended live connector qualification.

A successful qualification permits Phase 8 reference generation and campaign registration only. It does not constitute Phase 8 PASS.

Phase 8 PASS still requires the full frozen live-shadow campaign and exact final review outcome `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN`. Even that outcome permits Phase 9 design only and never authorizes broker execution.
