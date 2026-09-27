from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .historical_result_review_contract import (
    EXP061_HISTORICAL_TERMINAL_REVIEW_DECISION,
    classify_historical_terminal_result,
)


EXP061_FAILED_RESULT_DECISION = "DEC-291"
EXP061_FAILED_RESULT_VERSION = "fmp-exp061-failed-historical-result-review-v1"

EXP061_HISTORICAL_RUN_ID = 36335879839
EXP061_HISTORICAL_HEAD_SHA = "a7b3bc2d0b196da2631b64c19331efb3af12c98e"
EXP061_EXECUTOR_RUN_ID = 36335739823

EXECUTOR_ARTIFACT_ID = 10936194549
EXECUTOR_ARTIFACT_DIGEST = (
    "sha256:e7ffe1f08ce358eca210ef41397165196cb64bee31696a180c7fd02af8c68f1c"
)
PREFLIGHT_ARTIFACT_ID = 10937316246
PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:e9a898df51317250944ad0a111d01d96d2081d708ea80872ed11b5cee48d356f"
)

TERMINAL_REVIEW_BLOB_SHA = "2df4caa00aa683b8d627d061ae806178fbd5cd9c"
MARKET_LEARNING_ADAPTER_BLOB_SHA = "978a33554fad7e9d78b002778c4896be0af3333a"
PATTERN_MINER_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"
PATTERN_PROTOCOL_BLOB_SHA = "63b3f0121d6a50eb9e8e62ab666d70eb91791621"
RANGE_LIMITED_LOADER_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
RUN_CONTRACT_BLOB_SHA = "260eb6930673427266463517546969635188b143"
DISCOVERY_WORKFLOW_BLOB_SHA = "d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9"
EXECUTOR_BLOB_SHA = "82dbec289ed69e7333a90fd28ce430b024a99936"
EXECUTOR_WORKFLOW_BLOB_SHA = "4efb80cf9eee3f7073de28531babc269d3c7a8cc"

EXPECTED_CELL_FAILURE_FEATURES = {
    "exp061-cell-EURUSD-5m-60m": "realized_vol_8h",
    "exp061-cell-EURUSD-5m-240m": "realized_vol_8h",
    "exp061-cell-EURUSD-15m-60m": "realized_vol_1h",
    "exp061-cell-EURUSD-15m-240m": "realized_vol_1h",
    "exp061-cell-EURUSD-1h-60m": "realized_vol_8h",
    "exp061-cell-EURUSD-1h-240m": "realized_vol_8h",
    "exp061-cell-GBPUSD-5m-60m": "realized_vol_1h",
    "exp061-cell-GBPUSD-5m-240m": "realized_vol_1h",
    "exp061-cell-GBPUSD-15m-60m": "realized_vol_1h",
    "exp061-cell-GBPUSD-15m-240m": "realized_vol_1h",
    "exp061-cell-GBPUSD-1h-60m": "realized_vol_8h",
    "exp061-cell-GBPUSD-1h-240m": "realized_vol_8h",
    "exp061-cell-USDJPY-5m-60m": "realized_vol_1h",
    "exp061-cell-USDJPY-5m-240m": "realized_vol_1h",
    "exp061-cell-USDJPY-15m-60m": "realized_vol_8h",
    "exp061-cell-USDJPY-15m-240m": "realized_vol_8h",
    "exp061-cell-USDJPY-1h-60m": "realized_vol_8h",
    "exp061-cell-USDJPY-1h-240m": "realized_vol_8h",
}

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
    import hashlib
    return hashlib.sha1(header + payload).hexdigest()


def validate_failed_result_sources(*, repository_root: Path) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "terminal_review": (
            root / "src/fmp/discovery/historical_result_review_contract.py",
            TERMINAL_REVIEW_BLOB_SHA,
        ),
        "market_learning_adapter": (
            root / "src/fmp/discovery/market_learning_adapter.py",
            MARKET_LEARNING_ADAPTER_BLOB_SHA,
        ),
        "pattern_miner": (
            root / "src/fmp/discovery/pattern_miner.py",
            PATTERN_MINER_BLOB_SHA,
        ),
        "pattern_protocol": (
            root / "src/fmp/discovery/pattern_protocol.py",
            PATTERN_PROTOCOL_BLOB_SHA,
        ),
        "range_limited_loader": (
            root / "src/fmp/discovery/range_limited_loader.py",
            RANGE_LIMITED_LOADER_BLOB_SHA,
        ),
        "run_contract": (
            root / "src/fmp/discovery/run_contract.py",
            RUN_CONTRACT_BLOB_SHA,
        ),
        "discovery_workflow": (
            root / ".github/workflows/phase8a-exp061-discovery.yml",
            DISCOVERY_WORKFLOW_BLOB_SHA,
        ),
        "executor": (
            root / "src/fmp/discovery/historical_executor.py",
            EXECUTOR_BLOB_SHA,
        ),
        "executor_workflow": (
            root / ".github/workflows/phase8a-exp061-historical-one-shot-execute.yml",
            EXECUTOR_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-291 source dependency: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"DEC-291 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha
    return actual


def freeze_failed_historical_result(
    *,
    repository_root: Path,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    executor_artifact: Mapping[str, object],
    cell_failure_features: Mapping[str, str],
) -> dict[str, object]:
    sources = validate_failed_result_sources(repository_root=repository_root)
    terminal = classify_historical_terminal_result(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        expected_head_sha=EXP061_HISTORICAL_HEAD_SHA,
    )

    if run.get("id") != EXP061_HISTORICAL_RUN_ID:
        raise ValueError("DEC-291 historical run id mismatch")
    if terminal.get("stage") != "EXP061_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED":
        raise ValueError("DEC-291 requires the frozen terminal failure stage")
    if terminal.get("historical_run_conclusion") != "failure":
        raise ValueError("DEC-291 requires historical conclusion failure")
    if terminal.get("materialized_job_count") != 20:
        raise ValueError("DEC-291 requires all 20 jobs to have materialized")
    if terminal.get("artifact_count") != 1:
        raise ValueError("DEC-291 requires the sole preflight artifact")

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("DEC-291 jobs payload is malformed")
    conclusions = {str(j.get("name")): j.get("conclusion") for j in jobs if isinstance(j, Mapping)}
    if conclusions.get("exp061-preflight") != "success":
        raise ValueError("DEC-291 requires successful preflight")
    if conclusions.get("exp061-aggregate") != "skipped":
        raise ValueError("DEC-291 requires skipped aggregate")
    cell_names = {name for name in conclusions if name.startswith("exp061-cell-")}
    if cell_names != set(EXPECTED_CELL_FAILURE_FEATURES):
        raise ValueError("DEC-291 cell job inventory mismatch")
    if any(conclusions[name] != "failure" for name in cell_names):
        raise ValueError("DEC-291 requires every cell job to fail")

    if dict(cell_failure_features) != EXPECTED_CELL_FAILURE_FEATURES:
        raise ValueError("DEC-291 cell failure signature map mismatch")
    if set(cell_failure_features.values()) != {"realized_vol_1h", "realized_vol_8h"}:
        raise ValueError("DEC-291 unexpected non-finite failure feature")

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-291 historical artifact inventory mismatch")
    artifact = artifacts[0]
    if (
        not isinstance(artifact, Mapping)
        or artifact.get("id") != PREFLIGHT_ARTIFACT_ID
        or artifact.get("digest") != PREFLIGHT_ARTIFACT_DIGEST
        or artifact.get("expired") is not False
    ):
        raise ValueError("DEC-291 preflight artifact identity mismatch")

    if (
        executor_artifact.get("id") != EXECUTOR_ARTIFACT_ID
        or executor_artifact.get("digest") != EXECUTOR_ARTIFACT_DIGEST
        or executor_artifact.get("expired") is not False
    ):
        raise ValueError("DEC-291 executor artifact identity mismatch")

    return {
        "decision": EXP061_FAILED_RESULT_DECISION,
        "version": EXP061_FAILED_RESULT_VERSION,
        "stage": "EXP061_HISTORICAL_RESULT_FAILED_AND_FROZEN",
        "terminal_review_decision": EXP061_HISTORICAL_TERMINAL_REVIEW_DECISION,
        "historical_run_id": EXP061_HISTORICAL_RUN_ID,
        "historical_run_head_sha": EXP061_HISTORICAL_HEAD_SHA,
        "historical_run_number": 2,
        "historical_run_attempt": 1,
        "historical_run_conclusion": "failure",
        "executor_run_id": EXP061_EXECUTOR_RUN_ID,
        "executor_artifact_id": EXECUTOR_ARTIFACT_ID,
        "executor_artifact_digest": EXECUTOR_ARTIFACT_DIGEST,
        "preflight_artifact_id": PREFLIGHT_ARTIFACT_ID,
        "preflight_artifact_digest": PREFLIGHT_ARTIFACT_DIGEST,
        "preflight_conclusion": "success",
        "failed_cell_count": 18,
        "aggregate_conclusion": "skipped",
        "historical_result_slot_consumed": True,
        "root_cause_class": "NONFINITE_DERIVED_FEATURE_ADAPTER_BOUNDARY",
        "observed_nonfinite_features": ["realized_vol_1h", "realized_vol_8h"],
        "cell_failure_features": dict(sorted(cell_failure_features.items())),
        "failure_before_pattern_mining": True,
        "pattern_hypothesis_result_produced": False,
        "sources": sources,
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
    "EXPECTED_CELL_FAILURE_FEATURES",
    "EXP061_FAILED_RESULT_DECISION",
    "EXP061_FAILED_RESULT_VERSION",
    "EXP061_HISTORICAL_HEAD_SHA",
    "EXP061_HISTORICAL_RUN_ID",
    "freeze_failed_historical_result",
    "validate_failed_result_sources",
]
