from __future__ import annotations

import hashlib
import json
import math
import os
import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Mapping, Protocol

from fmp.phase9.design import validate_phase9_demo_design
from fmp.phase9.protocol import validate_phase9_demo_order_request


PHASE9_MT5_PREFLIGHT_DECISION = "DEC-057"
PHASE9_MT5_PREFLIGHT_EXPERIMENT_ID = "EXP-20260922-028"
PHASE9_MT5_DEMO_PREFLIGHT_PROTOCOL = "fmp-phase9-mt5-demo-preflight-v1"
PHASE9_MT5_ORDER_CHECK_REQUEST_PROTOCOL = (
    "fmp-phase9-mt5-demo-order-check-request-v1"
)
PHASE9_MT5_ORDER_CHECK_PROTOCOL = "fmp-phase9-mt5-demo-order-check-v1"
PHASE9_MT5_PREFLIGHT_ARTIFACT_PROTOCOL = (
    "fmp-phase9-mt5-demo-preflight-artifacts-v1"
)
PHASE9_MT5_DEMO_PREFLIGHT_READY = "PHASE9_MT5_DEMO_PREFLIGHT_READY"

ORDER_CHECK_SUCCESS_RETCODE = 0
FILLING_MODES = frozenset({"FOK", "IOC", "RETURN"})
UTC_SUFFIX = "Z"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class MT5DemoCheckBackend(Protocol):
    def account_snapshot(self) -> Mapping[str, object]: ...

    def symbol_snapshot(self, symbol: str) -> Mapping[str, object]: ...

    def tick_snapshot(self, symbol: str) -> Mapping[str, object]: ...

    def order_check(
        self,
        mt5_request: Mapping[str, object],
    ) -> Mapping[str, object]: ...


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
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


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _bool(value: object, *, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be boolean")
    return value


def _number(
    value: object,
    *,
    field: str,
    positive: bool = True,
    allow_zero: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    if positive and result <= 0:
        if not (allow_zero and result == 0):
            raise ValueError(f"{field} must be positive")
    return result


def _int(
    value: object,
    *,
    field: str,
    minimum: int = 0,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{field} must be an integer >= {minimum}")
    return value


def _decimal(value: object, *, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"{field} must be decimal-compatible")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} is invalid") from exc
    if not result.is_finite():
        raise ValueError(f"{field} must be finite")
    return result


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith(UTC_SUFFIX):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")
    return parsed


def _validate_account(
    account: Mapping[str, object],
    *,
    design: Mapping[str, object],
) -> dict[str, object]:
    execution = design["execution_path"]
    assert isinstance(execution, Mapping)
    result = {
        "account_mode": _text(
            account.get("account_mode"),
            field="MT5 account mode",
        ),
        "account_fingerprint": _sha256(
            account.get("account_fingerprint"),
            field="MT5 account fingerprint",
        ),
        "server": _text(account.get("server"), field="MT5 server"),
        "trade_allowed": _bool(
            account.get("trade_allowed"),
            field="MT5 account trade_allowed",
        ),
    }
    if result["account_mode"] != "DEMO":
        raise ValueError("DEC-057 requires a DEMO account")
    if result["account_fingerprint"] != execution.get("account_fingerprint"):
        raise ValueError("MT5 account fingerprint does not match design")
    if result["server"] != execution.get("server"):
        raise ValueError("MT5 server does not match design")
    if result["trade_allowed"] is not True:
        raise ValueError("MT5 account trading is disabled")
    return result


def _validate_symbol(
    snapshot: Mapping[str, object],
    *,
    symbol: str,
) -> dict[str, object]:
    result = {
        "symbol": _text(snapshot.get("symbol"), field="MT5 symbol"),
        "trade_contract_size": _number(
            snapshot.get("trade_contract_size"),
            field="MT5 trade contract size",
        ),
        "volume_min": _number(
            snapshot.get("volume_min"),
            field="MT5 volume minimum",
        ),
        "volume_step": _number(
            snapshot.get("volume_step"),
            field="MT5 volume step",
        ),
        "volume_max": _number(
            snapshot.get("volume_max"),
            field="MT5 volume maximum",
        ),
        "digits": _int(snapshot.get("digits"), field="MT5 digits", minimum=0),
        "point": _number(snapshot.get("point"), field="MT5 point"),
        "trade_stops_level_points": _number(
            snapshot.get("trade_stops_level_points"),
            field="MT5 stops level",
            allow_zero=True,
        ),
        "filling_mode": _text(
            snapshot.get("filling_mode"),
            field="MT5 filling mode",
        ),
        "trade_enabled": _bool(
            snapshot.get("trade_enabled"),
            field="MT5 trade_enabled",
        ),
    }
    if result["symbol"] != symbol:
        raise ValueError("MT5 symbol snapshot identity mismatch")
    if result["volume_min"] > result["volume_max"]:
        raise ValueError("MT5 volume minimum exceeds maximum")
    if result["filling_mode"] not in FILLING_MODES:
        raise ValueError("MT5 filling mode is unsupported")
    if result["trade_enabled"] is not True:
        raise ValueError("MT5 symbol trading is disabled")
    return result


def _validate_tick(
    snapshot: Mapping[str, object],
    *,
    symbol: str,
) -> dict[str, object]:
    tick_symbol = _text(snapshot.get("symbol"), field="MT5 tick symbol")
    if tick_symbol != symbol:
        raise ValueError("MT5 tick symbol identity mismatch")
    source = _text(
        snapshot.get("source_time_utc"),
        field="MT5 tick source time",
    )
    _parse_utc(source, field="MT5 tick source time")
    bid = _number(snapshot.get("bid"), field="MT5 tick bid")
    ask = _number(snapshot.get("ask"), field="MT5 tick ask")
    if ask < bid:
        raise ValueError("MT5 tick is crossed")
    return {
        "symbol": tick_symbol,
        "source_time_utc": source,
        "bid": bid,
        "ask": ask,
    }


def _exact_volume(
    *,
    units: int,
    symbol_snapshot: Mapping[str, object],
) -> Decimal:
    contract = _decimal(
        symbol_snapshot["trade_contract_size"],
        field="MT5 trade contract size",
    )
    raw = Decimal(units) / contract
    minimum = _decimal(
        symbol_snapshot["volume_min"],
        field="MT5 volume minimum",
    )
    maximum = _decimal(
        symbol_snapshot["volume_max"],
        field="MT5 volume maximum",
    )
    step = _decimal(
        symbol_snapshot["volume_step"],
        field="MT5 volume step",
    )
    if raw < minimum or raw > maximum:
        raise ValueError("Phase 9 units are outside MT5 volume bounds")
    steps = (raw - minimum) / step
    if steps != steps.to_integral_value():
        raise ValueError(
            "Phase 9 units are not exactly representable on MT5 volume grid"
        )
    return raw


def _on_grid(
    value: object,
    *,
    point: object,
    field: str,
) -> None:
    raw = _decimal(value, field=field)
    grid = _decimal(point, field="MT5 point")
    quotient = raw / grid
    if quotient != quotient.to_integral_value():
        raise ValueError(f"{field} is not exactly representable on MT5 price grid")


def build_phase9_mt5_order_check_request(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    account_snapshot: Mapping[str, object],
    symbol_snapshot: Mapping[str, object],
    tick_snapshot: Mapping[str, object],
) -> dict[str, object]:
    validate_phase9_demo_design(design)
    validate_phase9_demo_order_request(request, design=design)
    account = _validate_account(account_snapshot, design=design)
    symbol = str(request["broker_symbol"])
    execution = design["execution_path"]
    assert isinstance(execution, Mapping)
    mapping = execution.get("symbol_mapping")
    if not isinstance(mapping, Mapping) or mapping.get(request["symbol"]) != symbol:
        raise ValueError("MT5 broker symbol mapping mismatch")
    normalized_symbol = _validate_symbol(symbol_snapshot, symbol=symbol)
    tick = _validate_tick(tick_snapshot, symbol=symbol)

    raw_units = request.get("units")
    if isinstance(raw_units, bool) or not isinstance(raw_units, int) or raw_units <= 0:
        raise ValueError("Phase 9 request units are invalid")
    volume = _exact_volume(
        units=raw_units,
        symbol_snapshot=normalized_symbol,
    )
    side = "BUY" if request["direction"] == "LONG" else "SELL"
    price = tick["ask"] if side == "BUY" else tick["bid"]
    stop = _number(request.get("stop_price"), field="Phase 9 stop price")
    target_raw = request.get("target_price")
    target = (
        None
        if target_raw is None
        else _number(target_raw, field="Phase 9 target price")
    )
    point = normalized_symbol["point"]
    _on_grid(price, point=point, field="MT5 requested market price")
    _on_grid(stop, point=point, field="MT5 protective stop")
    if target is not None:
        _on_grid(target, point=point, field="MT5 target")

    minimum_distance = (
        float(normalized_symbol["trade_stops_level_points"])
        * float(normalized_symbol["point"])
    )
    if side == "BUY":
        if stop >= price:
            raise ValueError("MT5 BUY stop must be below current ask")
        if price - stop + 1e-15 < minimum_distance:
            raise ValueError("MT5 BUY stop violates minimum stop distance")
        if target is not None and target <= price:
            raise ValueError("MT5 BUY target must be above current ask")
    else:
        if stop <= price:
            raise ValueError("MT5 SELL stop must be above current bid")
        if stop - price + 1e-15 < minimum_distance:
            raise ValueError("MT5 SELL stop violates minimum stop distance")
        if target is not None and target >= price:
            raise ValueError("MT5 SELL target must be below current bid")

    mt5_request = {
        "action": "TRADE_ACTION_DEAL",
        "symbol": symbol,
        "volume": float(volume),
        "type": f"ORDER_TYPE_{side}",
        "price": price,
        "sl": stop,
        "tp": target,
        "deviation": 0,
        "type_time": "ORDER_TIME_GTC",
        "type_filling": f"ORDER_FILLING_{normalized_symbol['filling_mode']}",
        "comment": str(request["client_order_id"]),
    }
    payload = {
        "protocol": PHASE9_MT5_ORDER_CHECK_REQUEST_PROTOCOL,
        "experiment_id": PHASE9_MT5_PREFLIGHT_EXPERIMENT_ID,
        "decision": PHASE9_MT5_PREFLIGHT_DECISION,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "account": account,
        "symbol_snapshot": normalized_symbol,
        "tick_snapshot": tick,
        "side": side,
        "volume_lots": float(volume),
        "minimum_stop_distance": minimum_distance,
        "mt5_request": mt5_request,
        "order_send_attempted": False,
        "broker_mutation_attempted": False,
        "demo_order_submitted": False,
        "live_order_submitted": False,
        "real_money_action_attempted": False,
        "phase10_authorized": False,
    }
    return payload | {
        "order_check_request_fingerprint": _digest(payload)
    }


def validate_phase9_mt5_order_check_request(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE9_MT5_ORDER_CHECK_REQUEST_PROTOCOL:
        raise ValueError("Phase 9 MT5 order-check request protocol mismatch")
    if value.get("experiment_id") != PHASE9_MT5_PREFLIGHT_EXPERIMENT_ID:
        raise ValueError("Phase 9 MT5 order-check request experiment mismatch")
    if value.get("decision") != PHASE9_MT5_PREFLIGHT_DECISION:
        raise ValueError("Phase 9 MT5 order-check request decision mismatch")
    for field in (
        "demo_design_fingerprint",
        "request_fingerprint",
        "order_check_request_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 MT5 {field}")
    if value.get("side") not in {"BUY", "SELL"}:
        raise ValueError("Phase 9 MT5 side is invalid")
    mt5_request = value.get("mt5_request")
    if not isinstance(mt5_request, Mapping):
        raise ValueError("Phase 9 MT5 request is malformed")
    if mt5_request.get("action") != "TRADE_ACTION_DEAL":
        raise ValueError("Phase 9 MT5 action mismatch")
    if mt5_request.get("type_time") != "ORDER_TIME_GTC":
        raise ValueError("Phase 9 MT5 time-in-force mismatch")
    if mt5_request.get("deviation") != 0:
        raise ValueError("Phase 9 MT5 check-only deviation must be zero")
    if mt5_request.get("type") != f"ORDER_TYPE_{value['side']}":
        raise ValueError("Phase 9 MT5 order side mismatch")
    for field in (
        "order_send_attempted",
        "broker_mutation_attempted",
        "demo_order_submitted",
        "live_order_submitted",
        "real_money_action_attempted",
        "phase10_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 MT5 request requires {field}=false")
    fingerprint = value["order_check_request_fingerprint"]
    payload = dict(value)
    payload.pop("order_check_request_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 MT5 order-check request fingerprint mismatch")


def build_phase9_mt5_order_check(
    *,
    order_check_request: Mapping[str, object],
    raw_result: Mapping[str, object],
) -> dict[str, object]:
    validate_phase9_mt5_order_check_request(order_check_request)
    retcode = _int(
        raw_result.get("retcode"),
        field="MT5 order-check retcode",
        minimum=0,
    )
    comment = str(raw_result.get("comment", ""))
    financial: dict[str, float | None] = {}
    for field in (
        "balance",
        "equity",
        "profit",
        "margin",
        "margin_free",
        "margin_level",
    ):
        raw = raw_result.get(field)
        if raw is None:
            financial[field] = None
            continue
        financial[field] = _number(
            raw,
            field=f"MT5 order-check {field}",
            positive=False,
        )
    payload = {
        "protocol": PHASE9_MT5_ORDER_CHECK_PROTOCOL,
        "experiment_id": PHASE9_MT5_PREFLIGHT_EXPERIMENT_ID,
        "decision": PHASE9_MT5_PREFLIGHT_DECISION,
        "order_check_request_fingerprint": order_check_request[
            "order_check_request_fingerprint"
        ],
        "retcode": retcode,
        "comment": comment,
        **financial,
        "check_passed": retcode == ORDER_CHECK_SUCCESS_RETCODE,
        "order_send_attempted": False,
        "broker_mutation_attempted": False,
        "demo_order_submitted": False,
        "live_order_submitted": False,
        "real_money_action_attempted": False,
        "phase10_authorized": False,
    }
    return payload | {"order_check_fingerprint": _digest(payload)}


def validate_phase9_mt5_order_check(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE9_MT5_ORDER_CHECK_PROTOCOL:
        raise ValueError("Phase 9 MT5 order-check protocol mismatch")
    if value.get("experiment_id") != PHASE9_MT5_PREFLIGHT_EXPERIMENT_ID:
        raise ValueError("Phase 9 MT5 order-check experiment mismatch")
    _sha256(
        value.get("order_check_request_fingerprint"),
        field="Phase 9 MT5 order-check request fingerprint",
    )
    fingerprint = _sha256(
        value.get("order_check_fingerprint"),
        field="Phase 9 MT5 order-check fingerprint",
    )
    retcode = _int(
        value.get("retcode"),
        field="Phase 9 MT5 order-check retcode",
        minimum=0,
    )
    if value.get("check_passed") is not (retcode == ORDER_CHECK_SUCCESS_RETCODE):
        raise ValueError("Phase 9 MT5 order-check pass flag mismatch")
    for field in (
        "order_send_attempted",
        "broker_mutation_attempted",
        "demo_order_submitted",
        "live_order_submitted",
        "real_money_action_attempted",
        "phase10_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 MT5 order-check requires {field}=false")
    payload = dict(value)
    payload.pop("order_check_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 MT5 order-check fingerprint mismatch")


def run_phase9_mt5_demo_preflight(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    backend: MT5DemoCheckBackend,
    code_commit: str,
) -> dict[str, object]:
    validate_phase9_demo_design(design)
    validate_phase9_demo_order_request(request, design=design)
    commit = _commit(
        code_commit,
        field="Phase 9 MT5 preflight code commit",
    )
    symbol = str(request["broker_symbol"])
    account = backend.account_snapshot()
    symbol_snapshot = backend.symbol_snapshot(symbol)
    tick = backend.tick_snapshot(symbol)
    check_request = build_phase9_mt5_order_check_request(
        design=design,
        request=request,
        account_snapshot=account,
        symbol_snapshot=symbol_snapshot,
        tick_snapshot=tick,
    )
    raw_check = backend.order_check(check_request["mt5_request"])
    check = build_phase9_mt5_order_check(
        order_check_request=check_request,
        raw_result=raw_check,
    )
    validate_phase9_mt5_order_check(check)
    if check["check_passed"] is not True:
        raise ValueError(
            f"MT5 order_check failed with retcode {check['retcode']}"
        )

    payload = {
        "protocol": PHASE9_MT5_DEMO_PREFLIGHT_PROTOCOL,
        "experiment_id": PHASE9_MT5_PREFLIGHT_EXPERIMENT_ID,
        "decision": PHASE9_MT5_PREFLIGHT_DECISION,
        "outcome": PHASE9_MT5_DEMO_PREFLIGHT_READY,
        "mt5_preflight_code_commit": commit,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "order_check_request_fingerprint": check_request[
            "order_check_request_fingerprint"
        ],
        "order_check_fingerprint": check["order_check_fingerprint"],
        "account": check_request["account"],
        "symbol_snapshot": check_request["symbol_snapshot"],
        "tick_snapshot": check_request["tick_snapshot"],
        "side": check_request["side"],
        "volume_lots": check_request["volume_lots"],
        "minimum_stop_distance": check_request["minimum_stop_distance"],
        "check_passed": True,
        "mt5_demo_preflight_source_ready": True,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {"mt5_preflight_fingerprint": _digest(payload)}
    validate_phase9_mt5_demo_preflight(result)
    return result


def validate_phase9_mt5_demo_preflight(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE9_MT5_DEMO_PREFLIGHT_PROTOCOL:
        raise ValueError("Phase 9 MT5 demo-preflight protocol mismatch")
    if value.get("experiment_id") != PHASE9_MT5_PREFLIGHT_EXPERIMENT_ID:
        raise ValueError("Phase 9 MT5 demo-preflight experiment mismatch")
    if value.get("decision") != PHASE9_MT5_PREFLIGHT_DECISION:
        raise ValueError("Phase 9 MT5 demo-preflight decision mismatch")
    if value.get("outcome") != PHASE9_MT5_DEMO_PREFLIGHT_READY:
        raise ValueError("Phase 9 MT5 demo-preflight outcome mismatch")
    _commit(
        value.get("mt5_preflight_code_commit"),
        field="Phase 9 MT5 preflight code commit",
    )
    for field in (
        "demo_design_fingerprint",
        "request_fingerprint",
        "order_check_request_fingerprint",
        "order_check_fingerprint",
        "mt5_preflight_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 MT5 preflight {field}")
    if value.get("check_passed") is not True:
        raise ValueError("Phase 9 MT5 demo-preflight requires passing order_check")
    if value.get("mt5_demo_preflight_source_ready") is not True:
        raise ValueError("Phase 9 MT5 demo-preflight source is not ready")
    for field in (
        "demo_execution_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase10_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 MT5 preflight requires {field}=false")
    fingerprint = value["mt5_preflight_fingerprint"]
    payload = dict(value)
    payload.pop("mt5_preflight_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 MT5 demo-preflight fingerprint mismatch")


def write_phase9_mt5_demo_preflight(
    value: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    validate_phase9_mt5_demo_preflight(value)
    root = Path(out_dir)
    result_path = root / "preflight.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 9 MT5 preflight artifacts already exist")
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(value))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE9_MT5_PREFLIGHT_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_MT5_PREFLIGHT_EXPERIMENT_ID,
        "decision": PHASE9_MT5_PREFLIGHT_DECISION,
        "outcome": PHASE9_MT5_DEMO_PREFLIGHT_READY,
        "mt5_preflight_fingerprint": value["mt5_preflight_fingerprint"],
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
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
    "FILLING_MODES",
    "MT5DemoCheckBackend",
    "ORDER_CHECK_SUCCESS_RETCODE",
    "PHASE9_MT5_DEMO_PREFLIGHT_PROTOCOL",
    "PHASE9_MT5_DEMO_PREFLIGHT_READY",
    "PHASE9_MT5_ORDER_CHECK_PROTOCOL",
    "PHASE9_MT5_ORDER_CHECK_REQUEST_PROTOCOL",
    "PHASE9_MT5_PREFLIGHT_ARTIFACT_PROTOCOL",
    "PHASE9_MT5_PREFLIGHT_DECISION",
    "PHASE9_MT5_PREFLIGHT_EXPERIMENT_ID",
    "build_phase9_mt5_order_check",
    "build_phase9_mt5_order_check_request",
    "run_phase9_mt5_demo_preflight",
    "validate_phase9_mt5_demo_preflight",
    "validate_phase9_mt5_order_check",
    "validate_phase9_mt5_order_check_request",
    "write_phase9_mt5_demo_preflight",
]
