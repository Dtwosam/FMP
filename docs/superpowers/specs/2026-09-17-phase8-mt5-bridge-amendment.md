# Phase 8 MT5 Demo Quote Bridge Amendment

**Status:** APPROVED / ACTIVATED  
**Date:** 2026-09-17  
**Repository:** `Dtwosam/FMP`  
**Phase:** 8 — Live shadow mode  
**Amends:** `docs/superpowers/specs/2026-09-15-phase8-shadow-design.md` / DEC-036  
**Proposed decision:** DEC-037  
**Proposed experiment:** EXP-20260917-010  
**Branch:** `phase8-mt5-bridge-amendment`

## 1. Purpose and phase boundary

This amendment replaces the unavailable OANDA Practice quote-source path with a read-only MetaTrader 5 demo quote bridge for the same frozen Phase 8 shadow boundary.

The operator cannot open the OANDA account required by DEC-036 because OANDA does not accept new clients from the operator's country of residence. The original Phase 8 design explicitly requires a new approved design amendment rather than an automatic fallback when OANDA Practice is unavailable.

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

The selected FP Markets demo account is a Raw account, but this amendment does **not** reinterpret the frozen Phase 8 financial simulation as broker-specific executable economics. Raw-account commission is not added ad hoc after observing live quotes. If Phase 8 eventually passes, any Phase 9 demo-execution design must explicitly model and gate the actual broker commission schedule before placing any demo order.

## 3. Provider decision

### 3.1 Selected provider path

The amended Phase 8 live quote source is the operator's FP Markets MetaTrader 5 **demo** account, consumed through a purpose-built read-only MQL5 Expert Advisor named:

`FMPPhase8QuoteBridge`

The Expert Advisor is attached only to the `USDJPY` chart in the operator's local MT5 terminal. It reads incoming quote events and writes a local transport file. FMP reads that file and does not call the MetaTrader5 Python package.

The bridge is a quote-source adapter, not a broker execution adapter.

### 3.2 Why the file bridge is selected

Three approaches were considered:

1. MQL5 Expert Advisor -> local file -> FMP reader;
2. MQL5 Expert Advisor -> localhost socket -> FMP reader;
3. direct Python `MetaTrader5` package integration.

The file bridge is selected because it minimizes runtime surface and makes the no-order boundary easier to audit. The direct Python package is rejected because it exposes execution functions such as `order_send()`. The socket bridge is deferred because it adds network lifecycle and transport complexity without a Phase 8 requirement for sub-file-system latency.

### 3.3 No automatic provider fallback

This amendment authorizes only the FP Markets MT5 demo bridge described here. There is no automatic fallback to OANDA production, MT5 live accounts, another broker, another symbol, cTrader, or a generic market-data vendor.

Any later provider change requires another design amendment and source-of-truth update.

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

The bridge performs only account-mode validation, server/symbol validation, tick reads, timer handling, account fingerprint hashing, session identification, and file writes.

A repository-level structural guard must scan the bridge source and fail if forbidden execution surfaces are introduced.

### 4.2 FMP runtime restrictions

Python runtime code under `src/fmp/shadow` must continue to import no `MetaTrader5` or `mt5` package and expose no public broker mutation method.

The existing repository-level structural safety guard is amended only enough to permit the local-file quote reader while continuing to prohibit broker execution surfaces.

### 4.3 AutoTrading remains off

The operator is instructed to keep the MT5 AutoTrading button disabled. MetaQuotes documents that `OnTick()` continues to receive NewTick events even when AutoTrading is disabled; disabling AutoTrading blocks EA trade requests but does not stop EA event processing.

Official reference:

- `https://www.mql5.com/en/docs/event_handlers/ontick`

AutoTrading-off is an additional operator safety control, not the primary structural guarantee. The bridge source itself must remain incapable of submitting trades.

## 5. Account, server, symbol, and fingerprint binding

The bridge must fail closed during initialization unless all of the following are true:

- `AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_DEMO`;
- chart symbol is exactly `USDJPY`;
- account server is exactly one of `FPMarketsSC-Demo` or `FPMarketsSC-Demo2`;
- the first accepted tick has finite positive Bid and Ask with Bid <= Ask.

Only those two demo server names observed in the operator's FP Markets MT5 server selection are authorized by this amendment. `FPMarketsSC-Live`, `FPMarketsSC-Live2`, any other live server, and any caller-supplied arbitrary server are forbidden.

The plain account login must never be written to the bridge transport file or Phase 8 evidence. The EA computes a lowercase SHA-256 fingerprint locally from the account login using MQL5 hashing support and writes only the fingerprint.

Official hashing reference:

- `https://www.mql5.com/en/docs/common/cryptencode`

## 6. Bridge transport protocol

### 6.1 File transport

The bridge writes to an MT5 sandbox file using `FILE_COMMON`, making the transport file consistently locatable from the Wine-backed macOS terminal.

Official references:

- `https://www.mql5.com/en/docs/files/fileopen`
- `https://www.mql5.com/en/docs/files/fileflush`

The file name is fixed in source:

`FMP/phase8-usdjpy-feed.jsonl`

No arbitrary output path is accepted from the operator or FMP CLI.

The bridge file is a **local transport**, not the durable Phase 8 evidence ledger. FMP remains responsible for durable append-only evidence under the existing evidence architecture.

### 6.2 Bridge session lifecycle

Each EA initialization creates a new bridge session identifier and starts a fresh local transport session. Recreating/truncating the transport file is allowed only at EA session initialization before the first session record. During an active bridge session, records are append-only and the bridge must not rewrite earlier records.

The first complete record in every bridge session is `BRIDGE_START`. All later records in that file must carry the same `bridge_session_id`, demo-server identifier, and account fingerprint.

If the EA restarts, a new bridge session begins. FMP treats that as a restart boundary; it never assumes unseen market continuity across the restart.

### 6.3 Record types

The bridge emits exactly three record types:

- `BRIDGE_START`
- `TICK`
- `BRIDGE_HEARTBEAT`

No order, trade, position, balance, margin, transaction, or account-history records are emitted.

### 6.4 BRIDGE_START record

`BRIDGE_START` contains only:

- protocol version
- record type `BRIDGE_START`
- `bridge_session_id`
- fixed symbol `USDJPY`
- demo account mode marker
- approved demo-server identifier
- one-way account fingerprint
- bridge start audit time

It contains no password, token, account name, or plain account login.

FMP validates this record before accepting any tick or heartbeat from the session.

### 6.5 TICK record

Each `TICK` record contains only:

- protocol version
- record type `TICK`
- `bridge_session_id`
- fixed symbol `USDJPY`
- source tick time in milliseconds from `MqlTick.time_msc`
- Bid
- Ask
- MQL5 tick flags
- approved demo-server identifier
- one-way account fingerprint

`MqlTick` is the authoritative source for Bid, Ask, tick time, and flags.

Official reference:

- `https://www.mql5.com/en/docs/constants/structures/mqltick`

The bridge does not emit Last price, volume, leverage, account equity, account balance, or personally identifying account fields because Phase 8 does not need them.

### 6.6 BRIDGE_HEARTBEAT record

The bridge emits one `BRIDGE_HEARTBEAT` approximately every five seconds from an EA timer.

The heartbeat proves only that the local MT5/EA/file bridge is alive. It is **not** an FP Markets provider heartbeat and is never used as authoritative market time.

It contains:

- protocol version
- record type `BRIDGE_HEARTBEAT`
- `bridge_session_id`
- fixed symbol `USDJPY`
- bridge emission audit time
- approved demo-server identifier
- one-way account fingerprint
- last observed tick source-time milliseconds, or null before the first tick

A bridge heartbeat never creates or closes a market bar, advances strategy time, triggers entry/exit, or satisfies a market-quote deadline.

## 7. Append, durability, and reader-start semantics

The bridge opens the transport file for shared reading/writing and appends complete newline-terminated records during an active session. It calls `FileFlush()` after each emitted record during qualification and live-shadow capture so FMP can observe durable transport records promptly.

FMP treats a partial final line as incomplete and waits for completion. Malformed complete lines are rejected; none are silently accepted.

When FMP qualification or capture starts against an already-running EA session, it may read the initial `BRIDGE_START` only to establish the active session identity, then records the current end-of-file offset. Qualification/capture counts and processes only complete records appended **after** that reader-start offset. Earlier ticks in the local transport file are not replayed into the live campaign and cannot be used as backfill.

FMP durable evidence records the accepted bridge inputs and its own receive metadata. It never reconstructs ticks missed while MT5, the EA, the Mac, or FMP was stopped.

## 8. Timestamp and liveness semantics

### 8.1 Market ordering

Market ordering uses `MqlTick.time_msc` from each accepted `TICK` record. FMP converts the millisecond epoch into an aware UTC datetime before constructing the existing `NormalizedQuote` contract.

FMP records its own local UTC receive timestamp and segment-local monotonic receive timestamp when it observes each complete record. These remain the timing inputs for processing-latency evidence.

Tick source-time regression fails closed for the current segment. Exact duplicate ticks may be deduplicated only when source time, symbol, Bid, Ask, flags, session identity, server identity, and account fingerprint are identical. A conflicting duplicate at the same source time is an integrity failure.

### 8.2 Two liveness dimensions

The MT5 bridge separates local bridge liveness from market-feed liveness:

- **bridge liveness:** time since the last valid `BRIDGE_START`, `TICK`, or `BRIDGE_HEARTBEAT` record received by FMP;
- **market-feed liveness:** time since the last valid `TICK` received by FMP.

The existing 15-second Phase 8 stale threshold applies conservatively to both dimensions during a live-shadow segment. A missing bridge heartbeat diagnoses local EA/file failure; continuing heartbeats with no tick diagnose an alive bridge with a stalled/quiet market feed. Either condition crossing 15 seconds makes the live shadow stream stale and invalidates continuity under the existing gap rules.

During bounded qualification, a >15-second market-feed gap while bridge heartbeats continue may return `INCONCLUSIVE` rather than `CONNECTOR_REJECTED` when no integrity defect is present and market activity is insufficient. A >15-second bridge-liveness gap or malformed identity is a connector failure.

## 9. Normalization boundary

The MT5-specific adapter handles bridge records as follows:

- valid `BRIDGE_START` -> session binding only;
- valid `TICK` -> existing `NormalizedQuote`;
- valid `BRIDGE_HEARTBEAT` -> liveness/operational evidence only.

`BRIDGE_HEARTBEAT` is deliberately **not** converted into the existing market `HeartbeatEvent`, because a local EA heartbeat is not provider market time and must not advance the live bar builder.

For a valid `TICK`:

- symbol must be exactly `USDJPY`;
- Bid and Ask must be finite and positive;
- Bid must be <= Ask;
- bridge session ID, account fingerprint, and server identity must match the active session binding;
- source tick timestamp must parse as UTC epoch time;
- `tradeable=True` is assigned only after the demo/server/symbol/tick integrity boundary passes, meaning the quote may form shadow bars; it does not authorize broker execution.

After normalization, the existing live-bar builder, frozen strategy adapter, shadow simulator, evidence writer, deterministic replay, and financial review logic are reused.

No strategy code is reimplemented for MT5.

## 10. Qualification protocol

Qualification remains an explicit operator action before any live-shadow campaign begins.

It runs for at most ten minutes and may stop early only after all of the following are observed **after qualification reader start**:

- one valid active-session `BRIDGE_START` binding;
- at least 100 valid `TICK` records;
- at least 6 valid `BRIDGE_HEARTBEAT` records.

Qualification PASS additionally requires:

- bridge protocol/version match;
- demo account mode proven by `BRIDGE_START`;
- approved FP Markets demo server identity;
- only `USDJPY` tick records;
- finite positive Bid and Ask on every accepted tick;
- Bid <= Ask;
- tick source timestamps do not regress;
- no bridge-liveness gap greater than 15 seconds;
- no market-feed liveness gap greater than 15 seconds;
- no malformed or unknown complete record silently accepted;
- structural safety tests prove the EA and Python runtime contain no broker mutation surfaces.

Low market activity that prevents the sample minimum or market-feed liveness requirement without an integrity failure returns `INCONCLUSIVE`.

Missing file, inactive EA, wrong account type, wrong server, wrong symbol, or inaccessible bridge returns `CONNECTOR_UNAVAILABLE` unless evidence identifies an implementation defect.

Malformed/conflicting records, source-time regression, session/identity mismatch, or safety violation returns `CONNECTOR_REJECTED`.

Qualification invokes no strategy logic.

Successful local compilation of `FMPPhase8QuoteBridge.mq5` in MetaEditor and successful attachment to the demo USDJPY chart are operator preconditions to qualification; CI does not claim to compile MQL5 unless a trusted compiler is later added explicitly.

## 11. Evidence protocol amendment

The existing evidence protocol hard-codes the OANDA Practice connector identity. The amended implementation therefore bumps the evidence protocol version rather than reusing OANDA-specific fields with new meanings.

Frozen amended values:

- evidence protocol: `fmp-phase8-shadow-evidence-v2`
- connector protocol: `fmp-mt5-demo-file-bridge-v1`
- provider: `FP_MARKETS_MT5_DEMO`
- provider instrument: `USDJPY`
- transport: `MT5_FILE_COMMON_JSONL`
- bridge file: `FMP/phase8-usdjpy-feed.jsonl`
- allowed servers: `FPMarketsSC-Demo`, `FPMarketsSC-Demo2`

OANDA-specific manifest fields such as HTTP method, host, path template, snapshot, and home-conversion flags are removed from new v2 segments.

New connector-bound manifest fields include:

- connector protocol
- provider
- provider instrument
- transport identity
- bridge file identity
- bridge session identity
- approved demo-server identity
- account fingerprint SHA-256
- bridge source/repository commit binding

All existing strategy, upstream Phase 7 identity, slippage scenario, risk policy, file hashes, replay digest, run start/end, and code-commit bindings remain.

The review compiler accepts only the registered evidence protocol/connector identity for the campaign. OANDA v1 and MT5 v2 segments must not be mixed inside one registered campaign.

## 12. Campaign identity and source-of-truth transition

The OANDA connector attempt under `EXP-20260915-009` did not reach successful connector qualification and produced no scored live-shadow campaign evidence.

The source-of-truth amendment will record that experiment as stopped before qualification because the required account is unavailable to the operator's jurisdiction. This is not a market, strategy, financial, or safety rejection.

New experiment identity:

`EXP-20260917-010 — Phase 8 MT5 demo live-shadow evaluation`

Proposed decision:

`DEC-037 — Replace unavailable OANDA Practice connector with read-only FP Markets MT5 demo quote bridge`

The new campaign must be registered from scratch under the amended connector identity before the first scored observation. No prior OANDA qualification or campaign evidence may be reclassified as MT5 evidence.

Phase 8 remains ACTIVE. Phase 9 remains locked.

## 13. Operator workflow on macOS

After source-free implementation verification passes, the operator workflow is:

1. keep the FP Markets MT5 demo account logged in;
2. confirm `USDJPY` is receiving changing quotes;
3. keep MT5 AutoTrading disabled;
4. install and compile `FMPPhase8QuoteBridge.mq5` in MetaEditor;
5. attach the EA to the `USDJPY` chart only;
6. verify the EA reports demo/server/symbol startup checks as PASS;
7. run the bounded FMP qualification command against the fixed bridge transport;
8. inspect qualification evidence;
9. only after PASS, build/freeze the historical spread reference and register the new campaign;
10. start each shadow segment explicitly;
11. replay every finalized segment offline.

No daemon, launch agent, cron job, auto-start service, or CI job starts MT5 or the live campaign.

## 14. Testing requirements

Implementation must use TDD and include at least:

### 14.1 MQL5 structural safety tests

Repository tests inspect the `.mq5` source and reject forbidden trading identifiers/imports.

Tests also require explicit source checks for:

- demo account mode validation;
- exact USDJPY symbol validation;
- exact two-server demo allowlist;
- explicit rejection/absence of live server literals;
- fixed output file identity;
- fixed protocol version;
- local SHA-256 fingerprinting;
- `BRIDGE_START`, `TICK`, and `BRIDGE_HEARTBEAT` record support.

### 14.2 Python bridge reader/parser tests

Cover:

- valid start/tick/heartbeat parsing;
- malformed/unknown record rejection;
- wrong symbol rejection;
- wrong server rejection;
- wrong session rejection;
- account fingerprint mismatch rejection;
- crossed/non-finite/non-positive price rejection;
- source-time regression;
- exact duplicate handling;
- conflicting duplicate rejection;
- partial-line handling;
- reader-start offset/no-backfill behavior;
- heartbeat never advancing market bars;
- separate bridge and market liveness;
- no silent malformed acceptance.

### 14.3 Qualification tests

Cover PASS, INCONCLUSIVE, CONNECTOR_UNAVAILABLE, and CONNECTOR_REJECTED with injected clocks and temporary bridge files.

### 14.4 Runner and replay parity tests

Prove that accepted MT5 ticks reach the same existing normalized quote -> bars -> strategy -> simulator pipeline and deterministic replay reproduces derived evidence from captured bridge inputs.

### 14.5 Evidence/campaign tests

Prove v2 manifest identity, no OANDA-specific connector fields in v2 segments, no mixed connector protocols in one campaign, account-secret redaction, and unchanged acceptance thresholds.

### 14.6 Full regression

Before merge:

- all Phase 8 tests PASS;
- full Python test suite PASS;
- workflow YAML validation PASS;
- Python compile PASS;
- Phase 3 deterministic acceptance remains PASS;
- no Phase 1 acquisition path runs;
- no live MT5 qualification runs in CI.

## 15. Failure handling

The bridge and FMP fail closed.

Examples:

- EA detached or terminal closes -> bridge liveness timeout, current date becomes ineligible, open shadow outcomes become unknown after gap;
- EA alive but no tick for >=15 seconds -> market-feed stale, same continuity invalidation rules apply;
- bridge file cannot be read -> connector unavailable/failure evidence, no strategy continuation;
- demo-to-live account change -> bridge startup/runtime identity fails and no valid ticks are accepted;
- wrong server or symbol -> bridge initialization/session rejection;
- malformed record -> durable rejection and segment failure;
- source-time regression/conflicting duplicate -> integrity failure;
- EA/FMP restart -> no reconstruction/backfill; current London date is handled under existing restart rules.

No historical MT5 candles, broker order history, positions, account state, or reconstructed tick path may be used to repair a live gap.

## 16. Security and privacy

No broker password is required by FMP.

The EA runs inside the already authenticated local MT5 terminal. The transport file contains no password, token, account name, or plain account login.

Durable FMP evidence stores only the approved provider/server/session identity and a one-way account fingerprint for run binding.

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
