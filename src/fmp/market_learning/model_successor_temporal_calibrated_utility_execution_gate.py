from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_temporal_calibrated_utility_artifacts import (
    AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_temporal_calibrated_utility_artifact_runner_sources,
)
from .model_successor_temporal_calibrated_utility_protocol import (
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION,
    TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION,
)
from .model_successor_temporal_calibrated_utility_training import (
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION,
    TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_VERSION,
)


TEMPORAL_CALIBRATED_UTILITY_MODEL_EXECUTION_GATE_DECISION = "DEC-153"
TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_FILE = (
    "phase8a-exp051-temporal-calibrated-utility-model-training.yml"
)
TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_NAME = (
    "phase8a-exp051-temporal-calibrated-utility-model-training"
)

DEC150_MERGED_COMMIT = (
    "b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833"
)
DEC151_MERGED_COMMIT = (
    "68028ef37b72e3f0695b475928434ede40ad7690"
)
DEC152_MERGED_COMMIT = (
    "9f8fc93096fb29579924932c5c3b526598afaf28"
)

DEC152_RUNNER_BLOB_SHA = (
    "3b25ad8dee80ad2d68a421b01b3e7789b1de9f1a"
)
DEC151_CORE_BLOB_SHA = (
    "959fbfd52f41c08de3c1a26769e0e7fd2545b92a"
)
DEC150_PROTOCOL_BLOB_SHA = (
    "c39309c4115cae1ea058e56f30cae4af6407e36e"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)

TEMPORAL_CALIBRATED_UTILITY_WORKFLOW_BLOB_SHA = (
    "4ab7480e31e91cbfe39eb5e289eccadde428d1a4"
)
TEMPORAL_CALIBRATED_UTILITY_CLI_BLOB_SHA = (
    "c88b05a14bc961391ff59e29f742c1dac27272b6"
)
TEMPORAL_CALIBRATED_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA = (
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

TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN = True
TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = False
AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = (
    False
)
TEMPORAL_CALIBRATED_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = False
TEMPORAL_CALIBRATED_UTILITY_MODEL_FIT_AUTHORIZED = False
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


def validate_temporal_calibrated_utility_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = (
        validate_temporal_calibrated_utility_artifact_runner_sources(
            repository_root=root,
        )
    )
    if runner.get(
        "temporal_calibrated_utility_model_artifact_runner_decision"
    ) != TEMPORAL_CALIBRATED_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION:
        raise ValueError(
            "EXP-051 artifact-runner decision drift"
        )
    if runner.get(
        "temporal_calibrated_utility_model_artifact_runner_version"
    ) != TEMPORAL_CALIBRATED_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION:
        raise ValueError(
            "EXP-051 artifact-runner version drift"
        )

    if TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION != "DEC-150":
        raise ValueError(
            "EXP-051 protocol decision drift"
        )
    if TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp051-temporal-calibrated-utility-protocol-v1"
    ):
        raise ValueError(
            "EXP-051 protocol version drift"
        )
    if TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION != "DEC-151":
        raise ValueError(
            "EXP-051 training-core decision drift"
        )
    if TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_VERSION != (
        "fmp-exp051-temporal-calibrated-utility-training-core-v1"
    ):
        raise ValueError(
            "EXP-051 training-core version drift"
        )
    if (
        TEMPORAL_CALIBRATED_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        != "DEC-152"
    ):
        raise ValueError(
            "EXP-051 artifact-runner decision drift"
        )
    if (
        TEMPORAL_CALIBRATED_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        != "fmp-exp051-temporal-calibrated-utility-artifact-runner-v1"
    ):
        raise ValueError(
            "EXP-051 artifact-runner version constant drift"
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
            TEMPORAL_CALIBRATED_UTILITY_RESULT_EXECUTION_AUTHORIZED,
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
                f"EXP-051 {field} drift"
            )

    expected = {
        "temporal_calibrated_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_calibrated_utility_artifacts.py",
            DEC152_RUNNER_BLOB_SHA,
        ),
        "temporal_calibrated_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_calibrated_utility_training.py",
            DEC151_CORE_BLOB_SHA,
        ),
        "temporal_calibrated_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_calibrated_utility_protocol.py",
            DEC150_PROTOCOL_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root
            / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp051-temporal-calibrated-utility-model-training.yml",
            TEMPORAL_CALIBRATED_UTILITY_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root
            / "scripts/phase8a_exp051_model_run.py",
            TEMPORAL_CALIBRATED_UTILITY_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root
            / "requirements/exp051-model-run.txt",
            TEMPORAL_CALIBRATED_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
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
                f"missing frozen EXP-051 workflow source: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-051 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        **runner,
        "temporal_calibrated_utility_model_execution_gate_decision": (
            TEMPORAL_CALIBRATED_UTILITY_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec150_merged_commit": DEC150_MERGED_COMMIT,
        "dec151_merged_commit": DEC151_MERGED_COMMIT,
        "dec152_merged_commit": DEC152_MERGED_COMMIT,
        "temporal_calibrated_utility_runner_blob_sha": actual[
            "temporal_calibrated_runner"
        ],
        "temporal_calibrated_utility_core_blob_sha": actual[
            "temporal_calibrated_core"
        ],
        "temporal_calibrated_utility_protocol_blob_sha": actual[
            "temporal_calibrated_protocol"
        ],
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "temporal_calibrated_utility_workflow_blob_sha": actual[
            "workflow"
        ],
        "temporal_calibrated_utility_cli_blob_sha": actual[
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


def build_temporal_calibrated_utility_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = (
        validate_temporal_calibrated_utility_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    return {
        **source,
        "stage": (
            "TEMPORAL_CALIBRATED_UTILITY_MODEL_"
            "RUN_WORKFLOW_SOURCE_FROZEN"
        ),
        "next_action": (
            "A later separate decision must predeclare terminal review "
            "before any guarded EXP-051 historical model-result run may "
            "be considered. DEC-153 does not authorize or dispatch execution."
        ),
        "temporal_calibrated_utility_model_workflow_source_frozen": (
            TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        ),
        "temporal_calibrated_utility_model_run_dispatch_authorized": (
            TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        ),
        "authoritative_temporal_calibrated_utility_model_result_execution_authorized": (
            AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": (
            TEMPORAL_CALIBRATED_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        ),
        "model_fit_authorized": (
            TEMPORAL_CALIBRATED_UTILITY_MODEL_FIT_AUTHORIZED
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


def require_authoritative_temporal_calibrated_utility_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = (
        validate_temporal_calibrated_utility_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    commit = _validate_commit(
        code_commit,
        field="EXP-051 model execution code commit",
    )

    if (
        TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-051 model-run dispatch is not authorized"
        )
    if (
        AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-051 authoritative model-result execution "
            "is not authorized"
        )
    if (
        TEMPORAL_CALIBRATED_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-051 model-protocol result is not authorized"
        )
    if (
        TEMPORAL_CALIBRATED_UTILITY_MODEL_FIT_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "EXP-051 model fitting is not authorized"
        )

    return {
        **source,
        "code_commit": commit,
        "temporal_calibrated_utility_model_run_dispatch_authorized": True,
        "authoritative_temporal_calibrated_utility_model_result_execution_authorized": (
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


__all__ = [
    "AUTHORIZED_PYTHON_VERSION",
    "AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC150_MERGED_COMMIT",
    "DEC150_PROTOCOL_BLOB_SHA",
    "DEC151_CORE_BLOB_SHA",
    "DEC151_MERGED_COMMIT",
    "DEC152_MERGED_COMMIT",
    "DEC152_RUNNER_BLOB_SHA",
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
    "TEMPORAL_CALIBRATED_UTILITY_CLI_BLOB_SHA",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_EXECUTION_GATE_DECISION",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_FIT_AUTHORIZED",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_FILE",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_NAME",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN",
    "TEMPORAL_CALIBRATED_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "TEMPORAL_CALIBRATED_UTILITY_WORKFLOW_BLOB_SHA",
    "TRADING_AUTHORIZED",
    "build_temporal_calibrated_utility_model_workflow_source_gate",
    "require_authoritative_temporal_calibrated_utility_model_execution",
    "validate_temporal_calibrated_utility_model_workflow_sources",
]
