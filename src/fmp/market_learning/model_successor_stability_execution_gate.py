from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_stability_artifacts import (
    AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    STABILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    STABILITY_MODEL_ARTIFACT_RUNNER_VERSION,
    STABILITY_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_stability_artifact_runner_sources,
)
from .model_successor_stability_protocol import (
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
    STABILITY_PROTOCOL_DECISION,
    STABILITY_PROTOCOL_VERSION,
)
from .model_successor_stability_training import (
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
    STABILITY_TRAINING_CORE_DECISION,
    STABILITY_TRAINING_CORE_VERSION,
    STABILITY_TRAINING_RESULT_EXECUTION_AUTHORIZED,
)


STABILITY_MODEL_EXECUTION_GATE_DECISION = "DEC-107"
STABILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-109"
STABILITY_MODEL_WORKFLOW_FILE = (
    "phase8a-exp046-stability-model-training.yml"
)
STABILITY_MODEL_WORKFLOW_NAME = (
    "phase8a-exp046-stability-model-training"
)

DEC104_MERGED_COMMIT = (
    "bb2ee82a7d081138e1c0847e8c406d6c3ac68589"
)
DEC105_MERGED_COMMIT = (
    "7aa3d86f6c1fce61dd7e35d9ba9830b1fa7355b5"
)
DEC106_MERGED_COMMIT = (
    "f1316addb56741fcd9b6b12f57e66b677c515188"
)
DEC107_MERGED_COMMIT = (
    "0ac50f49ed677ee767c02ca8c964fab569315127"
)
DEC108_MERGED_COMMIT = (
    "16ef2773a6f1bf6eae54d981ebd6f843e25d4e2a"
)

DEC107_WORKFLOW_BLOB_SHA = (
    "eb4690091a92021bb0c60f153800dc6cd9111cd5"
)
DEC107_CLI_BLOB_SHA = (
    "525be24ec365d50f6f7a390f7eb4f6ac370440b9"
)
DEC107_GATE_BLOB_SHA = (
    "d20ab76ec7ce112f6a1ca5485e78a395bacdf49b"
)
DEC108_REVIEW_BLOB_SHA = (
    "e5ff3c6a0cb65ba14bb3bd43d5dd1d4a5a491cf6"
)

DEC106_RUNNER_BLOB_SHA = (
    "2d8d6f82cd15f5bdb75bb384fe3efe1dc560857a"
)
DEC105_CORE_BLOB_SHA = (
    "6733d3c530fba944b9ea0c62783ed2110552e532"
)
DEC104_PROTOCOL_BLOB_SHA = (
    "4c8da2259f1fd6d27862a50a47a0d8108b58bc2e"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)

STABILITY_WORKFLOW_BLOB_SHA = (
    "3fc199f72665fad2a5d66c346645e9362b1e48e3"
)
STABILITY_CLI_BLOB_SHA = (
    "525be24ec365d50f6f7a390f7eb4f6ac370440b9"
)
STABILITY_RUNTIME_REQUIREMENTS_BLOB_SHA = (
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

STABILITY_MODEL_WORKFLOW_SOURCE_FROZEN = True
STABILITY_MODEL_RUN_DISPATCH_AUTHORIZED = True
AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = True
STABILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = True
STABILITY_MODEL_FIT_AUTHORIZED = True
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


def validate_stability_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = validate_stability_artifact_runner_sources(
        repository_root=root,
    )
    if (
        runner.get("stability_model_artifact_runner_decision")
        != STABILITY_MODEL_ARTIFACT_RUNNER_DECISION
    ):
        raise ValueError(
            "EXP-046 artifact-runner decision drift"
        )
    if (
        runner.get("stability_model_artifact_runner_version")
        != STABILITY_MODEL_ARTIFACT_RUNNER_VERSION
    ):
        raise ValueError(
            "EXP-046 artifact-runner version drift"
        )

    if STABILITY_PROTOCOL_DECISION != "DEC-104":
        raise ValueError(
            "EXP-046 protocol decision drift"
        )
    if (
        STABILITY_PROTOCOL_VERSION
        != "fmp-exp046-stability-protocol-v1"
    ):
        raise ValueError(
            "EXP-046 protocol version drift"
        )
    if STABILITY_TRAINING_CORE_DECISION != "DEC-105":
        raise ValueError(
            "EXP-046 training-core decision drift"
        )
    if (
        STABILITY_TRAINING_CORE_VERSION
        != "fmp-exp046-stability-training-core-v1"
    ):
        raise ValueError(
            "EXP-046 training-core version drift"
        )
    if STABILITY_MODEL_ARTIFACT_RUNNER_DECISION != "DEC-106":
        raise ValueError(
            "EXP-046 artifact-runner constant drift"
        )
    if (
        STABILITY_MODEL_ARTIFACT_RUNNER_VERSION
        != "fmp-exp046-stability-artifact-runner-v1"
    ):
        raise ValueError(
            "EXP-046 artifact-runner constant version drift"
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
            STABILITY_TRAINING_RESULT_EXECUTION_AUTHORIZED,
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
                f"EXP-046 {field} drift"
            )

    expected = {
        "stability_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_stability_artifacts.py",
            DEC106_RUNNER_BLOB_SHA,
        ),
        "stability_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_stability_training.py",
            DEC105_CORE_BLOB_SHA,
        ),
        "stability_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_stability_protocol.py",
            DEC104_PROTOCOL_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root
            / "src/fmp/market_learning/"
            "model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "terminal_review": (
            root
            / "src/fmp/market_learning/"
            "model_successor_stability_result_review.py",
            DEC108_REVIEW_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp046-stability-model-training.yml",
            STABILITY_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root
            / "scripts/"
            "phase8a_exp046_model_run.py",
            STABILITY_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root
            / "requirements/"
            "exp046-model-run.txt",
            STABILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
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
                f"missing frozen EXP-046 workflow source: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-046 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        **runner,
        "stability_model_execution_gate_decision": (
            STABILITY_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec104_merged_commit": DEC104_MERGED_COMMIT,
        "dec105_merged_commit": DEC105_MERGED_COMMIT,
        "dec106_merged_commit": DEC106_MERGED_COMMIT,
        "dec107_merged_commit": DEC107_MERGED_COMMIT,
        "dec108_merged_commit": DEC108_MERGED_COMMIT,
        "dec107_workflow_blob_sha": DEC107_WORKFLOW_BLOB_SHA,
        "dec107_cli_blob_sha": DEC107_CLI_BLOB_SHA,
        "dec107_gate_blob_sha": DEC107_GATE_BLOB_SHA,
        "dec108_review_blob_sha": actual["terminal_review"],
        "stability_model_execution_authorization_decision": (
            STABILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "stability_runner_blob_sha": actual[
            "stability_runner"
        ],
        "stability_core_blob_sha": actual[
            "stability_core"
        ],
        "stability_protocol_blob_sha": actual[
            "stability_protocol"
        ],
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "stability_workflow_blob_sha": actual[
            "workflow"
        ],
        "stability_cli_blob_sha": actual["cli"],
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


def build_stability_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_stability_model_workflow_sources(
        repository_root=repository_root,
    )
    return {
        **source,
        "stage": "STABILITY_MODEL_RUN_DISPATCH_REQUIRED",
        "next_action": (
            "DEC-109 authorizes at most one guarded historical EXP-046 "
            "model-result run after merge. This source change does not "
            "dispatch the workflow."
        ),
        "stability_model_execution_authorization_decision": (
            STABILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "stability_model_workflow_source_frozen": (
            STABILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        ),
        "stability_model_run_dispatch_authorized": (
            STABILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        ),
        "authoritative_stability_model_result_execution_authorized": (
            AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": (
            STABILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        ),
        "model_fit_authorized": (
            STABILITY_MODEL_FIT_AUTHORIZED
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


def require_authoritative_stability_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = validate_stability_model_workflow_sources(
        repository_root=repository_root,
    )
    commit = _validate_commit(
        code_commit,
        field="EXP-046 model execution code commit",
    )

    if STABILITY_MODEL_RUN_DISPATCH_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-046 model-run dispatch is not authorized"
        )
    if (
        AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-046 authoritative model-result execution "
            "is not authorized"
        )
    if (
        STABILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-046 model-protocol result is not authorized"
        )
    if STABILITY_MODEL_FIT_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-046 model fitting is not authorized"
        )

    return {
        **source,
        "code_commit": commit,
        "stability_model_run_dispatch_authorized": True,
        "authoritative_stability_model_result_execution_authorized": True,
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
    "AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC104_MERGED_COMMIT",
    "DEC104_PROTOCOL_BLOB_SHA",
    "DEC105_CORE_BLOB_SHA",
    "DEC105_MERGED_COMMIT",
    "DEC106_MERGED_COMMIT",
    "DEC106_RUNNER_BLOB_SHA",
    "DEC108_REVIEW_BLOB_SHA",
    "DEC107_GATE_BLOB_SHA",
    "DEC107_CLI_BLOB_SHA",
    "DEC107_WORKFLOW_BLOB_SHA",
    "DEC108_MERGED_COMMIT",
    "DEC107_MERGED_COMMIT",
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
    "STABILITY_CLI_BLOB_SHA",
    "STABILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION",
    "STABILITY_MODEL_EXECUTION_GATE_DECISION",
    "STABILITY_MODEL_FIT_AUTHORIZED",
    "STABILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "STABILITY_MODEL_RUN_DISPATCH_AUTHORIZED",
    "STABILITY_MODEL_WORKFLOW_FILE",
    "STABILITY_MODEL_WORKFLOW_NAME",
    "STABILITY_MODEL_WORKFLOW_SOURCE_FROZEN",
    "STABILITY_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "STABILITY_WORKFLOW_BLOB_SHA",
    "TRADING_AUTHORIZED",
    "build_stability_model_workflow_source_gate",
    "require_authoritative_stability_model_execution",
    "validate_stability_model_workflow_sources",
]
