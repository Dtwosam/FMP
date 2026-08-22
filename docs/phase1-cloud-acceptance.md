# Phase 1 Cloud Acceptance Contract

This document defines the evidence required to declare FMP Phase 1 historical acquisition complete. It is an acceptance contract, not a progress estimate.

## Frozen target

- UTC start: `2015-01-01`
- exclusive end: `2026-08-21`
- pairs: `EURUSD`, `GBPUSD`, `USDJPY`
- sides: `BID`, `ASK`
- one acquisition manifest per calendar day / pair / side
- expected manifest count: **25,500**

A source day that legitimately returns HTTP 404 is still represented by a manifest with `status=not_found`; therefore a complete Phase 1 snapshot still requires all 25,500 manifest paths to exist.

## Gate A — exhaustive manifest coverage

Run against the dedicated FMP Supabase project:

```sql
with bounds as (
  select date '2015-01-01' as start_day,
         date '2026-08-21' as end_exclusive
), expected as (
  select
    p.pair,
    s.side,
    d::date as day,
    format(
      'manifests/dukascopy/v1/%s/%s/%s/%s/%s_candles_min_1.json',
      p.pair,
      to_char(d, 'YYYY'),
      lpad(((extract(month from d)::int) - 1)::text, 2, '0'),
      to_char(d, 'DD'),
      s.side
    ) as object_name
  from bounds b
  cross join lateral generate_series(
    b.start_day,
    b.end_exclusive - 1,
    interval '1 day'
  ) d
  cross join (values ('EURUSD'), ('GBPUSD'), ('USDJPY')) p(pair)
  cross join (values ('BID'), ('ASK')) s(side)
), present as (
  select name
  from storage.objects
  where bucket_id = 'fmp-raw'
    and name like 'manifests/%'
)
select
  count(*) as expected_manifests,
  count(present.name) as present_manifests,
  count(*) - count(present.name) as missing_manifests,
  round(100.0 * count(present.name) / count(*), 4) as completion_pct
from expected
left join present on present.name = expected.object_name;
```

Phase 1 cannot pass unless the result is exactly:

```text
expected_manifests = 25500
present_manifests  = 25500
missing_manifests  = 0
completion_pct     = 100.0000
```

## Gate B — local monthly provenance verification

Every active monthly recovery job must run the repository verifier after acquisition:

```bash
python -m fmp.data.cli verify \
  --pair ALL \
  --start <MONTH_START> \
  --end <MONTH_END_EXCLUSIVE> \
  --out <LOCAL_SHARD_DIR>
```

The verifier requires every planned chunk in that month to have consistent acquisition provenance. For completed chunks, the local raw bytes must match the SHA-256 recorded in the manifest. A failed monthly verification is not ignored; its month remains a retry target.

## Gate C — cloud-ingest integrity chain

For every object mirrored to the private `fmp-raw` bucket:

1. the acquisition layer writes the raw source bytes and manifest locally;
2. completed raw bytes are SHA-256 hashed;
3. the mirror client SHA-256 hashes the exact object body sent to Supabase;
4. `fmp-raw-ingest` recomputes SHA-256 from the received request body and rejects a mismatch;
5. new objects are stored with `upsert=false`;
6. duplicate raw objects are accepted only when the already-stored bytes hash to the same SHA-256;
7. duplicate manifests may differ only in top-level `retrieved_at_utc`; every substantive field must match;
8. substantive conflicts return HTTP 409 and must block acceptance.

This creates the Phase 1 integrity chain:

```text
Dukascopy bytes
  -> local structural validation
  -> local SHA-256 + manifest
  -> monthly local verifier
  -> authenticated GitHub OIDC mirror
  -> Edge Function SHA-256 recomputation
  -> private immutable Supabase object
```

## Gate D — missing-location report

If Gate A has any missing manifests, localize them before rerunning anything:

```sql
with bounds as (
  select date '2015-01-01' as start_day,
         date '2026-08-21' as end_exclusive
), expected as (
  select
    p.pair,
    s.side,
    d::date as day,
    format(
      'manifests/dukascopy/v1/%s/%s/%s/%s/%s_candles_min_1.json',
      p.pair,
      to_char(d, 'YYYY'),
      lpad(((extract(month from d)::int) - 1)::text, 2, '0'),
      to_char(d, 'DD'),
      s.side
    ) as object_name
  from bounds b
  cross join lateral generate_series(
    b.start_day,
    b.end_exclusive - 1,
    interval '1 day'
  ) d
  cross join (values ('EURUSD'), ('GBPUSD'), ('USDJPY')) p(pair)
  cross join (values ('BID'), ('ASK')) s(side)
)
select
  pair,
  extract(year from day)::int as year,
  extract(month from day)::int as month,
  count(*) as missing_manifests
from expected e
left join storage.objects o
  on o.bucket_id = 'fmp-raw'
 and o.name = e.object_name
where o.name is null
group by pair, year, month
order by year, month, pair;
```

Only missing/failed monthly shards should be retried. Existing cloud progress must not be deleted or overwritten.

## Gate E — final evidence record

Before Phase 1 PASS, `docs/project-state.md` must record:

- the final Gate A result;
- any failed monthly shards and their successful retry evidence;
- the final raw/manifest object totals;
- the last object timestamp for the frozen snapshot;
- the recovery workflow/commit used;
- confirmation that no unexplained planned manifest remains missing;
- confirmation that Phase 2 stayed locked until this gate passed.

## Promotion rule

Phase 1 is **PASS** only when all of the following are true:

- Gate A = `25,500 / 25,500` manifests;
- every monthly shard has successful provenance verification, either on its first run or a documented retry;
- no unexplained acquisition conflict remains;
- final evidence is committed to the source-of-truth;
- a Phase 1 checkpoint is recorded.

Until then the state remains Phase 1, regardless of how many raw objects have already been downloaded.
