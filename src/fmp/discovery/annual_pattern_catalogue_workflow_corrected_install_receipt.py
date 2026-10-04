from __future__ import annotations

import hashlib
from pathlib import Path

from .annual_pattern_catalogue_workflow_source import (
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    validate_dormant_workflow_template,
)


ANNUAL_CATALOGUE_WORKFLOW_CORRECTED_INSTALL_RECEIPT_DECISION = "DEC-520"
ANNUAL_CATALOGUE_WORKFLOW_CORRECTED_INSTALL_RECEIPT_VERSION = (
    "fmp-annual-catalogue-workflow-corrected-install-receipt-v1"
)
HISTORICAL_INSTALL_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_workflow_install_receipt.py"
)
EXPECTED_HISTORICAL_INSTALL_RECEIPT_SOURCE_BLOB_SHA = (
    "970ab466dfa5f87c6955ad65da4653a993e9d6fd"
)
EXPECTED_DORMANT_ANNUAL_WORKFLOW_BLOB_SHA = (
    "31633e87b79551f5b7dfa6b0deb76a82eb070129"
)
EXPECTED_ACTIVE_ANNUAL_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def validate_corrected_annual_workflow_install_receipt_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    historical = root / HISTORICAL_INSTALL_RECEIPT_SOURCE_PATH
    dormant = root / DORMANT_WORKFLOW_TEMPLATE_PATH
    active = root / RESERVED_ACTIVE_WORKFLOW_PATH

    expected = {
        "historical_install_receipt_source_blob_sha": (
            historical,
            EXPECTED_HISTORICAL_INSTALL_RECEIPT_SOURCE_BLOB_SHA,
        ),
        "dormant_annual_workflow_template_blob_sha": (
            dormant,
            EXPECTED_DORMANT_ANNUAL_WORKFLOW_BLOB_SHA,
        ),
        "active_annual_workflow_blob_sha": (
            active,
            EXPECTED_ACTIVE_ANNUAL_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-520 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-520 {field} mismatch: {sha} != {expected_sha}")
        actual[field] = sha

    dormant_text = dormant.read_text(encoding="utf-8")
    validate_dormant_workflow_template(dormant_text)

    active_text = active.read_text(encoding="utf-8")
    if "  workflow_dispatch:" not in active_text:
        raise ValueError("DEC-520 corrected workflow must remain manual-dispatch only")
    if "  push:" in active_text or "  pull_request:" in active_text:
        raise ValueError("DEC-520 corrected workflow gained automatic trigger")
    if "  contents: read" not in active_text or "  actions: read" not in active_text:
        raise ValueError("DEC-520 corrected workflow read permissions drift")
    if "  actions: write" in active_text or "gh workflow run " in active_text:
        raise ValueError("DEC-520 corrected workflow gained nested dispatch authority")
    if active_text.count("include-hidden-files: true") != 3:
        raise ValueError("DEC-520 corrected workflow hidden-file repair drift")
    if active_text.count(
        "python scripts/phase8a_annual_pattern_catalogue.py require-execution"
    ) != 3:
        raise ValueError("DEC-520 corrected workflow execution-gate count drift")

    return {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_CORRECTED_INSTALL_RECEIPT_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_CORRECTED_INSTALL_RECEIPT_VERSION,
        **actual,
        "historical_install_receipt_decision": "DEC-491",
        "workflow_correction_decision": "DEC-520",
    }


__all__ = [
    "ANNUAL_CATALOGUE_WORKFLOW_CORRECTED_INSTALL_RECEIPT_DECISION",
    "ANNUAL_CATALOGUE_WORKFLOW_CORRECTED_INSTALL_RECEIPT_VERSION",
    "EXPECTED_ACTIVE_ANNUAL_WORKFLOW_BLOB_SHA",
    "EXPECTED_DORMANT_ANNUAL_WORKFLOW_BLOB_SHA",
    "validate_corrected_annual_workflow_install_receipt_sources",
]
