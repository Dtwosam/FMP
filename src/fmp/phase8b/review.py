from __future__ import annotations

import hashlib
import json
import math
import os
import re
import statistics
from pathlib import Path
from typing import Callable, Mapping

from fmp.phase8b.acceptance import (
    PHASE8B_ACCEPTANCE_CONTRACT_DECISION,
    PHASE8B_NEED_MORE_DATA,
    PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
    PHASE8B_REJECT_FINANCIAL_MISMATCH,
    PHASE8B_REJECT_MARKET_MISMATCH,
    PHASE8B_REJECT_OPERATIONAL_MISMATCH,
    PHASE8B_REJECT_SAFETY_FAILURE,
    PHASE8B_SPREAD_REFERENCE_PROTOCOL,
    compile_phase8b_acceptance,
    validate_phase8b_acceptance,
    validate_phase8b_campaign_evidence,
    validate_phase8b_spread_reference,
    write_phase8b_acceptance_artifacts,
)
from fmp.phase8b.campaign_close import (
    PHASE8B_CAMPAIGN_CLOSE_MANIFEST_PROTOCOL,
    PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY,
)
from fmp.phase8b.capture import validate_phase8b_capture_preflight
from fmp.phase8b.runtime import reconstruct_phase8b_champion_set
from fmp.portfolio.contracts import (
    StrategyLifecycle,
    StrategyRecord,
)
from fmp.portfolio.registry import (
    freeze_shadow_champion_set,
    transition_strategy,
)
from fmp.portfolio.research_data import (
    PHASE8A_RETROSPECTIVE_END_EXCLUSIVE,
    PHASE8A_RETROSPECTIVE_LABEL,
    PHASE8A_RETROSPECTIVE_START,
    LoadedRetrospectiveBars,
    RetrospectiveRange,
    load_phase8a_retrospective_bars,
)


PHASE8B_REVIEW_EXPERIMENT_ID = "EXP-20260922-025"
PHASE8B_REVIEW_DECISION = "DEC-054"
PHASE8B_SPREAD_REFERENCE_ARTIFACT_PROTOCOL = (
    "fmp-phase8b-spread-reference-artifacts-v1"
)
PHASE8B_REVIEW_MANIFEST_PROTOCOL = "fmp-phase8b-review-artifacts-v1"
PHASE8B_SHADOW_VALIDATION_PROTOCOL = "fmp-phase8b-shadow-validation-v1"
PHASE8B_CAMPAIGN_TERMINAL_PROTOCOL = "fmp-phase8b-campaign-terminal-v1"
SHADOW_VALIDATION_EVIDENCE_ID = (
    "EXP-20260922-025:PHASE8B_SHADOW_VALIDATED"
)
SPREAD_METHOD = "CANONICAL_1M_OPEN_CLOSE_SPREAD_V1"
SPREAD_TIMEFRAME = "1m"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _load_json(path: Path, *, label: str) -> dict[str, object]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value


def _pip_size(symbol: str) -> float:
    if symbol == "USDJPY":
        return 0.01
    if symbol in {"EURUSD", "GBPUSD"}:
        return 0.0001
    raise ValueError(f"unsupported Phase 8B spread symbol: {symbol}")


def _nearest_rank(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("spread reference requires non-empty samples")
    ordered = sorted(values)
    rank = max(1, math.ceil(fraction * len(ordered)))
    return float(ordered[rank - 1])


def _spread_stats(values: list[float]) -> tuple[int, float, float]:
    if not values:
        raise ValueError("spread reference requires non-empty samples")
    if any(not math.isfinite(item) or item < 0 for item in values):
        raise ValueError("spread reference contains invalid spread")
    return (
        len(values),
        float(statistics.median(values)),
        _nearest_rank(values, 0.95),
    )


def build_phase8b_spread_reference(
    *,
    preflight: Mapping[str, object],
    dataset_root: Path,
    code_commit: str,
    bar_loader: Callable[..., LoadedRetrospectiveBars] = (
        load_phase8a_retrospective_bars
    ),
) -> dict[str, object]:
    validate_phase8b_capture_preflight(preflight)
    commit = _validate_commit(
        code_commit,
        field="Phase 8B spread-reference code commit",
    )
    raw_symbols = preflight.get("required_symbols")
    if not isinstance(raw_symbols, list) or not raw_symbols:
        raise ValueError("Phase 8B spread-reference required symbols are malformed")
    symbols = sorted(str(item) for item in raw_symbols)
    root = Path(dataset_root)
    research_range = RetrospectiveRange(
        start=PHASE8A_RETROSPECTIVE_START,
        end_exclusive=PHASE8A_RETROSPECTIVE_END_EXCLUSIVE,
    )
    per_symbol: dict[str, object] = {}
    manifest_sha: dict[str, str] = {}
    opened_months: dict[str, list[str]] = {}

    for symbol in symbols:
        manifest_path = (
            root
            / "manifests"
            / "processed"
            / "fmp-canonical-1m-v1"
            / f"{symbol}.json"
        )
        loaded = bar_loader(
            dataset_root=root,
            manifest_path=manifest_path,
            symbol=symbol,
            timeframe=SPREAD_TIMEFRAME,
            research_range=research_range,
        )
        if loaded.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
            raise ValueError("Phase 8B spread-reference source label drift")
        if loaded.start != PHASE8A_RETROSPECTIVE_START:
            raise ValueError("Phase 8B spread-reference start date drift")
        if loaded.end_exclusive != PHASE8A_RETROSPECTIVE_END_EXCLUSIVE:
            raise ValueError("Phase 8B spread-reference end date drift")
        if not loaded.bars:
            raise ValueError(
                f"Phase 8B spread-reference has no complete 1m bars for {symbol}"
            )
        entry = [
            (bar.ask_open - bar.bid_open) / _pip_size(symbol)
            for bar in loaded.bars
        ]
        exit_ = [
            (bar.ask_close - bar.bid_close) / _pip_size(symbol)
            for bar in loaded.bars
        ]
        entry_count, entry_median, entry_p95 = _spread_stats(entry)
        exit_count, exit_median, exit_p95 = _spread_stats(exit_)
        per_symbol[symbol] = {
            "entry_sample_count": entry_count,
            "exit_sample_count": exit_count,
            "entry_median_pips": entry_median,
            "entry_p95_pips": entry_p95,
            "exit_median_pips": exit_median,
            "exit_p95_pips": exit_p95,
        }
        manifest_sha[symbol] = loaded.processed_manifest_sha256
        opened_months[symbol] = list(loaded.opened_artifact_months)

    payload = {
        "protocol": PHASE8B_SPREAD_REFERENCE_PROTOCOL,
        "contract_decision": PHASE8B_ACCEPTANCE_CONTRACT_DECISION,
        "builder_decision": PHASE8B_REVIEW_DECISION,
        "spread_reference_code_commit": commit,
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "champion_set_fingerprint": preflight[
            "champion_set_fingerprint"
        ],
        "required_symbols": symbols,
        "slippage_scenarios": list(preflight["slippage_scenarios"]),
        "source_label": PHASE8A_RETROSPECTIVE_LABEL,
        "retrospective_start": PHASE8A_RETROSPECTIVE_START.isoformat(),
        "retrospective_end_exclusive": (
            PHASE8A_RETROSPECTIVE_END_EXCLUSIVE.isoformat()
        ),
        "timeframe": SPREAD_TIMEFRAME,
        "spread_method": SPREAD_METHOD,
        "processed_manifest_sha256_by_symbol": manifest_sha,
        "opened_artifact_months_by_symbol": opened_months,
        "per_symbol": per_symbol,
    }
    result = payload | {
        "spread_reference_fingerprint": _canonical_digest(payload)
    }
    validate_phase8b_spread_reference(result)
    return result


def write_phase8b_spread_reference(
    reference: Mapping[str, object],
    campaign_dir: Path,
) -> dict[str, object]:
    validate_phase8b_spread_reference(reference)
    root = Path(campaign_dir)
    result_path = root / "spread-reference.json"
    manifest_path = root / "spread-reference-manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 8B spread reference already exists")
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(reference))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE8B_SPREAD_REFERENCE_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE8B_REVIEW_EXPERIMENT_ID,
        "spread_reference_fingerprint": reference[
            "spread_reference_fingerprint"
        ],
        "artifacts": [
            {
                "path": result_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


def validate_phase8b_shadow_validation(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE8B_SHADOW_VALIDATION_PROTOCOL:
        raise ValueError("Phase 8B shadow-validation protocol mismatch")
    if value.get("experiment_id") != PHASE8B_REVIEW_EXPERIMENT_ID:
        raise ValueError("Phase 8B shadow-validation experiment mismatch")
    for field in (
        "review_id",
        "acceptance_fingerprint",
        "campaign_evidence_fingerprint",
        "spread_reference_fingerprint",
        "champion_set_fingerprint",
        "shadow_validation_fingerprint",
    ):
        _validate_sha256(
            value.get(field),
            field=f"Phase 8B shadow-validation {field}",
        )
    strategies = value.get("strategy_fingerprints")
    rows = value.get("strategies")
    if not isinstance(strategies, list) or not strategies:
        raise ValueError("Phase 8B shadow-validation strategies are malformed")
    if strategies != sorted(strategies):
        raise ValueError("Phase 8B shadow-validation strategies must be sorted")
    if not isinstance(rows, list) or len(rows) != len(strategies):
        raise ValueError("Phase 8B shadow-validation rows are malformed")
    if [row.get("fingerprint") for row in rows if isinstance(row, Mapping)] != strategies:
        raise ValueError("Phase 8B shadow-validation strategy identity mismatch")
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("Phase 8B shadow-validation strategy row is malformed")
        if row.get("prior_lifecycle") != "SHADOW_CANDIDATE":
            raise ValueError("Phase 8B shadow-validation prior lifecycle mismatch")
        if row.get("lifecycle") != "SHADOW_VALIDATED":
            raise ValueError("Phase 8B shadow-validation lifecycle mismatch")
    if value.get("demo_design_eligible") is not True:
        raise ValueError("Phase 8B shadow-validation must be demo-design eligible")
    for field in (
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_execution_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(
                f"Phase 8B shadow-validation requires {field}=false"
            )
    fingerprint = value["shadow_validation_fingerprint"]
    payload = dict(value)
    payload.pop("shadow_validation_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 8B shadow-validation fingerprint mismatch")


def build_phase8b_shadow_validation(
    *,
    preflight: Mapping[str, object],
    acceptance: Mapping[str, object],
    review_id: str,
) -> dict[str, object]:
    validate_phase8b_capture_preflight(preflight)
    validate_phase8b_acceptance(acceptance)
    review = _validate_sha256(review_id, field="Phase 8B review ID")
    if acceptance.get("outcome") != PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN:
        raise ValueError("Phase 8B shadow validation requires exact PASS")
    if acceptance.get("capture_preflight_fingerprint") != preflight.get(
        "capture_preflight_fingerprint"
    ):
        raise ValueError("Phase 8B shadow-validation preflight mismatch")
    if acceptance.get("champion_set_fingerprint") != preflight.get(
        "champion_set_fingerprint"
    ):
        raise ValueError("Phase 8B shadow-validation champion mismatch")

    champion = reconstruct_phase8b_champion_set(preflight)
    raw_rows = preflight.get("strategies")
    if not isinstance(raw_rows, list):
        raise ValueError("Phase 8B preflight strategy rows are malformed")
    rows_by_fp = {
        str(row.get("fingerprint")): row
        for row in raw_rows
        if isinstance(row, Mapping)
    }
    before: list[StrategyRecord] = []
    for strategy in champion.strategies:
        row = rows_by_fp.get(strategy.fingerprint)
        if row is None:
            raise ValueError("Phase 8B shadow-validation strategy row is missing")
        if row.get("lifecycle") != StrategyLifecycle.SHADOW_CANDIDATE.value:
            raise ValueError(
                "Phase 8B shadow-validation strategy must enter from SHADOW_CANDIDATE"
            )
        evidence_id = row.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id:
            raise ValueError("Phase 8B shadow-validation prior evidence ID is missing")
        before.append(
            StrategyRecord(
                strategy=strategy,
                lifecycle=StrategyLifecycle.SHADOW_CANDIDATE,
                evidence_id=evidence_id,
            )
        )

    after = [
        transition_strategy(
            item,
            StrategyLifecycle.SHADOW_VALIDATED,
            evidence_id=SHADOW_VALIDATION_EVIDENCE_ID,
        )
        for item in before
    ]
    refrozen = freeze_shadow_champion_set(
        after,
        champion_set_id=champion.champion_set_id,
    )
    if refrozen.fingerprint != champion.fingerprint:
        raise ValueError("Phase 8B shadow-validation champion identity changed")

    ordered = sorted(
        zip(before, after, strict=True),
        key=lambda pair: pair[0].strategy.fingerprint,
    )
    payload = {
        "protocol": PHASE8B_SHADOW_VALIDATION_PROTOCOL,
        "experiment_id": PHASE8B_REVIEW_EXPERIMENT_ID,
        "decision": PHASE8B_REVIEW_DECISION,
        "review_id": review,
        "acceptance_fingerprint": acceptance["acceptance_fingerprint"],
        "campaign_evidence_fingerprint": acceptance[
            "campaign_evidence_fingerprint"
        ],
        "spread_reference_fingerprint": acceptance[
            "spread_reference_fingerprint"
        ],
        "champion_set_id": champion.champion_set_id,
        "champion_set_fingerprint": champion.fingerprint,
        "strategy_fingerprints": [
            pair[0].strategy.fingerprint for pair in ordered
        ],
        "strategies": [
            {
                "fingerprint": prior.strategy.fingerprint,
                "identity_json": prior.strategy.identity_json,
                "prior_lifecycle": prior.lifecycle.value,
                "prior_evidence_id": prior.evidence_id,
                "lifecycle": current.lifecycle.value,
                "evidence_id": current.evidence_id,
            }
            for prior, current in ordered
        ],
        "demo_design_eligible": True,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    result = payload | {
        "shadow_validation_fingerprint": _canonical_digest(payload)
    }
    validate_phase8b_shadow_validation(result)
    return result


def _closure_campaign_evidence(
    *,
    campaign_dir: Path,
    closure_id: str,
) -> dict[str, object]:
    closure = _validate_sha256(closure_id, field="Phase 8B closure ID")
    root = Path(campaign_dir) / "closures" / closure
    manifest = _load_json(
        root / "manifest.json",
        label="Phase 8B closure manifest",
    )
    if manifest.get("protocol") != PHASE8B_CAMPAIGN_CLOSE_MANIFEST_PROTOCOL:
        raise ValueError("Phase 8B closure manifest protocol mismatch")
    if manifest.get("closure_id") != closure:
        raise ValueError("Phase 8B closure manifest identity mismatch")
    if manifest.get("outcome") != PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY:
        raise ValueError("Phase 8B closure outcome mismatch")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("Phase 8B closure manifest artifacts are malformed")
    expected_sha = None
    for row in artifacts:
        if isinstance(row, Mapping) and row.get("path") == "campaign-evidence.json":
            expected_sha = row.get("sha256")
            break
    expected = _validate_sha256(
        expected_sha,
        field="Phase 8B campaign-evidence artifact digest",
    )
    evidence_path = root / "campaign-evidence.json"
    raw = evidence_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("Phase 8B campaign-evidence byte digest mismatch")
    evidence = json.loads(raw)
    if not isinstance(evidence, dict):
        raise ValueError("Phase 8B campaign evidence root must be an object")
    validate_phase8b_campaign_evidence(evidence)
    if manifest.get("campaign_evidence_fingerprint") != evidence.get(
        "campaign_evidence_fingerprint"
    ):
        raise ValueError("Phase 8B closure campaign-evidence identity mismatch")
    return evidence


def _terminal_marker(
    *,
    review_id: str,
    acceptance: Mapping[str, object],
) -> dict[str, object]:
    payload = {
        "protocol": PHASE8B_CAMPAIGN_TERMINAL_PROTOCOL,
        "experiment_id": PHASE8B_REVIEW_EXPERIMENT_ID,
        "decision": PHASE8B_REVIEW_DECISION,
        "review_id": review_id,
        "acceptance_fingerprint": acceptance["acceptance_fingerprint"],
        "outcome": acceptance["outcome"],
        "champion_set_fingerprint": acceptance[
            "champion_set_fingerprint"
        ],
        "terminal": True,
        "demo_design_eligible": acceptance["demo_design_eligible"],
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    return payload | {
        "campaign_terminal_fingerprint": _canonical_digest(payload)
    }


def review_phase8b_campaign_directory(
    *,
    campaign_dir: Path,
    closure_id: str,
    code_commit: str,
) -> dict[str, object]:
    root = Path(campaign_dir)
    terminal_path = root / "campaign-terminal.json"
    if terminal_path.exists():
        raise ValueError("Phase 8B campaign is already terminal")
    commit = _validate_commit(
        code_commit,
        field="Phase 8B review code commit",
    )
    preflight = _load_json(
        root / "capture-preflight.json",
        label="Phase 8B capture preflight",
    )
    validate_phase8b_capture_preflight(preflight)
    reference_path = root / "spread-reference.json"
    reference_raw = reference_path.read_bytes()
    reference = json.loads(reference_raw)
    if not isinstance(reference, dict):
        raise ValueError("Phase 8B spread reference root must be an object")
    validate_phase8b_spread_reference(reference)
    if reference.get("capture_preflight_fingerprint") != preflight.get(
        "capture_preflight_fingerprint"
    ):
        raise ValueError("Phase 8B review spread-reference preflight mismatch")

    evidence = _closure_campaign_evidence(
        campaign_dir=root,
        closure_id=closure_id,
    )
    acceptance = compile_phase8b_acceptance(
        campaign_evidence=evidence,
        spread_reference=reference,
        code_commit=commit,
    )
    validate_phase8b_acceptance(acceptance)
    source_sha = hashlib.sha256(reference_raw).hexdigest()
    review_payload = {
        "campaign_evidence_fingerprint": evidence[
            "campaign_evidence_fingerprint"
        ],
        "spread_reference_fingerprint": reference[
            "spread_reference_fingerprint"
        ],
        "spread_reference_sha256": source_sha,
        "review_code_commit": commit,
    }
    review_id = _canonical_digest(review_payload)
    review_dir = root / "reviews" / review_id
    if review_dir.exists():
        raise FileExistsError("Phase 8B review already exists")

    shadow_validation = None
    if acceptance["outcome"] == PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN:
        shadow_validation = build_phase8b_shadow_validation(
            preflight=preflight,
            acceptance=acceptance,
            review_id=review_id,
        )

    review_dir.mkdir(parents=True, exist_ok=False)
    _atomic_write(
        review_dir / "source-spread-reference.json",
        reference_raw,
    )
    acceptance_dir = review_dir / "acceptance"
    acceptance_manifest = write_phase8b_acceptance_artifacts(
        acceptance,
        acceptance_dir,
    )
    artifacts: list[dict[str, object]] = [
        {
            "path": "source-spread-reference.json",
            "sha256": source_sha,
        },
        {
            "path": "acceptance/acceptance.json",
            "sha256": hashlib.sha256(
                (acceptance_dir / "acceptance.json").read_bytes()
            ).hexdigest(),
        },
        {
            "path": "acceptance/manifest.json",
            "sha256": hashlib.sha256(
                (acceptance_dir / "manifest.json").read_bytes()
            ).hexdigest(),
        },
    ]
    if shadow_validation is not None:
        shadow_path = review_dir / "shadow-validation.json"
        _atomic_write(shadow_path, _stable_json_bytes(shadow_validation))
        artifacts.append(
            {
                "path": shadow_path.name,
                "sha256": hashlib.sha256(shadow_path.read_bytes()).hexdigest(),
            }
        )

    terminal_outcomes = {
        PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
        PHASE8B_REJECT_OPERATIONAL_MISMATCH,
        PHASE8B_REJECT_MARKET_MISMATCH,
        PHASE8B_REJECT_FINANCIAL_MISMATCH,
        PHASE8B_REJECT_SAFETY_FAILURE,
    }
    terminal = acceptance["outcome"] in terminal_outcomes
    manifest = {
        "protocol": PHASE8B_REVIEW_MANIFEST_PROTOCOL,
        "experiment_id": PHASE8B_REVIEW_EXPERIMENT_ID,
        "decision": PHASE8B_REVIEW_DECISION,
        "review_id": review_id,
        "closure_id": closure_id,
        "outcome": acceptance["outcome"],
        "acceptance_fingerprint": acceptance["acceptance_fingerprint"],
        "spread_reference_fingerprint": reference[
            "spread_reference_fingerprint"
        ],
        "shadow_validation_fingerprint": (
            None
            if shadow_validation is None
            else shadow_validation["shadow_validation_fingerprint"]
        ),
        "terminal": terminal,
        "capture_may_continue": acceptance["outcome"] == PHASE8B_NEED_MORE_DATA,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
        "artifacts": artifacts,
        "acceptance_manifest_protocol": acceptance_manifest["protocol"],
    }
    _atomic_write(review_dir / "manifest.json", _stable_json_bytes(manifest))

    terminal_marker = None
    if terminal:
        if terminal_path.exists():
            raise ValueError("Phase 8B campaign became terminal during review")
        terminal_marker = _terminal_marker(
            review_id=review_id,
            acceptance=acceptance,
        )
        _atomic_write(terminal_path, _stable_json_bytes(terminal_marker))

    return {
        "review_id": review_id,
        "acceptance": acceptance,
        "shadow_validation": shadow_validation,
        "terminal_marker": terminal_marker,
        "manifest": manifest,
    }


__all__ = [
    "PHASE8B_CAMPAIGN_TERMINAL_PROTOCOL",
    "PHASE8B_REVIEW_DECISION",
    "PHASE8B_REVIEW_EXPERIMENT_ID",
    "PHASE8B_REVIEW_MANIFEST_PROTOCOL",
    "PHASE8B_SHADOW_VALIDATION_PROTOCOL",
    "PHASE8B_SPREAD_REFERENCE_ARTIFACT_PROTOCOL",
    "SHADOW_VALIDATION_EVIDENCE_ID",
    "SPREAD_METHOD",
    "build_phase8b_shadow_validation",
    "build_phase8b_spread_reference",
    "review_phase8b_campaign_directory",
    "validate_phase8b_shadow_validation",
    "write_phase8b_spread_reference",
]
