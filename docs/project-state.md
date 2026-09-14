# FMP Project State

**Updated:** 2026-09-14  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 2 — Validation, Normalization & Derived Bars  
**Phase status:** ACCEPTANCE_REVIEW_PASS_CHECKPOINT_PENDING  
**Next milestone:** create checkpoint `fmp-v1-phase2-normalized-data`, record formal Phase 2 PASS, and keep Phase 3 unstarted until the next approved implementation slice

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Frozen Phase 1 snapshot: 2015-01-01 through 2026-08-20 inclusive
- Frozen raw identities: 25,500
- Historical source: Dukascopy daily M1 BID/ASK `.bi5`
- Persistent immutable raw snapshot: Supabase private bucket `fmp-raw`
- Frozen plan SHA-256: `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`
- Real-money trading: locked

## Phase 0 — PASS

- Merge commit: `31cd8decca5dcb90f9d123ff33f71ac20413e269`
- Checkpoint: `fmp-v1-phase0-source-of-truth`

## Phase 1 — PASS

Phase 1 is closed for the frozen three-pair snapshot. Final acceptance established 25,500 expected and present raw-backed manifests, zero missing identities, zero inferred `not_found`, zero unexpected raw/manifest paths, and zero checksum/size mismatches.

- final provenance workflow: `phase1-final-cloud-audit`
- run ID: `34758527971`
- head SHA: `0ff45220cd930839059afcfba631e1e120cb38aa`
- result: SUCCESS
- artifact ID: `10318323714`
- artifact SHA-256: `53dbc184677393642e07c78fb6f2229a2c9bf5d8a38c2169935c23297003244b`
- cross-report acceptance: 55 checks passed, 0 failed
- checkpoint/source identity: `fmp-v1-phase1-source-of-truth`

Phase 1 acceptance proves acquisition completeness and immutable provenance only. No further acquisition is required unless later evidence demonstrates an integrity defect.

## Phase 2 — ACCEPTANCE REVIEW PASS

The canonical-data foundation and exhaustive authenticated cloud-read materialization are complete. The detailed acceptance record is `docs/phase2-acceptance-evidence.md`.

### Exhaustive workflow

- workflow: `phase2-full-history`
- run number: #1
- run ID: `34782357048`
- final attempt: 2
- head SHA: `158c1c121655867b7fb2886fe755585dfcd682ec`
- final conclusion: SUCCESS
- completion: `2026-09-13T23:10:00Z`

Attempt 1 completed EURUSD and GBPUSD but USDJPY received one HTTP 401 from the read-only raw Edge Function. The isolated USDJPY rerun succeeded without code, data, source, or configuration changes; the 401 did not reproduce.

### Frozen scope proved

For each of EURUSD, GBPUSD, and USDJPY:

- 4,250 days and exactly 8,500 verified raw reads (4,250 BID + 4,250 ASK)
- 140 calendar months
- 140 monthly partitions for each of 1m, 5m, 15m, and 1h
- row counts: 1m 6,120,000; 5m 1,224,000; 15m 408,000; 1h 102,000
- 561 processed-manifest artifacts
- exact raw ledger with zero missing or duplicate frozen identities

### Artifact digests

- EURUSD artifact `10325737935`: `db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3`
- GBPUSD artifact `10326096831`: `fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2`
- USDJPY artifact `10327600628`: `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`

Independent inspection verified every ZIP digest, every manifest-listed file size/SHA, every ledger identity, and every monthly partition set with zero validation errors.

### Quality acceptance

For all three pair histories:

- actual range: `2015-01-01T00:00:00Z` through `2026-08-20T23:59:00Z`
- duplicate rows: 0
- missing BID rows: 0
- missing ASK rows: 0
- required null count: 0
- missing open-market minutes: 0
- maximum suspicious gap minutes: 0

Outlier findings remain recorded as telemetry and were not silently removed or rewritten.

The Phase 2 acceptance review against `docs/data-spec.md` and `docs/build-order.md` is PASS. Canonical/schema, quote-sanity, duplicate/missing-timestamp, deterministic resampling boundary, weekend-gap, DST-sensitive utility, ledger, workflow-guard, and real Parquet materialization tests were green on the merged implementation and post-merge main CI.

## Remaining Phase 2 closure action

Create checkpoint `fmp-v1-phase2-normalized-data` if checkpoints are represented by Git tags/refs. After that administrative checkpoint exists, record formal Phase 2 status as PASS.

Phase 3 — Backtesting Engine — has **not started**.
