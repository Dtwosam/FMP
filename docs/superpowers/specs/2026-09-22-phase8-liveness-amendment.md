# Phase 8 Bridge/Market Liveness Separation Amendment

**Status:** APPROVED / ACTIVATED — DEC-038; implementation verification pending merge  
**Date:** 2026-09-22  
**Repository:** `Dtwosam/FMP`  
**Phase:** 8 — Live shadow mode  
**Experiment:** `EXP-20260922-011`  
**Decision:** `DEC-038`  
**Checkpoint target:** `fmp-v1-phase8-shadow`

## 1. Purpose

This amendment refines only the Phase 8 live-shadow liveness semantics after prospective FP Markets MT5 demo evidence showed that the local bridge can remain continuously healthy while USDJPY produces no new tick for more than the original 15-second market-feed timeout.

The strategy, risk policy, slippage scenarios, quote deadlines, campaign minimums, acceptance thresholds, provider, server allowlist, symbol, transport, evidence integrity, deterministic replay, and structural no-order boundary remain unchanged.

This amendment does not authorize demo orders, live orders, broker mutation, or real-money trading. Phase 9 remains locked.

## 2. Diagnostic evidence from EXP-20260917-010

The UTC-correct MT5 campaign under `EXP-20260917-010` is retained as diagnostic evidence only and is not eligible to be reclassified under this amendment.

During the diagnostic capture:

- 46,721 normalized USDJPY quotes were observed;
- 1,340 quote-to-quote gaps exceeded 5 seconds;
- 291 exceeded 10 seconds;
- 102 exceeded 15 seconds;
- 23 exceeded 30 seconds;
- 3 exceeded 60 seconds;
- the maximum observed gap was 4,301.580 seconds;
- across the long approximately 10:18–11:30 UTC no-tick interval on 2026-09-21, 870 valid `BRIDGE_HEARTBEAT` records were still received.

The evidence therefore distinguishes an alive MT5/EA/file transport from periods with no new market tick. Treating both conditions as the same whole-day continuity failure made valid-date accumulation depend on normal/possible tick-arrival sparsity rather than only on actual transport failure or missing strategy/execution evidence.

## 3. Frozen amended liveness semantics

The existing 15-second constant remains `LIVENESS_TIMEOUT_SECONDS = 15.0`, but its live-capture meaning is separated by liveness dimension.

### 3.1 Bridge liveness

Bridge liveness is time since the last valid `BRIDGE_START`, `TICK`, or `BRIDGE_HEARTBEAT` received by FMP.

If bridge silence reaches 15 seconds:

- emit the existing `stale` operational event with `liveness_reason = "bridge"`;
- mark the current London date ineligible;
- invalidate any open simulated trade path as unknown after gap;
- mark the affected live-bar interval stale;
- preserve the existing recovery and no-backfill rules.

This remains a true continuity failure.

### 3.2 Market tick activity while the bridge is healthy

Market tick activity is time since the last valid `TICK`.

If no new tick is received for 15 seconds while valid bridge records continue to arrive:

- emit a diagnostic `market_quiet` operational event;
- do **not** mark the whole London date ineligible solely because of that no-tick duration;
- do **not** synthesize ticks, candles, or prices;
- do **not** mark otherwise observed bar time stale solely from the elapsed no-tick duration;
- on the next valid market quote, emit `market_resumed`.

A `market_quiet` interval is not proof that the broker market feed is healthy or unhealthy. It records only the observed fact that the bridge remained alive while no new valid tick reached FMP for the threshold duration.

## 4. Fail-closed protections that remain mandatory

Separating market quiet from bridge failure does not permit FMP to score unseen price paths.

- If a simulated position is open when a market-quiet interval crosses 15 seconds, that position is invalidated as `OUTCOME_UNKNOWN_AFTER_GAP`. It is not scored from a later price.
- If a required 1-minute or 15-minute bar cannot be constructed from actually observed quotes, the strategy retains its existing incomplete-session behavior and the affected London date is ineligible when required context is missing.
- Entry and scheduled-exit execution still require a valid quote within the frozen 5-second quote deadline. Missed deadlines fail closed under the existing simulator outcomes.
- Tick source-time regression, malformed/conflicting records, bridge/session/account/server/symbol identity failures, restart boundaries, and disconnects retain their existing failure behavior.
- No historical MT5 candle, prior transport content, alternate provider, interpolated price, reconstructed tick, or other backfill may repair a live gap.

## 5. Qualification

The bounded MT5 connector qualification remains unchanged.

Qualification may still return `INCONCLUSIVE` when market activity is insufficient or market-feed liveness exceeds the existing bounded requirement without an integrity defect. Bridge-liveness failure or identity/integrity defects retain their existing failure outcomes.

This amendment changes scored live-shadow capture semantics, not the purpose of qualification as a short connector-health gate.

## 6. Evidence and replay identity

The evidence protocol remains `fmp-phase8-shadow-evidence-v2` because the durable connector/manifest schema does not change. The new `market_quiet` and `market_resumed` records are operational event values inside the existing stream.

A fresh campaign is mandatory because campaign registration and every segment manifest bind the exact code commit. Evidence produced under the superseded EXP-010 live-runner semantics cannot be mixed with or reclassified into the amended campaign.

## 7. Experiment transition

`EXP-20260917-010` is stopped as **INCONCLUSIVE / DIAGNOSTIC** after exposing the liveness-design defect. Its qualification and campaign evidence remain preserved for audit and do not count toward Phase 8 acceptance.

The amended experiment is:

`EXP-20260922-011 — Phase 8 MT5 demo live-shadow evaluation with separated bridge/market liveness`

Before EXP-011 scored observation:

1. merge and verify this amendment implementation;
2. preserve/archive EXP-010 local evidence without rewriting it;
3. run a fresh connector qualification;
4. rebuild the historical reference under the new merged code commit;
5. register a fresh campaign under `EXP-20260922-011`;
6. start a fresh prospective segment with no backfill.

The eight-week, 30 fully observed London dates, 40 completed scorable 0.2-pip trades, coverage, latency, quote-delay, spread-parity, drawdown, financial, scenario-consistency, replay, and structural safety gates remain unchanged.

## 8. Safety boundary

The MQL5 bridge remains read-only and structurally incapable of trade submission. Python shadow runtime remains without a MetaTrader5 execution surface. Keep AutoTrading OFF.

Even a future `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN` result permits only separate Phase 9 design work. It does not authorize demo execution, live execution, or real-money trading.
