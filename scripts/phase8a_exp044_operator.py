from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence

from fmp.market_learning.evidence import load_feature_evidence_index
from fmp.market_learning.execution_status import build_execution_status
from fmp.market_learning.model_execution_gate import build_model_workflow_source_gate
from fmp.market_learning.model_protocol import protocol_fingerprint
from fmp.market_learning.model_result_evidence import (
    load_model_result_evidence,
    validate_model_result_evidence,
)
from fmp.market_learning.model_run_gate import build_model_run_source_gate
from fmp.market_learning.operator import (
    FEATURE_WORKFLOW_NAME,
    MODEL_WORKFLOW_NAME,
    OUTCOME_WORKFLOW_NAME,
    PRESERVATION_WORKFLOW_NAME,
    REPOSITORY,
    artifact_download_endpoint,
    classify_manual_run,
    dispatch_command_for_next_report,
    feature_dispatch_command,
    feature_run_artifacts_endpoint,
    feature_run_endpoint,
    feature_runs_endpoint,
    model_dispatch_command,
    model_run_artifacts_endpoint,
    model_run_endpoint,
    model_runs_endpoint,
    outcome_dispatch_command,
    outcome_run_artifacts_endpoint,
    outcome_run_endpoint,
    outcome_runs_endpoint,
    release_asset_download_endpoint,
    preservation_dispatch_command,
    preservation_runs_endpoint,
    select_feature_evidence_artifact,
    select_latest_manual_main_run_after_reviewed_failures,
    select_model_result_artifact,
    select_only_manual_main_run,
    select_outcome_evidence_artifacts,
    shell_join,
    validate_feature_evidence_for_outcomes,
    validate_feature_run_for_outcomes,
    validate_model_run_for_result,
    validate_no_existing_manual_runs,
    validate_operator_checkout,
    validate_outcome_run_for_readiness,
)
from fmp.market_learning.outcome_evidence import load_outcome_evidence_index
from fmp.market_learning.readiness import load_training_readiness
from fmp.market_learning.source_availability import compile_source_availability
from fmp.market_learning.source_preflight import (
    SOURCE_ARTIFACTS,
    compile_source_preflight,
)
from fmp.market_learning.source_preservation import (
    PRESERVATION_TAG,
    select_preservation_manifest_asset,
    validate_published_release_metadata,
)


REVIEWED_FAILED_OUTCOME_RUN_IDS = frozenset({35869906438})
REVIEWED_FAILED_MODEL_RUN_IDS = frozenset({35891605645})


def _run(command: Sequence[str], *, capture: bool = True) -> str:
    completed = subprocess.run(
        list(command),
        check=True,
        text=True,
        capture_output=capture,
    )
    return completed.stdout.strip() if capture else ""


def _gh_json(endpoint: str) -> dict[str, object]:
    raw = _run(("gh", "api", endpoint))
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"GitHub API returned invalid JSON for {endpoint}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"GitHub API returned a non-object for {endpoint}")
    return value


def _gh_json_optional(endpoint: str) -> dict[str, object] | None:
    completed = subprocess.run(
        ["gh", "api", endpoint],
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        return None
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"GitHub API returned invalid JSON for {endpoint}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"GitHub API returned a non-object for {endpoint}")
    return value


def _original_source_preflight() -> dict[str, object]:
    metadata: dict[str, dict[str, object]] = {}
    for spec in SOURCE_ARTIFACTS:
        metadata[spec.symbol] = _gh_json(
            f"repos/{REPOSITORY}/actions/artifacts/{spec.artifact_id}"
        )
    return compile_source_preflight(
        metadata_by_symbol=metadata,
        now_utc=datetime.now(timezone.utc),
        minimum_remaining=timedelta(hours=12),
    )


def _download_release_json_asset(*, asset_id: int) -> Mapping[str, object]:
    with tempfile.TemporaryDirectory(prefix="fmp-phase2-release-") as tmp:
        path = Path(tmp) / "asset.json"
        with path.open("wb") as handle:
            subprocess.run(
                [
                    "gh",
                    "api",
                    "-H",
                    "Accept: application/octet-stream",
                    release_asset_download_endpoint(asset_id),
                ],
                check=True,
                stdout=handle,
            )
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SystemExit("preservation manifest release asset is invalid JSON") from exc
        if not isinstance(value, dict):
            raise SystemExit("preservation manifest release asset must be an object")
        return value


def _source_artifact_preflight() -> dict[str, object]:
    metadata: dict[str, dict[str, object]] = {}
    for spec in SOURCE_ARTIFACTS:
        value = _gh_json_optional(
            f"repos/{REPOSITORY}/actions/artifacts/{spec.artifact_id}"
        )
        metadata[spec.symbol] = value if value is not None else {"unavailable": True}

    now = datetime.now(timezone.utc)
    minimum = timedelta(hours=12)
    try:
        return compile_source_availability(
            metadata_by_symbol=metadata,
            now_utc=now,
            minimum_remaining=minimum,
        )
    except ValueError:
        release = _gh_json_optional(
            f"repos/{REPOSITORY}/releases/tags/{PRESERVATION_TAG}"
        )
        if release is None:
            raise SystemExit(
                "original Phase 2 artifacts are unavailable and the preservation release is missing"
            )
        selected = select_preservation_manifest_asset(release)
        manifest = _download_release_json_asset(asset_id=int(selected["asset_id"]))
        return compile_source_availability(
            metadata_by_symbol=metadata,
            now_utc=now,
            minimum_remaining=minimum,
            release=release,
            preservation_manifest=manifest,
        )

def _safe_extract_zip(archive_path: Path, destination: Path) -> None:
    root = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise SystemExit("feature evidence ZIP contains an unsafe path") from exc
        archive.extractall(destination)


def _download_json_artifact(
    *,
    artifact_id: int,
    expected_filename: str,
    loader: Callable[[Path], Mapping[str, object]],
) -> Mapping[str, object]:
    with tempfile.TemporaryDirectory(prefix="fmp-exp044-artifact-") as tmp:
        root = Path(tmp)
        archive_path = root / "artifact.zip"
        extracted = root / "extracted"
        extracted.mkdir()
        with archive_path.open("wb") as handle:
            subprocess.run(
                [
                    "gh",
                    "api",
                    "-H",
                    "Accept: application/vnd.github+json",
                    artifact_download_endpoint(artifact_id),
                ],
                check=True,
                stdout=handle,
            )
        _safe_extract_zip(archive_path, extracted)
        matches = sorted(extracted.rglob(expected_filename))
        if len(matches) != 1:
            raise SystemExit(
                f"artifact ZIP must contain exactly one {expected_filename}"
            )
        return loader(matches[0])


def _download_feature_evidence(
    *,
    feature_run_id: int,
    feature_head_sha: str,
) -> tuple[dict[str, object], Mapping[str, object]]:
    artifacts = _gh_json(feature_run_artifacts_endpoint(feature_run_id))
    selected = select_feature_evidence_artifact(
        artifacts,
        feature_head_sha=feature_head_sha,
    )
    artifact_id = int(selected["artifact_id"])
    evidence = _download_json_artifact(
        artifact_id=artifact_id,
        expected_filename="feature-evidence.json",
        loader=load_feature_evidence_index,
    )
    verified = validate_feature_evidence_for_outcomes(
        evidence,
        expected_code_commit=feature_head_sha,
    )
    return (
        {
            **selected,
            **verified,
        },
        evidence,
    )


def _download_outcome_readiness_bundle(
    *,
    outcome_run_id: int,
    outcome_head_sha: str,
    feature_head_sha: str,
) -> tuple[dict[str, object], Mapping[str, object], Mapping[str, object]]:
    artifacts = _gh_json(outcome_run_artifacts_endpoint(outcome_run_id))
    selected = select_outcome_evidence_artifacts(
        artifacts,
        outcome_head_sha=outcome_head_sha,
        feature_head_sha=feature_head_sha,
    )
    outcome_evidence = _download_json_artifact(
        artifact_id=int(selected["outcome_evidence_artifact_id"]),
        expected_filename="outcome-evidence.json",
        loader=load_outcome_evidence_index,
    )
    readiness = _download_json_artifact(
        artifact_id=int(selected["readiness_artifact_id"]),
        expected_filename="readiness.json",
        loader=load_training_readiness,
    )
    return selected, outcome_evidence, readiness


def _published_preservation() -> dict[str, object] | None:
    release = _gh_json_optional(
        f"repos/{REPOSITORY}/releases/tags/{PRESERVATION_TAG}"
    )
    if release is None:
        return None
    selected = select_preservation_manifest_asset(release)
    manifest = _download_release_json_asset(asset_id=int(selected["asset_id"]))
    verified = validate_published_release_metadata(
        release=release,
        manifest=manifest,
    )
    return {
        "release": release,
        "manifest": manifest,
        "verified": verified,
    }


def _next_report(
    *,
    checkout: Mapping[str, object],
    stage: str,
    next_action: str,
    dispatch_command: Sequence[str] | None = None,
    model_protocol_result_authorized: bool = False,
    model_fit_authorized: bool = False,
    **details: object,
) -> dict[str, object]:
    report: dict[str, object] = {
        **dict(checkout),
        **details,
        "stage": stage,
        "next_action": next_action,
        "read_only": True,
        "model_protocol_result_authorized": (
            model_protocol_result_authorized
        ),
        "model_fit_authorized": model_fit_authorized,
        "promotion_authorized": False,
        "trading_authorized": False,
    }
    if dispatch_command is not None:
        report["dispatch_command"] = shell_join(dispatch_command)
    return report


def _checkout_preflight() -> dict[str, object]:
    _run(("git", "fetch", "--quiet", "origin", "main"), capture=False)
    return validate_operator_checkout(
        branch=_run(("git", "branch", "--show-current")),
        head_sha=_run(("git", "rev-parse", "HEAD")),
        origin_main_sha=_run(("git", "rev-parse", "origin/main")),
        porcelain_status=_run(("git", "status", "--porcelain")),
        origin_url=_run(("git", "remote", "get-url", "origin")),
    )


def _require_gh_auth() -> None:
    try:
        _run(("gh", "auth", "status"))
    except subprocess.CalledProcessError as exc:
        raise SystemExit("GitHub CLI authentication is required before EXP-044 dispatch") from exc


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Safely prepare or perform the manual EXP-044 GitHub workflow dispatch"
    )
    sub = out.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "next",
        help="inspect live EXP-044 evidence and report exactly one next authoritative action",
    )

    advance = sub.add_parser(
        "advance",
        help="prepare or execute exactly one DEC-086-authorized next dispatch",
    )
    advance.add_argument("--execute", action="store_true")

    preserve = sub.add_parser(
        "preserve-phase2",
        help="prepare or dispatch exact Phase 2 release preservation",
    )
    preserve.add_argument("--execute", action="store_true")

    features = sub.add_parser("features", help="prepare or dispatch EXP-044 feature generation")
    features.add_argument("--execute", action="store_true")

    outcomes = sub.add_parser("outcomes", help="prepare or dispatch EXP-044 outcome materialization")
    outcomes.add_argument("--feature-run-id", type=int, required=True)
    outcomes.add_argument("--execute", action="store_true")

    readiness = sub.add_parser(
        "readiness",
        help="verify the completed feature/outcome/readiness evidence chain",
    )
    readiness.add_argument("--feature-run-id", type=int, required=True)
    readiness.add_argument("--outcome-run-id", type=int, required=True)
    return out


def _print_report(report: dict[str, object]) -> None:
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))


def _read_next_plan_via_public_cli() -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "next"],
        check=True,
        text=True,
        capture_output=True,
    )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit("DEC-086 next planner did not return valid JSON") from exc
    if not isinstance(value, dict):
        raise SystemExit("DEC-086 next planner must return a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    _require_gh_auth()
    checkout = _checkout_preflight()

    if args.command == "advance":
        plan = _read_next_plan_via_public_cli()
        command = dispatch_command_for_next_report(plan)
        report = {
            **plan,
            "advance_execute_requested": bool(args.execute),
            "advance_dispatchable": command is not None,
        }
        if not args.execute or command is None:
            report["dispatch_submitted"] = False
            _print_report(report)
            return 0

        confirmed = _read_next_plan_via_public_cli()
        if confirmed != plan:
            raise SystemExit(
                "EXP-044 live state changed between planning and execution; rerun advance"
            )
        confirmed_command = dispatch_command_for_next_report(confirmed)
        if confirmed_command != command:
            raise SystemExit("EXP-044 dispatch plan changed before execution")

        _run(command, capture=False)
        report["read_only"] = False
        report["dispatch_submitted"] = True
        report["result_claimed"] = False
        _print_report(report)
        return 0

    if args.command == "next":
        preservation = _published_preservation()
        preservation_listing = _gh_json(preservation_runs_endpoint())
        preservation_run = select_only_manual_main_run(
            preservation_listing,
            workflow_name=PRESERVATION_WORKFLOW_NAME,
        )
        preservation_state = classify_manual_run(
            preservation_run,
            workflow_name=PRESERVATION_WORKFLOW_NAME,
        )

        if preservation is None:
            run_state = preservation_state["run_state"]
            if run_state == "MISSING":
                source_preflight = _original_source_preflight()
                _print_report(
                    _next_report(
                        checkout=checkout,
                        stage="PRESERVATION_DISPATCH_REQUIRED",
                        next_action=(
                            "Dispatch exact Phase 2 preservation before EXP-044 "
                            "feature generation."
                        ),
                        dispatch_command=preservation_dispatch_command(),
                        source_preflight_ready=source_preflight["source_ready"],
                        source_earliest_expires_at=source_preflight[
                            "earliest_expires_at"
                        ],
                        preservation_release_verified=False,
                        preservation_run_state=run_state,
                    )
                )
                return 0
            if run_state == "IN_PROGRESS":
                _print_report(
                    _next_report(
                        checkout=checkout,
                        stage="PRESERVATION_RUN_IN_PROGRESS",
                        next_action=(
                            "Inspect the existing preservation workflow run; do not "
                            "create a duplicate."
                        ),
                        preservation_release_verified=False,
                        preservation_run_state=run_state,
                        preservation_run_id=preservation_state["run_id"],
                    )
                )
                return 0
            if run_state == "FAILED":
                _print_report(
                    _next_report(
                        checkout=checkout,
                        stage="PRESERVATION_REVIEW_REQUIRED",
                        next_action=(
                            "Review the failed preservation workflow evidence; do not "
                            "retry automatically."
                        ),
                        preservation_release_verified=False,
                        preservation_run_state=run_state,
                        preservation_run_id=preservation_state["run_id"],
                    )
                )
                return 0
            raise SystemExit(
                "preservation workflow succeeded but the exact published release is missing"
            )

        feature_listing = _gh_json(feature_runs_endpoint())
        feature_run = select_only_manual_main_run(
            feature_listing,
            workflow_name=FEATURE_WORKFLOW_NAME,
        )
        feature_state = classify_manual_run(
            feature_run,
            workflow_name=FEATURE_WORKFLOW_NAME,
        )
        if feature_state["run_state"] == "MISSING":
            source_preflight = _source_artifact_preflight()
            _print_report(
                _next_report(
                    checkout=checkout,
                    stage="FEATURE_DISPATCH_REQUIRED",
                    next_action="Dispatch EXP-044 feature generation from merged main.",
                    dispatch_command=feature_dispatch_command(),
                    preservation_release_verified=True,
                    preservation_tag=PRESERVATION_TAG,
                    source_mode=source_preflight["source_mode"],
                    feature_run_state="MISSING",
                )
            )
            return 0
        if feature_state["run_state"] == "IN_PROGRESS":
            _print_report(
                _next_report(
                    checkout=checkout,
                    stage="FEATURE_RUN_IN_PROGRESS",
                    next_action=(
                        "Inspect the existing feature workflow run; do not create a duplicate."
                    ),
                    preservation_release_verified=True,
                    feature_run_state="IN_PROGRESS",
                    feature_run_id=feature_state["run_id"],
                )
            )
            return 0
        if feature_state["run_state"] == "FAILED":
            _print_report(
                _next_report(
                    checkout=checkout,
                    stage="FEATURE_REVIEW_REQUIRED",
                    next_action=(
                        "Review the failed feature workflow evidence; do not retry automatically."
                    ),
                    preservation_release_verified=True,
                    feature_run_state="FAILED",
                    feature_run_id=feature_state["run_id"],
                )
            )
            return 0

        feature_run_id = int(feature_state["run_id"])
        feature_run_exact = _gh_json(feature_run_endpoint(feature_run_id))
        feature = validate_feature_run_for_outcomes(
            feature_run_exact,
            expected_run_id=feature_run_id,
        )
        feature_evidence_summary, feature_evidence = _download_feature_evidence(
            feature_run_id=feature_run_id,
            feature_head_sha=str(feature["feature_head_sha"]),
        )
        feature_report_details = {
            **feature,
            **feature_evidence_summary,
        }

        outcome_listing = _gh_json(outcome_runs_endpoint())
        outcome_run = select_latest_manual_main_run_after_reviewed_failures(
            outcome_listing,
            workflow_name=OUTCOME_WORKFLOW_NAME,
            reviewed_failed_run_ids=REVIEWED_FAILED_OUTCOME_RUN_IDS,
        )
        outcome_state = classify_manual_run(
            outcome_run,
            workflow_name=OUTCOME_WORKFLOW_NAME,
        )
        if outcome_state["run_state"] == "MISSING":
            source_preflight = _source_artifact_preflight()
            _print_report(
                _next_report(
                    checkout=checkout,
                    stage="OUTCOME_DISPATCH_REQUIRED",
                    next_action=(
                        "Dispatch EXP-044 outcomes using the exact verified feature run."
                    ),
                    dispatch_command=outcome_dispatch_command(feature_run_id),
                    preservation_release_verified=True,
                    source_mode=source_preflight["source_mode"],
                    **feature_report_details,
                    outcome_run_state="MISSING",
                )
            )
            return 0
        if outcome_state["run_state"] == "IN_PROGRESS":
            _print_report(
                _next_report(
                    checkout=checkout,
                    stage="OUTCOME_RUN_IN_PROGRESS",
                    next_action=(
                        "Inspect the existing outcome workflow run; do not create a duplicate."
                    ),
                    **feature_report_details,
                    outcome_run_state="IN_PROGRESS",
                    outcome_run_id=outcome_state["run_id"],
                )
            )
            return 0
        if outcome_state["run_state"] == "FAILED":
            failed_run_id = int(outcome_state["run_id"])
            failed_head_sha = (
                outcome_run.get("head_sha")
                if outcome_run is not None
                else None
            )
            if (
                failed_run_id in REVIEWED_FAILED_OUTCOME_RUN_IDS
                and isinstance(failed_head_sha, str)
                and failed_head_sha != checkout["head_sha"]
            ):
                source_preflight = _source_artifact_preflight()
                _print_report(
                    _next_report(
                        checkout=checkout,
                        stage="OUTCOME_REPLACEMENT_DISPATCH_REQUIRED",
                        next_action=(
                            "Dispatch one replacement EXP-044 outcome run after "
                            "the reviewed workflow-shell failure."
                        ),
                        dispatch_command=outcome_dispatch_command(feature_run_id),
                        preservation_release_verified=True,
                        source_mode=source_preflight["source_mode"],
                        **feature_report_details,
                        outcome_run_state="FAILED",
                        reviewed_failed_outcome_run_id=failed_run_id,
                        reviewed_failed_outcome_head_sha=failed_head_sha,
                    )
                )
                return 0

            _print_report(
                _next_report(
                    checkout=checkout,
                    stage="OUTCOME_REVIEW_REQUIRED",
                    next_action=(
                        "Review the failed outcome workflow evidence; do not retry automatically."
                    ),
                    **feature_report_details,
                    outcome_run_state="FAILED",
                    outcome_run_id=outcome_state["run_id"],
                )
            )
            return 0

        outcome_run_id = int(outcome_state["run_id"])
        outcome_run_exact = _gh_json(outcome_run_endpoint(outcome_run_id))
        outcome = validate_outcome_run_for_readiness(
            outcome_run_exact,
            expected_run_id=outcome_run_id,
        )
        selected, outcome_evidence, readiness = _download_outcome_readiness_bundle(
            outcome_run_id=outcome_run_id,
            outcome_head_sha=str(outcome["outcome_head_sha"]),
            feature_head_sha=str(feature["feature_head_sha"]),
        )
        status = build_execution_status(
            feature_run=feature_run_exact,
            feature_evidence=feature_evidence,
            outcome_run=outcome_run_exact,
            outcome_evidence=outcome_evidence,
            readiness=readiness,
        )
        gate = build_model_run_source_gate(
            execution_status=status,
            protocol_fingerprint_value=protocol_fingerprint(),
            feature_run_id=feature_run_id,
            feature_evidence_fingerprint=str(
                feature_evidence_summary["feature_evidence_fingerprint"]
            ),
            outcome_run_id=outcome_run_id,
            outcome_evidence_artifact_id=int(
                selected["outcome_evidence_artifact_id"]
            ),
            readiness_artifact_id=int(selected["readiness_artifact_id"]),
        )
        if gate.get("stage") != "MODEL_PROTOCOL_FROZEN":
            raise SystemExit("EXP-044 model-run source gate returned an invalid stage")
        workflow_gate = build_model_workflow_source_gate(
            repository_root=Path(__file__).resolve().parents[1],
        )
        if workflow_gate.get("stage") != "MODEL_RUN_WORKFLOW_SOURCE_FROZEN":
            raise SystemExit(
                "EXP-044 model-workflow source gate returned an invalid stage"
            )
        for field in (
            "model_run_dispatch_authorized",
            "authoritative_model_result_execution_authorized",
            "model_protocol_result_authorized",
            "model_fit_authorized",
        ):
            if workflow_gate.get(field) is not True:
                raise SystemExit(
                    f"EXP-044 DEC-093 authorization field is not open: {field}"
                )

        readiness_report_details = {
            **feature_report_details,
            **outcome,
            **selected,
        }
        workflow_report_details = {
            **readiness_report_details,
            "readiness_verified": status["readiness_verified"],
            "model_protocol_source_open_authorized": status[
                "model_protocol_source_open_authorized"
            ],
            "model_protocol_frozen": gate["model_protocol_frozen"],
            "model_run_source_open_authorized": gate[
                "model_run_source_open_authorized"
            ],
            "model_protocol_decision": gate["model_protocol_decision"],
            "model_protocol_version": gate["model_protocol_version"],
            "model_protocol_source_commit": gate[
                "model_protocol_source_commit"
            ],
            "model_protocol_fingerprint": gate[
                "model_protocol_fingerprint"
            ],
            "model_run_workflow_source_frozen": workflow_gate[
                "model_run_workflow_source_frozen"
            ],
            "model_execution_authorization_decision": workflow_gate[
                "model_execution_authorization_decision"
            ],
            "dec092_merged_commit": workflow_gate[
                "dec092_merged_commit"
            ],
            "dec093_workflow_blob_sha": workflow_gate[
                "dec093_workflow_blob_sha"
            ],
            "dec094_workflow_blob_sha": workflow_gate[
                "dec094_workflow_blob_sha"
            ],
            "reviewed_failed_model_run_id": workflow_gate[
                "reviewed_failed_model_run_id"
            ],
            "dec092_cli_blob_sha": workflow_gate[
                "dec092_cli_blob_sha"
            ],
            "artifact_runner_blob_sha": workflow_gate[
                "artifact_runner_blob_sha"
            ],
            "training_core_blob_sha": workflow_gate[
                "training_core_blob_sha"
            ],
            "model_protocol_blob_sha": workflow_gate[
                "model_protocol_blob_sha"
            ],
        }

        model_listing = _gh_json(model_runs_endpoint())
        model_run = select_latest_manual_main_run_after_reviewed_failures(
            model_listing,
            workflow_name=MODEL_WORKFLOW_NAME,
            reviewed_failed_run_ids=REVIEWED_FAILED_MODEL_RUN_IDS,
        )
        model_state = classify_manual_run(
            model_run,
            workflow_name=MODEL_WORKFLOW_NAME,
        )
        if model_state["run_state"] == "MISSING":
            _print_report(
                _next_report(
                    checkout=checkout,
                    stage="MODEL_RUN_REVIEW_REQUIRED",
                    next_action=(
                        "DEC-094 replacement authorization requires the reviewed "
                        "failed model run 35891605645. Do not dispatch."
                    ),
                    preservation_release_verified=True,
                    **workflow_report_details,
                    model_run_state="MISSING",
                    model_run_dispatch_authorized=False,
                    authoritative_model_result_execution_authorized=False,
                )
            )
            return 0

        if model_state["run_state"] == "IN_PROGRESS":
            _print_report(
                _next_report(
                    checkout=checkout,
                    stage="MODEL_RUN_IN_PROGRESS",
                    next_action=(
                        "Inspect the existing model workflow run; do not create "
                        "another model run."
                    ),
                    preservation_release_verified=True,
                    **workflow_report_details,
                    model_run_state="IN_PROGRESS",
                    model_run_id=model_state["run_id"],
                    model_run_dispatch_authorized=False,
                    authoritative_model_result_execution_authorized=False,
                )
            )
            return 0

        if model_state["run_state"] == "FAILED":
            failed_run_id = int(model_state["run_id"])
            if failed_run_id in REVIEWED_FAILED_MODEL_RUN_IDS:
                _print_report(
                    _next_report(
                        checkout=checkout,
                        stage="MODEL_RUN_REPLACEMENT_DISPATCH_REQUIRED",
                        next_action=(
                            "Dispatch exactly one reviewed replacement EXP-044 "
                            "historical model-result run from merged main."
                        ),
                        dispatch_command=model_dispatch_command(),
                        model_protocol_result_authorized=True,
                        model_fit_authorized=True,
                        preservation_release_verified=True,
                        **workflow_report_details,
                        model_run_state="REVIEWED_FAILED",
                        model_run_id=failed_run_id,
                        model_run_dispatch_authorized=True,
                        authoritative_model_result_execution_authorized=True,
                    )
                )
                return 0

            _print_report(
                _next_report(
                    checkout=checkout,
                    stage="MODEL_RUN_REVIEW_REQUIRED",
                    next_action=(
                        "Review the failed replacement model workflow evidence; "
                        "do not retry or replace it automatically."
                    ),
                    preservation_release_verified=True,
                    **workflow_report_details,
                    model_run_state="FAILED",
                    model_run_id=failed_run_id,
                    model_run_dispatch_authorized=False,
                    authoritative_model_result_execution_authorized=False,
                )
            )
            return 0

        model_run_id = int(model_state["run_id"])
        model_run_exact = _gh_json(model_run_endpoint(model_run_id))
        model = validate_model_run_for_result(
            model_run_exact,
            expected_run_id=model_run_id,
        )
        model_artifacts = _gh_json(
            model_run_artifacts_endpoint(model_run_id)
        )
        model_selected = select_model_result_artifact(
            model_artifacts,
            model_head_sha=str(model["model_head_sha"]),
        )
        model_evidence = _download_json_artifact(
            artifact_id=int(model_selected["model_result_artifact_id"]),
            expected_filename="model-result-evidence.json",
            loader=lambda path: load_model_result_evidence(
                path,
                expected_code_commit=str(model["model_head_sha"]),
            ),
        )
        model_summary = validate_model_result_evidence(
            model_evidence,
            expected_code_commit=str(model["model_head_sha"]),
        )
        _print_report(
            _next_report(
                checkout=checkout,
                stage="MODEL_RESULT_REVIEW_REQUIRED",
                next_action=(
                    "Review the verified retrospective EXP-044 model-result "
                    "evidence. Do not promote or open shadow/demo/trading activity."
                ),
                preservation_release_verified=True,
                **workflow_report_details,
                **model,
                **model_selected,
                **model_summary,
                model_run_state="SUCCESS",
                model_run_dispatch_authorized=False,
                authoritative_model_result_execution_authorized=False,
            )
        )
        return 0

    if args.command == "preserve-phase2":
        source_preflight = _original_source_preflight()
        listing = _gh_json(preservation_runs_endpoint())
        validate_no_existing_manual_runs(
            listing,
            workflow_name=PRESERVATION_WORKFLOW_NAME,
        )
        command = preservation_dispatch_command()
        report: dict[str, object] = {
            **checkout,
            "source_preflight_ready": source_preflight["source_ready"],
            "source_earliest_expires_at": source_preflight["earliest_expires_at"],
            "stage": "preserve-phase2",
            "existing_manual_main_runs": 0,
            "ready_to_dispatch": True,
            "execute_requested": bool(args.execute),
            "dispatch_command": shell_join(command),
            "model_fit_authorized": False,
            "promotion_authorized": False,
            "trading_authorized": False,
        }
        if not args.execute:
            _print_report(report)
            return 0
        _run(command, capture=False)
        report["dispatch_submitted"] = True
        report["result_claimed"] = False
        _print_report(report)
        return 0

    if args.command == "features":
        source_preflight = _source_artifact_preflight()
        listing = _gh_json(feature_runs_endpoint())
        validate_no_existing_manual_runs(
            listing,
            workflow_name=FEATURE_WORKFLOW_NAME,
        )
        command = feature_dispatch_command()
        report: dict[str, object] = {
            **checkout,
            "source_preflight_ready": source_preflight["source_ready"],
            "source_mode": source_preflight["source_mode"],
            "source_earliest_expires_at": source_preflight.get("earliest_expires_at"),
            "stage": "features",
            "existing_manual_main_runs": 0,
            "ready_to_dispatch": True,
            "execute_requested": bool(args.execute),
            "dispatch_command": shell_join(command),
            "model_fit_authorized": False,
            "promotion_authorized": False,
            "trading_authorized": False,
        }
        if not args.execute:
            _print_report(report)
            return 0
        _run(command, capture=False)
        report["dispatch_submitted"] = True
        report["result_claimed"] = False
        _print_report(report)
        return 0

    feature_run_id = args.feature_run_id
    run = _gh_json(feature_run_endpoint(feature_run_id))
    feature = validate_feature_run_for_outcomes(
        run,
        expected_run_id=feature_run_id,
    )
    feature_evidence_summary, feature_evidence = _download_feature_evidence(
        feature_run_id=feature_run_id,
        feature_head_sha=str(feature["feature_head_sha"]),
    )

    if args.command == "readiness":
        outcome_run_id = args.outcome_run_id
        outcome_run = _gh_json(outcome_run_endpoint(outcome_run_id))
        outcome = validate_outcome_run_for_readiness(
            outcome_run,
            expected_run_id=outcome_run_id,
        )
        selected, outcome_evidence, readiness = _download_outcome_readiness_bundle(
            outcome_run_id=outcome_run_id,
            outcome_head_sha=str(outcome["outcome_head_sha"]),
            feature_head_sha=str(feature["feature_head_sha"]),
        )
        status = build_execution_status(
            feature_run=run,
            feature_evidence=feature_evidence,
            outcome_run=outcome_run,
            outcome_evidence=outcome_evidence,
            readiness=readiness,
        )
        if status.get("stage") != "MODEL_PROTOCOL_SOURCE_OPEN":
            raise SystemExit(
                f"EXP-044 evidence chain is not protocol-source-open: {status.get('stage')}"
            )
        _print_report(
            {
                **checkout,
                **feature,
                **feature_evidence_summary,
                **outcome,
                **selected,
                "stage": status["stage"],
                "next_action": status["next_action"],
                "readiness_verified": status["readiness_verified"],
                "model_protocol_source_open_authorized": status[
                    "model_protocol_source_open_authorized"
                ],
                "model_protocol_result_authorized": False,
                "model_fit_authorized": False,
                "promotion_authorized": False,
                "trading_authorized": False,
            }
        )
        return 0

    source_preflight = _source_artifact_preflight()
    listing = _gh_json(outcome_runs_endpoint())
    validate_no_existing_manual_runs(
        listing,
        workflow_name=OUTCOME_WORKFLOW_NAME,
    )
    command = outcome_dispatch_command(feature_run_id)
    report = {
        **checkout,
        **feature,
        **feature_evidence_summary,
        "source_preflight_ready": source_preflight["source_ready"],
        "source_mode": source_preflight["source_mode"],
        "source_earliest_expires_at": source_preflight.get("earliest_expires_at"),
        "stage": "outcomes",
        "existing_manual_main_runs": 0,
        "ready_to_dispatch": True,
        "execute_requested": bool(args.execute),
        "dispatch_command": shell_join(command),
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "trading_authorized": False,
    }
    if not args.execute:
        _print_report(report)
        return 0
    _run(command, capture=False)
    report["dispatch_submitted"] = True
    report["result_claimed"] = False
    _print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
