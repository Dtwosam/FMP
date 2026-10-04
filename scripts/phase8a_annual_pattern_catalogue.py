from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_evidence import (
    validated_cell_summary,
)
from fmp.discovery.annual_pattern_catalogue_runtime import (
    require_historical_catalogue_execution_authorized,
    run_locked_annual_catalogue_cell,
)
from fmp.discovery.annual_pattern_catalogue_segment_evidence import (
    EXPECTED_CELLS_PER_SEGMENT,
    compile_annual_segment_freeze,
    validate_annual_segment_freeze,
)
from fmp.discovery.annual_pattern_catalogue_workflow_corrected_install_receipt import (
    validate_corrected_annual_workflow_install_receipt_sources,
)
from fmp.discovery.annual_pattern_catalogue_workflow_source import (
    validate_annual_segment_label,
    validate_prior_segment_freeze,
    validate_source_snapshots,
    workflow_source_payload,
)


def _read_json(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(
            dict(value),
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    if (
        destination.exists()
        and destination.read_text(encoding="utf-8") != payload
    ):
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _write_bytes(path: Path, value: bytes) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() != value:
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_bytes(value)


def _cmd_status(args: argparse.Namespace) -> int:
    value = workflow_source_payload(code_commit=args.code_commit)
    value["installed_workflow_receipt_sources"] = (
        validate_corrected_annual_workflow_install_receipt_sources(
            repository_root=Path(".")
        )
    )
    print(json.dumps(value, sort_keys=True, indent=2, allow_nan=False))
    return 0


def _cmd_preflight(args: argparse.Namespace) -> int:
    validate_annual_segment_label(args.annual_segment_label)
    report = validate_source_snapshots(
        feature_run=_read_json(args.feature_run_json),
        feature_artifacts=_read_json(args.feature_artifacts_json),
        outcome_run=_read_json(args.outcome_run_json),
        outcome_artifacts=_read_json(args.outcome_artifacts_json),
    )
    value = dict(report)
    value["annual_segment_label"] = args.annual_segment_label
    value["code_commit"] = args.code_commit
    value["workflow_source"] = workflow_source_payload(
        code_commit=args.code_commit
    )
    value["installed_workflow_receipt_sources"] = (
        validate_corrected_annual_workflow_install_receipt_sources(
            repository_root=Path(".")
        )
    )
    _write_json(args.out, value)
    return 0


def _cmd_require_execution(args: argparse.Namespace) -> int:
    validate_annual_segment_label(args.annual_segment_label)
    # The runtime gate is intentionally closed in DEC-475/478.
    require_historical_catalogue_execution_authorized(
        code_commit=args.code_commit
    )
    return 0


def _cmd_require_prior_freeze(args: argparse.Namespace) -> int:
    previous_run = (
        _read_json(args.previous_run_json)
        if args.previous_run_json is not None
        else None
    )
    previous_freeze = (
        _read_json(args.previous_freeze_evidence)
        if args.previous_freeze_evidence is not None
        else None
    )
    report = validate_prior_segment_freeze(
        annual_segment_label=args.annual_segment_label,
        previous_run=previous_run,
        previous_freeze=previous_freeze,
        expected_previous_run_id=args.expected_previous_run_id,
    )
    _write_json(args.out, report)
    return 0


def _cmd_cell(args: argparse.Namespace) -> int:
    validate_annual_segment_label(args.annual_segment_label)
    product = run_locked_annual_catalogue_cell(
        feature_root=args.feature_root,
        outcome_root=args.outcome_root,
        feature_evidence_path=args.feature_evidence,
        outcome_evidence_path=args.outcome_evidence,
        annual_segment_label=args.annual_segment_label,
        symbol=args.symbol,
        timeframe=args.timeframe,
        horizon_minutes=args.horizon_minutes,
        code_commit=args.code_commit,
    )
    _write_json(args.evidence_out, product.evidence)
    _write_bytes(args.catalogue_out, product.catalogue_payload_bytes)
    return 0


def _load_validated_cell_summaries(root: Path):
    paths = sorted(Path(root).rglob("cell-evidence.json"))
    if len(paths) != EXPECTED_CELLS_PER_SEGMENT:
        raise ValueError(
            f"annual freeze requires exactly {EXPECTED_CELLS_PER_SEGMENT} "
            "cell-evidence.json files"
        )
    summaries = []
    for evidence_path in paths:
        payload_path = evidence_path.with_name("catalogue-payload.json")
        if not payload_path.is_file():
            raise ValueError(
                f"missing catalogue payload beside cell evidence: {evidence_path}"
            )
        summaries.append(
            validated_cell_summary(
                _read_json(evidence_path),
                payload_path.read_bytes(),
            )
        )
    return summaries


def _cmd_freeze(args: argparse.Namespace) -> int:
    validate_annual_segment_label(args.annual_segment_label)
    # This gate remains before any historical result artifact is opened.
    require_historical_catalogue_execution_authorized(
        code_commit=args.code_commit
    )
    evidence = compile_annual_segment_freeze(
        _load_validated_cell_summaries(args.result_root),
        annual_segment_label=args.annual_segment_label,
        code_commit=args.code_commit,
    )
    validate_annual_segment_freeze(evidence)
    _write_json(args.out, evidence)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Source-only annual pattern catalogue dormant workflow CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status")
    status.add_argument("--code-commit", required=True)
    status.set_defaults(func=_cmd_status)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--feature-run-json", type=Path, required=True)
    preflight.add_argument("--feature-artifacts-json", type=Path, required=True)
    preflight.add_argument("--outcome-run-json", type=Path, required=True)
    preflight.add_argument("--outcome-artifacts-json", type=Path, required=True)
    preflight.add_argument("--annual-segment-label", required=True)
    preflight.add_argument("--code-commit", required=True)
    preflight.add_argument("--out", type=Path, required=True)
    preflight.set_defaults(func=_cmd_preflight)

    require = subparsers.add_parser("require-execution")
    require.add_argument("--annual-segment-label", required=True)
    require.add_argument("--code-commit", required=True)
    require.set_defaults(func=_cmd_require_execution)

    prior = subparsers.add_parser("require-prior-freeze")
    prior.add_argument("--annual-segment-label", required=True)
    prior.add_argument("--expected-previous-run-id", type=int)
    prior.add_argument("--previous-run-json", type=Path)
    prior.add_argument("--previous-freeze-evidence", type=Path)
    prior.add_argument("--out", type=Path, required=True)
    prior.set_defaults(func=_cmd_require_prior_freeze)

    cell = subparsers.add_parser("cell")
    cell.add_argument("--feature-root", type=Path, required=True)
    cell.add_argument("--outcome-root", type=Path, required=True)
    cell.add_argument("--feature-evidence", type=Path, required=True)
    cell.add_argument("--outcome-evidence", type=Path, required=True)
    cell.add_argument("--annual-segment-label", required=True)
    cell.add_argument("--symbol", required=True)
    cell.add_argument("--timeframe", required=True)
    cell.add_argument("--horizon-minutes", type=int, required=True)
    cell.add_argument("--code-commit", required=True)
    cell.add_argument("--evidence-out", type=Path, required=True)
    cell.add_argument("--catalogue-out", type=Path, required=True)
    cell.set_defaults(func=_cmd_cell)

    freeze = subparsers.add_parser("freeze")
    freeze.add_argument("--result-root", type=Path, required=True)
    freeze.add_argument("--annual-segment-label", required=True)
    freeze.add_argument("--code-commit", required=True)
    freeze.add_argument("--out", type=Path, required=True)
    freeze.set_defaults(func=_cmd_freeze)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
