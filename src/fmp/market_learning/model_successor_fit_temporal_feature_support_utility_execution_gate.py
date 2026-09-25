from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_fit_temporal_feature_support_utility_artifacts import (
    AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_fit_temporal_feature_support_utility_artifact_runner_sources,
)
from .model_successor_fit_temporal_feature_support_utility_protocol import (
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
)
from .model_successor_fit_temporal_feature_support_utility_training import (
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION,
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
)


FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_GATE_DECISION = "DEC-177"
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-179"
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_WORKFLOW_FILE = (
    "phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml"
)
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_WORKFLOW_NAME = (
    "phase8a-exp053-fit-temporal-feature-support-utility-model-training"
)

DEC174_MERGED_COMMIT = "9687eb8ea3920e87d6681adf7366a3ce0bba7154"
DEC175_MERGED_COMMIT = "60abce7c2674f9c25e4132037c9eb24cab1baf22"
DEC176_MERGED_COMMIT = "a37462015ada9499fccf7ebb0a9f515e74bff1b6"
DEC177_MERGED_COMMIT = "7faa5e765f08a47062444ebce3756bf9435ef1d4"
DEC178_MERGED_COMMIT = "132fa1621771f9fd072ba6b3a396a70e55c6883b"

DEC177_WORKFLOW_BLOB_SHA = "0a6704f75e83b06b7555dbb9dc912cda31443bbc"
DEC177_CLI_BLOB_SHA = "dbd146100d81be6ffc492de448d8dc4e0a2f4e73"
DEC177_GATE_BLOB_SHA = "600ea84946fe908d143f3fbe2082b3505733cdf5"
DEC178_REVIEW_BLOB_SHA = "c1586f8ddf48ad1125adaed7d8d8f0a476862beb"

DEC176_RUNNER_BLOB_SHA = "431c879bf26d88e33bdf0f0965ec62566b1a3e22"
DEC175_CORE_BLOB_SHA = "4fd0e48302f97e188a8124e1543bde0ffdb43b6f"
DEC174_PROTOCOL_BLOB_SHA = "11ae3fc8e68687cc04957ed9243d8c5969227fb8"
LEGACY_DATA_LOADER_BLOB_SHA = "27c0848d16722a22b4762f5842396c2aebc92bec"

FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_WORKFLOW_BLOB_SHA = (
    "0a6704f75e83b06b7555dbb9dc912cda31443bbc"
)
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_CLI_BLOB_SHA = (
    "dbd146100d81be6ffc492de448d8dc4e0a2f4e73"
)
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA = (
    "d25ab16056b9f5df283147d67b8f401f60ae7520"
)
PYPROJECT_BLOB_SHA = "de850a1ba397fc69ba634ecf178d732b5012c378"
PREPROCESSING_BLOB_SHA = "fcc42f45b9588d38311bc66bc454e6ea0a563e54"
FEATURE_SCHEMA_BLOB_SHA = "afbddc84676faadb8660b4da03c6abeb10cd2a13"
MARKET_CONTRACTS_BLOB_SHA = "4c5a75232e66715c0829e545d8659f59fb8b7724"
MARKET_OUTCOMES_BLOB_SHA = "c83fefd4252b2fe426af97686f86e43021760c77"

AUTHORIZED_PYTHON_VERSION = "3.12.14"

FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN = True
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = True
AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = (
    True
)
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = True
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED = True
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


def validate_fit_temporal_feature_support_utility_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = validate_fit_temporal_feature_support_utility_artifact_runner_sources(
        repository_root=root,
    )
    if runner.get(
        "fit_temporal_feature_support_utility_model_artifact_runner_decision"
    ) != FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION:
        raise ValueError("EXP-053 artifact-runner decision drift")
    if runner.get(
        "fit_temporal_feature_support_utility_model_artifact_runner_version"
    ) != FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION:
        raise ValueError("EXP-053 artifact-runner version drift")

    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION != "DEC-174":
        raise ValueError("EXP-053 protocol decision drift")
    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp053-fit-temporal-feature-support-utility-protocol-v1"
    ):
        raise ValueError("EXP-053 protocol version drift")
    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION != "DEC-175":
        raise ValueError("EXP-053 training-core decision drift")
    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION != (
        "fmp-exp053-fit-temporal-feature-support-utility-training-core-v1"
    ):
        raise ValueError("EXP-053 training-core version drift")
    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION != "DEC-176":
        raise ValueError("EXP-053 artifact-runner decision drift")
    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION != (
        "fmp-exp053-fit-temporal-feature-support-utility-artifact-runner-v1"
    ):
        raise ValueError("EXP-053 artifact-runner version constant drift")

    for field, value in (
        ("protocol result authorization", PROTOCOL_RESULT_AUTHORIZED),
        ("protocol execution authorization", PROTOCOL_EXECUTION_AUTHORIZED),
        ("protocol fit authorization", PROTOCOL_MODEL_FIT_AUTHORIZED),
        (
            "training execution authorization",
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED,
        ),
        ("training-core fit authorization", CORE_MODEL_FIT_AUTHORIZED),
        ("artifact-runner execution authorization", RUNNER_EXECUTION_AUTHORIZED),
        ("artifact-runner fit authorization", RUNNER_MODEL_FIT_AUTHORIZED),
    ):
        if value is not False:
            raise ValueError(f"EXP-053 {field} drift")

    expected = {
        "fit_temporal_support_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_feature_support_utility_artifacts.py",
            DEC176_RUNNER_BLOB_SHA,
        ),
        "fit_temporal_support_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_feature_support_utility_training.py",
            DEC175_CORE_BLOB_SHA,
        ),
        "fit_temporal_support_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_feature_support_utility_protocol.py",
            DEC174_PROTOCOL_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "terminal_review": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_feature_support_utility_result_review.py",
            DEC178_REVIEW_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml",
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root / "scripts/phase8a_exp053_model_run.py",
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp053-model-run.txt",
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
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
            raise ValueError(f"missing EXP-053 workflow dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-053 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "fit_temporal_feature_support_utility_model_execution_gate_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec163_merged_commit": DEC174_MERGED_COMMIT,
        "dec164_merged_commit": DEC175_MERGED_COMMIT,
        "dec165_merged_commit": DEC176_MERGED_COMMIT,
        "dec177_merged_commit": DEC177_MERGED_COMMIT,
        "dec178_merged_commit": DEC178_MERGED_COMMIT,
        "dec177_workflow_blob_sha": DEC177_WORKFLOW_BLOB_SHA,
        "dec177_cli_blob_sha": DEC177_CLI_BLOB_SHA,
        "dec177_gate_blob_sha": DEC177_GATE_BLOB_SHA,
        "dec178_review_blob_sha": actual["terminal_review"],
        "fit_temporal_feature_support_utility_model_execution_authorization_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "fit_temporal_feature_support_utility_runner_blob_sha": actual[
            "fit_temporal_support_runner"
        ],
        "fit_temporal_feature_support_utility_core_blob_sha": actual[
            "fit_temporal_support_core"
        ],
        "fit_temporal_feature_support_utility_protocol_blob_sha": actual[
            "fit_temporal_support_protocol"
        ],
        "legacy_data_loader_blob_sha": actual["legacy_data_loader"],
        "fit_temporal_feature_support_utility_workflow_blob_sha": actual["workflow"],
        "fit_temporal_feature_support_utility_cli_blob_sha": actual["cli"],
        "runtime_requirements_blob_sha": actual["runtime_requirements"],
        "pyproject_blob_sha": actual["pyproject"],
        "preprocessing_blob_sha": actual["preprocessing"],
        "feature_schema_blob_sha": actual["feature_schema"],
        "market_contracts_blob_sha": actual["market_contracts"],
        "market_outcomes_blob_sha": actual["market_outcomes"],
        "authorized_python_version": AUTHORIZED_PYTHON_VERSION,
        "fit_temporal_feature_support_utility_model_workflow_source_frozen": True,
        "fit_temporal_feature_support_utility_model_run_dispatch_authorized": True,
        "authoritative_fit_temporal_feature_support_utility_model_result_execution_authorized": (
            True
        ),
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


def build_fit_temporal_feature_support_utility_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_fit_temporal_feature_support_utility_model_workflow_sources(
        repository_root=repository_root,
    )
    return {
        **source,
        "stage": (
            "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_"
            "RUN_DISPATCH_REQUIRED"
        ),
        "next_action": (
            "DEC-179 authorizes at most one guarded historical EXP-053 "
            "model-result run after merge. This source change does not "
            "dispatch the workflow."
        ),
        "fit_temporal_feature_support_utility_model_execution_authorization_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
    }


def require_authoritative_fit_temporal_feature_support_utility_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = validate_fit_temporal_feature_support_utility_model_workflow_sources(
        repository_root=repository_root,
    )
    commit = _validate_commit(code_commit, field="EXP-053 code commit")

    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED is not True:
        raise PermissionError("EXP-053 model-run dispatch is not authorized")
    if (
        AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-053 authoritative model-result execution is not authorized"
        )
    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED is not True:
        raise PermissionError("EXP-053 model-protocol result is not authorized")
    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED is not True:
        raise PermissionError("EXP-053 model fitting is not authorized")

    return {
        **source,
        "code_commit": commit,
        "stage": "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZED",
        "fit_temporal_feature_support_utility_model_run_dispatch_authorized": True,
        "authoritative_fit_temporal_feature_support_utility_model_result_execution_authorized": True,
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


__all__ = [
    "AUTHORIZED_PYTHON_VERSION",
    "AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC174_MERGED_COMMIT",
    "DEC174_PROTOCOL_BLOB_SHA",
    "DEC175_CORE_BLOB_SHA",
    "DEC175_MERGED_COMMIT",
    "DEC176_MERGED_COMMIT",
    "DEC176_RUNNER_BLOB_SHA",
    "DEC177_CLI_BLOB_SHA",
    "DEC177_GATE_BLOB_SHA",
    "DEC177_MERGED_COMMIT",
    "DEC177_WORKFLOW_BLOB_SHA",
    "DEC178_MERGED_COMMIT",
    "DEC178_REVIEW_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FEATURE_SCHEMA_BLOB_SHA",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_CLI_BLOB_SHA",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_GATE_DECISION",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_WORKFLOW_FILE",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_WORKFLOW_NAME",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_WORKFLOW_BLOB_SHA",
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
    "build_fit_temporal_feature_support_utility_model_workflow_source_gate",
    "require_authoritative_fit_temporal_feature_support_utility_model_execution",
    "validate_fit_temporal_feature_support_utility_model_workflow_sources",
]
