# Phase 2 Full-History Materialization Design

**Status:** Approved continuation of the active Phase 2 roadmap  
**Date:** 2026-09-13  
**Phase:** Phase 2 — Validation, Normalization & Derived Bars  
**Source snapshot:** frozen Phase 1 snapshot, 2015-01-01 through 2026-08-20 inclusive  
**Repository:** `Dtwosam/FMP`

## Purpose

The authenticated cloud raw-reader foundation and bounded real-cloud golden proof are complete. The next approved Phase 2 milestone is exhaustive processing of the frozen Phase 1 snapshot for EURUSD, GBPUSD, and USDJPY into reproducible canonical 1-minute data, deterministic 5m/15m/1h bars, pair-level quality evidence, and processed manifests.

This slice does not mark Phase 2 PASS by itself. It creates the source-free full-history materialization path and evidence needed for the Phase 2 acceptance review. It does not start Phase 3.

## Frozen scope

The full-history plan is fixed in code:

- pairs: `EURUSD`, `GBPUSD`, `USDJPY`;
- start: `2015-01-01` inclusive;
- end: `2026-08-20` inclusive (`2026-08-21` exclusive in iteration);
- expected days per pair: 4,250;
- expected raw reads per pair: 8,500 (`BID` and `ASK` for every day);
- canonical timeframe: 1m;
- derived timeframes: 5m, 15m, 1h;
- raw protocol: `fmp-raw-read-v1`;
- source bucket remains `fmp-raw` and read-only.

The workflow exposes no date-range input and no source/acquisition mode. Expanding the frozen snapshot requires a separate source-of-truth change.

## Security boundary

`fmp-raw-read` keeps custom GitHub OIDC authentication with audience `fmp-supabase-raw-read` and exact checks for:

- repository `Dtwosam/FMP`;
- repository ID `1342321016`;
- repository owner ID `42391449`;
- ref `refs/heads/main`;
- event `workflow_dispatch`;
- runner environment `github-hosted`.

The only trust expansion is `workflow_ref`. Exactly two workflow refs are accepted:

1. `Dtwosam/FMP/.github/workflows/phase2-cloud-golden.yml@refs/heads/main`
2. `Dtwosam/FMP/.github/workflows/phase2-full-history.yml@refs/heads/main`

No wildcard, prefix, branch family, pull-request identity, push event, or arbitrary reusable workflow is accepted.

The Edge Function remains read-only: manifest-first reads from `fmp-raw`, exact Phase 1 manifest validation, raw SHA-256/size verification, no upload/update/remove/list/signed-URL/proxy surface.

## Materialization architecture

### Pair isolation

The workflow runs one job per pair using a fixed three-value matrix. Pair jobs are independent, so a failure cannot create a cross-pair partial manifest that looks complete.

### Month-bounded processing

A pair job iterates the frozen range by UTC calendar month. For each month:

1. normalize each day through `CloudRawChunkReader`;
2. read BID and ASK only through the authenticated `fmp-raw-read` function;
3. process days concurrently with a fixed default of four workers;
4. collect only that month's canonical frames in memory;
5. sort deterministically by `symbol,timestamp_utc`;
6. write the 1m monthly partition;
7. derive and write deterministic 5m, 15m, and 1h monthly partitions;
8. discard the month frame before advancing.

Calendar-month boundaries are valid resampling boundaries because every supported timeframe is UTC-aligned and divides midnight exactly. Existing Phase 2 boundary tests remain authoritative.

The worker count is bounded to `1..8`. The workflow uses four workers, limiting the three-pair matrix to at most 12 concurrent day tasks. Existing raw-read retries remain the only retry layer: transport errors, HTTP 429, and 5xx only; permanent/auth/protocol/integrity failures fail closed.

### Full-pair quality pass

After all monthly 1m partitions for a pair are written, the job reads those 1m partitions in chronological order and runs the existing `analyze_quality` semantics across the full pair history. This preserves pair-wide IQR thresholds and cross-month gap detection rather than weakening quality analysis to independent monthly reports.

The quality report must retain all existing Phase 2 fields and findings. It is evidence, not an auto-cleaning step; suspicious observations are reported and never rewritten.

### Raw-read ledger

Every successful `CloudRawChunkReader` read is already protocol/identity/SHA/size verified. The full-history wrapper records a deterministic ledger entry containing:

- pair;
- side;
- date_utc;
- SHA-256 of returned raw bytes;
- size_bytes;
- status `complete`.

The ledger must contain exactly 8,500 unique entries per pair: 4,250 BID and 4,250 ASK, covering every frozen date exactly once per side. A verified `not_found` is an error for this frozen Phase 1 snapshot because Phase 1 acceptance recorded all 25,500 chunks as complete.

The ledger is written as stable JSON and its digest is included in the pair summary/processed evidence.

## Output layout

For a job output root `<root>`:

```text
<root>/
  processed/fmp-canonical-1m-v1/
    1m/<PAIR>/YYYY/MM.parquet
    5m/<PAIR>/YYYY/MM.parquet
    15m/<PAIR>/YYYY/MM.parquet
    1h/<PAIR>/YYYY/MM.parquet
    quality/<PAIR>.json
  manifests/processed/fmp-canonical-1m-v1/<PAIR>.json
  raw-ledger.json
  summary.json
```

Parquet writer configuration remains the frozen deterministic configuration already implemented in Phase 2 (`zstd`, level 3, statistics enabled).

The processed manifest remains the authoritative reproducibility record for the pair and includes source checkpoint/plan identity, schema and ingestion versions, code commit, artifact digests/sizes/row counts, quality summary, Polars version, and writer configuration.

`summary.json` additionally records the frozen requested range, pair, month count, raw-read counts, raw-ledger digest, row counts, processed-manifest digest, and quality finding counts.

## GitHub Actions workflow

Create `.github/workflows/phase2-full-history.yml` with:

- trigger: `workflow_dispatch` only;
- permissions: `contents: read`, `id-token: write` only;
- runner: `ubuntu-latest`;
- fixed matrix: EURUSD, GBPUSD, USDJPY;
- `fail-fast: false`;
- Python 3.12;
- Node 24 action majors (`actions/checkout@v6`, `actions/setup-python@v6`, `actions/upload-artifact@v6`);
- fixed endpoint `https://htjqqzlezyguveuajuat.supabase.co/functions/v1/fmp-raw-read`;
- fixed four-worker invocation;
- no source URL, acquisition CLI, repair workflow, raw upload, or date inputs;
- timeout 330 minutes per pair job.

Each pair job validates `summary.json` before upload and uploads one artifact named `phase2-full-history-<PAIR>` containing the complete pair output tree. The output directory is dot-prefixed, so `include-hidden-files: true` is mandatory. `if-no-files-found: error` is mandatory.

GitHub Actions artifacts are execution outputs/evidence, not source truth. The durable reproducibility identity is the immutable Phase 1 raw snapshot plus code commit, schema version, writer configuration, and processed manifest. No new Supabase processed-data bucket is introduced in this slice.

## Failure semantics

The materializer fails closed when any of the following occurs:

- OIDC token request fails permanently or exhausts transient retries;
- Edge Function rejects workflow identity;
- raw protocol, identity, content type, manifest status, SHA, or size mismatches;
- any frozen raw key is verified `not_found`;
- a day normalizes to an invalid canonical frame;
- an existing output partition conflicts by digest;
- the raw ledger is missing, duplicated, or contains an unexpected identity;
- full-pair quality analysis cannot complete;
- processed manifest or summary evidence fails validation.

A failed job must not mutate Phase 1 raw data and must not claim completion.

## Tests

### Edge/OIDC

- golden workflow ref remains accepted;
- full-history workflow ref is accepted;
- unlisted workflow refs are rejected;
- all other exact claims remain required;
- static no-storage-mutation guard remains green.

### Full-history planner/materializer

- frozen pair/range constants produce exactly 4,250 days and 140 calendar months per pair;
- worker bounds reject values outside `1..8`;
- month iteration is deterministic and covers each frozen day once;
- month materialization sorts output deterministically;
- raw ledger rejects missing, duplicate, wrong-pair, wrong-side, wrong-date, or `not_found` entries;
- a test-scale two-month run writes 1m/5m/15m/1h partitions, quality JSON, raw ledger, processed manifest, and summary with verified digests;
- repeated generation from identical inputs is deterministic except explicitly time-varying manifest metadata already covered by current contract.

### Workflow

- manual-only trigger;
- minimal permissions;
- fixed three-pair matrix;
- fixed endpoint and worker count;
- no arbitrary date inputs;
- no Dukascopy/source acquisition commands or raw storage writes;
- Node 24 action majors;
- artifact upload includes hidden files and errors on missing output.

### Repository verification

Before merge:

- workflow YAML validation;
- all Python unit tests;
- `python -m compileall -q src tests`;
- Deno tests and `deno check` for all Edge Functions;
- Phase 1 source-capable PR workflows skipped under `[phase1-no-source]`;
- complete diff review and frozen gap-queue non-modification.

After merge:

- main CI green;
- no Phase 1 acquisition triggered;
- deploy only the updated `fmp-raw-read` function;
- verify deployed function version/contents;
- manually dispatch `phase2-full-history` on `main` because the available GitHub integration cannot create new `workflow_dispatch` runs;
- inspect all three jobs, logs, and uploaded artifacts before any Phase 2 PASS decision.

## Non-goals

This slice does not:

- contact Dukascopy or any historical source;
- mutate, repair, delete, list, or rewrite `fmp-raw`;
- modify `docs/phase1-exact-gap-queue.json`;
- add arbitrary raw-object proxying;
- introduce a processed-data cloud bucket;
- add features, strategies, backtesting, ML, execution, or Phase 3 work;
- declare Phase 2 PASS before exhaustive run evidence is inspected against the Phase 2 exit gate.
