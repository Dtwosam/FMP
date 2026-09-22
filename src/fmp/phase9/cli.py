from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

from .arming import (
    build_phase9_demo_execution_arm,
    write_phase9_demo_execution_arm,
)
from .design import (
    build_phase9_demo_design_from_campaign,
    write_phase9_demo_design,
)


def _current_code_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        raise RuntimeError("unable to resolve current code commit") from None
    commit = completed.stdout.strip()
    if (
        len(commit) != 40
        or any(character not in "0123456789abcdef" for character in commit)
    ):
        raise RuntimeError("current code commit is invalid")
    return commit



def _load_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP Phase 9 source-only demo design tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    design = subparsers.add_parser(
        "design-demo",
        help="freeze a Phase 9 demo design from an exact Phase 8B PASS review",
    )
    design.add_argument("--campaign-dir", required=True, type=Path)
    design.add_argument("--review-id", required=True)

    materialize = subparsers.add_parser(
        "materialize-arm",
        help="materialize one local-only DEC-060 demo execution-arm package",
    )
    materialize.add_argument("--design", required=True, type=Path)
    materialize.add_argument("--request", required=True, type=Path)
    materialize.add_argument("--session-arm", required=True, type=Path)
    materialize.add_argument("--session-ready", required=True, type=Path)
    materialize.add_argument("--out-dir", required=True, type=Path)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    code_commit_resolver: Callable[[], str] = _current_code_commit,
) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "design-demo":
        result = build_phase9_demo_design_from_campaign(
            campaign_dir=args.campaign_dir,
            review_id=args.review_id,
            code_commit=code_commit_resolver(),
        )
        out_dir = (
            args.campaign_dir
            / "phase9"
            / "designs"
            / str(args.review_id)
        )
        manifest = write_phase9_demo_design(result, out_dir)
        print(
            json.dumps(
                {
                    "design": str(out_dir / "design.json"),
                    "manifest": str(out_dir / "manifest.json"),
                    "demo_design_fingerprint": result[
                        "demo_design_fingerprint"
                    ],
                    "demo_adapter_source_authorized": True,
                    "demo_execution_authorized": False,
                    "demo_order_authorized": False,
                    "phase10_authorized": False,
                    "artifact_count": len(manifest["artifacts"]),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "materialize-arm":
        design = _load_json_object(
            args.design,
            label="Phase 9 demo design",
        )
        request = _load_json_object(
            args.request,
            label="Phase 9 demo order request",
        )
        session_arm = _load_json_object(
            args.session_arm,
            label="Phase 9 demo session arm",
        )
        session_ready = _load_json_object(
            args.session_ready,
            label="Phase 9 demo session readiness",
        )
        result = build_phase9_demo_execution_arm(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            code_commit=code_commit_resolver(),
        )
        manifest = write_phase9_demo_execution_arm(
            result,
            out_dir=args.out_dir,
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
        )
        print(
            json.dumps(
                {
                    "execution_arm": str(args.out_dir / "execution-arm.json"),
                    "manifest": str(args.out_dir / "manifest.json"),
                    "execution_arm_fingerprint": result[
                        "execution_arm_fingerprint"
                    ],
                    "demo_execution_arm_artifact_ready": True,
                    "demo_execution_source_armed": False,
                    "demo_execution_authorized": False,
                    "demo_order_authorized": False,
                    "broker_mutation_authorized": False,
                    "phase10_authorized": False,
                    "artifact_count": len(manifest["artifacts"]),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    raise AssertionError("unreachable Phase 9 command")


__all__ = ["build_parser", "main"]
