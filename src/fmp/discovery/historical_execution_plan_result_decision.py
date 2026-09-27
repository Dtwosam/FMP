from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .historical_execution_operator import (
    EXP061_HISTORICAL_EXECUTION_OPERATOR_DECISION,
    EXP061_HISTORICAL_EXECUTION_OPERATOR_VERSION,
    validate_historical_execution_plan,
)
from .historical_execution_authorization import (
    EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION,
    EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION,
)
from .proof_result_decision import (
    EXP061_GATE_PROOF_RUN_ID,
)


EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_DECISION = "DEC-288"
EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_VERSION = (
    "fmp-exp061-reviewed-historical-execution-plan-proof-v1"
)

DEC287_MERGED_COMMIT = "958a0b830bb867d1c11e2a82be7fc301a6a75474"
DEC287_PROOF_RUN_ID = 36329787371
DEC287_PROOF_WORKFLOW_NAME = "phase8a-exp061-historical-execution-plan"
DEC287_PROOF_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp061-historical-execution-plan.yml"
)
DEC287_PROOF_ARTIFACT_ID = 10935233025
DEC287_PROOF_ARTIFACT_NAME = (
    "exp061-dec287-historical-execution-plan-"
    "958a0b830bb867d1c11e2a82be7fc301a6a75474"
)
DEC287_PROOF_ARTIFACT_DIGEST = (
    "sha256:bb81bd8f0cb1adfc0054db4f5c16f13808793c520d443a0f05a89a90f92a415d"
)
DEC287_PLAN_RAW_SHA256 = (
    "2ca76921e17096b444202573a950825244e07c27e0f476cecfb510ad5e0a95e5"
)
DEC287_PLAN_CANONICAL_SHA256 = (
    "86b37433e183bfd9199822da0212b79fe11950461206335fc53e6f783210a74e"
)

DEC287_WORKFLOW_BLOB_SHA = "6f4b6a04291465f0f32f1f8e9276ff4a62417ec2"
DEC286_OPERATOR_BLOB_SHA = "a711b14fb613f1c9952f5b2a6bf85d892bd2c4a5"
DEC286_OPERATOR_CLI_BLOB_SHA = "1f43e1218072918d2ebb33b2c312ba8e950881f9"
DEC285_AUTHORIZATION_BLOB_SHA = "30258e076f6a786c977fac8c588ac2b22aeed66e"
ACTIVATED_CLI_BLOB_SHA = "477aa9e8de4452e6444d1ee4361218aca445180d"
ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA = (
    "d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9"
)

HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_EXECUTE_MODE_AVAILABLE = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_sha256_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    _validate_sha256(value.removeprefix("sha256:"), field=field)
    return value.lower()


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def validate_reviewed_historical_execution_plan_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec287_workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp061-historical-execution-plan.yml",
            DEC287_WORKFLOW_BLOB_SHA,
        ),
        "dec286_operator": (
            root / "src/fmp/discovery/historical_execution_operator.py",
            DEC286_OPERATOR_BLOB_SHA,
        ),
        "dec286_operator_cli": (
            root / "scripts/phase8a_exp061_historical_execution_operator.py",
            DEC286_OPERATOR_CLI_BLOB_SHA,
        ),
        "dec285_authorization": (
            root / "src/fmp/discovery/historical_execution_authorization.py",
            DEC285_AUTHORIZATION_BLOB_SHA,
        ),
        "activated_cli": (
            root / "scripts/phase8a_exp061.py",
            ACTIVATED_CLI_BLOB_SHA,
        ),
        "active_discovery_workflow": (
            root / ".github/workflows/phase8a-exp061-discovery.yml",
            ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA,
        ),
    }

    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-288 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-288 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "decision": EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_DECISION,
        "version": EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_VERSION,
        "dec287_merged_commit": DEC287_MERGED_COMMIT,
        "dec287_workflow_blob_sha": actual["dec287_workflow"],
        "dec286_operator_blob_sha": actual["dec286_operator"],
        "dec286_operator_cli_blob_sha": actual["dec286_operator_cli"],
        "dec285_authorization_blob_sha": actual["dec285_authorization"],
        "activated_cli_blob_sha": actual["activated_cli"],
        "active_discovery_workflow_blob_sha": actual[
            "active_discovery_workflow"
        ],
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_execute_mode_available": HISTORICAL_EXECUTE_MODE_AVAILABLE,
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


def _validate_proof_run(run: Mapping[str, object]) -> None:
    _require_exact(
        run,
        {
            "id": DEC287_PROOF_RUN_ID,
            "name": DEC287_PROOF_WORKFLOW_NAME,
            "path": DEC287_PROOF_WORKFLOW_PATH,
            "event": "push",
            "head_branch": "main",
            "head_sha": DEC287_MERGED_COMMIT,
            "run_number": 1,
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "success",
        },
        prefix="DEC-287 historical execution-plan proof run",
    )


def _validate_artifact(artifacts_payload: Mapping[str, object]) -> None:
    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError(
            "DEC-288 requires exactly one DEC-287 execution-plan artifact"
        )
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-287 execution-plan artifact row is malformed")
    _require_exact(
        artifact,
        {
            "id": DEC287_PROOF_ARTIFACT_ID,
            "name": DEC287_PROOF_ARTIFACT_NAME,
            "digest": DEC287_PROOF_ARTIFACT_DIGEST,
            "expired": False,
        },
        prefix="DEC-287 execution-plan artifact",
    )
    _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-287 execution-plan artifact digest",
    )


def _validate_plan(plan: Mapping[str, object]) -> Mapping[str, object]:
    validated = validate_historical_execution_plan(plan)
    _require_exact(
        validated,
        {
            "decision": EXP061_HISTORICAL_EXECUTION_OPERATOR_DECISION,
            "operator_version": EXP061_HISTORICAL_EXECUTION_OPERATOR_VERSION,
            "authorization_decision": (
                EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION
            ),
            "authorization_version": (
                EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION
            ),
            "expected_head_sha": DEC287_MERGED_COMMIT,
            "stage": "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE",
            "proof_run_id": EXP061_GATE_PROOF_RUN_ID,
            "proof_run_count": 1,
            "proof_run_number": 1,
            "historical_result_attempt_count": 0,
            "historical_result_run_id": None,
            "historical_result_run_status": None,
            "historical_result_run_conclusion": None,
            "historical_result_slot_consumed": False,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "planned_dispatch_command": (
                "gh workflow run phase8a-exp061-discovery.yml --ref main"
            ),
            "historical_execution_source_authorized": True,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
            "reserved_robustness_access_authorized": False,
            "candidate_compilation_authorized": False,
            "promotion_authorized": False,
            "phase8b_authorized": False,
            "demo_order_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "trading_authorized": False,
        },
        prefix="DEC-287 historical execution plan",
    )
    if hashlib.sha256(_canonical_json(dict(validated))).hexdigest() != (
        DEC287_PLAN_CANONICAL_SHA256
    ):
        raise ValueError(
            "DEC-287 historical execution plan canonical fingerprint mismatch"
        )
    return validated


def freeze_reviewed_historical_execution_plan_proof(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    plan: Mapping[str, object],
    artifact_zip_sha256: str,
    plan_raw_sha256: str,
) -> dict[str, object]:
    sources = validate_reviewed_historical_execution_plan_sources(
        repository_root=repository_root,
    )
    _validate_proof_run(proof_run)
    _validate_artifact(proof_artifacts_payload)
    _validate_plan(plan)

    if _validate_sha256(
        artifact_zip_sha256,
        field="DEC-287 artifact ZIP sha256",
    ) != DEC287_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:"):
        raise ValueError("DEC-287 artifact ZIP sha256 mismatch")
    if _validate_sha256(
        plan_raw_sha256,
        field="DEC-287 plan raw sha256",
    ) != DEC287_PLAN_RAW_SHA256:
        raise ValueError("DEC-287 plan raw sha256 mismatch")

    return {
        **sources,
        "stage": (
            "EXP061_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_AND_FROZEN"
        ),
        "proof_run_id": DEC287_PROOF_RUN_ID,
        "proof_head_sha": DEC287_MERGED_COMMIT,
        "proof_workflow_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_artifact_id": DEC287_PROOF_ARTIFACT_ID,
        "proof_artifact_name": DEC287_PROOF_ARTIFACT_NAME,
        "proof_artifact_digest": DEC287_PROOF_ARTIFACT_DIGEST,
        "plan_raw_sha256": DEC287_PLAN_RAW_SHA256,
        "plan_canonical_sha256": DEC287_PLAN_CANONICAL_SHA256,
        "gate_proof_run_id": EXP061_GATE_PROOF_RUN_ID,
        "gate_proof_workflow_run_number": 1,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp061-discovery.yml --ref main"
        ),
        "historical_execution_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


__all__ = [
    "DEC287_MERGED_COMMIT",
    "DEC287_PLAN_CANONICAL_SHA256",
    "DEC287_PLAN_RAW_SHA256",
    "DEC287_PROOF_ARTIFACT_DIGEST",
    "DEC287_PROOF_ARTIFACT_ID",
    "DEC287_PROOF_RUN_ID",
    "EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_DECISION",
    "EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_VERSION",
    "freeze_reviewed_historical_execution_plan_proof",
    "validate_reviewed_historical_execution_plan_sources",
]
