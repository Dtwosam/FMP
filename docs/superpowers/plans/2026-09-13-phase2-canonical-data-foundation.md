# Phase 2 Canonical Data Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the local, bounded Phase 2 canonical-data foundation: typed BI5 decoding, canonical BID/ASK normalization, deterministic quality analysis, 5m/15m/1h resampling, Parquet artifacts, processed manifests, and CLI wiring without touching the immutable Phase 1 raw snapshot.

**Architecture:** Add a focused `fmp.data.phase2` package under the existing data layer. Decode each Dukascopy side independently, outer-join by UTC minute into schema `fmp-canonical-1m-v1`, analyze but never mutate anomalies, resample deterministically, and write versioned Parquet plus JSON manifests. The authenticated cloud reader and exhaustive full-history processing are deliberately excluded from this plan and receive a separate plan after this local foundation is green.

**Tech Stack:** Python >=3.11, `unittest`, standard-library `lzma`/`struct`/`hashlib`/`zoneinfo`, `polars==1.44.2`, Parquet, JSON.

**Spec:** `docs/superpowers/specs/2026-09-13-phase2-canonical-data-design.md`

## Global Constraints

- Phase 1 snapshot is immutable and remains the source of truth.
- V1 symbols are exactly `EURUSD`, `GBPUSD`, `USDJPY`.
- Canonical schema identity is `fmp-canonical-1m-v1`.
- Derived schema identity is `fmp-derived-bars-v1`.
- Ingestion identity is `dukascopy-bi5-candles-v1`.
- Canonical timestamps are UTC bar-start labels.
- BID and ASK remain separate; missing sides stay null and are never synthesized.
- Quote anomalies are reported, never silently repaired or dropped.
- Resampling intervals are closed-left/open-right and UTC aligned.
- Polars is pinned exactly to `1.44.2`; Parquet uses Zstandard level 3 and statistics enabled.
- No full-history processing until a real accepted Phase 1 golden raw chunk has been decoded and checked.
- This plan must not start any Phase 1 acquisition/repair workflow.
- Real-money trading remains locked.

---

### Task 1: Dependency, schema constants, and BI5 decoder

**Files:**
- Modify: `pyproject.toml`
- Modify: `.github/workflows/tests.yml`
- Create: `src/fmp/data/phase2/__init__.py`
- Create: `src/fmp/data/phase2/schema.py`
- Create: `src/fmp/data/phase2/bi5.py`
- Create: `tests/test_phase2_bi5.py`

**Interfaces:**
- Produces constants:
  - `CANONICAL_SCHEMA_VERSION = "fmp-canonical-1m-v1"`
  - `DERIVED_SCHEMA_VERSION = "fmp-derived-bars-v1"`
  - `INGESTION_VERSION = "dukascopy-bi5-candles-v1"`
  - `PRICE_DIVISORS = {"EURUSD": 100_000, "GBPUSD": 100_000, "USDJPY": 1_000}`
- Produces `decode_bi5_day(key: RawChunkKey, body: bytes) -> pl.DataFrame`.
- Decoder frame columns in stable order: `timestamp_utc`, `symbol`, `side`, `open`, `high`, `low`, `close`, `volume`.

- [ ] **Step 1: Add failing decoder tests using repository-style synthetic BI5 fixtures**

```python
# tests/test_phase2_bi5.py
import lzma, struct, unittest
from datetime import date, datetime, timezone
from fmp.data.types import RawChunkKey
from fmp.data.phase2.bi5 import Phase2DecodeError, decode_bi5_day


def make_bi5(rows):
    raw = b"".join(struct.pack(">IIIIIf", *row) for row in rows)
    return lzma.compress(raw)


class Phase2Bi5Tests(unittest.TestCase):
    def test_decodes_eurusd_field_order_and_scale(self):
        body = make_bi5([(0, 110000, 110010, 109990, 110020, 1.5)])
        frame = decode_bi5_day(RawChunkKey("EURUSD", "BID", date(2024, 1, 2)), body)
        self.assertEqual(frame["open"].to_list(), [1.10])
        self.assertEqual(frame["close"].to_list(), [1.10010])
        self.assertEqual(frame["low"].to_list(), [1.09990])
        self.assertEqual(frame["high"].to_list(), [1.10020])
        self.assertEqual(frame["timestamp_utc"].to_list()[0], datetime(2024, 1, 2, tzinfo=timezone.utc))

    def test_decodes_usdjpy_with_1000_divisor(self):
        body = make_bi5([(60, 145123, 145130, 145100, 145150, 2.0)])
        frame = decode_bi5_day(RawChunkKey("USDJPY", "ASK", date(2024, 1, 2)), body)
        self.assertAlmostEqual(frame["open"][0], 145.123)

    def test_preserves_zero_price_for_quality_layer(self):
        body = make_bi5([(0, 0, 1, 0, 2, 1.0)])
        frame = decode_bi5_day(RawChunkKey("EURUSD", "BID", date(2024, 1, 2)), body)
        self.assertEqual(frame["open"][0], 0.0)
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```bash
PYTHONPATH=src python -m unittest tests.test_phase2_bi5 -v
```

Expected: FAIL because `fmp.data.phase2.bi5` does not exist.

- [ ] **Step 3: Pin Polars and make CI install project dependencies**

`pyproject.toml`:

```toml
dependencies = ["polars==1.44.2"]
```

Add before workflow validation/tests:

```yaml
- name: Install package
  run: python -m pip install -e .
```

- [ ] **Step 4: Implement the minimal decoder**

```python
# src/fmp/data/phase2/bi5.py
_RECORD = struct.Struct(">IIIIIf")

class Phase2DecodeError(ValueError):
    pass


def decode_bi5_day(key: RawChunkKey, body: bytes) -> pl.DataFrame:
    try:
        payload = lzma.decompress(body)
    except lzma.LZMAError as exc:
        raise Phase2DecodeError("invalid BI5 LZMA payload") from exc
    if not payload or len(payload) % _RECORD.size:
        raise Phase2DecodeError("BI5 payload is not a non-zero multiple of 24 bytes")
    divisor = PRICE_DIVISORS[key.pair]
    rows = []
    previous = -1
    day_start = datetime.combine(key.day, time.min, tzinfo=timezone.utc)
    for offset in range(0, len(payload), _RECORD.size):
        seconds, open_i, close_i, low_i, high_i, volume = _RECORD.unpack_from(payload, offset)
        if seconds >= 86400 or seconds <= previous:
            raise Phase2DecodeError("BI5 second offsets must be strictly increasing within the UTC day")
        previous = seconds
        rows.append((day_start + timedelta(seconds=seconds), key.pair, key.side,
                     open_i / divisor, high_i / divisor, low_i / divisor,
                     close_i / divisor, float(volume)))
    return pl.DataFrame(rows, schema=DECODED_SIDE_SCHEMA, orient="row")
```

- [ ] **Step 5: Add structural failure tests**

Cover invalid LZMA, non-24-byte payload, duplicate/non-increasing offsets, out-of-day offsets, stable column order, and preservation of non-finite/abnormal numeric quote values.

- [ ] **Step 6: Run focused tests and full existing suite**

```bash
PYTHONPATH=src python -m unittest tests.test_phase2_bi5 -v
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests
ruby scripts/validate_workflow_yaml.rb .github/workflows
```

Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .github/workflows/tests.yml src/fmp/data/phase2 tests/test_phase2_bi5.py
git commit -m "feat: add Phase 2 BI5 decoder"
```

---

### Task 2: Verified local raw reader and canonical BID/ASK normalization

**Files:**
- Create: `src/fmp/data/phase2/raw_reader.py`
- Create: `src/fmp/data/phase2/normalize.py`
- Create: `tests/test_phase2_normalize.py`

**Interfaces:**
- Produces protocol `RawChunkReader.read(key: RawChunkKey) -> bytes | None`.
- Produces `LocalRawChunkReader(root: Path)` that verifies the Phase 1 manifest, SHA-256, and byte size before returning raw bytes; valid `not_found` returns `None`.
- Produces `normalize_decoded_sides(bid: pl.DataFrame | None, ask: pl.DataFrame | None) -> pl.DataFrame`.
- Produces `normalize_day(reader: RawChunkReader, pair: Pair, day: date) -> pl.DataFrame`.
- Canonical output column order exactly matches the approved schema.

- [ ] **Step 1: Write failing normalization tests**

```python
class Phase2NormalizeTests(unittest.TestCase):
    def test_outer_join_preserves_one_sided_minute(self):
        bid = decoded_side("BID", ["00:00", "00:01"])
        ask = decoded_side("ASK", ["00:00"])
        out = normalize_decoded_sides(bid, ask)
        self.assertEqual(out.height, 2)
        self.assertIsNone(out.filter(pl.col("timestamp_utc") == minute_1)["ask_open"][0])

    def test_output_has_stable_schema_and_metadata(self):
        out = normalize_decoded_sides(decoded_bid, decoded_ask)
        self.assertEqual(out.columns, list(CANONICAL_COLUMNS))
        self.assertEqual(out["source"].unique().to_list(), ["dukascopy"])
        self.assertEqual(out["schema_version"].unique().to_list(), [CANONICAL_SCHEMA_VERSION])
```

- [ ] **Step 2: Verify RED**

```bash
PYTHONPATH=src python -m unittest tests.test_phase2_normalize -v
```

Expected: module/function missing.

- [ ] **Step 3: Implement `LocalRawChunkReader` fail-closed verification**

Reuse existing `load_manifest` and `validate_manifest_for_key`. For `complete`, require raw existence, exact manifest SHA-256, and exact `compressed_size_bytes`. For `not_found`, require no raw object and return `None`. Any incomplete/inconsistent local state raises `RawReadError`.

- [ ] **Step 4: Implement normalization**

Rename side-neutral decoded columns to `bid_*` / `ask_*`, outer-join on `timestamp_utc + symbol`, coalesce join keys, append constant metadata, sort by `symbol,timestamp_utc`, and cast to the canonical Polars schema. Do not fill missing quote values.

- [ ] **Step 5: Add reader integrity tests**

Cover valid complete, checksum mismatch, size mismatch, missing manifest, valid `not_found`, and illegal raw beside `not_found`.

- [ ] **Step 6: Run focused/full tests and commit**

```bash
PYTHONPATH=src python -m unittest tests.test_phase2_normalize -v
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests
git add src/fmp/data/phase2 tests/test_phase2_normalize.py
git commit -m "feat: normalize Phase 2 canonical minutes"
```

---

### Task 3: Quality findings, market-week/DST logic, and deterministic reports

**Files:**
- Create: `src/fmp/data/phase2/market_hours.py`
- Create: `src/fmp/data/phase2/quality.py`
- Create: `tests/test_phase2_quality.py`

**Interfaces:**
- Produces `is_market_open_minute(timestamp_utc: datetime) -> bool` using `America/New_York`.
- Produces frozen dataclass `QualityFinding(symbol, timestamp_start_utc, timestamp_end_utc, code, severity, details)`.
- Produces `analyze_quality(frame: pl.DataFrame) -> dict[str, object]` with deterministic serializable report plus finding list.
- Pip scaling for close-spread reports: EURUSD/GBPUSD ×10,000; USDJPY ×100.
- IQR quartiles use Polars `quantile(..., interpolation="nearest")`; flag strictly above `Q3 + 10*IQR` and use `Q3` when `IQR == 0`.

- [ ] **Step 1: Write failing market-week tests**

Test Sunday 16:59 New York closed, Sunday 17:00 open, Friday 16:59 open, Friday 17:00 closed, plus UTC examples on both sides of US DST spring/fall transitions.

- [ ] **Step 2: Write failing quote-quality tests**

Create tiny canonical frames proving findings for `missing_bid_side`, `missing_ask_side`, side OHLC invalidity, `ask_below_bid`, non-positive prices, and non-finite values while asserting the input frame is unchanged.

- [ ] **Step 3: Write failing continuity/outlier tests**

Use hand-built minutes to prove:
- weekend-only missing span -> `weekend_closure_gap`;
- a 29-minute open-market gap is not `long_weekday_gap`;
- a 30-minute open-market gap is;
- a weekend reopening move is excluded from one-minute jump statistics;
- a constructed extreme close spread and midpoint return exceed the frozen IQR threshold.

- [ ] **Step 4: Verify RED**

```bash
PYTHONPATH=src python -m unittest tests.test_phase2_quality -v
```

- [ ] **Step 5: Implement deterministic quality analysis**

Keep finding order stable by `(timestamp_start_utc, code)`. Report schema/ingestion version, actual range, row counts, one-sided counts, null/anomaly counts, gap summary, spread summary/threshold, and midpoint-return summary/threshold. Never mutate canonical values.

- [ ] **Step 6: Run focused/full tests and commit**

```bash
PYTHONPATH=src python -m unittest tests.test_phase2_quality -v
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests
git add src/fmp/data/phase2 tests/test_phase2_quality.py
git commit -m "feat: add Phase 2 quality analysis"
```

---

### Task 4: Deterministic 5m/15m/1h resampling

**Files:**
- Create: `src/fmp/data/phase2/resample.py`
- Create: `tests/test_phase2_resample.py`

**Interfaces:**
- `Timeframe = Literal["5m", "15m", "1h"]`.
- `resample_canonical(frame: pl.DataFrame, timeframe: Timeframe) -> pl.DataFrame`.
- Output carries side OHLC/volume, `source_minutes`, `expected_open_minutes`, `is_complete`, `timeframe`, and `schema_version="fmp-derived-bars-v1"`.

- [ ] **Step 1: Write exact-boundary failing tests**

Build 1m fixtures around 00:00/00:05/00:15/01:00 UTC and assert first/max/min/last aggregation for BID and ASK independently.

- [ ] **Step 2: Write incomplete-window failing tests**

Assert a window with one missing side/minute remains present with `is_complete=False`; no missing values are filled. Assert a fully populated open-market window is complete.

- [ ] **Step 3: Write Friday-close/Sunday-open and DST tests**

Use `expected_open_minutes` to prove the completeness calculation follows New York market-week rules rather than fixed UTC hours.

- [ ] **Step 4: Implement resampling**

Use UTC-aligned Polars dynamic grouping (`closed="left"`, `label="left"`). For each side use first non-null open, max high, min low, last non-null close, and sum volume only when at least one valid source value exists; otherwise preserve null. Compute expected open minutes deterministically from the market-hours helper.

- [ ] **Step 5: Run focused/full tests and commit**

```bash
PYTHONPATH=src python -m unittest tests.test_phase2_resample -v
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests
git add src/fmp/data/phase2 tests/test_phase2_resample.py
git commit -m "feat: add deterministic Phase 2 resampling"
```

---

### Task 5: Parquet artifacts, processed manifests, and bounded CLI orchestration

**Files:**
- Create: `src/fmp/data/phase2/artifacts.py`
- Create: `src/fmp/data/phase2/phase2_cli.py`
- Modify: `src/fmp/data/cli.py`
- Create: `tests/test_phase2_artifacts_cli.py`
- Modify: `docs/project-state.md`
- Modify: `docs/superpowers/specs/2026-09-13-phase2-canonical-data-design.md`

**Interfaces:**
- `write_parquet_partition(frame, path) -> ArtifactDigest` with stable sort/column order and `compression="zstd", compression_level=3, statistics=True`.
- `sha256_file(path: Path) -> str`.
- `build_processed_manifest(...) -> dict[str, object]` and `write_processed_manifest(...)`.
- CLI additions: `decode-day`, `normalize`, `quality`, `resample`, `process-phase2`.
- Local orchestration consumes `LocalRawChunkReader` only. Cloud/full-history support is intentionally absent from this plan.

- [ ] **Step 1: Write failing Parquet determinism tests**

Write the same stable frame twice to separate files and require same byte size/SHA-256, exact canonical schema after round-trip, and Zstd writer metadata recorded in the processed manifest.

- [ ] **Step 2: Write failing manifest tests**

Require manifest version, canonical/ingestion version, Phase 1 checkpoint name, frozen plan SHA-256 `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`, partition paths, row counts, artifact SHA/size, quality summary, Polars version, writer config, explicit generation timestamp, and optional code commit.

- [ ] **Step 3: Write failing bounded CLI integration tests**

Create a temporary Phase 1-compatible local raw+manifest tree for one pair/day, call `main([...])`, and prove `decode-day`, `normalize`, `quality`, `resample`, and a one-day `process-phase2` produce the expected JSON/Parquet paths without modifying raw bytes.

- [ ] **Step 4: Implement artifact writers and CLI helpers**

Keep Phase 2 transformation logic out of the existing `cli.py`; `cli.py` only registers parser arguments and delegates to `phase2_cli.py`.

- [ ] **Step 5: Update project state/spec status**

Set current phase to `Phase 2 — Validation, Normalization & Derived Bars`, status to `CANONICAL_FOUNDATION_ACTIVE`, and record that this branch implements only the local foundation. Change spec status from `implementation not started` to `IMPLEMENTATION ACTIVE`. Do not mark Phase 2 PASS.

- [ ] **Step 6: Run full verification**

```bash
ruby scripts/validate_workflow_yaml.rb .github/workflows
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests
git diff --check
```

Expected: all green / no diff whitespace errors.

- [ ] **Step 7: Commit**

```bash
git add src/fmp/data/phase2 src/fmp/data/cli.py tests/test_phase2_artifacts_cli.py docs/project-state.md docs/superpowers/specs/2026-09-13-phase2-canonical-data-design.md
git commit -m "feat: complete Phase 2 canonical data foundation"
```

---

### Task 6: Review, CI, merge, and next-plan gate

**Files:**
- No production changes unless review finds a defect.

**Interfaces:**
- Foundation PR must leave Phase 2 open, not PASS.
- Follow-on work begins with a separate plan for authenticated `fmp-raw-read`, accepted golden-chunk verification, and full-history orchestration.

- [ ] **Step 1: Compare branch to current `main`**

Confirm only intended Phase 2 dependency/code/tests/docs/CI-install changes are present and no Phase 1 acquisition workflow/source logic was changed.

- [ ] **Step 2: Open PR**

PR body must list local-foundation scope, TDD evidence, no raw mutation, no full-history processing, and the remaining golden/cloud-reader gate.

- [ ] **Step 3: Wait for PR CI and inspect jobs**

Require workflow YAML validation, unit tests, and compile to pass. Fix failures on the feature branch and rerun verification before merge.

- [ ] **Step 4: Merge only if green**

After merge, verify main CI success and confirm no `phase1-full-acquisition` source-capable run was started by the Phase 2 commits.

- [ ] **Step 5: Start the next design-plan cycle without declaring Phase 2 PASS**

The next implementation plan covers `CloudRawChunkReader`/`fmp-raw-read`, real accepted golden-chunk decoder validation, bounded cloud materialization, then full-history processing. Phase 2 remains open until all three pairs have quantified quality evidence, deterministic derived bars, reproducible processed manifests, and the Phase 2 checkpoint is created.
