from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping, Sequence

import polars as pl

from fmp.contracts import Direction, QuoteBar
from fmp.features.schema import FEATURE_COLUMNS, FEATURE_VALUE_COLUMNS
from fmp.research.contracts import ResearchSplit
from fmp.strategies.contracts import SignalCandidate
from fmp.strategies.session_breakout import (
    SessionBreakoutConfig,
    generate_session_breakout_candidates,
)
from fmp.strategies.volatility_breakout import (
    VolatilityBreakoutConfig,
    generate_volatility_breakout_candidates,
)

from .contracts import (
    FEATURE_SET_VERSION,
    FINAL_START,
    FROZEN_STRATEGIES,
    PHASE5_CHECKPOINT_SHA,
    USDJPY_PROCESSED_MANIFEST_SHA256,
    FrozenStrategySpec,
)


PHASE5_FEATURE_IMPLEMENTATION_SHA = "74dce1b945ad31a05416a4fc9e63443a884cb90c"
MODEL_INPUT_COLUMNS = FEATURE_VALUE_COLUMNS + ("signal_direction",)
_SOURCE_START = date(2015, 1, 1)
_JOIN_IDENTITY_COLUMNS = (
    "candidate_id",
    "symbol",
    "observation_bar_timestamp_utc",
    "signal_known_timestamp_utc",
    "stop_price",
    "target_price",
    "latest_exit_timestamp_utc",
    "reason_code",
)


@dataclass(frozen=True, slots=True)
class LoadedModelFeatures:
    frame: pl.DataFrame
    feature_manifest_sha256: str
    processed_manifest_sha256: str
    phase5_checkpoint_sha: str
    phase5_code_commit: str
    opened_artifacts: tuple[str, ...]


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _schema_sha256(frame: pl.DataFrame) -> str:
    schema = [(name, str(dtype)) for name, dtype in frame.schema.items()]
    return hashlib.sha256(_canonical_json(schema)).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json_bytes(path: Path) -> tuple[Mapping[str, object], bytes]:
    try:
        raw = Path(path).read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read Phase 5 feature manifest: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("Phase 5 feature manifest root must be an object")
    return value, raw


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def _parse_feature_artifact_path(
    *,
    root: Path,
    raw_path: str,
    strategy: FrozenStrategySpec,
) -> tuple[Path, date, date]:
    root_resolved = root.resolve()
    candidate = (root / raw_path).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError("Phase 5 feature artifact path escapes feature root") from exc

    parts = PurePosixPath(raw_path).parts
    expected_prefix = (
        "data",
        "features",
        FEATURE_SET_VERSION,
        strategy.symbol,
        strategy.timeframe,
    )
    if len(parts) != 7 or tuple(parts[:5]) != expected_prefix:
        raise ValueError("Phase 5 feature artifact path violates frozen layout")
    year_text, filename = parts[5], parts[6]
    if not filename.endswith(".parquet"):
        raise ValueError("Phase 5 feature artifact path must end in .parquet")
    month_text = filename[:-8]
    try:
        year = int(year_text)
        month = int(month_text)
        start, end = _month_bounds(year, month)
    except ValueError as exc:
        raise ValueError("Phase 5 feature artifact path has invalid year/month") from exc
    if start >= FINAL_START:
        raise ValueError("final-test lock: Phase 5 feature artifact reaches 2024-01-01 or later")
    return candidate, start, end


def _validate_split_before_io(split: ResearchSplit) -> None:
    if split.start < _SOURCE_START:
        raise ValueError("Phase 6 source may not start before 2015-01-01")
    if split.end_exclusive > FINAL_START:
        raise ValueError("final-test lock: Phase 6 source may not reach 2024-01-01 or later")


def load_phase6_feature_frame(
    *,
    feature_root: Path,
    feature_manifest_path: Path,
    strategy: FrozenStrategySpec,
    split: ResearchSplit,
    parquet_reader: Callable[[Path], pl.DataFrame] = pl.read_parquet,
) -> LoadedModelFeatures:
    """Load a verified pre-2024 Phase 5 feature frame for one frozen strategy."""
    _validate_split_before_io(split)
    if strategy.symbol != "USDJPY":
        raise ValueError("Phase 6 V1 accepts only the frozen USDJPY strategies")

    manifest, raw_manifest = _load_json_bytes(Path(feature_manifest_path))
    version = manifest.get("manifest_version")
    if version != 1 or isinstance(version, bool):
        raise ValueError("Phase 5 feature manifest version must be exact integer 1")
    if manifest.get("feature_set_version") != FEATURE_SET_VERSION:
        raise ValueError("Phase 5 feature-set identity mismatch")
    if manifest.get("code_commit") != PHASE5_FEATURE_IMPLEMENTATION_SHA:
        raise ValueError("Phase 5 code/checkpoint provenance mismatch")
    if manifest.get("processed_manifest_sha256") != USDJPY_PROCESSED_MANIFEST_SHA256:
        raise ValueError("Phase 5 processed manifest identity mismatch")
    if manifest.get("symbol") != strategy.symbol:
        raise ValueError("Phase 5 feature manifest symbol mismatch")
    if manifest.get("timeframe") != strategy.timeframe:
        raise ValueError("Phase 5 feature manifest timeframe mismatch")
    if tuple(manifest.get("feature_columns", ())) != FEATURE_VALUE_COLUMNS:
        raise ValueError("Phase 5 feature manifest feature-column identity mismatch")
    if tuple(manifest.get("schema_columns", ())) != FEATURE_COLUMNS:
        raise ValueError("Phase 5 feature manifest schema-column identity mismatch")

    generation = manifest.get("generation_parameters")
    if not isinstance(generation, Mapping):
        raise ValueError("Phase 5 feature manifest generation parameters are missing")
    if generation.get("requested_start") != "2015-01-01":
        raise ValueError("Phase 5 feature manifest source start identity mismatch")
    if generation.get("requested_end_exclusive") != "2024-01-01":
        raise ValueError("Phase 5 feature manifest source end identity mismatch")
    opened_source_months = manifest.get("opened_source_months")
    if not isinstance(opened_source_months, list) or any(
        not isinstance(month, str) or month >= "2024-01" for month in opened_source_months
    ):
        raise ValueError("final-test lock: Phase 5 manifest opened source months reach 2024+")
    if manifest.get("row_count") != manifest.get("unique_key_count"):
        raise ValueError("Phase 5 feature manifest does not certify unique output keys")

    raw_artifacts = manifest.get("artifacts")
    if not isinstance(raw_artifacts, list) or not raw_artifacts:
        raise ValueError("Phase 5 feature manifest artifacts must be a non-empty list")
    selected: list[tuple[date, Path, str, Mapping[str, object]]] = []
    seen_months: set[date] = set()
    for raw_record in raw_artifacts:
        if not isinstance(raw_record, Mapping):
            raise ValueError("Phase 5 feature artifact record must be an object")
        raw_path = raw_record.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError("Phase 5 feature artifact path is missing")
        path, month_start, month_end = _parse_feature_artifact_path(
            root=Path(feature_root), raw_path=raw_path, strategy=strategy
        )
        if month_start in seen_months:
            raise ValueError("duplicate Phase 5 feature artifact month")
        seen_months.add(month_start)
        if month_end <= split.start or month_start >= split.end_exclusive:
            continue
        selected.append((month_start, path, raw_path, raw_record))
    selected.sort(key=lambda item: item[0])
    if not selected:
        raise ValueError(f"no Phase 5 feature artifacts overlap Phase 6 split {split.name!r}")

    verified: list[tuple[Path, str, Mapping[str, object]]] = []
    for _, path, raw_path, record in selected:
        if not path.is_file():
            raise ValueError(f"Phase 5 feature artifact file is missing: {raw_path}")
        expected_size = record.get("size_bytes")
        if not isinstance(expected_size, int) or isinstance(expected_size, bool):
            raise ValueError("Phase 5 feature artifact size metadata is invalid")
        if path.stat().st_size != expected_size:
            raise ValueError(f"Phase 5 feature artifact size mismatch: {raw_path}")
        expected_sha = record.get("sha256")
        if not isinstance(expected_sha, str) or _sha256_file(path) != expected_sha:
            raise ValueError(f"Phase 5 feature artifact checksum/sha mismatch: {raw_path}")
        verified.append((path, raw_path, record))

    frames: list[pl.DataFrame] = []
    for path, raw_path, record in verified:
        frame = parquet_reader(path)
        expected_rows = record.get("row_count")
        if not isinstance(expected_rows, int) or isinstance(expected_rows, bool):
            raise ValueError("Phase 5 feature artifact row-count metadata is invalid")
        if frame.height != expected_rows:
            raise ValueError(f"Phase 5 feature artifact row-count mismatch: {raw_path}")
        frames.append(frame)
    frame = pl.concat(frames, how="vertical") if len(frames) > 1 else frames[0]

    if tuple(frame.columns) != FEATURE_COLUMNS:
        raise ValueError("Phase 5 feature frame does not match the frozen schema")
    if _schema_sha256(frame) != manifest.get("schema_sha256"):
        raise ValueError("Phase 5 feature frame schema sha mismatch")
    if set(frame["symbol"].to_list()) != {strategy.symbol}:
        raise ValueError("Phase 5 feature frame symbol mismatch")
    if set(frame["timeframe"].to_list()) != {strategy.timeframe}:
        raise ValueError("Phase 5 feature frame timeframe mismatch")
    if set(frame["feature_set_version"].to_list()) != {FEATURE_SET_VERSION}:
        raise ValueError("Phase 5 feature frame feature-set identity mismatch")
    if set(frame["processed_manifest_sha256"].to_list()) != {
        USDJPY_PROCESSED_MANIFEST_SHA256
    }:
        raise ValueError("Phase 5 feature frame processed manifest identity mismatch")

    unique_count = frame.select(
        pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
    ).item()
    if unique_count != frame.height:
        raise ValueError("duplicate Phase 5 feature key; unique identity required")
    keys = frame.select(["symbol", "timeframe", "bar_start_utc"]).rows()
    if keys != sorted(keys, key=lambda row: (row[2], row[0], row[1])):
        raise ValueError("Phase 5 feature keys are not monotonic/sorted")

    boundary = datetime(FINAL_START.year, FINAL_START.month, FINAL_START.day, tzinfo=timezone.utc)
    if frame.filter(
        (pl.col("bar_start_utc") >= boundary)
        | (pl.col("bar_end_utc") >= boundary)
        | (pl.col("available_at_utc") >= boundary)
    ).height:
        raise ValueError("final-test lock: loaded Phase 5 feature rows reach 2024-01-01")

    start_utc = datetime(split.start.year, split.start.month, split.start.day, tzinfo=timezone.utc)
    end_utc = datetime(
        split.end_exclusive.year,
        split.end_exclusive.month,
        split.end_exclusive.day,
        tzinfo=timezone.utc,
    )
    scoped = frame.filter(
        (pl.col("bar_start_utc") >= start_utc) & (pl.col("bar_start_utc") < end_utc)
    )
    if scoped.is_empty():
        raise ValueError(f"Phase 6 feature split {split.name!r} is empty")

    return LoadedModelFeatures(
        frame=scoped,
        feature_manifest_sha256=hashlib.sha256(raw_manifest).hexdigest(),
        processed_manifest_sha256=USDJPY_PROCESSED_MANIFEST_SHA256,
        phase5_checkpoint_sha=PHASE5_CHECKPOINT_SHA,
        phase5_code_commit=PHASE5_FEATURE_IMPLEMENTATION_SHA,
        opened_artifacts=tuple(raw_path for _, raw_path, _ in verified),
    )


def generate_frozen_candidates(
    strategy_id: str,
    bars: Sequence[QuoteBar],
) -> tuple[SignalCandidate, ...]:
    try:
        strategy = FROZEN_STRATEGIES[strategy_id]
    except KeyError as exc:
        raise ValueError(f"unsupported frozen Phase 6 strategy: {strategy_id!r}") from exc

    if strategy_id == "session_breakout":
        config = SessionBreakoutConfig(
            buffer_pips=int(strategy.parameters["buffer_pips"]),
            target_range_multiple=float(strategy.parameters["target_range_multiple"]),
            timeframe=strategy.timeframe,
        )
        return generate_session_breakout_candidates(bars, config=config)
    if strategy_id == "volatility_breakout":
        if float(strategy.parameters["target_r"]) != 1.0:
            raise ValueError("frozen volatility-breakout target must remain exactly 1.0R")
        config = VolatilityBreakoutConfig(
            range_multiplier=float(strategy.parameters["range_multiplier"]),
            timeframe=strategy.timeframe,
        )
        return generate_volatility_breakout_candidates(bars, config=config)
    raise ValueError(f"unsupported frozen Phase 6 strategy: {strategy_id!r}")


def join_directional_candidates_to_features(
    candidates: Sequence[SignalCandidate],
    features: LoadedModelFeatures,
) -> pl.DataFrame:
    directional = [
        candidate
        for candidate in candidates
        if candidate.direction in {Direction.LONG, Direction.SHORT}
    ]
    if not directional:
        return pl.DataFrame()
    ids = [candidate.candidate_id for candidate in directional]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate directional Phase 6 candidate id")

    frame = features.frame
    if tuple(frame.columns) != FEATURE_COLUMNS:
        raise ValueError("Phase 6 join requires the exact frozen Phase 5 feature schema")
    if frame.select(pl.col("bar_start_utc").n_unique()).item() != frame.height:
        raise ValueError("Phase 6 join requires unique feature observation timestamps")
    by_timestamp = {
        row["bar_start_utc"]: row
        for row in frame.to_dicts()
    }
    boundary = datetime(FINAL_START.year, FINAL_START.month, FINAL_START.day, tzinfo=timezone.utc)
    rows: list[dict[str, object]] = []
    for candidate in sorted(
        directional,
        key=lambda item: (item.observation_bar_timestamp_utc, item.candidate_id),
    ):
        if candidate.symbol != "USDJPY":
            raise ValueError("Phase 6 candidate symbol must remain USDJPY")
        timestamps = (
            candidate.observation_bar_timestamp_utc,
            candidate.signal_known_timestamp_utc,
            candidate.latest_exit_timestamp_utc,
        )
        if any(value is not None and value >= boundary for value in timestamps):
            raise ValueError("final-test lock: Phase 6 candidate timestamp reaches 2024-01-01")
        feature = by_timestamp.get(candidate.observation_bar_timestamp_utc)
        if feature is None:
            raise ValueError(f"missing Phase 5 feature row for candidate {candidate.candidate_id}")
        if feature["available_at_utc"] != candidate.signal_known_timestamp_utc:
            raise ValueError(
                f"feature available time does not equal signal known time for {candidate.candidate_id}"
            )
        if feature["feature_set_version"] != FEATURE_SET_VERSION:
            raise ValueError("Phase 6 join feature-set identity mismatch")
        if feature["processed_manifest_sha256"] != USDJPY_PROCESSED_MANIFEST_SHA256:
            raise ValueError("Phase 6 join processed-manifest identity mismatch")
        if feature["symbol"] != candidate.symbol:
            raise ValueError("Phase 6 candidate/feature symbol mismatch")

        row: dict[str, object] = {
            "candidate_id": candidate.candidate_id,
            "symbol": candidate.symbol,
            "observation_bar_timestamp_utc": candidate.observation_bar_timestamp_utc,
            "signal_known_timestamp_utc": candidate.signal_known_timestamp_utc,
            "stop_price": candidate.stop_price,
            "target_price": candidate.target_price,
            "latest_exit_timestamp_utc": candidate.latest_exit_timestamp_utc,
            "reason_code": candidate.reason_code,
        }
        for name in FEATURE_VALUE_COLUMNS:
            row[name] = feature[name]
        row["signal_direction"] = 1 if candidate.direction is Direction.LONG else -1
        rows.append(row)

    result = pl.DataFrame(rows).select([*_JOIN_IDENTITY_COLUMNS, *MODEL_INPUT_COLUMNS])
    return result
