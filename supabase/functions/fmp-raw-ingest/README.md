# fmp-raw-ingest

Private ingestion endpoint for immutable Phase 1 raw market-data objects.

Security is based on GitHub Actions OIDC, not a long-lived GitHub secret. The function validates issuer, audience, repository identity, owner identity, main-branch ref, workflow identity, event type, and GitHub-hosted runner environment before using Supabase server credentials internally.


## Raw-only safety

For canonical manifest uploads with `status = "not_found"`, the function checks the matching raw object path first. If immutable raw already exists, the manifest is rejected with HTTP 409. A Storage error is treated as absence only when it is a verified missing-key/not-found response; all other lookup failures fail closed.


For canonical `complete` manifests, the function downloads the matching immutable raw object with `cache: no-store` and requires exact SHA-256 and byte-size agreement with the manifest before the manifest can be stored. Malformed JSON and unknown manifest statuses are rejected before immutable storage.


## Canonical manifest validation

Before immutable manifest storage, the ingest function requires the exact frozen Phase 1 manifest field set and validates path-derived pair/side/date/source identity, retrieval method, granularity/format constants, timezone-aware retrieval timestamp, and status-specific `complete` / `not_found` metadata. Extra fields, missing fields, identity mismatches, malformed JSON, and unknown statuses are rejected.


## Frozen object namespace

Canonical raw and manifest paths are accepted only when their zero-based year/month/day components resolve to a real Gregorian date in the frozen Phase 1 interval, 2015-01-01 through 2026-08-20 inclusive. Regex-shaped impossible dates and paths outside that interval are rejected before Storage access.


## Protocol preflight

Authenticated GitHub Actions callers may send `GET` to the function endpoint. A deployment that matches the hardened Phase 1 ingest contract returns exactly:

```json
{"status":"ready","protocol":"fmp-raw-ingest-v2"}
```

The Python mirror client requires this response before any cloud-mirrored source acquisition. This makes a stale or incorrectly deployed ingest endpoint fail before Dukascopy access rather than during object persistence.
