from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .historical_operator import (
    EXP061_HISTORICAL_OPERATOR_DECISION,
    EXP061_HISTORICAL_OPERATOR_VERSION,
    validate_historical_plan,
)
from .historical_run_authorization import (
    EXP061_HISTORICAL_RUN_AUTHORIZATION_DECISION,
    EXP061_HISTORICAL_RUN_AUTHORIZATION_VERSION,
)
from .proof_result_decision import (
    EXP061_GATE_PROOF_HEAD_SHA,
    EXP061_GATE_PROOF_RUN_ID,
)


EXP061_REVIEWED_HISTORICAL_PLAN_DECISION = "DEC-284"
EXP061_REVIEWED_HISTORICAL_PLAN_VERSION = (
    "fmp-exp061-reviewed-historical-plan-proof-v1"
)

DEC283_MERGED_COMMIT = "7fd3a9e878bf2760850037548e93dc1e8173c0c1"
DEC283_PROOF_RUN_ID = 36323674455
DEC283_PROOF_WORKFLOW_NAME = "phase8a-exp061-historical-plan"
DEC283_PROOF_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp061-historical-plan.yml"
)
DEC283_PROOF_ARTIFACT_ID = 10932743232
DEC283_PROOF_ARTIFACT_NAME = (
    "exp061-dec283-historical-plan-"
    "7fd3a9e878bf2760850037548e93dc1e8173c0c1"
)
DEC283_PROOF_ARTIFACT_DIGEST = (
    "sha256:a71585da8c7e858d7ed309cf52965c5a0fbb7ef42b65e28a18933792eeb9460a"
)
DEC283_PLAN_RAW_SHA256 = (
    "7cbe58c3ec256ff0973c9baa86e109486f0c2e37eaa973bf053fa1337cc1849e"
)
DEC283_PLAN_CANONICAL_SHA256 = (
    "605af14b35bdf132217340e7701263bfaf24d6280d6e45edbb43d2d1debc35de"
)

DEC283_WORKFLOW_BLOB_SHA = "7c2d7409d1a05ce287cc36f5371a85273a6a027b"
DEC282_OPERATOR_BLOB_SHA = "1ffef37d94b04a8206f665c375dc0b2642c4caa9"
DEC282_OPERATOR_CLI_BLOB_SHA = "4d667d05ef2a5bd672cb9d98a81f13dd2ba9370c"
DEC281_AUTHORIZATION_BLOB_SHA = "1eab1cee2fc81441cf1c3168cc73275cd29addf5"

HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
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


def validate_reviewed_historical_plan_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec283_workflow": (
            root / ".github/workflows/phase8a-exp061-historical-plan.yml",
            DEC283_WORKFLOW_BLOB_SHA,
        ),
        "dec282_operator": (
            root / "src/fmp/discovery/historical_operator.py",
            DEC282_OPERATOR_BLOB_SHA,
        ),
        "dec282_operator_cli": (
            root / "scripts/phase8a_exp061_historical_operator.py",
            DEC282_OPERATOR_CLI_BLOB_SHA,
        ),
        "dec281_authorization": (
            root / "src/fmp/discovery/historical_run_authorization.py",
            DEC281_AUTHORIZATION_BLOB_SHA,
        ),
    }

    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-284 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-284 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "decision": EXP061_REVIEWED_HISTORICAL_PLAN_DECISION,
        "version": EXP061_REVIEWED_HISTORICAL_PLAN_VERSION,
        "dec283_merged_commit": DEC283_MERGED_COMMIT,
        "dec283_workflow_blob_sha": actual["dec283_workflow"],
        "dec282_operator_blob_sha": actual["dec282_operator"],
        "dec282_operator_cli_blob_sha": actual["dec282_operator_cli"],
        "dec281_authorization_blob_sha": actual["dec281_authorization"],
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
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
            "id": DEC283_PROOF_RUN_ID,
            "name": DEC283_PROOF_WORKFLOW_NAME,
            "path": DEC283_PROOF_WORKFLOW_PATH,
            "event": "push",
            "head_branch": "main",
            "head_sha": DEC283_MERGED_COMMIT,
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "success",
        },
        prefix="DEC-283 historical-plan proof run",
    )


def _validate_artifact(artifacts_payload: Mapping[str, object]) -> None:
    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-284 requires exactly one DEC-283 plan artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-283 plan artifact row is malformed")
    _require_exact(
        artifact,
        {
            "id": DEC283_PROOF_ARTIFACT_ID,
            "name": DEC283_PROOF_ARTIFACT_NAME,
            "digest": DEC283_PROOF_ARTIFACT_DIGEST,
            "expired": False,
        },
        prefix="DEC-283 plan artifact",
    )
    _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-283 plan artifact digest",
    )


def _validate_plan(plan: Mapping[str, object]) -> Mapping[str, object]:
    validated = validate_historical_plan(plan)
    _require_exact(
        validated,
        {
            "decision": EXP061_HISTORICAL_OPERATOR_DECISION,
            "operator_version": EXP061_HISTORICAL_OPERATOR_VERSION,
            "authorization_decision": (
                EXP061_HISTORICAL_RUN_AUTHORIZATION_DECISION
            ),
            "authorization_version": (
                EXP061_HISTORICAL_RUN_AUTHORIZATION_VERSION
            ),
            "expected_head_sha": DEC283_MERGED_COMMIT,
            "stage": "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE",
            "proof_run_id": EXP061_GATE_PROOF_RUN_ID,
            "proof_head_sha": EXP061_GATE_PROOF_HEAD_SHA,
            "proof_run_count": 1,
            "historical_result_attempt_count": 0,
            "historical_result_run_id": None,
            "historical_result_head_sha": None,
            "historical_result_run_status": None,
            "historical_result_run_conclusion": None,
            "historical_result_slot_consumed": False,
            "planned_dispatch_command": (
                "gh workflow run phase8a-exp061-discovery.yml --ref main"
            ),
            "historical_result_slot_source_authorized": True,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": False,
            "discovery_result_authorized": False,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
            "reserved_robustness_access_authorized": False,
            "candidate_compilation_authorized": False,
            "phase8b_authorized": False,
            "demo_order_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "trading_authorized": False,
        },
        prefix="DEC-283 historical plan",
    )
    if hashlib.sha256(_canonical_json(dict(validated))).hexdigest() != (
        DEC283_PLAN_CANONICAL_SHA256
    ):
        raise ValueError("DEC-283 historical plan canonical fingerprint mismatch")
    return validated


def freeze_reviewed_historical_plan_proof(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    plan: Mapping[str, object],
    artifact_zip_sha256: str,
    plan_raw_sha256: str,
) -> dict[str, object]:
    sources = validate_reviewed_historical_plan_sources(
        repository_root=repository_root,
    )
    _validate_proof_run(proof_run)
    _validate_artifact(proof_artifacts_payload)
    _validate_plan(plan)

    if _validate_sha256(
        artifact_zip_sha256,
        field="DEC-283 artifact ZIP sha256",
    ) != DEC283_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:"):
        raise ValueError("DEC-283 artifact ZIP sha256 mismatch")
    if _validate_sha256(
        plan_raw_sha256,
        field="DEC-283 plan raw sha256",
    ) != DEC283_PLAN_RAW_SHA256:
        raise ValueError("DEC-283 plan raw sha256 mismatch")

    return {
        **sources,
        "stage": "EXP061_HISTORICAL_PLAN_PROOF_REVIEWED_AND_FROZEN",
        "proof_run_id": DEC283_PROOF_RUN_ID,
        "proof_head_sha": DEC283_MERGED_COMMIT,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_artifact_id": DEC283_PROOF_ARTIFACT_ID,
        "proof_artifact_name": DEC283_PROOF_ARTIFACT_NAME,
        "proof_artifact_digest": DEC283_PROOF_ARTIFACT_DIGEST,
        "plan_raw_sha256": DEC283_PLAN_RAW_SHA256,
        "plan_canonical_sha256": DEC283_PLAN_CANONICAL_SHA256,
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp061-discovery.yml --ref main"
        ),
        "historical_result_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


__all__ = [
    "DEC283_MERGED_COMMIT",
    "DEC283_PLAN_CANONICAL_SHA256",
    "DEC283_PLAN_RAW_SHA256",
    "DEC283_PROOF_ARTIFACT_DIGEST",
    "DEC283_PROOF_ARTIFACT_ID",
    "DEC283_PROOF_RUN_ID",
    "EXP061_REVIEWED_HISTORICAL_PLAN_DECISION",
    "EXP061_REVIEWED_HISTORICAL_PLAN_VERSION",
    "freeze_reviewed_historical_plan_proof",
    "validate_reviewed_historical_plan_sources",
]
