from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_regime_utility_artifacts import (
    AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
    REGIME_UTILITY_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_regime_utility_artifact_runner_sources,
)
from .model_successor_regime_utility_protocol import (
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
    REGIME_UTILITY_PROTOCOL_DECISION,
    REGIME_UTILITY_PROTOCOL_VERSION,
)
from .model_successor_regime_utility_training import (
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
    REGIME_UTILITY_TRAINING_CORE_DECISION,
    REGIME_UTILITY_TRAINING_CORE_VERSION,
    REGIME_UTILITY_RESULT_EXECUTION_AUTHORIZED,
)


REGIME_UTILITY_MODEL_EXECUTION_GATE_DECISION = "DEC-135"
REGIME_UTILITY_MODEL_WORKFLOW_FILE = (
    "phase8a-exp049-regime-utility-model-training.yml"
)
REGIME_UTILITY_MODEL_WORKFLOW_NAME = (
    "phase8a-exp049-regime-utility-model-training"
)

DEC132_MERGED_COMMIT = (
    "d17326eebf6b456211225d7bad3a182a0307b707"
)
DEC133_MERGED_COMMIT = (
    "a6420e35a9219c81e65c5179843488f94b6668d3"
)
DEC134_MERGED_COMMIT = (
    "1576336d8faaf146aaa11d4213b21e69134ceaa7"
)

DEC134_RUNNER_BLOB_SHA = (
    "6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13"
)
DEC133_CORE_BLOB_SHA = (
    "e1018b20210b7bb8d666071d8eb878aba5899111"
)
DEC132_PROTOCOL_BLOB_SHA = (
    "ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)

REGIME_UTILITY_WORKFLOW_BLOB_SHA = (
    "955152835ec1cedf39d6d31e54d6028a7953fab5"
)
REGIME_UTILITY_CLI_BLOB_SHA = (
    "cba5ece4eda8e02a7ca07a780d8caa69a239e094"
)
REGIME_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA = (
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

REGIME_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN = True
REGIME_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = False
AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = False
REGIME_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = False
REGIME_UTILITY_MODEL_FIT_AUTHORIZED = False
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


def validate_regime_utility_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = validate_regime_utility_artifact_runner_sources(
        repository_root=root,
    )
    if (
        runner.get("regime_utility_model_artifact_runner_decision")
        != REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
    ):
        raise ValueError(
            "EXP-049 artifact-runner decision drift"
        )
    if (
        runner.get("regime_utility_model_artifact_runner_version")
        != REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
    ):
        raise ValueError(
            "EXP-049 artifact-runner version drift"
        )

    if REGIME_UTILITY_PROTOCOL_DECISION != "DEC-132":
        raise ValueError(
            "EXP-049 protocol decision drift"
        )
    if (
        REGIME_UTILITY_PROTOCOL_VERSION
        != "fmp-exp049-regime-utility-protocol-v1"
    ):
        raise ValueError(
            "EXP-049 protocol version drift"
        )
    if REGIME_UTILITY_TRAINING_CORE_DECISION != "DEC-133":
        raise ValueError(
            "EXP-049 training-core decision drift"
        )
    if (
        REGIME_UTILITY_TRAINING_CORE_VERSION
        != "fmp-exp049-regime-utility-training-core-v1"
    ):
        raise ValueError(
            "EXP-049 training-core version drift"
        )
    if REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION != "DEC-134":
        raise ValueError(
            "EXP-049 artifact-runner constant drift"
        )
    if (
        REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        != "fmp-exp049-regime-utility-artifact-runner-v1"
    ):
        raise ValueError(
            "EXP-049 artifact-runner version constant drift"
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
            REGIME_UTILITY_RESULT_EXECUTION_AUTHORIZED,
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
                f"EXP-049 {field} drift"
            )

    expected = {
        "regime_utility_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_utility_artifacts.py",
            DEC134_RUNNER_BLOB_SHA,
        ),
        "regime_utility_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_utility_training.py",
            DEC133_CORE_BLOB_SHA,
        ),
        "regime_utility_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_utility_protocol.py",
            DEC132_PROTOCOL_BLOB_SHA,
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
            "phase8a-exp049-regime-utility-model-training.yml",
            REGIME_UTILITY_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root
            / "scripts/"
            "phase8a_exp047_model_run.py",
            REGIME_UTILITY_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root
            / "requirements/"
            "exp047-model-run.txt",
            REGIME_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
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
                f"missing frozen EXP-049 workflow source: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-049 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        **runner,
        "regime_utility_model_execution_gate_decision": (
            REGIME_UTILITY_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec132_merged_commit": DEC132_MERGED_COMMIT,
        "dec133_merged_commit": DEC133_MERGED_COMMIT,
        "dec134_merged_commit": DEC134_MERGED_COMMIT,
        "regime_utility_runner_blob_sha": actual[
            "regime_utility_runner"
        ],
        "regime_utility_core_blob_sha": actual[
            "regime_utility_core"
        ],
        "regime_utility_protocol_blob_sha": actual[
            "regime_utility_protocol"
        ],
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "regime_utility_workflow_blob_sha": actual[
            "workflow"
        ],
        "regime_utility_cli_blob_sha": actual["cli"],
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


def build_regime_utility_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_regime_utility_model_workflow_sources(
        repository_root=repository_root,
    )
    return {
        **source,
        "stage": "REGIME_UTILITY_MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        "next_action": (
            "A later separate decision may authorize at most a "
            "guarded EXP-049 historical model-result run. "
            "DEC-135 does not authorize or dispatch execution."
        ),
        "regime_utility_model_workflow_source_frozen": (
            REGIME_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        ),
        "regime_utility_model_run_dispatch_authorized": (
            REGIME_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        ),
        "authoritative_regime_utility_model_result_execution_authorized": (
            AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": (
            REGIME_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        ),
        "model_fit_authorized": (
            REGIME_UTILITY_MODEL_FIT_AUTHORIZED
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


def require_authoritative_regime_utility_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = validate_regime_utility_model_workflow_sources(
        repository_root=repository_root,
    )
    commit = _validate_commit(
        code_commit,
        field="EXP-049 model execution code commit",
    )

    if REGIME_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-049 model-run dispatch is not authorized"
        )
    if (
        AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-049 authoritative model-result execution "
            "is not authorized"
        )
    if (
        REGIME_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-049 model-protocol result is not authorized"
        )
    if REGIME_UTILITY_MODEL_FIT_AUTHORIZED is not True:
        raise PermissionError(
            "EXP-049 model fitting is not authorized"
        )

    return {
        **source,
        "code_commit": commit,
        "regime_utility_model_run_dispatch_authorized": True,
        "authoritative_regime_utility_model_result_execution_authorized": True,
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
    "AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC132_MERGED_COMMIT",
    "DEC132_PROTOCOL_BLOB_SHA",
    "DEC133_CORE_BLOB_SHA",
    "DEC133_MERGED_COMMIT",
    "DEC134_MERGED_COMMIT",
    "DEC134_RUNNER_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "REGIME_UTILITY_CLI_BLOB_SHA",
    "REGIME_UTILITY_MODEL_EXECUTION_GATE_DECISION",
    "REGIME_UTILITY_MODEL_FIT_AUTHORIZED",
    "REGIME_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "REGIME_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED",
    "REGIME_UTILITY_MODEL_WORKFLOW_FILE",
    "REGIME_UTILITY_MODEL_WORKFLOW_NAME",
    "REGIME_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN",
    "REGIME_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "REGIME_UTILITY_WORKFLOW_BLOB_SHA",
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
    "build_regime_utility_model_workflow_source_gate",
    "require_authoritative_regime_utility_model_execution",
    "validate_regime_utility_model_workflow_sources",
]
