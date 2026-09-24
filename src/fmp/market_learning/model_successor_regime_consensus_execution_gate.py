from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_regime_consensus_artifacts import (
    AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    REGIME_CONSENSUS_MODEL_ARTIFACT_RUNNER_DECISION,
    REGIME_CONSENSUS_MODEL_ARTIFACT_RUNNER_VERSION,
    REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_regime_consensus_artifact_runner_sources,
)
from .model_successor_regime_consensus_protocol import (
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
    REGIME_CONSENSUS_PROTOCOL_DECISION,
    REGIME_CONSENSUS_PROTOCOL_VERSION,
)
from .model_successor_regime_consensus_training import (
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
    REGIME_CONSENSUS_RESULT_EXECUTION_AUTHORIZED as CORE_RESULT_EXECUTION_AUTHORIZED,
    REGIME_CONSENSUS_TRAINING_CORE_DECISION,
    REGIME_CONSENSUS_TRAINING_CORE_VERSION,
)


REGIME_CONSENSUS_MODEL_EXECUTION_GATE_DECISION = "DEC-126"
REGIME_CONSENSUS_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-128"
REGIME_CONSENSUS_MODEL_WORKFLOW_FILE = (
    "phase8a-exp048-regime-consensus-model-training.yml"
)
REGIME_CONSENSUS_MODEL_WORKFLOW_NAME = (
    "phase8a-exp048-regime-consensus-model-training"
)

DEC123_MERGED_COMMIT = (
    "39674f482e57922ac61fb0a6dff15a5ef621efd3"
)
DEC124_MERGED_COMMIT = (
    "83c5b40eebae884cda9b2b65a8494dcd63bcbb7a"
)
DEC125_MERGED_COMMIT = (
    "c695ea8add9227896d26b5641f4f8b51f4bb310e"
)
DEC126_MERGED_COMMIT = (
    "e2713ab33648901d42f9a9e1c4b8e7f0ff7920a6"
)
DEC127_MERGED_COMMIT = (
    "589782a92f9f1db2008bff99065cb070017311ca"
)

DEC126_WORKFLOW_BLOB_SHA = (
    "09d6d9fa710d18637648de23ae45968628032765"
)
DEC126_CLI_BLOB_SHA = (
    "f4a6941512824c1d60bff98175dd2fce9353aa68"
)
DEC126_GATE_BLOB_SHA = (
    "b70e2a8854439f20b25a9549820fad9c95612390"
)
DEC127_REVIEW_BLOB_SHA = (
    "0cd943cb4bb8780a6adfab02b0743c8415dcd5fe"
)

DEC125_RUNNER_BLOB_SHA = (
    "b62f3ff775f30c96fa2f6f1a15256fd696ea5c2e"
)
DEC124_CORE_BLOB_SHA = (
    "d902f9601ef3b04e0deaead18951d43350cb09be"
)
DEC123_PROTOCOL_BLOB_SHA = (
    "39b6b3f5adc7f34ffd8cebcf881138d6ca3eab84"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)

REGIME_CONSENSUS_WORKFLOW_BLOB_SHA = (
    "89a2c78af2c3d0925d7c8a2773af9291caacd95d"
)
REGIME_CONSENSUS_CLI_BLOB_SHA = (
    "f4a6941512824c1d60bff98175dd2fce9353aa68"
)
REGIME_CONSENSUS_RUNTIME_REQUIREMENTS_BLOB_SHA = (
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

REGIME_CONSENSUS_MODEL_WORKFLOW_SOURCE_FROZEN = True
REGIME_CONSENSUS_MODEL_RUN_DISPATCH_AUTHORIZED = True
AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED = True
REGIME_CONSENSUS_MODEL_PROTOCOL_RESULT_AUTHORIZED = True
REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED = True
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


def validate_regime_consensus_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = validate_regime_consensus_artifact_runner_sources(
        repository_root=root,
    )
    if (
        runner.get(
            "regime_consensus_model_artifact_runner_decision"
        )
        != REGIME_CONSENSUS_MODEL_ARTIFACT_RUNNER_DECISION
    ):
        raise ValueError(
            "EXP-048 artifact-runner decision drift"
        )
    if (
        runner.get(
            "regime_consensus_model_artifact_runner_version"
        )
        != REGIME_CONSENSUS_MODEL_ARTIFACT_RUNNER_VERSION
    ):
        raise ValueError(
            "EXP-048 artifact-runner version drift"
        )

    if REGIME_CONSENSUS_PROTOCOL_DECISION != "DEC-123":
        raise ValueError(
            "EXP-048 protocol decision drift"
        )
    if (
        REGIME_CONSENSUS_PROTOCOL_VERSION
        != "fmp-exp048-regime-consensus-protocol-v1"
    ):
        raise ValueError(
            "EXP-048 protocol version drift"
        )
    if (
        REGIME_CONSENSUS_TRAINING_CORE_DECISION
        != "DEC-124"
    ):
        raise ValueError(
            "EXP-048 training-core decision drift"
        )
    if (
        REGIME_CONSENSUS_TRAINING_CORE_VERSION
        != "fmp-exp048-regime-consensus-training-core-v1"
    ):
        raise ValueError(
            "EXP-048 training-core version drift"
        )
    if (
        REGIME_CONSENSUS_MODEL_ARTIFACT_RUNNER_DECISION
        != "DEC-125"
    ):
        raise ValueError(
            "EXP-048 artifact-runner constant drift"
        )
    if (
        REGIME_CONSENSUS_MODEL_ARTIFACT_RUNNER_VERSION
        != "fmp-exp048-regime-consensus-artifact-runner-v1"
    ):
        raise ValueError(
            "EXP-048 artifact-runner version constant drift"
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
            CORE_RESULT_EXECUTION_AUTHORIZED,
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
                f"EXP-048 {field} drift"
            )

    expected = {
        "regime_consensus_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_consensus_artifacts.py",
            DEC125_RUNNER_BLOB_SHA,
        ),
        "regime_consensus_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_consensus_training.py",
            DEC124_CORE_BLOB_SHA,
        ),
        "regime_consensus_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_consensus_protocol.py",
            DEC123_PROTOCOL_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root
            / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "terminal_review": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_consensus_result_review.py",
            DEC127_REVIEW_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp048-regime-consensus-model-training.yml",
            REGIME_CONSENSUS_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root
            / "scripts/phase8a_exp048_model_run.py",
            REGIME_CONSENSUS_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root
            / "requirements/exp048-model-run.txt",
            REGIME_CONSENSUS_RUNTIME_REQUIREMENTS_BLOB_SHA,
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
                f"missing frozen EXP-048 workflow source: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-048 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        **runner,
        "regime_consensus_model_execution_gate_decision": (
            REGIME_CONSENSUS_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec123_merged_commit": DEC123_MERGED_COMMIT,
        "dec124_merged_commit": DEC124_MERGED_COMMIT,
        "dec125_merged_commit": DEC125_MERGED_COMMIT,
        "dec126_merged_commit": DEC126_MERGED_COMMIT,
        "dec127_merged_commit": DEC127_MERGED_COMMIT,
        "dec126_workflow_blob_sha": DEC126_WORKFLOW_BLOB_SHA,
        "dec126_cli_blob_sha": DEC126_CLI_BLOB_SHA,
        "dec126_gate_blob_sha": DEC126_GATE_BLOB_SHA,
        "dec127_review_blob_sha": actual["terminal_review"],
        "regime_consensus_model_execution_authorization_decision": (
            REGIME_CONSENSUS_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "regime_consensus_runner_blob_sha": actual[
            "regime_consensus_runner"
        ],
        "regime_consensus_core_blob_sha": actual[
            "regime_consensus_core"
        ],
        "regime_consensus_protocol_blob_sha": actual[
            "regime_consensus_protocol"
        ],
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "regime_consensus_workflow_blob_sha": actual[
            "workflow"
        ],
        "regime_consensus_cli_blob_sha": actual["cli"],
        "authorized_python_version": (
            AUTHORIZED_PYTHON_VERSION
        ),
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


def build_regime_consensus_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_regime_consensus_model_workflow_sources(
        repository_root=repository_root,
    )
    return {
        **source,
        "stage": "REGIME_CONSENSUS_MODEL_RUN_DISPATCH_REQUIRED",
        "next_action": (
            "DEC-128 authorizes at most one guarded historical EXP-048 "
            "model-result run after merge. This source change does not "
            "dispatch the workflow."
        ),
        "regime_consensus_model_execution_authorization_decision": (
            REGIME_CONSENSUS_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "regime_consensus_model_workflow_source_frozen": (
            REGIME_CONSENSUS_MODEL_WORKFLOW_SOURCE_FROZEN
        ),
        "regime_consensus_model_run_dispatch_authorized": (
            REGIME_CONSENSUS_MODEL_RUN_DISPATCH_AUTHORIZED
        ),
        "authoritative_regime_consensus_model_result_execution_authorized": (
            AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": (
            REGIME_CONSENSUS_MODEL_PROTOCOL_RESULT_AUTHORIZED
        ),
        "model_fit_authorized": (
            REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED
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


def require_authoritative_regime_consensus_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = validate_regime_consensus_model_workflow_sources(
        repository_root=repository_root,
    )
    commit = _validate_commit(
        code_commit,
        field="EXP-048 model execution code commit",
    )

    if (
        REGIME_CONSENSUS_MODEL_RUN_DISPATCH_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-048 model-run dispatch is not authorized"
        )
    if (
        AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-048 authoritative model-result execution "
            "is not authorized"
        )
    if (
        REGIME_CONSENSUS_MODEL_PROTOCOL_RESULT_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-048 model-protocol result is not authorized"
        )
    if REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-048 model fitting is not authorized"
        )

    return {
        **source,
        "code_commit": commit,
        "regime_consensus_model_run_dispatch_authorized": True,
        "authoritative_regime_consensus_model_result_execution_authorized": True,
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
    "AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC123_MERGED_COMMIT",
    "DEC123_PROTOCOL_BLOB_SHA",
    "DEC124_CORE_BLOB_SHA",
    "DEC124_MERGED_COMMIT",
    "DEC125_MERGED_COMMIT",
    "DEC125_RUNNER_BLOB_SHA",
    "DEC126_CLI_BLOB_SHA",
    "DEC126_GATE_BLOB_SHA",
    "DEC126_MERGED_COMMIT",
    "DEC126_WORKFLOW_BLOB_SHA",
    "DEC127_MERGED_COMMIT",
    "DEC127_REVIEW_BLOB_SHA",
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
    "REGIME_CONSENSUS_CLI_BLOB_SHA",
    "REGIME_CONSENSUS_MODEL_EXECUTION_AUTHORIZATION_DECISION",
    "REGIME_CONSENSUS_MODEL_EXECUTION_GATE_DECISION",
    "REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED",
    "REGIME_CONSENSUS_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "REGIME_CONSENSUS_MODEL_RUN_DISPATCH_AUTHORIZED",
    "REGIME_CONSENSUS_MODEL_WORKFLOW_FILE",
    "REGIME_CONSENSUS_MODEL_WORKFLOW_NAME",
    "REGIME_CONSENSUS_MODEL_WORKFLOW_SOURCE_FROZEN",
    "REGIME_CONSENSUS_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "REGIME_CONSENSUS_WORKFLOW_BLOB_SHA",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "build_regime_consensus_model_workflow_source_gate",
    "require_authoritative_regime_consensus_model_execution",
    "validate_regime_consensus_model_workflow_sources",
]
