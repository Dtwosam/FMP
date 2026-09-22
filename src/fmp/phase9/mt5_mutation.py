from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping, Sequence

from fmp.phase9.design import validate_phase9_demo_design
from fmp.phase9.mt5_preflight import (
    build_phase9_mt5_order_check,
    build_phase9_mt5_order_check_request,
    validate_phase9_mt5_order_check,
)
from fmp.phase9.protocol import (
    DemoExecutionLockedError,
    validate_phase9_demo_order_request,
)


PHASE9_MT5_MUTATION_DECISION = "DEC-058"
PHASE9_MT5_MUTATION_EXPERIMENT_ID = "EXP-20260922-029"
PHASE9_MT5_MUTATION_SOURCE_PROTOCOL = (
    "fmp-phase9-mt5-demo-mutation-source-v1"
)
PHASE9_MT5_SEND_RESULT_PROTOCOL = "fmp-phase9-mt5-demo-send-result-v1"
PHASE9_MT5_MUTATION_SOURCE_READY = "PHASE9_MT5_MUTATION_SOURCE_READY"

TRADE_RETCODE_DONE = 10009
DEMO_EXECUTION_SOURCE_ARMED = False

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _asdict(value: object, *, label: str) -> dict[str, object]:
    if value is None:
        raise ValueError(f"{label} returned no result")
    if isinstance(value, Mapping):
        return dict(value)
    converter = getattr(value, "_asdict", None)
    if callable(converter):
        result = converter()
        if isinstance(result, Mapping):
            return dict(result)
    raise ValueError(f"{label} result is not mapping-compatible")


def _int(value: object, *, field: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{field} must be an integer >= {minimum}")
    return value


def _finite(
    value: object,
    *,
    field: str,
    allow_zero: bool = True,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    if allow_zero:
        if result < 0:
            raise ValueError(f"{field} must be non-negative")
    elif result <= 0:
        raise ValueError(f"{field} must be positive")
    return result


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _to_utc_string(time_msc: object) -> str:
    value = _int(time_msc, field="MT5 tick time_msc", minimum=1)
    seconds, milliseconds = divmod(value, 1000)
    timestamp = datetime.fromtimestamp(seconds, tz=timezone.utc).replace(
        microsecond=milliseconds * 1000
    )
    return timestamp.isoformat().replace("+00:00", "Z")


def _account_fingerprint(login: object) -> str:
    value = _int(login, field="MT5 account login", minimum=1)
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _constant(module: object, name: str) -> object:
    if not hasattr(module, name):
        raise ValueError(f"MetaTrader5 module is missing {name}")
    return getattr(module, name)


def _translate_request(
    module: object,
    request: Mapping[str, object],
) -> dict[str, object]:
    enum_fields = {
        "action": str(request["action"]),
        "type": str(request["type"]),
        "type_time": str(request["type_time"]),
        "type_filling": str(request["type_filling"]),
    }
    result = {
        key: _constant(module, value)
        for key, value in enum_fields.items()
    }
    for field in (
        "symbol",
        "volume",
        "price",
        "sl",
        "deviation",
        "comment",
    ):
        result[field] = request[field]
    target = request.get("tp")
    result["tp"] = 0.0 if target is None else target
    return result


def _normalize_stop_id(ticket: object, stop: object) -> str | None:
    try:
        price = float(stop)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(price) or price <= 0:
        return None
    identifier = _int(ticket, field="MT5 broker ticket", minimum=1)
    return f"sl:{identifier}:{price:.12g}"


class MetaTrader5PythonDemoBackend:
    """Infrastructure wrapper for an already connected MetaTrader5-like module."""

    __slots__ = ("_mt5",)

    def __init__(self, mt5_module: object) -> None:
        self._mt5 = mt5_module

    def account_snapshot(self) -> dict[str, object]:
        raw = _asdict(self._mt5.account_info(), label="MT5 account_info")
        trade_mode = raw.get("trade_mode")
        demo_mode = _constant(self._mt5, "ACCOUNT_TRADE_MODE_DEMO")
        mode = "DEMO" if trade_mode == demo_mode else "OTHER"
        trade_allowed = bool(raw.get("trade_allowed")) and bool(
            raw.get("trade_expert")
        )
        return {
            "account_mode": mode,
            "account_fingerprint": _account_fingerprint(raw.get("login")),
            "server": _text(raw.get("server"), field="MT5 account server"),
            "trade_allowed": trade_allowed,
        }

    def symbol_snapshot(self, symbol: str) -> dict[str, object]:
        raw = _asdict(
            self._mt5.symbol_info(symbol),
            label="MT5 symbol_info",
        )
        execution_mode = raw.get("trade_exemode")
        market_execution = _constant(
            self._mt5,
            "SYMBOL_TRADE_EXECUTION_MARKET",
        )
        filling_flags = _int(
            raw.get("filling_mode"),
            field="MT5 symbol filling flags",
            minimum=0,
        )
        if execution_mode != market_execution:
            filling_mode = "RETURN"
        elif filling_flags & int(
            _constant(self._mt5, "SYMBOL_FILLING_FOK")
        ):
            filling_mode = "FOK"
        elif filling_flags & int(
            _constant(self._mt5, "SYMBOL_FILLING_IOC")
        ):
            filling_mode = "IOC"
        else:
            raise ValueError(
                "MT5 Market Execution symbol has no supported fill policy"
            )
        trade_disabled = _constant(
            self._mt5,
            "SYMBOL_TRADE_MODE_DISABLED",
        )
        return {
            "symbol": symbol,
            "trade_contract_size": _finite(
                raw.get("trade_contract_size"),
                field="MT5 contract size",
                allow_zero=False,
            ),
            "volume_min": _finite(
                raw.get("volume_min"),
                field="MT5 volume_min",
                allow_zero=False,
            ),
            "volume_step": _finite(
                raw.get("volume_step"),
                field="MT5 volume_step",
                allow_zero=False,
            ),
            "volume_max": _finite(
                raw.get("volume_max"),
                field="MT5 volume_max",
                allow_zero=False,
            ),
            "digits": _int(
                raw.get("digits"),
                field="MT5 symbol digits",
                minimum=0,
            ),
            "point": _finite(
                raw.get("point"),
                field="MT5 point",
                allow_zero=False,
            ),
            "trade_stops_level_points": _int(
                raw.get("trade_stops_level"),
                field="MT5 stop level",
                minimum=0,
            ),
            "filling_mode": filling_mode,
            "trade_enabled": raw.get("trade_mode") != trade_disabled,
        }

    def tick_snapshot(self, symbol: str) -> dict[str, object]:
        raw = _asdict(
            self._mt5.symbol_info_tick(symbol),
            label="MT5 symbol_info_tick",
        )
        return {
            "symbol": symbol,
            "source_time_utc": _to_utc_string(raw.get("time_msc")),
            "bid": _finite(
                raw.get("bid"),
                field="MT5 tick bid",
                allow_zero=False,
            ),
            "ask": _finite(
                raw.get("ask"),
                field="MT5 tick ask",
                allow_zero=False,
            ),
        }

    def order_check(
        self,
        mt5_request: Mapping[str, object],
    ) -> dict[str, object]:
        translated = _translate_request(self._mt5, mt5_request)
        return _asdict(
            self._mt5.order_check(translated),
            label="MT5 order_check",
        )

    def order_send(
        self,
        mt5_request: Mapping[str, object],
    ) -> dict[str, object]:
        translated = _translate_request(self._mt5, mt5_request)
        return _asdict(
            self._mt5.order_send(translated),
            label="MT5 order_send",
        )

    def broker_orders(self) -> list[dict[str, object]]:
        raw_rows = self._mt5.orders_get()
        if raw_rows is None:
            raise ValueError("MT5 orders_get returned no result")
        rows: list[dict[str, object]] = []
        for raw in raw_rows:
            row = _asdict(raw, label="MT5 order")
            ticket = _int(
                row.get("ticket"),
                field="MT5 order ticket",
                minimum=1,
            )
            rows.append(
                {
                    "broker_order_id": str(ticket),
                    "client_order_id": _text(
                        row.get("comment"),
                        field="MT5 order comment",
                    ),
                    "protective_stop_id": _normalize_stop_id(
                        ticket,
                        row.get("sl"),
                    ),
                }
            )
        rows.sort(
            key=lambda item: (
                str(item["broker_order_id"]),
                str(item["client_order_id"]),
            )
        )
        return rows

    def broker_positions(self) -> list[dict[str, object]]:
        raw_rows = self._mt5.positions_get()
        if raw_rows is None:
            raise ValueError("MT5 positions_get returned no result")
        rows: list[dict[str, object]] = []
        for raw in raw_rows:
            row = _asdict(raw, label="MT5 position")
            ticket = _int(
                row.get("ticket"),
                field="MT5 position ticket",
                minimum=1,
            )
            rows.append(
                {
                    "broker_position_id": str(ticket),
                    "client_order_id": _text(
                        row.get("comment"),
                        field="MT5 position comment",
                    ),
                    "protective_stop_id": _normalize_stop_id(
                        ticket,
                        row.get("sl"),
                    ),
                }
            )
        rows.sort(
            key=lambda item: (
                str(item["broker_position_id"]),
                str(item["client_order_id"]),
            )
        )
        return rows


def build_phase9_mt5_mutation_source_foundation(
    *,
    design: Mapping[str, object],
    code_commit: str,
) -> dict[str, object]:
    validate_phase9_demo_design(design)
    commit = _commit(
        code_commit,
        field="Phase 9 MT5 mutation-source code commit",
    )
    payload = {
        "protocol": PHASE9_MT5_MUTATION_SOURCE_PROTOCOL,
        "experiment_id": PHASE9_MT5_MUTATION_EXPERIMENT_ID,
        "decision": PHASE9_MT5_MUTATION_DECISION,
        "outcome": PHASE9_MT5_MUTATION_SOURCE_READY,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "mt5_mutation_source_code_commit": commit,
        "mt5_mutation_source_ready": True,
        "demo_execution_source_armed": DEMO_EXECUTION_SOURCE_ARMED,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    return payload | {
        "mt5_mutation_source_fingerprint": _digest(payload)
    }


def build_phase9_mt5_send_result(
    *,
    request_fingerprint: str,
    order_check_request_fingerprint: str,
    order_check_fingerprint: str,
    expected_volume_lots: float,
    raw_result: Mapping[str, object],
) -> dict[str, object]:
    request_fp = _sha256(
        request_fingerprint,
        field="Phase 9 request fingerprint",
    )
    check_request_fp = _sha256(
        order_check_request_fingerprint,
        field="Phase 9 order-check request fingerprint",
    )
    check_fp = _sha256(
        order_check_fingerprint,
        field="Phase 9 order-check fingerprint",
    )
    expected = _finite(
        expected_volume_lots,
        field="Phase 9 expected volume",
        allow_zero=False,
    )
    retcode = _int(
        raw_result.get("retcode"),
        field="MT5 order_send retcode",
        minimum=0,
    )
    confirmed_volume = _finite(
        raw_result.get("volume", 0.0),
        field="MT5 confirmed volume",
        allow_zero=True,
    )
    full_volume = Decimal(str(confirmed_volume)) == Decimal(str(expected))
    payload = {
        "protocol": PHASE9_MT5_SEND_RESULT_PROTOCOL,
        "experiment_id": PHASE9_MT5_MUTATION_EXPERIMENT_ID,
        "decision": PHASE9_MT5_MUTATION_DECISION,
        "request_fingerprint": request_fp,
        "order_check_request_fingerprint": check_request_fp,
        "order_check_fingerprint": check_fp,
        "retcode": retcode,
        "retcode_external": _int(
            raw_result.get("retcode_external", 0),
            field="MT5 external retcode",
            minimum=0,
        ),
        "deal_ticket": _int(
            raw_result.get("deal", 0),
            field="MT5 deal ticket",
            minimum=0,
        ),
        "order_ticket": _int(
            raw_result.get("order", 0),
            field="MT5 order ticket",
            minimum=0,
        ),
        "confirmed_volume_lots": confirmed_volume,
        "expected_volume_lots": expected,
        "full_volume_confirmed": full_volume,
        "confirmed_price": _finite(
            raw_result.get("price", 0.0),
            field="MT5 confirmed price",
            allow_zero=True,
        ),
        "returned_bid": _finite(
            raw_result.get("bid", 0.0),
            field="MT5 returned bid",
            allow_zero=True,
        ),
        "returned_ask": _finite(
            raw_result.get("ask", 0.0),
            field="MT5 returned ask",
            allow_zero=True,
        ),
        "comment": str(raw_result.get("comment", "")),
        "request_id": _int(
            raw_result.get("request_id", 0),
            field="MT5 request ID",
            minimum=0,
        ),
        "completed": retcode == TRADE_RETCODE_DONE and full_volume,
    }
    return payload | {"send_result_fingerprint": _digest(payload)}


def validate_phase9_mt5_send_result(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE9_MT5_SEND_RESULT_PROTOCOL:
        raise ValueError("Phase 9 MT5 send-result protocol mismatch")
    if value.get("experiment_id") != PHASE9_MT5_MUTATION_EXPERIMENT_ID:
        raise ValueError("Phase 9 MT5 send-result experiment mismatch")
    if value.get("decision") != PHASE9_MT5_MUTATION_DECISION:
        raise ValueError("Phase 9 MT5 send-result decision mismatch")
    for field in (
        "request_fingerprint",
        "order_check_request_fingerprint",
        "order_check_fingerprint",
        "send_result_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 MT5 send result {field}")
    retcode = _int(
        value.get("retcode"),
        field="Phase 9 MT5 send-result retcode",
        minimum=0,
    )
    full_volume = value.get("full_volume_confirmed")
    if not isinstance(full_volume, bool):
        raise ValueError("Phase 9 MT5 full-volume flag is malformed")
    if value.get("completed") is not (
        retcode == TRADE_RETCODE_DONE and full_volume
    ):
        raise ValueError("Phase 9 MT5 completed flag mismatch")
    fingerprint = value["send_result_fingerprint"]
    payload = dict(value)
    payload.pop("send_result_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 MT5 send-result fingerprint mismatch")


@dataclass(frozen=True, slots=True)
class GatedMT5DemoMutationAdapter:
    design: Mapping[str, object]
    backend: Any

    def __post_init__(self) -> None:
        validate_phase9_demo_design(self.design)

    def submit(
        self,
        request: Mapping[str, object],
    ) -> dict[str, object]:
        if DEMO_EXECUTION_SOURCE_ARMED is not True:
            raise DemoExecutionLockedError(
                "DEC-058 keeps demo execution source unarmed"
            )

        validate_phase9_demo_order_request(
            request,
            design=self.design,
        )
        symbol = str(request["broker_symbol"])
        account = self.backend.account_snapshot()
        symbol_snapshot = self.backend.symbol_snapshot(symbol)
        tick = self.backend.tick_snapshot(symbol)
        check_request = build_phase9_mt5_order_check_request(
            design=self.design,
            request=request,
            account_snapshot=account,
            symbol_snapshot=symbol_snapshot,
            tick_snapshot=tick,
        )
        raw_check = self.backend.order_check(
            check_request["mt5_request"]
        )
        check = build_phase9_mt5_order_check(
            order_check_request=check_request,
            raw_result=raw_check,
        )
        validate_phase9_mt5_order_check(check)
        if check["check_passed"] is not True:
            raise ValueError(
                f"MT5 order_check failed with retcode {check['retcode']}"
            )
        raw_result = self.backend.order_send(
            check_request["mt5_request"]
        )
        result = build_phase9_mt5_send_result(
            request_fingerprint=str(request["request_fingerprint"]),
            order_check_request_fingerprint=str(
                check_request["order_check_request_fingerprint"]
            ),
            order_check_fingerprint=str(check["order_check_fingerprint"]),
            expected_volume_lots=float(check_request["volume_lots"]),
            raw_result=raw_result,
        )
        validate_phase9_mt5_send_result(result)
        return result


__all__ = [
    "DEMO_EXECUTION_SOURCE_ARMED",
    "GatedMT5DemoMutationAdapter",
    "MetaTrader5PythonDemoBackend",
    "PHASE9_MT5_MUTATION_DECISION",
    "PHASE9_MT5_MUTATION_EXPERIMENT_ID",
    "PHASE9_MT5_MUTATION_SOURCE_PROTOCOL",
    "PHASE9_MT5_MUTATION_SOURCE_READY",
    "PHASE9_MT5_SEND_RESULT_PROTOCOL",
    "TRADE_RETCODE_DONE",
    "build_phase9_mt5_mutation_source_foundation",
    "build_phase9_mt5_send_result",
    "validate_phase9_mt5_send_result",
]
