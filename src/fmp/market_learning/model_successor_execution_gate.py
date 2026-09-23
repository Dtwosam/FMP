from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_artifacts import (
    SUCCESSOR_MODEL_ARTIFACT_RUNNER_DECISION,
    SUCCESSOR_MODEL_ARTIFACT_RUNNER_VERSION,
    validate_successor_artifact_runner_sources,
)
from .model_successor_protocol import (
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_DECISION,
    SUCCESSOR_PROTOCOL_VERSION,
)
from .model_successor_training import (
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_TRAINING_CORE_DECISION,
    SUCCESSOR_TRAINING_CORE_VERSION,
    SUCCESSOR_TRAINING_RESULT_EXECUTION_AUTHORIZED,
)


SUCCESSOR_MODEL_EXECUTION_GATE_DECISION = "DEC-098"
SUCCESSOR_MODEL_WORKFLOW_FILE = "phase8a-exp045-model-training.yml"
SUCCESSOR_MODEL_WORKFLOW_NAME = "phase8a-exp045-model-training"

DEC097_MERGED_COMMIT = "f6c1090064cd3d85c7c3503dec1ef461eeba5da2"
DEC097_RUNNER_BLOB_SHA = "adebcc48130e8800741810c239528ef6c21eea6e"
DEC096_CORE_BLOB_SHA = "3f0bc1bfa9640d08175e72cdf131bb97c94d562c"
DEC095_PROTOCOL_BLOB_SHA = "44129fc5337fb55b9c7d81f5ba0561ea788bd264"
DEC094_FAILURE_REVIEW_BLOB_SHA = "2260ad4ad08a7e9874bd28030be977a3e71436f9"
LEGACY_DATA_LOADER_BLOB_SHA = "27c0848d16722a22b4762f5842396c2aebc92bec"

SUCCESSOR_WORKFLOW_BLOB_SHA = "d3e4d11a8e8270417d6bbced27e756b7cc23c324"
SUCCESSOR_CLI_BLOB_SHA = "ff0ed231e22589c3597672bb8bab1f62b321647d"
SUCCESSOR_RUNTIME_REQUIREMENTS_BLOB_SHA = (
    "d25ab16056b9f5df283147d67b8f401f60ae7520"
)
PYPROJECT_BLOB_SHA = "de850a1ba397fc69ba634ecf178d732b5012c378"
PREPROCESSING_BLOB_SHA = "fcc42f45b9588d38311bc66bc454e6ea0a563e54"
FEATURE_SCHEMA_BLOB_SHA = "afbddc84676faadb8660b4da03c6abeb10cd2a13"
MARKET_CONTRACTS_BLOB_SHA = "4c5a75232e66715c0829e545d8659f59fb8b7724"
MARKET_OUTCOMES_BLOB_SHA = "c83fefd4252b2fe426af97686f86e43021760c77"

AUTHORIZED_PYTHON_VERSION = "3.12.14"

SUCCESSOR_MODEL_WORKFLOW_SOURCE_FROZEN = True
SUCCESSOR_MODEL_RUN_DISPATCH_AUTHORIZED = False
AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED = False
SUCCESSOR_MODEL_PROTOCOL_RESULT_AUTHORIZED = False
SUCCESSOR_MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
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


def validate_successor_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = validate_successor_artifact_runner_sources(
        repository_root=root,
    )
    if runner.get("successor_model_artifact_runner_decision") != "DEC-097":
        raise ValueError("EXP-045 artifact-runner decision drift")
    if (
        runner.get("successor_model_artifact_runner_version")
        != "fmp-exp045-model-artifact-runner-v1"
    ):
        raise ValueError("EXP-045 artifact-runner version drift")
    if SUCCESSOR_MODEL_ARTIFACT_RUNNER_DECISION != "DEC-097":
        raise ValueError("EXP-045 artifact-runner constant drift")
    if (
        SUCCESSOR_MODEL_ARTIFACT_RUNNER_VERSION
        != "fmp-exp045-model-artifact-runner-v1"
    ):
        raise ValueError("EXP-045 artifact-runner constant version drift")
    if SUCCESSOR_PROTOCOL_DECISION != "DEC-095":
        raise ValueError("EXP-045 protocol decision drift")
    if SUCCESSOR_PROTOCOL_VERSION != "fmp-exp045-model-protocol-v1":
        raise ValueError("EXP-045 protocol version drift")
    if SUCCESSOR_TRAINING_CORE_DECISION != "DEC-096":
        raise ValueError("EXP-045 training-core decision drift")
    if (
        SUCCESSOR_TRAINING_CORE_VERSION
        != "fmp-exp045-model-training-core-v1"
    ):
        raise ValueError("EXP-045 training-core version drift")

    if PROTOCOL_RESULT_AUTHORIZED is not False:
        raise ValueError("EXP-045 protocol result authorization drift")
    if PROTOCOL_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError("EXP-045 protocol fit authorization drift")
    if SUCCESSOR_TRAINING_RESULT_EXECUTION_AUTHORIZED is not False:
        raise ValueError("EXP-045 training execution authorization drift")
    if CORE_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError("EXP-045 training-core fit authorization drift")

    expected = {
        "successor_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_artifacts.py",
            DEC097_RUNNER_BLOB_SHA,
        ),
        "successor_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_training.py",
            DEC096_CORE_BLOB_SHA,
        ),
        "successor_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_protocol.py",
            DEC095_PROTOCOL_BLOB_SHA,
        ),
        "failure_review": (
            root
            / "src/fmp/market_learning/"
            "model_run_failure_review.py",
            DEC094_FAILURE_REVIEW_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp045-model-training.yml",
            SUCCESSOR_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root / "scripts/phase8a_exp045_model_run.py",
            SUCCESSOR_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp045-model-run.txt",
            SUCCESSOR_RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
        "pyproject": (
            root / "pyproject.toml",
            PYPROJECT_BLOB_SHA,
        ),
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
            raise ValueError(
                f"missing frozen EXP-045 workflow source: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-045 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        **runner,
        "successor_model_execution_gate_decision": (
            SUCCESSOR_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec097_merged_commit": DEC097_MERGED_COMMIT,
        "successor_runner_blob_sha": actual["successor_runner"],
        "successor_core_blob_sha": actual["successor_core"],
        "successor_protocol_blob_sha": actual["successor_protocol"],
        "failure_review_blob_sha": actual["failure_review"],
        "legacy_data_loader_blob_sha": actual["legacy_data_loader"],
        "successor_workflow_blob_sha": actual["workflow"],
        "successor_cli_blob_sha": actual["cli"],
        "authorized_python_version": AUTHORIZED_PYTHON_VERSION,
        "runtime_requirements_blob_sha": actual[
            "runtime_requirements"
        ],
        "pyproject_blob_sha": actual["pyproject"],
        "preprocessing_blob_sha": actual["preprocessing"],
        "feature_schema_blob_sha": actual["feature_schema"],
        "market_contracts_blob_sha": actual["market_contracts"],
        "market_outcomes_blob_sha": actual["market_outcomes"],
    }


def build_successor_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_successor_model_workflow_sources(
        repository_root=repository_root,
    )
    return {
        **source,
        "stage": "SUCCESSOR_MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        "next_action": (
            "EXP-045 workflow/CLI source is frozen but historical result "
            "execution remains disabled. Do not dispatch the workflow."
        ),
        "successor_model_workflow_source_frozen": (
            SUCCESSOR_MODEL_WORKFLOW_SOURCE_FROZEN
        ),
        "successor_model_run_dispatch_authorized": (
            SUCCESSOR_MODEL_RUN_DISPATCH_AUTHORIZED
        ),
        "authoritative_successor_model_result_execution_authorized": (
            AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": (
            SUCCESSOR_MODEL_PROTOCOL_RESULT_AUTHORIZED
        ),
        "model_fit_authorized": SUCCESSOR_MODEL_FIT_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


def require_authoritative_successor_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = validate_successor_model_workflow_sources(
        repository_root=repository_root,
    )
    commit = _validate_commit(
        code_commit,
        field="EXP-045 model execution code commit",
    )

    if SUCCESSOR_MODEL_RUN_DISPATCH_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-045 model-run dispatch is not authorized"
        )
    if (
        AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-045 authoritative model-result execution is not authorized"
        )
    if SUCCESSOR_MODEL_PROTOCOL_RESULT_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-045 model-protocol result is not authorized"
        )
    if SUCCESSOR_MODEL_FIT_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-045 model fitting is not authorized"
        )

    return {
        **source,
        "code_commit": commit,
        "successor_model_run_dispatch_authorized": True,
        "authoritative_successor_model_result_execution_authorized": True,
        "model_protocol_result_authorized": True,
        "model_fit_authorized": True,
        "promotion_authorized": False,
        "trading_authorized": False,
    }


__all__ = [
    "AUTHORIZED_PYTHON_VERSION",
    "AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "DEC094_FAILURE_REVIEW_BLOB_SHA",
    "DEC095_PROTOCOL_BLOB_SHA",
    "DEC096_CORE_BLOB_SHA",
    "DEC097_MERGED_COMMIT",
    "DEC097_RUNNER_BLOB_SHA",
    "FEATURE_SCHEMA_BLOB_SHA",
    "LEGACY_DATA_LOADER_BLOB_SHA",
    "MARKET_CONTRACTS_BLOB_SHA",
    "MARKET_OUTCOMES_BLOB_SHA",
    "PREPROCESSING_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "PYPROJECT_BLOB_SHA",
    "SUCCESSOR_CLI_BLOB_SHA",
    "SUCCESSOR_MODEL_EXECUTION_GATE_DECISION",
    "SUCCESSOR_MODEL_FIT_AUTHORIZED",
    "SUCCESSOR_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "SUCCESSOR_MODEL_RUN_DISPATCH_AUTHORIZED",
    "SUCCESSOR_MODEL_WORKFLOW_FILE",
    "SUCCESSOR_MODEL_WORKFLOW_NAME",
    "SUCCESSOR_MODEL_WORKFLOW_SOURCE_FROZEN",
    "SUCCESSOR_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "SUCCESSOR_WORKFLOW_BLOB_SHA",
    "TRADING_AUTHORIZED",
    "build_successor_model_workflow_source_gate",
    "require_authoritative_successor_model_execution",
    "validate_successor_model_workflow_sources",
]
