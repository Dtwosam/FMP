from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_temporal_jackknife_utility_artifacts import (
    AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_temporal_jackknife_utility_artifact_runner_sources,
)
from .model_successor_temporal_jackknife_utility_protocol import (
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION,
)
from .model_successor_temporal_jackknife_utility_training import (
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION,
)


TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_GATE_DECISION = "DEC-144"
TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-146"
TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_FILE = (
    "phase8a-exp050-temporal-jackknife-utility-model-training.yml"
)
TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_NAME = (
    "phase8a-exp050-temporal-jackknife-utility-model-training"
)

DEC141_MERGED_COMMIT = (
    "4729da0e769f76f44b97ff6349ee25c5b7c0f5c7"
)
DEC142_MERGED_COMMIT = (
    "fa6fd14a880a84a44795efe4099679ed0f642497"
)
DEC143_MERGED_COMMIT = (
    "f0f584f2bfa1d6f0858af46312e41ffde5fe7d71"
)
DEC144_MERGED_COMMIT = (
    "9f2986c783823cf7d9647ed4b0a50c66470bea21"
)
DEC145_MERGED_COMMIT = (
    "b2907cced930afa4d877596a8268ec3bc49ceb9c"
)

DEC144_WORKFLOW_BLOB_SHA = (
    "ec8ed4ab3f0b8a18ffc735af92172e059ed29955"
)
DEC144_CLI_BLOB_SHA = (
    "70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09"
)
DEC144_GATE_BLOB_SHA = (
    "4814f0db86bec943d7282ab13586559b1eb8caa7"
)
DEC145_REVIEW_BLOB_SHA = (
    "e93f7f26e6f0cf8541c9dffd0d359acf0a7ec64e"
)

DEC143_RUNNER_BLOB_SHA = (
    "60076ccb45b3468bce68f88f667225e0b5662d92"
)
DEC142_CORE_BLOB_SHA = (
    "ec97a9941af052d6e223e4bafab9a9989ec57ff0"
)
DEC141_PROTOCOL_BLOB_SHA = (
    "b41b817b03aa0cc03a9d893227caa399b46d3cf8"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)

TEMPORAL_JACKKNIFE_UTILITY_WORKFLOW_BLOB_SHA = (
    "7a5875c69d8cdf33e9aaae58fc321dba0537ce0b"
)
TEMPORAL_JACKKNIFE_UTILITY_CLI_BLOB_SHA = (
    "70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09"
)
TEMPORAL_JACKKNIFE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA = (
    "d25ab16056b9f5df283147d67b8f401f60ae7520"
)
PYPROJECT_BLOB_SHA = (
    "de850a1ba397fc69ba634ecf178d732b5012c378"
)
PREPROCESSING_BLOB_SHA = (
    "fcc42f45b9588d38311bc66bc454e6ea0a563e54"
)
FEATURE_SCHEMA_BLOB_SHA = (
    "afbddc84676faadb8660b4da03c6abeb10cd2a13"
)
MARKET_CONTRACTS_BLOB_SHA = (
    "4c5a75232e66715c0829e545d8659f59fb8b7724"
)
MARKET_OUTCOMES_BLOB_SHA = (
    "c83fefd4252b2fe426af97686f86e43021760c77"
)

AUTHORIZED_PYTHON_VERSION = "3.12.14"

TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN = True
TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = True
AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = True
TEMPORAL_JACKKNIFE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = True
TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED = True
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
        raise ValueError(
            f"{field} must be a 40-character Git commit"
        )
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(
            f"{field} must be hexadecimal"
        ) from exc
    return value.lower()


def validate_temporal_jackknife_utility_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = (
        validate_temporal_jackknife_utility_artifact_runner_sources(
            repository_root=root,
        )
    )
    if runner.get(
        "temporal_jackknife_utility_model_artifact_runner_decision"
    ) != TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION:
        raise ValueError(
            "EXP-050 artifact-runner decision drift"
        )
    if runner.get(
        "temporal_jackknife_utility_model_artifact_runner_version"
    ) != TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION:
        raise ValueError(
            "EXP-050 artifact-runner version drift"
        )

    if TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION != "DEC-141":
        raise ValueError(
            "EXP-050 protocol decision drift"
        )
    if (
        TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION
        != "fmp-exp050-temporal-jackknife-utility-protocol-v1"
    ):
        raise ValueError(
            "EXP-050 protocol version drift"
        )
    if (
        TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION
        != "DEC-142"
    ):
        raise ValueError(
            "EXP-050 training-core decision drift"
        )
    if (
        TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION
        != "fmp-exp050-temporal-jackknife-utility-training-core-v1"
    ):
        raise ValueError(
            "EXP-050 training-core version drift"
        )
    if (
        TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        != "DEC-143"
    ):
        raise ValueError(
            "EXP-050 artifact-runner decision drift"
        )
    if (
        TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        != "fmp-exp050-temporal-jackknife-utility-artifact-runner-v1"
    ):
        raise ValueError(
            "EXP-050 artifact-runner version constant drift"
        )

    for field, value in (
        (
            "protocol result authorization",
            PROTOCOL_RESULT_AUTHORIZED,
        ),
        (
            "protocol execution authorization",
            PROTOCOL_EXECUTION_AUTHORIZED,
        ),
        (
            "protocol fit authorization",
            PROTOCOL_MODEL_FIT_AUTHORIZED,
        ),
        (
            "training execution authorization",
            TEMPORAL_JACKKNIFE_UTILITY_RESULT_EXECUTION_AUTHORIZED,
        ),
        (
            "training-core fit authorization",
            CORE_MODEL_FIT_AUTHORIZED,
        ),
        (
            "artifact-runner execution authorization",
            RUNNER_EXECUTION_AUTHORIZED,
        ),
        (
            "artifact-runner fit authorization",
            RUNNER_MODEL_FIT_AUTHORIZED,
        ),
    ):
        if value is not False:
            raise ValueError(
                f"EXP-050 {field} drift"
            )

    expected = {
        "temporal_jackknife_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_jackknife_utility_artifacts.py",
            DEC143_RUNNER_BLOB_SHA,
        ),
        "temporal_jackknife_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_jackknife_utility_training.py",
            DEC142_CORE_BLOB_SHA,
        ),
        "temporal_jackknife_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_jackknife_utility_protocol.py",
            DEC141_PROTOCOL_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root
            / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "terminal_review": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_jackknife_utility_result_review.py",
            DEC145_REVIEW_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp050-temporal-jackknife-utility-model-training.yml",
            TEMPORAL_JACKKNIFE_UTILITY_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root
            / "scripts/phase8a_exp050_model_run.py",
            TEMPORAL_JACKKNIFE_UTILITY_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root
            / "requirements/exp050-model-run.txt",
            TEMPORAL_JACKKNIFE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
        "pyproject": (
            root / "pyproject.toml",
            PYPROJECT_BLOB_SHA,
        ),
        "preprocessing": (
            root
            / "src/fmp/models/preprocessing.py",
            PREPROCESSING_BLOB_SHA,
        ),
        "feature_schema": (
            root
            / "src/fmp/features/schema.py",
            FEATURE_SCHEMA_BLOB_SHA,
        ),
        "market_contracts": (
            root
            / "src/fmp/market_learning/contracts.py",
            MARKET_CONTRACTS_BLOB_SHA,
        ),
        "market_outcomes": (
            root
            / "src/fmp/market_learning/outcomes.py",
            MARKET_OUTCOMES_BLOB_SHA,
        ),
    }

    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing frozen EXP-050 workflow source: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-050 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        **runner,
        "temporal_jackknife_utility_model_execution_gate_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec141_merged_commit": DEC141_MERGED_COMMIT,
        "dec142_merged_commit": DEC142_MERGED_COMMIT,
        "dec143_merged_commit": DEC143_MERGED_COMMIT,
        "dec144_merged_commit": DEC144_MERGED_COMMIT,
        "dec145_merged_commit": DEC145_MERGED_COMMIT,
        "dec144_workflow_blob_sha": DEC144_WORKFLOW_BLOB_SHA,
        "dec144_cli_blob_sha": DEC144_CLI_BLOB_SHA,
        "dec144_gate_blob_sha": DEC144_GATE_BLOB_SHA,
        "dec145_review_blob_sha": actual["terminal_review"],
        "temporal_jackknife_utility_model_execution_authorization_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "temporal_jackknife_utility_runner_blob_sha": actual[
            "temporal_jackknife_runner"
        ],
        "temporal_jackknife_utility_core_blob_sha": actual[
            "temporal_jackknife_core"
        ],
        "temporal_jackknife_utility_protocol_blob_sha": actual[
            "temporal_jackknife_protocol"
        ],
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "temporal_jackknife_utility_workflow_blob_sha": actual[
            "workflow"
        ],
        "temporal_jackknife_utility_cli_blob_sha": actual[
            "cli"
        ],
        "authorized_python_version": AUTHORIZED_PYTHON_VERSION,
        "runtime_requirements_blob_sha": actual[
            "runtime_requirements"
        ],
        "pyproject_blob_sha": actual["pyproject"],
        "preprocessing_blob_sha": actual[
            "preprocessing"
        ],
        "feature_schema_blob_sha": actual[
            "feature_schema"
        ],
        "market_contracts_blob_sha": actual[
            "market_contracts"
        ],
        "market_outcomes_blob_sha": actual[
            "market_outcomes"
        ],
    }


def build_temporal_jackknife_utility_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = (
        validate_temporal_jackknife_utility_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    return {
        **source,
        "stage": (
            "TEMPORAL_JACKKNIFE_UTILITY_MODEL_"
            "RUN_DISPATCH_REQUIRED"
        ),
        "next_action": (
            "DEC-146 authorizes at most one guarded historical EXP-050 "
            "model-result run after merge. This source change does not "
            "dispatch the workflow."
        ),
        "temporal_jackknife_utility_model_execution_authorization_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "temporal_jackknife_utility_model_workflow_source_frozen": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        ),
        "temporal_jackknife_utility_model_run_dispatch_authorized": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        ),
        "authoritative_temporal_jackknife_utility_model_result_execution_authorized": (
            AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        ),
        "model_fit_authorized": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED
        ),
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "shadow_authorized": SHADOW_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": (
            BROKER_MUTATION_AUTHORIZED
        ),
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


def require_authoritative_temporal_jackknife_utility_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = (
        validate_temporal_jackknife_utility_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    commit = _validate_commit(
        code_commit,
        field="EXP-050 model execution code commit",
    )

    if (
        TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-050 model-run dispatch is not authorized"
        )
    if (
        AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-050 authoritative model-result execution "
            "is not authorized"
        )
    if (
        TEMPORAL_JACKKNIFE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-050 model-protocol result is not authorized"
        )
    if (
        TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-050 model fitting is not authorized"
        )

    return {
        **source,
        "code_commit": commit,
        "temporal_jackknife_utility_model_run_dispatch_authorized": True,
        "authoritative_temporal_jackknife_utility_model_result_execution_authorized": True,
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
    "AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC141_MERGED_COMMIT",
    "DEC141_PROTOCOL_BLOB_SHA",
    "DEC142_CORE_BLOB_SHA",
    "DEC142_MERGED_COMMIT",
    "DEC143_MERGED_COMMIT",
    "DEC143_RUNNER_BLOB_SHA",
    "DEC144_CLI_BLOB_SHA",
    "DEC144_GATE_BLOB_SHA",
    "DEC144_MERGED_COMMIT",
    "DEC144_WORKFLOW_BLOB_SHA",
    "DEC145_MERGED_COMMIT",
    "DEC145_REVIEW_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FEATURE_SCHEMA_BLOB_SHA",
    "LEGACY_DATA_LOADER_BLOB_SHA",
    "LIVE_ORDER_AUTHORIZED",
    "MARKET_CONTRACTS_BLOB_SHA",
    "MARKET_OUTCOMES_BLOB_SHA",
    "PREPROCESSING_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "PYPROJECT_BLOB_SHA",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TEMPORAL_JACKKNIFE_UTILITY_CLI_BLOB_SHA",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_GATE_DECISION",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_FILE",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_NAME",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN",
    "TEMPORAL_JACKKNIFE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "TEMPORAL_JACKKNIFE_UTILITY_WORKFLOW_BLOB_SHA",
    "TRADING_AUTHORIZED",
    "build_temporal_jackknife_utility_model_workflow_source_gate",
    "require_authoritative_temporal_jackknife_utility_model_execution",
    "validate_temporal_jackknife_utility_model_workflow_sources",
]
