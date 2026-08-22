# Phase 1 Dukascopy Acquisition Spike

**Date:** 2026-08-22  
**Phase:** 1 — Historical Data Acquisition  
**Status:** CODE_READY_FOR_BOUNDED_NETWORK_SMOKE

## Question

Can FMP acquire source-faithful, free, daily 1-minute BID and ASK forex history for EUR/USD, GBP/USD, and USD/JPY without an API key or paid service, while preserving immutable raw files and reproducible provenance?

## Evidence

Dukascopy's official Historical Data Export states that historical data is available and includes bid prices, ask prices, and trading volumes:

- https://www.dukascopy.com/api/data/get/historical-data-export

Dukascopy's own support material shows its historical file service using paths such as:

- `https://www.dukascopy.com/datafeed/EURUSD/.../BID_candles_min_1.bi5`
- `https://www.dukascopy.com/datafeed/USDCHF/.../ASK_candles_min_1.bi5`

Relevant Dukascopy support page:

- https://www.dukascopy.com/swiss/english/forex/jforex/forum/viewtopic.php?p=64144

Current open-source clients independently use the active host `https://datafeed.dukascopy.com/datafeed` and the daily M1 naming scheme with zero-based month folders. These are corroborating implementation references, not the authority for FMP's market claims:

- https://github.com/knusul/dukascopy-tools
- https://github.com/Nosvemos/dukascopy-go

## Retrieval method under test

For each UTC calendar date and each side independently:

```text
https://datafeed.dukascopy.com/datafeed/{PAIR}/{YYYY}/{MM_ZERO_BASED}/{DD}/{SIDE}_candles_min_1.bi5
```

Where:

- `PAIR` is one of `EURUSD`, `GBPUSD`, `USDJPY`
- `SIDE` is `BID` or `ASK`
- month is zero-based in the source path (`00` = January)
- each successful body is kept byte-for-byte as immutable source data

## Structural assumptions checked by FMP

FMP does not normalize prices in Phase 1. It only performs enough structural inspection to reject an obviously partial/corrupt source response:

- HTTP 2xx body must be non-empty
- body must decompress as LZMA
- decompressed length must be a non-zero multiple of 24 bytes
- a daily chunk may not contain more than 1,440 records
- the first 4 bytes of each record are treated only as the candle's second offset for structural checking; offsets must be strictly increasing and remain inside one UTC day

Full price-field decoding and quote sanity are Phase 2 responsibilities.

## Missing-source semantics

HTTP 404 is recorded as a `not_found` acquisition manifest, not silently discarded and not automatically classified as a market-data defect. Phase 2 will distinguish expected market closures from suspicious gaps.

A prior `not_found` manifest is resumable by default without another network request, but the operator can explicitly re-check it with `--recheck-not-found`. This matters for recently published history because a missing file can be temporary.

## Reproducibility

Every attempted chunk receives a deterministic path. Successful chunks receive:

- immutable `.bi5` file
- SHA-256 checksum
- source URL
- pair/side/date/granularity
- source-format version
- compressed byte size
- structurally observed record count
- retrieval timestamp
- HTTP status

Existing successful chunks are never overwritten. Resume first verifies the recorded checksum. An inconsistent raw/manifest pair fails closed.

## Limits / usage behavior

FMP does not assume an undocumented request-rate entitlement. The Phase 1 CLI is intentionally sequential in its first implementation, uses bounded retries, and is resumable. This favors provider friendliness and correctness over download speed.

Historical market data is not committed to Git. The repository contains acquisition code and manifests/schema rules only.

## Freeze condition

The method becomes the Phase 1 frozen source adapter only after a real bounded network smoke test downloads BID and ASK daily M1 chunks and verifies the generated manifests/checksums in a clean environment.
