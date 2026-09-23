from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .contracts import EVIDENCE_LABEL, EXPERIMENT_ID, MARKET_FEATURE_SET_VERSION
from .evidence import EXPECTED_CELLS, load_feature_evidence_index
from .outcome_evidence import load_outcome_evidence_index
from .outcomes import MARKET_OUTCOME_SET_VERSION


READINESS_VERSION = "fmp-market-learning-readiness-v1"


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build_training_readiness(
    *,
    feature_evidence: Mapping[str, object],
    outcome_evidence: Mapping[str, object],
) -> dict[str, object]:
    feature_fingerprint = feature_evidence.get("evidence_fingerprint")
    outcome_fingerprint = outcome_evidence.get("evidence_fingerprint")
    if not isinstance(feature_fingerprint, str) or len(feature_fingerprint) != 64:
        raise ValueError("feature evidence fingerprint is invalid")
    if not isinstance(outcome_fingerprint, str) or len(outcome_fingerprint) != 64:
        raise ValueError("outcome evidence fingerprint is invalid")
    if outcome_evidence.get("feature_evidence_fingerprint") != feature_fingerprint:
        raise ValueError("outcome evidence does not bind the supplied feature evidence")

    if feature_evidence.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("feature evidence experiment identity mismatch")
    if outcome_evidence.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("outcome evidence experiment identity mismatch")
    if feature_evidence.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
        raise ValueError("feature evidence set identity mismatch")
    if outcome_evidence.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
        raise ValueError("outcome evidence feature-set identity mismatch")
    if outcome_evidence.get("outcome_set_version") != MARKET_OUTCOME_SET_VERSION:
        raise ValueError("outcome evidence set identity mismatch")
    if feature_evidence.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError("feature evidence label mismatch")
    if outcome_evidence.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError("outcome evidence label mismatch")
    if feature_evidence.get("feature_evidence_complete") is not True:
        raise ValueError("feature evidence is not complete")
    if outcome_evidence.get("outcome_evidence_complete") is not True:
        raise ValueError("outcome evidence is not complete")

    for evidence_name, evidence in (
        ("feature", feature_evidence),
        ("outcome", outcome_evidence),
    ):
        for flag in (
            "model_fit_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
        ):
            if evidence.get(flag) is not False:
                raise ValueError(
                    f"{evidence_name} evidence {flag} must remain false"
                )

    feature_cells_raw = feature_evidence.get("cells")
    outcome_cells_raw = outcome_evidence.get("cells")
    if not isinstance(feature_cells_raw, list) or not isinstance(outcome_cells_raw, list):
        raise ValueError("readiness evidence cells must be lists")
    if len(feature_cells_raw) != len(EXPECTED_CELLS):
        raise ValueError("feature evidence must contain exactly nine cells")
    if len(outcome_cells_raw) != len(EXPECTED_CELLS):
        raise ValueError("outcome evidence must contain exactly nine cells")

    feature_by_cell: dict[tuple[str, str], Mapping[str, object]] = {}
    for cell in feature_cells_raw:
        if not isinstance(cell, Mapping):
            raise ValueError("feature evidence cell must be an object")
        identity = (str(cell.get("symbol")), str(cell.get("timeframe")))
        if identity in feature_by_cell:
            raise ValueError("duplicate feature evidence cell")
        feature_by_cell[identity] = cell

    outcome_by_cell: dict[tuple[str, str], Mapping[str, object]] = {}
    for cell in outcome_cells_raw:
        if not isinstance(cell, Mapping):
            raise ValueError("outcome evidence cell must be an object")
        identity = (str(cell.get("symbol")), str(cell.get("timeframe")))
        if identity in outcome_by_cell:
            raise ValueError("duplicate outcome evidence cell")
        outcome_by_cell[identity] = cell

    if tuple(sorted(feature_by_cell)) != EXPECTED_CELLS:
        raise ValueError("feature evidence cell identities are incomplete")
    if tuple(sorted(outcome_by_cell)) != EXPECTED_CELLS:
        raise ValueError("outcome evidence cell identities are incomplete")

    cells: list[dict[str, object]] = []
    for identity in EXPECTED_CELLS:
        feature_cell = feature_by_cell[identity]
        outcome_cell = outcome_by_cell[identity]
        if (
            outcome_cell.get("feature_manifest_sha256")
            != feature_cell.get("manifest_sha256")
        ):
            raise ValueError(
                f"outcome cell does not bind feature manifest for {identity}"
            )
        if (
            outcome_cell.get("processed_manifest_sha256")
            != feature_cell.get("processed_manifest_sha256")
        ):
            raise ValueError(
                f"feature/outcome Phase 2 identity mismatch for {identity}"
            )
        if outcome_cell.get("source_feature_rows") != feature_cell.get("row_count"):
            raise ValueError(
                f"feature/outcome row-count mismatch for {identity}"
            )
        labeled_rows = outcome_cell.get("labeled_rows")
        if (
            not isinstance(labeled_rows, int)
            or isinstance(labeled_rows, bool)
            or labeled_rows <= 0
        ):
            raise ValueError(f"outcome labeled row count is invalid for {identity}")
        cells.append(
            {
                "symbol": identity[0],
                "timeframe": identity[1],
                "feature_manifest_sha256": feature_cell["manifest_sha256"],
                "processed_manifest_sha256": feature_cell[
                    "processed_manifest_sha256"
                ],
                "feature_row_count": feature_cell["row_count"],
                "outcome_manifest_sha256": outcome_cell["manifest_sha256"],
                "labeled_outcome_rows": labeled_rows,
            }
        )

    readiness: dict[str, object] = {
        "readiness_version": READINESS_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "feature_evidence_fingerprint": feature_fingerprint,
        "outcome_evidence_fingerprint": outcome_fingerprint,
        "feature_code_commit": feature_evidence["code_commit"],
        "outcome_code_commit": outcome_evidence["code_commit"],
        "verified_cell_count": len(cells),
        "data_preparation_complete": True,
        "model_protocol_source_open_authorized": True,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "cells": cells,
    }
    readiness["readiness_fingerprint"] = _sha256(_canonical_json(readiness))
    return readiness


def compile_training_readiness(
    *,
    feature_evidence_path: Path,
    outcome_evidence_path: Path,
) -> dict[str, object]:
    feature_evidence = load_feature_evidence_index(Path(feature_evidence_path))
    outcome_evidence = load_outcome_evidence_index(Path(outcome_evidence_path))
    return build_training_readiness(
        feature_evidence=feature_evidence,
        outcome_evidence=outcome_evidence,
    )



def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def load_training_readiness(path: Path) -> Mapping[str, object]:
    try:
        raw = Path(path).read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read EXP-044 training readiness: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("EXP-044 training readiness root must be an object")

    fingerprint = _validate_sha256(
        value.get("readiness_fingerprint"),
        field="EXP-044 readiness fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("readiness_fingerprint", None)
    if _sha256(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("EXP-044 readiness fingerprint mismatch")

    if value.get("readiness_version") != READINESS_VERSION:
        raise ValueError("EXP-044 readiness version mismatch")
    if value.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("EXP-044 readiness experiment identity mismatch")
    if value.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
        raise ValueError("EXP-044 readiness feature-set identity mismatch")
    if value.get("outcome_set_version") != MARKET_OUTCOME_SET_VERSION:
        raise ValueError("EXP-044 readiness outcome-set identity mismatch")
    if value.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError("EXP-044 readiness evidence label mismatch")
    _validate_sha256(
        value.get("feature_evidence_fingerprint"),
        field="EXP-044 readiness feature evidence fingerprint",
    )
    _validate_sha256(
        value.get("outcome_evidence_fingerprint"),
        field="EXP-044 readiness outcome evidence fingerprint",
    )
    _validate_commit(
        value.get("feature_code_commit"),
        field="EXP-044 readiness feature code commit",
    )
    _validate_commit(
        value.get("outcome_code_commit"),
        field="EXP-044 readiness outcome code commit",
    )

    if value.get("verified_cell_count") != len(EXPECTED_CELLS):
        raise ValueError("EXP-044 readiness verified cell count mismatch")
    if value.get("data_preparation_complete") is not True:
        raise ValueError("EXP-044 readiness data preparation is not complete")
    if value.get("model_protocol_source_open_authorized") is not True:
        raise ValueError("EXP-044 readiness must authorize protocol source only")

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
        if value.get(flag) is not False:
            raise ValueError(f"EXP-044 readiness {flag} must remain false")

    cells = value.get("cells")
    if not isinstance(cells, list) or len(cells) != len(EXPECTED_CELLS):
        raise ValueError("EXP-044 readiness cells are incomplete")
    seen: list[tuple[str, str]] = []
    for cell in cells:
        if not isinstance(cell, Mapping):
            raise ValueError("EXP-044 readiness cell must be an object")
        identity = (cell.get("symbol"), cell.get("timeframe"))
        if identity not in EXPECTED_CELLS:
            raise ValueError(f"unexpected EXP-044 readiness cell: {identity!r}")
        seen.append(identity)
        _validate_sha256(
            cell.get("feature_manifest_sha256"),
            field="EXP-044 readiness feature manifest sha256",
        )
        _validate_sha256(
            cell.get("processed_manifest_sha256"),
            field="EXP-044 readiness Phase 2 manifest sha256",
        )
        _validate_sha256(
            cell.get("outcome_manifest_sha256"),
            field="EXP-044 readiness outcome manifest sha256",
        )
        feature_rows = cell.get("feature_row_count")
        outcome_rows = cell.get("labeled_outcome_rows")
        if (
            not isinstance(feature_rows, int)
            or isinstance(feature_rows, bool)
            or feature_rows <= 0
        ):
            raise ValueError("EXP-044 readiness feature row count is invalid")
        if (
            not isinstance(outcome_rows, int)
            or isinstance(outcome_rows, bool)
            or outcome_rows <= 0
        ):
            raise ValueError("EXP-044 readiness outcome row count is invalid")
    if tuple(seen) != EXPECTED_CELLS:
        raise ValueError("EXP-044 readiness cells are not exact and sorted")
    return value


def write_training_readiness(
    *,
    readiness: Mapping[str, object],
    path: Path,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(dict(readiness), sort_keys=True, indent=2, allow_nan=False) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(
            f"conflicting existing EXP-044 training readiness artifact: {destination}"
        )
    destination.write_text(payload, encoding="utf-8")


__all__ = [
    "READINESS_VERSION",
    "build_training_readiness",
    "compile_training_readiness",
    "load_training_readiness",
    "write_training_readiness",
]
