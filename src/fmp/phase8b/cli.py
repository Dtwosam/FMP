from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path

from .bridge import (
    Phase8BBridgeFileTail,
    discover_phase8b_bridge_files,
)
from .campaign_start import (
    build_phase8b_campaign_start_authorization,
    write_phase8b_campaign_start_authorization,
)
from .design import (
    build_phase8b_design,
    validate_phase8b_design,
    write_phase8b_design_artifacts,
)
from .qualification import (
    Phase8BQualificationOutcome,
    qualify_phase8b_design,
    write_phase8b_qualification_artifacts,
)
from .registration import (
    build_phase8b_registration,
    write_phase8b_registration,
)


def _load_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP Phase 8B read-only shadow preparation tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    design = subparsers.add_parser(
        "design",
        help="compile an accepted Phase 8A candidate into a frozen Phase 8B design",
    )
    design.add_argument("--acceptance", required=True, type=Path)
    design.add_argument("--code-commit", required=True)
    design.add_argument("--out", required=True, type=Path)

    qualify = subparsers.add_parser(
        "qualify",
        help="qualify every fixed required-symbol MT5 demo feed in a Phase 8B design",
    )
    qualify.add_argument("--design", required=True, type=Path)
    qualify.add_argument("--out", required=True, type=Path)

    register = subparsers.add_parser(
        "register",
        help="register an immutable Phase 8B campaign boundary after qualification PASS",
    )
    register.add_argument("--design", required=True, type=Path)
    register.add_argument("--qualification", required=True, type=Path)
    register.add_argument("--campaign-dir", required=True, type=Path)

    authorize_start = subparsers.add_parser(
        "authorize-start",
        help="freeze the exact prospective Phase 8B campaign start boundary",
    )
    authorize_start.add_argument(
        "--campaign-dir",
        required=True,
        type=Path,
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    code_commit_resolver: Callable[[], str] = _current_code_commit,
    utc_now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    monotonic_ns: Callable[[], int] = time.monotonic_ns,
    sleep: Callable[[float], None] = time.sleep,
    bridge_discoverer: Callable[
        [Sequence[str]],
        Mapping[str, Path],
    ] = discover_phase8b_bridge_files,
    tail_factory: Callable[
        [Path, str],
        Phase8BBridgeFileTail,
    ] = lambda path, symbol: Phase8BBridgeFileTail(
        path,
        expected_symbol=symbol,
    ),
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "design":
        acceptance = _load_json_object(
            args.acceptance,
            label="Phase 8A acceptance artifact",
        )
        acceptance_sha = hashlib.sha256(
            args.acceptance.read_bytes()
        ).hexdigest()
        result = build_phase8b_design(
            acceptance=acceptance,
            acceptance_sha256=acceptance_sha,
            code_commit=args.code_commit,
        )
        write_phase8b_design_artifacts(result, args.out)
        print(
            json.dumps(
                {
                    "design": str(args.out / "design.json"),
                    "manifest": str(args.out / "manifest.json"),
                    "design_fingerprint": result["design_fingerprint"],
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "qualify":
        design = _load_json_object(
            args.design,
            label="Phase 8B design artifact",
        )
        validate_phase8b_design(design)
        design_sha = hashlib.sha256(
            args.design.read_bytes()
        ).hexdigest()
        raw_symbols = design.get("required_symbols")
        if not isinstance(raw_symbols, list):
            raise ValueError("Phase 8B design required_symbols is malformed")
        symbols = tuple(str(item) for item in raw_symbols)
        paths = dict(bridge_discoverer(symbols))
        if set(paths) != set(symbols):
            raise ValueError("Phase 8B bridge discovery coverage mismatch")
        tails = {
            symbol: tail_factory(Path(paths[symbol]), symbol)
            for symbol in symbols
        }
        result = qualify_phase8b_design(
            design=design,
            design_sha256=design_sha,
            code_commit=code_commit_resolver(),
            tails=tails,
            utc_now=utc_now,
            monotonic_ns=monotonic_ns,
            sleep=sleep,
        )
        write_phase8b_qualification_artifacts(result, args.out)
        print(
            json.dumps(
                {
                    "qualification": str(
                        args.out / "qualification.json"
                    ),
                    "manifest": str(args.out / "manifest.json"),
                    "outcome": result["outcome"],
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return {
            Phase8BQualificationOutcome.QUALIFIED.value: 0,
            Phase8BQualificationOutcome.INCONCLUSIVE.value: 2,
            Phase8BQualificationOutcome.CONNECTOR_UNAVAILABLE.value: 3,
            Phase8BQualificationOutcome.CONNECTOR_REJECTED.value: 4,
        }[str(result["outcome"])]

    if args.command == "register":
        design = _load_json_object(
            args.design,
            label="Phase 8B design artifact",
        )
        qualification = _load_json_object(
            args.qualification,
            label="Phase 8B qualification artifact",
        )
        registration = build_phase8b_registration(
            design=design,
            design_sha256=hashlib.sha256(
                args.design.read_bytes()
            ).hexdigest(),
            qualification=qualification,
            qualification_sha256=hashlib.sha256(
                args.qualification.read_bytes()
            ).hexdigest(),
            code_commit=code_commit_resolver(),
            registered_at_utc=utc_now(),
        )
        manifest = write_phase8b_registration(
            registration,
            args.campaign_dir,
        )
        print(
            json.dumps(
                {
                    "registration": str(
                        args.campaign_dir / "registration.json"
                    ),
                    "manifest": str(
                        args.campaign_dir / "registration-manifest.json"
                    ),
                    "registration_fingerprint": registration[
                        "registration_fingerprint"
                    ],
                    "campaign_start_authorized": False,
                    "artifact_count": len(manifest["artifacts"]),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "authorize-start":
        registration_path = args.campaign_dir / "registration.json"
        registration = _load_json_object(
            registration_path,
            label="Phase 8B campaign registration",
        )
        raw_symbols = registration.get("required_symbols")
        if not isinstance(raw_symbols, list) or not raw_symbols:
            raise ValueError(
                "Phase 8B registration required_symbols is malformed"
            )
        symbols = tuple(str(item) for item in raw_symbols)
        paths = dict(bridge_discoverer(symbols))
        if set(paths) != set(symbols):
            raise ValueError(
                "Phase 8B bridge discovery coverage mismatch"
            )
        tails = {
            symbol: tail_factory(Path(paths[symbol]), symbol)
            for symbol in symbols
        }
        authorization = build_phase8b_campaign_start_authorization(
            registration=registration,
            registration_sha256=hashlib.sha256(
                registration_path.read_bytes()
            ).hexdigest(),
            bridge_tails=tails,
            code_commit=code_commit_resolver(),
            started_at_utc=utc_now(),
        )
        manifest = write_phase8b_campaign_start_authorization(
            authorization,
            args.campaign_dir,
        )
        print(
            json.dumps(
                {
                    "start_authorization": str(
                        args.campaign_dir / "start-authorization.json"
                    ),
                    "manifest": str(
                        args.campaign_dir
                        / "start-authorization-manifest.json"
                    ),
                    "start_authorization_fingerprint": authorization[
                        "start_authorization_fingerprint"
                    ],
                    "campaign_start_authorized": True,
                    "prospective_capture_authorized": True,
                    "artifact_count": len(manifest["artifacts"]),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    raise AssertionError("unreachable Phase 8B command")


__all__ = ["build_parser", "main"]
