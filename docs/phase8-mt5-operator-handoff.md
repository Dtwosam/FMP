# Phase 8 MT5 Operator Handoff (macOS)

> **PAUSED BY DEC-039 — DO NOT REGISTER OR START EXP-20260922-011.**  
> The connector qualification/reference artifacts remain valid non-scored evidence, but Phase 8A portfolio research is now active. This handoff is retained for historical/technical reference until Phase 8B defines the multi-pair shadow campaign.

Status: historical/operator reference for the read-only USDJPY bridge. **Campaign launch is paused under DEC-039.**

This workflow is **read-only**. It reads the FP Markets MT5 demo USDJPY quote feed through the local `FMPPhase8QuoteBridge.mq5` Expert Advisor. Keep **AutoTrading OFF** throughout. There are **no demo or live orders** in this workflow, and no step authorizes broker execution.

Do not share your broker password, account password, access token, Client Secret, or other credentials in chat, GitHub, repository files, evidence, or command-line arguments. FMP does not need them for this MT5 file bridge.

## 1. Confirm the MT5 demo session

Before touching the bridge:

- MT5 must be logged into the FP Markets **demo** account.
- The active server must be exactly `FPMarketsSC-Demo` or `FPMarketsSC-Demo2`.
- `USDJPY` must be visible in Market Watch and receiving changing Bid/Ask quotes.
- Keep **AutoTrading OFF**.

If the account, server, or symbol is wrong, stop. Do not substitute another broker, server, symbol, or live account into this campaign.

## 2. Install and compile the read-only EA

The repository source is:

`mt5/Experts/FMPPhase8QuoteBridge.mq5`

On the Mac MT5 terminal:

1. Choose **File -> Open Data Folder**.
2. Open `MQL5/Experts`.
3. Copy `FMPPhase8QuoteBridge.mq5` into that folder.
4. Open the file in **MetaEditor** and compile it.
5. Require a successful compile with no errors before continuing.
6. Return to MT5. In Navigator, refresh Expert Advisors if needed.
7. Open the `USDJPY` chart and attach `FMPPhase8QuoteBridge` to that chart only.
8. Leave **AutoTrading OFF**.

The EA fails closed unless the chart is `USDJPY`, the account is demo, and the server is one of the two approved demo servers. It has no order/trade execution surface.

The bridge writes through MT5 `FILE_COMMON` to the fixed logical file:

`FMP/phase8-usdjpy-feed.jsonl`

FMP discovers that fixed file automatically. There is no supported `--path`, filename, server, credential, or instrument override.

## 3. Run the bounded connector qualification

From the FMP repository:

```bash
python scripts/phase8_shadow.py qualify --out evidence/phase8/qualification
```

Qualification runs for at most ten minutes and uses only records appended after the reader starts. It does not run strategy logic.

Qualification also verifies that MT5 tick source times are aligned to UTC within the frozen 5-second quote deadline. The EA converts the broker/server tick clock to UTC before writing `source_time_msc`; a multi-hour broker clock offset must therefore fail qualification rather than shift the London-session bars.

Interpret the result exactly:

- `PASS` — the connector qualification passed; continue to the historical reference step.
- `INCONCLUSIVE` — market activity was insufficient or the bounded sample could not qualify without an integrity failure. Keep the evidence and retry later without changing the protocol.
- `CONNECTOR_UNAVAILABLE` — the local bridge is missing, inactive, inaccessible, or not correctly attached. Check MT5, the EA, demo login, server, and USDJPY chart.
- `CONNECTOR_REJECTED` — an integrity/session/source-time/safety condition failed. Stop, retain the evidence, and correct the defect before a fresh qualification.

A qualification `PASS` is only permission to proceed with Phase 8 evidence collection. It is not Phase 8 PASS.

## 4. Build and freeze the historical spread reference

Only after qualification `PASS`:

```bash
python scripts/phase8_shadow.py build-reference \
  --dataset-root <accepted-phase2-dataset-root> \
  --processed-manifest <accepted-usdjpy-processed-manifest> \
  --out evidence/phase8/reference
```

Use only the already accepted Phase 2/7 USDJPY artifacts bound by the repository. Do not use MT5 historical candles to repair or replace them.

## 5. Register the new MT5 campaign once

```bash
python scripts/phase8_shadow.py register \
  --reference evidence/phase8/reference \
  --campaign-dir evidence/phase8/campaign
```

Registration freezes the connector/evidence identity and the existing Phase 8 thresholds. Do not edit the registration after scored observation begins.

## 6. Start an explicit shadow-capture segment

```bash
python scripts/phase8_shadow.py run --campaign-dir evidence/phase8/campaign
```

This is an operator-started local capture, not a daemon. Stop the segment explicitly when intended.

A restart, disconnect, **bridge-liveness stale interval**, MT5 restart, or EA restart is a real continuity break. There is **no backfill** and no reconstruction of unseen price path. FMP must never use pre-reader transport content, MT5 candles, or another provider to fill a gap.

A no-tick period while bridge heartbeats remain healthy is recorded as `market_quiet` and, by itself, does **not** invalidate the entire London date. The safety gates remain fail-closed:

- if required 1m/15m market context is actually missing, the strategy date becomes incomplete/ineligible;
- if a simulated position is open when a market-quiet gap crosses the 15-second threshold, that position outcome becomes unknown rather than being scored from an unseen price path;
- entry and scheduled-exit quotes still must satisfy the frozen 5-second quote deadline;
- no missing quote path is backfilled or reconstructed.

## 7. Replay every finalized segment offline

For every finalized segment:

```bash
python scripts/phase8_shadow.py replay --segment-dir evidence/phase8/campaign/<segment>
```

Any replay mismatch blocks acceptance for that segment. Retain failed evidence; do not rewrite it into a passing result.

## 8. Review the frozen campaign evidence

When enough real campaign evidence exists:

```bash
python scripts/phase8_shadow.py review --campaign-dir evidence/phase8/campaign
```

The existing Phase 8 minimums and operational/market/financial/safety gates remain unchanged. A short campaign should return the existing need-more-data outcome rather than relaxing thresholds.

Even a final Phase 8 outcome of `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN` **does not authorize** a demo order, live order, or real-money action. It permits only separate **Phase 9 design** work under its own later approval gates.

## Troubleshooting the local bridge

If FMP cannot discover the bridge file:

- confirm the EA is attached to the `USDJPY` chart;
- confirm MT5 is still logged into the approved demo server;
- inspect MT5's Experts/Journal messages for an EA startup rejection;
- confirm the source compiled successfully in MetaEditor;
- confirm the EA is using the fixed `FILE_COMMON` transport.

If discovery finds more than one candidate file, stop and resolve the stale/duplicate MT5 terminal data roots. Do not add or use an arbitrary path override.

If qualification reports `SOURCE_TIME_SKEW`, stop. Confirm that the installed EA is the current repository version, recompile it in MetaEditor, and requalify before starting a campaign. Do not reinterpret or backfill previously captured timestamps.

If the EA restarts, it creates a new bridge session. Treat that as a restart boundary; do not claim continuity across it.
