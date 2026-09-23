from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence

from fmp.market_learning.evidence import load_feature_evidence_index
from fmp.market_learning.execution_status import build_execution_status
from fmp.market_learning.operator import (
    FEATURE_WORKFLOW_NAME,
    OUTCOME_WORKFLOW_NAME,
    PRESERVATION_WORKFLOW_NAME,
    REPOSITORY,
    artifact_download_endpoint,
    feature_dispatch_command,
    feature_run_artifacts_endpoint,
    feature_run_endpoint,
    feature_runs_endpoint,
    outcome_dispatch_command,
    outcome_run_artifacts_endpoint,
    outcome_run_endpoint,
    outcome_runs_endpoint,
    release_asset_download_endpoint,
    preservation_dispatch_command,
    preservation_runs_endpoint,
    select_feature_evidence_artifact,
    select_outcome_evidence_artifacts,
    shell_join,
    validate_feature_evidence_for_outcomes,
    validate_feature_run_for_outcomes,
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
)


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
        _run(("gh", "auth", "status"), capture=False)
    except subprocess.CalledProcessError as exc:
        raise SystemExit("GitHub CLI authentication is required before EXP-044 dispatch") from exc


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Safely prepare or perform the manual EXP-044 GitHub workflow dispatch"
    )
    sub = out.add_subparsers(dest="command", required=True)

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


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    _require_gh_auth()
    checkout = _checkout_preflight()

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
