from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .contracts import EVIDENCE_LABEL, EXPERIMENT_ID
from .model_artifacts import (
    AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID,
    AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT,
    AUTHORITATIVE_FEATURE_RUN_ID,
    AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID,
    AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT,
    AUTHORITATIVE_OUTCOME_RUN_ID,
    AUTHORITATIVE_PROTOCOL_COMMIT,
    AUTHORITATIVE_PROTOCOL_FINGERPRINT,
    AUTHORITATIVE_READINESS_ARTIFACT_ID,
    AUTHORITATIVE_READINESS_FINGERPRINT,
    AUTHORITATIVE_TRAINING_CORE_COMMIT,
    MODEL_ARTIFACT_RUNNER_DECISION,
    MODEL_ARTIFACT_RUNNER_VERSION,
)
from .model_protocol import (
    MODEL_CELLS,
    MODEL_PROTOCOL_DECISION,
    MODEL_PROTOCOL_VERSION,
)
from .model_training import (
    MODEL_TRAINING_CORE_DECISION,
    MODEL_TRAINING_CORE_VERSION,
)


MODEL_RESULT_VALIDATION_DECISION = "DEC-093"
MODEL_RESULT_EVIDENCE_VERSION = 1


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


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def _validate_status_chain(
    *,
    selection: object,
    validation: object,
    holdout: object,
) -> None:
    if selection == "NO_MODEL_CHALLENGER":
        if validation != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-044 no-challenger cell must keep validation locked"
            )
        if holdout != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-044 no-challenger cell must keep holdout locked"
            )
        return

    if selection != "SELECTED":
        raise ValueError(
            f"unexpected EXP-044 selection status: {selection!r}"
        )

    if validation == "REJECT":
        if holdout != "LOCKED_VALIDATION_REJECT":
            raise ValueError(
                "EXP-044 rejected validation must keep holdout locked"
            )
        return

    if validation == "PASS":
        if holdout not in {"PASS", "REJECT"}:
            raise ValueError(
                "EXP-044 passed validation must produce a holdout result"
            )
        return

    raise ValueError(
        f"unexpected EXP-044 validation status: {validation!r}"
    )


def validate_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    if not isinstance(evidence, Mapping):
        raise ValueError("EXP-044 model-result evidence must be an object")

    commit = _validate_commit(
        expected_code_commit,
        field="EXP-044 expected model-run code commit",
    )
    unsigned = dict(evidence)
    supplied_fingerprint = _validate_sha256(
        unsigned.pop("evidence_fingerprint", None),
        field="EXP-044 model-result evidence fingerprint",
    )
    if _sha256(_canonical_json(unsigned)) != supplied_fingerprint:
        raise ValueError(
            "EXP-044 model-result evidence content fingerprint mismatch"
        )

    exact = {
        "evidence_version": MODEL_RESULT_EVIDENCE_VERSION,
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
        "code_commit": commit,
        "feature_run_id": AUTHORITATIVE_FEATURE_RUN_ID,
        "feature_evidence_artifact_id": (
            AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID
        ),
        "feature_evidence_fingerprint": (
            AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT
        ),
        "outcome_run_id": AUTHORITATIVE_OUTCOME_RUN_ID,
        "outcome_evidence_artifact_id": (
            AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID
        ),
        "outcome_evidence_fingerprint": (
            AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT
        ),
        "readiness_artifact_id": AUTHORITATIVE_READINESS_ARTIFACT_ID,
        "readiness_fingerprint": AUTHORITATIVE_READINESS_FINGERPRINT,
        "verified_cell_count": 18,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
    }
    for field, expected in exact.items():
        if evidence.get(field) != expected:
            raise ValueError(
                f"EXP-044 model-result evidence {field} mismatch"
            )

    cells = evidence.get("cells")
    if not isinstance(cells, list) or len(cells) != 18:
        raise ValueError(
            "EXP-044 model-result evidence must contain exactly 18 cells"
        )
    expected_cells = {
        (cell.symbol, cell.timeframe, cell.horizon_minutes)
        for cell in MODEL_CELLS
    }
    indexed: dict[tuple[str, str, int], Mapping[str, object]] = {}
    selected_count = 0
    selection_pass_count = 0
    validation_pass_count = 0
    holdout_pass_count = 0

    for raw in cells:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-044 model-result cell is malformed")
        symbol = raw.get("symbol")
        timeframe = raw.get("timeframe")
        horizon = raw.get("horizon_minutes")
        if (
            not isinstance(symbol, str)
            or not isinstance(timeframe, str)
            or not isinstance(horizon, int)
            or isinstance(horizon, bool)
        ):
            raise ValueError("EXP-044 model-result cell identity is malformed")
        identity = (symbol, timeframe, horizon)
        if identity not in expected_cells:
            raise ValueError(
                f"unexpected EXP-044 model-result cell: {identity}"
            )
        if identity in indexed:
            raise ValueError("duplicate EXP-044 model-result cell")
        _validate_sha256(
            raw.get("result_fingerprint"),
            field="EXP-044 model cell result fingerprint",
        )
        selection = raw.get("selection_status")
        validation = raw.get("validation_status")
        holdout = raw.get("retrospective_holdout_status")
        _validate_status_chain(
            selection=selection,
            validation=validation,
            holdout=holdout,
        )
        if selection == "SELECTED":
            selected_count += 1
            selection_pass_count += 1
        if validation == "PASS":
            validation_pass_count += 1
        if holdout == "PASS":
            holdout_pass_count += 1
        indexed[identity] = raw

    if set(indexed) != expected_cells:
        missing = sorted(expected_cells - set(indexed))
        raise ValueError(
            f"EXP-044 model-result evidence is missing cells: {missing}"
        )

    return {
        "model_result_evidence_verified": True,
        "model_result_evidence_fingerprint": supplied_fingerprint,
        "model_result_code_commit": commit,
        "verified_cell_count": 18,
        "selected_cell_count": selected_count,
        "selection_pass_count": selection_pass_count,
        "validation_pass_count": validation_pass_count,
        "retrospective_holdout_pass_count": holdout_pass_count,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def load_model_result_evidence(
    path: Path,
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"cannot read EXP-044 model-result evidence: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("EXP-044 model-result evidence root must be an object")
    validate_model_result_evidence(
        value,
        expected_code_commit=expected_code_commit,
    )
    return value


__all__ = [
    "MODEL_RESULT_EVIDENCE_VERSION",
    "MODEL_RESULT_VALIDATION_DECISION",
    "load_model_result_evidence",
    "validate_model_result_evidence",
]
