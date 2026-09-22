from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Protocol

from .bridge import (
    Phase8BBridgeHeartbeatRecord,
    Phase8BBridgeProtocolError,
    Phase8BBridgeRecord,
    Phase8BBridgeSessionValidator,
    Phase8BBridgeStartRecord,
    Phase8BBridgeTickRecord,
)
from .design import (
    BRIDGE_FILE_BY_SYMBOL,
    LIVENESS_TIMEOUT_SECONDS,
    MT5_ALLOWED_SERVERS,
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
    PHASE8B_DESIGN_PROTOCOL,
    QUOTE_DEADLINE_SECONDS,
    validate_phase8b_design,
)


MAX_QUALIFICATION_SECONDS = 600.0
MIN_PRICE_COUNT = 100
MIN_HEARTBEAT_COUNT = 6
_POLL_INTERVAL_SECONDS = 0.05
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

PHASE8B_QUALIFICATION_PROTOCOL = "fmp-phase8b-qualification-v1"
PHASE8B_QUALIFICATION_ARTIFACT_PROTOCOL = (
    "fmp-phase8b-qualification-artifacts-v1"
)


class FeedQualificationOutcome(str, Enum):
    PASS = "PASS"
    INCONCLUSIVE = "INCONCLUSIVE"
    CONNECTOR_UNAVAILABLE = "CONNECTOR_UNAVAILABLE"
    CONNECTOR_REJECTED = "CONNECTOR_REJECTED"


class Phase8BQualificationOutcome(str, Enum):
    QUALIFIED = "PHASE8B_CONNECTOR_QUALIFIED"
    INCONCLUSIVE = "INCONCLUSIVE"
    CONNECTOR_UNAVAILABLE = "CONNECTOR_UNAVAILABLE"
    CONNECTOR_REJECTED = "CONNECTOR_REJECTED"


class Phase8BRecordTail(Protocol):
    start_record: Phase8BBridgeStartRecord

    def read_available(self) -> tuple[Phase8BBridgeRecord, ...]: ...


@dataclass(frozen=True, slots=True)
class FeedQualificationResult:
    symbol: str
    outcome: FeedQualificationOutcome
    account_fingerprint: str
    bridge_session_id: str
    server: str
    started_at_utc: datetime
    ended_at_utc: datetime
    elapsed_seconds: float
    price_count: int
    heartbeat_count: int
    max_bridge_liveness_gap_seconds: float
    max_market_liveness_gap_seconds: float
    rejection_codes: tuple[str, ...]

    def to_record(self) -> dict[str, object]:
        return {
            "symbol": self.symbol,
            "outcome": self.outcome.value,
            "account_fingerprint": self.account_fingerprint,
            "bridge_session_id": self.bridge_session_id,
            "server": self.server,
            "started_at_utc": self.started_at_utc.isoformat().replace(
                "+00:00",
                "Z",
            ),
            "ended_at_utc": self.ended_at_utc.isoformat().replace(
                "+00:00",
                "Z",
            ),
            "elapsed_seconds": self.elapsed_seconds,
            "price_count": self.price_count,
            "heartbeat_count": self.heartbeat_count,
            "max_bridge_liveness_gap_seconds": (
                self.max_bridge_liveness_gap_seconds
            ),
            "max_market_liveness_gap_seconds": (
                self.max_market_liveness_gap_seconds
            ),
            "rejection_codes": list(self.rejection_codes),
        }


def _validate_utc_clock(value: datetime, *, field: str) -> None:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise ValueError(f"{field} must return UTC datetime")


def _validate_monotonic(value: int, *, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must return non-negative integer")


def qualify_phase8b_feed(
    tail: Phase8BRecordTail,
    *,
    expected_symbol: str,
    utc_now: Callable[[], datetime],
    monotonic_ns: Callable[[], int],
    sleep: Callable[[float], None],
) -> FeedQualificationResult:
    started_at_utc = utc_now()
    started_ns = monotonic_ns()
    _validate_utc_clock(started_at_utc, field="qualification UTC clock")
    _validate_monotonic(started_ns, field="qualification monotonic clock")

    start = tail.start_record
    if not isinstance(start, Phase8BBridgeStartRecord):
        raise ValueError("Phase 8B qualification requires BRIDGE_START")
    if (
        start.protocol != MT5_BRIDGE_PROTOCOL
        or start.symbol != expected_symbol
        or start.server not in MT5_ALLOWED_SERVERS
        or start.account_mode != "DEMO"
        or not _SHA256_RE.fullmatch(start.bridge_session_id)
        or not _SHA256_RE.fullmatch(start.account_fingerprint)
    ):
        raise ValueError("Phase 8B qualification start identity is invalid")

    validator = Phase8BBridgeSessionValidator(expected_symbol)
    try:
        validator.accept(
            start,
            received_at_utc=started_at_utc,
            receive_monotonic_ns=started_ns,
        )
    except Phase8BBridgeProtocolError as exc:
        raise ValueError(
            "Phase 8B qualification start identity is invalid"
        ) from exc

    price_count = 0
    heartbeat_count = 0
    max_bridge_gap = 0.0
    max_market_gap = 0.0
    last_bridge_ns = started_ns
    last_market_ns = started_ns
    saw_post_start_activity = False

    def finish(
        outcome: FeedQualificationOutcome,
        *,
        codes: tuple[str, ...] = (),
        elapsed_override: float | None = None,
    ) -> FeedQualificationResult:
        ended_at_utc = utc_now()
        ended_ns = monotonic_ns()
        _validate_utc_clock(ended_at_utc, field="qualification UTC clock")
        _validate_monotonic(ended_ns, field="qualification monotonic clock")
        elapsed = max(0.0, (ended_ns - started_ns) / 1_000_000_000)
        if elapsed_override is not None:
            elapsed = elapsed_override
        return FeedQualificationResult(
            symbol=expected_symbol,
            outcome=outcome,
            account_fingerprint=start.account_fingerprint,
            bridge_session_id=start.bridge_session_id,
            server=start.server,
            started_at_utc=started_at_utc,
            ended_at_utc=ended_at_utc,
            elapsed_seconds=min(elapsed, MAX_QUALIFICATION_SECONDS),
            price_count=price_count,
            heartbeat_count=heartbeat_count,
            max_bridge_liveness_gap_seconds=max_bridge_gap,
            max_market_liveness_gap_seconds=max_market_gap,
            rejection_codes=codes,
        )

    while True:
        try:
            records = tail.read_available()
        except (FileNotFoundError, OSError):
            return finish(
                FeedQualificationOutcome.CONNECTOR_UNAVAILABLE,
                codes=("BRIDGE_UNAVAILABLE",),
            )
        except Phase8BBridgeProtocolError as exc:
            if "unavailable" in str(exc).casefold():
                return finish(
                    FeedQualificationOutcome.CONNECTOR_UNAVAILABLE,
                    codes=("BRIDGE_UNAVAILABLE",),
                )
            return finish(
                FeedQualificationOutcome.CONNECTOR_REJECTED,
                codes=("BRIDGE_INTEGRITY",),
            )
        except Exception:
            return finish(
                FeedQualificationOutcome.CONNECTOR_REJECTED,
                codes=("BRIDGE_IMPLEMENTATION_ERROR",),
            )

        received_at_utc = utc_now()
        received_ns = monotonic_ns()
        _validate_utc_clock(
            received_at_utc,
            field="qualification UTC clock",
        )
        _validate_monotonic(
            received_ns,
            field="qualification monotonic clock",
        )
        elapsed = max(
            0.0,
            (received_ns - started_ns) / 1_000_000_000,
        )
        if elapsed >= MAX_QUALIFICATION_SECONDS:
            return finish(
                FeedQualificationOutcome.INCONCLUSIVE,
                elapsed_override=MAX_QUALIFICATION_SECONDS,
            )

        bridge_gap = max(
            0.0,
            (received_ns - last_bridge_ns) / 1_000_000_000,
        )
        market_gap = max(
            0.0,
            (received_ns - last_market_ns) / 1_000_000_000,
        )
        max_bridge_gap = max(max_bridge_gap, bridge_gap)
        max_market_gap = max(max_market_gap, market_gap)

        if bridge_gap > LIVENESS_TIMEOUT_SECONDS:
            if not saw_post_start_activity:
                return finish(
                    FeedQualificationOutcome.CONNECTOR_UNAVAILABLE,
                    codes=("BRIDGE_INACTIVE",),
                )
            return finish(
                FeedQualificationOutcome.CONNECTOR_REJECTED,
                codes=("BRIDGE_LIVENESS_GAP",),
            )
        if market_gap > LIVENESS_TIMEOUT_SECONDS:
            return finish(
                FeedQualificationOutcome.INCONCLUSIVE,
                codes=("MARKET_LIVENESS_GAP",),
            )

        if not records:
            sleep(_POLL_INTERVAL_SECONDS)
            continue

        for record in records:
            try:
                quote = validator.accept(
                    record,
                    received_at_utc=received_at_utc,
                    receive_monotonic_ns=received_ns,
                )
            except (Phase8BBridgeProtocolError, TypeError):
                return finish(
                    FeedQualificationOutcome.CONNECTOR_REJECTED,
                    codes=("BRIDGE_INTEGRITY",),
                )

            saw_post_start_activity = True
            last_bridge_ns = received_ns
            if isinstance(record, Phase8BBridgeHeartbeatRecord):
                heartbeat_count += 1
            elif isinstance(record, Phase8BBridgeTickRecord):
                if quote is not None:
                    source_skew_seconds = abs(
                        (
                            received_at_utc
                            - quote.source_time_utc
                        ).total_seconds()
                    )
                    if source_skew_seconds > QUOTE_DEADLINE_SECONDS:
                        return finish(
                            FeedQualificationOutcome.CONNECTOR_REJECTED,
                            codes=("SOURCE_TIME_SKEW",),
                        )
                    price_count += 1
                    last_market_ns = received_ns
            else:
                return finish(
                    FeedQualificationOutcome.CONNECTOR_REJECTED,
                    codes=("BRIDGE_INTEGRITY",),
                )

            if (
                price_count >= MIN_PRICE_COUNT
                and heartbeat_count >= MIN_HEARTBEAT_COUNT
            ):
                return finish(FeedQualificationOutcome.PASS)


def _overall_outcome(
    results: Mapping[str, FeedQualificationResult],
) -> Phase8BQualificationOutcome:
    outcomes = {item.outcome for item in results.values()}
    if FeedQualificationOutcome.CONNECTOR_REJECTED in outcomes:
        return Phase8BQualificationOutcome.CONNECTOR_REJECTED
    if FeedQualificationOutcome.CONNECTOR_UNAVAILABLE in outcomes:
        return Phase8BQualificationOutcome.CONNECTOR_UNAVAILABLE
    if FeedQualificationOutcome.INCONCLUSIVE in outcomes:
        return Phase8BQualificationOutcome.INCONCLUSIVE
    if outcomes == {FeedQualificationOutcome.PASS}:
        return Phase8BQualificationOutcome.QUALIFIED
    raise ValueError("unsupported Phase 8B qualification outcome combination")


def _qualification_payload(
    *,
    design: Mapping[str, object],
    design_sha256: str,
    code_commit: str,
    feed_results: Mapping[str, FeedQualificationResult],
) -> dict[str, object]:
    validate_phase8b_design(design)
    if not _SHA256_RE.fullmatch(design_sha256):
        raise ValueError("Phase 8B design digest is invalid")
    if not _COMMIT_RE.fullmatch(code_commit):
        raise ValueError("Phase 8B qualification code commit is invalid")

    raw_symbols = design.get("required_symbols")
    if not isinstance(raw_symbols, list):
        raise ValueError("Phase 8B design required_symbols is malformed")
    required_symbols = tuple(str(item) for item in raw_symbols)
    if set(feed_results) != set(required_symbols):
        raise ValueError("Phase 8B qualification feed coverage mismatch")

    outcome = _overall_outcome(feed_results)
    rejection_codes: list[str] = []
    account_fingerprint: str | None = None
    server: str | None = None

    if outcome is Phase8BQualificationOutcome.QUALIFIED:
        accounts = {
            result.account_fingerprint
            for result in feed_results.values()
        }
        servers = {result.server for result in feed_results.values()}
        sessions = {
            result.bridge_session_id
            for result in feed_results.values()
        }
        if len(accounts) != 1:
            outcome = Phase8BQualificationOutcome.CONNECTOR_REJECTED
            rejection_codes.append("ACCOUNT_FINGERPRINT_MISMATCH")
        if len(servers) != 1:
            outcome = Phase8BQualificationOutcome.CONNECTOR_REJECTED
            rejection_codes.append("SERVER_MISMATCH")
        if len(sessions) != len(feed_results):
            outcome = Phase8BQualificationOutcome.CONNECTOR_REJECTED
            rejection_codes.append("BRIDGE_SESSION_COLLISION")
        if not rejection_codes:
            account_fingerprint = next(iter(accounts))
            server = next(iter(servers))

    if outcome is not Phase8BQualificationOutcome.QUALIFIED:
        for result in feed_results.values():
            rejection_codes.extend(result.rejection_codes)

    registration_authorized = (
        outcome is Phase8BQualificationOutcome.QUALIFIED
    )
    return {
        "protocol": PHASE8B_QUALIFICATION_PROTOCOL,
        "experiment_id": "EXP-20260922-018",
        "design_sha256": design_sha256,
        "design_fingerprint": design["design_fingerprint"],
        "qualification_code_commit": code_commit,
        "provider": MT5_PROVIDER,
        "transport": MT5_TRANSPORT,
        "connector_protocol": MT5_BRIDGE_PROTOCOL,
        "required_symbols": list(required_symbols),
        "bridge_file_by_symbol": {
            symbol: BRIDGE_FILE_BY_SYMBOL[symbol]
            for symbol in required_symbols
        },
        "allowed_servers": list(MT5_ALLOWED_SERVERS),
        "per_symbol": {
            symbol: feed_results[symbol].to_record()
            for symbol in required_symbols
        },
        "common_account_fingerprint": account_fingerprint,
        "common_server": server,
        "outcome": outcome.value,
        "rejection_codes": sorted(set(rejection_codes)),
        "campaign_registration_authorized": registration_authorized,
        "campaign_start_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }


def qualify_phase8b_design(
    *,
    design: Mapping[str, object],
    design_sha256: str,
    code_commit: str,
    tails: Mapping[str, Phase8BRecordTail],
    utc_now: Callable[[], datetime],
    monotonic_ns: Callable[[], int],
    sleep: Callable[[float], None],
) -> dict[str, object]:
    validate_phase8b_design(design)
    raw_symbols = design.get("required_symbols")
    if not isinstance(raw_symbols, list):
        raise ValueError("Phase 8B design required_symbols is malformed")
    required_symbols = tuple(str(item) for item in raw_symbols)
    if set(tails) != set(required_symbols):
        raise ValueError("Phase 8B qualification tails coverage mismatch")

    results: dict[str, FeedQualificationResult] = {}
    for symbol in required_symbols:
        results[symbol] = qualify_phase8b_feed(
            tails[symbol],
            expected_symbol=symbol,
            utc_now=utc_now,
            monotonic_ns=monotonic_ns,
            sleep=sleep,
        )
    return _qualification_payload(
        design=design,
        design_sha256=design_sha256,
        code_commit=code_commit,
        feed_results=results,
    )


def summarize_phase8b_qualification(
    *,
    design: Mapping[str, object],
    design_sha256: str,
    code_commit: str,
    feed_results: Mapping[str, FeedQualificationResult],
) -> dict[str, object]:
    return _qualification_payload(
        design=design,
        design_sha256=design_sha256,
        code_commit=code_commit,
        feed_results=feed_results,
    )


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


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def write_phase8b_qualification_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if result.get("protocol") != PHASE8B_QUALIFICATION_PROTOCOL:
        raise ValueError("Phase 8B qualification protocol mismatch")
    for field in (
        "campaign_start_authorized",
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_authorized",
    ):
        if result.get(field) is not False:
            raise ValueError(f"Phase 8B qualification requires {field}=false")
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "qualification.json"
    payload = _stable_json_bytes(dict(result))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE8B_QUALIFICATION_ARTIFACT_PROTOCOL,
        "experiment_id": "EXP-20260922-018",
        "campaign_registration_authorized": bool(
            result.get("campaign_registration_authorized")
        ),
        "campaign_start_authorized": False,
        "promotion_authorized": False,
        "artifacts": [
            {
                "path": result_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "FeedQualificationOutcome",
    "FeedQualificationResult",
    "MAX_QUALIFICATION_SECONDS",
    "MIN_HEARTBEAT_COUNT",
    "MIN_PRICE_COUNT",
    "PHASE8B_QUALIFICATION_PROTOCOL",
    "Phase8BQualificationOutcome",
    "qualify_phase8b_design",
    "qualify_phase8b_feed",
    "summarize_phase8b_qualification",
    "write_phase8b_qualification_artifacts",
]
