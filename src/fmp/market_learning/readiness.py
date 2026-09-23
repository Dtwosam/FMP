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
    "write_training_readiness",
]
