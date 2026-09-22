from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, Sequence

from fmp.contracts import Direction, OrderIntent
from fmp.phase9.design import (
    PHASE9_DEMO_DESIGN_PROTOCOL,
    validate_phase9_demo_design,
)


PHASE9_DEMO_ORDER_DECISION = "DEC-056"
PHASE9_DEMO_ORDER_EXPERIMENT_ID = "EXP-20260922-027"
PHASE9_DEMO_ORDER_PROTOCOL_READY = "PHASE9_DEMO_ORDER_PROTOCOL_READY"

PHASE9_DEMO_ORDER_FOUNDATION_PROTOCOL = (
    "fmp-phase9-demo-order-protocol-foundation-v1"
)
PHASE9_DEMO_ORDER_REQUEST_PROTOCOL = "fmp-phase9-demo-order-request-v1"
PHASE9_DEMO_DRY_RUN_PROTOCOL = "fmp-phase9-demo-dry-run-v1"
PHASE9_DEMO_DRY_RUN_ARTIFACT_PROTOCOL = (
    "fmp-phase9-demo-dry-run-artifacts-v1"
)
PHASE9_DEMO_RECONCILIATION_PROTOCOL = (
    "fmp-phase9-demo-reconciliation-v1"
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class DemoExecutionLockedError(RuntimeError):
    """Raised whenever DEC-056 code is asked to submit a broker order."""


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


def _require_utc(value: object, *, field: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise ValueError(f"{field} must use UTC")
    return value


def _utc_string(value: datetime) -> str:
    _require_utc(value, field="timestamp")
    return value.isoformat().replace("+00:00", "Z")


def _positive_number(value: object, *, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) <= 0
    ):
        raise ValueError(f"{field} must be finite and positive")
    return float(value)


def _positive_int(value: object, *, field: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise ValueError(f"{field} must be a positive integer")
    return value


def _nonempty_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _design_execution(
    design: Mapping[str, object],
) -> Mapping[str, object]:
    validate_phase9_demo_design(design)
    if design.get("protocol") != PHASE9_DEMO_DESIGN_PROTOCOL:
        raise ValueError("Phase 9 demo-order design protocol mismatch")
    if design.get("demo_adapter_source_authorized") is not True:
        raise ValueError("Phase 9 demo-adapter source is not authorized")
    for field in (
        "demo_execution_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase10_authorized",
    ):
        if design.get(field) is not False:
            raise ValueError(
                f"Phase 9 demo-order protocol requires {field}=false"
            )
    execution = design.get("execution_path")
    if not isinstance(execution, Mapping):
        raise ValueError("Phase 9 demo-order execution path is malformed")
    if execution.get("account_mode") != "DEMO":
        raise ValueError("Phase 9 demo-order protocol requires DEMO account")
    return execution


def _strategy_row(
    design: Mapping[str, object],
    *,
    strategy_fingerprint: str,
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        strategy_fingerprint,
        field="Phase 9 strategy fingerprint",
    )
    rows = design.get("strategies")
    if not isinstance(rows, list):
        raise ValueError("Phase 9 demo-design strategies are malformed")
    matches = [
        row
        for row in rows
        if isinstance(row, Mapping)
        and row.get("fingerprint") == fingerprint
    ]
    if len(matches) != 1:
        raise ValueError(
            "Phase 9 order request strategy must be in the accepted champion"
        )
    return matches[0]


def _request_identity_payload(
    *,
    design: Mapping[str, object],
    intent: OrderIntent,
    strategy_fingerprint: str,
) -> dict[str, object]:
    return {
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprint": strategy_fingerprint,
        "decision_id": intent.decision_id,
        "symbol": intent.symbol,
        "direction": intent.direction.value,
        "units": intent.units,
        "stop_price": intent.stop_price,
        "target_price": intent.target_price,
        "decision_timestamp_utc": _utc_string(
            intent.decision_timestamp_utc
        ),
        "earliest_executable_timestamp_utc": _utc_string(
            intent.earliest_executable_timestamp_utc
        ),
    }


def build_phase9_demo_order_protocol_foundation(
    *,
    design: Mapping[str, object],
    code_commit: str,
) -> dict[str, object]:
    _design_execution(design)
    commit = _validate_commit(
        code_commit,
        field="Phase 9 demo-order protocol code commit",
    )
    payload = {
        "protocol": PHASE9_DEMO_ORDER_FOUNDATION_PROTOCOL,
        "experiment_id": PHASE9_DEMO_ORDER_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_ORDER_DECISION,
        "outcome": PHASE9_DEMO_ORDER_PROTOCOL_READY,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "demo_order_protocol_code_commit": commit,
        "demo_adapter_protocol_ready": True,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    return payload | {
        "demo_order_protocol_fingerprint": _canonical_digest(payload)
    }


def build_phase9_demo_order_request(
    *,
    design: Mapping[str, object],
    intent: OrderIntent,
    strategy_fingerprint: str,
    reference_entry_price: float,
) -> dict[str, object]:
    execution = _design_execution(design)
    if not isinstance(intent, OrderIntent):
        raise TypeError("intent must be an OrderIntent")

    decision_id = _nonempty_string(
        intent.decision_id,
        field="Phase 9 decision ID",
    )
    if intent.direction not in {Direction.LONG, Direction.SHORT}:
        raise ValueError("Phase 9 demo request requires LONG or SHORT")
    units = _positive_int(intent.units, field="Phase 9 units")
    reserved_risk = _positive_number(
        intent.reserved_risk_usd,
        field="Phase 9 reserved risk",
    )
    stop = _positive_number(
        intent.stop_price,
        field="Phase 9 protective stop",
    )
    target = (
        None
        if intent.target_price is None
        else _positive_number(
            intent.target_price,
            field="Phase 9 target",
        )
    )
    reference = _positive_number(
        reference_entry_price,
        field="Phase 9 reference entry price",
    )
    decision_time = _require_utc(
        intent.decision_timestamp_utc,
        field="Phase 9 decision timestamp",
    )
    earliest = _require_utc(
        intent.earliest_executable_timestamp_utc,
        field="Phase 9 earliest executable timestamp",
    )
    if earliest <= decision_time:
        raise ValueError(
            "Phase 9 earliest executable timestamp must be after decision"
        )

    row = _strategy_row(
        design,
        strategy_fingerprint=strategy_fingerprint,
    )
    if row.get("symbol") != intent.symbol:
        raise ValueError(
            "Phase 9 order request symbol does not match strategy"
        )

    symbols = execution.get("required_symbols")
    mapping = execution.get("symbol_mapping")
    if (
        not isinstance(symbols, list)
        or intent.symbol not in symbols
        or not isinstance(mapping, Mapping)
        or mapping.get(intent.symbol) != intent.symbol
    ):
        raise ValueError("Phase 9 order request symbol is not approved")

    if intent.direction is Direction.LONG:
        if stop >= reference:
            raise ValueError("Phase 9 LONG stop must be below reference price")
        if target is not None and target <= reference:
            raise ValueError(
                "Phase 9 LONG target must be above reference price"
            )
    else:
        if stop <= reference:
            raise ValueError("Phase 9 SHORT stop must be above reference price")
        if target is not None and target >= reference:
            raise ValueError(
                "Phase 9 SHORT target must be below reference price"
            )

    identity_payload = _request_identity_payload(
        design=design,
        intent=intent,
        strategy_fingerprint=strategy_fingerprint,
    )
    identity_sha = _canonical_digest(identity_payload)
    client_order_id = f"fmp9-{identity_sha[:24]}"
    payload = {
        "protocol": PHASE9_DEMO_ORDER_REQUEST_PROTOCOL,
        "experiment_id": PHASE9_DEMO_ORDER_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_ORDER_DECISION,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprint": strategy_fingerprint,
        "request_identity_sha256": identity_sha,
        "client_order_id": client_order_id,
        "decision_id": decision_id,
        "symbol": intent.symbol,
        "broker_symbol": intent.symbol,
        "direction": intent.direction.value,
        "units": units,
        "reserved_risk_usd": reserved_risk,
        "stop_price": stop,
        "target_price": target,
        "reference_entry_price": reference,
        "decision_timestamp_utc": _utc_string(decision_time),
        "earliest_executable_timestamp_utc": _utc_string(earliest),
        "provider": execution["provider"],
        "account_mode": "DEMO",
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {
        "request_fingerprint": _canonical_digest(payload)
    }
    validate_phase9_demo_order_request(
        result,
        design=design,
    )
    return result


def validate_phase9_demo_order_request(
    request: Mapping[str, object],
    *,
    design: Mapping[str, object],
) -> None:
    execution = _design_execution(design)
    if request.get("protocol") != PHASE9_DEMO_ORDER_REQUEST_PROTOCOL:
        raise ValueError("Phase 9 demo-order request protocol mismatch")
    if request.get("experiment_id") != PHASE9_DEMO_ORDER_EXPERIMENT_ID:
        raise ValueError("Phase 9 demo-order request experiment mismatch")
    if request.get("decision") != PHASE9_DEMO_ORDER_DECISION:
        raise ValueError("Phase 9 demo-order request decision mismatch")
    if request.get("demo_design_fingerprint") != design.get(
        "demo_design_fingerprint"
    ):
        raise ValueError("Phase 9 demo-order design identity mismatch")
    if request.get("champion_set_fingerprint") != design.get(
        "champion_set_fingerprint"
    ):
        raise ValueError("Phase 9 demo-order champion identity mismatch")

    strategy = _validate_sha256(
        request.get("strategy_fingerprint"),
        field="Phase 9 demo-order strategy fingerprint",
    )
    row = _strategy_row(design, strategy_fingerprint=strategy)
    symbol = _nonempty_string(
        request.get("symbol"),
        field="Phase 9 demo-order symbol",
    )
    if row.get("symbol") != symbol:
        raise ValueError("Phase 9 demo-order strategy/symbol mismatch")

    direction_raw = request.get("direction")
    try:
        direction = Direction(direction_raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("Phase 9 demo-order direction is invalid") from exc
    if direction not in {Direction.LONG, Direction.SHORT}:
        raise ValueError("Phase 9 demo-order direction must be LONG or SHORT")

    units = _positive_int(request.get("units"), field="Phase 9 demo-order units")
    _positive_number(
        request.get("reserved_risk_usd"),
        field="Phase 9 demo-order reserved risk",
    )
    stop = _positive_number(
        request.get("stop_price"),
        field="Phase 9 demo-order protective stop",
    )
    raw_target = request.get("target_price")
    target = (
        None
        if raw_target is None
        else _positive_number(
            raw_target,
            field="Phase 9 demo-order target",
        )
    )
    reference = _positive_number(
        request.get("reference_entry_price"),
        field="Phase 9 demo-order reference entry price",
    )

    if direction is Direction.LONG:
        if stop >= reference:
            raise ValueError("Phase 9 LONG stop must be below reference price")
        if target is not None and target <= reference:
            raise ValueError("Phase 9 LONG target must be above reference price")
    else:
        if stop <= reference:
            raise ValueError("Phase 9 SHORT stop must be above reference price")
        if target is not None and target >= reference:
            raise ValueError("Phase 9 SHORT target must be below reference price")

    if request.get("broker_symbol") != symbol:
        raise ValueError("Phase 9 demo-order broker-symbol mapping mismatch")
    if request.get("provider") != execution.get("provider"):
        raise ValueError("Phase 9 demo-order provider identity mismatch")
    if request.get("account_mode") != "DEMO":
        raise ValueError("Phase 9 demo-order account mode mismatch")
    if request.get("account_fingerprint") != execution.get(
        "account_fingerprint"
    ):
        raise ValueError("Phase 9 demo-order account identity mismatch")
    if request.get("server") != execution.get("server"):
        raise ValueError("Phase 9 demo-order server identity mismatch")

    decision_time = _parse_request_timestamp(
        request.get("decision_timestamp_utc"),
        field="Phase 9 demo-order decision timestamp",
    )
    earliest = _parse_request_timestamp(
        request.get("earliest_executable_timestamp_utc"),
        field="Phase 9 demo-order earliest executable timestamp",
    )
    if earliest <= decision_time:
        raise ValueError(
            "Phase 9 demo-order earliest executable timestamp must be after decision"
        )
    decision_id = _nonempty_string(
        request.get("decision_id"),
        field="Phase 9 demo-order decision ID",
    )

    identity_payload = {
        "demo_design_fingerprint": request["demo_design_fingerprint"],
        "champion_set_fingerprint": request["champion_set_fingerprint"],
        "strategy_fingerprint": strategy,
        "decision_id": decision_id,
        "symbol": symbol,
        "direction": direction.value,
        "units": units,
        "stop_price": stop,
        "target_price": target,
        "decision_timestamp_utc": request["decision_timestamp_utc"],
        "earliest_executable_timestamp_utc": request[
            "earliest_executable_timestamp_utc"
        ],
    }
    identity_sha = _canonical_digest(identity_payload)
    if request.get("request_identity_sha256") != identity_sha:
        raise ValueError("Phase 9 demo-order request identity mismatch")
    if request.get("client_order_id") != f"fmp9-{identity_sha[:24]}":
        raise ValueError("Phase 9 demo-order client order ID mismatch")

    for field in (
        "demo_execution_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase10_authorized",
    ):
        if request.get(field) is not False:
            raise ValueError(f"Phase 9 demo-order request requires {field}=false")

    fingerprint = _validate_sha256(
        request.get("request_fingerprint"),
        field="Phase 9 demo-order request fingerprint",
    )
    payload = dict(request)
    payload.pop("request_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 9 demo-order request fingerprint mismatch")


def _parse_request_timestamp(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    return _require_utc(parsed, field=field)


def build_phase9_demo_dry_run(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
) -> dict[str, object]:
    validate_phase9_demo_order_request(request, design=design)
    payload = {
        "protocol": PHASE9_DEMO_DRY_RUN_PROTOCOL,
        "experiment_id": PHASE9_DEMO_ORDER_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_ORDER_DECISION,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "validation_result": "VALIDATED",
        "submission_attempted": False,
        "broker_mutation_attempted": False,
        "demo_order_submitted": False,
        "live_order_submitted": False,
        "real_money_action_attempted": False,
        "phase10_authorized": False,
    }
    return payload | {
        "dry_run_fingerprint": _canonical_digest(payload)
    }


def validate_phase9_demo_dry_run(value: Mapping[str, object]) -> None:
    if value.get("protocol") != PHASE9_DEMO_DRY_RUN_PROTOCOL:
        raise ValueError("Phase 9 demo dry-run protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_ORDER_EXPERIMENT_ID:
        raise ValueError("Phase 9 demo dry-run experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_ORDER_DECISION:
        raise ValueError("Phase 9 demo dry-run decision mismatch")
    for field in (
        "demo_design_fingerprint",
        "request_fingerprint",
        "dry_run_fingerprint",
    ):
        _validate_sha256(value.get(field), field=f"Phase 9 dry-run {field}")
    if value.get("validation_result") != "VALIDATED":
        raise ValueError("Phase 9 demo dry-run validation result mismatch")
    for field in (
        "submission_attempted",
        "broker_mutation_attempted",
        "demo_order_submitted",
        "live_order_submitted",
        "real_money_action_attempted",
        "phase10_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 demo dry-run requires {field}=false")
    fingerprint = value["dry_run_fingerprint"]
    payload = dict(value)
    payload.pop("dry_run_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 9 demo dry-run fingerprint mismatch")


def write_phase9_demo_dry_run(
    value: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    validate_phase9_demo_dry_run(value)
    root = Path(out_dir)
    result_path = root / "dry-run.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 9 demo dry-run artifacts already exist")
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(value))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE9_DEMO_DRY_RUN_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_DEMO_ORDER_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_ORDER_DECISION,
        "dry_run_fingerprint": value["dry_run_fingerprint"],
        "submission_attempted": False,
        "broker_mutation_attempted": False,
        "demo_order_submitted": False,
        "live_order_submitted": False,
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


def _normalized_broker_orders(
    rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("Phase 9 broker-order fixture must be an object")
        result.append(
            {
                "broker_order_id": _nonempty_string(
                    row.get("broker_order_id"),
                    field="Phase 9 broker order ID",
                ),
                "client_order_id": _nonempty_string(
                    row.get("client_order_id"),
                    field="Phase 9 broker-order client ID",
                ),
                "protective_stop_id": _optional_identifier(
                    row.get("protective_stop_id"),
                    field="Phase 9 broker-order protective-stop ID",
                ),
            }
        )
    result.sort(
        key=lambda item: (
            str(item["broker_order_id"]),
            str(item["client_order_id"]),
        )
    )
    return result


def _normalized_broker_positions(
    rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("Phase 9 broker-position fixture must be an object")
        result.append(
            {
                "broker_position_id": _nonempty_string(
                    row.get("broker_position_id"),
                    field="Phase 9 broker position ID",
                ),
                "client_order_id": _nonempty_string(
                    row.get("client_order_id"),
                    field="Phase 9 broker-position client ID",
                ),
                "protective_stop_id": _optional_identifier(
                    row.get("protective_stop_id"),
                    field="Phase 9 broker-position protective-stop ID",
                ),
            }
        )
    result.sort(
        key=lambda item: (
            str(item["broker_position_id"]),
            str(item["client_order_id"]),
        )
    )
    return result


def _optional_identifier(value: object, *, field: str) -> str | None:
    if value is None:
        return None
    return _nonempty_string(value, field=field)


def _duplicates(values: Sequence[str]) -> list[str]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return sorted(key for key, count in counts.items() if count > 1)


def build_phase9_demo_reconciliation(
    *,
    design: Mapping[str, object],
    local_requests: Sequence[Mapping[str, object]],
    broker_orders: Sequence[Mapping[str, object]],
    broker_positions: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    execution = _design_execution(design)

    normalized_local: list[dict[str, str]] = []
    local_client_ids: list[str] = []
    for request in local_requests:
        validate_phase9_demo_order_request(request, design=design)
        row = {
            "request_fingerprint": str(request["request_fingerprint"]),
            "client_order_id": str(request["client_order_id"]),
        }
        normalized_local.append(row)
        local_client_ids.append(row["client_order_id"])
    normalized_local.sort(
        key=lambda item: (
            item["client_order_id"],
            item["request_fingerprint"],
        )
    )

    orders = _normalized_broker_orders(broker_orders)
    positions = _normalized_broker_positions(broker_positions)
    local_set = set(local_client_ids)

    duplicate_client_ids = sorted(
        set(_duplicates(local_client_ids))
        | set(
            _duplicates(
                [str(item["client_order_id"]) for item in orders]
            )
        )
        | set(
            _duplicates(
                [str(item["client_order_id"]) for item in positions]
            )
        )
    )
    unknown_order_ids = sorted(
        str(item["broker_order_id"])
        for item in orders
        if item["client_order_id"] not in local_set
    )
    orphan_position_ids = sorted(
        str(item["broker_position_id"])
        for item in positions
        if item["client_order_id"] not in local_set
    )
    missing_stop_ids = sorted(
        {
            str(item["client_order_id"])
            for item in [*orders, *positions]
            if item["client_order_id"] in local_set
            and item["protective_stop_id"] is None
        }
    )

    healthy = not any(
        (
            duplicate_client_ids,
            unknown_order_ids,
            orphan_position_ids,
            missing_stop_ids,
        )
    )
    payload = {
        "protocol": PHASE9_DEMO_RECONCILIATION_PROTOCOL,
        "experiment_id": PHASE9_DEMO_ORDER_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_ORDER_DECISION,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
        "local_requests": normalized_local,
        "broker_orders": orders,
        "broker_positions": positions,
        "duplicate_client_order_ids": duplicate_client_ids,
        "unknown_broker_order_ids": unknown_order_ids,
        "orphan_broker_position_ids": orphan_position_ids,
        "missing_expected_protective_stop_ids": missing_stop_ids,
        "healthy": healthy,
        "broker_read_performed": False,
        "broker_mutation_attempted": False,
        "demo_order_submitted": False,
        "live_order_submitted": False,
        "real_money_action_attempted": False,
        "phase10_authorized": False,
    }
    return payload | {
        "reconciliation_fingerprint": _canonical_digest(payload)
    }


def validate_phase9_demo_reconciliation(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE9_DEMO_RECONCILIATION_PROTOCOL:
        raise ValueError("Phase 9 demo reconciliation protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_ORDER_EXPERIMENT_ID:
        raise ValueError("Phase 9 demo reconciliation experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_ORDER_DECISION:
        raise ValueError("Phase 9 demo reconciliation decision mismatch")
    for field in (
        "demo_design_fingerprint",
        "account_fingerprint",
        "reconciliation_fingerprint",
    ):
        _validate_sha256(
            value.get(field),
            field=f"Phase 9 reconciliation {field}",
        )
    for field in (
        "duplicate_client_order_ids",
        "unknown_broker_order_ids",
        "orphan_broker_position_ids",
        "missing_expected_protective_stop_ids",
    ):
        rows = value.get(field)
        if (
            not isinstance(rows, list)
            or rows != sorted(rows)
            or len(set(rows)) != len(rows)
            or any(not isinstance(item, str) or not item for item in rows)
        ):
            raise ValueError(
                f"Phase 9 reconciliation {field} is malformed"
            )
    discrepancies = any(
        value[field]
        for field in (
            "duplicate_client_order_ids",
            "unknown_broker_order_ids",
            "orphan_broker_position_ids",
            "missing_expected_protective_stop_ids",
        )
    )
    if value.get("healthy") is not (not discrepancies):
        raise ValueError("Phase 9 reconciliation healthy flag mismatch")
    for field in (
        "broker_read_performed",
        "broker_mutation_attempted",
        "demo_order_submitted",
        "live_order_submitted",
        "real_money_action_attempted",
        "phase10_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(
                f"Phase 9 reconciliation requires {field}=false"
            )
    fingerprint = value["reconciliation_fingerprint"]
    payload = dict(value)
    payload.pop("reconciliation_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 9 reconciliation fingerprint mismatch")


@dataclass(frozen=True, slots=True)
class LockedDemoOrderAdapter:
    design: Mapping[str, object]

    def __post_init__(self) -> None:
        _design_execution(self.design)

    def validate_request(
        self,
        request: Mapping[str, object],
    ) -> None:
        validate_phase9_demo_order_request(
            request,
            design=self.design,
        )

    def dry_run(
        self,
        request: Mapping[str, object],
    ) -> dict[str, object]:
        return build_phase9_demo_dry_run(
            design=self.design,
            request=request,
        )

    def reconcile(
        self,
        *,
        local_requests: Sequence[Mapping[str, object]],
        broker_orders: Sequence[Mapping[str, object]],
        broker_positions: Sequence[Mapping[str, object]],
    ) -> dict[str, object]:
        result = build_phase9_demo_reconciliation(
            design=self.design,
            local_requests=local_requests,
            broker_orders=broker_orders,
            broker_positions=broker_positions,
        )
        validate_phase9_demo_reconciliation(result)
        return result

    def submit(
        self,
        request: Mapping[str, object],
    ) -> None:
        self.validate_request(request)
        raise DemoExecutionLockedError(
            "DEC-056 forbids demo execution and broker mutation"
        )


__all__ = [
    "DemoExecutionLockedError",
    "LockedDemoOrderAdapter",
    "PHASE9_DEMO_DRY_RUN_ARTIFACT_PROTOCOL",
    "PHASE9_DEMO_DRY_RUN_PROTOCOL",
    "PHASE9_DEMO_ORDER_DECISION",
    "PHASE9_DEMO_ORDER_EXPERIMENT_ID",
    "PHASE9_DEMO_ORDER_FOUNDATION_PROTOCOL",
    "PHASE9_DEMO_ORDER_PROTOCOL_READY",
    "PHASE9_DEMO_ORDER_REQUEST_PROTOCOL",
    "PHASE9_DEMO_RECONCILIATION_PROTOCOL",
    "build_phase9_demo_dry_run",
    "build_phase9_demo_order_protocol_foundation",
    "build_phase9_demo_order_request",
    "build_phase9_demo_reconciliation",
    "validate_phase9_demo_dry_run",
    "validate_phase9_demo_order_request",
    "validate_phase9_demo_reconciliation",
    "write_phase9_demo_dry_run",
]
