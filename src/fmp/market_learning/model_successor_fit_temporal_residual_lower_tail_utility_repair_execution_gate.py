from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_fit_temporal_residual_lower_tail_utility_repair_artifacts import (
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_VERSION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_fit_temporal_residual_lower_tail_utility_repair_artifact_contract_sources,
)
from .model_successor_fit_temporal_residual_lower_tail_utility_repair_protocol import (
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
)
from .model_successor_fit_temporal_residual_lower_tail_utility_repair_training import (
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_TRAINING_CORE_VERSION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
)


FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION = (
    "DEC-223"
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION = (
    "DEC-225"
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_WORKFLOW_FILE = (
    "phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml"
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_WORKFLOW_NAME = (
    "phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training"
)

DEC220_MERGED_COMMIT = "865ab1569a0765078ed099008a5722f8a6d310b4"
DEC221_MERGED_COMMIT = "6ea34dd3c62f72c55376e891eeb44d96ad5de54b"
DEC222_MERGED_COMMIT = "51e9ccde9feaada7932384fc4547b721c1341588"
DEC223_MERGED_COMMIT = "160c618352739a1ae12b86c80be9573e4c2f234a"
DEC224_MERGED_COMMIT = "e0f2328334d6da6b52cad53f23c9a3b05eeb72cd"

DEC223_WORKFLOW_BLOB_SHA = "db9d8ccaa7da674124963acc6ab4e65e6c2ad83f"
DEC223_CLI_BLOB_SHA = "889b2daa4e44175e0479377d6c8ea39846da596d"
DEC223_GATE_BLOB_SHA = "07c7db8bc7fc29cf595aa617f1d66ec4f77e4879"
DEC224_REVIEW_BLOB_SHA = "1a5f3e86b4d445ba4a77f3496f81de2b16b333cd"

DEC222_RUNNER_BLOB_SHA = "d69eb668ade480b66faf992190b3a4929f414960"
DEC221_CORE_BLOB_SHA = "ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd"
DEC220_PROTOCOL_BLOB_SHA = "2f355526476a4d41967bb46e1bfad6aa525cbfa9"
LEGACY_DATA_LOADER_BLOB_SHA = "27c0848d16722a22b4762f5842396c2aebc92bec"

FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_WORKFLOW_BLOB_SHA = (
    "2f28eea9f1e9cb941a91553bd6a7dc93245da7f8"
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_CLI_BLOB_SHA = (
    "889b2daa4e44175e0479377d6c8ea39846da596d"
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_RUNTIME_REQUIREMENTS_BLOB_SHA = (
    "d25ab16056b9f5df283147d67b8f401f60ae7520"
)
PYPROJECT_BLOB_SHA = "de850a1ba397fc69ba634ecf178d732b5012c378"
PREPROCESSING_BLOB_SHA = "fcc42f45b9588d38311bc66bc454e6ea0a563e54"
FEATURE_SCHEMA_BLOB_SHA = "afbddc84676faadb8660b4da03c6abeb10cd2a13"
MARKET_CONTRACTS_BLOB_SHA = "4c5a75232e66715c0829e545d8659f59fb8b7724"
MARKET_OUTCOMES_BLOB_SHA = "c83fefd4252b2fe426af97686f86e43021760c77"

AUTHORIZED_PYTHON_VERSION = "3.12.14"

FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_WORKFLOW_SOURCE_FROZEN = True
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED = True
AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED = True
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED = True
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED = True
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_fit_temporal_residual_lower_tail_utility_repair_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = (
        validate_fit_temporal_residual_lower_tail_utility_repair_artifact_contract_sources(
            repository_root=root,
        )
    )
    if runner.get("artifact_contract_decision") != (
        FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_DECISION
    ):
        raise ValueError("EXP-057 artifact-contract decision drift")
    if runner.get("artifact_contract_version") != (
        FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_VERSION
    ):
        raise ValueError("EXP-057 artifact-contract version drift")

    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_DECISION != "DEC-220":
        raise ValueError("EXP-057 protocol decision drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_VERSION != (
        "fmp-exp057-fit-temporal-residual-lower-tail-utility-"
        "implementation-repair-protocol-v1"
    ):
        raise ValueError("EXP-057 protocol version drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_TRAINING_CORE_DECISION != "DEC-221":
        raise ValueError("EXP-057 training-core decision drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_TRAINING_CORE_VERSION != (
        "fmp-exp057-fit-temporal-residual-lower-tail-utility-"
        "implementation-repair-training-core-v1"
    ):
        raise ValueError("EXP-057 training-core version drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_DECISION != "DEC-222":
        raise ValueError("EXP-057 artifact-contract decision drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_VERSION != (
        "fmp-exp057-fit-temporal-residual-lower-tail-utility-"
        "implementation-repair-artifact-contract-v1"
    ):
        raise ValueError("EXP-057 artifact-contract version constant drift")

    for field, value in (
        ("protocol result authorization", PROTOCOL_RESULT_AUTHORIZED),
        ("protocol execution authorization", PROTOCOL_EXECUTION_AUTHORIZED),
        ("protocol fit authorization", PROTOCOL_MODEL_FIT_AUTHORIZED),
        (
            "training execution authorization",
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RESULT_EXECUTION_AUTHORIZED,
        ),
        ("training-core fit authorization", CORE_MODEL_FIT_AUTHORIZED),
        ("artifact-contract execution authorization", RUNNER_EXECUTION_AUTHORIZED),
        ("artifact-contract fit authorization", RUNNER_MODEL_FIT_AUTHORIZED),
    ):
        if value is not False:
            raise ValueError(f"EXP-057 {field} drift")

    expected = {
        "residual_lower_tail_repair_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_lower_tail_utility_repair_artifacts.py",
            DEC222_RUNNER_BLOB_SHA,
        ),
        "residual_lower_tail_repair_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_lower_tail_utility_repair_training.py",
            DEC221_CORE_BLOB_SHA,
        ),
        "residual_lower_tail_repair_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_lower_tail_utility_repair_protocol.py",
            DEC220_PROTOCOL_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "terminal_review": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_lower_tail_utility_repair_result_review.py",
            DEC224_REVIEW_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml",
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root / "scripts/phase8a_exp057_model_run.py",
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp057-model-run.txt",
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
        "pyproject": (root / "pyproject.toml", PYPROJECT_BLOB_SHA),
        "preprocessing": (
            root / "src/fmp/models/preprocessing.py",
            PREPROCESSING_BLOB_SHA,
        ),
        "feature_schema": (
            root / "src/fmp/features/schema.py",
            FEATURE_SCHEMA_BLOB_SHA,
        ),
        "market_contracts": (
            root / "src/fmp/market_learning/contracts.py",
            MARKET_CONTRACTS_BLOB_SHA,
        ),
        "market_outcomes": (
            root / "src/fmp/market_learning/outcomes.py",
            MARKET_OUTCOMES_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing EXP-057 workflow dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-057 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "fit_temporal_residual_lower_tail_utility_repair_model_execution_gate_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec220_merged_commit": DEC220_MERGED_COMMIT,
        "dec221_merged_commit": DEC221_MERGED_COMMIT,
        "dec222_merged_commit": DEC222_MERGED_COMMIT,
        "dec223_merged_commit": DEC223_MERGED_COMMIT,
        "dec224_merged_commit": DEC224_MERGED_COMMIT,
        "dec223_workflow_blob_sha": DEC223_WORKFLOW_BLOB_SHA,
        "dec223_cli_blob_sha": DEC223_CLI_BLOB_SHA,
        "dec223_gate_blob_sha": DEC223_GATE_BLOB_SHA,
        "dec224_review_blob_sha": actual["terminal_review"],
        "fit_temporal_residual_lower_tail_utility_repair_model_execution_authorization_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "fit_temporal_residual_lower_tail_utility_repair_runner_blob_sha": actual[
            "residual_lower_tail_repair_runner"
        ],
        "fit_temporal_residual_lower_tail_utility_repair_core_blob_sha": actual[
            "residual_lower_tail_repair_core"
        ],
        "fit_temporal_residual_lower_tail_utility_repair_protocol_blob_sha": actual[
            "residual_lower_tail_repair_protocol"
        ],
        "legacy_data_loader_blob_sha": actual["legacy_data_loader"],
        "fit_temporal_residual_lower_tail_utility_repair_workflow_blob_sha": actual[
            "workflow"
        ],
        "fit_temporal_residual_lower_tail_utility_repair_cli_blob_sha": actual["cli"],
        "runtime_requirements_blob_sha": actual["runtime_requirements"],
        "pyproject_blob_sha": actual["pyproject"],
        "preprocessing_blob_sha": actual["preprocessing"],
        "feature_schema_blob_sha": actual["feature_schema"],
        "market_contracts_blob_sha": actual["market_contracts"],
        "market_outcomes_blob_sha": actual["market_outcomes"],
        "authorized_python_version": AUTHORIZED_PYTHON_VERSION,
        "fit_temporal_residual_lower_tail_utility_repair_model_workflow_source_frozen": True,
        "fit_temporal_residual_lower_tail_utility_repair_model_run_dispatch_authorized": True,
        "authoritative_fit_temporal_residual_lower_tail_utility_repair_model_result_execution_authorized": True,
        "model_protocol_result_authorized": True,
        "model_fit_authorized": True,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def build_fit_temporal_residual_lower_tail_utility_repair_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = (
        validate_fit_temporal_residual_lower_tail_utility_repair_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    return {
        **source,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_"
            "RUN_DISPATCH_REQUIRED"
        ),
        "next_action": (
            "DEC-225 authorizes at most one guarded historical EXP-057 "
            "model-result run after merge. This source change does not "
            "dispatch the workflow."
        ),
    }


def require_authoritative_fit_temporal_residual_lower_tail_utility_repair_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = (
        validate_fit_temporal_residual_lower_tail_utility_repair_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    commit = _validate_commit(code_commit, field="EXP-057 code commit")

    required_true = (
        FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED,
        AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED,
        FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED,
        FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED,
    )
    if not all(required_true):
        raise PermissionError(
            "DEC-225 EXP-057 historical model-result execution "
            "authorization is not open"
        )

    return {
        **source,
        "code_commit": commit,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_"
            "EXECUTION_AUTHORIZED"
        ),
    }


__all__ = [
    "AUTHORIZED_PYTHON_VERSION",
    "AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC220_MERGED_COMMIT",
    "DEC220_PROTOCOL_BLOB_SHA",
    "DEC221_CORE_BLOB_SHA",
    "DEC221_MERGED_COMMIT",
    "DEC222_MERGED_COMMIT",
    "DEC222_RUNNER_BLOB_SHA",
    "DEC223_CLI_BLOB_SHA",
    "DEC223_GATE_BLOB_SHA",
    "DEC223_MERGED_COMMIT",
    "DEC223_WORKFLOW_BLOB_SHA",
    "DEC224_MERGED_COMMIT",
    "DEC224_REVIEW_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FEATURE_SCHEMA_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_CLI_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_WORKFLOW_FILE",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_WORKFLOW_NAME",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_WORKFLOW_SOURCE_FROZEN",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_WORKFLOW_BLOB_SHA",
    "LEGACY_DATA_LOADER_BLOB_SHA",
    "LIVE_ORDER_AUTHORIZED",
    "MARKET_CONTRACTS_BLOB_SHA",
    "MARKET_OUTCOMES_BLOB_SHA",
    "PREPROCESSING_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "PYPROJECT_BLOB_SHA",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "build_fit_temporal_residual_lower_tail_utility_repair_model_workflow_source_gate",
    "require_authoritative_fit_temporal_residual_lower_tail_utility_repair_model_execution",
    "validate_fit_temporal_residual_lower_tail_utility_repair_model_workflow_sources",
]
