# Phase 8B MT5 Operator Handoff — Multi-Strategy Portfolio Shadow

**Status:** current operator reference for the Phase 8B prospective shadow campaign.

This workflow is **read-only**. It uses the FP Markets MT5 DEMO account only to
export quote/heartbeat records through the repository's Phase 8B FILE_COMMON
bridge. It never places an order and never authorizes broker mutation. It does not authorize a demo order, live order, broker mutation, or real-money action.

Keep **AutoTrading OFF** throughout Phase 8B.

Do not place broker passwords, account passwords, access tokens, or other
credentials in chat, GitHub, repository files, evidence artifacts, or command
arguments.

## 1. What Phase 8B is testing

Phase 8B prospectively tests the immutable portfolio accepted by Phase 8A.

The V1 research universe is:

- EURUSD
- GBPUSD
- USDJPY

The exact required symbols for a campaign come from the frozen Phase 8B design.
A candidate may require two or three V1 pairs; do not add or remove a pair by
hand.

The Phase 7 USDJPY 15m session-breakout strategy is a historical
baseline/control. Phase 8B is not a USDJPY-only campaign.

## 2. Freeze the Phase 8B design

Start from the exact accepted DEC-045 Phase 8A acceptance artifact:

```bash
python scripts/phase8b_shadow.py design \
  --acceptance <phase8a-acceptance.json> \
  --code-commit "$(git rev-parse HEAD)" \
  --out evidence/phase8b/design
```

The design freezes the champion set, strategy fingerprints, required symbols,
required timeframes, connector contract, liveness limits, and 0.2 / 0.5 /
1.0-pip scenarios.

Do not edit the design after creation.

## 3. Install the current multi-symbol read-only bridge

Use this repository EA:

`mt5/Experts/FMPPhase8BQuoteBridge.mq5`

Do **not** use the older `FMPPhase8QuoteBridge.mq5` USDJPY-only Phase 8 file for
the Phase 8B campaign.

On the MT5 terminal:

1. Log in to the accepted FP Markets **DEMO** account.
2. Require server `FPMarketsSC-Demo` or `FPMarketsSC-Demo2`.
3. Keep AutoTrading OFF.
4. Choose **File -> Open Data Folder**, then open `MQL5/Experts`.
5. Copy `FMPPhase8BQuoteBridge.mq5` there and compile it in MetaEditor with no errors.
6. Open one chart for every symbol listed in the frozen design's
   `required_symbols`.
7. Attach one instance of `FMPPhase8BQuoteBridge` to each required-symbol
   chart.

The EA accepts only EURUSD, GBPUSD, and USDJPY and writes fixed FILE_COMMON
files:

- EURUSD -> `FMP/phase8b-eurusd-feed.jsonl`
- GBPUSD -> `FMP/phase8b-gbpusd-feed.jsonl`
- USDJPY -> `FMP/phase8b-usdjpy-feed.jsonl`

All required symbol instances must come from the same accepted DEMO
account/server. There is no supported arbitrary path, symbol, server, or live
account override.

## 4. Qualify the required feeds

```bash
python scripts/phase8b_shadow.py qualify \
  --design evidence/phase8b/design/design.json \
  --out evidence/phase8b/qualification
```

Qualification is bounded and read-only. It requires the frozen bridge identity,
DEMO account, approved server, source-time integrity, heartbeats, and quote
activity for every required symbol.

Interpret outcomes literally:

- `PHASE8B_CONNECTOR_QUALIFIED` — all required feeds qualified.
- `INCONCLUSIVE` — retain evidence and retry later without changing the
  protocol.
- `CONNECTOR_UNAVAILABLE` — a required bridge/file is missing or inaccessible.
- `CONNECTOR_REJECTED` — an identity, integrity, source-time, or safety check
  failed.

Qualification is not Phase 8 PASS.

## 5. Register the campaign once

Only after connector qualification passes:

```bash
python scripts/phase8b_shadow.py register \
  --design evidence/phase8b/design/design.json \
  --qualification evidence/phase8b/qualification/qualification.json \
  --campaign-dir evidence/phase8b/campaign
```

Registration freezes the exact campaign identity, champion set, required
symbols, account/server, and per-symbol bridge-session IDs.

Do not edit or overwrite registration evidence.

## 6. Authorize the prospective start boundary

With the same bridge sessions still running:

```bash
python scripts/phase8b_shadow.py authorize-start \
  --campaign-dir evidence/phase8b/campaign
```

This creates the immutable campaign start plus capture preflight and establishes
the tail-at-current-EOF/no-backfill boundary.

If a bridge session changed since registration, stop and requalify/register a
new campaign. Do not silently rebind the existing campaign.

## 7. Freeze the historical spread reference

After start authorization/preflight and before capture:

```bash
python scripts/phase8b_shadow.py freeze-spread-reference \
  --campaign-dir evidence/phase8b/campaign \
  --dataset-root <accepted-phase2-dataset-root>
```

This uses the accepted retrospective canonical BID/ASK dataset only. It does not
use future captured results to choose spread thresholds.

## 8. Run the read-only readiness audit

Immediately before a prospective segment:

```bash
python scripts/phase8b_shadow.py readiness \
  --campaign-dir evidence/phase8b/campaign
```

The readiness command writes nothing to the campaign directory and consumes no
post-EOF quote records. It checks the frozen artifact chain and the currently
visible bridge-start identities.

Possible useful next actions are:

- `authorize-start`
- `freeze-spread-reference`
- `capture-segment`

A readiness result is **not authorization evidence** and does not prove current
15-second liveness or 5-second quote freshness. The actual capture runtime
revalidates independently.

## 9. Capture one bounded prospective segment

Only by explicit operator action:

```bash
python scripts/phase8b_shadow.py capture-segment \
  --campaign-dir evidence/phase8b/campaign \
  --duration-seconds <1-to-86400>
```

Each invocation is one prospective segment. The fixed polling interval is
source-controlled.

The segment stores append-only/fsynced raw records, latency audit rows,
operational events, compiled shadow evidence, and deterministic replay evidence.

Important continuity rules:

- no pre-reader content is admitted;
- no missing interval is backfilled;
- no MT5 candle is used to reconstruct unseen price path;
- no alternate provider repairs a gap;
- an EA/MT5/FMP restart is a real restart boundary;
- malformed/truncated/session-replaced feeds fail closed;
- a clean segment must replay exactly.

A quiet market with healthy bridge heartbeats is distinct from a dead bridge.
The frozen runtime handles that distinction.

## 10. Inspect campaign progress without closing

After one or more clean segments, you may inspect current evidence progress
without creating a closure:

```bash
python scripts/phase8b_shadow.py progress \
  --campaign-dir evidence/phase8b/campaign
```

The progress command reuses the exact campaign-close aggregation kernel but
writes no closure, review, acceptance, or terminal artifact. It reports current
elapsed weeks, complete London dates, completed 0.2-pip trades, represented
strategy families/pairs, remaining DEC-051 minimums, replay status, and whether
the current aggregate is closeable.

Meeting all minimums in this preview is not Phase 8B PASS. Formal close and
review remain mandatory.

## 11. Close a campaign evidence snapshot

After one or more clean segments:

```bash
python scripts/phase8b_shadow.py close-campaign \
  --campaign-dir evidence/phase8b/campaign
```

The command prints a `closure_id`. Closing creates an immutable aggregate
snapshot; it does not permanently stop further capture when the eventual review
returns NEED_MORE_DATA.

## 12. Review the closure

```bash
python scripts/phase8b_shadow.py review-campaign \
  --campaign-dir evidence/phase8b/campaign \
  --closure-id <closure-id>
```

Phase 8B acceptance remains frozen under DEC-051. Among other gates, acceptance
requires at least:

- 40 completed 0.2-pip scorable trades;
- 8 elapsed weeks;
- 30 complete London dates;
- representation from at least 2 strategy families;
- representation from at least 2 V1 pairs;
- operational/replay/safety integrity;
- frozen spread and financial thresholds.

If the result is `PHASE8B_NEED_MORE_DATA`, keep the same valid campaign,
capture additional clean prospective segments, create a new closure, and review
that new closure. Do not relax thresholds.

A terminal PASS creates the exact SHADOW_VALIDATED evidence needed for Phase 9
design eligibility.

## 13. What Phase 8B never authorizes

Even a Phase 8B PASS does **not** authorize:

- a demo order;
- a live order;
- broker mutation;
- real-money trading;
- Phase 10 deployment;
- Phase 11.

It only permits the separately gated Phase 9 demo-design/evidence chain already
implemented in the repository.

## 14. Troubleshooting

If bridge discovery fails:

- confirm `FMPPhase8BQuoteBridge.mq5` is attached to every required-symbol
  chart;
- confirm MT5 is still on the accepted DEMO account/server;
- inspect MT5 Experts/Journal output for a bridge startup refusal;
- confirm the current EA compiled successfully;
- confirm there is only one discoverable FILE_COMMON file for each required
  symbol.

If a bridge session changes, do not claim continuity. A pre-registration change
requires fresh qualification/registration; a post-start change becomes a real
prospective continuity failure/restart boundary under the frozen campaign
rules.

If source-time skew fails, verify the current repository EA, recompile, and
requalify. Never reinterpret or backfill captured timestamps.
