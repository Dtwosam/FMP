from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_density_artifacts import (
    AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    DENSITY_MODEL_ARTIFACT_RUNNER_DECISION,
    DENSITY_MODEL_ARTIFACT_RUNNER_VERSION,
    DENSITY_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_density_artifact_runner_sources,
)
from .model_successor_density_protocol import (
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
    DENSITY_PROTOCOL_DECISION,
    DENSITY_PROTOCOL_VERSION,
)
from .model_successor_density_training import (
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
    DENSITY_TRAINING_CORE_DECISION,
    DENSITY_TRAINING_CORE_VERSION,
    DENSITY_TRAINING_RESULT_EXECUTION_AUTHORIZED,
)


DENSITY_MODEL_EXECUTION_GATE_DECISION = "DEC-116"
DENSITY_MODEL_WORKFLOW_FILE = (
    "phase8a-exp047-density-model-training.yml"
)
DENSITY_MODEL_WORKFLOW_NAME = (
    "phase8a-exp047-density-model-training"
)

DEC113_MERGED_COMMIT = (
    "060bde94835158d62d47640aaf1a77ec56b483ff"
)
DEC114_MERGED_COMMIT = (
    "3e236169ae71074630ece7d78516d5e6586abe1f"
)
DEC115_MERGED_COMMIT = (
    "93f1b25cb4260d6b25f484c33014e322cc1ea9af"
)

DEC115_RUNNER_BLOB_SHA = (
    "2d3997ca97fb4568187be54914fe76e8dbf76ff5"
)
DEC114_CORE_BLOB_SHA = (
    "8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945"
)
DEC113_PROTOCOL_BLOB_SHA = (
    "871936729a1090d675f6f5181ef04c8f32494394"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)

DENSITY_WORKFLOW_BLOB_SHA = (
    "7ae75dbca58266736be6a6cdf66bf58b61ec3b63"
)
DENSITY_CLI_BLOB_SHA = (
    "28941013c2cf9942a94667d58ec6b76de9d13cd2"
)
DENSITY_RUNTIME_REQUIREMENTS_BLOB_SHA = (
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

DENSITY_MODEL_WORKFLOW_SOURCE_FROZEN = True
DENSITY_MODEL_RUN_DISPATCH_AUTHORIZED = False
AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED = False
DENSITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = False
DENSITY_MODEL_FIT_AUTHORIZED = False
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


def validate_density_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = validate_density_artifact_runner_sources(
        repository_root=root,
    )
    if (
        runner.get("density_model_artifact_runner_decision")
        != DENSITY_MODEL_ARTIFACT_RUNNER_DECISION
    ):
        raise ValueError(
            "EXP-047 artifact-runner decision drift"
        )
    if (
        runner.get("density_model_artifact_runner_version")
        != DENSITY_MODEL_ARTIFACT_RUNNER_VERSION
    ):
        raise ValueError(
            "EXP-047 artifact-runner version drift"
        )

    if DENSITY_PROTOCOL_DECISION != "DEC-113":
        raise ValueError(
            "EXP-047 protocol decision drift"
        )
    if (
        DENSITY_PROTOCOL_VERSION
        != "fmp-exp047-hgb-density-protocol-v1"
    ):
        raise ValueError(
            "EXP-047 protocol version drift"
        )
    if DENSITY_TRAINING_CORE_DECISION != "DEC-114":
        raise ValueError(
            "EXP-047 training-core decision drift"
        )
    if (
        DENSITY_TRAINING_CORE_VERSION
        != "fmp-exp047-hgb-density-training-core-v1"
    ):
        raise ValueError(
            "EXP-047 training-core version drift"
        )
    if DENSITY_MODEL_ARTIFACT_RUNNER_DECISION != "DEC-115":
        raise ValueError(
            "EXP-047 artifact-runner constant drift"
        )
    if (
        DENSITY_MODEL_ARTIFACT_RUNNER_VERSION
        != "fmp-exp047-density-artifact-runner-v1"
    ):
        raise ValueError(
            "EXP-047 artifact-runner version constant drift"
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
            DENSITY_TRAINING_RESULT_EXECUTION_AUTHORIZED,
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
                f"EXP-047 {field} drift"
            )

    expected = {
        "density_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_density_artifacts.py",
            DEC115_RUNNER_BLOB_SHA,
        ),
        "density_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_density_training.py",
            DEC114_CORE_BLOB_SHA,
        ),
        "density_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_density_protocol.py",
            DEC113_PROTOCOL_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root
            / "src/fmp/market_learning/"
            "model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp047-density-model-training.yml",
            DENSITY_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root
            / "scripts/"
            "phase8a_exp047_model_run.py",
            DENSITY_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root
            / "requirements/"
            "exp047-model-run.txt",
            DENSITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
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
                f"missing frozen EXP-047 workflow source: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-047 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        **runner,
        "density_model_execution_gate_decision": (
            DENSITY_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec113_merged_commit": DEC113_MERGED_COMMIT,
        "dec114_merged_commit": DEC114_MERGED_COMMIT,
        "dec115_merged_commit": DEC115_MERGED_COMMIT,
        "density_runner_blob_sha": actual[
            "density_runner"
        ],
        "density_core_blob_sha": actual[
            "density_core"
        ],
        "density_protocol_blob_sha": actual[
            "density_protocol"
        ],
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "density_workflow_blob_sha": actual[
            "workflow"
        ],
        "density_cli_blob_sha": actual["cli"],
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


def build_density_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_density_model_workflow_sources(
        repository_root=repository_root,
    )
    return {
        **source,
        "stage": "DENSITY_MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        "next_action": (
            "A later separate decision may authorize at most a "
            "guarded EXP-047 historical model-result run. "
            "DEC-116 does not authorize or dispatch execution."
        ),
        "density_model_workflow_source_frozen": (
            DENSITY_MODEL_WORKFLOW_SOURCE_FROZEN
        ),
        "density_model_run_dispatch_authorized": (
            DENSITY_MODEL_RUN_DISPATCH_AUTHORIZED
        ),
        "authoritative_density_model_result_execution_authorized": (
            AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": (
            DENSITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        ),
        "model_fit_authorized": (
            DENSITY_MODEL_FIT_AUTHORIZED
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


def require_authoritative_density_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = validate_density_model_workflow_sources(
        repository_root=repository_root,
    )
    commit = _validate_commit(
        code_commit,
        field="EXP-047 model execution code commit",
    )

    if DENSITY_MODEL_RUN_DISPATCH_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-047 model-run dispatch is not authorized"
        )
    if (
        AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-047 authoritative model-result execution "
            "is not authorized"
        )
    if (
        DENSITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-047 model-protocol result is not authorized"
        )
    if DENSITY_MODEL_FIT_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-047 model fitting is not authorized"
        )

    return {
        **source,
        "code_commit": commit,
        "density_model_run_dispatch_authorized": True,
        "authoritative_density_model_result_execution_authorized": True,
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
    "AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC113_MERGED_COMMIT",
    "DEC113_PROTOCOL_BLOB_SHA",
    "DEC114_CORE_BLOB_SHA",
    "DEC114_MERGED_COMMIT",
    "DEC115_MERGED_COMMIT",
    "DEC115_RUNNER_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_CLI_BLOB_SHA",
    "DENSITY_MODEL_EXECUTION_GATE_DECISION",
    "DENSITY_MODEL_FIT_AUTHORIZED",
    "DENSITY_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "DENSITY_MODEL_RUN_DISPATCH_AUTHORIZED",
    "DENSITY_MODEL_WORKFLOW_FILE",
    "DENSITY_MODEL_WORKFLOW_NAME",
    "DENSITY_MODEL_WORKFLOW_SOURCE_FROZEN",
    "DENSITY_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "DENSITY_WORKFLOW_BLOB_SHA",
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
    "TRADING_AUTHORIZED",
    "build_density_model_workflow_source_gate",
    "require_authoritative_density_model_execution",
    "validate_density_model_workflow_sources",
]
