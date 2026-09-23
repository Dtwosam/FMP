from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .model_artifacts import (
    AUTHORITATIVE_PROTOCOL_FINGERPRINT,
    MODEL_ARTIFACT_RUNNER_DECISION,
    MODEL_ARTIFACT_RUNNER_VERSION,
)
from .model_protocol import (
    MODEL_PROTOCOL_DECISION,
    MODEL_PROTOCOL_VERSION,
    protocol_fingerprint,
)
from .model_training import (
    MODEL_TRAINING_CORE_DECISION,
    MODEL_TRAINING_CORE_VERSION,
)


MODEL_EXECUTION_GATE_DECISION = "DEC-092"
MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-094"
MODEL_WORKFLOW_FILE = "phase8a-exp044-model-training.yml"
MODEL_WORKFLOW_NAME = "phase8a-exp044-model-training"

DEC091_MERGED_COMMIT = "397ef1410fe92b376431a66f5a7e3ee44d71dec6"
DEC092_MERGED_COMMIT = "9645bae73ec1d113383c9957569c6e05a70b2e96"
DEC092_WORKFLOW_BLOB_SHA = "004f6c0062b6e5c1e15dcd507ea19b288b821e40"
DEC093_WORKFLOW_BLOB_SHA = "491a9ab5ac688402ef71506e1207463940c8931b"
DEC094_WORKFLOW_BLOB_SHA = "37164e5d2dd06848e5f76ef50a6731017300beaa"
DEC092_CLI_BLOB_SHA = "daae5b3a54a3412e799a8ec44206724859a74ba4"
DEC092_GATE_BLOB_SHA = "74639615946dba49e742e0d6738b9c8d34855340"
DEC092_OPERATOR_BLOB_SHA = "97a13779c7f5425697487a5a8772613e48362556"
AUTHORIZED_PYTHON_VERSION = "3.12.14"
EXP044_RUNTIME_REQUIREMENTS_BLOB_SHA = "d25ab16056b9f5df283147d67b8f401f60ae7520"
PYPROJECT_BLOB_SHA = "de850a1ba397fc69ba634ecf178d732b5012c378"
PREPROCESSING_BLOB_SHA = "fcc42f45b9588d38311bc66bc454e6ea0a563e54"
FEATURE_SCHEMA_BLOB_SHA = "afbddc84676faadb8660b4da03c6abeb10cd2a13"
MARKET_CONTRACTS_BLOB_SHA = "4c5a75232e66715c0829e545d8659f59fb8b7724"
MARKET_OUTCOMES_BLOB_SHA = "c83fefd4252b2fe426af97686f86e43021760c77"
DEC091_RUNNER_BLOB_SHA = "27c0848d16722a22b4762f5842396c2aebc92bec"
DEC094_ARTIFACT_RUNNER_BLOB_SHA = "f050f82e9d0dbf641bf02d206d5ecd877e4446fa"
DEC094_RESULT_VALIDATOR_BLOB_SHA = "f7f73da8fa7db0e34f20307ab155599b910714fd"
DEC090_CORE_BLOB_SHA = "34b50a3f907d26b1c5ec50a0a0b444a3417d04f7"
DEC094_CORE_BLOB_SHA = "a6092dbe1d36f81e1929bf1f18ba43f4ec494ebc"
REVIEWED_FAILED_MODEL_RUN_ID = 35891605645
DEC088_PROTOCOL_BLOB_SHA = "549b2a04f961d9d8ad83caea9c02b40ee54adec2"

MODEL_RUN_WORKFLOW_SOURCE_FROZEN = True
MODEL_RUN_DISPATCH_AUTHORIZED = True
AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED = True
MODEL_PROTOCOL_RESULT_AUTHORIZED = True
MODEL_FIT_AUTHORIZED = True


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


def validate_frozen_model_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    if MODEL_ARTIFACT_RUNNER_DECISION != "DEC-091":
        raise ValueError("EXP-044 artifact-runner decision drift")
    if MODEL_ARTIFACT_RUNNER_VERSION != "fmp-exp044-model-artifact-runner-v1":
        raise ValueError("EXP-044 artifact-runner version drift")
    if MODEL_TRAINING_CORE_DECISION != "DEC-090":
        raise ValueError("EXP-044 training-core decision drift")
    if MODEL_TRAINING_CORE_VERSION != "fmp-exp044-model-training-core-v1":
        raise ValueError("EXP-044 training-core version drift")
    if MODEL_PROTOCOL_DECISION != "DEC-088":
        raise ValueError("EXP-044 model-protocol decision drift")
    if MODEL_PROTOCOL_VERSION != "fmp-exp044-model-protocol-v1":
        raise ValueError("EXP-044 model-protocol version drift")
    if protocol_fingerprint() != AUTHORITATIVE_PROTOCOL_FINGERPRINT:
        raise ValueError("EXP-044 model-protocol fingerprint drift")

    expected = {
        "artifact_runner": (
            root / "src/fmp/market_learning/model_artifacts.py",
            DEC094_ARTIFACT_RUNNER_BLOB_SHA,
        ),
        "result_validator": (
            root / "src/fmp/market_learning/model_result_evidence.py",
            DEC094_RESULT_VALIDATOR_BLOB_SHA,
        ),
        "training_core": (
            root / "src/fmp/market_learning/model_training.py",
            DEC094_CORE_BLOB_SHA,
        ),
        "model_protocol": (
            root / "src/fmp/market_learning/model_protocol.py",
            DEC088_PROTOCOL_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing frozen EXP-044 source file: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-044 frozen {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "model_run_workflow_source_frozen": MODEL_RUN_WORKFLOW_SOURCE_FROZEN,
        "dec091_merged_commit": DEC091_MERGED_COMMIT,
        "dec091_runner_blob_sha": DEC091_RUNNER_BLOB_SHA,
        "artifact_runner_blob_sha": actual["artifact_runner"],
        "result_validator_blob_sha": actual["result_validator"],
        "dec090_core_blob_sha": DEC090_CORE_BLOB_SHA,
        "training_core_blob_sha": actual["training_core"],
        "model_protocol_blob_sha": actual["model_protocol"],
        "model_protocol_fingerprint": AUTHORITATIVE_PROTOCOL_FINGERPRINT,
    }


def validate_authorized_model_execution_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    upstream = validate_frozen_model_sources(
        repository_root=root,
    )
    expected = {
        "model_workflow": (
            root / ".github/workflows/phase8a-exp044-model-training.yml",
            DEC094_WORKFLOW_BLOB_SHA,
        ),
        "model_cli": (
            root / "scripts/phase8a_exp044_model_run.py",
            DEC092_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp044-model-run.txt",
            EXP044_RUNTIME_REQUIREMENTS_BLOB_SHA,
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
                f"missing authorized EXP-044 execution source file: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-044 authorized {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return {
        **upstream,
        "dec092_merged_commit": DEC092_MERGED_COMMIT,
        "dec092_workflow_blob_sha": DEC092_WORKFLOW_BLOB_SHA,
        "dec093_workflow_blob_sha": DEC093_WORKFLOW_BLOB_SHA,
        "dec094_workflow_blob_sha": actual["model_workflow"],
        "reviewed_failed_model_run_id": REVIEWED_FAILED_MODEL_RUN_ID,
        "dec092_cli_blob_sha": actual["model_cli"],
        "authorized_python_version": AUTHORIZED_PYTHON_VERSION,
        "runtime_requirements_blob_sha": actual["runtime_requirements"],
        "pyproject_blob_sha": actual["pyproject"],
        "preprocessing_blob_sha": actual["preprocessing"],
        "feature_schema_blob_sha": actual["feature_schema"],
        "market_contracts_blob_sha": actual["market_contracts"],
        "market_outcomes_blob_sha": actual["market_outcomes"],
        "dec092_gate_blob_sha": DEC092_GATE_BLOB_SHA,
        "dec092_operator_blob_sha": DEC092_OPERATOR_BLOB_SHA,
    }


def build_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_authorized_model_execution_sources(
        repository_root=repository_root,
    )
    return {
        **source,
        "stage": "MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        "next_action": (
            "DEC-094 authorizes exactly one reviewed replacement model-result run "
            "after failed run 35891605645. Inspect workflow state before dispatch."
        ),
        "model_execution_authorization_decision": (
            MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "model_run_dispatch_authorized": MODEL_RUN_DISPATCH_AUTHORIZED,
        "authoritative_model_result_execution_authorized": (
            AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": MODEL_PROTOCOL_RESULT_AUTHORIZED,
        "model_fit_authorized": MODEL_FIT_AUTHORIZED,
        "promotion_authorized": False,
        "trading_authorized": False,
    }


def require_authoritative_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = validate_authorized_model_execution_sources(
        repository_root=repository_root,
    )
    commit = _validate_commit(
        code_commit,
        field="EXP-044 model execution code commit",
    )

    if MODEL_RUN_DISPATCH_AUTHORIZED is not True:
        raise PermissionError("EXP-044 model-run dispatch is not authorized")
    if AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-044 authoritative model-result execution is not authorized"
        )
    if MODEL_PROTOCOL_RESULT_AUTHORIZED is not True:
        raise PermissionError("EXP-044 model-protocol result is not authorized")
    if MODEL_FIT_AUTHORIZED is not True:
        raise PermissionError("EXP-044 model fitting is not authorized")

    return {
        **source,
        "code_commit": commit,
        "model_run_dispatch_authorized": True,
        "authoritative_model_result_execution_authorized": True,
        "model_protocol_result_authorized": True,
        "model_fit_authorized": True,
        "promotion_authorized": False,
        "trading_authorized": False,
    }


__all__ = [
    "AUTHORIZED_PYTHON_VERSION",
    "AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "DEC088_PROTOCOL_BLOB_SHA",
    "DEC090_CORE_BLOB_SHA",
    "DEC091_MERGED_COMMIT",
    "DEC094_ARTIFACT_RUNNER_BLOB_SHA",
    "DEC094_RESULT_VALIDATOR_BLOB_SHA",
    "DEC092_CLI_BLOB_SHA",
    "DEC092_GATE_BLOB_SHA",
    "DEC092_MERGED_COMMIT",
    "DEC092_OPERATOR_BLOB_SHA",
    "DEC092_WORKFLOW_BLOB_SHA",
    "DEC093_WORKFLOW_BLOB_SHA",
    "DEC094_CORE_BLOB_SHA",
    "DEC094_WORKFLOW_BLOB_SHA",
    "EXP044_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "FEATURE_SCHEMA_BLOB_SHA",
    "MARKET_CONTRACTS_BLOB_SHA",
    "MARKET_OUTCOMES_BLOB_SHA",
    "PREPROCESSING_BLOB_SHA",
    "PYPROJECT_BLOB_SHA",
    "DEC091_RUNNER_BLOB_SHA",
    "MODEL_EXECUTION_AUTHORIZATION_DECISION",
    "MODEL_EXECUTION_GATE_DECISION",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "MODEL_RUN_DISPATCH_AUTHORIZED",
    "MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
    "REVIEWED_FAILED_MODEL_RUN_ID",
    "MODEL_WORKFLOW_FILE",
    "MODEL_WORKFLOW_NAME",
    "build_model_workflow_source_gate",
    "require_authoritative_model_execution",
    "validate_authorized_model_execution_sources",
    "validate_frozen_model_sources",
]
