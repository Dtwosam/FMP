from __future__ import annotations

import hashlib
from pathlib import Path


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_WORKFLOW_SOURCE_DECISION = "DEC-355"
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_WORKFLOW_SOURCE_VERSION = (
    "fmp-exp062-one-shot-historical-executor-dormant-workflow-source-v1"
)

DEC354_INSTALLATION_SOURCE_CONTRACT_BLOB_SHA = (
    "e4fc6a7d1faaca50bc6936597f0e8b66fe096985"
)
DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA = (
    "51ce87584369be957482460d81649adb1cb9f05d"
)
ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA = (
    "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
)

DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "phase8a-exp062-one-shot-historical-executor.yml.disabled"
)
EXPECTED_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)
ACTIVE_DISCOVERY_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-discovery.yml"
)

DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PRESENT = True
DORMANT_TEMPLATE_DISPATCH_CAPABLE_IF_INSTALLED = True
DORMANT_TEMPLATE_ACTIONS_WRITE_REQUIRED_IF_INSTALLED = True
HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED = False
HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED = False
HISTORICAL_EXECUTOR_AVAILABLE = False
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


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def validate_one_shot_historical_executor_dormant_workflow_source_dependencies(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec354_installation_source_contract": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_workflow_installation_source_contract.py",
            DEC354_INSTALLATION_SOURCE_CONTRACT_BLOB_SHA,
        ),
        "dormant_executor_workflow_template": (
            root / DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH,
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA,
        ),
        "active_discovery_workflow": (
            root / ACTIVE_DISCOVERY_WORKFLOW_PATH,
            ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-355 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-355 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def validate_dormant_one_shot_historical_executor_workflow_template(
    text: str,
) -> None:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("DEC-355 dormant executor template must be non-empty")

    required = (
        "name: phase8a-exp062-one-shot-historical-executor",
        "workflow_dispatch:",
        "contents: read",
        "actions: write",
        "name: one-shot-historical-executor",
        'test "$GITHUB_RUN_NUMBER" = "1"',
        'test "$GITHUB_RUN_ATTEMPT" = "1"',
        'test "$GITHUB_REF" = "refs/heads/main"',
        (
            'test "$(git hash-object .github/workflows/'
            'phase8a-exp062-discovery.yml)" = '
            '"1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"'
        ),
        'row.get("id") == 36358289723',
        'row.get("run_number") == 2',
        'row.get("run_attempt") == 1',
        "gh workflow run phase8a-exp062-discovery.yml --ref main",
        '"rerun_authorized": False',
        '"retry_authorized": False',
        '"replacement_run_authorized": False',
        '"reserved_robustness_access_authorized": False',
        '"candidate_compilation_authorized": False',
        '"promotion_authorized": False',
        '"phase8b_authorized": False',
        '"demo_order_authorized": False',
        '"broker_mutation_authorized": False',
        '"live_order_authorized": False',
        '"real_money_authorized": False',
        '"trading_authorized": False',
        "uses: actions/upload-artifact@v6",
        "one-shot-historical-executor-receipt.json",
    )
    for token in required:
        if token not in text:
            raise ValueError(
                f"DEC-355 dormant executor template missing token: {token}"
            )

    forbidden = (
        "push:",
        "pull_request:",
        "schedule:",
        "cron:",
        "actions: read",
        "GITHUB_RUN_ATTEMPT\" = \"2",
        "gh run rerun",
        "gh workflow enable",
        "phase8b",
        "live-order",
        "real-money",
    )
    for token in forbidden:
        if token in text:
            raise ValueError(
                f"DEC-355 dormant executor template contains forbidden token: {token}"
            )

    shell_dispatches = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
        == "gh workflow run phase8a-exp062-discovery.yml --ref main"
    ]
    if shell_dispatches != [
        "gh workflow run phase8a-exp062-discovery.yml --ref main"
    ]:
        raise ValueError(
            "DEC-355 dormant executor template must contain exactly one "
            "shell dispatch"
        )

    if "test "$found" = "1"" not in text:
        raise ValueError(
            "DEC-355 dormant executor template must require target resolution"
        )


def build_one_shot_historical_executor_dormant_workflow_source(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    source_blobs = (
        validate_one_shot_historical_executor_dormant_workflow_source_dependencies(
            repository_root=root,
        )
    )
    template = (
        root / DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
    ).read_text(encoding="utf-8")
    validate_dormant_one_shot_historical_executor_workflow_template(template)

    return {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_WORKFLOW_SOURCE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_WORKFLOW_SOURCE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_TEMPLATE_SOURCE_"
            "FROZEN_ACTIVE_WORKFLOW_UNINSTALLED"
        ),
        "source_blobs": source_blobs,
        "installation_source_contract_decision": "DEC-354",
        "dormant_executor_workflow_template_path": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
        ),
        "dormant_executor_workflow_template_blob_sha": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "active_discovery_workflow_path": ACTIVE_DISCOVERY_WORKFLOW_PATH,
        "active_discovery_workflow_blob_sha": (
            ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA
        ),
        "dormant_executor_workflow_template_present": True,
        "dormant_template_dispatch_capable_if_installed": True,
        "dormant_template_actions_write_required_if_installed": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
        "historical_executor_available": False,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
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
        "next_gate": (
            "REPOSITORY_HOSTED_READ_ONLY_DORMANT_ONE_SHOT_HISTORICAL_"
            "EXECUTOR_WORKFLOW_SOURCE_PROOF"
        ),
    }


__all__ = [
    "ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA",
    "ACTIVE_DISCOVERY_WORKFLOW_PATH",
    "DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA",
    "DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH",
    "EXPECTED_EXECUTOR_WORKFLOW_PATH",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_WORKFLOW_SOURCE_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_WORKFLOW_SOURCE_VERSION",
    "build_one_shot_historical_executor_dormant_workflow_source",
    "validate_dormant_one_shot_historical_executor_workflow_template",
    "validate_one_shot_historical_executor_dormant_workflow_source_dependencies",
]
