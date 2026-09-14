# Phase 2 Acceptance Evidence

**Review date:** 2026-09-14  
**Materializer commit:** `158c1c121655867b7fb2886fe755585dfcd682ec`  
**Frozen source checkpoint:** `fmp-v1-phase1-source-of-truth`  
**Frozen plan SHA-256:** `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`

## Exhaustive workflow

`phase2-full-history` run `34782357048` on `main` completed successfully on attempt 2. EURUSD and GBPUSD succeeded on the initial attempt. USDJPY initially received one HTTP 401 from the read-only raw Edge Function; rerunning only that job without code, data, source, or configuration changes succeeded, so the 401 did not reproduce.

Each pair covers 2015-01-01 through 2026-08-20 inclusive: 4,250 days, exactly 8,500 verified raw reads (4,250 BID + 4,250 ASK), and 140 calendar months.

Every pair produced exactly 6,120,000 1m rows, 1,224,000 5m rows, 408,000 15m rows, and 102,000 1h rows, with 140 monthly Parquet partitions per timeframe and 561 artifacts in its processed manifest.

## Persisted artifacts

| Pair | Artifact ID | ZIP bytes | ZIP SHA-256 |
| --- | ---: | ---: | --- |
| EURUSD | 10325737935 | 182037581 | `db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3` |
| GBPUSD | 10326096831 | 190706384 | `fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2` |
| USDJPY | 10327600628 | 160033414 | `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72` |

Downloaded ZIPs were independently verified. For every pair: ZIP digest matched GitHub; every manifest-listed artifact matched byte size and SHA-256; the raw ledger contained exactly the frozen 8,500 date/side identities with no duplicates or omissions; and all 140 months existed for each of 1m/5m/15m/1h. Independent verification found zero validation errors.

## Quality review

All three reports cover `2015-01-01T00:00:00Z` through `2026-08-20T23:59:00Z` and report zero duplicates, zero missing BID rows, zero missing ASK rows, zero required nulls, zero missing open-market minutes, and zero suspicious gaps.

Finding telemetry is preserved without mutation: EURUSD has 6,621 price-jump and 53 spread-outlier findings; GBPUSD has 7,422 price-jump findings; USDJPY has 7,158 price-jump and 127 spread-outlier findings.

## Acceptance

The exhaustive evidence satisfies the Phase 2 exit gates in `docs/build-order.md` and `docs/data-spec.md`: canonical normalized histories exist for all three pairs, quality anomalies/gaps are quantified rather than hidden, deterministic 5m/15m/1h bars and versioned processed manifests exist, and the required canonical/resampling/weekend/DST test suite passed on the merged implementation.

**Acceptance review: PASS.**

Checkpoint `fmp-v1-phase2-normalized-data` remains the administrative closure action if project checkpoints are represented by Git tags/refs. Phase 3 has not started.
