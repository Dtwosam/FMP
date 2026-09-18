from __future__ import annotations

import re
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from .contracts import (
    FMP_SYMBOL,
    LIVENESS_TIMEOUT_SECONDS,
    MT5_ALLOWED_SERVERS,
    MT5_BRIDGE_FILE,
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
)
from .mt5_bridge import (
    BridgeHeartbeatRecord,
    BridgeProtocolError,
    BridgeRecord,
    BridgeSessionValidator,
    BridgeStartRecord,
    BridgeTickRecord,
)


MAX_QUALIFICATION_SECONDS = 600.0
MIN_PRICE_COUNT = 100
MIN_HEARTBEAT_COUNT = 6
_POLL_INTERVAL_SECONDS = 0.05
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class QualificationOutcome(str, Enum):
    PASS = "PASS"
    INCONCLUSIVE = "INCONCLUSIVE"
    CONNECTOR_UNAVAILABLE = "CONNECTOR_UNAVAILABLE"
    CONNECTOR_REJECTED = "CONNECTOR_REJECTED"


class BridgeRecordTail(Protocol):
    start_record: BridgeStartRecord

    def read_available(self) -> tuple[BridgeRecord, ...]: ...


@dataclass(frozen=True, slots=True)
class QualificationResult:
    outcome: QualificationOutcome
    account_fingerprint: str
    started_at_utc: datetime
    ended_at_utc: datetime
    elapsed_seconds: float
    price_count: int
    heartbeat_count: int
    max_liveness_gap_seconds: float
    boundary_audit: Mapping[str, object]
    rejection_codes: tuple[str, ...]
    bridge_session_id: str | None = None
    server: str | None = None
    max_bridge_liveness_gap_seconds: float = 0.0
    max_market_liveness_gap_seconds: float = 0.0

    def to_record(self) -> dict[str, object]:
        record: dict[str, object] = {
            "outcome": self.outcome.value,
            "account_fingerprint": self.account_fingerprint,
            "started_at_utc": self.started_at_utc.isoformat().replace("+00:00", "Z"),
            "ended_at_utc": self.ended_at_utc.isoformat().replace("+00:00", "Z"),
            "elapsed_seconds": self.elapsed_seconds,
            "price_count": self.price_count,
            "heartbeat_count": self.heartbeat_count,
            "max_liveness_gap_seconds": self.max_liveness_gap_seconds,
            "boundary_audit": dict(self.boundary_audit),
            "rejection_codes": list(self.rejection_codes),
        }
        if self.bridge_session_id is not None:
            record["bridge_session_id"] = self.bridge_session_id
            record["server"] = self.server
            record["max_bridge_liveness_gap_seconds"] = self.max_bridge_liveness_gap_seconds
            record["max_market_liveness_gap_seconds"] = self.max_market_liveness_gap_seconds
        return record


def mt5_boundary_audit() -> dict[str, object]:
    return {
        "connector_protocol": MT5_BRIDGE_PROTOCOL,
        "provider": MT5_PROVIDER,
        "transport": MT5_TRANSPORT,
        "bridge_file": MT5_BRIDGE_FILE,
        "instrument": FMP_SYMBOL,
        "allowed_servers": list(MT5_ALLOWED_SERVERS),
    }


def _validated_clock(
    *,
    utc_now: Callable[[], datetime],
    monotonic_ns: Callable[[], int],
) -> tuple[datetime, int]:
    now = utc_now()
    tick = monotonic_ns()
    if not isinstance(now, datetime) or now.utcoffset() is None or now.utcoffset().total_seconds() != 0:
        raise ValueError("qualification UTC clock must return UTC datetimes")
    if isinstance(tick, bool) or not isinstance(tick, int) or tick < 0:
        raise ValueError("qualification monotonic clock must return non-negative integers")
    return now, tick


def qualify_bridge(
    tail: BridgeRecordTail,
    *,
    utc_now: Callable[[], datetime],
    monotonic_ns: Callable[[], int],
) -> QualificationResult:
    started_at_utc, started_ns = _validated_clock(
        utc_now=utc_now,
        monotonic_ns=monotonic_ns,
    )
    audit = mt5_boundary_audit()
    start = tail.start_record
    if not isinstance(start, BridgeStartRecord):
        raise ValueError("bridge qualification requires a validated BRIDGE_START")
    if (
        start.protocol != MT5_BRIDGE_PROTOCOL
        or start.symbol != FMP_SYMBOL
        or start.server not in MT5_ALLOWED_SERVERS
        or start.account_mode != "DEMO"
        or not _SHA256.fullmatch(start.bridge_session_id)
        or not _SHA256.fullmatch(start.account_fingerprint)
    ):
        raise ValueError("bridge qualification start identity is invalid")

    validator = BridgeSessionValidator()
    try:
        validator.accept(
            start,
            received_at_utc=started_at_utc,
            receive_monotonic_ns=started_ns,
        )
    except BridgeProtocolError as exc:
        raise ValueError("bridge qualification start identity is invalid") from exc

    price_count = 0
    heartbeat_count = 0
    max_bridge_gap = 0.0
    max_market_gap = 0.0
    last_bridge_ns = started_ns
    last_market_ns = started_ns
    saw_post_start_activity = False

    def finish(
        outcome: QualificationOutcome,
        *,
        codes: tuple[str, ...] = (),
        elapsed_override: float | None = None,
    ) -> QualificationResult:
        ended_at_utc, ended_ns = _validated_clock(
            utc_now=utc_now,
            monotonic_ns=monotonic_ns,
        )
        elapsed = max(0.0, (ended_ns - started_ns) / 1_000_000_000)
        if elapsed_override is not None:
            elapsed = elapsed_override
        elapsed = min(elapsed, MAX_QUALIFICATION_SECONDS)
        return QualificationResult(
            outcome=outcome,
            account_fingerprint=start.account_fingerprint,
            started_at_utc=started_at_utc,
            ended_at_utc=ended_at_utc,
            elapsed_seconds=elapsed,
            price_count=price_count,
            heartbeat_count=heartbeat_count,
            max_liveness_gap_seconds=max(max_bridge_gap, max_market_gap),
            boundary_audit=audit,
            rejection_codes=codes,
            bridge_session_id=start.bridge_session_id,
            server=start.server,
            max_bridge_liveness_gap_seconds=max_bridge_gap,
            max_market_liveness_gap_seconds=max_market_gap,
        )

    while True:
        try:
            records = tail.read_available()
        except (FileNotFoundError, OSError):
            return finish(
                QualificationOutcome.CONNECTOR_UNAVAILABLE,
                codes=("BRIDGE_UNAVAILABLE",),
            )
        except BridgeProtocolError as exc:
            if "unavailable" in str(exc).casefold():
                return finish(
                    QualificationOutcome.CONNECTOR_UNAVAILABLE,
                    codes=("BRIDGE_UNAVAILABLE",),
                )
            return finish(
                QualificationOutcome.CONNECTOR_REJECTED,
                codes=("BRIDGE_INTEGRITY",),
            )
        except Exception:
            return finish(
                QualificationOutcome.CONNECTOR_REJECTED,
                codes=("BRIDGE_IMPLEMENTATION_ERROR",),
            )

        received_at_utc, received_ns = _validated_clock(
            utc_now=utc_now,
            monotonic_ns=monotonic_ns,
        )
        elapsed = max(0.0, (received_ns - started_ns) / 1_000_000_000)
        if elapsed >= MAX_QUALIFICATION_SECONDS:
            return finish(
                QualificationOutcome.INCONCLUSIVE,
                elapsed_override=MAX_QUALIFICATION_SECONDS,
            )

        bridge_gap = max(0.0, (received_ns - last_bridge_ns) / 1_000_000_000)
        market_gap = max(0.0, (received_ns - last_market_ns) / 1_000_000_000)
        max_bridge_gap = max(max_bridge_gap, bridge_gap)
        max_market_gap = max(max_market_gap, market_gap)

        if bridge_gap > LIVENESS_TIMEOUT_SECONDS:
            if not saw_post_start_activity:
                return finish(
                    QualificationOutcome.CONNECTOR_UNAVAILABLE,
                    codes=("BRIDGE_INACTIVE",),
                )
            return finish(
                QualificationOutcome.CONNECTOR_REJECTED,
                codes=("BRIDGE_LIVENESS_GAP",),
            )

        if market_gap > LIVENESS_TIMEOUT_SECONDS:
            return finish(
                QualificationOutcome.INCONCLUSIVE,
                codes=("MARKET_LIVENESS_GAP",),
            )

        if not records:
            time.sleep(_POLL_INTERVAL_SECONDS)
            continue

        for record in records:
            try:
                quote = validator.accept(
                    record,
                    received_at_utc=received_at_utc,
                    receive_monotonic_ns=received_ns,
                )
            except (BridgeProtocolError, TypeError):
                return finish(
                    QualificationOutcome.CONNECTOR_REJECTED,
                    codes=("BRIDGE_INTEGRITY",),
                )

            saw_post_start_activity = True
            last_bridge_ns = received_ns
            if isinstance(record, BridgeHeartbeatRecord):
                heartbeat_count += 1
            elif isinstance(record, BridgeTickRecord):
                if quote is not None:
                    price_count += 1
                    last_market_ns = received_ns
            else:
                return finish(
                    QualificationOutcome.CONNECTOR_REJECTED,
                    codes=("BRIDGE_INTEGRITY",),
                )

            if price_count >= MIN_PRICE_COUNT and heartbeat_count >= MIN_HEARTBEAT_COUNT:
                return finish(QualificationOutcome.PASS)


__all__ = [
    "MAX_QUALIFICATION_SECONDS",
    "MIN_HEARTBEAT_COUNT",
    "MIN_PRICE_COUNT",
    "QualificationOutcome",
    "QualificationResult",
    "mt5_boundary_audit",
    "qualify_bridge",
]
