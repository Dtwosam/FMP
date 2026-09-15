from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from .contracts import (
    LIVENESS_TIMEOUT_SECONDS,
    PRACTICE_STREAM_HOST,
    PRACTICE_STREAM_PATH_TEMPLATE,
    PROVIDER_INSTRUMENT,
)
from .normalization import ProviderMessageError, StreamSegmentNormalizer
from .oanda import OandaPracticeStreamError, parse_provider_line


MAX_QUALIFICATION_SECONDS = 600.0
MIN_PRICE_COUNT = 100
MIN_HEARTBEAT_COUNT = 6
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class QualificationOutcome(str, Enum):
    PASS = "PASS"
    INCONCLUSIVE = "INCONCLUSIVE"
    CONNECTOR_UNAVAILABLE = "CONNECTOR_UNAVAILABLE"
    CONNECTOR_REJECTED = "CONNECTOR_REJECTED"


class PricingLineStream(Protocol):
    def iter_lines(self): ...  # type: ignore[no-untyped-def]


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

    def to_record(self) -> dict[str, object]:
        return {
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


def practice_boundary_audit() -> dict[str, object]:
    return {
        "method": "GET",
        "host": PRACTICE_STREAM_HOST,
        "path_template": PRACTICE_STREAM_PATH_TEMPLATE,
        "instrument": PROVIDER_INSTRUMENT,
        "snapshot": True,
        "include_home_conversions": False,
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


def qualify_stream(
    stream: PricingLineStream,
    *,
    utc_now: Callable[[], datetime],
    monotonic_ns: Callable[[], int],
    account_fingerprint: str,
) -> QualificationResult:
    if not isinstance(account_fingerprint, str) or not _SHA256.fullmatch(account_fingerprint):
        raise ValueError("account_fingerprint must be a lowercase SHA-256 digest")

    started_at_utc, started_ns = _validated_clock(
        utc_now=utc_now,
        monotonic_ns=monotonic_ns,
    )
    normalizer = StreamSegmentNormalizer()
    price_count = 0
    heartbeat_count = 0
    max_gap = 0.0
    last_valid_ns: int | None = None
    audit = practice_boundary_audit()

    def finish(
        outcome: QualificationOutcome,
        *,
        codes: tuple[str, ...] = (),
        elapsed_override: float | None = None,
    ) -> QualificationResult:
        ended_at_utc = utc_now()
        ended_ns = monotonic_ns()
        elapsed = max(0.0, (ended_ns - started_ns) / 1_000_000_000)
        if elapsed_override is not None:
            elapsed = elapsed_override
        return QualificationResult(
            outcome=outcome,
            account_fingerprint=account_fingerprint,
            started_at_utc=started_at_utc,
            ended_at_utc=ended_at_utc,
            elapsed_seconds=elapsed,
            price_count=price_count,
            heartbeat_count=heartbeat_count,
            max_liveness_gap_seconds=max_gap,
            boundary_audit=audit,
            rejection_codes=codes,
        )

    try:
        for line in stream.iter_lines():
            received_ns = monotonic_ns()
            elapsed = max(0.0, (received_ns - started_ns) / 1_000_000_000)
            if elapsed > MAX_QUALIFICATION_SECONDS:
                return finish(
                    QualificationOutcome.INCONCLUSIVE,
                    elapsed_override=MAX_QUALIFICATION_SECONDS,
                )
            received_at_utc = utc_now()

            if last_valid_ns is not None:
                gap = max(0.0, (received_ns - last_valid_ns) / 1_000_000_000)
                max_gap = max(max_gap, gap)
                if gap > LIVENESS_TIMEOUT_SECONDS:
                    return finish(
                        QualificationOutcome.CONNECTOR_REJECTED,
                        codes=("LIVENESS_GAP",),
                    )

            try:
                raw = parse_provider_line(line)
            except OandaPracticeStreamError:
                return finish(
                    QualificationOutcome.CONNECTOR_REJECTED,
                    codes=("MALFORMED_MESSAGE",),
                )

            try:
                normalizer.accept(
                    raw,
                    received_at_utc=received_at_utc,
                    receive_monotonic_ns=received_ns,
                )
            except ProviderMessageError:
                return finish(
                    QualificationOutcome.CONNECTOR_REJECTED,
                    codes=("MESSAGE_INTEGRITY",),
                )

            message_type = raw.get("type")
            if message_type == "PRICE":
                price_count += 1
            elif message_type == "HEARTBEAT":
                heartbeat_count += 1
            else:
                return finish(
                    QualificationOutcome.CONNECTOR_REJECTED,
                    codes=("MESSAGE_TYPE",),
                )
            last_valid_ns = received_ns

            if price_count >= MIN_PRICE_COUNT and heartbeat_count >= MIN_HEARTBEAT_COUNT:
                return finish(QualificationOutcome.PASS)
    except OandaPracticeStreamError:
        return finish(
            QualificationOutcome.CONNECTOR_UNAVAILABLE,
            codes=("STREAM_UNAVAILABLE",),
        )
    except Exception:
        return finish(
            QualificationOutcome.CONNECTOR_UNAVAILABLE,
            codes=("STREAM_UNAVAILABLE",),
        )

    return finish(QualificationOutcome.INCONCLUSIVE)


__all__ = [
    "MAX_QUALIFICATION_SECONDS",
    "MIN_HEARTBEAT_COUNT",
    "MIN_PRICE_COUNT",
    "QualificationOutcome",
    "QualificationResult",
    "practice_boundary_audit",
    "qualify_stream",
]
