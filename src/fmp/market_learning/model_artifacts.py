from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

import polars as pl

from fmp.features.schema import FEATURE_COLUMNS

from .contracts import (
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    MARKET_FEATURE_SET_VERSION,
)
from .model_protocol import (
    MODEL_CELLS,
    MODEL_PROTOCOL_DECISION,
    MODEL_PROTOCOL_VERSION,
    ModelCell,
    protocol_fingerprint,
)
from .model_training import (
    MODEL_TRAINING_CORE_DECISION,
    MODEL_TRAINING_CORE_VERSION,
    run_model_cell_core,
)
from .outcomes import (
    MARKET_OUTCOME_SET_VERSION,
    OUTCOME_COLUMNS,
)


MODEL_ARTIFACT_RUNNER_VERSION = "fmp-exp044-model-artifact-runner-v1"
MODEL_ARTIFACT_RUNNER_DECISION = "DEC-091"

AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED = False

AUTHORITATIVE_TRAINING_CORE_COMMIT = (
    "640274df9dcbefa0feee599bffdeb63a581db780"
)
AUTHORITATIVE_PROTOCOL_COMMIT = (
    "a9305ba9c42b7224e5d4b3f7d26f268447cdf469"
)
AUTHORITATIVE_PROTOCOL_FINGERPRINT = (
    "1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605"
)

AUTHORITATIVE_FEATURE_RUN_ID = 35867307338
AUTHORITATIVE_FEATURE_CODE_COMMIT = (
    "b71912e254d2a597c0ef55b5e1b3b87b052039ea"
)
AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID = 10753455784
AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT = (
    "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815"
)

AUTHORITATIVE_OUTCOME_RUN_ID = 35876715434
AUTHORITATIVE_OUTCOME_CODE_COMMIT = (
    "edeb43bb4de88923e3349caa8ace36350839ccb8"
)
AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID = 10758027876
AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT = (
    "b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117"
)
AUTHORITATIVE_READINESS_ARTIFACT_ID = 10757578276
AUTHORITATIVE_READINESS_FINGERPRINT = (
    "412573f505ec7912ff934cc6338cf4591b604e0beddb2cb6abb79447c777b105"
)

AUTHORITATIVE_CELL_ARTIFACT_COUNT = 140

AUTHORITATIVE_FEATURE_ARTIFACTS: Mapping[tuple[str, str], Mapping[str, object]] = {
    ("EURUSD", "5m"): {
        "artifact_id": 10752009633,
        "digest": "sha256:a466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2",
    },
    ("EURUSD", "15m"): {
        "artifact_id": 10753305695,
        "digest": "sha256:a942b0bf97995cd67e94335435ab3c06ee0da7688f5ac494b79470c1c637b4ee",
    },
    ("EURUSD", "1h"): {
        "artifact_id": 10753555531,
        "digest": "sha256:831a1957519714933cc34c12fe126a88aeaf7fa9a359be6399b8569a236ee59e",
    },
    ("GBPUSD", "5m"): {
        "artifact_id": 10753690116,
        "digest": "sha256:62bb96d9492fa092cd5aa157223be34dab6c78fb20e381a4d7804adbcec22498",
    },
    ("GBPUSD", "15m"): {
        "artifact_id": 10753680126,
        "digest": "sha256:c5d894f595e85f84670ac66348b0fb40366a80286408c8c1b777549a5dffdc84",
    },
    ("GBPUSD", "1h"): {
        "artifact_id": 10753440747,
        "digest": "sha256:f7c66064a0255585ecf5e4eca6da86bbea3eee58d38bbf9aaeecd04748a8f6f8",
    },
    ("USDJPY", "5m"): {
        "artifact_id": 10752846673,
        "digest": "sha256:d719b40919b1edf1f868352c19579f30528232387df3862c7f85782d8a2a7360",
    },
    ("USDJPY", "15m"): {
        "artifact_id": 10753781465,
        "digest": "sha256:5fdec186a2e086e725623682fd8143294d941635a780038070904e15ed2a4a92",
    },
    ("USDJPY", "1h"): {
        "artifact_id": 10752752044,
        "digest": "sha256:bc8936d2a02bfc6cde9d11eae23330bfc047374f03fe265ed15eaa6d4d0bd3b4",
    },
}

AUTHORITATIVE_OUTCOME_ARTIFACTS: Mapping[tuple[str, str], Mapping[str, object]] = {
    ("EURUSD", "5m"): {
        "artifact_id": 10759485253,
        "digest": "sha256:243824ecfb365a94dbe49442352440ffc3730240b4ca9758b0b94d8e6224534b",
    },
    ("EURUSD", "15m"): {
        "artifact_id": 10759375276,
        "digest": "sha256:dca7f656c08e7b35c51e3549cdcaf92849b2905d70cbeecc5ff1ed3773eeedd0",
    },
    ("EURUSD", "1h"): {
        "artifact_id": 10759490258,
        "digest": "sha256:4594975177b8f7b0ff2979ddba85b774d55b65afe3da61491226dc0bb6f1eaf4",
    },
    ("GBPUSD", "5m"): {
        "artifact_id": 10759375400,
        "digest": "sha256:69b5a774707fe1bf26e271ad6a89084f22169a9155dc5debcbf5d00c00a2fdf4",
    },
    ("GBPUSD", "15m"): {
        "artifact_id": 10759695313,
        "digest": "sha256:a04e9a5ffa5faaf8200385fe7a71bf1d9a56aba3021d60bae25c247b537c365f",
    },
    ("GBPUSD", "1h"): {
        "artifact_id": 10759645383,
        "digest": "sha256:b2a192ceca9031dc2460194db698318a04b99df9f346b4c32c8e9ba7803d4f49",
    },
    ("USDJPY", "5m"): {
        "artifact_id": 10757827671,
        "digest": "sha256:42794311c61189b95a130efafab50cc2c9586d00761e053727f7a05ecd66e36f",
    },
    ("USDJPY", "15m"): {
        "artifact_id": 10757812657,
        "digest": "sha256:edc30a8f49b072e6504a82ae0d90d30a1a362b4dd825bf48d0ed1d2b567af2be",
    },
    ("USDJPY", "1h"): {
        "artifact_id": 10757692733,
        "digest": "sha256:aa7fda1ca6e43c3b41a2ee1fb3729de61bb7dc6ea55e98fda70e8434770a8ee4",
    },
}


@dataclass(frozen=True, slots=True)
class VerifiedCellArtifacts:
    symbol: str
    timeframe: str
    feature_frame: pl.DataFrame
    outcome_frame: pl.DataFrame
    feature_manifest_sha256: str
    outcome_manifest_sha256: str
    processed_manifest_sha256: str


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _schema_sha256(frame: pl.DataFrame) -> str:
    schema = [(name, str(dtype)) for name, dtype in frame.schema.items()]
    return _sha256_bytes(_canonical_json(schema))


def _read_manifest(root: Path) -> tuple[dict[str, object], str]:
    manifest_path = Path(root) / "manifest.json"
    try:
        raw = manifest_path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"cannot read EXP-044 cell manifest: {manifest_path}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("EXP-044 cell manifest root must be an object")
    return value, _sha256_bytes(raw)


def _safe_artifact_path(root: Path, relative: object) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("EXP-044 manifest artifact path must be non-empty")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("EXP-044 manifest artifact path is unsafe")
    resolved_root = Path(root).resolve()
    resolved = (Path(root) / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("EXP-044 manifest artifact path escapes root") from exc
    return resolved


def _load_partitioned_frame(
    *,
    root: Path,
    manifest: Mapping[str, object],
    expected_columns: Sequence[str],
    expected_artifact_count: int,
) -> pl.DataFrame:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("EXP-044 cell manifest artifacts must be a list")
    if len(artifacts) != expected_artifact_count:
        raise ValueError(
            "EXP-044 cell artifact count mismatch: "
            f"expected {expected_artifact_count}, got {len(artifacts)}"
        )

    paths: list[Path] = []
    relative_paths: list[str] = []
    total_rows = 0
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-044 cell manifest artifact row is malformed")

        relative = raw.get("path")
        path = _safe_artifact_path(Path(root), relative)
        if not path.is_file():
            raise ValueError(f"missing EXP-044 cell parquet artifact: {relative}")

        expected_sha = _validate_sha256(
            raw.get("sha256"),
            field="EXP-044 partition sha256",
        )
        if _sha256_file(path) != expected_sha:
            raise ValueError(f"EXP-044 partition sha256 mismatch: {relative}")

        size = raw.get("size_bytes")
        if (
            not isinstance(size, int)
            or isinstance(size, bool)
            or size <= 0
            or path.stat().st_size != size
        ):
            raise ValueError(f"EXP-044 partition size mismatch: {relative}")

        row_count = raw.get("row_count")
        if (
            not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count <= 0
        ):
            raise ValueError(f"EXP-044 partition row count is invalid: {relative}")

        partition = pl.read_parquet(path)
        if tuple(partition.columns) != tuple(expected_columns):
            raise ValueError(
                f"EXP-044 partition schema columns mismatch: {relative}"
            )
        if partition.height != row_count:
            raise ValueError(f"EXP-044 partition row count mismatch: {relative}")

        relative_paths.append(str(relative))
        paths.append(path)
        total_rows += row_count

    if relative_paths != sorted(relative_paths):
        raise ValueError("EXP-044 cell artifact paths must be sorted")
    if len(set(relative_paths)) != len(relative_paths):
        raise ValueError("EXP-044 cell artifact paths must be unique")

    frame = pl.concat(
        [pl.read_parquet(path) for path in paths],
        how="vertical",
    )
    if frame.height != total_rows:
        raise ValueError("EXP-044 concatenated partition row count mismatch")
    return frame


def _validate_common_manifest(
    manifest: Mapping[str, object],
    *,
    symbol: str,
    timeframe: str,
    expected_code_commit: str,
) -> str:
    if manifest.get("manifest_version") != 1:
        raise ValueError("EXP-044 cell manifest version mismatch")
    if manifest.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("EXP-044 cell experiment identity mismatch")
    if manifest.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError("EXP-044 cell evidence label mismatch")
    if manifest.get("symbol") != symbol:
        raise ValueError("EXP-044 cell symbol mismatch")
    if manifest.get("timeframe") != timeframe:
        raise ValueError("EXP-044 cell timeframe mismatch")
    if manifest.get("code_commit") != expected_code_commit:
        raise ValueError("EXP-044 cell code commit mismatch")
    if manifest.get("promotion_authorized") is not False:
        raise ValueError("EXP-044 cell promotion authorization must remain false")
    return _validate_sha256(
        manifest.get("processed_manifest_sha256"),
        field="EXP-044 processed manifest sha256",
    )


def load_verified_feature_cell(
    *,
    root: Path,
    symbol: str,
    timeframe: str,
    expected_manifest_sha256: str,
    expected_processed_manifest_sha256: str,
    expected_row_count: int,
    expected_code_commit: str,
    expected_artifact_count: int = AUTHORITATIVE_CELL_ARTIFACT_COUNT,
) -> tuple[pl.DataFrame, Mapping[str, object]]:
    manifest, manifest_sha = _read_manifest(Path(root))
    if manifest_sha != _validate_sha256(
        expected_manifest_sha256,
        field="expected feature manifest sha256",
    ):
        raise ValueError("EXP-044 feature manifest sha256 mismatch")

    processed = _validate_common_manifest(
        manifest,
        symbol=symbol,
        timeframe=timeframe,
        expected_code_commit=_validate_commit(
            expected_code_commit,
            field="expected feature code commit",
        ),
    )
    if processed != _validate_sha256(
        expected_processed_manifest_sha256,
        field="expected feature processed manifest sha256",
    ):
        raise ValueError("EXP-044 feature processed-manifest mismatch")

    if manifest.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
        raise ValueError("EXP-044 feature-set version mismatch")
    if manifest.get("base_feature_definition_version") != "fmp-feature-v1":
        raise ValueError("EXP-044 base feature definition mismatch")
    if manifest.get("untouched_oos") is not False:
        raise ValueError("EXP-044 feature evidence must remain retrospective")
    if manifest.get("model_training_authorized") is not False:
        raise ValueError("EXP-044 feature manifest training authorization must be false")
    if manifest.get("row_count") != expected_row_count:
        raise ValueError("EXP-044 feature manifest row count mismatch")
    if manifest.get("unique_key_count") != expected_row_count:
        raise ValueError("EXP-044 feature unique-key count mismatch")
    if tuple(manifest.get("schema_columns", ())) != tuple(FEATURE_COLUMNS):
        raise ValueError("EXP-044 feature manifest schema columns mismatch")

    opened_months = manifest.get("opened_source_months")
    if expected_artifact_count == AUTHORITATIVE_CELL_ARTIFACT_COUNT:
        if (
            not isinstance(opened_months, list)
            or len(opened_months) != AUTHORITATIVE_CELL_ARTIFACT_COUNT
            or opened_months[0] != "2015-01"
            or opened_months[-1] != "2026-08"
        ):
            raise ValueError("EXP-044 authoritative feature month coverage mismatch")

    frame = _load_partitioned_frame(
        root=Path(root),
        manifest=manifest,
        expected_columns=FEATURE_COLUMNS,
        expected_artifact_count=expected_artifact_count,
    )
    if frame.height != expected_row_count:
        raise ValueError("EXP-044 loaded feature row count mismatch")
    if _schema_sha256(frame) != manifest.get("schema_sha256"):
        raise ValueError("EXP-044 feature schema fingerprint mismatch")
    return frame.sort(["symbol", "timeframe", "bar_start_utc"]), manifest


def load_verified_outcome_cell(
    *,
    root: Path,
    symbol: str,
    timeframe: str,
    expected_manifest_sha256: str,
    expected_feature_manifest_sha256: str,
    expected_feature_evidence_fingerprint: str,
    expected_processed_manifest_sha256: str,
    expected_source_feature_rows: int,
    expected_labeled_rows: int,
    expected_code_commit: str,
    expected_artifact_count: int = AUTHORITATIVE_CELL_ARTIFACT_COUNT,
) -> tuple[pl.DataFrame, Mapping[str, object]]:
    manifest, manifest_sha = _read_manifest(Path(root))
    if manifest_sha != _validate_sha256(
        expected_manifest_sha256,
        field="expected outcome manifest sha256",
    ):
        raise ValueError("EXP-044 outcome manifest sha256 mismatch")

    processed = _validate_common_manifest(
        manifest,
        symbol=symbol,
        timeframe=timeframe,
        expected_code_commit=_validate_commit(
            expected_code_commit,
            field="expected outcome code commit",
        ),
    )
    if processed != _validate_sha256(
        expected_processed_manifest_sha256,
        field="expected outcome processed manifest sha256",
    ):
        raise ValueError("EXP-044 outcome processed-manifest mismatch")

    if manifest.get("outcome_set_version") != MARKET_OUTCOME_SET_VERSION:
        raise ValueError("EXP-044 outcome-set version mismatch")
    if manifest.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
        raise ValueError("EXP-044 outcome feature-set version mismatch")
    if manifest.get("untouched_oos") is not False:
        raise ValueError("EXP-044 outcome evidence must remain retrospective")
    if manifest.get("model_fit_authorized") is not False:
        raise ValueError("EXP-044 outcome manifest fit authorization must be false")
    if manifest.get("feature_manifest_sha256") != expected_feature_manifest_sha256:
        raise ValueError("EXP-044 outcome feature-manifest binding mismatch")
    if (
        manifest.get("feature_evidence_fingerprint")
        != expected_feature_evidence_fingerprint
    ):
        raise ValueError("EXP-044 outcome feature-evidence binding mismatch")
    if manifest.get("source_feature_rows") != expected_source_feature_rows:
        raise ValueError("EXP-044 outcome source-feature row count mismatch")
    if manifest.get("labeled_rows") != expected_labeled_rows:
        raise ValueError("EXP-044 outcome labeled row count mismatch")
    if manifest.get("horizons_minutes") != [60, 240]:
        raise ValueError("EXP-044 outcome horizon identity mismatch")
    if manifest.get("slippage_pips_per_fill") != [0.2, 0.5, 1.0]:
        raise ValueError("EXP-044 outcome slippage identity mismatch")
    if tuple(manifest.get("schema_columns", ())) != tuple(OUTCOME_COLUMNS):
        raise ValueError("EXP-044 outcome manifest schema columns mismatch")

    frame = _load_partitioned_frame(
        root=Path(root),
        manifest=manifest,
        expected_columns=OUTCOME_COLUMNS,
        expected_artifact_count=expected_artifact_count,
    )
    if frame.height != expected_labeled_rows:
        raise ValueError("EXP-044 loaded outcome row count mismatch")
    if _schema_sha256(frame) != manifest.get("schema_sha256"):
        raise ValueError("EXP-044 outcome schema fingerprint mismatch")
    return frame.sort(
        ["symbol", "timeframe", "bar_start_utc", "horizon_minutes"]
    ), manifest


def validate_authoritative_readiness(
    readiness: Mapping[str, object],
) -> dict[tuple[str, str], Mapping[str, object]]:
    unsigned = dict(readiness)
    supplied_fingerprint = unsigned.pop("readiness_fingerprint", None)
    if supplied_fingerprint != AUTHORITATIVE_READINESS_FINGERPRINT:
        raise ValueError("EXP-044 authoritative readiness fingerprint mismatch")
    if _sha256_bytes(_canonical_json(unsigned)) != supplied_fingerprint:
        raise ValueError("EXP-044 authoritative readiness content fingerprint mismatch")
    if readiness.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("EXP-044 authoritative readiness experiment mismatch")
    if readiness.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError("EXP-044 authoritative readiness evidence label mismatch")
    if readiness.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
        raise ValueError("EXP-044 authoritative readiness feature-set mismatch")
    if readiness.get("outcome_set_version") != MARKET_OUTCOME_SET_VERSION:
        raise ValueError("EXP-044 authoritative readiness outcome-set mismatch")
    if readiness.get("feature_code_commit") != AUTHORITATIVE_FEATURE_CODE_COMMIT:
        raise ValueError("EXP-044 authoritative readiness feature commit mismatch")
    if readiness.get("outcome_code_commit") != AUTHORITATIVE_OUTCOME_CODE_COMMIT:
        raise ValueError("EXP-044 authoritative readiness outcome commit mismatch")
    if (
        readiness.get("feature_evidence_fingerprint")
        != AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT
    ):
        raise ValueError("EXP-044 authoritative feature evidence fingerprint mismatch")
    if (
        readiness.get("outcome_evidence_fingerprint")
        != AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT
    ):
        raise ValueError("EXP-044 authoritative outcome evidence fingerprint mismatch")
    if readiness.get("data_preparation_complete") is not True:
        raise ValueError("EXP-044 authoritative data preparation is incomplete")
    if readiness.get("verified_cell_count") != 9:
        raise ValueError("EXP-044 authoritative readiness must contain nine cells")
    if readiness.get("model_protocol_source_open_authorized") is not True:
        raise ValueError("EXP-044 authoritative protocol source gate is closed")

    for flag in (
        "model_protocol_result_authorized",
        "model_fit_authorized",
        "promotion_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
    ):
        if readiness.get(flag) is not False:
            raise ValueError(
                f"EXP-044 authoritative readiness {flag} must remain false"
            )

    cells = readiness.get("cells")
    if not isinstance(cells, list) or len(cells) != 9:
        raise ValueError("EXP-044 authoritative readiness cells are malformed")

    indexed: dict[tuple[str, str], Mapping[str, object]] = {}
    for cell in cells:
        if not isinstance(cell, Mapping):
            raise ValueError("EXP-044 authoritative readiness cell is malformed")
        identity = (str(cell.get("symbol")), str(cell.get("timeframe")))
        if identity in indexed:
            raise ValueError("duplicate EXP-044 authoritative readiness cell")
        if identity not in AUTHORITATIVE_FEATURE_ARTIFACTS:
            raise ValueError(f"unexpected EXP-044 authoritative readiness cell: {identity}")
        for field in (
            "feature_manifest_sha256",
            "outcome_manifest_sha256",
            "processed_manifest_sha256",
        ):
            _validate_sha256(cell.get(field), field=f"readiness {field}")
        for field in ("feature_row_count", "labeled_outcome_rows"):
            value = cell.get(field)
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value <= 0
            ):
                raise ValueError(f"readiness {field} must be a positive integer")
        indexed[identity] = cell

    if set(indexed) != set(AUTHORITATIVE_FEATURE_ARTIFACTS):
        raise ValueError("EXP-044 authoritative readiness cell set mismatch")
    return indexed


def load_authoritative_cell_artifacts(
    *,
    readiness: Mapping[str, object],
    feature_root: Path,
    outcome_root: Path,
    symbol: str,
    timeframe: str,
) -> VerifiedCellArtifacts:
    indexed = validate_authoritative_readiness(readiness)
    identity = (symbol, timeframe)
    try:
        expected = indexed[identity]
    except KeyError as exc:
        raise ValueError(f"unsupported authoritative EXP-044 cell: {identity}") from exc

    feature_frame, feature_manifest = load_verified_feature_cell(
        root=Path(feature_root),
        symbol=symbol,
        timeframe=timeframe,
        expected_manifest_sha256=str(expected["feature_manifest_sha256"]),
        expected_processed_manifest_sha256=str(
            expected["processed_manifest_sha256"]
        ),
        expected_row_count=int(expected["feature_row_count"]),
        expected_code_commit=AUTHORITATIVE_FEATURE_CODE_COMMIT,
    )
    outcome_frame, outcome_manifest = load_verified_outcome_cell(
        root=Path(outcome_root),
        symbol=symbol,
        timeframe=timeframe,
        expected_manifest_sha256=str(expected["outcome_manifest_sha256"]),
        expected_feature_manifest_sha256=str(
            expected["feature_manifest_sha256"]
        ),
        expected_feature_evidence_fingerprint=(
            AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT
        ),
        expected_processed_manifest_sha256=str(
            expected["processed_manifest_sha256"]
        ),
        expected_source_feature_rows=int(expected["feature_row_count"]),
        expected_labeled_rows=int(expected["labeled_outcome_rows"]),
        expected_code_commit=AUTHORITATIVE_OUTCOME_CODE_COMMIT,
    )

    if (
        feature_manifest.get("processed_manifest_sha256")
        != outcome_manifest.get("processed_manifest_sha256")
    ):
        raise ValueError("EXP-044 authoritative feature/outcome source mismatch")

    return VerifiedCellArtifacts(
        symbol=symbol,
        timeframe=timeframe,
        feature_frame=feature_frame,
        outcome_frame=outcome_frame,
        feature_manifest_sha256=str(expected["feature_manifest_sha256"]),
        outcome_manifest_sha256=str(expected["outcome_manifest_sha256"]),
        processed_manifest_sha256=str(expected["processed_manifest_sha256"]),
    )


def run_authoritative_model_bundle(
    *,
    readiness: Mapping[str, object],
    feature_roots: Mapping[tuple[str, str], Path],
    outcome_roots: Mapping[tuple[str, str], Path],
    code_commit: str,
) -> dict[str, object]:
    if AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED is not True:
        raise PermissionError(
            "DEC-091 source is non-executable for authoritative EXP-044 model fitting"
        )

    # This branch is intentionally unreachable under DEC-091. A later decision
    # must change the authorization gate before authoritative model results exist.
    indexed = validate_authoritative_readiness(readiness)
    cell_results: list[dict[str, object]] = []
    for cell in MODEL_CELLS:
        identity = (cell.symbol, cell.timeframe)
        if identity not in indexed:
            raise ValueError(f"missing authoritative EXP-044 cell: {identity}")
        if identity not in feature_roots or identity not in outcome_roots:
            raise ValueError(f"missing extracted artifact root for {identity}")
        loaded = load_authoritative_cell_artifacts(
            readiness=readiness,
            feature_root=feature_roots[identity],
            outcome_root=outcome_roots[identity],
            symbol=cell.symbol,
            timeframe=cell.timeframe,
        )
        cell_results.append(
            run_model_cell_core(
                features=loaded.feature_frame,
                outcomes=loaded.outcome_frame,
                cell=cell,
            )
        )
    return compile_model_result_evidence(
        cell_results,
        code_commit=code_commit,
    )


def compile_model_result_evidence(
    cell_results: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    _validate_commit(code_commit, field="EXP-044 model-result code commit")
    expected_cells = {
        (cell.symbol, cell.timeframe, cell.horizon_minutes)
        for cell in MODEL_CELLS
    }
    indexed: dict[tuple[str, str, int], Mapping[str, object]] = {}
    for result in cell_results:
        if not isinstance(result, Mapping):
            raise ValueError("EXP-044 model result row must be an object")
        cell = result.get("cell")
        if not isinstance(cell, Mapping):
            raise ValueError("EXP-044 model result is missing cell identity")
        identity = (
            str(cell.get("symbol")),
            str(cell.get("timeframe")),
            int(cell.get("horizon_minutes")),
        )
        if identity in indexed:
            raise ValueError("duplicate EXP-044 model result cell")
        if identity not in expected_cells:
            raise ValueError(f"unexpected EXP-044 model result cell: {identity}")
        if result.get("training_core_version") != MODEL_TRAINING_CORE_VERSION:
            raise ValueError("EXP-044 model result training-core version mismatch")
        if result.get("training_core_decision") != MODEL_TRAINING_CORE_DECISION:
            raise ValueError("EXP-044 model result training-core decision mismatch")
        if result.get("protocol_decision") != MODEL_PROTOCOL_DECISION:
            raise ValueError("EXP-044 model result protocol decision mismatch")
        if result.get("protocol_version") != MODEL_PROTOCOL_VERSION:
            raise ValueError("EXP-044 model result protocol version mismatch")
        if result.get("protocol_fingerprint") != AUTHORITATIVE_PROTOCOL_FINGERPRINT:
            raise ValueError("EXP-044 model result protocol fingerprint mismatch")
        if result.get("evidence_label") != EVIDENCE_LABEL:
            raise ValueError("EXP-044 model result evidence label mismatch")
        if result.get("untouched_oos") is not False:
            raise ValueError("EXP-044 model result must remain retrospective")
        result_fingerprint = _validate_sha256(
            result.get("result_fingerprint"),
            field="EXP-044 model cell result fingerprint",
        )
        for flag in (
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
        ):
            if result.get(flag) is not False:
                raise ValueError(f"EXP-044 model result {flag} must remain false")
        indexed[identity] = {
            "symbol": identity[0],
            "timeframe": identity[1],
            "horizon_minutes": identity[2],
            "result_fingerprint": result_fingerprint,
            "selection_status": result.get("selection", {}).get("status")
            if isinstance(result.get("selection"), Mapping)
            else None,
            "validation_status": result.get("validation", {}).get("status")
            if isinstance(result.get("validation"), Mapping)
            else None,
            "retrospective_holdout_status": result.get(
                "retrospective_holdout", {}
            ).get("status")
            if isinstance(result.get("retrospective_holdout"), Mapping)
            else None,
        }

    if set(indexed) != expected_cells:
        missing = sorted(expected_cells - set(indexed))
        raise ValueError(f"EXP-044 model result evidence is incomplete: {missing}")

    cells = [indexed[key] for key in sorted(indexed)]
    evidence: dict[str, object] = {
        "evidence_version": 1,
        "runner_version": MODEL_ARTIFACT_RUNNER_VERSION,
        "runner_decision": MODEL_ARTIFACT_RUNNER_DECISION,
        "training_core_version": MODEL_TRAINING_CORE_VERSION,
        "training_core_decision": MODEL_TRAINING_CORE_DECISION,
        "training_core_commit": AUTHORITATIVE_TRAINING_CORE_COMMIT,
        "protocol_decision": MODEL_PROTOCOL_DECISION,
        "protocol_version": MODEL_PROTOCOL_VERSION,
        "protocol_commit": AUTHORITATIVE_PROTOCOL_COMMIT,
        "protocol_fingerprint": AUTHORITATIVE_PROTOCOL_FINGERPRINT,
        "experiment_id": EXPERIMENT_ID,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "code_commit": code_commit,
        "feature_run_id": AUTHORITATIVE_FEATURE_RUN_ID,
        "feature_evidence_artifact_id": AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID,
        "feature_evidence_fingerprint": AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT,
        "outcome_run_id": AUTHORITATIVE_OUTCOME_RUN_ID,
        "outcome_evidence_artifact_id": AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID,
        "outcome_evidence_fingerprint": AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT,
        "readiness_artifact_id": AUTHORITATIVE_READINESS_ARTIFACT_ID,
        "readiness_fingerprint": AUTHORITATIVE_READINESS_FINGERPRINT,
        "verified_cell_count": len(cells),
        "cells": cells,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
    }
    evidence["evidence_fingerprint"] = _sha256_bytes(_canonical_json(evidence))
    return evidence


def write_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    path: Path,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        dict(evidence),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(
            f"conflicting existing EXP-044 model-result evidence: {destination}"
        )
    destination.write_text(payload, encoding="utf-8")


__all__ = [
    "AUTHORITATIVE_CELL_ARTIFACT_COUNT",
    "AUTHORITATIVE_FEATURE_ARTIFACTS",
    "AUTHORITATIVE_FEATURE_CODE_COMMIT",
    "AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID",
    "AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT",
    "AUTHORITATIVE_FEATURE_RUN_ID",
    "AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "AUTHORITATIVE_OUTCOME_ARTIFACTS",
    "AUTHORITATIVE_OUTCOME_CODE_COMMIT",
    "AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID",
    "AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT",
    "AUTHORITATIVE_OUTCOME_RUN_ID",
    "AUTHORITATIVE_PROTOCOL_COMMIT",
    "AUTHORITATIVE_PROTOCOL_FINGERPRINT",
    "AUTHORITATIVE_READINESS_ARTIFACT_ID",
    "AUTHORITATIVE_READINESS_FINGERPRINT",
    "AUTHORITATIVE_TRAINING_CORE_COMMIT",
    "MODEL_ARTIFACT_RUNNER_DECISION",
    "MODEL_ARTIFACT_RUNNER_VERSION",
    "VerifiedCellArtifacts",
    "compile_model_result_evidence",
    "load_authoritative_cell_artifacts",
    "load_verified_feature_cell",
    "load_verified_outcome_cell",
    "run_authoritative_model_bundle",
    "validate_authoritative_readiness",
    "write_model_result_evidence",
]
