# FMP Project State

**Updated:** 2026-08-22  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 1 — Historical Data Acquisition  
**Phase status:** FULL_HISTORY_CLOUD_ACQUISITION_IN_PROGRESS  
**Next phase:** Phase 2 — Validation, Normalization & Derived Bars (LOCKED until Phase 1 PASS)

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Frozen first snapshot target: 2015-01-01 through 2026-08-20 inclusive
- Development budget: $0
- Historical source: Dukascopy daily M1 BID/ASK `.bi5`, frozen by DEC-009
- Phase 1 persistent cloud copy: dedicated Supabase `FMP` project, private `fmp-raw` bucket, frozen by DEC-010
- Phase 2+ research storage: Parquet + DuckDB outside the Phase 1 raw bucket
- Language: Python
- ML: optional, only after baselines
- Execution choice: deferred until demo/shadow needs justify it
- Real-money trading: locked

## Phase 0 — PASS

**Merge commit:** `31cd8decca5dcb90f9d123ff33f71ac20413e269`  
**Checkpoint ref:** `fmp-v1-phase0-source-of-truth`

All Phase 0 source-of-truth, architecture, data, research, risk, build-order, experiment-log and continuation-rule gates are complete.

## Phase 1 — completed gates

### Source/acquisition
- [x] deterministic Dukascopy daily M1 BID/ASK source adapter
- [x] resumable acquisition
- [x] atomic raw/manifest writes
- [x] SHA-256 provenance
- [x] fail-closed tamper handling
- [x] structural LZMA/record validation
- [x] explicit 404 `not_found` provenance
- [x] delayed-404 recheck path
- [x] hardened transient 5xx retry policy
- [x] acquisition coverage report
- [x] snapshot provenance verifier
- [x] bounded live-network smoke PASS
- [x] all-pair golden sample PASS
- [x] retrieval method frozen as DEC-009

### Persistent cloud snapshot
- [x] dedicated Supabase `FMP` project created at verified `$0/month`
- [x] private `fmp-raw` bucket created
- [x] GitHub OIDC trust boundary implemented/tested
- [x] Supabase `fmp-raw-ingest` Edge Function deployed
- [x] canonical V1 object-path validation
- [x] SHA-256 required before storage
- [x] Python GitHub-OIDC mirror client
- [x] immediate per-result cloud mirroring
- [x] 36-shard pair/year GitHub acquisition workflow
- [x] main-branch end-to-end cloud smoke PASS
- [x] four expected smoke objects independently observed
- [x] `[phase1-full]` full-history trigger issued
- [x] full acquisition observed writing objects to the private bucket
- [x] retry-manifest idempotency defect discovered, regression-tested, fixed and live-verified

## Full-history acquisition — ACTIVE

Trigger commit:

- `496ef145daf694902d09d17e5f969cc62a93fefd` — `chore: start Phase 1 full acquisition [phase1-full]`

Workflow shape:

- 3 pairs × 12 year shards = 36 jobs
- years 2015–2025 use full calendar years
- 2026 shard ends at exclusive `2026-08-21`
- maximum 3 concurrent jobs
- every acquisition result is mirrored immediately to Supabase
- each shard runs local provenance verification
- market data is not stored as a GitHub artifact

Latest independently observed Supabase progress during this update:

- total objects: **94**
- raw objects: **47**
- manifest objects: **47**
- persisted bytes: **389,188**
- latest observed object timestamp: `2026-08-22 01:44:33.57992+00`

These numbers prove active persistence only. They are **not** Phase 1 completion evidence.

## Manifest retry incident — FIXED

A duplicate main-branch smoke discovered that raw `.bi5` retry semantics were correct but manifests were not byte-idempotent because `retrieved_at_utc` changes on every fresh acquisition attempt.

Observed v2 behavior:

- duplicate raw object: HTTP 200 `already_verified`
- semantically identical regenerated manifest: HTTP 409 conflict

Root cause: acquisition manifests intentionally record attempt-specific `retrieved_at_utc`, so identical source/provenance can produce different manifest bytes.

Approved fix:

- raw `.bi5` objects remain strictly byte-for-byte immutable;
- duplicate manifest bytes are accepted directly when SHA-256 matches;
- when manifest bytes differ, semantic comparison ignores **only** top-level `retrieved_at_utc`;
- every other field must match, including source URL, pair, side, date, status, raw SHA-256, record count, source format and any additional field;
- the first cloud manifest remains stored; retry attempts never overwrite it;
- substantive differences still return HTTP 409.

TDD evidence:

- regression tests were first observed red because `manifestsEquivalent` did not exist;
- Python tests remained green;
- implementation then made Edge tests + type-check green;
- fix was deployed as `fmp-raw-ingest` **version 3**;
- live duplicate requests on v3 returned multiple HTTP 200 idempotent responses with no new v3 409 observed;
- current-main replay CI passed Python + Edge suites;
- merged via PR #5 at commit `a2906a37f380dc6c4d27e90d46f15c2c2731d417`.

PR #4 was closed unmerged because `main` advanced during the live run; PR #5 replayed the identical tested fix onto current `main`.

## Remaining Phase 1 gates

- [ ] all pair/year acquisition shards accounted for
- [ ] full target cloud snapshot independently audited
- [ ] expected source-404/market-closure manifests accounted for
- [ ] no unexplained missing planned chunks
- [ ] final cloud provenance/coverage evidence recorded
- [ ] Phase 1 acceptance gate recorded PASS
- [ ] Phase 1 checkpoint recorded

## Immediate next action

Continue evidence collection on the already-triggered full acquisition. Do **not** begin Phase 2 merely because objects are arriving. After acquisition stops changing, independently audit the private bucket against the full planned 2015-01-01 → 2026-08-21-exclusive pair/side/date plan. If any shard or date is missing, rerun safely using the v3 idempotent cloud layer. Only a complete accounted-for snapshot may unlock Phase 2.

## Known open decisions

1. Exact chronological train/validation/final-test boundaries — Phase 2 data-quality dependent.
2. Exact intrabar ambiguity policy implementation details — Phase 3.
3. Exact demo broker/adapter — Phase 8/9.
4. Exact live capital/risk — outside current scope until Phase 10 review + Phase 11 approval.

## Backlog — do not pull forward

- economic-calendar/event-risk filter
- tick-level execution validation
- dashboard
- advanced multi-pair correlation controls
- alternative data
- broader cloud hosting beyond Phase 1 raw persistence
- live-money execution
- indices/crypto/gold/commodities
