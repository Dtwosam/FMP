from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

import polars as pl

from fmp.backtest.costs import pip_size
from fmp.data.phase2.artifacts import write_parquet_partition
from fmp.features.schema import FEATURE_COLUMNS

from .contracts import (
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    HORIZONS_MINUTES,
    MARKET_FEATURE_SET_VERSION,
    MARKET_HISTORY_END_EXCLUSIVE,
    MARKET_HISTORY_START,
    SLIPPAGE_PIPS,
)


MARKET_OUTCOME_SET_VERSION = "fmp-market-outcome-grid-v1"

_OUTCOME_SCENARIO_COLUMNS = tuple(
    column
    for suffix in ("0p2", "0p5", "1p0")
    for column in (
        f"long_net_pips_{suffix}",
        f"short_net_pips_{suffix}",
        f"best_direction_{suffix}",
    )
)

OUTCOME_COLUMNS = (
    "symbol",
    "timeframe",
    "bar_start_utc",
    "available_at_utc",
    "exit_timestamp_utc",
    "horizon_minutes",
    "future_mid_move_pips",
    *_OUTCOME_SCENARIO_COLUMNS,
    "feature_set_version",
    "outcome_set_version",
    "evidence_label",
    "processed_manifest_sha256",
)

OUTCOME_FEATURE_IDENTITY_COLUMNS = (
    "symbol",
    "timeframe",
    "bar_start_utc",
    "available_at_utc",
    "feature_set_version",
    "processed_manifest_sha256",
)

_REQUIRED_QUOTE_COLUMNS = (
    "timestamp_utc",
    "symbol",
    "bid_open",
    "ask_open",
)


@dataclass(frozen=True, slots=True)
class MarketOutcomeGridBuild:
    frame: pl.DataFrame
    source_feature_rows: int
    labeled_rows_by_horizon: Mapping[int, int]
    missing_entry_rows_by_horizon: Mapping[int, int]
    missing_exit_rows_by_horizon: Mapping[int, int]

    @property
    def labeled_rows(self) -> int:
        return self.frame.height


def _validate_sha256(value: str, *, field: str) -> None:
    if len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc


def _validate_feature_identity_frame(
    features: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
) -> None:
    missing = [
        name for name in OUTCOME_FEATURE_IDENTITY_COLUMNS if name not in features.columns
    ]
    if missing:
        raise ValueError(f"market-outcome feature identity is missing columns: {missing}")
    if features.is_empty():
        raise ValueError("market-learning feature frame must not be empty")
    if set(features["symbol"].to_list()) != {symbol}:
        raise ValueError("market-learning feature symbol identity mismatch")
    if set(features["timeframe"].to_list()) != {timeframe}:
        raise ValueError("market-learning feature timeframe identity mismatch")
    if set(features["feature_set_version"].to_list()) != {MARKET_FEATURE_SET_VERSION}:
        raise ValueError("market-learning feature-set identity mismatch")
    processed = set(features["processed_manifest_sha256"].to_list())
    if len(processed) != 1:
        raise ValueError("market-learning feature source manifest identity is not singular")
    _validate_sha256(str(next(iter(processed))), field="processed_manifest_sha256")

    accepted_start = datetime(
        MARKET_HISTORY_START.year,
        MARKET_HISTORY_START.month,
        MARKET_HISTORY_START.day,
        tzinfo=timezone.utc,
    )
    accepted_end = datetime(
        MARKET_HISTORY_END_EXCLUSIVE.year,
        MARKET_HISTORY_END_EXCLUSIVE.month,
        MARKET_HISTORY_END_EXCLUSIVE.day,
        tzinfo=timezone.utc,
    )
    if features.filter(
        (pl.col("available_at_utc") < accepted_start)
        | (pl.col("available_at_utc") >= accepted_end)
    ).height:
        raise ValueError("market-learning features are outside accepted historical coverage")

    unique = features.select(
        pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
    ).item()
    if unique != features.height:
        raise ValueError("duplicate market-learning feature identity")


def _validate_feature_frame(
    features: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
) -> None:
    missing = [name for name in FEATURE_COLUMNS if name not in features.columns]
    if missing:
        raise ValueError(f"market-learning feature frame is missing columns: {missing}")
    if features.is_empty():
        raise ValueError("market-learning feature frame must not be empty")
    if set(features["symbol"].to_list()) != {symbol}:
        raise ValueError("market-learning feature symbol identity mismatch")
    if set(features["timeframe"].to_list()) != {timeframe}:
        raise ValueError("market-learning feature timeframe identity mismatch")
    if set(features["feature_set_version"].to_list()) != {MARKET_FEATURE_SET_VERSION}:
        raise ValueError("market-learning feature-set identity mismatch")
    processed = set(features["processed_manifest_sha256"].to_list())
    if len(processed) != 1:
        raise ValueError("market-learning feature source manifest identity is not singular")
    _validate_sha256(str(next(iter(processed))), field="processed_manifest_sha256")

    accepted_start = datetime(
        MARKET_HISTORY_START.year,
        MARKET_HISTORY_START.month,
        MARKET_HISTORY_START.day,
        tzinfo=timezone.utc,
    )
    accepted_end = datetime(
        MARKET_HISTORY_END_EXCLUSIVE.year,
        MARKET_HISTORY_END_EXCLUSIVE.month,
        MARKET_HISTORY_END_EXCLUSIVE.day,
        tzinfo=timezone.utc,
    )
    if features.filter(
        (pl.col("available_at_utc") < accepted_start)
        | (pl.col("available_at_utc") >= accepted_end)
    ).height:
        raise ValueError("market-learning features are outside accepted historical coverage")

    unique = features.select(
        pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
    ).item()
    if unique != features.height:
        raise ValueError("duplicate market-learning feature identity")


def _validate_quote_frame(quotes: pl.DataFrame, *, symbol: str) -> None:
    missing = [name for name in _REQUIRED_QUOTE_COLUMNS if name not in quotes.columns]
    if missing:
        raise ValueError(f"market-outcome quotes are missing columns: {missing}")
    if quotes.is_empty():
        raise ValueError("market-outcome quote frame must not be empty")
    if set(quotes["symbol"].to_list()) != {symbol}:
        raise ValueError("market-outcome quote symbol identity mismatch")
    if quotes.select(pl.struct(["symbol", "timestamp_utc"]).n_unique()).item() != quotes.height:
        raise ValueError("duplicate market-outcome quote identity")
    invalid = quotes.filter(
        pl.col("bid_open").is_null()
        | pl.col("ask_open").is_null()
        | (pl.col("bid_open") <= 0)
        | (pl.col("ask_open") <= 0)
        | (pl.col("ask_open") < pl.col("bid_open"))
    )
    if invalid.height:
        raise ValueError("market-outcome quote prices are invalid")


def _scenario_suffix(slippage_pips: float) -> str:
    mapping = {0.2: "0p2", 0.5: "0p5", 1.0: "1p0"}
    try:
        return mapping[slippage_pips]
    except KeyError as exc:
        raise ValueError("unsupported market-outcome slippage scenario") from exc


def build_market_outcome_grid(
    features: pl.DataFrame,
    minute_quotes: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
) -> MarketOutcomeGridBuild:
    _validate_feature_frame(features, symbol=symbol, timeframe=timeframe)
    _validate_quote_frame(minute_quotes, symbol=symbol)
    feature_identity = features.select(
        list(OUTCOME_FEATURE_IDENTITY_COLUMNS)
    ).sort(["symbol", "timeframe", "bar_start_utc"])
    return _build_market_outcome_grid_from_validated_identity(
        feature_identity,
        minute_quotes,
        symbol=symbol,
        timeframe=timeframe,
    )


def build_market_outcome_grid_from_identity(
    feature_identity: pl.DataFrame,
    minute_quotes: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
) -> MarketOutcomeGridBuild:
    _validate_feature_identity_frame(
        feature_identity,
        symbol=symbol,
        timeframe=timeframe,
    )
    _validate_quote_frame(minute_quotes, symbol=symbol)
    identity = feature_identity.select(
        list(OUTCOME_FEATURE_IDENTITY_COLUMNS)
    ).sort(["symbol", "timeframe", "bar_start_utc"])
    return _build_market_outcome_grid_from_validated_identity(
        identity,
        minute_quotes,
        symbol=symbol,
        timeframe=timeframe,
    )


def _build_market_outcome_grid_from_validated_identity(
    feature_identity: pl.DataFrame,
    minute_quotes: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
) -> MarketOutcomeGridBuild:
    entry_quotes = minute_quotes.select(
        [
            "symbol",
            pl.col("timestamp_utc").alias("available_at_utc"),
            pl.col("bid_open").alias("entry_bid_open"),
            pl.col("ask_open").alias("entry_ask_open"),
        ]
    )
    exit_quotes = minute_quotes.select(
        [
            "symbol",
            pl.col("timestamp_utc").alias("exit_timestamp_utc"),
            pl.col("bid_open").alias("exit_bid_open"),
            pl.col("ask_open").alias("exit_ask_open"),
        ]
    )

    pip = pip_size(symbol)
    frames: list[pl.DataFrame] = []
    labeled: dict[int, int] = {}
    missing_entry: dict[int, int] = {}
    missing_exit: dict[int, int] = {}

    for horizon in HORIZONS_MINUTES:
        joined = (
            feature_identity.with_columns(
                (
                    pl.col("available_at_utc")
                    + pl.duration(minutes=horizon)
                ).alias("exit_timestamp_utc")
            )
            .join(
                entry_quotes,
                on=["symbol", "available_at_utc"],
                how="left",
            )
            .join(
                exit_quotes,
                on=["symbol", "exit_timestamp_utc"],
                how="left",
            )
        )

        missing_entry_count = joined.filter(pl.col("entry_bid_open").is_null()).height
        missing_exit_count = joined.filter(
            pl.col("entry_bid_open").is_not_null()
            & pl.col("exit_bid_open").is_null()
        ).height
        usable = joined.filter(
            pl.col("entry_bid_open").is_not_null()
            & pl.col("entry_ask_open").is_not_null()
            & pl.col("exit_bid_open").is_not_null()
            & pl.col("exit_ask_open").is_not_null()
        )

        long_base = (
            (pl.col("exit_bid_open") - pl.col("entry_ask_open")) / pl.lit(pip)
        )
        short_base = (
            (pl.col("entry_bid_open") - pl.col("exit_ask_open")) / pl.lit(pip)
        )
        value_expressions: list[pl.Expr] = [
            pl.lit(horizon, dtype=pl.Int64).alias("horizon_minutes"),
            (
                (
                    (pl.col("exit_bid_open") + pl.col("exit_ask_open")) / 2.0
                    - (pl.col("entry_bid_open") + pl.col("entry_ask_open")) / 2.0
                )
                / pl.lit(pip)
            ).alias("future_mid_move_pips"),
        ]
        direction_expressions: list[pl.Expr] = []

        for slippage in SLIPPAGE_PIPS:
            suffix = _scenario_suffix(slippage)
            long_name = f"long_net_pips_{suffix}"
            short_name = f"short_net_pips_{suffix}"
            direction_name = f"best_direction_{suffix}"
            value_expressions.extend(
                [
                    (long_base - pl.lit(2.0 * slippage)).alias(long_name),
                    (short_base - pl.lit(2.0 * slippage)).alias(short_name),
                ]
            )
            direction_expressions.append(
                pl.when(
                    (pl.col(long_name) > 0.0)
                    & (pl.col(long_name) > pl.col(short_name))
                )
                .then(pl.lit("LONG"))
                .when(
                    (pl.col(short_name) > 0.0)
                    & (pl.col(short_name) > pl.col(long_name))
                )
                .then(pl.lit("SHORT"))
                .otherwise(pl.lit("NO_TRADE"))
                .alias(direction_name)
            )

        out = (
            usable.with_columns(value_expressions)
            .with_columns(direction_expressions)
            .with_columns(
                pl.lit(MARKET_OUTCOME_SET_VERSION).alias("outcome_set_version"),
                pl.lit(EVIDENCE_LABEL).alias("evidence_label"),
            )
            .select(list(OUTCOME_COLUMNS))
            .sort(
                [
                    "symbol",
                    "timeframe",
                    "bar_start_utc",
                    "horizon_minutes",
                ]
            )
        )
        frames.append(out)
        labeled[horizon] = out.height
        missing_entry[horizon] = missing_entry_count
        missing_exit[horizon] = missing_exit_count

    for horizon in HORIZONS_MINUTES:
        accounted = (
            labeled[horizon]
            + missing_entry[horizon]
            + missing_exit[horizon]
        )
        if accounted != feature_identity.height:
            raise ValueError("market-outcome horizon row accounting mismatch")

    combined = pl.concat(frames, how="vertical").sort(
        ["symbol", "timeframe", "bar_start_utc", "horizon_minutes"]
    )
    unique = combined.select(
        pl.struct(
            ["symbol", "timeframe", "bar_start_utc", "horizon_minutes"]
        ).n_unique()
    ).item()
    if unique != combined.height:
        raise ValueError("duplicate market-outcome grid identity")

    return MarketOutcomeGridBuild(
        frame=combined,
        source_feature_rows=feature_identity.height,
        labeled_rows_by_horizon=dict(sorted(labeled.items())),
        missing_entry_rows_by_horizon=dict(sorted(missing_entry.items())),
        missing_exit_rows_by_horizon=dict(sorted(missing_exit.items())),
    )


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _schema_sha256(frame: pl.DataFrame) -> str:
    schema = [(name, str(dtype)) for name, dtype in frame.schema.items()]
    return hashlib.sha256(_canonical_json(schema)).hexdigest()


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def write_market_outcome_artifacts(
    *,
    build: MarketOutcomeGridBuild,
    output_root: Path,
    symbol: str,
    timeframe: str,
    code_commit: str,
    feature_manifest_sha256: str,
    feature_evidence_fingerprint: str,
    processed_manifest_sha256: str,
) -> dict[str, object]:
    if build.frame.is_empty():
        raise ValueError("cannot write empty market-outcome grid")
    if tuple(build.frame.columns) != OUTCOME_COLUMNS:
        raise ValueError("market-outcome grid does not match frozen schema")
    if len(code_commit) != 40:
        raise ValueError("code_commit must be a 40-character Git commit")
    try:
        int(code_commit, 16)
    except ValueError as exc:
        raise ValueError("code_commit must be hexadecimal") from exc
    _validate_sha256(feature_manifest_sha256, field="feature_manifest_sha256")
    _validate_sha256(
        feature_evidence_fingerprint,
        field="feature_evidence_fingerprint",
    )
    _validate_sha256(
        processed_manifest_sha256,
        field="processed_manifest_sha256",
    )
    if set(build.frame["symbol"].to_list()) != {symbol}:
        raise ValueError("market-outcome output symbol identity mismatch")
    if set(build.frame["timeframe"].to_list()) != {timeframe}:
        raise ValueError("market-outcome output timeframe identity mismatch")
    if set(build.frame["feature_set_version"].to_list()) != {
        MARKET_FEATURE_SET_VERSION
    }:
        raise ValueError("market-outcome feature-set identity mismatch")
    if set(build.frame["outcome_set_version"].to_list()) != {
        MARKET_OUTCOME_SET_VERSION
    }:
        raise ValueError("market-outcome set identity mismatch")
    if set(build.frame["evidence_label"].to_list()) != {EVIDENCE_LABEL}:
        raise ValueError("market-outcome evidence label mismatch")
    if set(build.frame["processed_manifest_sha256"].to_list()) != {
        processed_manifest_sha256
    }:
        raise ValueError("market-outcome Phase 2 identity mismatch")

    accepted_end = datetime(
        MARKET_HISTORY_END_EXCLUSIVE.year,
        MARKET_HISTORY_END_EXCLUSIVE.month,
        MARKET_HISTORY_END_EXCLUSIVE.day,
        tzinfo=timezone.utc,
    )
    if build.frame.filter(pl.col("exit_timestamp_utc") >= accepted_end).height:
        raise ValueError("market-outcome targets extend beyond accepted history")
    for horizon in HORIZONS_MINUTES:
        if (
            build.labeled_rows_by_horizon.get(horizon, 0)
            + build.missing_entry_rows_by_horizon.get(horizon, 0)
            + build.missing_exit_rows_by_horizon.get(horizon, 0)
            != build.source_feature_rows
        ):
            raise ValueError("market-outcome manifest row accounting mismatch")

    root = Path(output_root)
    artifacts: list[dict[str, object]] = []
    month_pairs = (
        build.frame.select(
            pl.col("bar_start_utc").dt.year().alias("year"),
            pl.col("bar_start_utc").dt.month().alias("month"),
        )
        .unique()
        .sort(["year", "month"])
        .rows()
    )
    for year, month in month_pairs:
        monthly = build.frame.filter(
            (pl.col("bar_start_utc").dt.year() == year)
            & (pl.col("bar_start_utc").dt.month() == month)
        ).sort(
            [
                "symbol",
                "timeframe",
                "bar_start_utc",
                "horizon_minutes",
            ]
        )
        relative = (
            Path("data")
            / "market-outcomes"
            / MARKET_OUTCOME_SET_VERSION
            / symbol
            / timeframe
            / f"{year:04d}"
            / f"{month:02d}.parquet"
        )
        digest = write_parquet_partition(monthly, root / relative)
        artifacts.append(
            {
                "path": relative.as_posix(),
                "sha256": digest.sha256,
                "size_bytes": digest.size_bytes,
                "row_count": digest.row_count,
            }
        )

    frame = build.frame
    manifest: dict[str, object] = {
        "manifest_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "code_commit": code_commit,
        "feature_manifest_sha256": feature_manifest_sha256,
        "feature_evidence_fingerprint": feature_evidence_fingerprint,
        "processed_manifest_sha256": processed_manifest_sha256,
        "symbol": symbol,
        "timeframe": timeframe,
        "horizons_minutes": list(HORIZONS_MINUTES),
        "slippage_pips_per_fill": list(SLIPPAGE_PIPS),
        "source_feature_rows": build.source_feature_rows,
        "labeled_rows": build.labeled_rows,
        "labeled_rows_by_horizon": {
            str(key): value for key, value in build.labeled_rows_by_horizon.items()
        },
        "missing_entry_rows_by_horizon": {
            str(key): value
            for key, value in build.missing_entry_rows_by_horizon.items()
        },
        "missing_exit_rows_by_horizon": {
            str(key): value
            for key, value in build.missing_exit_rows_by_horizon.items()
        },
        "output_start_utc": _iso(frame["available_at_utc"][0]),
        "output_end_utc": _iso(frame["exit_timestamp_utc"][-1]),
        "schema_columns": list(OUTCOME_COLUMNS),
        "schema_sha256": _schema_sha256(frame),
        "artifacts": artifacts,
    }
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "manifest.json"
    payload = json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing market-outcome manifest: {manifest_path}")
    manifest_path.write_text(payload, encoding="utf-8")
    return manifest


__all__ = [
    "MARKET_OUTCOME_SET_VERSION",
    "OUTCOME_COLUMNS",
    "OUTCOME_FEATURE_IDENTITY_COLUMNS",
    "MarketOutcomeGridBuild",
    "build_market_outcome_grid",
    "build_market_outcome_grid_from_identity",
    "write_market_outcome_artifacts",
]
