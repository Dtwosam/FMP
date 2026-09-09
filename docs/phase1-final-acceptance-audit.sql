-- Phase 1 structural acceptance audit for the frozen Dukascopy V1 snapshot.
-- This is a cloud-ledger gate. It does not replace local SHA/provenance verification.
--
-- PASS conditions represented here:
--   expected_manifests = 25,500
--   present_manifests = 25,500
--   missing_manifests = 0
--   unexpected_manifest_paths = 0
--   raw_without_manifest = 0
--   unexpected_raw_paths = 0
--
-- Local verifier evidence is still required before recording Phase 1 PASS.

with bounds as (
  select
    date '2015-01-01' as start_day,
    date '2026-08-21' as end_exclusive
),
expected as (
  select
    format(
      'manifests/dukascopy/v1/%s/%s/%s/%s/%s_candles_min_1.json',
      p.pair,
      to_char(d, 'YYYY'),
      lpad(((extract(month from d)::int) - 1)::text, 2, '0'),
      to_char(d, 'DD'),
      s.side
    ) as manifest_name,
    format(
      'raw/dukascopy/v1/%s/%s/%s/%s/%s_candles_min_1.bi5',
      p.pair,
      to_char(d, 'YYYY'),
      lpad(((extract(month from d)::int) - 1)::text, 2, '0'),
      to_char(d, 'DD'),
      s.side
    ) as raw_name
  from bounds b
  cross join lateral generate_series(
    b.start_day,
    b.end_exclusive - 1,
    interval '1 day'
  ) d
  cross join (values ('EURUSD'), ('GBPUSD'), ('USDJPY')) p(pair)
  cross join (values ('BID'), ('ASK')) s(side)
),
manifests as (
  select name, created_at
  from storage.objects
  where bucket_id = 'fmp-raw'
    and name like 'manifests/dukascopy/v1/%'
),
raws as (
  select name, created_at
  from storage.objects
  where bucket_id = 'fmp-raw'
    and name like 'raw/dukascopy/v1/%'
),
manifest_coverage as (
  select
    count(*) as expected_manifests,
    count(m.name) as present_manifests
  from expected e
  left join manifests m on m.name = e.manifest_name
),
unexpected_manifests as (
  select count(*) as unexpected_manifest_paths
  from manifests m
  left join expected e on e.manifest_name = m.name
  where e.manifest_name is null
),
unexpected_raws as (
  select count(*) as unexpected_raw_paths
  from raws r
  left join expected e on e.raw_name = r.name
  where e.raw_name is null
),
raw_without_manifest as (
  select count(*) as raw_without_manifest
  from raws r
  left join expected e on e.raw_name = r.name
  left join manifests m on m.name = e.manifest_name
  where e.raw_name is not null
    and m.name is null
)
select
  1 as report_version,
  'phase1_structural_acceptance' as scope,
  b.start_day as frozen_start_date,
  b.end_exclusive as frozen_end_date_exclusive,
  mc.expected_manifests,
  mc.present_manifests,
  mc.expected_manifests - mc.present_manifests as missing_manifests,
  round(100.0 * mc.present_manifests / mc.expected_manifests, 4) as completion_pct,
  (select count(*) from raws) as raw_objects,
  um.unexpected_manifest_paths,
  rwm.raw_without_manifest,
  ur.unexpected_raw_paths,
  (select max(created_at) from manifests) as latest_manifest_write,
  to_char(
    now() at time zone 'UTC',
    'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'
  ) as audited_at_utc,
  (
    mc.expected_manifests = 25500
    and mc.present_manifests = 25500
    and mc.expected_manifests - mc.present_manifests = 0
    and um.unexpected_manifest_paths = 0
    and rwm.raw_without_manifest = 0
    and ur.unexpected_raw_paths = 0
  ) as structural_gate_pass
from manifest_coverage mc
cross join bounds b
cross join unexpected_manifests um
cross join raw_without_manifest rwm
cross join unexpected_raws ur;
