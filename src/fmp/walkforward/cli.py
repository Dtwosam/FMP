from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Mapping, Sequence

from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION

from .artifacts import (
    PHASE6_CHECKPOINT_TAG,
    PHASE7_ARTIFACT_PROTOCOL,
    STRATEGY_VERSION,
    write_stage1_evidence,
    write_stage2_evidence,
)
from .contracts import (
    EXPERIMENT_ID,
    FROZEN_CANDIDATES,
    PHASE6_CHECKPOINT_SHA,
    SLIPPAGE_SCENARIOS,
    STAGE1_WINDOW,
    STAGE2_WINDOWS,
    USDJPY_PHASE2_ARTIFACT_ID,
    USDJPY_PHASE2_ZIP_SHA256,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)
from .data import load_phase7_bars
from .evaluation import REFIT_STATUS, evaluate_phase7_window
from .gates import stage1_gate, stage2_gate


CANDIDATES = tuple(FROZEN_CANDIDATES)
_STAGE1_FILES = ("manifest.json", "result.json", "stage1.json")
_STAGE1_CONTENT_FILES = ("result.json", "stage1.json")
_STAGE1_SCORED_RANGE = {
    "start_utc": "2024-01-01T00:00:00Z",
    "end_exclusive_utc": "2025-01-01T00:00:00Z",
}
_STAGE1_WARMUP_START = "2023-12-25T00:00:00Z"


def _require_candidate(candidate_id: str):
    try:
        return FROZEN_CANDIDATES[candidate_id]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"unsupported frozen Phase 7 candidate: {candidate_id!r}") from exc


def _require_code_commit(code_commit: str) -> str:
    if not isinstance(code_commit, str) or not code_commit.strip():
        raise ValueError("Phase 7 code_commit must be non-empty")
    return code_commit


def _load_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        raw = Path(path).read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _verify_common_identity(
    payload: Mapping[str, object],
    *,
    candidate_id: str,
    expected_code_commit: str | None,
    label: str,
) -> str:
    candidate = _require_candidate(candidate_id)
    if payload.get("protocol") != PHASE7_ARTIFACT_PROTOCOL:
        raise ValueError(f"{label} protocol identity mismatch")
    if payload.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError(f"{label} experiment identity mismatch")
    if payload.get("phase6_checkpoint_tag") != PHASE6_CHECKPOINT_TAG:
        raise ValueError(f"{label} Phase 6 checkpoint tag mismatch")
    if payload.get("phase6_checkpoint_sha") != PHASE6_CHECKPOINT_SHA:
        raise ValueError(f"{label} Phase 6 checkpoint SHA mismatch")
    if payload.get("phase2_artifact_id") != USDJPY_PHASE2_ARTIFACT_ID:
        raise ValueError(f"{label} Phase 2 artifact identity mismatch")
    if payload.get("phase2_zip_sha256") != USDJPY_PHASE2_ZIP_SHA256:
        raise ValueError(f"{label} Phase 2 ZIP identity mismatch")
    if payload.get("processed_manifest_sha256") != USDJPY_PROCESSED_MANIFEST_SHA256:
        raise ValueError(f"{label} processed manifest identity mismatch")
    if payload.get("canonical_schema_version") != CANONICAL_SCHEMA_VERSION:
        raise ValueError(f"{label} canonical schema identity mismatch")

    frozen = payload.get("candidate")
    if not isinstance(frozen, Mapping):
        raise ValueError(f"{label} candidate identity is missing")
    if frozen.get("candidate_id") != candidate_id:
        raise ValueError(f"{label} candidate ID mismatch")
    if frozen.get("strategy_version") != STRATEGY_VERSION:
        raise ValueError(f"{label} strategy version mismatch")
    if frozen.get("symbol") != candidate.symbol or frozen.get("timeframe") != candidate.timeframe:
        raise ValueError(f"{label} candidate symbol/timeframe mismatch")
    parameters = frozen.get("parameters")
    if not isinstance(parameters, Mapping) or dict(parameters) != dict(candidate.parameters):
        raise ValueError(f"{label} candidate parameter identity mismatch")

    code_commit = payload.get("code_commit")
    if not isinstance(code_commit, str) or not code_commit.strip():
        raise ValueError(f"{label} code commit identity is missing")
    if expected_code_commit is not None and code_commit != expected_code_commit:
        raise ValueError(f"{label} code commit identity mismatch")
    return code_commit


def _verify_manifest_artifacts(root: Path, manifest: Mapping[str, object]) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 2:
        raise ValueError("Stage 1 manifest must contain exactly two content artifacts")
    by_name: dict[str, Mapping[str, object]] = {}
    for record in artifacts:
        if not isinstance(record, Mapping):
            raise ValueError("Stage 1 manifest artifact record must be an object")
        name = record.get("path")
        if name not in _STAGE1_CONTENT_FILES or name in by_name:
            raise ValueError("Stage 1 manifest artifact path set is invalid")
        by_name[str(name)] = record
    if set(by_name) != set(_STAGE1_CONTENT_FILES):
        raise ValueError("Stage 1 manifest artifact coverage is incomplete")

    for name in _STAGE1_CONTENT_FILES:
        path = root / name
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ValueError(f"Stage 1 evidence artifact is missing: {name}") from exc
        record = by_name[name]
        size = record.get("size_bytes")
        digest = record.get("sha256")
        if isinstance(size, bool) or not isinstance(size, int) or size != len(raw):
            raise ValueError(f"Stage 1 evidence artifact size mismatch: {name}")
        if not isinstance(digest, str) or digest != _sha256_bytes(raw):
            raise ValueError(f"Stage 1 evidence artifact digest mismatch: {name}")


def _stage1_gate_from_payload(stage1: Mapping[str, object], *, candidate_id: str):
    raw_results = stage1.get("results_by_slippage")
    if not isinstance(raw_results, Mapping) or set(raw_results) != {"0.2", "0.5", "1.0"}:
        raise ValueError("Stage 1 evidence must contain all three frozen slippage results")
    rows: dict[float, SimpleNamespace] = {}
    for slippage in SLIPPAGE_SCENARIOS:
        raw = raw_results.get(f"{slippage:.1f}")
        if not isinstance(raw, Mapping):
            raise ValueError("Stage 1 evidence result row must be an object")
        if raw.get("candidate_id") != candidate_id or raw.get("window_name") != STAGE1_WINDOW.name:
            raise ValueError("Stage 1 evidence row candidate/window identity mismatch")
        if raw.get("slippage_pips") != slippage:
            raise ValueError("Stage 1 evidence row slippage identity mismatch")
        if raw.get("scored_range") != _STAGE1_SCORED_RANGE:
            raise ValueError("Stage 1 evidence row scored range is not exact 2024")
        warmup = raw.get("warmup_range")
        if not isinstance(warmup, Mapping):
            raise ValueError("Stage 1 evidence row warm-up accounting is missing")
        if warmup.get("end_exclusive_utc") != _STAGE1_SCORED_RANGE["start_utc"]:
            raise ValueError("Stage 1 evidence warm-up must end at the scored boundary")
        warmup_start = warmup.get("start_utc")
        if not isinstance(warmup_start, str) or warmup_start < _STAGE1_WARMUP_START:
            raise ValueError("Stage 1 evidence warm-up exceeds the frozen seven-day bound")
        if raw.get("refit_status") != REFIT_STATUS:
            raise ValueError("Stage 1 evidence refit status mismatch")
        opened = raw.get("opened_partition_keys")
        if not isinstance(opened, list) or not opened:
            raise ValueError("Stage 1 evidence opened partition accounting is missing")
        if any(not isinstance(key, str) or key.split(":", 1)[-1] >= "2025-01" for key in opened):
            raise ValueError("Stage 1 evidence opened partitions reach 2025+")
        rows[slippage] = SimpleNamespace(**dict(raw))
    return stage1_gate(rows)


def verify_stage1_evidence(
    evidence_dir: Path,
    *,
    candidate_id: str,
) -> dict[str, object]:
    _require_candidate(candidate_id)
    root = Path(evidence_dir)
    if not root.is_dir():
        raise ValueError("Stage 1 evidence directory is missing")
    if any(not (root / name).is_file() for name in _STAGE1_FILES):
        raise ValueError("Stage 1 evidence package is incomplete")

    manifest_path = root / "manifest.json"
    manifest_raw = manifest_path.read_bytes()
    manifest = _load_json_object(manifest_path, label="Stage 1 manifest")
    manifest_code = _verify_common_identity(
        manifest,
        candidate_id=candidate_id,
        expected_code_commit=None,
        label="Stage 1 manifest",
    )
    if manifest.get("stage") != "stage1" or manifest.get("status") != "STAGE1_PASS":
        raise ValueError("Stage 1 manifest does not authorize Stage 2")
    _verify_manifest_artifacts(root, manifest)

    stage1 = _load_json_object(root / "stage1.json", label="Stage 1 evidence")
    result = _load_json_object(root / "result.json", label="Stage 1 result")
    _verify_common_identity(
        stage1,
        candidate_id=candidate_id,
        expected_code_commit=manifest_code,
        label="Stage 1 evidence",
    )
    _verify_common_identity(
        result,
        candidate_id=candidate_id,
        expected_code_commit=manifest_code,
        label="Stage 1 result",
    )
    if stage1.get("stage") != "stage1" or stage1.get("status") != "STAGE1_PASS":
        raise ValueError("Stage 1 evidence status is not PASS")
    if stage1.get("scored_range") != _STAGE1_SCORED_RANGE:
        raise ValueError("Stage 1 evidence does not cover exact 2024")
    if result.get("stage") != "stage1" or result.get("status") != "STAGE1_PASS":
        raise ValueError("Stage 1 result status is not PASS")
    statuses = result.get("candidate_statuses")
    if statuses != {candidate_id: "PASS"} or result.get("stage2_authorized") is not True:
        raise ValueError("Stage 1 result does not authorize this candidate for Stage 2")

    recomputed = _stage1_gate_from_payload(stage1, candidate_id=candidate_id)
    recorded_gate = stage1.get("gate")
    if not isinstance(recorded_gate, Mapping):
        raise ValueError("Stage 1 evidence gate record is missing")
    if recorded_gate.get("passed") is not True:
        raise ValueError("Stage 1 evidence gate did not pass")
    if recorded_gate.get("criteria") != dict(recomputed.criteria) or not recomputed.passed:
        raise ValueError("Stage 1 evidence gate does not match recomputed criteria")
    if result.get("gate") != recorded_gate:
        raise ValueError("Stage 1 result/evidence gate identity mismatch")

    return {
        "experiment_id": EXPERIMENT_ID,
        "candidate_id": candidate_id,
        "status": "STAGE1_PASS",
        "code_commit": manifest_code,
        "phase6_checkpoint_sha": PHASE6_CHECKPOINT_SHA,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
        "manifest_sha256": _sha256_bytes(manifest_raw),
    }


def run_stage1(
    *,
    dataset_root: Path,
    processed_manifest_path: Path,
    candidate_id: str,
    out_dir: Path,
    code_commit: str,
):
    _require_candidate(candidate_id)
    _require_code_commit(code_commit)
    loaded = load_phase7_bars(
        dataset_root=Path(dataset_root),
        manifest_path=Path(processed_manifest_path),
        candidate_id=candidate_id,
        window_name=STAGE1_WINDOW.name,
    )
    results = {
        slippage: evaluate_phase7_window(
            loaded=loaded,
            candidate_id=candidate_id,
            window_name=STAGE1_WINDOW.name,
            code_commit=code_commit,
            slippage_pips=slippage,
        )
        for slippage in SLIPPAGE_SCENARIOS
    }
    gate = stage1_gate(results)
    return write_stage1_evidence(
        out_dir=Path(out_dir),
        candidate_id=candidate_id,
        code_commit=code_commit,
        results_by_slippage=results,
        gate=gate,
    )


def run_stage2(
    *,
    dataset_root: Path,
    processed_manifest_path: Path,
    candidate_id: str,
    stage1_evidence_dir: Path,
    out_dir: Path,
    code_commit: str,
):
    _require_candidate(candidate_id)
    _require_code_commit(code_commit)
    stage1_identity = verify_stage1_evidence(
        Path(stage1_evidence_dir), candidate_id=candidate_id
    )

    results: dict[float, list[object]] = {slippage: [] for slippage in SLIPPAGE_SCENARIOS}
    for window in STAGE2_WINDOWS:
        loaded = load_phase7_bars(
            dataset_root=Path(dataset_root),
            manifest_path=Path(processed_manifest_path),
            candidate_id=candidate_id,
            window_name=window.name,
        )
        for slippage in SLIPPAGE_SCENARIOS:
            results[slippage].append(
                evaluate_phase7_window(
                    loaded=loaded,
                    candidate_id=candidate_id,
                    window_name=window.name,
                    code_commit=code_commit,
                    slippage_pips=slippage,
                )
            )
    frozen_results = {key: tuple(value) for key, value in results.items()}
    gate = stage2_gate(frozen_results)
    return write_stage2_evidence(
        out_dir=Path(out_dir),
        candidate_id=candidate_id,
        code_commit=code_commit,
        results_by_slippage=frozen_results,
        gate=gate,
        stage1_identity=stage1_identity,
    )


def _common_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--processed-manifest", required=True, type=Path)
    parser.add_argument("--candidate", required=True, choices=CANDIDATES)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--code-commit", required=True)
    return parser


def build_stage1_parser() -> argparse.ArgumentParser:
    return _common_parser("Run the frozen Phase 7 2024 final-test promotion gate.")


def build_stage2_parser() -> argparse.ArgumentParser:
    parser = _common_parser("Run the frozen Phase 7 walk-forward evaluation.")
    parser.add_argument("--stage1-evidence", required=True, type=Path)
    return parser


def stage1_main(argv: Sequence[str] | None = None) -> int:
    args = build_stage1_parser().parse_args(argv)
    run_stage1(
        dataset_root=args.dataset_root,
        processed_manifest_path=args.processed_manifest,
        candidate_id=args.candidate,
        out_dir=args.out,
        code_commit=args.code_commit,
    )
    print(json.dumps({"manifest": str(args.out / "manifest.json")}, sort_keys=True))
    return 0


def stage2_main(argv: Sequence[str] | None = None) -> int:
    args = build_stage2_parser().parse_args(argv)
    run_stage2(
        dataset_root=args.dataset_root,
        processed_manifest_path=args.processed_manifest,
        candidate_id=args.candidate,
        stage1_evidence_dir=args.stage1_evidence,
        out_dir=args.out,
        code_commit=args.code_commit,
    )
    print(json.dumps({"manifest": str(args.out / "manifest.json")}, sort_keys=True))
    return 0
