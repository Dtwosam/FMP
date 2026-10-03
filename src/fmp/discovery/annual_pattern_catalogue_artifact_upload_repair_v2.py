from __future__ import annotations

import hashlib
from pathlib import Path


ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_V2_DECISION = "DEC-500"
ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_V2_VERSION = (
    "fmp-annual-catalogue-artifact-upload-repair-v2"
)

PRIOR_REPAIR_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_artifact_upload_repair.py"
)
EXPECTED_PRIOR_REPAIR_SOURCE_BLOB_SHA = (
    "adfa75b352a561667b8c23efbcfb07af804d1131"
)
FAILED_REPAIR_WORKFLOW_SNAPSHOT_PATH = (
    "tests/fixtures/phase8a_annual_pattern_catalogue_workflow_dec496.yml.snapshot"
)
EXPECTED_FAILED_REPAIR_WORKFLOW_BLOB_SHA = (
    "f7e65ee95f472918e390bceedd7cf2f38bbf7e92"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_CORRECTED_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

REPLACEMENT_RUN_AUTHORIZED = False
NEXT_SEGMENT_EXECUTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _assert_upload_block(
    text: str,
    *,
    artifact_name_fragment: str,
    path_line: str,
) -> None:
    marker = "uses: actions/upload-artifact@v6"
    cursor = 0
    matches: list[str] = []
    while True:
        start = text.find(marker, cursor)
        if start < 0:
            break
        end = text.find("\n  ", start + len(marker))
        if end < 0:
            end = len(text)
        block = text[start:end]
        if artifact_name_fragment in block:
            matches.append(block)
        cursor = start + len(marker)

    if len(matches) != 1:
        raise ValueError(
            f"DEC-500 expected exactly one upload block for {artifact_name_fragment}"
        )
    block = matches[0]
    if path_line not in block:
        raise ValueError(f"DEC-500 upload path mismatch for {artifact_name_fragment}")
    if block.count("include-hidden-files: true") != 1:
        raise ValueError(
            f"DEC-500 hidden-file flag count mismatch for {artifact_name_fragment}"
        )
    if "if-no-files-found: error" not in block:
        raise ValueError(
            f"DEC-500 missing fail-closed upload behavior for {artifact_name_fragment}"
        )


def validate_artifact_upload_repair_v2_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "prior_repair_source_blob_sha": (
            root / PRIOR_REPAIR_SOURCE_PATH,
            EXPECTED_PRIOR_REPAIR_SOURCE_BLOB_SHA,
        ),
        "failed_repair_workflow_blob_sha": (
            root / FAILED_REPAIR_WORKFLOW_SNAPSHOT_PATH,
            EXPECTED_FAILED_REPAIR_WORKFLOW_BLOB_SHA,
        ),
        "corrected_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_CORRECTED_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-500 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-500 {field} mismatch")
        actual[field] = sha

    flawed = (root / FAILED_REPAIR_WORKFLOW_SNAPSHOT_PATH).read_text(
        encoding="utf-8"
    )
    corrected = (root / ACTIVE_WORKFLOW_PATH).read_text(encoding="utf-8")

    if flawed.count("include-hidden-files: true") != 3:
        raise ValueError("DEC-500 flawed repair snapshot count drift")
    flawed_preflight = (
        "path: .preflight\n"
        "          if-no-files-found: error\n"
        "          include-hidden-files: true\n"
        "          include-hidden-files: true\n"
        "          include-hidden-files: true"
    )
    if flawed_preflight not in flawed:
        raise ValueError("DEC-500 flawed repair mechanism no longer reproduced")
    if (
        "path: .result\n"
        "          if-no-files-found: error\n"
        "          include-hidden-files: true"
    ) in flawed:
        raise ValueError("DEC-500 flawed snapshot unexpectedly repaired cell upload")
    if (
        "path: .annual-freeze/annual-freeze.json\n"
        "          if-no-files-found: error\n"
        "          include-hidden-files: true"
    ) in flawed:
        raise ValueError("DEC-500 flawed snapshot unexpectedly repaired freeze upload")

    if corrected.count("uses: actions/upload-artifact@v6") != 3:
        raise ValueError("DEC-500 corrected upload action count drift")
    if corrected.count("include-hidden-files: true") != 3:
        raise ValueError("DEC-500 corrected hidden-file flag count drift")

    _assert_upload_block(
        corrected,
        artifact_name_fragment="phase8a-annual-catalogue-preflight-",
        path_line="path: .preflight",
    )
    _assert_upload_block(
        corrected,
        artifact_name_fragment="phase8a-annual-catalogue-cell-",
        path_line="path: .result",
    )
    _assert_upload_block(
        corrected,
        artifact_name_fragment="phase8a-annual-catalogue-freeze-",
        path_line="path: .annual-freeze/annual-freeze.json",
    )

    return actual


def build_artifact_upload_repair_v2_receipt(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_artifact_upload_repair_v2_sources(
        repository_root=Path(repository_root),
    )
    return {
        "decision": ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_V2_DECISION,
        "version": ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_V2_VERSION,
        **source,
        "stage": "ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_DISTRIBUTION_CORRECTED",
        "prior_repair_decision": "DEC-496",
        "repair_reason": "hidden_file_flags_were_concentrated_on_preflight_upload",
        "corrected_upload_count": 3,
        "preflight_hidden_upload_flag_count": 1,
        "cell_hidden_upload_flag_count": 1,
        "freeze_hidden_upload_flag_count": 1,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "next_segment_execution_authorized": NEXT_SEGMENT_EXECUTION_AUTHORIZED,
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": (
            "REFRESH_2015_REPLACEMENT_DISPATCH_PREFLIGHT_"
            "AGAINST_CORRECTED_WORKFLOW"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_V2_DECISION",
    "ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_V2_VERSION",
    "EXPECTED_CORRECTED_WORKFLOW_BLOB_SHA",
    "build_artifact_upload_repair_v2_receipt",
    "validate_artifact_upload_repair_v2_sources",
]
