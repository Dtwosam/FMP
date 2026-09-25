from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Mapping, Sequence

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_repair_execution_gate import (
    build_fit_temporal_residual_lower_tail_utility_repair_model_workflow_source_gate,
)
from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_repair_operator import (
    build_fit_temporal_residual_lower_tail_utility_repair_operator_report,
    dispatch_command_for_fit_temporal_residual_lower_tail_utility_repair_report,
    fit_temporal_residual_lower_tail_utility_repair_artifact_download_endpoint,
    fit_temporal_residual_lower_tail_utility_repair_model_run_artifacts_endpoint,
    fit_temporal_residual_lower_tail_utility_repair_model_run_endpoint,
    fit_temporal_residual_lower_tail_utility_repair_model_run_jobs_endpoint,
    fit_temporal_residual_lower_tail_utility_repair_model_runs_endpoint,
    fit_temporal_residual_lower_tail_utility_repair_operator_gate_metadata,
    select_fit_temporal_residual_lower_tail_utility_repair_aggregate_artifact,
    select_fit_temporal_residual_lower_tail_utility_repair_manual_main_run,
    validate_fit_temporal_residual_lower_tail_utility_repair_operator_checkout,
)
from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_repair_result_review import (
    validate_fit_temporal_residual_lower_tail_utility_repair_model_terminal_review,
)


ROOT = Path(__file__).resolve().parents[1]
OPERATOR_DECISION = "DEC-226"


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
        raise SystemExit(
            f"GitHub API returned invalid JSON for {endpoint}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            f"GitHub API returned a non-object for {endpoint}"
        )
    return value


def _require_gh_auth() -> None:
    try:
        _run(("gh", "auth", "status"))
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "GitHub CLI authentication is required before "
            "EXP-057 operator use"
        ) from exc


def _checkout_preflight() -> dict[str, object]:
    _run(("git", "fetch", "--quiet", "origin", "main"), capture=False)
    return validate_fit_temporal_residual_lower_tail_utility_repair_operator_checkout(
        branch=_run(("git", "branch", "--show-current")),
        head_sha=_run(("git", "rev-parse", "HEAD")),
        origin_main_sha=_run(("git", "rev-parse", "origin/main")),
        porcelain_status=_run(("git", "status", "--porcelain")),
        origin_url=_run(("git", "remote", "get-url", "origin")),
    )


def _safe_extract_zip(archive_path: Path, destination: Path) -> None:
    root = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise SystemExit(
                    "EXP-057 aggregate ZIP contains an unsafe path"
                ) from exc
        archive.extractall(destination)


def _download_aggregate_evidence(
    *,
    artifact_id: int,
    head_sha: str,
) -> Mapping[str, object]:
    with tempfile.TemporaryDirectory(
        prefix="fmp-exp057-model-result-"
    ) as tmp:
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
                    fit_temporal_residual_lower_tail_utility_repair_artifact_download_endpoint(
                        artifact_id
                    ),
                ],
                check=True,
                stdout=handle,
            )

        _safe_extract_zip(archive_path, extracted)
        matches = sorted(extracted.rglob("model-result-evidence.json"))
        if len(matches) != 1:
            raise SystemExit(
                "EXP-057 aggregate artifact must contain exactly "
                "one model-result-evidence.json"
            )
        try:
            raw = json.loads(matches[0].read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(
                "EXP-057 aggregate evidence is not valid JSON"
            ) from exc
        if not isinstance(raw, dict):
            raise SystemExit(
                "EXP-057 aggregate evidence must be a JSON object"
            )
        if raw.get("code_commit") != head_sha:
            raise SystemExit(
                "EXP-057 aggregate evidence code commit mismatch"
            )
        return raw


def _validated_source_gate() -> dict[str, object]:
    gate = build_fit_temporal_residual_lower_tail_utility_repair_model_workflow_source_gate(
        repository_root=ROOT,
    )
    if gate.get("stage") != (
        "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RUN_DISPATCH_REQUIRED"
    ):
        raise SystemExit(
            "EXP-057 DEC-225 source gate returned an invalid stage"
        )
    for field in (
        "fit_temporal_residual_lower_tail_utility_repair_model_run_dispatch_authorized",
        "authoritative_fit_temporal_residual_lower_tail_utility_repair_model_result_execution_authorized",
        "model_protocol_result_authorized",
        "model_fit_authorized",
    ):
        if gate.get(field) is not True:
            raise SystemExit(
                f"EXP-057 DEC-225 source gate {field} must be true"
            )
    for field in ("promotion_authorized", "trading_authorized"):
        if gate.get(field) is not False:
            raise SystemExit(
                f"EXP-057 DEC-225 source gate {field} must be false"
            )
    return gate


def _next_report() -> dict[str, object]:
    checkout = _checkout_preflight()
    gate = _validated_source_gate()
    listing = _gh_json(
        fit_temporal_residual_lower_tail_utility_repair_model_runs_endpoint()
    )
    run = select_fit_temporal_residual_lower_tail_utility_repair_manual_main_run(listing)

    report = build_fit_temporal_residual_lower_tail_utility_repair_operator_report(
        checkout=checkout,
        run=run,
    )
    report.update(
        {
            "operator_decision": OPERATOR_DECISION,
            **fit_temporal_residual_lower_tail_utility_repair_operator_gate_metadata(gate),
        }
    )

    if report["stage"] != (
        "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_TERMINAL_REVIEW_REQUIRED"
    ):
        return report

    run_id = int(report["run_id"])
    exact_run = _gh_json(
        fit_temporal_residual_lower_tail_utility_repair_model_run_endpoint(run_id)
    )
    jobs = _gh_json(
        fit_temporal_residual_lower_tail_utility_repair_model_run_jobs_endpoint(run_id)
    )
    artifacts = _gh_json(
        fit_temporal_residual_lower_tail_utility_repair_model_run_artifacts_endpoint(run_id)
    )

    aggregate_evidence: Mapping[str, object] | None = None
    if exact_run.get("conclusion") == "success":
        head_sha = exact_run.get("head_sha")
        if not isinstance(head_sha, str):
            raise SystemExit(
                "successful EXP-057 run is missing head SHA"
            )
        selected = select_fit_temporal_residual_lower_tail_utility_repair_aggregate_artifact(
            artifacts,
            head_sha=head_sha,
        )
        aggregate_evidence = _download_aggregate_evidence(
            artifact_id=int(selected["artifact_id"]),
            head_sha=head_sha,
        )
        report.update(selected)

    review = validate_fit_temporal_residual_lower_tail_utility_repair_model_terminal_review(
        run=exact_run,
        jobs_payload=jobs,
        artifacts_payload=artifacts,
        aggregate_evidence=aggregate_evidence,
    )
    report.update(review)
    report["read_only"] = True
    report["next_action"] = (
        "Review the frozen DEC-224 terminal evidence. "
        "Do not rerun automatically or promote/trade."
    )
    return report


def _print_report(report: Mapping[str, object]) -> None:
    print(
        json.dumps(
            dict(report),
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
    )


def _read_next_via_public_cli() -> dict[str, object]:
    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "next",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            "DEC-226 next planner did not return valid JSON"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "DEC-226 next planner must return a JSON object"
        )
    return value


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description=(
            "Fail-closed single-step EXP-057 historical model-run operator"
        )
    )
    sub = out.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "next",
        help=(
            "inspect live EXP-057 workflow state and return "
            "the one next authoritative action"
        ),
    )
    advance = sub.add_parser(
        "advance",
        help=(
            "prepare or execute exactly one DEC-225-authorized dispatch"
        ),
    )
    advance.add_argument("--execute", action="store_true")
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    _require_gh_auth()

    if args.command == "next":
        _print_report(_next_report())
        return 0

    if args.command != "advance":
        raise SystemExit(
            f"unsupported EXP-057 operator command: {args.command}"
        )

    plan = _read_next_via_public_cli()
    command = dispatch_command_for_fit_temporal_residual_lower_tail_utility_repair_report(
        plan
    )
    report = {
        **plan,
        "advance_execute_requested": bool(args.execute),
        "advance_dispatchable": command is not None,
        "dispatch_submitted": False,
    }

    if not args.execute or command is None:
        _print_report(report)
        return 0

    confirmed = _read_next_via_public_cli()
    if confirmed != plan:
        raise SystemExit(
            "EXP-057 live state changed between planning and execution; "
            "rerun advance"
        )

    confirmed_command = (
        dispatch_command_for_fit_temporal_residual_lower_tail_utility_repair_report(
            confirmed
        )
    )
    if confirmed_command != command:
        raise SystemExit(
            "EXP-057 dispatch plan changed before execution"
        )

    _run(command, capture=False)
    report["read_only"] = False
    report["dispatch_submitted"] = True
    report["result_claimed"] = False
    _print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
