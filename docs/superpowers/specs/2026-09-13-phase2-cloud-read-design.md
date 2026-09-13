# Phase 2 Cloud Raw Read Foundation Design

## Status

Approved implementation slice for Phase 2. Phase 1 remains PASS and closed at checkpoint `fmp-v1-phase1-source-of-truth`. Phase 2 remains active and MUST NOT be declared PASS by this slice.

## Goal

Add a fail-closed, read-only authenticated path from GitHub Actions to the immutable Phase 1 Supabase `fmp-raw` bucket, expose it through `RawChunkReader.read(key) -> bytes | None`, and prove a tiny bounded real-cloud Phase 2 materialization for both Dukascopy price-divisor classes without contacting Dukascopy or mutating Phase 1 data.

## Scope and invariants

This slice adds one Supabase Edge Function, one Python cloud reader, their tests/configuration, and one manual source-free workflow. It does not modify `docs/phase1-exact-gap-queue.json`, does not invoke Phase 1 acquisition or repair, does not write to `fmp-raw`, does not process full history, does not start Phase 3, and does not change the Phase 1 checkpoint.

All commits for this slice include `[phase1-no-source]`.

## Edge Function: `fmp-raw-read`

The new function is `supabase/functions/fmp-raw-read`. Supabase configuration sets `[functions.fmp-raw-read] verify_jwt = false` because the function validates GitHub OIDC itself.

The protocol identifier is `fmp-raw-read-v1`. The GitHub OIDC audience is `fmp-supabase-raw-read`.

### Authentication

Authentication follows the existing `fmp-raw-audit` fail-closed model with `jose` and GitHub's OIDC JWKS. The token MUST have exactly the trusted claims below:

- `repository = Dtwosam/FMP`
- `repository_id = 1342321016`
- `repository_owner_id = 42391449`
- `ref = refs/heads/main`
- `event_name = workflow_dispatch`
- `runner_environment = github-hosted`
- `workflow_ref = Dtwosam/FMP/.github/workflows/phase2-cloud-golden.yml@refs/heads/main`

Issuer is `https://token.actions.githubusercontent.com`; audience is `fmp-supabase-raw-read`. Missing, malformed, expired, wrong-audience, or claim-mismatched tokens fail with HTTP 401 and no storage access.

### Request contract

`GET` is an authenticated readiness check and returns exactly:

```json
{"status":"ready","protocol":"fmp-raw-read-v1"}
```

`POST` accepts a JSON object containing exactly three fields:

```json
{"pair":"EURUSD","side":"BID","date_utc":"2026-08-20"}
```

Allowed pairs are `EURUSD`, `GBPUSD`, and `USDJPY`. Allowed sides are `BID` and `ASK`. `date_utc` MUST be a real UTC calendar date from 2015-01-01 through 2026-08-20 inclusive. Extra fields, missing fields, non-string values, malformed dates, out-of-range dates, unsupported pairs/sides, empty bodies, and oversized bodies fail with HTTP 400.

The caller never supplies a storage path. The function derives both object paths from the validated identity using the frozen zero-based Dukascopy month convention:

- manifest: `manifests/dukascopy/v1/{PAIR}/{YYYY}/{MM0}/{DD}/{SIDE}_candles_min_1.json`
- raw: `raw/dukascopy/v1/{PAIR}/{YYYY}/{MM0}/{DD}/{SIDE}_candles_min_1.bi5`

where `MM0` is `00` through `11`.

### Manifest-first integrity gate

The function always downloads the derived manifest first with cache disabled. A missing/unreadable manifest, malformed JSON, wrong field set, wrong field types, wrong identity, wrong source URL, wrong retrieval method/source/granularity/format/record size/month indexing, invalid timestamp, unsupported status, or inconsistent status fields fails closed before returning raw bytes.

The validator implements the exact frozen Phase 1 manifest contract already represented by `src/fmp/data/manifest.py`:

- exact field set;
- integer, non-boolean `manifest_version = 1`;
- `retrieval_method = dukascopy-public-daily-m1-bi5-v1`;
- `source = dukascopy`;
- exact Dukascopy daily URL for the requested key using zero-based source month;
- exact pair/side/date identity;
- `granularity = 1m`;
- `source_format = bi5-lzma-daily-candles`;
- `record_size_bytes = 24`;
- `month_indexing = zero_based_in_source_url`;
- UTC `retrieved_at_utc`;
- exact complete/not-found status rules.

For `status = complete`, the function downloads the raw object only after manifest validation, computes SHA-256 and byte length, and requires exact equality with `sha256` and `compressed_size_bytes`. Missing raw bytes, a storage error, SHA mismatch, or size mismatch fails closed with HTTP 502.

For a verified `status = not_found`, the function returns the protocol not-found response and does not expose bytes. The response is HTTP 404 JSON with exactly `status`, `protocol`, `pair`, `side`, and `date_utc`, where `status = not_found` and `protocol = fmp-raw-read-v1`.

### Complete response

A verified complete chunk returns the exact `.bi5` bytes with HTTP 200 and `Content-Type: application/octet-stream`.

The response carries immutable identity/provenance headers used by the Python client to bind the bytes to the requested key and frozen Phase 1 manifest:

- `X-FMP-Protocol: fmp-raw-read-v1`
- `X-FMP-Pair: {PAIR}`
- `X-FMP-Side: {SIDE}`
- `X-FMP-Date-UTC: {YYYY-MM-DD}`
- `X-FMP-SHA256: {manifest sha256}`
- `X-FMP-Size-Bytes: {manifest compressed_size_bytes}`
- `X-FMP-Manifest-Status: complete`
- `Cache-Control: no-store`

No signed URL, list API, arbitrary proxy path, upload, update, or delete surface is added.

## Python: `CloudRawChunkReader`

`CloudRawChunkReader` is added alongside the existing `RawChunkReader`, `RawReadError`, and `LocalRawChunkReader` in `src/fmp/data/phase2/raw_reader.py` or a focused adjacent module re-exported from there. It implements `read(key: RawChunkKey) -> bytes | None`.

The reader receives an HTTPS Edge Function endpoint plus an OIDC token provider. The default GitHub token provider requests audience `fmp-supabase-raw-read` from `ACTIONS_ID_TOKEN_REQUEST_URL` using `ACTIONS_ID_TOKEN_REQUEST_TOKEN`, following the existing cloud-audit token acquisition model and token-expiry caching behavior.

For each key the reader POSTs only pair, side, and ISO date. It accepts only two successful protocol outcomes:

1. HTTP 200 octet-stream with exact protocol, identity, manifest-status, SHA, and size headers; the client recomputes SHA-256 and byte length and returns bytes only if every check matches.
2. HTTP 404 JSON with the exact not-found schema and exact requested identity; then `read` returns `None`.

All other responses fail with `RawReadError`.

### Retry policy

Both GitHub OIDC acquisition and Edge Function reads use bounded retries with defaults of three attempts and an injectable one-second delay.

Retry only:

- `TimeoutError`
- `ConnectionError`
- `OSError`
- HTTP 429
- HTTP 5xx

Do not retry:

- permanent/auth HTTP 4xx other than the protocol's verified not-found response;
- wrong protocol;
- malformed success or not-found response;
- wrong content type;
- wrong identity/provenance headers;
- malformed SHA/size headers;
- SHA mismatch;
- size mismatch;
- any provenance/integrity failure.

## Manual source-free workflow

Add `.github/workflows/phase2-cloud-golden.yml` with `workflow_dispatch` as its only trigger and top-level permissions limited to `contents: read` and `id-token: write`.

The workflow never contacts Dukascopy and never invokes Phase 1 acquisition/repair. It installs the project dependencies, runs a small script/CLI path that constructs `CloudRawChunkReader` against the deployed `fmp-raw-read` endpoint, and reads only a tiny explicit allowlist of real frozen Phase 1 chunks containing at least one EURUSD chunk and one USDJPY chunk. This ensures both Dukascopy price-divisor classes are exercised.

The proof materializes only those bounded chunks through the existing Phase 2 decoder/normalizer/quality/resampling pipeline and emits reproducible evidence for canonical 1m plus quality plus 5m/15m/1h outputs. It does not iterate the frozen history and does not invoke source acquisition.

Evidence uploaded as GitHub Actions artifacts includes a machine-readable summary with requested chunk identities, raw SHA/size provenance, canonical row counts/digests, quality result paths/digests, and 5m/15m/1h artifact paths/digests. The workflow fails if either pair is absent, if a cloud read is not integrity verified, or if expected evidence is missing.

The Edge Function endpoint is derived from fixed Supabase project ID `htjqqzlezyguveuajuat`; no secret service-role key is exposed to the workflow. GitHub OIDC is the only caller credential.

## Testing strategy

Development follows small RED → GREEN cycles.

Deno validation tests cover request schema/date bounds/path derivation, exact manifest contract, complete/not-found states, integrity mismatches, and trusted GitHub claims. Python tests cover OIDC audience/caching, retry classification, exact request body, complete header/body verification, verified not-found handling, all non-retry integrity failures, and `RawChunkReader` compatibility. Workflow/config tests assert manual-only triggering, exact permissions, source-free behavior, both divisor classes, bounded materialization, evidence upload, and `verify_jwt = false`.

Before merge, run the full Python suite, `compileall`, workflow YAML validation, Deno/Edge validation tests, and a clean-diff check. PR CI must be green and Phase 1 source-capable jobs must be skipped. The complete PR diff is reviewed before a squash merge.

After merge, verify `main` CI and confirm any `phase1-full-acquisition` push run is skipped. Deploy only `fmp-raw-read`, then manually dispatch `phase2-cloud-golden.yml` and inspect the real uploaded evidence. This successful bounded proof still does not make Phase 2 PASS.

## Safety boundary

No code in this slice may write to Supabase Storage. The new Edge Function is read-only by construction and the workflow is source-free. Any failure to prove caller identity, request identity, manifest provenance, raw integrity, or response identity terminates the read rather than falling back to a source or another path.
