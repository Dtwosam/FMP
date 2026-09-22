from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TypeAlias

from .design import (
    BRIDGE_FILE_BY_SYMBOL,
    MT5_ALLOWED_SERVERS,
    MT5_BRIDGE_PROTOCOL,
    SUPPORTED_SYMBOLS,
)


UTC = timezone.utc
_COMMON_FIELDS = frozenset(
    {
        "record_type",
        "protocol",
        "bridge_session_id",
        "symbol",
        "server",
        "account_fingerprint",
    }
)
_START_FIELDS = _COMMON_FIELDS | frozenset({"account_mode", "bridge_start_time_msc"})
_TICK_FIELDS = _COMMON_FIELDS | frozenset({"source_time_msc", "bid", "ask", "flags"})
_HEARTBEAT_FIELDS = _COMMON_FIELDS | frozenset(
    {"bridge_emitted_time_msc", "last_tick_time_msc"}
)
_HEX = frozenset("0123456789abcdef")


class Phase8BBridgeProtocolError(ValueError):
    """Fail-closed error for malformed Phase 8B bridge data."""


@dataclass(frozen=True, slots=True)
class Phase8BBridgeStartRecord:
    protocol: str
    bridge_session_id: str
    symbol: str
    server: str
    account_fingerprint: str
    account_mode: str
    bridge_start_time_msc: int
    record_type: str = "BRIDGE_START"


@dataclass(frozen=True, slots=True)
class Phase8BBridgeTickRecord:
    protocol: str
    bridge_session_id: str
    symbol: str
    server: str
    account_fingerprint: str
    source_time_msc: int
    bid: float
    ask: float
    flags: int
    record_type: str = "TICK"


@dataclass(frozen=True, slots=True)
class Phase8BBridgeHeartbeatRecord:
    protocol: str
    bridge_session_id: str
    symbol: str
    server: str
    account_fingerprint: str
    bridge_emitted_time_msc: int
    last_tick_time_msc: int | None
    record_type: str = "BRIDGE_HEARTBEAT"


Phase8BBridgeRecord: TypeAlias = (
    Phase8BBridgeStartRecord
    | Phase8BBridgeTickRecord
    | Phase8BBridgeHeartbeatRecord
)


@dataclass(frozen=True, slots=True)
class Phase8BQuote:
    source_time_utc: datetime
    received_at_utc: datetime
    receive_monotonic_ns: int
    symbol: str
    bid: float
    ask: float
    tradeable: bool = True

    def __post_init__(self) -> None:
        for field, value in (
            ("source_time_utc", self.source_time_utc),
            ("received_at_utc", self.received_at_utc),
        ):
            if (
                not isinstance(value, datetime)
                or value.tzinfo is None
                or value.utcoffset() != timedelta(0)
            ):
                raise ValueError(f"{field} must use UTC")
        if (
            isinstance(self.receive_monotonic_ns, bool)
            or not isinstance(self.receive_monotonic_ns, int)
            or self.receive_monotonic_ns < 0
        ):
            raise ValueError("receive_monotonic_ns must be a non-negative integer")
        if self.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError("unsupported Phase 8B quote symbol")
        for field, value in (("bid", self.bid), ("ask", self.ask)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{field} must be numeric")
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{field} must be finite and positive")
        if self.bid > self.ask:
            raise ValueError("bid must not exceed ask")
        if type(self.tradeable) is not bool:
            raise TypeError("tradeable must be bool")


def _require_lower_hex(value: object, *, field: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in _HEX for character in value)
    ):
        raise Phase8BBridgeProtocolError(f"bridge {field} is invalid")
    return value


def _require_int(value: object, *, field: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise Phase8BBridgeProtocolError(f"bridge {field} is invalid")
    return value


def _require_optional_positive_int(
    value: object,
    *,
    field: str,
) -> int | None:
    if value is None:
        return None
    return _require_int(value, field=field, minimum=1)


def _require_price(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Phase8BBridgeProtocolError(f"bridge {field} is invalid")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise Phase8BBridgeProtocolError(f"bridge {field} is invalid")
    return result


def _validate_common(
    raw: dict[str, object],
) -> tuple[str, str, str, str, str]:
    protocol = raw.get("protocol")
    if protocol != MT5_BRIDGE_PROTOCOL:
        raise Phase8BBridgeProtocolError("bridge protocol is invalid")
    symbol = raw.get("symbol")
    if not isinstance(symbol, str) or symbol not in SUPPORTED_SYMBOLS:
        raise Phase8BBridgeProtocolError("bridge symbol is invalid")
    server = raw.get("server")
    if not isinstance(server, str) or server not in MT5_ALLOWED_SERVERS:
        raise Phase8BBridgeProtocolError("bridge server is invalid")
    bridge_session_id = _require_lower_hex(
        raw.get("bridge_session_id"),
        field="bridge_session_id",
    )
    account_fingerprint = _require_lower_hex(
        raw.get("account_fingerprint"),
        field="account_fingerprint",
    )
    return (
        protocol,
        bridge_session_id,
        symbol,
        server,
        account_fingerprint,
    )


def parse_phase8b_bridge_line(line: bytes) -> Phase8BBridgeRecord:
    if not isinstance(line, bytes):
        raise TypeError("bridge line must be bytes")
    if not line or not line.endswith(b"\n"):
        raise Phase8BBridgeProtocolError(
            "bridge record must be a complete newline-terminated line"
        )
    try:
        raw = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise Phase8BBridgeProtocolError("bridge record is invalid JSON") from None
    if not isinstance(raw, dict):
        raise Phase8BBridgeProtocolError("bridge record must be an object")

    record_type = raw.get("record_type")
    if record_type == "BRIDGE_START":
        expected = _START_FIELDS
    elif record_type == "TICK":
        expected = _TICK_FIELDS
    elif record_type == "BRIDGE_HEARTBEAT":
        expected = _HEARTBEAT_FIELDS
    else:
        raise Phase8BBridgeProtocolError("bridge record type is invalid")
    if frozenset(raw) != expected:
        raise Phase8BBridgeProtocolError("bridge record fields are invalid")

    protocol, session, symbol, server, account = _validate_common(raw)
    if record_type == "BRIDGE_START":
        if raw.get("account_mode") != "DEMO":
            raise Phase8BBridgeProtocolError("bridge account mode is invalid")
        return Phase8BBridgeStartRecord(
            protocol=protocol,
            bridge_session_id=session,
            symbol=symbol,
            server=server,
            account_fingerprint=account,
            account_mode="DEMO",
            bridge_start_time_msc=_require_int(
                raw.get("bridge_start_time_msc"),
                field="bridge_start_time_msc",
                minimum=1,
            ),
        )
    if record_type == "TICK":
        bid = _require_price(raw.get("bid"), field="bid")
        ask = _require_price(raw.get("ask"), field="ask")
        if bid > ask:
            raise Phase8BBridgeProtocolError("bridge quote is crossed")
        return Phase8BBridgeTickRecord(
            protocol=protocol,
            bridge_session_id=session,
            symbol=symbol,
            server=server,
            account_fingerprint=account,
            source_time_msc=_require_int(
                raw.get("source_time_msc"),
                field="source_time_msc",
                minimum=1,
            ),
            bid=bid,
            ask=ask,
            flags=_require_int(raw.get("flags"), field="flags", minimum=0),
        )
    return Phase8BBridgeHeartbeatRecord(
        protocol=protocol,
        bridge_session_id=session,
        symbol=symbol,
        server=server,
        account_fingerprint=account,
        bridge_emitted_time_msc=_require_int(
            raw.get("bridge_emitted_time_msc"),
            field="bridge_emitted_time_msc",
            minimum=1,
        ),
        last_tick_time_msc=_require_optional_positive_int(
            raw.get("last_tick_time_msc"),
            field="last_tick_time_msc",
        ),
    )


def _validate_receive_metadata(
    received_at_utc: datetime,
    receive_monotonic_ns: int,
) -> None:
    if (
        not isinstance(received_at_utc, datetime)
        or received_at_utc.tzinfo is None
        or received_at_utc.utcoffset() != timedelta(0)
    ):
        raise Phase8BBridgeProtocolError("bridge receive time must use UTC")
    if (
        isinstance(receive_monotonic_ns, bool)
        or not isinstance(receive_monotonic_ns, int)
        or receive_monotonic_ns < 0
    ):
        raise Phase8BBridgeProtocolError("bridge monotonic receive time is invalid")


def _utc_from_milliseconds(value: int) -> datetime:
    seconds, milliseconds = divmod(value, 1000)
    try:
        return datetime.fromtimestamp(seconds, tz=UTC).replace(
            microsecond=milliseconds * 1000
        )
    except (OverflowError, OSError, ValueError):
        raise Phase8BBridgeProtocolError("bridge source time is invalid") from None


class Phase8BBridgeSessionValidator:
    __slots__ = (
        "expected_symbol",
        "_bridge_session_id",
        "_server",
        "_account_fingerprint",
        "_last_source_time_msc",
        "_last_tick_fingerprint",
        "_last_bridge_received_at_utc",
        "_last_market_received_at_utc",
    )

    def __init__(self, expected_symbol: str) -> None:
        if expected_symbol not in SUPPORTED_SYMBOLS:
            raise ValueError("unsupported expected Phase 8B symbol")
        self.expected_symbol = expected_symbol
        self._bridge_session_id: str | None = None
        self._server: str | None = None
        self._account_fingerprint: str | None = None
        self._last_source_time_msc: int | None = None
        self._last_tick_fingerprint: tuple[int, float, float, int] | None = None
        self._last_bridge_received_at_utc: datetime | None = None
        self._last_market_received_at_utc: datetime | None = None

    @property
    def bridge_session_id(self) -> str | None:
        return self._bridge_session_id

    @property
    def server(self) -> str | None:
        return self._server

    @property
    def account_fingerprint(self) -> str | None:
        return self._account_fingerprint

    def _bind_or_validate_identity(
        self,
        record: Phase8BBridgeRecord,
    ) -> None:
        if record.symbol != self.expected_symbol:
            raise Phase8BBridgeProtocolError("bridge symbol identity changed")
        if self._bridge_session_id is None:
            if not isinstance(record, Phase8BBridgeStartRecord):
                raise Phase8BBridgeProtocolError(
                    "first bridge record must be BRIDGE_START"
                )
            self._bridge_session_id = record.bridge_session_id
            self._server = record.server
            self._account_fingerprint = record.account_fingerprint
            return
        if isinstance(record, Phase8BBridgeStartRecord):
            raise Phase8BBridgeProtocolError(
                "bridge session changed after BRIDGE_START"
            )
        if record.bridge_session_id != self._bridge_session_id:
            raise Phase8BBridgeProtocolError("bridge session identity changed")
        if record.server != self._server:
            raise Phase8BBridgeProtocolError("bridge server identity changed")
        if record.account_fingerprint != self._account_fingerprint:
            raise Phase8BBridgeProtocolError(
                "bridge account fingerprint changed"
            )

    def accept(
        self,
        record: Phase8BBridgeRecord,
        *,
        received_at_utc: datetime,
        receive_monotonic_ns: int,
    ) -> Phase8BQuote | None:
        if not isinstance(
            record,
            (
                Phase8BBridgeStartRecord,
                Phase8BBridgeTickRecord,
                Phase8BBridgeHeartbeatRecord,
            ),
        ):
            raise TypeError("record must be a Phase 8B bridge record")
        _validate_receive_metadata(received_at_utc, receive_monotonic_ns)
        self._bind_or_validate_identity(record)
        self._last_bridge_received_at_utc = received_at_utc
        if isinstance(
            record,
            (Phase8BBridgeStartRecord, Phase8BBridgeHeartbeatRecord),
        ):
            return None

        fingerprint = (
            record.source_time_msc,
            record.bid,
            record.ask,
            record.flags,
        )
        if self._last_source_time_msc is not None:
            if record.source_time_msc < self._last_source_time_msc:
                raise Phase8BBridgeProtocolError("bridge source time regressed")
            if record.source_time_msc == self._last_source_time_msc:
                if fingerprint == self._last_tick_fingerprint:
                    return None
                raise Phase8BBridgeProtocolError(
                    "conflicting duplicate bridge tick"
                )

        quote = Phase8BQuote(
            source_time_utc=_utc_from_milliseconds(record.source_time_msc),
            received_at_utc=received_at_utc,
            receive_monotonic_ns=receive_monotonic_ns,
            symbol=record.symbol,
            bid=record.bid,
            ask=record.ask,
            tradeable=True,
        )
        self._last_source_time_msc = record.source_time_msc
        self._last_tick_fingerprint = fingerprint
        self._last_market_received_at_utc = received_at_utc
        return quote


class Phase8BBridgeFileTail:
    __slots__ = (
        "path",
        "expected_symbol",
        "start_record",
        "_offset",
        "_pending",
    )

    def __init__(self, path: Path, *, expected_symbol: str) -> None:
        if expected_symbol not in SUPPORTED_SYMBOLS:
            raise ValueError("unsupported expected Phase 8B symbol")
        self.path = Path(path)
        self.expected_symbol = expected_symbol
        try:
            with self.path.open("rb") as handle:
                first_line = handle.readline()
                if not first_line.endswith(b"\n"):
                    raise Phase8BBridgeProtocolError(
                        "bridge file must begin with a complete BRIDGE_START"
                    )
                first = parse_phase8b_bridge_line(first_line)
                if not isinstance(first, Phase8BBridgeStartRecord):
                    raise Phase8BBridgeProtocolError(
                        "bridge file must begin with BRIDGE_START"
                    )
                if first.symbol != expected_symbol:
                    raise Phase8BBridgeProtocolError(
                        "bridge file start symbol does not match expected symbol"
                    )
                handle.seek(0, os.SEEK_END)
                self._offset = handle.tell()
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise Phase8BBridgeProtocolError(
                "bridge file is unavailable"
            ) from exc
        self.start_record = first
        self._pending = b""

    def read_available(self) -> tuple[Phase8BBridgeRecord, ...]:
        try:
            size = self.path.stat().st_size
        except OSError as exc:
            raise Phase8BBridgeProtocolError(
                "bridge file is unavailable"
            ) from exc
        if size < self._offset:
            raise Phase8BBridgeProtocolError("bridge file was truncated")
        if size == self._offset:
            return ()
        try:
            with self.path.open("rb") as handle:
                handle.seek(self._offset)
                chunk = handle.read()
                self._offset = handle.tell()
        except OSError as exc:
            raise Phase8BBridgeProtocolError(
                "bridge file is unavailable"
            ) from exc
        data = self._pending + chunk
        parts = data.split(b"\n")
        self._pending = parts.pop()
        records: list[Phase8BBridgeRecord] = []
        for part in parts:
            if not part:
                raise Phase8BBridgeProtocolError(
                    "bridge file contains an empty record"
                )
            record = parse_phase8b_bridge_line(part + b"\n")
            if isinstance(record, Phase8BBridgeStartRecord):
                raise Phase8BBridgeProtocolError(
                    "bridge session changed during tailing"
                )
            if record.symbol != self.expected_symbol:
                raise Phase8BBridgeProtocolError(
                    "bridge file record symbol does not match expected symbol"
                )
            records.append(record)
        return tuple(records)


def _standard_common_files_roots() -> tuple[Path, ...]:
    home = Path.home()
    roots: list[Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        roots.append(
            Path(appdata)
            / "MetaQuotes"
            / "Terminal"
            / "Common"
            / "Files"
        )
    wine_user_names = tuple(dict.fromkeys((home.name, "user")))
    for application_support_name in (
        "net.metaquotes.wine.metatrader5",
        "MetaTrader 5",
    ):
        for wine_user_name in wine_user_names:
            roots.append(
                home
                / "Library"
                / "Application Support"
                / application_support_name
                / "drive_c"
                / "users"
                / wine_user_name
                / "AppData"
                / "Roaming"
                / "MetaQuotes"
                / "Terminal"
                / "Common"
                / "Files"
            )
    return tuple(roots)


def _discover_phase8b_bridge_file(
    symbol: str,
    roots: tuple[Path, ...],
) -> Path:
    if symbol not in SUPPORTED_SYMBOLS:
        raise ValueError("unsupported Phase 8B bridge symbol")
    relative = Path(*BRIDGE_FILE_BY_SYMBOL[symbol].split("/"))
    matches: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        candidate = Path(root).expanduser() / relative
        if candidate.is_file():
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                matches.append(candidate)
    if not matches:
        raise FileNotFoundError(
            f"MT5 Phase 8B {symbol} bridge file was not found"
        )
    if len(matches) != 1:
        raise Phase8BBridgeProtocolError(
            f"multiple MT5 Phase 8B {symbol} bridge files found"
        )
    return matches[0]


def discover_phase8b_bridge_files(
    required_symbols: tuple[str, ...] | list[str],
) -> dict[str, Path]:
    symbols = tuple(required_symbols)
    if (
        not symbols
        or len(set(symbols)) != len(symbols)
        or any(symbol not in SUPPORTED_SYMBOLS for symbol in symbols)
    ):
        raise ValueError("required Phase 8B symbols are invalid")
    roots = _standard_common_files_roots()
    return {
        symbol: _discover_phase8b_bridge_file(symbol, roots)
        for symbol in symbols
    }


__all__ = [
    "Phase8BBridgeFileTail",
    "Phase8BBridgeHeartbeatRecord",
    "Phase8BBridgeProtocolError",
    "Phase8BBridgeRecord",
    "Phase8BBridgeSessionValidator",
    "Phase8BBridgeStartRecord",
    "Phase8BBridgeTickRecord",
    "Phase8BQuote",
    "discover_phase8b_bridge_files",
    "parse_phase8b_bridge_line",
]
