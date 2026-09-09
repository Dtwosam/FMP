-- Phase 1 recovery/accounting audit for the frozen Dukascopy V1 snapshot.
--
-- Purpose:
--   Reconcile every planned pair/date/side key to the immutable cloud object
--   ledger and produce deterministic pair/side acquisition accounting.
--
-- Important inference:
--   The Python mirror writes COMPLETE results raw first, then manifest.
--   NOT_FOUND results write manifest only. Cloud raw/manifest objects are
--   immutable and never deleted as a repair shortcut. Therefore, when
--   raw_without_manifest = 0 and unexpected paths = 0, a planned manifest
--   without its planned raw object is the acquisition-accounting class
--   manifest_only_inferred_not_found.
--
-- This query does NOT parse manifest JSON bodies and does NOT replace the
-- Python provenance verifier. It is an accounting gate, not a Phase 2 data
-- quality gate.
--
-- Frozen snapshot: 2015-01-01 through 2026-08-20 inclusive.
-- Expected plan: 25,500 manifests = 4,250 days x 3 pairs x 2 sides.

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
planned_state as (
  select
    e.pair,
    e.side,
    e.day,
    e.manifest_name,
    e.raw_name,
    m.name is not null as has_manifest,
    r.name is not null as has_raw
  from expected e
  left join manifests m on m.name = e.manifest_name
  left join raws r on r.name = e.raw_name
),
pair_side as (
  select
    pair,
    side,
    count(*)::int as expected_manifests,
    count(*) filter (where has_manifest)::int as present_manifests,
    count(*) filter (where not has_manifest)::int as missing_manifests,
    count(*) filter (where has_manifest and has_raw)::int as raw_backed_manifests,
    count(*) filter (where has_manifest and not has_raw)::int
      as manifest_only_inferred_not_found,
    count(*) filter (where has_raw and not has_manifest)::int
      as raw_without_manifest
  from planned_state
  group by pair, side
),
totals as (
  select
    sum(expected_manifests)::int as expected_manifests,
    sum(present_manifests)::int as present_manifests,
    sum(missing_manifests)::int as missing_manifests,
    sum(raw_backed_manifests)::int as raw_backed_manifests,
    sum(manifest_only_inferred_not_found)::int
      as manifest_only_inferred_not_found,
    sum(raw_without_manifest)::int as raw_without_manifest
  from pair_side
),
unexpected_manifests as (
  select count(*)::int as unexpected_manifest_paths
  from manifests m
  left join expected e on e.manifest_name = m.name
  where e.manifest_name is null
),
unexpected_raws as (
  select count(*)::int as unexpected_raw_paths
  from raws r
  left join expected e on e.raw_name = r.name
  where e.raw_name is null
),
accounting as (
  select
    t.*,
    um.unexpected_manifest_paths,
    ur.unexpected_raw_paths,
    (
      t.expected_manifests = 25500
      and t.present_manifests = 25500
      and t.missing_manifests = 0
      and t.raw_without_manifest = 0
      and um.unexpected_manifest_paths = 0
      and ur.unexpected_raw_paths = 0
      and (
        t.raw_backed_manifests
        + t.manifest_only_inferred_not_found
      ) = t.present_manifests
    ) as accounting_gate_pass
  from totals t
  cross join unexpected_manifests um
  cross join unexpected_raws ur
)
select jsonb_build_object(
  'report_version', 1,
  'scope', 'phase1_recovery_accounting',
  'frozen_start_date', '2015-01-01',
  'frozen_end_date_exclusive', '2026-08-21',
  'audited_at_utc',
    to_char(now() at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
  'totals', jsonb_build_object(
    'expected_manifests', a.expected_manifests,
    'present_manifests', a.present_manifests,
    'missing_manifests', a.missing_manifests,
    'raw_backed_manifests', a.raw_backed_manifests,
    'manifest_only_inferred_not_found',
      a.manifest_only_inferred_not_found,
    'raw_without_manifest', a.raw_without_manifest,
    'unexpected_manifest_paths', a.unexpected_manifest_paths,
    'unexpected_raw_paths', a.unexpected_raw_paths
  ),
  'pair_side_breakdown', (
    select jsonb_agg(
      jsonb_build_object(
        'pair', ps.pair,
        'side', ps.side,
        'expected_manifests', ps.expected_manifests,
        'present_manifests', ps.present_manifests,
        'missing_manifests', ps.missing_manifests,
        'raw_backed_manifests', ps.raw_backed_manifests,
        'manifest_only_inferred_not_found',
          ps.manifest_only_inferred_not_found,
        'raw_without_manifest', ps.raw_without_manifest
      )
      order by ps.pair, ps.side
    )
    from pair_side ps
  ),
  'accounting_gate_pass', a.accounting_gate_pass,
  'note',
    'Accounting only: manifest-only is inferred not_found from immutable mirror ordering; Python provenance verification remains required.'
) as phase1_recovery_accounting
from accounting a;
