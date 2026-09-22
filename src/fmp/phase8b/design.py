from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Mapping

from fmp.portfolio.acceptance_review import (
    DEC045_EXPERIMENT_ID,
    PHASE8A_ACCEPTANCE_PROTOCOL,
    PHASE8A_SHADOW_CANDIDATE_ACCEPTED,
    resolve_phase8a_shadow_candidate_records,
)

PHASE8B_EXPERIMENT_ID = "EXP-20260922-017"
PHASE8B_DESIGN_PROTOCOL = "fmp-phase8b-shadow-design-v1"
PHASE8B_DESIGN_ARTIFACT_PROTOCOL = "fmp-phase8b-shadow-design-artifacts-v1"
PHASE8B_DESIGN_FROZEN = "PHASE8B_DESIGN_FROZEN"

MT5_PROVIDER = "FP_MARKETS_MT5_DEMO"
MT5_TRANSPORT = "MT5_FILE_COMMON_JSONL"
MT5_BRIDGE_PROTOCOL = "fmp-mt5-demo-multisymbol-file-bridge-v1"
MT5_ALLOWED_SERVERS = ("FPMarketsSC-Demo", "FPMarketsSC-Demo2")
LIVENESS_TIMEOUT_SECONDS = 15.0
QUOTE_DEADLINE_SECONDS = 5.0
SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
SUPPORTED_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
SUPPORTED_TIMEFRAMES = ("5m", "15m", "1h")
BRIDGE_FILE_BY_SYMBOL = {
    "EURUSD": "FMP/phase8b-eurusd-feed.jsonl",
    "GBPUSD": "FMP/phase8b-gbpusd-feed.jsonl",
    "USDJPY": "FMP/phase8b-usdjpy-feed.jsonl",
}

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


def _canonical_digest(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _artifact_record(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": path.name,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _validate_acceptance(
    acceptance: Mapping[str, object],
) -> None:
    if acceptance.get("protocol") != PHASE8A_ACCEPTANCE_PROTOCOL:
        raise ValueError("Phase 8B design requires DEC-045 acceptance protocol")
    if acceptance.get("experiment_id") != DEC045_EXPERIMENT_ID:
        raise ValueError("Phase 8B design requires EXP-20260922-016 acceptance")
    if acceptance.get("outcome") != PHASE8A_SHADOW_CANDIDATE_ACCEPTED:
        raise ValueError("Phase 8B design requires an accepted shadow candidate")
    if acceptance.get("shadow_candidate_authorized") is not True:
        raise ValueError("Phase 8B shadow candidate is not authorized")
    if acceptance.get("phase8b_design_authorized") is not True:
        raise ValueError("Phase 8B design is not authorized")
    for field in (
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_authorized",
    ):
        if acceptance.get(field) is not False:
            raise ValueError(f"Phase 8B design requires {field}=false")
    _validate_commit(
        acceptance.get("acceptance_code_commit"),
        field="DEC-045 acceptance compiler commit",
    )


def _design_payload_without_fingerprint(
    *,
    acceptance: Mapping[str, object],
    acceptance_sha256: str,
    design_code_commit: str,
) -> dict[str, object]:
    _validate_acceptance(acceptance)
    accepted_sha = _validate_sha256(
        acceptance_sha256,
        field="DEC-045 acceptance artifact digest",
    )
    design_commit = _validate_commit(
        design_code_commit,
        field="Phase 8B design compiler commit",
    )
    records = resolve_phase8a_shadow_candidate_records(acceptance)
    if len(records) < 2:
        raise ValueError("Phase 8B design requires at least two shadow-candidate strategies")

    required_symbols = sorted({item.strategy.symbol for item in records})
    required_timeframes = sorted(
        {item.strategy.timeframe for item in records},
        key=SUPPORTED_TIMEFRAMES.index,
    )
    if any(symbol not in SUPPORTED_SYMBOLS for symbol in required_symbols):
        raise ValueError("Phase 8B design contains unsupported symbol")
    if any(timeframe not in SUPPORTED_TIMEFRAMES for timeframe in required_timeframes):
        raise ValueError("Phase 8B design contains unsupported timeframe")

    candidate = acceptance.get("shadow_candidate")
    if not isinstance(candidate, Mapping):
        raise ValueError("Phase 8B design acceptance candidate is missing")
    champion_set_id = candidate.get("champion_set_id")
    champion_set_fingerprint = candidate.get("champion_set_fingerprint")
    if not isinstance(champion_set_id, str) or not champion_set_id:
        raise ValueError("Phase 8B design champion_set_id is missing")
    _validate_sha256(
        champion_set_fingerprint,
        field="Phase 8B champion-set fingerprint",
    )

    strategies = [
        {
            "fingerprint": item.strategy.fingerprint,
            "identity_json": item.strategy.identity_json,
            "family": item.strategy.family,
            "symbol": item.strategy.symbol,
            "timeframe": item.strategy.timeframe,
            "parameters_json": item.strategy.parameters_json,
            "code_commit": item.strategy.code_commit,
            "lifecycle": item.lifecycle.value,
            "evidence_id": item.evidence_id,
        }
        for item in records
    ]

    return {
        "protocol": PHASE8B_DESIGN_PROTOCOL,
        "experiment_id": PHASE8B_EXPERIMENT_ID,
        "outcome": PHASE8B_DESIGN_FROZEN,
        "dec045_acceptance_sha256": accepted_sha,
        "dec045_acceptance_code_commit": acceptance["acceptance_code_commit"],
        "phase8b_design_code_commit": design_commit,
        "champion_set_id": champion_set_id,
        "champion_set_fingerprint": champion_set_fingerprint,
        "strategy_count": len(strategies),
        "strategy_fingerprints": [item["fingerprint"] for item in strategies],
        "strategies": strategies,
        "required_symbols": required_symbols,
        "required_timeframes": required_timeframes,
        "connector": {
            "provider": MT5_PROVIDER,
            "transport": MT5_TRANSPORT,
            "protocol": MT5_BRIDGE_PROTOCOL,
            "allowed_servers": list(MT5_ALLOWED_SERVERS),
            "account_mode": "DEMO",
            "one_ea_per_required_symbol": True,
            "bridge_file_by_symbol": {
                symbol: BRIDGE_FILE_BY_SYMBOL[symbol]
                for symbol in required_symbols
            },
            "auto_trading_required_off": True,
            "broker_order_surface_allowed": False,
            "arbitrary_symbol_override_allowed": False,
            "arbitrary_path_override_allowed": False,
        },
        "liveness": {
            "bridge_timeout_seconds": LIVENESS_TIMEOUT_SECONDS,
            "market_quiet_threshold_seconds": LIVENESS_TIMEOUT_SECONDS,
            "quote_deadline_seconds": QUOTE_DEADLINE_SECONDS,
            "per_required_symbol": True,
            "market_quiet_is_bridge_failure": False,
            "backfill_allowed": False,
            "interpolation_allowed": False,
            "alternate_provider_repair_allowed": False,
        },
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "campaign_registration_authorized": False,
        "campaign_start_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }


def build_phase8b_design(
    *,
    acceptance: Mapping[str, object],
    acceptance_sha256: str,
    code_commit: str,
) -> dict[str, object]:
    payload = _design_payload_without_fingerprint(
        acceptance=acceptance,
        acceptance_sha256=acceptance_sha256,
        design_code_commit=code_commit,
    )
    fingerprint = _canonical_digest(payload)
    return payload | {"design_fingerprint": fingerprint}


def validate_phase8b_design(design: Mapping[str, object]) -> None:
    if design.get("protocol") != PHASE8B_DESIGN_PROTOCOL:
        raise ValueError("Phase 8B design protocol mismatch")
    if design.get("experiment_id") != PHASE8B_EXPERIMENT_ID:
        raise ValueError("Phase 8B design experiment mismatch")
    if design.get("outcome") != PHASE8B_DESIGN_FROZEN:
        raise ValueError("Phase 8B design outcome mismatch")
    _validate_sha256(
        design.get("dec045_acceptance_sha256"),
        field="DEC-045 acceptance artifact digest",
    )
    _validate_commit(
        design.get("dec045_acceptance_code_commit"),
        field="DEC-045 acceptance compiler commit",
    )
    _validate_commit(
        design.get("phase8b_design_code_commit"),
        field="Phase 8B design compiler commit",
    )
    _validate_sha256(
        design.get("champion_set_fingerprint"),
        field="Phase 8B champion-set fingerprint",
    )
    strategy_fingerprints = design.get("strategy_fingerprints")
    strategies = design.get("strategies")
    if not isinstance(strategy_fingerprints, list) or len(strategy_fingerprints) < 2:
        raise ValueError("Phase 8B design strategy fingerprints are malformed")
    if strategy_fingerprints != sorted(str(strategy) for strategy in strategy_fingerprints):
        raise ValueError("Phase 8B design strategy fingerprints must be sorted")
    if len(set(strategy_fingerprints)) != len(strategy_fingerprints):
        raise ValueError("Phase 8B design contains duplicate strategy fingerprints")
    if not isinstance(strategies, list) or len(strategies) != len(strategy_fingerprints):
        raise ValueError("Phase 8B design strategy rows are malformed")
    if [row.get("fingerprint") for row in strategies if isinstance(row, Mapping)] != strategy_fingerprints:
        raise ValueError("Phase 8B design strategy row identity mismatch")
    if any(
        not isinstance(row, Mapping) or row.get("lifecycle") != "SHADOW_CANDIDATE"
        for row in strategies
    ):
        raise ValueError("Phase 8B design requires SHADOW_CANDIDATE strategies")

    required_symbols = design.get("required_symbols")
    required_timeframes = design.get("required_timeframes")
    if not isinstance(required_symbols, list) or not required_symbols:
        raise ValueError("Phase 8B required symbols are malformed")
    if required_symbols != sorted(required_symbols):
        raise ValueError("Phase 8B required symbols must be sorted")
    if any(symbol not in SUPPORTED_SYMBOLS for symbol in required_symbols):
        raise ValueError("Phase 8B design has unsupported required symbol")
    if not isinstance(required_timeframes, list) or not required_timeframes:
        raise ValueError("Phase 8B required timeframes are malformed")
    if any(timeframe not in SUPPORTED_TIMEFRAMES for timeframe in required_timeframes):
        raise ValueError("Phase 8B design has unsupported required timeframe")
    expected_timeframes = sorted(required_timeframes, key=SUPPORTED_TIMEFRAMES.index)
    if required_timeframes != expected_timeframes:
        raise ValueError("Phase 8B required timeframes are not canonically ordered")

    strategy_symbols = sorted({str(row["symbol"]) for row in strategies})
    strategy_timeframes = sorted(
        {str(row["timeframe"]) for row in strategies},
        key=SUPPORTED_TIMEFRAMES.index,
    )
    if required_symbols != strategy_symbols:
        raise ValueError("Phase 8B required symbol union mismatch")
    if required_timeframes != strategy_timeframes:
        raise ValueError("Phase 8B required timeframe union mismatch")

    connector = design.get("connector")
    if not isinstance(connector, Mapping):
        raise ValueError("Phase 8B connector design is missing")
    if connector.get("provider") != MT5_PROVIDER:
        raise ValueError("Phase 8B provider drift")
    if connector.get("transport") != MT5_TRANSPORT:
        raise ValueError("Phase 8B transport drift")
    if connector.get("protocol") != MT5_BRIDGE_PROTOCOL:
        raise ValueError("Phase 8B bridge protocol drift")
    if connector.get("allowed_servers") != list(MT5_ALLOWED_SERVERS):
        raise ValueError("Phase 8B allowed-server drift")
    if connector.get("account_mode") != "DEMO":
        raise ValueError("Phase 8B requires demo account mode")
    expected_files = {
        symbol: BRIDGE_FILE_BY_SYMBOL[symbol]
        for symbol in required_symbols
    }
    if connector.get("bridge_file_by_symbol") != expected_files:
        raise ValueError("Phase 8B bridge-file mapping mismatch")
    for field in (
        "one_ea_per_required_symbol",
        "auto_trading_required_off",
    ):
        if connector.get(field) is not True:
            raise ValueError(f"Phase 8B connector requires {field}=true")
    for field in (
        "broker_order_surface_allowed",
        "arbitrary_symbol_override_allowed",
        "arbitrary_path_override_allowed",
    ):
        if connector.get(field) is not False:
            raise ValueError(f"Phase 8B connector requires {field}=false")

    liveness = design.get("liveness")
    if not isinstance(liveness, Mapping):
        raise ValueError("Phase 8B liveness design is missing")
    expected_liveness = {
        "bridge_timeout_seconds": LIVENESS_TIMEOUT_SECONDS,
        "market_quiet_threshold_seconds": LIVENESS_TIMEOUT_SECONDS,
        "quote_deadline_seconds": QUOTE_DEADLINE_SECONDS,
        "per_required_symbol": True,
        "market_quiet_is_bridge_failure": False,
        "backfill_allowed": False,
        "interpolation_allowed": False,
        "alternate_provider_repair_allowed": False,
    }
    if dict(liveness) != expected_liveness:
        raise ValueError("Phase 8B liveness contract drift")
    if design.get("slippage_scenarios") != list(SLIPPAGE_SCENARIOS):
        raise ValueError("Phase 8B slippage scenario drift")

    for field in (
        "campaign_registration_authorized",
        "campaign_start_authorized",
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_authorized",
    ):
        if design.get(field) is not False:
            raise ValueError(f"Phase 8B design requires {field}=false")

    fingerprint = _validate_sha256(
        design.get("design_fingerprint"),
        field="Phase 8B design fingerprint",
    )
    payload = dict(design)
    payload.pop("design_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 8B design fingerprint mismatch")


def write_phase8b_design_artifacts(
    design: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    validate_phase8b_design(design)
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "design.json"
    _atomic_write(result_path, _stable_json_bytes(dict(design)))
    manifest = {
        "protocol": PHASE8B_DESIGN_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE8B_EXPERIMENT_ID,
        "promotion_authorized": False,
        "campaign_registration_authorized": False,
        "campaign_start_authorized": False,
        "artifacts": [_artifact_record(result_path)],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "BRIDGE_FILE_BY_SYMBOL",
    "LIVENESS_TIMEOUT_SECONDS",
    "MT5_ALLOWED_SERVERS",
    "MT5_BRIDGE_PROTOCOL",
    "MT5_PROVIDER",
    "MT5_TRANSPORT",
    "PHASE8B_DESIGN_FROZEN",
    "PHASE8B_DESIGN_PROTOCOL",
    "PHASE8B_EXPERIMENT_ID",
    "QUOTE_DEADLINE_SECONDS",
    "SLIPPAGE_SCENARIOS",
    "build_phase8b_design",
    "validate_phase8b_design",
    "write_phase8b_design_artifacts",
]
