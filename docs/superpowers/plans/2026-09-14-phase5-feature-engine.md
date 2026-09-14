# Phase 5 Leakage-Safe Feature Engine Implementation Plan

**Date:** 2026-09-14
**Protocol:** DEC-029 / `docs/superpowers/specs/2026-09-14-phase5-leakage-safe-feature-engine-design.md`
**Base:** corrected `main` at `6f8451902fb6737168d7d1e0ed45710d29a4f1d2`
**Method:** strict TDD. Add focused failing tests first, prove RED on GitHub Actions, then add only enough production code to turn them green. Do not open/read any 2024+ processed partition.

## Existing interfaces to reuse

- `src/fmp/research/data.py` already validates the accepted Phase 2 processed-manifest identity, resolves monthly derived-bar artifacts, and reads Parquet with Polars. Phase 5 will reuse its manifest/path-safety ideas, but will own a stricter reader because Phase 4 split selection is not strong enough for the DEC-029 rule that 2024+ paths fail before opening.
- `src/fmp/data/phase2/resample.py` defines the derived-bar columns and confirms bars are left-labelled; complete 5m/15m/1h rows contain BID/ASK OHLC, volumes, `source_minutes`, `expected_open_minutes`, `is_complete`, `timeframe`, and schema version.
- `src/fmp/data/phase2/artifacts.py` supplies deterministic Parquet writer settings and SHA-256 helpers. Phase 5 will reuse `sha256_file` and writer configuration semantics rather than creating a conflicting format.
- Project dependency surface remains Python 3.11+ with `polars==1.44.2`; use stdlib `zoneinfo` for time zones, no new dependency.

## Task 1 — Freeze feature contracts and the final-test-safe reader

**Tests first:**
- Add `tests/test_phase5_feature_data.py`.
- Cover eligible symbols/timeframes, processed manifest identity, path escape rejection, missing artifact rejection, exact month selection, incomplete-bar retention policy at load boundary, monotonic/unique rows, and the hard `2024-01-01` source boundary.
- Hard-boundary test must instrument the Parquet opener/reader and assert a request needing a 2024 partition raises before the opener receives that path.

**Production files:**
- `src/fmp/features/__init__.py`
- `src/fmp/features/contracts.py`
- `src/fmp/features/data.py`

**Contract:**
- `FEATURE_SET_VERSION = "fmp-feature-v1"`.
- symbols exactly EURUSD/GBPUSD/USDJPY; TF exactly 5m/15m/1h.
- source end exclusive may not exceed `2024-01-01 UTC`.
- reader validates Phase 2 schema/symbol and artifact records before reading any file.
- requested partition selection occurs before any `pl.read_parquet` call; if any selected month reaches 2024, fail immediately.
- source bars remain sorted/unique and retain `is_complete`; feature calculations decide when incomplete rows invalidate windows.

**RED command:** `python -m unittest tests.test_phase5_feature_data -v`.

## Task 2 — Build a deterministic base feature frame and row-time contract

**Tests first:** `tests/test_phase5_feature_base.py`.
- midpoint OHLC is exact arithmetic average of BID/ASK OHLC.
- pip size exact by symbol.
- `bar_end_utc = timestamp_utc + timeframe width`; `available_at_utc == bar_end_utc`.
- current fully closed bar is usable; incomplete current rows produce null market-derived features rather than being silently repaired.
- identity columns and feature-set version are stable and rows stay sorted/unique.

**Production files:**
- `src/fmp/features/base.py`
- extend `contracts.py`.

**RED command:** `python -m unittest tests.test_phase5_feature_base -v`.

## Task 3 — Implement local/rolling numerical families

**Tests first:** `tests/test_phase5_feature_numeric.py`.
- returns: 1bar, exact 1h, exact 24h, log return.
- volatility/range: range, true range, realized vol 1h/8h/24h, range vs prior 8h median.
- trend: SMA distance/slope 2h/8h and prior-8h breakout flags.
- momentum: ROC 4h/8h and 4h acceleration.
- candle: body/wicks/ratios/location/direction/streak cap 20.
- exact-cadence windows become null if any required timestamp/bar is absent/incomplete/non-finite; no shortened window.
- current bar excluded where protocol says prior reference `[T-window,T)`.

**Production files:**
- `src/fmp/features/numeric.py`

Implementation should favor explicit timestamp/index validation over Polars row-count rolling shortcuts so weekend/closure gaps cannot masquerade as complete duration windows.

**RED command:** `python -m unittest tests.test_phase5_feature_numeric -v`.

## Task 4 — Implement named-zone session/time features

**Tests first:** `tests/test_phase5_feature_sessions.py`.
- Asia 09:00-17:00 `Asia/Tokyo`.
- London 08:00-16:00 `Europe/London`.
- New York 08:00-17:00 `America/New_York`.
- complete interval, not just start instant, must lie within session.
- overlap iff London and NY flags are both true.
- UTC hour/minute/DOW and minutes-since-open.
- explicit examples across UK and US DST changes, including mismatch weeks.

**Production files:**
- `src/fmp/features/sessions.py`

Use `zoneinfo.ZoneInfo`; do not hard-code UTC offsets.

**RED command:** `python -m unittest tests.test_phase5_feature_sessions -v`.

## Task 5 — Implement completed-reference market-location features

**Tests first:** `tests/test_phase5_feature_location.py`.
- previous FX day is `[17:00 America/New_York, next 17:00 America/New_York)`.
- completed reference must have exact expected cadence and finite complete midpoint OHLC.
- previous FX day high/low/close distances.
- most recent completed Asia and London high/low distances.
- incomplete references are skipped, never partially used.
- a completed reference may persist until a later complete reference supersedes it; this is the only intentional level carry.
- reset boundaries and DST transitions.

**Production files:**
- `src/fmp/features/location.py`

**RED command:** `python -m unittest tests.test_phase5_feature_location -v`.

## Task 6 — Implement spread/quote-quality features

**Tests first:** `tests/test_phase5_feature_spread.py`.
- close spread pips.
- complete trailing mean 1h.
- prior median 8h excluding current.
- current/prior-median ratio with null on non-positive/non-finite denominator.
- percentile versus complete prior 24h (`<= current`).
- incomplete/gapped windows null; no quote repair.

**Production files:**
- `src/fmp/features/spread.py`

**RED command:** `python -m unittest tests.test_phase5_feature_spread -v`.

## Task 7 — Compose the engine, freeze schema, and publish the dictionary

**Tests first:** `tests/test_phase5_feature_engine.py`.
- all eight family columns exist exactly once.
- no unapproved activity/cross-pair/multi-timeframe/label/model fields.
- feature key `(symbol,timeframe,bar_start_utc)` unique and sorted.
- feature-set version + processed-manifest SHA persisted per row/manifest.
- output schema hash deterministic.
- dictionary column list matches machine schema.

**Production/docs:**
- `src/fmp/features/engine.py`
- `src/fmp/features/schema.py`
- `docs/phase5-feature-dictionary.md`

Dictionary must reproduce DEC-029 formulas, units, null semantics, availability timing, and reference semantics without adding new feature degrees of freedom.

**RED command:** `python -m unittest tests.test_phase5_feature_engine -v`.

## Task 8 — Add deterministic partition/artifact generation and CLI

**Tests first:** `tests/test_phase5_feature_artifacts.py` and `tests/test_phase5_feature_cli.py`.
- output layout `data/features/fmp-feature-v1/<symbol>/<timeframe>/<year>/<month>.parquet`.
- writer is stable/idempotent and conflicts fail closed.
- monthly partitions contain only rows before 2024.
- evidence manifest records version, code SHA, accepted processed-manifest SHA, symbol/TF, opened source coverage, output coverage, row/unique counts, schema/list/hash, per-column null counts, output path/size/SHA, and frozen params.
- JSON is sorted/stable and forbids NaN.
- CLI rejects 2024+ before invoking the reader.

**Production:**
- `src/fmp/features/artifacts.py`
- `src/fmp/features/cli.py`
- `scripts/phase5_features.py`

**RED command:** `python -m unittest tests.test_phase5_feature_artifacts tests.test_phase5_feature_cli -v`.

## Task 9 — Add whole-engine leakage/determinism regression tests

**Tests first and permanent:** `tests/test_phase5_feature_leakage.py`.
- prefix equivalence.
- future perturbation.
- current-closed-bar allowance.
- exact-cadence failure and post-closure warm-up.
- completed-reference completeness/persistence.
- deterministic regeneration value/hash equality.
- hard final-test read block with an opener spy.
- no 2024+ output or opened-source record.

Run all Phase 5 tests together before any workflow is added.

## Task 10 — Add source-free 9-cell acceptance workflow

**Tests first:** `tests/test_phase5_feature_workflow.py`.
- workflow matrix exactly three accepted Phase 2 artifacts × 5m/15m/1h = 9 cells.
- artifact IDs and outer ZIP SHA-256 identities frozen to accepted Phase 2 evidence.
- workflow passes no final split/date token and uses the feature CLI bounded through 2023-12-31.
- permissions read-only for repository/actions; no Dukascopy, Supabase raw write/read acquisition path, broker, or live endpoint.
- each cell regenerates twice and checks deterministic manifest/data digests before artifact upload.

**Production:**
- `.github/workflows/phase5-features.yml`

Accepted Phase 2 artifact identities:
- EURUSD `10325737935` / `db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3`
- GBPUSD `10326096831` / `fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2`
- USDJPY `10327600628` / `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`

Accepted processed-manifest SHA-256 identities remain frozen from Phase 2 evidence.

## Task 11 — Verification and merge gates

Before opening the implementation PR:
- `python -m unittest discover -s tests -v`
- workflow YAML validation used by repository tests
- `python -m compileall -q src scripts`
- `git diff --check`
- verify no helper/test-runner workflow remains.
- verify no final-test, broker/live, model/label, activity, 1m feature-matrix, cross-pair, or multi-timeframe implementation exists.

PR title must include `[phase1-no-source]`. Required PR checks:
- full tests/YAML/compile SUCCESS;
- unchanged Phase 3 acceptance SUCCESS;
- Phase 1 source-capable checks SKIPPED.

After merge, verify merged-main tests and Phase 3 again. Only then trigger the authoritative 9-cell `phase5-features` workflow from the merged implementation SHA. Independently audit all nine uploaded artifacts before any Phase 5 PASS/closure/checkpoint decision.
