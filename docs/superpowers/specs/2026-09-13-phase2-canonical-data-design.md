# Phase 2 Canonical Data Design

**Date:** 2026-09-13  
**Status:** APPROVED DESIGN — IMPLEMENTATION ACTIVE  
**Branch:** `phase2-canonical-data-foundation`

## Purpose

Phase 2 converts the accepted immutable Dukascopy Phase 1 snapshot into trustworthy canonical 1-minute bid/ask data, quantified quality reports, and deterministic 5m/15m/1h derived bars. Phase 2 must never rewrite Phase 1 raw objects and must never silently repair questionable observations.

The design follows `docs/master-spec.md`, `docs/build-order.md`, `docs/data-spec.md`, and DEC-014 in `docs/decision-log.md`.

## Scope

Phase 2 includes:

1. frozen canonical schema/version identity;
2. Dukascopy daily M1 BI5 decoding;
3. BID/ASK normalization into one canonical 1-minute row model;
4. structural, quote-sanity, and time-continuity validation;
5. deterministic gap classification where evidence is sufficient;
6. pair-level quality reports;
7. deterministic 5m/15m/1h resampling;
8. processed Parquet artifacts plus manifests/checksums;
9. a reproducible path from the accepted private `fmp-raw` snapshot to the Phase 2 processor.

Phase 2 does not add trading logic, features, strategy research, ML, backtesting, live data, or real-money execution.

## Technology

- Python >= 3.11.
- Standard library for BI5/LZMA decoding and hashing.
- `polars==1.44.2` for typed tabular transforms, Parquet output, joins, and resampling.
- `zoneinfo` for DST-aware market-week utilities.
- Parquet for processed datasets.
- JSON for quality summaries and processed manifests.

Polars is the first runtime data-processing dependency added by Phase 2. Phase 2 pins stable Polars 1.44.2 and does not adopt the Polars 2.0 release candidate while the data contract is being frozen.

## Raw input boundary

The accepted source of truth remains the immutable Phase 1 cloud snapshot in Supabase bucket `fmp-raw`.

Phase 2 processing consumes bytes through a `RawChunkReader` protocol so decoding and validation are independent of storage location.

Two implementations are required:

- `LocalRawChunkReader`: reads an already-materialized Phase 1-compatible local `data/raw` tree for unit/integration tests and bounded development;
- `CloudRawChunkReader`: obtains accepted raw objects from the private `fmp-raw` bucket through a dedicated read-only GitHub-OIDC-authenticated endpoint. GitHub must not receive a Supabase service-role key.

The cloud reader must verify returned object path, SHA-256, and byte size against the Phase 1 manifest before decoding. A mismatch is fatal. The existing `fmp-raw-audit` protocol stays read-only metadata/provenance verification and is not overloaded with bulk-byte export semantics.

A separate `fmp-raw-read` Edge Function is preferred for full-history materialization. It accepts only canonical frozen V1 raw paths, authenticates GitHub OIDC using the same repository/workflow trust boundary, and returns one immutable raw object with explicit SHA-256 and size headers. It cannot write Storage.

## Dukascopy BI5 decoder contract

Phase 1 already proves that a successful daily M1 candle payload:

- is LZMA-compressed;
- decompresses to a non-zero multiple of 24 bytes;
- contains at most 1,440 records;
- has strictly increasing second offsets within the UTC day;
- has no second offset >= 86,400.

Phase 2 decodes each 24-byte record as big-endian `>IIIIIf`:

1. seconds since UTC midnight;
2. open price integer;
3. close price integer;
4. low price integer;
5. high price integer;
6. volume/activity float32.

Price divisors are frozen for V1:

- `EURUSD`: 100,000;
- `GBPUSD`: 100,000;
- `USDJPY`: 1,000.

A decoded timestamp is `date_utc 00:00:00+00:00 + seconds`, and labels the start of the one-minute interval.

The decoder fails closed on invalid LZMA, non-24-byte alignment, duplicate/non-increasing offsets, out-of-day offsets, or unsupported symbols. Quote-value anomalies such as zero/non-finite prices or volume are preserved in decoded rows so the quality layer can report them rather than hiding source evidence.

Before this field-order/divisor contract is used on full history, a bounded golden fixture from the accepted Phase 1 snapshot must be decoded and independently checked for plausible OHLC ordering and price scale. If that fixture contradicts the contract, implementation stops and this design is amended rather than compensating silently.

## Canonical 1-minute schema v1

Schema identity: `fmp-canonical-1m-v1`.

Required columns, in stable order:

- `timestamp_utc`: timezone-aware UTC datetime, bar-start label;
- `symbol`: `EURUSD`, `GBPUSD`, or `USDJPY`;
- `bid_open`: float64 nullable;
- `bid_high`: float64 nullable;
- `bid_low`: float64 nullable;
- `bid_close`: float64 nullable;
- `ask_open`: float64 nullable;
- `ask_high`: float64 nullable;
- `ask_low`: float64 nullable;
- `ask_close`: float64 nullable;
- `bid_volume`: float64 nullable;
- `ask_volume`: float64 nullable;
- `source`: constant `dukascopy`;
- `ingestion_version`: constant `dukascopy-bi5-candles-v1`;
- `schema_version`: constant `fmp-canonical-1m-v1`.

BID and ASK daily records are decoded independently, then full-outer-joined by `symbol + timestamp_utc`.

A one-sided timestamp is preserved with nulls for the missing side. It is not dropped, forward-filled, midpoint-filled, or synthesized. Its presence is reported by the quality layer.

Rows are sorted by `symbol, timestamp_utc`. Duplicate timestamps within a side are a decoder/normalization error, not something to deduplicate automatically.

## Quality findings model

Quality findings are separate from canonical quote columns so questionable data remains source-faithful.

Each finding contains:

- `symbol`;
- `timestamp_start_utc`;
- optional `timestamp_end_utc`;
- `code`;
- `severity` (`info`, `warning`, `error`);
- deterministic structured details.

Required finding codes include:

- `missing_bid_side`;
- `missing_ask_side`;
- `bid_ohlc_invalid`;
- `ask_ohlc_invalid`;
- `ask_below_bid`;
- `non_positive_price`;
- `non_finite_value`;
- `duplicate_timestamp`;
- `missing_open_market_minute`;
- `weekend_closure_gap`;
- `long_weekday_gap`;
- `spread_outlier`;
- `price_jump_outlier`.

Validators report observations; they do not mutate quote values.

## Quote-sanity rules

For each populated side:

- `low <= open <= high`;
- `low <= close <= high`;
- all OHLC values are finite and positive;
- volume/activity is finite and non-negative.

When both sides exist, ask must not be below bid for the corresponding open, high, low, or close comparison. Such cases are findings, not auto-corrections.

Spread outliers are computed from valid both-sided close spreads in pips for each symbol. Let `Q1` and `Q3` be the 25th and 75th percentiles and `IQR = Q3 - Q1`; a valid close spread is a `spread_outlier` when it is greater than `Q3 + 10 * IQR`. The report records the calculated threshold.

Price-jump outliers use absolute one-minute midpoint close returns only where consecutive canonical timestamps differ by exactly 60 seconds and both sides are populated. Using the same `Q1/Q3/IQR` rule, a return is a `price_jump_outlier` when it is greater than `Q3 + 10 * IQR`. This deliberately avoids treating weekend reopening jumps as one-minute returns. The report records the calculated threshold.

If `IQR == 0`, the threshold is `Q3`; only values strictly greater than that threshold are flagged.

Outlier status is descriptive and never deletes or alters a row.

## Time continuity and market-week rules

All continuity checks operate in UTC while market-week classification uses `America/New_York` through `zoneinfo` so DST transitions are not hard-coded.

The baseline forex market-week model is:

- opens Sunday 17:00 New York time;
- closes Friday 17:00 New York time.

Missing minutes wholly outside that interval are classified as `weekend_closure_gap`.

Missing minutes inside that interval are suspicious and reported as `missing_open_market_minute`. A contiguous suspicious open-market gap of **30 minutes or more** is additionally summarized as `long_weekday_gap`.

Phase 2 does not fabricate a comprehensive holiday calendar. Likely holiday closures remain visible in the suspicious-gap report unless later source-backed rules are added through change control.

## Quality reports

A deterministic per-symbol quality report must include at least:

- actual start/end timestamps;
- canonical row count;
- one-sided row counts;
- duplicate count;
- required-null count;
- OHLC-invalid counts by side;
- ask-below-bid count;
- non-positive/non-finite counts;
- missing open-market minute count;
- weekend-closure gap count/duration;
- suspicious gap spans and maximum duration;
- spread distribution summary, calculated threshold, and outlier count;
- one-minute midpoint-return distribution summary, calculated threshold, and outlier count;
- schema version and ingestion version.

The report is evidence for Phase 2 acceptance, not a data-cleaning instruction.

## Resampling contract

Derived intervals are exactly `5m`, `15m`, and `1h`.

Intervals are UTC, closed-left/open-right `[T, T + interval)`, and labeled at `T`.

For each quote side independently:

- open = first valid open in the interval;
- high = maximum valid high;
- low = minimum valid low;
- close = last valid close;
- volume = sum of valid source activity values.

Derived rows also carry:

- `source_minutes`: count of distinct canonical 1-minute timestamps contributing to the interval;
- `is_complete`: true only when all expected open-market source minutes for the interval are present and both sides are populated for every contributing minute;
- `timeframe`: `5m`, `15m`, or `1h`;
- `schema_version`: `fmp-derived-bars-v1`.

Incomplete intervals remain present and are explicitly marked; they are never silently filled.

Exact-boundary tests must cover 00:00 UTC, interval transitions, Friday close, Sunday open, and DST transition weekends.

## Processed artifact layout

Processed files are not committed to Git.

Deterministic layout:

```text
data/processed/fmp-canonical-1m-v1/1m/{SYMBOL}/{YYYY}/{MM}.parquet
data/processed/fmp-canonical-1m-v1/5m/{SYMBOL}/{YYYY}/{MM}.parquet
data/processed/fmp-canonical-1m-v1/15m/{SYMBOL}/{YYYY}/{MM}.parquet
data/processed/fmp-canonical-1m-v1/1h/{SYMBOL}/{YYYY}/{MM}.parquet
data/processed/fmp-canonical-1m-v1/quality/{SYMBOL}.json
data/manifests/processed/fmp-canonical-1m-v1/{SYMBOL}.json
```

Monthly partitioning keeps regeneration bounded while preserving deterministic ordering.

Parquet writes use the pinned Polars version, Zstandard compression at level 3, statistics enabled, and stable column order. The processed manifest records the Polars version and Parquet write configuration so byte checksums are tied to the generating environment.

## Processed manifests

Each symbol manifest records:

- manifest version;
- schema version;
- ingestion version;
- source snapshot identity (`fmp-v1-phase1-source-of-truth` plus Phase 1 frozen plan SHA-256);
- symbol;
- actual canonical start/end;
- partition paths;
- row counts by timeframe;
- SHA-256 and byte size for every Parquet/quality artifact;
- quality summary counts;
- `polars_version` and Parquet write configuration;
- generation timestamp UTC;
- generating code commit when available.

Manifest generation is deterministic except for the explicit generation timestamp and commit identity. Checksums cover exact written bytes.

## CLI design

The existing `fmp-data` entry point remains the single data CLI. Phase 1 commands remain unchanged.

Phase 2 adds commands behind focused helper modules rather than expanding `cli.py` with transformation logic:

- `fmp-data decode-day` — bounded decoder/golden-fixture inspection;
- `fmp-data normalize` — materialize canonical 1m for a pair/date range;
- `fmp-data quality` — emit deterministic quality report;
- `fmp-data resample` — create 5m/15m/1h outputs from canonical 1m;
- `fmp-data process-phase2` — orchestrate normalize → quality → resample → manifest for selected pairs/date range.

The orchestration command fails non-zero on structural/schema/manifest integrity errors. Data-quality findings are reported and persisted; they do not automatically make the command fail unless the finding means canonical representation itself is impossible.

## Error handling

Fail immediately on:

- raw SHA/size mismatch against Phase 1 manifest;
- unsupported path/symbol/schema identity;
- invalid BI5/LZMA structure;
- duplicate side timestamp;
- non-deterministic or conflicting output partition;
- output checksum verification failure;
- malformed processed manifest.

Report but preserve on:

- one-sided quotes;
- non-positive/non-finite quote values;
- ask-below-bid observations;
- suspicious gaps;
- extreme spread/jump observations;
- likely holiday/weekday closures not covered by the deterministic weekend rule.

## Test strategy

TDD is mandatory. Required test layers:

1. BI5 decoder fixtures for EURUSD and USDJPY scaling, field order, timestamp offsets, invalid compression, invalid length, invalid offsets, and preservation of anomalous numeric values;
2. golden accepted Phase 1 raw-chunk decoder integration before full-history processing;
3. normalization tests for BID/ASK joins, one-sided rows, stable ordering, and duplicate rejection;
4. quality tests for OHLC sanity, ask-below-bid, non-positive/non-finite values, weekend gaps, weekday gaps, 30-minute long-gap classification, spread outliers, and price-jump outliers;
5. timezone/DST tests around New York spring/fall transitions;
6. exact resampling examples for 5m/15m/1h boundaries and incomplete windows;
7. Parquet round-trip/schema tests with the pinned writer configuration;
8. processed-manifest checksum/determinism tests;
9. CLI integration tests over a bounded local fixture;
10. full Python suite and workflow-YAML validation before merge.

No full-history processing is authorized until the bounded golden decoder and canonical round-trip tests are green.

## Implementation sequence

Implementation is staged so each milestone is independently reviewable:

1. canonical schema + BI5 decoder + golden fixture validation;
2. normalization + quality findings + market-week/DST utilities;
3. resampling + Parquet partitions + processed manifests;
4. authenticated cloud raw reader + full-history orchestration;
5. exhaustive Phase 2 processing, reports, acceptance evidence, and checkpoint `fmp-v1-phase2-normalized-data`.

Phase 2 is not PASS merely because code exists. PASS requires all three pairs to be processed, quality/anomaly counts quantified, 5m/15m/1h outputs deterministic, manifests reproducible, and the required tests green.
