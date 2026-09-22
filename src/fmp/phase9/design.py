from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Mapping

from fmp.phase8b.acceptance import (
    PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
    validate_phase8b_acceptance,
)
from fmp.phase8b.capture import validate_phase8b_capture_preflight
from fmp.phase8b.design import (
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
)
from fmp.phase8b.review import (
    PHASE8B_CAMPAIGN_TERMINAL_PROTOCOL,
    PHASE8B_REVIEW_MANIFEST_PROTOCOL,
    validate_phase8b_shadow_validation,
)
from fmp.risk import RiskConfig


PHASE9_DECISION = "DEC-055"
PHASE9_EXPERIMENT_ID = "EXP-20260922-026"
PHASE9_DEMO_DESIGN_PROTOCOL = "fmp-phase9-demo-design-v1"
PHASE9_DEMO_DESIGN_ARTIFACT_PROTOCOL = "fmp-phase9-demo-design-artifacts-v1"
PHASE9_DEMO_DESIGN_FROZEN = "PHASE9_DEMO_DESIGN_FROZEN"
PHASE9_MT5_ORDER_BRIDGE_PROTOCOL = "fmp-mt5-demo-order-bridge-v1"

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


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


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


def _validate_terminal_marker(
    terminal: Mapping[str, object],
    *,
    review_id: str,
    acceptance: Mapping[str, object],
) -> None:
    if terminal.get("protocol") != PHASE8B_CAMPAIGN_TERMINAL_PROTOCOL:
        raise ValueError("Phase 9 requires the Phase 8B campaign-terminal protocol")
    if terminal.get("review_id") != review_id:
        raise ValueError("Phase 9 terminal review identity mismatch")
    if terminal.get("acceptance_fingerprint") != acceptance.get(
        "acceptance_fingerprint"
    ):
        raise ValueError("Phase 9 terminal acceptance identity mismatch")
    if terminal.get("outcome") != PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN:
        raise ValueError("Phase 9 design requires terminal Phase 8B PASS")
    if terminal.get("champion_set_fingerprint") != acceptance.get(
        "champion_set_fingerprint"
    ):
        raise ValueError("Phase 9 terminal champion identity mismatch")
    if terminal.get("terminal") is not True:
        raise ValueError("Phase 9 requires terminal Phase 8B evidence")
    if terminal.get("demo_design_eligible") is not True:
        raise ValueError("Phase 9 demo design is not eligible")
    for field in (
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_execution_authorized",
    ):
        if terminal.get(field) is not False:
            raise ValueError(f"Phase 9 terminal marker requires {field}=false")
    fingerprint = _validate_sha256(
        terminal.get("campaign_terminal_fingerprint"),
        field="Phase 8B campaign-terminal fingerprint",
    )
    payload = dict(terminal)
    payload.pop("campaign_terminal_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 8B campaign-terminal fingerprint mismatch")


def _validate_review_manifest(
    manifest: Mapping[str, object],
    *,
    review_id: str,
    acceptance: Mapping[str, object],
    shadow_validation: Mapping[str, object],
) -> None:
    if manifest.get("protocol") != PHASE8B_REVIEW_MANIFEST_PROTOCOL:
        raise ValueError("Phase 9 requires the Phase 8B review-manifest protocol")
    if manifest.get("review_id") != review_id:
        raise ValueError("Phase 9 review-manifest identity mismatch")
    if manifest.get("outcome") != PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN:
        raise ValueError("Phase 9 design requires exact Phase 8B PASS")
    if manifest.get("acceptance_fingerprint") != acceptance.get(
        "acceptance_fingerprint"
    ):
        raise ValueError("Phase 9 review-manifest acceptance mismatch")
    if manifest.get("shadow_validation_fingerprint") != shadow_validation.get(
        "shadow_validation_fingerprint"
    ):
        raise ValueError("Phase 9 review-manifest shadow-validation mismatch")
    if manifest.get("terminal") is not True:
        raise ValueError("Phase 9 review must be terminal")
    if manifest.get("capture_may_continue") is not False:
        raise ValueError("Phase 9 PASS review cannot permit more Phase 8B capture")
    for field in (
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_execution_authorized",
    ):
        if manifest.get(field) is not False:
            raise ValueError(f"Phase 9 review manifest requires {field}=false")


def _validated_pass_inputs(
    *,
    preflight: Mapping[str, object],
    review_id: str,
    review_manifest: Mapping[str, object],
    acceptance: Mapping[str, object],
    shadow_validation: Mapping[str, object],
    terminal: Mapping[str, object],
) -> None:
    validate_phase8b_capture_preflight(preflight)
    validate_phase8b_acceptance(acceptance)
    validate_phase8b_shadow_validation(shadow_validation)
    review = _validate_sha256(review_id, field="Phase 9 review ID")

    if acceptance.get("outcome") != PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN:
        raise ValueError("Phase 9 demo design requires exact Phase 8B PASS")
    if acceptance.get("demo_design_eligible") is not True:
        raise ValueError("Phase 9 demo design is not eligible")
    if acceptance.get("capture_preflight_fingerprint") != preflight.get(
        "capture_preflight_fingerprint"
    ):
        raise ValueError("Phase 9 acceptance/preflight identity mismatch")
    if acceptance.get("champion_set_fingerprint") != preflight.get(
        "champion_set_fingerprint"
    ):
        raise ValueError("Phase 9 acceptance champion identity mismatch")
    if acceptance.get("strategy_fingerprints") != preflight.get(
        "strategy_fingerprints"
    ):
        raise ValueError("Phase 9 acceptance strategy identity mismatch")

    if shadow_validation.get("review_id") != review:
        raise ValueError("Phase 9 shadow-validation review mismatch")
    if shadow_validation.get("acceptance_fingerprint") != acceptance.get(
        "acceptance_fingerprint"
    ):
        raise ValueError("Phase 9 shadow-validation acceptance mismatch")
    if shadow_validation.get("champion_set_fingerprint") != preflight.get(
        "champion_set_fingerprint"
    ):
        raise ValueError("Phase 9 shadow-validation champion mismatch")
    if shadow_validation.get("strategy_fingerprints") != preflight.get(
        "strategy_fingerprints"
    ):
        raise ValueError("Phase 9 shadow-validation strategy mismatch")

    _validate_review_manifest(
        review_manifest,
        review_id=review,
        acceptance=acceptance,
        shadow_validation=shadow_validation,
    )
    _validate_terminal_marker(
        terminal,
        review_id=review,
        acceptance=acceptance,
    )

    if preflight.get("provider") != MT5_PROVIDER:
        raise ValueError("Phase 9 design requires the accepted MT5 demo provider")
    if preflight.get("transport") != MT5_TRANSPORT:
        raise ValueError("Phase 9 design requires the accepted MT5 demo transport")
    if preflight.get("connector_protocol") != MT5_BRIDGE_PROTOCOL:
        raise ValueError("Phase 9 design requires the accepted MT5 quote protocol")
    server = preflight.get("server")
    if not isinstance(server, str) or not server:
        raise ValueError("Phase 9 accepted demo server is missing")
    _validate_sha256(
        preflight.get("account_fingerprint"),
        field="Phase 9 accepted demo account fingerprint",
    )


def build_phase9_demo_design(
    *,
    preflight: Mapping[str, object],
    review_id: str,
    review_manifest: Mapping[str, object],
    acceptance: Mapping[str, object],
    shadow_validation: Mapping[str, object],
    terminal: Mapping[str, object],
    code_commit: str,
) -> dict[str, object]:
    _validated_pass_inputs(
        preflight=preflight,
        review_id=review_id,
        review_manifest=review_manifest,
        acceptance=acceptance,
        shadow_validation=shadow_validation,
        terminal=terminal,
    )
    commit = _validate_commit(
        code_commit,
        field="Phase 9 demo-design code commit",
    )
    symbols = preflight.get("required_symbols")
    if not isinstance(symbols, list) or not symbols:
        raise ValueError("Phase 9 required symbols are malformed")
    if symbols != sorted(symbols):
        raise ValueError("Phase 9 required symbols must be sorted")
    strategies = preflight.get("strategies")
    if not isinstance(strategies, list) or not strategies:
        raise ValueError("Phase 9 strategy rows are malformed")

    payload = {
        "protocol": PHASE9_DEMO_DESIGN_PROTOCOL,
        "experiment_id": PHASE9_EXPERIMENT_ID,
        "decision": PHASE9_DECISION,
        "outcome": PHASE9_DEMO_DESIGN_FROZEN,
        "demo_design_code_commit": commit,
        "phase8b_review_id": review_id,
        "phase8b_acceptance_fingerprint": acceptance["acceptance_fingerprint"],
        "phase8b_shadow_validation_fingerprint": shadow_validation[
            "shadow_validation_fingerprint"
        ],
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "champion_set_id": preflight["champion_set_id"],
        "champion_set_fingerprint": preflight["champion_set_fingerprint"],
        "strategy_fingerprints": list(preflight["strategy_fingerprints"]),
        "strategies": [
            {
                "fingerprint": row["fingerprint"],
                "identity_json": row["identity_json"],
                "family": row["family"],
                "symbol": row["symbol"],
                "timeframe": row["timeframe"],
                "code_commit": row["code_commit"],
                "lifecycle": "SHADOW_VALIDATED",
            }
            for row in strategies
            if isinstance(row, Mapping)
        ],
        "execution_path": {
            "provider": MT5_PROVIDER,
            "accepted_quote_transport": MT5_TRANSPORT,
            "accepted_quote_protocol": MT5_BRIDGE_PROTOCOL,
            "future_order_bridge_protocol": PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
            "account_mode": "DEMO",
            "account_fingerprint": preflight["account_fingerprint"],
            "server": preflight["server"],
            "required_symbols": list(symbols),
            "symbol_mapping": {symbol: symbol for symbol in symbols},
            "auto_trading_change_authorized": False,
            "provider_change_authorized": False,
        },
        "risk_config": RiskConfig().to_config(),
        "required_controls": {
            "practice_account_assertion_before_order_session": True,
            "mandatory_protective_stop": True,
            "unprotected_position_healthy_state_allowed": False,
            "deterministic_client_order_ids": True,
            "duplicate_client_order_prevention": True,
            "requested_vs_fill_price_logging": True,
            "order_validation_journal": True,
            "order_ack_fill_rejection_journal": True,
            "startup_position_order_reconciliation": True,
            "orphan_unknown_position_fail_closed": True,
            "restart_recovery_required": True,
            "daily_halt_required": True,
            "secrets_in_git_allowed": False,
            "secrets_in_evidence_artifacts_allowed": False,
        },
        "demo_adapter_source_authorized": True,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {
        "demo_design_fingerprint": _canonical_digest(payload)
    }
    validate_phase9_demo_design(result)
    return result


def validate_phase9_demo_design(design: Mapping[str, object]) -> None:
    if design.get("protocol") != PHASE9_DEMO_DESIGN_PROTOCOL:
        raise ValueError("Phase 9 demo-design protocol mismatch")
    if design.get("experiment_id") != PHASE9_EXPERIMENT_ID:
        raise ValueError("Phase 9 demo-design experiment mismatch")
    if design.get("decision") != PHASE9_DECISION:
        raise ValueError("Phase 9 demo-design decision mismatch")
    if design.get("outcome") != PHASE9_DEMO_DESIGN_FROZEN:
        raise ValueError("Phase 9 demo-design outcome mismatch")
    _validate_commit(
        design.get("demo_design_code_commit"),
        field="Phase 9 demo-design code commit",
    )
    for field in (
        "phase8b_review_id",
        "phase8b_acceptance_fingerprint",
        "phase8b_shadow_validation_fingerprint",
        "capture_preflight_fingerprint",
        "champion_set_fingerprint",
        "demo_design_fingerprint",
    ):
        _validate_sha256(design.get(field), field=f"Phase 9 {field}")

    fingerprints = design.get("strategy_fingerprints")
    strategies = design.get("strategies")
    if (
        not isinstance(fingerprints, list)
        or not fingerprints
        or fingerprints != sorted(fingerprints)
        or len(set(fingerprints)) != len(fingerprints)
    ):
        raise ValueError("Phase 9 strategy fingerprints are malformed")
    if not isinstance(strategies, list) or len(strategies) != len(fingerprints):
        raise ValueError("Phase 9 strategy rows are malformed")
    if [
        row.get("fingerprint")
        for row in strategies
        if isinstance(row, Mapping)
    ] != fingerprints:
        raise ValueError("Phase 9 strategy row identity mismatch")
    if any(
        not isinstance(row, Mapping) or row.get("lifecycle") != "SHADOW_VALIDATED"
        for row in strategies
    ):
        raise ValueError("Phase 9 design requires SHADOW_VALIDATED strategies")

    execution = design.get("execution_path")
    if not isinstance(execution, Mapping):
        raise ValueError("Phase 9 execution path is malformed")
    expected_execution = {
        "provider": MT5_PROVIDER,
        "accepted_quote_transport": MT5_TRANSPORT,
        "accepted_quote_protocol": MT5_BRIDGE_PROTOCOL,
        "future_order_bridge_protocol": PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
        "account_mode": "DEMO",
    }
    for field, expected in expected_execution.items():
        if execution.get(field) != expected:
            raise ValueError(f"Phase 9 execution-path {field} mismatch")
    _validate_sha256(
        execution.get("account_fingerprint"),
        field="Phase 9 demo account fingerprint",
    )
    symbols = execution.get("required_symbols")
    mapping = execution.get("symbol_mapping")
    if not isinstance(symbols, list) or not symbols or symbols != sorted(symbols):
        raise ValueError("Phase 9 required symbols are malformed")
    if not isinstance(mapping, Mapping) or mapping != {
        symbol: symbol for symbol in symbols
    }:
        raise ValueError("Phase 9 symbol mapping must be exact identity mapping")
    if execution.get("auto_trading_change_authorized") is not False:
        raise ValueError("Phase 9 design cannot change AutoTrading")
    if execution.get("provider_change_authorized") is not False:
        raise ValueError("Phase 9 design cannot authorize provider change")

    if design.get("risk_config") != RiskConfig().to_config():
        raise ValueError("Phase 9 risk configuration drift")

    controls = design.get("required_controls")
    if not isinstance(controls, Mapping):
        raise ValueError("Phase 9 required controls are malformed")
    required_true = {
        "practice_account_assertion_before_order_session",
        "mandatory_protective_stop",
        "deterministic_client_order_ids",
        "duplicate_client_order_prevention",
        "requested_vs_fill_price_logging",
        "order_validation_journal",
        "order_ack_fill_rejection_journal",
        "startup_position_order_reconciliation",
        "orphan_unknown_position_fail_closed",
        "restart_recovery_required",
        "daily_halt_required",
    }
    for field in required_true:
        if controls.get(field) is not True:
            raise ValueError(f"Phase 9 required control {field} must be true")
    for field in (
        "unprotected_position_healthy_state_allowed",
        "secrets_in_git_allowed",
        "secrets_in_evidence_artifacts_allowed",
    ):
        if controls.get(field) is not False:
            raise ValueError(f"Phase 9 safety control {field} must be false")

    if design.get("demo_adapter_source_authorized") is not True:
        raise ValueError("Phase 9 design must authorize demo-adapter source only")
    for field in (
        "demo_execution_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase10_authorized",
    ):
        if design.get(field) is not False:
            raise ValueError(f"Phase 9 design requires {field}=false")

    fingerprint = design["demo_design_fingerprint"]
    payload = dict(design)
    payload.pop("demo_design_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 9 demo-design fingerprint mismatch")


def build_phase9_demo_design_from_campaign(
    *,
    campaign_dir: Path,
    review_id: str,
    code_commit: str,
) -> dict[str, object]:
    root = Path(campaign_dir)
    review = _validate_sha256(review_id, field="Phase 9 review ID")
    review_dir = root / "reviews" / review
    preflight = _load_json(
        root / "capture-preflight.json",
        label="Phase 8B capture preflight",
    )
    manifest = _load_json(
        review_dir / "manifest.json",
        label="Phase 8B review manifest",
    )
    acceptance = _load_json(
        review_dir / "acceptance" / "acceptance.json",
        label="Phase 8B acceptance artifact",
    )
    shadow_validation = _load_json(
        review_dir / "shadow-validation.json",
        label="Phase 8B shadow-validation artifact",
    )
    terminal = _load_json(
        root / "campaign-terminal.json",
        label="Phase 8B campaign-terminal artifact",
    )
    return build_phase9_demo_design(
        preflight=preflight,
        review_id=review,
        review_manifest=manifest,
        acceptance=acceptance,
        shadow_validation=shadow_validation,
        terminal=terminal,
        code_commit=code_commit,
    )


def write_phase9_demo_design(
    design: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    validate_phase9_demo_design(design)
    root = Path(out_dir)
    result_path = root / "design.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 9 demo-design artifacts already exist")
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(design))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE9_DEMO_DESIGN_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_EXPERIMENT_ID,
        "decision": PHASE9_DECISION,
        "outcome": PHASE9_DEMO_DESIGN_FROZEN,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "demo_adapter_source_authorized": True,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
        "artifacts": [
            {
                "path": result_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "PHASE9_DECISION",
    "PHASE9_EXPERIMENT_ID",
    "PHASE9_DEMO_DESIGN_ARTIFACT_PROTOCOL",
    "PHASE9_DEMO_DESIGN_FROZEN",
    "PHASE9_DEMO_DESIGN_PROTOCOL",
    "PHASE9_MT5_ORDER_BRIDGE_PROTOCOL",
    "build_phase9_demo_design",
    "build_phase9_demo_design_from_campaign",
    "validate_phase9_demo_design",
    "write_phase9_demo_design",
]
