from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TypeAlias

from .contracts import (
    FMP_SYMBOL,
    MT5_ALLOWED_SERVERS,
    MT5_BRIDGE_FILE,
    MT5_BRIDGE_PROTOCOL,
    NormalizedQuote,
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


class BridgeProtocolError(ValueError):
    """Fail-closed error for malformed or integrity-invalid MT5 bridge data."""


@dataclass(frozen=True, slots=True)
class BridgeStartRecord:
    protocol: str
    bridge_session_id: str
    symbol: str
    server: str
    account_fingerprint: str
    account_mode: str
    bridge_start_time_msc: int
    record_type: str = "BRIDGE_START"


@dataclass(frozen=True, slots=True)
class BridgeTickRecord:
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
class BridgeHeartbeatRecord:
    protocol: str
    bridge_session_id: str
    symbol: str
    server: str
    account_fingerprint: str
    bridge_emitted_time_msc: int
    last_tick_time_msc: int | None
    record_type: str = "BRIDGE_HEARTBEAT"


BridgeRecord: TypeAlias = BridgeStartRecord | BridgeTickRecord | BridgeHeartbeatRecord


def _require_lower_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in _HEX for ch in value):
        raise BridgeProtocolError(f"bridge {field} is invalid")
    return value


def _require_int(value: object, *, field: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise BridgeProtocolError(f"bridge {field} is invalid")
    return value


def _require_optional_positive_int(value: object, *, field: str) -> int | None:
    if value is None:
        return None
    return _require_int(value, field=field, minimum=1)


def _require_price(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BridgeProtocolError(f"bridge {field} is invalid")
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise BridgeProtocolError(f"bridge {field} is invalid")
    return result


def _validate_common(raw: dict[str, object]) -> tuple[str, str, str, str, str]:
    protocol = raw.get("protocol")
    if protocol != MT5_BRIDGE_PROTOCOL:
        raise BridgeProtocolError("bridge protocol is invalid")
    symbol = raw.get("symbol")
    if symbol != FMP_SYMBOL:
        raise BridgeProtocolError("bridge symbol is invalid")
    server = raw.get("server")
    if not isinstance(server, str) or server not in MT5_ALLOWED_SERVERS:
        raise BridgeProtocolError("bridge server is invalid")
    bridge_session_id = _require_lower_hex(
        raw.get("bridge_session_id"), field="bridge_session_id"
    )
    account_fingerprint = _require_lower_hex(
        raw.get("account_fingerprint"), field="account_fingerprint"
    )
    return protocol, bridge_session_id, symbol, server, account_fingerprint


def parse_bridge_line(line: bytes) -> BridgeRecord:
    if not isinstance(line, bytes):
        raise TypeError("bridge line must be bytes")
    if not line or not line.endswith(b"\n"):
        raise BridgeProtocolError("bridge record must be a complete newline-terminated line")
    try:
        decoded = line.decode("utf-8")
        raw = json.loads(decoded)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise BridgeProtocolError("bridge record is invalid JSON") from None
    if not isinstance(raw, dict):
        raise BridgeProtocolError("bridge record must be an object")

    record_type = raw.get("record_type")
    if record_type == "BRIDGE_START":
        expected = _START_FIELDS
    elif record_type == "TICK":
        expected = _TICK_FIELDS
    elif record_type == "BRIDGE_HEARTBEAT":
        expected = _HEARTBEAT_FIELDS
    else:
        raise BridgeProtocolError("bridge record type is invalid")
    if frozenset(raw) != expected:
        raise BridgeProtocolError("bridge record fields are invalid")

    protocol, bridge_session_id, symbol, server, account_fingerprint = _validate_common(raw)
    if record_type == "BRIDGE_START":
        if raw.get("account_mode") != "DEMO":
            raise BridgeProtocolError("bridge account mode is invalid")
        bridge_start_time_msc = _require_int(
            raw.get("bridge_start_time_msc"), field="bridge_start_time_msc", minimum=1
        )
        return BridgeStartRecord(
            protocol=protocol,
            bridge_session_id=bridge_session_id,
            symbol=symbol,
            server=server,
            account_fingerprint=account_fingerprint,
            account_mode="DEMO",
            bridge_start_time_msc=bridge_start_time_msc,
        )

    if record_type == "TICK":
        source_time_msc = _require_int(
            raw.get("source_time_msc"), field="source_time_msc", minimum=1
        )
        bid = _require_price(raw.get("bid"), field="bid")
        ask = _require_price(raw.get("ask"), field="ask")
        if bid > ask:
            raise BridgeProtocolError("bridge quote is crossed")
        flags = _require_int(raw.get("flags"), field="flags", minimum=0)
        return BridgeTickRecord(
            protocol=protocol,
            bridge_session_id=bridge_session_id,
            symbol=symbol,
            server=server,
            account_fingerprint=account_fingerprint,
            source_time_msc=source_time_msc,
            bid=bid,
            ask=ask,
            flags=flags,
        )

    bridge_emitted_time_msc = _require_int(
        raw.get("bridge_emitted_time_msc"), field="bridge_emitted_time_msc", minimum=1
    )
    last_tick_time_msc = _require_optional_positive_int(
        raw.get("last_tick_time_msc"), field="last_tick_time_msc"
    )
    return BridgeHeartbeatRecord(
        protocol=protocol,
        bridge_session_id=bridge_session_id,
        symbol=symbol,
        server=server,
        account_fingerprint=account_fingerprint,
        bridge_emitted_time_msc=bridge_emitted_time_msc,
        last_tick_time_msc=last_tick_time_msc,
    )


def _validate_receive_metadata(received_at_utc: datetime, receive_monotonic_ns: int) -> None:
    if not isinstance(received_at_utc, datetime):
        raise BridgeProtocolError("bridge receive time is invalid")
    if received_at_utc.tzinfo is None or received_at_utc.utcoffset() != timedelta(0):
        raise BridgeProtocolError("bridge receive time must use UTC")
    if (
        isinstance(receive_monotonic_ns, bool)
        or not isinstance(receive_monotonic_ns, int)
        or receive_monotonic_ns < 0
    ):
        raise BridgeProtocolError("bridge monotonic receive time is invalid")


def _utc_from_milliseconds(value: int) -> datetime:
    seconds, milliseconds = divmod(value, 1000)
    try:
        return datetime.fromtimestamp(seconds, tz=UTC).replace(microsecond=milliseconds * 1000)
    except (OverflowError, OSError, ValueError):
        raise BridgeProtocolError("bridge source time is invalid") from None


class BridgeSessionValidator:
    __slots__ = (
        "_bridge_session_id",
        "_server",
        "_account_fingerprint",
        "_last_source_time_msc",
        "_last_tick_fingerprint",
        "_last_bridge_received_at_utc",
        "_last_market_received_at_utc",
    )

    def __init__(self) -> None:
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

    @property
    def last_bridge_received_at_utc(self) -> datetime | None:
        return self._last_bridge_received_at_utc

    @property
    def last_market_received_at_utc(self) -> datetime | None:
        return self._last_market_received_at_utc

    def _bind_or_validate_identity(self, record: BridgeRecord) -> None:
        if self._bridge_session_id is None:
            if not isinstance(record, BridgeStartRecord):
                raise BridgeProtocolError("first bridge record must be BRIDGE_START")
            self._bridge_session_id = record.bridge_session_id
            self._server = record.server
            self._account_fingerprint = record.account_fingerprint
            return

        if isinstance(record, BridgeStartRecord):
            raise BridgeProtocolError("bridge session changed after BRIDGE_START")
        if record.bridge_session_id != self._bridge_session_id:
            raise BridgeProtocolError("bridge session identity changed")
        if record.server != self._server:
            raise BridgeProtocolError("bridge server identity changed")
        if record.account_fingerprint != self._account_fingerprint:
            raise BridgeProtocolError("bridge account fingerprint changed")

    def accept(
        self,
        record: BridgeRecord,
        *,
        received_at_utc: datetime,
        receive_monotonic_ns: int,
    ) -> NormalizedQuote | None:
        if not isinstance(record, (BridgeStartRecord, BridgeTickRecord, BridgeHeartbeatRecord)):
            raise TypeError("record must be a bridge record")
        _validate_receive_metadata(received_at_utc, receive_monotonic_ns)
        self._bind_or_validate_identity(record)
        self._last_bridge_received_at_utc = received_at_utc

        if isinstance(record, (BridgeStartRecord, BridgeHeartbeatRecord)):
            return None

        fingerprint = (record.source_time_msc, record.bid, record.ask, record.flags)
        if self._last_source_time_msc is not None:
            if record.source_time_msc < self._last_source_time_msc:
                raise BridgeProtocolError("bridge source time regressed")
            if record.source_time_msc == self._last_source_time_msc:
                if fingerprint == self._last_tick_fingerprint:
                    return None
                raise BridgeProtocolError("conflicting duplicate bridge tick")

        source_time_utc = _utc_from_milliseconds(record.source_time_msc)
        try:
            quote = NormalizedQuote(
                source_time_utc=source_time_utc,
                received_at_utc=received_at_utc,
                receive_monotonic_ns=receive_monotonic_ns,
                symbol=FMP_SYMBOL,
                bid=record.bid,
                ask=record.ask,
                tradeable=True,
            )
        except (TypeError, ValueError):
            raise BridgeProtocolError("bridge tick receive metadata is invalid") from None

        self._last_source_time_msc = record.source_time_msc
        self._last_tick_fingerprint = fingerprint
        self._last_market_received_at_utc = received_at_utc
        return quote


class BridgeFileTail:
    __slots__ = ("path", "start_record", "_offset", "_pending")

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        try:
            with self.path.open("rb") as handle:
                first_line = handle.readline()
                if not first_line.endswith(b"\n"):
                    raise BridgeProtocolError("bridge file must begin with a complete BRIDGE_START")
                first = parse_bridge_line(first_line)
                if not isinstance(first, BridgeStartRecord):
                    raise BridgeProtocolError("bridge file must begin with BRIDGE_START")
                handle.seek(0, os.SEEK_END)
                self._offset = handle.tell()
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise BridgeProtocolError("bridge file is unavailable") from exc
        self.start_record = first
        self._pending = b""

    def read_available(self) -> tuple[BridgeRecord, ...]:
        try:
            size = self.path.stat().st_size
        except OSError as exc:
            raise BridgeProtocolError("bridge file is unavailable") from exc
        if size < self._offset:
            raise BridgeProtocolError("bridge file was truncated")
        if size == self._offset:
            return ()

        try:
            with self.path.open("rb") as handle:
                handle.seek(self._offset)
                chunk = handle.read()
                self._offset = handle.tell()
        except OSError as exc:
            raise BridgeProtocolError("bridge file is unavailable") from exc

        data = self._pending + chunk
        parts = data.split(b"\n")
        self._pending = parts.pop()
        records: list[BridgeRecord] = []
        for part in parts:
            if not part:
                raise BridgeProtocolError("bridge file contains an empty record")
            record = parse_bridge_line(part + b"\n")
            if isinstance(record, BridgeStartRecord):
                raise BridgeProtocolError("bridge session changed during tailing")
            records.append(record)
        return tuple(records)


def _discover_bridge_file(roots: tuple[Path, ...]) -> Path:
    relative = Path(*MT5_BRIDGE_FILE.split("/"))
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
        raise FileNotFoundError("MT5 Phase 8 bridge file was not found in approved Common Files roots")
    if len(matches) != 1:
        raise BridgeProtocolError("multiple MT5 Phase 8 bridge files found in approved roots")
    return matches[0]


def _standard_common_files_roots() -> tuple[Path, ...]:
    home = Path.home()
    roots: list[Path] = []

    appdata = os.environ.get("APPDATA")
    if appdata:
        roots.append(Path(appdata) / "MetaQuotes" / "Terminal" / "Common" / "Files")

    roots.extend(
        (
            home
            / "Library"
            / "Application Support"
            / "net.metaquotes.wine.metatrader5"
            / "drive_c"
            / "users"
            / home.name
            / "AppData"
            / "Roaming"
            / "MetaQuotes"
            / "Terminal"
            / "Common"
            / "Files",
            home
            / "Library"
            / "Application Support"
            / "MetaTrader 5"
            / "drive_c"
            / "users"
            / home.name
            / "AppData"
            / "Roaming"
            / "MetaQuotes"
            / "Terminal"
            / "Common"
            / "Files",
        )
    )
    return tuple(roots)


def discover_bridge_file() -> Path:
    return _discover_bridge_file(_standard_common_files_roots())


__all__ = [
    "BridgeFileTail",
    "BridgeHeartbeatRecord",
    "BridgeProtocolError",
    "BridgeRecord",
    "BridgeSessionValidator",
    "BridgeStartRecord",
    "BridgeTickRecord",
    "discover_bridge_file",
    "parse_bridge_line",
]
