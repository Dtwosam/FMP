from __future__ import annotations

from typing import Any, Mapping

FROZEN_MANIFEST_TARGET = 25_500
FROZEN_START_DATE = "2015-01-01"
FROZEN_END_DATE_EXCLUSIVE = "2026-08-21"
FROZEN_PLAN_SHA256 = "2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6"


def _is_exact_int(value: object, expected: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value == expected


def _int_value(mapping: Mapping[str, object], key: str) -> int | None:
    value = mapping.get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def evaluate_phase1_acceptance(
    structural: Mapping[str, object],
    accounting: Mapping[str, object],
    provenance: Mapping[str, object],
) -> dict[str, Any]:
    """Combine independent Phase 1 evidence into one fail-closed decision.

    A PASS requires:
    - structural cloud-ledger completeness,
    - recovery/acquisition accounting completeness,
    - full cloud manifest/raw provenance verification,
    - cross-report agreement on the same frozen 25,500-key snapshot.

    This does not evaluate quote/data cleanliness; that remains Phase 2.
    """

    totals = _mapping(accounting.get("totals"))

    structural_present = _int_value(structural, "present_manifests")
    structural_raw = _int_value(structural, "raw_objects")
    accounting_present = _int_value(totals, "present_manifests")
    accounting_raw_backed = _int_value(totals, "raw_backed_manifests")
    accounting_not_found = _int_value(totals, "manifest_only_inferred_not_found")
    provenance_planned = _int_value(provenance, "planned_chunks")
    provenance_complete = _int_value(provenance, "complete")
    provenance_not_found = _int_value(provenance, "not_found")

    checks: dict[str, bool] = {
        "structural_report_version": _is_exact_int(structural.get("report_version"), 1),
        "structural_scope": structural.get("scope") == "phase1_structural_acceptance",
        "structural_frozen_snapshot": (
            structural.get("frozen_start_date") == FROZEN_START_DATE
            and structural.get("frozen_end_date_exclusive") == FROZEN_END_DATE_EXCLUSIVE
        ),
        "structural_expected_25500": _is_exact_int(
            structural.get("expected_manifests"), FROZEN_MANIFEST_TARGET
        ),
        "structural_present_25500": _is_exact_int(
            structural.get("present_manifests"), FROZEN_MANIFEST_TARGET
        ),
        "structural_missing_zero": _is_exact_int(
            structural.get("missing_manifests"), 0
        ),
        "structural_unexpected_manifest_paths_zero": _is_exact_int(
            structural.get("unexpected_manifest_paths"), 0
        ),
        "structural_raw_without_manifest_zero": _is_exact_int(
            structural.get("raw_without_manifest"), 0
        ),
        "structural_unexpected_raw_paths_zero": _is_exact_int(
            structural.get("unexpected_raw_paths"), 0
        ),
        "structural_gate_pass": structural.get("structural_gate_pass") is True,
        "accounting_report_version": _is_exact_int(accounting.get("report_version"), 1),
        "accounting_scope": accounting.get("scope") == "phase1_recovery_accounting",
        "accounting_frozen_snapshot": (
            accounting.get("frozen_start_date") == FROZEN_START_DATE
            and accounting.get("frozen_end_date_exclusive")
            == FROZEN_END_DATE_EXCLUSIVE
        ),
        "accounting_expected_25500": _is_exact_int(
            totals.get("expected_manifests"), FROZEN_MANIFEST_TARGET
        ),
        "accounting_present_25500": _is_exact_int(
            totals.get("present_manifests"), FROZEN_MANIFEST_TARGET
        ),
        "accounting_missing_zero": _is_exact_int(totals.get("missing_manifests"), 0),
        "accounting_raw_without_manifest_zero": _is_exact_int(
            totals.get("raw_without_manifest"), 0
        ),
        "accounting_unexpected_manifest_paths_zero": _is_exact_int(
            totals.get("unexpected_manifest_paths"), 0
        ),
        "accounting_unexpected_raw_paths_zero": _is_exact_int(
            totals.get("unexpected_raw_paths"), 0
        ),
        "accounting_partition_complete": (
            accounting_raw_backed is not None
            and accounting_not_found is not None
            and accounting_present is not None
            and accounting_raw_backed + accounting_not_found == accounting_present
        ),
        "accounting_gate_pass": accounting.get("accounting_gate_pass") is True,
        "provenance_report_version": _is_exact_int(provenance.get("report_version"), 1),
        "provenance_source": provenance.get("source") == "dukascopy",
        "provenance_granularity": provenance.get("granularity") == "1m",
        "provenance_scope": provenance.get("scope") == "cloud_snapshot_provenance",
        "provenance_frozen_plan_sha256": provenance.get("plan_sha256") == FROZEN_PLAN_SHA256,
        "provenance_planned_chunks_25500": _is_exact_int(
            provenance.get("planned_chunks"), FROZEN_MANIFEST_TARGET
        ),
        "provenance_invalid_manifest_zero": _is_exact_int(
            provenance.get("invalid_manifest"), 0
        ),
        "provenance_raw_checksum_mismatch_zero": _is_exact_int(
            provenance.get("raw_checksum_mismatch"), 0
        ),
        "provenance_raw_size_mismatch_zero": _is_exact_int(
            provenance.get("raw_size_mismatch"), 0
        ),
        "provenance_invalid_raw_audit_zero": _is_exact_int(
            provenance.get("invalid_raw_audit"), 0
        ),
        "provenance_issues_zero": _is_exact_int(provenance.get("issues"), 0),
        "provenance_partition_complete": (
            provenance_complete is not None
            and provenance_not_found is not None
            and provenance_planned is not None
            and provenance_complete + provenance_not_found == provenance_planned
        ),
        "provenance_ready": provenance.get("ready") is True,
        "present_counts_agree": (
            structural_present is not None
            and accounting_present is not None
            and provenance_planned is not None
            and structural_present == accounting_present == provenance_planned
        ),
        "raw_backed_equals_provenance_complete": (
            structural_raw is not None
            and accounting_raw_backed is not None
            and provenance_complete is not None
            and structural_raw == accounting_raw_backed == provenance_complete
        ),
        "inferred_not_found_equals_provenance_not_found": (
            accounting_not_found is not None
            and provenance_not_found is not None
            and accounting_not_found == provenance_not_found
        ),
    }

    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "report_version": 1,
        "scope": "phase1_final_acceptance",
        "frozen_manifest_target": FROZEN_MANIFEST_TARGET,
        "frozen_start_date": FROZEN_START_DATE,
        "frozen_end_date_exclusive": FROZEN_END_DATE_EXCLUSIVE,
        "frozen_plan_sha256": FROZEN_PLAN_SHA256,
        "checks": checks,
        "checks_total": len(checks),
        "checks_failed": len(failed),
        "failed_checks": failed,
        "ready": not failed,
        "note": (
            "ready means Phase 1 acquisition/cloud provenance acceptance only; "
            "Phase 2 remains responsible for market-data cleanliness and normalization."
        ),
    }
