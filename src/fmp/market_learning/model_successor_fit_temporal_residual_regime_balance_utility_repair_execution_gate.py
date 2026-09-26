from __future__ import annotations

import hashlib
from pathlib import Path

from .model_successor_fit_temporal_residual_regime_balance_utility_repair_artifacts import (
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED as RUNNER_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_VERSION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED as RUNNER_MODEL_FIT_AUTHORIZED,
    validate_fit_temporal_residual_regime_balance_utility_repair_artifact_contract_sources,
)
from .model_successor_fit_temporal_residual_regime_balance_utility_repair_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED as PROTOCOL_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as PROTOCOL_MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED as PROTOCOL_RESULT_AUTHORIZED,
)
from .model_successor_fit_temporal_residual_regime_balance_utility_repair_training import (
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_TRAINING_CORE_VERSION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED as CORE_MODEL_FIT_AUTHORIZED,
)


FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION = (
    "DEC-256"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION = (
    "DEC-258"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_FILE = (
    "phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_NAME = (
    "phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training"
)

DEC253_MERGED_COMMIT = "7e5b399cb7960d385d956b33e5d96cea85bb2c28"
DEC254_MERGED_COMMIT = "c8cac108bc098dbceda4b8903f5a56ac7f62bf47"
DEC255_MERGED_COMMIT = "d3a52722c178c96eb865791be096661007d16dd5"
DEC256_MERGED_COMMIT = "cef9f6d201bf2b025f08c924a11c84e9684b9ba0"
DEC257_MERGED_COMMIT = "5998292b80c0986bdcc0b9f2a91cb024ef92158a"

DEC255_RUNNER_BLOB_SHA = "2a6c550dcafac2e7013136fcbbef95b13c2e7d18"
DEC254_CORE_BLOB_SHA = "202dcaa8ba4ad25324fbe53d00e812c60fbb37dd"
DEC253_PROTOCOL_BLOB_SHA = "82d336250e2cdd9894afa5554c6b422e0de6b1fe"
DEC256_WORKFLOW_BLOB_SHA = "20af1bf2f9057274a8c50d5b48becbf5f683ef86"
DEC256_CLI_BLOB_SHA = "90c6bc9e893c813d394e3a9c4adc5a155e938af0"
DEC256_GATE_BLOB_SHA = "82f51bf85ccb1793b3a980b2884f3e122a03c8db"
DEC257_REVIEW_BLOB_SHA = "989ebc7b0cc33e5076f83ea94337fe6581c321e3"
LEGACY_DATA_LOADER_BLOB_SHA = "27c0848d16722a22b4762f5842396c2aebc92bec"

FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_WORKFLOW_BLOB_SHA = (
    "91a5bb720ca10b261533409e36f6143994afcca3"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_CLI_BLOB_SHA = (
    "90c6bc9e893c813d394e3a9c4adc5a155e938af0"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA = (
    "d25ab16056b9f5df283147d67b8f401f60ae7520"
)
PYPROJECT_BLOB_SHA = "de850a1ba397fc69ba634ecf178d732b5012c378"
PREPROCESSING_BLOB_SHA = "fcc42f45b9588d38311bc66bc454e6ea0a563e54"
FEATURE_SCHEMA_BLOB_SHA = "afbddc84676faadb8660b4da03c6abeb10cd2a13"
MARKET_CONTRACTS_BLOB_SHA = "4c5a75232e66715c0829e545d8659f59fb8b7724"
MARKET_OUTCOMES_BLOB_SHA = "c83fefd4252b2fe426af97686f86e43021760c77"

AUTHORIZED_PYTHON_VERSION = "3.12.14"

FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_SOURCE_FROZEN = True
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED = True
AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED = True
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED = True
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED = True
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


def validate_fit_temporal_residual_regime_balance_utility_repair_model_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    runner = (
        validate_fit_temporal_residual_regime_balance_utility_repair_artifact_contract_sources(
            repository_root=root,
        )
    )
    if runner.get("artifact_contract_decision") != (
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_DECISION
    ):
        raise ValueError("EXP-060 artifact-contract decision drift")
    if runner.get("artifact_contract_version") != (
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_VERSION
    ):
        raise ValueError("EXP-060 artifact-contract version drift")

    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_DECISION != "DEC-253":
        raise ValueError("EXP-060 protocol decision drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_VERSION != (
        "fmp-exp060-fit-temporal-residual-regime-balance-utility-implementation-repair-protocol-v1"
    ):
        raise ValueError("EXP-060 protocol version drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_TRAINING_CORE_DECISION != "DEC-254":
        raise ValueError("EXP-060 training-core decision drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_TRAINING_CORE_VERSION != (
        "fmp-exp060-fit-temporal-residual-regime-balance-utility-implementation-repair-training-core-v1"
    ):
        raise ValueError("EXP-060 training-core version drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_DECISION != "DEC-255":
        raise ValueError("EXP-060 artifact-contract decision drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_ARTIFACT_RUNNER_VERSION != (
        "fmp-exp060-fit-temporal-residual-regime-balance-utility-implementation-repair-artifact-contract-v1"
    ):
        raise ValueError("EXP-060 artifact-contract version constant drift")

    for field, value in (
        ("protocol result authorization", PROTOCOL_RESULT_AUTHORIZED),
        ("protocol execution authorization", PROTOCOL_EXECUTION_AUTHORIZED),
        ("protocol fit authorization", PROTOCOL_MODEL_FIT_AUTHORIZED),
        (
            "training execution authorization",
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_RESULT_EXECUTION_AUTHORIZED,
        ),
        ("training-core fit authorization", CORE_MODEL_FIT_AUTHORIZED),
        ("artifact-contract execution authorization", RUNNER_EXECUTION_AUTHORIZED),
        ("artifact-contract fit authorization", RUNNER_MODEL_FIT_AUTHORIZED),
    ):
        if value is not False:
            raise ValueError(f"EXP-060 {field} drift")

    expected = {
        "residual_regime_balance_repair_runner": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_balance_utility_repair_artifacts.py",
            DEC255_RUNNER_BLOB_SHA,
        ),
        "residual_regime_balance_repair_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_balance_utility_repair_training.py",
            DEC254_CORE_BLOB_SHA,
        ),
        "residual_regime_balance_repair_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_balance_utility_repair_protocol.py",
            DEC253_PROTOCOL_BLOB_SHA,
        ),
        "legacy_data_loader": (
            root / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "terminal_review": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_balance_utility_repair_result_review.py",
            DEC257_REVIEW_BLOB_SHA,
        ),
        "workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml",
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root / "scripts/phase8a_exp060_model_run.py",
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp060-model-run.txt",
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
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
            raise ValueError(f"missing EXP-060 workflow dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-060 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "fit_temporal_residual_regime_balance_utility_repair_model_execution_gate_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION
        ),
        "dec253_merged_commit": DEC253_MERGED_COMMIT,
        "dec254_merged_commit": DEC254_MERGED_COMMIT,
        "dec255_merged_commit": DEC255_MERGED_COMMIT,
        "dec256_merged_commit": DEC256_MERGED_COMMIT,
        "dec257_merged_commit": DEC257_MERGED_COMMIT,
        "dec256_workflow_blob_sha": DEC256_WORKFLOW_BLOB_SHA,
        "dec256_cli_blob_sha": DEC256_CLI_BLOB_SHA,
        "dec256_gate_blob_sha": DEC256_GATE_BLOB_SHA,
        "dec257_review_blob_sha": actual["terminal_review"],
        "fit_temporal_residual_regime_balance_utility_repair_model_execution_authorization_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "fit_temporal_residual_regime_balance_utility_repair_runner_blob_sha": actual[
            "residual_regime_balance_repair_runner"
        ],
        "fit_temporal_residual_regime_balance_utility_repair_core_blob_sha": actual[
            "residual_regime_balance_repair_core"
        ],
        "fit_temporal_residual_regime_balance_utility_repair_protocol_blob_sha": actual[
            "residual_regime_balance_repair_protocol"
        ],
        "legacy_data_loader_blob_sha": actual["legacy_data_loader"],
        "fit_temporal_residual_regime_balance_utility_workflow_blob_sha": actual[
            "workflow"
        ],
        "fit_temporal_residual_regime_balance_utility_cli_blob_sha": actual["cli"],
        "runtime_requirements_blob_sha": actual["runtime_requirements"],
        "pyproject_blob_sha": actual["pyproject"],
        "preprocessing_blob_sha": actual["preprocessing"],
        "feature_schema_blob_sha": actual["feature_schema"],
        "market_contracts_blob_sha": actual["market_contracts"],
        "market_outcomes_blob_sha": actual["market_outcomes"],
        "authorized_python_version": AUTHORIZED_PYTHON_VERSION,
        "fit_temporal_residual_regime_balance_utility_repair_model_workflow_source_frozen": True,
        "fit_temporal_residual_regime_balance_utility_repair_model_run_dispatch_authorized": True,
        "authoritative_fit_temporal_residual_regime_balance_utility_repair_model_result_execution_authorized": True,
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


def build_fit_temporal_residual_regime_balance_utility_repair_model_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = (
        validate_fit_temporal_residual_regime_balance_utility_repair_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    return {
        **source,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_"
            "RUN_DISPATCH_REQUIRED"
        ),
        "next_action": (
            "DEC-258 authorizes at most one guarded historical EXP-060 "
            "model-result run after merge. This source change does not "
            "dispatch the workflow."
        ),
    }


def require_authoritative_fit_temporal_residual_regime_balance_utility_repair_model_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = (
        validate_fit_temporal_residual_regime_balance_utility_repair_model_workflow_sources(
            repository_root=repository_root,
        )
    )
    commit = _validate_commit(code_commit, field="EXP-060 code commit")

    required_true = (
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED,
        AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED,
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED,
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED,
    )
    if not all(required_true):
        raise PermissionError(
            "DEC-258 EXP-060 historical model-result execution "
            "authorization is not open"
        )

    return {
        **source,
        "code_commit": commit,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_"
            "EXECUTION_AUTHORIZED"
        ),
    }


__all__ = [
    "AUTHORIZED_PYTHON_VERSION",
    "AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC253_MERGED_COMMIT",
    "DEC253_PROTOCOL_BLOB_SHA",
    "DEC254_CORE_BLOB_SHA",
    "DEC254_MERGED_COMMIT",
    "DEC255_MERGED_COMMIT",
    "DEC255_RUNNER_BLOB_SHA",
    "DEC256_CLI_BLOB_SHA",
    "DEC256_GATE_BLOB_SHA",
    "DEC256_MERGED_COMMIT",
    "DEC256_WORKFLOW_BLOB_SHA",
    "DEC257_MERGED_COMMIT",
    "DEC257_REVIEW_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FEATURE_SCHEMA_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_CLI_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_FILE",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_NAME",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_SOURCE_FROZEN",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_WORKFLOW_BLOB_SHA",
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
    "build_fit_temporal_residual_regime_balance_utility_repair_model_workflow_source_gate",
    "require_authoritative_fit_temporal_residual_regime_balance_utility_repair_model_execution",
    "validate_fit_temporal_residual_regime_balance_utility_repair_model_workflow_sources",
]
