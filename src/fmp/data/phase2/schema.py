from __future__ import annotations

CANONICAL_SCHEMA_VERSION = "fmp-canonical-1m-v1"
DERIVED_SCHEMA_VERSION = "fmp-derived-bars-v1"
INGESTION_VERSION = "dukascopy-bi5-candles-v1"

PRICE_DIVISORS = {
    "EURUSD": 100_000,
    "GBPUSD": 100_000,
    "USDJPY": 1_000,
}

DECODED_SIDE_COLUMNS = (
    "timestamp_utc",
    "symbol",
    "side",
    "open",
    "high",
    "low",
    "close",
    "volume",
)
