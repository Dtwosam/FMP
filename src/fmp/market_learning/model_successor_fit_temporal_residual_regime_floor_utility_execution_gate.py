from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_fit_temporal_residual_regime_floor_utility_artifacts import (
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_fit_temporal_residual_regime_floor_utility_artifact_contract_sources,
)
from .model_successor_fit_temporal_residual_regime_floor_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
)
from .model_successor_fit_temporal_residual_regime_floor_utility_training import (
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_TRAINING_CORE_VERSION,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
)


FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_EXECUTION_GATE_DECISION = (
    "DEC-234"
)
FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_WORKFLOW_FILE = (
    "phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training.yml"
)
FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_WORKFLOW_NAME = (
    "phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training"
)

DEC231_MERGED_COMMIT = "a6926703d787a7fe0e2ba34261d14c4c4d362df2"
DEC232_MERGED_COMMIT = "24cb20bb0b1e3aa25f1ea87e1cfbba22587a0ae6"
DEC233_MERGED_COMMIT = "5425184a53b2bd5241291f9d561f47b69ca4d134"

DEC233_RUNNER_BLOB_SHA = "5a34f354b68e14bb7116c79f15f9cfebe149a811"
DEC232_CORE_BLOB_SHA = "77f2010574b3d8ecc958930d5bfadf7ddb4f2231"
DEC231_PROTOCOL_BLOB_SHA = "8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2"
LEGACY_DATA_LOADER_BLOB_SHA = "27c0848d16722a22b4762f5842396c2aebc92bec"

FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_WORKFLOW_BLOB_SHA = (
    "78e9bf66ade5f6fb42ebe27e28b7ba24f36741b8"
)
FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_CLI_BLOB_SHA = (
    "e35a6ee0ff11bd3928b3bf05bf19f3572f64952c"
)
FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA = (
    "d25ab16056b9f5df283147d67b8f401f60ae7520"
)
PYPROJECT_BLOB_SHA = "de850a1ba397fc69ba634ecf178d732b5012c378"
PREPROCESSING_BLOB_SHA = "fcc42f45b9588d38311bc66bc454e6ea0a563e54"
FEATURE_SCHEMA_BLOB_SHA = "afbddc84676faadb8660b4da03c6abeb10cd2a13"
MARKET_CONTRACTS_BLOB_SHA = "4c5a75232e66715c0829e545d8659f59fb8b7724"
MARKET_OUTCOMES_BLOB_SHA = "c83fefd4252b2fe426af97686f86e43021760c77"

AUTHORIZED_PYTHON_VERSION = "3.12.14"

FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN = True
FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = False
AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_FIT_AUTHORIZED = False
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


def validate_fit_temporal_residual_regime_floor_utility_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = (
        validate_fit_temporal_residual_regime_floor_utility_artifact_contract_sources(
            repository_root=root,
        )
    )
    if runner.get("artifact_contract_decision") != (
        FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
    ):
        raise ValueError("EXP-058 artifact-contract decision drift")
    if runner.get("artifact_contract_version") != (
        FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
    ):
        raise ValueError("EXP-058 artifact-contract version drift")

    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_DECISION != "DEC-231":
        raise ValueError("EXP-058 protocol decision drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp058-fit-temporal-residual-lower-tail-utility-"
        "implementation-repair-protocol-v1"
    ):
        raise ValueError("EXP-058 protocol version drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_TRAINING_CORE_DECISION != "DEC-232":
        raise ValueError("EXP-058 training-core decision drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_TRAINING_CORE_VERSION != (
        "fmp-exp058-fit-temporal-residual-lower-tail-utility-"
        "implementation-repair-training-core-v1"
    ):
        raise ValueError("EXP-058 training-core version drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION != "DEC-233":
        raise ValueError("EXP-058 artifact-contract decision drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION != (
        "fmp-exp058-fit-temporal-residual-lower-tail-utility-"
        "implementation-repair-artifact-contract-v1"
    ):
        raise ValueError("EXP-058 artifact-contract version constant drift")

    for field, value in (
        ("protocol result authorization", PROTOCOL_RESULT_AUTHORIZED),
        ("protocol execution authorization", PROTOCOL_EXECUTION_AUTHORIZED),
        ("protocol fit authorization", PROTOCOL_MODEL_FIT_AUTHORIZED),
        (
            "training execution authorization",
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RESULT_EXECUTION_AUTHORIZED,
        ),
        ("training-core fit authorization", CORE_MODEL_FIT_AUTHORIZED),
        ("artifact-contract execution authorization", RUNNER_EXECUTION_AUTHORIZED),
        ("artifact-contract fit authorization", RUNNER_MODEL_FIT_AUTHORIZED),
    ):
        if value is not False:
            raise ValueError(f"EXP-058 {field} drift")

    expected = {
        "residual_regime_floor_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_floor_utility_artifacts.py",
            DEC233_RUNNER_BLOB_SHA,
        ),
        "residual_regime_floor_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_floor_utility_training.py",
            DEC232_CORE_BLOB_SHA,
        ),
        "residual_regime_floor_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_floor_utility_protocol.py",
            DEC231_PROTOCOL_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training.yml",
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root / "scripts/phase8a_exp058_model_run.py",
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp058-model-run.txt",
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
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
            raise ValueError(f"missing EXP-058 workflow dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-058 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "fit_temporal_residual_regime_floor_utility_model_execution_gate_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec231_merged_commit": DEC231_MERGED_COMMIT,
        "dec232_merged_commit": DEC232_MERGED_COMMIT,
        "dec233_merged_commit": DEC233_MERGED_COMMIT,
        "fit_temporal_residual_regime_floor_utility_runner_blob_sha": actual[
            "residual_regime_floor_runner"
        ],
        "fit_temporal_residual_regime_floor_utility_core_blob_sha": actual[
            "residual_regime_floor_core"
        ],
        "fit_temporal_residual_regime_floor_utility_protocol_blob_sha": actual[
            "residual_regime_floor_protocol"
        ],
        "legacy_data_loader_blob_sha": actual["legacy_data_loader"],
        "fit_temporal_residual_regime_floor_utility_workflow_blob_sha": actual[
            "workflow"
        ],
        "fit_temporal_residual_regime_floor_utility_cli_blob_sha": actual["cli"],
        "runtime_requirements_blob_sha": actual["runtime_requirements"],
        "pyproject_blob_sha": actual["pyproject"],
        "preprocessing_blob_sha": actual["preprocessing"],
        "feature_schema_blob_sha": actual["feature_schema"],
        "market_contracts_blob_sha": actual["market_contracts"],
        "market_outcomes_blob_sha": actual["market_outcomes"],
        "authorized_python_version": AUTHORIZED_PYTHON_VERSION,
        "fit_temporal_residual_regime_floor_utility_model_workflow_source_frozen": True,
        "fit_temporal_residual_regime_floor_utility_model_run_dispatch_authorized": False,
        "authoritative_fit_temporal_residual_regime_floor_utility_model_result_execution_authorized": False,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def build_fit_temporal_residual_regime_floor_utility_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = (
        validate_fit_temporal_residual_regime_floor_utility_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    return {
        **source,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_"
            "RUN_WORKFLOW_SOURCE_FROZEN"
        ),
        "next_action": (
            "A later separate decision must predeclare terminal review "
            "before any guarded EXP-058 historical model-result run may "
            "be considered. DEC-234 does not authorize or dispatch execution."
        ),
    }


def require_authoritative_fit_temporal_residual_regime_floor_utility_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = (
        validate_fit_temporal_residual_regime_floor_utility_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    commit = _validate_commit(code_commit, field="EXP-058 code commit")

    required_true = (
        FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
        AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
        FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
        FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_FIT_AUTHORIZED,
    )
    if not all(required_true):
        raise PermissionError(
            "DEC-234 freezes EXP-058 workflow source but does not "
            "authorize historical model-result execution"
        )

    return {
        **source,
        "code_commit": commit,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_"
            "EXECUTION_AUTHORIZED"
        ),
    }


__all__ = [
    "AUTHORIZED_PYTHON_VERSION",
    "AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC231_MERGED_COMMIT",
    "DEC231_PROTOCOL_BLOB_SHA",
    "DEC232_CORE_BLOB_SHA",
    "DEC232_MERGED_COMMIT",
    "DEC233_MERGED_COMMIT",
    "DEC233_RUNNER_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FEATURE_SCHEMA_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_CLI_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_EXECUTION_GATE_DECISION",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_FIT_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_WORKFLOW_FILE",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_WORKFLOW_NAME",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_WORKFLOW_BLOB_SHA",
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
    "build_fit_temporal_residual_regime_floor_utility_model_workflow_source_gate",
    "require_authoritative_fit_temporal_residual_regime_floor_utility_model_execution",
    "validate_fit_temporal_residual_regime_floor_utility_model_workflow_sources",
]
