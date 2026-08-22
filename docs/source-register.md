# FMP External Source Register

**Last verified:** 2026-08-22

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

## SRC-003 — OANDA v20 Development Guide

Official page: https://developer.oanda.com/rest-live-v20/development-guide/

Verified foundation on 2026-08-22:
- separate `fxTrade Practice` REST environment exists;
- separate practice streaming environment exists;
- the guide describes practice as a stable environment recommended for testing;
- production and practice use different base URLs;
- real-time pricing and order endpoints are documented.

Allowed use in FMP:
- candidate shadow/demo execution adapter in Phases 8–9.

Does **not** guarantee:
- account eligibility in every jurisdiction;
- perpetual free access;
- that OANDA will be the final chosen demo broker.

Reverify in Phase 8/9.

## SRC-004 — MetaTrader 5 Python Integration

Official page: https://www.mql5.com/en/docs/python_metatrader5

Verified foundation:
- official Python integration exists;
- functions include quote/rate/tick retrieval, account/order/position access, order checking, and order sending.

Allowed use in FMP:
- candidate later broker/execution adapter, especially for demo/live environments exposing MT5.

Important architectural consequence:
- FMP core remains broker-independent; MT5 is not the research brain.

## Source policy

- Prefer official documentation for adapter contracts.
- Record verification date when a source affects implementation.
- If a service/API changes, do not silently patch around it; record the decision and update this register.
- No external source can override FMP risk/promotion rules.
