# Phase 1 Golden Sample Evidence

**Date:** 2026-08-22  
**Phase:** 1 — Historical Data Acquisition  
**Status:** PASS

## Purpose

Verify the frozen Dukascopy daily M1 BID/ASK adapter across every V1 pair before any full-history acquisition is trusted.

Golden sample date: **2024-01-02 UTC**.

Required matrix:

- EUR/USD BID
- EUR/USD ASK
- GBP/USD BID
- GBP/USD ASK
- USD/JPY BID
- USD/JPY ASK

Every successful source response had to pass FMP structural checks, be written atomically, receive a provenance manifest, and have its raw-file SHA-256 independently recomputed by GitHub Actions.

## First all-pair run — useful transient failure

GitHub Actions run `32541310014`, first job `96951733094`.

The run acquired and verified:

- EUR/USD BID — 1,440 records
- EUR/USD ASK — 1,440 records
- GBP/USD BID — 1,440 records
- GBP/USD ASK — 1,440 records

The next request, USD/JPY BID, received HTTP `503` on all three configured attempts. The request failed before payload parsing, so this was not evidence of a USD/JPY schema/path/parser problem.

## Unchanged reproduction

The exact failed job was rerun without changing acquisition code or source paths.

Rerun job: `96952048749`.

Result: **PASS**. All six pair/side chunks downloaded and independently verified.

This isolated the first failure to transient source/network availability rather than pair-specific acquisition logic.

## Hardening derived from the failure

The acquisition default was changed from 3 attempts / 0.5-second base exponential backoff to:

- 6 attempts
- 1.0-second base exponential backoff

A deterministic unit test proves the default retry budget survives three consecutive HTTP 503 responses and completes when the fourth response succeeds.

No concurrency was added. Phase 1 continues to prefer provider-friendly, resumable sequential acquisition over aggressive download speed.

## Final hardened golden run

GitHub Actions run `32541626104`, job `96952617097`.

Result: **PASS**.

| Pair | Side | Records | Compressed bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| EURUSD | BID | 1,440 | 11,714 | `9b2d2b718f9ca123b58dce4b4512d4e1bd35c692e23e1beafebdd700072cf546` |
| EURUSD | ASK | 1,440 | 12,015 | `a7dd327f5c59ad016c0e7e480d33fd7abd38da3e9c51dfe614f5e95f677386b3` |
| GBPUSD | BID | 1,440 | 11,547 | `bafd4aeb465e828f2f28de3e170d64f82e63e98cb79153522de9170e0b67db3b` |
| GBPUSD | ASK | 1,440 | 11,501 | `e92d44caaf7ccccb3a97a789a6d0c9f550ca8402acbfc638ad33200e2ff56254` |
| USDJPY | BID | 1,440 | 12,522 | `c090db5407da5b5733b2bba5fbd52b39d8ea5afdd43dd2f4741f8acbbca86915` |
| USDJPY | ASK | 1,440 | 12,514 | `f08b20f1fe78ae48bdb99f2080d93432f6ee5ab8b3b3063c3f8f62dfdc504242` |

Coverage assertions:

- 6 planned golden chunks
- 6 complete manifests
- 0 `not_found`
- 0 other statuses
- both BID and ASK present for all three pairs
- all six raw-file SHA-256 values match their manifests

## Conclusion

The Phase 1 source adapter and retry semantics are validated across all V1 pairs for the bounded golden sample.

This does **not** complete Phase 1. The remaining gate is acquisition and provenance verification of the full target historical snapshot. Data-quality judgments remain Phase 2 work.
