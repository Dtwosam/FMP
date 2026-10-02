from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from . import workflow_source as _exp061_source
from .annual_pattern_catalogue_workflow_plan import (
    CELLS_PER_SEGMENT,
    SEGMENT_COUNT,
    expected_segment_cells,
)
from .annual_pattern_catalogue_method import collection_segments
from .annual_pattern_catalogue_segment_evidence import validate_annual_segment_freeze


ANNUAL_CATALOGUE_WORKFLOW_SOURCE_DECISION = "DEC-478"
ANNUAL_CATALOGUE_WORKFLOW_SOURCE_VERSION = (
    "fmp-annual-pattern-catalogue-dormant-workflow-source-v1"
)
SOURCE_SEGMENT_FREEZE_DECISION = "DEC-477"
SOURCE_SEGMENT_FREEZE_HEAD_SHA = "df3de17a5363c1df0610faa2db9ec72b554fb9bd"

DORMANT_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/phase8a-annual-pattern-catalogue.yml.disabled"
)
RESERVED_ACTIVE_WORKFLOW_PATH = (
    ".github/workflows/phase8a-annual-pattern-catalogue.yml"
)
CLI_PATH = "scripts/phase8a_annual_pattern_catalogue.py"
RUNTIME_REQUIREMENTS_PATH = "requirements/exp061-discovery-run.txt"

FEATURE_RUN = _exp061_source.FEATURE_RUN
OUTCOME_RUN = _exp061_source.OUTCOME_RUN
FEATURE_EVIDENCE_ARTIFACT = _exp061_source.FEATURE_EVIDENCE_ARTIFACT
OUTCOME_EVIDENCE_ARTIFACT = _exp061_source.OUTCOME_EVIDENCE_ARTIFACT

WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED = False
WORKFLOW_INSTALLED = False
WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
NEXT_SEGMENT_EXECUTION_AUTHORIZED = False
CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
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
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_commit(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError("code_commit must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("code_commit must be hexadecimal") from exc
    return value.lower()


def source_artifacts_for_cell(
    symbol: str,
    timeframe: str,
) -> Mapping[str, object]:
    return _exp061_source.source_artifacts_for_cell(symbol, timeframe)


def validate_annual_segment_label(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("DEC-478 annual segment label must be a string")
    expected_segment_cells(value)
    return value


def prior_segment_label(annual_segment_label: str) -> str | None:
    current = validate_annual_segment_label(annual_segment_label)
    labels = tuple(segment.label for segment in collection_segments())
    index = labels.index(current)
    if index == 0:
        return None
    return labels[index - 1]


def validate_prior_segment_freeze(
    *,
    annual_segment_label: str,
    previous_run: Mapping[str, object] | None,
    previous_freeze: Mapping[str, object] | None,
    expected_previous_run_id: int | None,
) -> dict[str, object]:
    current = validate_annual_segment_label(annual_segment_label)
    previous = prior_segment_label(current)
    if previous is None:
        if (
            previous_run is not None
            or previous_freeze is not None
            or expected_previous_run_id is not None
        ):
            raise ValueError("DEC-478 2015 must not provide prior-segment evidence")
        return {
            "annual_segment_label": current,
            "prior_segment_required": False,
            "prior_segment_label": None,
            "prior_run_id": None,
            "prior_run_head_sha": None,
            "prior_freeze_evidence_fingerprint": None,
        }

    if not isinstance(expected_previous_run_id, int) or isinstance(
        expected_previous_run_id, bool
    ) or expected_previous_run_id <= 0:
        raise ValueError("DEC-478 prior annual freeze run id is required")
    if not isinstance(previous_run, Mapping):
        raise ValueError("DEC-478 prior annual freeze run metadata is required")
    if not isinstance(previous_freeze, Mapping):
        raise ValueError("DEC-478 prior annual freeze evidence is required")

    exact_run = {
        "id": expected_previous_run_id,
        "name": "phase8a-annual-pattern-catalogue",
        "path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in exact_run.items():
        if previous_run.get(field) != expected:
            raise ValueError(f"DEC-478 prior run {field} mismatch")
    run_head_sha = _validate_commit(previous_run.get("head_sha"))

    validate_annual_segment_freeze(previous_freeze)
    if previous_freeze.get("annual_segment_label") != previous:
        raise ValueError("DEC-478 prior freeze annual segment mismatch")
    if previous_freeze.get("code_commit") != run_head_sha:
        raise ValueError("DEC-478 prior freeze code commit/run head mismatch")

    fingerprint = previous_freeze.get("evidence_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-478 prior freeze evidence fingerprint malformed")
    return {
        "annual_segment_label": current,
        "prior_segment_required": True,
        "prior_segment_label": previous,
        "prior_run_id": expected_previous_run_id,
        "prior_run_head_sha": run_head_sha,
        "prior_freeze_evidence_fingerprint": fingerprint,
    }


def validate_source_snapshots(
    *,
    feature_run: Mapping[str, object],
    feature_artifacts: Mapping[str, object],
    outcome_run: Mapping[str, object],
    outcome_artifacts: Mapping[str, object],
) -> dict[str, object]:
    predecessor = _exp061_source.validate_source_snapshots(
        feature_run=feature_run,
        feature_artifacts=feature_artifacts,
        outcome_run=outcome_run,
        outcome_artifacts=outcome_artifacts,
    )
    if predecessor.get("source_ready") is not True:
        raise ValueError("DEC-478 accepted EXP-044 source snapshot is not ready")
    report: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_SOURCE_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_SOURCE_VERSION,
        "source_segment_freeze_decision": SOURCE_SEGMENT_FREEZE_DECISION,
        "source_segment_freeze_head_sha": SOURCE_SEGMENT_FREEZE_HEAD_SHA,
        "feature_run_id": predecessor["feature_run_id"],
        "feature_head_sha": predecessor["feature_head_sha"],
        "outcome_run_id": predecessor["outcome_run_id"],
        "outcome_head_sha": predecessor["outcome_head_sha"],
        "feature_evidence_artifact_id": predecessor[
            "feature_evidence_artifact_id"
        ],
        "outcome_evidence_artifact_id": predecessor[
            "outcome_evidence_artifact_id"
        ],
        "verified_pair_timeframe_source_count": predecessor[
            "verified_pair_timeframe_source_count"
        ],
        "source_ready": True,
        "new_data_acquisition_authorized": False,
        "workflow_template_install_authorized": False,
        "workflow_installed": False,
        "workflow_dispatch_authorized": False,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "trading_authorized": False,
    }
    report["source_fingerprint"] = _sha256_bytes(_canonical_json(report))
    return report


def validate_dormant_workflow_template(text: str) -> None:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("DEC-478 dormant workflow template must be non-empty")
    required = (
        "name: phase8a-annual-pattern-catalogue",
        "workflow_dispatch:",
        "annual_segment_label:",
        "previous_annual_freeze_run_id:",
        "name: annual-preflight-${{ inputs.annual_segment_label }}",
        "name: annual-cell-${{ inputs.annual_segment_label }}-"
        "${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-"
        "${{ matrix.dataset.horizon }}m",
        "name: annual-freeze-${{ inputs.annual_segment_label }}",
        "python scripts/phase8a_annual_pattern_catalogue.py preflight",
        "python scripts/phase8a_annual_pattern_catalogue.py require-execution",
        "python scripts/phase8a_annual_pattern_catalogue.py require-prior-freeze",
        "python scripts/phase8a_annual_pattern_catalogue.py cell",
        "python scripts/phase8a_annual_pattern_catalogue.py freeze",
        RUNTIME_REQUIREMENTS_PATH,
    )
    for needle in required:
        if needle not in text:
            raise ValueError(f"DEC-478 workflow template missing frozen source: {needle}")

    labels = tuple(segment.label for segment in collection_segments())
    if len(labels) != SEGMENT_COUNT:
        raise ValueError("DEC-478 annual segment inventory drift")
    options_marker = "        options:\n"
    options_start = text.index(options_marker) + len(options_marker)
    options_end = text.index(
        "      previous_annual_freeze_run_id:\n",
        options_start,
    )
    expected_options = "".join(f'          - "{label}"\n' for label in labels)
    if text[options_start:options_end] != expected_options:
        raise ValueError("DEC-478 workflow annual segment options drift")

    for current, previous in zip(labels[1:], labels[:-1]):
        mapping = f'{current}) previous_segment="{previous}" ;;'
        if mapping not in text:
            raise ValueError(
                f"DEC-478 workflow prior-segment mapping drift: {current}"
            )

    if text.count("          - symbol:") != CELLS_PER_SEGMENT:
        raise ValueError("DEC-478 workflow matrix must contain exactly 18 cells")
    if text.count("            horizon: 60") != 9:
        raise ValueError("DEC-478 workflow must contain nine 60m cells")
    if text.count("            horizon: 240") != 9:
        raise ValueError("DEC-478 workflow must contain nine 240m cells")

    execution_gate = text.index(
        "python scripts/phase8a_annual_pattern_catalogue.py require-execution"
    )
    prior_download = text.index("Fetch exact prior annual freeze evidence")
    prior_validation = text.index(
        "python scripts/phase8a_annual_pattern_catalogue.py require-prior-freeze"
    )
    source_download = text.index(
        "Download exact accepted EXP-044 feature/outcome/evidence artifacts"
    )
    if not execution_gate < prior_download < prior_validation < source_download:
        raise ValueError(
            "DEC-478 execution/prior-freeze/source-download ordering drift"
        )
    if "needs: annual_preflight" not in text:
        raise ValueError("DEC-478 annual cell must depend on annual preflight")
    if "pattern: phase8a-annual-catalogue-cell-${{ inputs.annual_segment_label }}-*-*-*m-${{ github.sha }}" not in text:
        raise ValueError("DEC-478 annual freeze artifact pattern drift")

    if RESERVED_ACTIVE_WORKFLOW_PATH in text:
        raise ValueError("DEC-478 dormant source cannot claim active workflow path")


def validate_dormant_source_files(*, repository_root: Path) -> dict[str, object]:
    root = Path(repository_root)
    template = root / DORMANT_WORKFLOW_TEMPLATE_PATH
    cli = root / CLI_PATH
    active = root / RESERVED_ACTIVE_WORKFLOW_PATH
    if not template.is_file():
        raise ValueError("DEC-478 dormant workflow template is missing")
    if not cli.is_file():
        raise ValueError("DEC-478 dormant CLI source is missing")
    if active.exists():
        raise ValueError("DEC-478 active workflow must not be installed")
    text = template.read_text(encoding="utf-8")
    validate_dormant_workflow_template(text)
    return {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_SOURCE_DECISION,
        "template_sha256": hashlib.sha256(template.read_bytes()).hexdigest(),
        "cli_sha256": hashlib.sha256(cli.read_bytes()).hexdigest(),
        "active_workflow_present": False,
        "workflow_template_install_authorized": False,
        "workflow_installed": False,
        "workflow_dispatch_authorized": False,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
    }


def workflow_source_payload(*, code_commit: str) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    labels = tuple(segment.label for segment in collection_segments())
    if len(labels) != 12:
        raise ValueError("DEC-478 annual segment count drift")
    cell_shape = expected_segment_cells(labels[0])
    if len(cell_shape) != 18:
        raise ValueError("DEC-478 cell shape drift")
    return {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_SOURCE_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_SOURCE_VERSION,
        "source_segment_freeze_decision": SOURCE_SEGMENT_FREEZE_DECISION,
        "source_segment_freeze_head_sha": SOURCE_SEGMENT_FREEZE_HEAD_SHA,
        "code_commit": code_commit,
        "dormant_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "reserved_active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "cli_path": CLI_PATH,
        "runtime_requirements_path": RUNTIME_REQUIREMENTS_PATH,
        "annual_segment_labels": list(labels),
        "prior_segment_dependencies": [
            {
                "annual_segment_label": label,
                "prior_segment_label": prior_segment_label(label),
            }
            for label in labels
        ],
        "prior_freeze_required_after_first_segment": True,
        "cells_per_segment": len(cell_shape),
        "jobs_per_segment": 20,
        "artifacts_per_segment": 20,
        "feature_source_run": dict(FEATURE_RUN),
        "outcome_source_run": dict(OUTCOME_RUN),
        "feature_evidence_artifact": dict(FEATURE_EVIDENCE_ARTIFACT),
        "outcome_evidence_artifact": dict(OUTCOME_EVIDENCE_ARTIFACT),
        "pair_timeframe_source_artifacts": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                **dict(source_artifacts_for_cell(symbol, timeframe)),
            }
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
        ],
        "workflow_template_install_authorized": WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED,
        "workflow_installed": WORKFLOW_INSTALLED,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
        "historical_result_production_authorized": HISTORICAL_RESULT_PRODUCTION_AUTHORIZED,
        "next_segment_execution_authorized": NEXT_SEGMENT_EXECUTION_AUTHORIZED,
        "cross_year_result_production_authorized": CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED,
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_CONTRACT",
    }


__all__ = [
    "ANNUAL_CATALOGUE_WORKFLOW_SOURCE_DECISION",
    "ANNUAL_CATALOGUE_WORKFLOW_SOURCE_VERSION",
    "CLI_PATH",
    "DORMANT_WORKFLOW_TEMPLATE_PATH",
    "FEATURE_EVIDENCE_ARTIFACT",
    "FEATURE_RUN",
    "OUTCOME_EVIDENCE_ARTIFACT",
    "OUTCOME_RUN",
    "RESERVED_ACTIVE_WORKFLOW_PATH",
    "prior_segment_label",
    "source_artifacts_for_cell",
    "validate_annual_segment_label",
    "validate_prior_segment_freeze",
    "validate_dormant_source_files",
    "validate_dormant_workflow_template",
    "validate_source_snapshots",
    "workflow_source_payload",
]
