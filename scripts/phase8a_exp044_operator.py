from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

from fmp.market_learning.evidence import load_feature_evidence_index
from fmp.market_learning.operator import (
    FEATURE_WORKFLOW_NAME,
    OUTCOME_WORKFLOW_NAME,
    REPOSITORY,
    artifact_download_endpoint,
    feature_dispatch_command,
    feature_run_artifacts_endpoint,
    feature_run_endpoint,
    feature_runs_endpoint,
    outcome_dispatch_command,
    outcome_runs_endpoint,
    select_feature_evidence_artifact,
    shell_join,
    validate_feature_evidence_for_outcomes,
    validate_feature_run_for_outcomes,
    validate_no_existing_manual_runs,
    validate_operator_checkout,
)
from fmp.market_learning.source_preflight import (
    SOURCE_ARTIFACTS,
    compile_source_preflight,
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


def _source_artifact_preflight() -> dict[str, object]:
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


def _download_feature_evidence(
    *,
    feature_run_id: int,
    feature_head_sha: str,
) -> dict[str, object]:
    artifacts = _gh_json(feature_run_artifacts_endpoint(feature_run_id))
    selected = select_feature_evidence_artifact(
        artifacts,
        feature_head_sha=feature_head_sha,
    )
    artifact_id = int(selected["artifact_id"])

    with tempfile.TemporaryDirectory(prefix="fmp-exp044-feature-evidence-") as tmp:
        root = Path(tmp)
        archive_path = root / "feature-evidence.zip"
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
        matches = sorted(extracted.rglob("feature-evidence.json"))
        if len(matches) != 1:
            raise SystemExit(
                "aggregate feature evidence ZIP must contain exactly one feature-evidence.json"
            )
        evidence = load_feature_evidence_index(matches[0])
        verified = validate_feature_evidence_for_outcomes(
            evidence,
            expected_code_commit=feature_head_sha,
        )
    return {
        **selected,
        **verified,
    }


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

    features = sub.add_parser("features", help="prepare or dispatch EXP-044 feature generation")
    features.add_argument("--execute", action="store_true")

    outcomes = sub.add_parser("outcomes", help="prepare or dispatch EXP-044 outcome materialization")
    outcomes.add_argument("--feature-run-id", type=int, required=True)
    outcomes.add_argument("--execute", action="store_true")
    return out


def _print_report(report: dict[str, object]) -> None:
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    _require_gh_auth()
    checkout = _checkout_preflight()
    source_preflight = _source_artifact_preflight()

    if args.command == "features":
        listing = _gh_json(feature_runs_endpoint())
        validate_no_existing_manual_runs(
            listing,
            workflow_name=FEATURE_WORKFLOW_NAME,
        )
        command = feature_dispatch_command()
        report: dict[str, object] = {
            **checkout,
            "source_preflight_ready": source_preflight["source_ready"],
            "source_earliest_expires_at": source_preflight["earliest_expires_at"],
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
    feature_evidence = _download_feature_evidence(
        feature_run_id=feature_run_id,
        feature_head_sha=str(feature["feature_head_sha"]),
    )
    listing = _gh_json(outcome_runs_endpoint())
    validate_no_existing_manual_runs(
        listing,
        workflow_name=OUTCOME_WORKFLOW_NAME,
    )
    command = outcome_dispatch_command(feature_run_id)
    report = {
        **checkout,
        **feature,
        **feature_evidence,
        "source_preflight_ready": source_preflight["source_ready"],
        "source_earliest_expires_at": source_preflight["earliest_expires_at"],
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
