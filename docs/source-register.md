# FMP External Source Register

**Last verified:** 2026-09-17

This register records external foundations we are allowed to rely on. External documentation can change, so implementation phases should reverify details that affect code before freezing an adapter.

## SRC-001 — Dukascopy Historical Data Export

Official page: https://www.dukascopy.com/api/data/get/historical-data-export

Verified foundation:
- historical data export is available;
- available data includes bid and ask prices and trading volumes.

Allowed use in FMP:
- supports Dukascopy as the primary free historical-data source candidate;
- supports preserving bid/ask rather than using only midpoint candles.

Does **not** yet freeze:
- exact programmatic download endpoint/format;
- rate limits;
- chunk sizes;
- complete field schema for our chosen retrieval path.

Those must be verified in the Phase 1 acquisition spike.

## SRC-002 — Dukascopy Forex Historical Data page

Official page: https://www.dukascopy.com/swiss/english/marketwatch/historical/

Verified foundation:
- Dukascopy provides historical price data for forex and discusses use for strategy testing/analysis.

Allowed use in FMP:
- background/availability confirmation only.

## SRC-003 — OANDA v20 Development Guide and Pricing Stream

Official pages:
- https://developer.oanda.com/rest-live-v20/development-guide/
- https://developer.oanda.com/rest-live-v20/pricing-ep/

Verified foundation on 2026-09-15:
- separate `fxTrade Practice` REST and streaming environments remain documented;
- Practice streaming base URL is `https://stream-fxpractice.oanda.com`;
- production streaming uses a different host and is outside the Phase 8 boundary;
- account pricing stream is `GET /v3/accounts/{accountID}/pricing/stream`;
- the pricing-stream response is line-delimited JSON carrying price and pricing-heartbeat objects;
- the pricing endpoint supports instrument selection, and the frozen Phase 8 provider instrument was `USD_JPY` under DEC-036.

Historical Phase 8 use under DEC-036 / `EXP-20260915-009`:
- OANDA fxTrade Practice pricing stream was the selected initial quote source;
- FMP hard-coded a GET-only Practice pricing boundary at `stream-fxpractice.oanda.com`;
- the experiment stopped before qualification because the required account was unavailable to the operator jurisdiction;
- no OANDA qualification or scored live-shadow campaign evidence was produced;
- DEC-037 / `EXP-20260917-010` supersedes this source role with SRC-005.

Does **not** guarantee:
- account eligibility in every jurisdiction;
- perpetual free access;
- that OANDA will be the final Phase 9 demo broker.

Reverify again before any later demo/execution adapter is designed.

## SRC-004 — MetaTrader 5 Python Integration

Official pages:
- https://www.mql5.com/en/docs/python_metatrader5
- https://www.mql5.com/en/docs/python_metatrader5/mt5symbolinfotick_py
- https://www.mql5.com/en/docs/python_metatrader5/mt5ordersend_py

Verified foundation on 2026-09-15:
- official Python integration remains documented;
- quote access includes `symbol_info_tick`;
- the integration also exposes trading operations including `order_send`, so importing it into the Phase 8 shadow runtime would weaken the structural no-order boundary.

Allowed use in FMP:
- deferred candidate for a separately designed later demo/execution phase only;
- direct Python `MetaTrader5` integration remains explicitly rejected for Phase 8 under DEC-037.

Important architectural consequence:
- FMP core remains broker-independent; the MT5 terminal is only a local quote-source edge in Phase 8 and is not the research brain.

## Source policy

- Prefer official documentation for adapter contracts.
- Record verification date when a source affects implementation.
- If a service/API changes, do not silently patch around it; record the decision and update this register.
- No external source can override FMP risk/promotion rules.

## SRC-005 — MQL5 read-only MT5 file bridge

- Status: SELECTED for amended Phase 8 quote-source role under DEC-037
- Reviewed: 2026-09-17
- Provider identity: `FP_MARKETS_MT5_DEMO`
- Allowed demo servers: `FPMarketsSC-Demo`, `FPMarketsSC-Demo2`
- Fixed transport: `MT5_FILE_COMMON_JSONL` at logical `FMP/phase8-usdjpy-feed.jsonl`
- Official references: MQL5 `OnTick`, `MqlTick`, `FileOpen`, `FileFlush`, and `CryptEncode` documentation.
- Outcome: use a purpose-built MQL5 EA only to validate demo/server/symbol identity, read USDJPY Bid/Ask ticks, emit local bridge liveness, compute an account SHA-256 fingerprint, and write the fixed `FILE_COMMON` transport. The EA and FMP Python runtime contain no order/trade/position mutation path. Direct Python `MetaTrader5` integration remains rejected for Phase 8 because its API exposes execution functions.
- Safety: AutoTrading remains OFF; live server names, generic provider fallback, demo/live orders, broker mutation, and real-money trading remain locked.
