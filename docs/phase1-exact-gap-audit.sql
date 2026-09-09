-- Phase 1 exact-gap audit for the frozen Dukascopy V1 snapshot.
-- Run against the dedicated FMP Supabase project after a repair sweep stops.
-- The single JSON result is directly compatible with:
--   python -m fmp.data.cli fetch-plan --plan docs/phase1-exact-gap-queue.json ...
--
-- Frozen snapshot: 2015-01-01 through 2026-08-20 inclusive.
-- Expected plan size at full coverage: 25,500 pair/date/side manifests.

with bounds as (
  select
    date '2015-01-01' as start_day,
    date '2026-08-21' as end_exclusive
),
expected as (
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
),
present as (
  select name
  from storage.objects
  where bucket_id = 'fmp-raw'
    and name like 'manifests/dukascopy/v1/%'
),
coverage as (
  select count(*)::int as present_manifests_at_audit
  from expected e
  join present p on p.name = e.object_name
),
missing as (
  select e.pair, e.side, e.day
  from expected e
  left join present p on p.name = e.object_name
  where p.name is null
),
missing_count as (
  select count(*)::int as missing_manifests_at_audit
  from missing
)
select jsonb_build_object(
  'plan_version', 1,
  'frozen_start_date', '2015-01-01',
  'frozen_end_date_exclusive', '2026-08-21',
  'audited_at_utc', to_char(now() at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
  'present_manifests_at_audit', coverage.present_manifests_at_audit,
  'missing_manifests_at_audit', missing_count.missing_manifests_at_audit,
  'chunks', coalesce(
    jsonb_agg(
      jsonb_build_object(
        'pair', pair,
        'side', side,
        'date_utc', to_char(day, 'YYYY-MM-DD')
      )
      order by day, pair, side
    ),
    '[]'::jsonb
  )
) as exact_gap_plan
from missing
cross join coverage
cross join missing_count
group by coverage.present_manifests_at_audit, missing_count.missing_manifests_at_audit;
