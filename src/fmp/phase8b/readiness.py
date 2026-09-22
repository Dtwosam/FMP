from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Callable, Mapping, Protocol, Sequence

from .acceptance import validate_phase8b_spread_reference
from .bridge import Phase8BBridgeFileTail, Phase8BBridgeStartRecord
from .campaign_start import validate_phase8b_campaign_start_authorization
from .capture import validate_phase8b_capture_preflight
from .registration import validate_phase8b_registration


PHASE8B_CAMPAIGN_READINESS_PROTOCOL = "fmp-phase8b-campaign-readiness-v1"
PHASE8B_CAMPAIGN_READINESS_DECISION = "DEC-070"
PHASE8B_CAMPAIGN_READINESS_EXPERIMENT_ID = "EXP-20260922-041"


class Phase8BCampaignReadinessOutcome(str, Enum):
    READY = "PHASE8B_READY_FOR_PROSPECTIVE_CAPTURE"
    NEEDS_START = "PHASE8B_NEEDS_START_AUTHORIZATION"
    NEEDS_SPREAD = "PHASE8B_NEEDS_SPREAD_REFERENCE"
    TERMINAL = "PHASE8B_CAMPAIGN_TERMINAL"
    CONNECTOR_UNAVAILABLE = "CONNECTOR_UNAVAILABLE"
    CONNECTOR_REJECTED = "CONNECTOR_REJECTED"
    PROTOCOL_FAILURE = "PROTOCOL_FAILURE"


class Phase8BReadinessTail(Protocol):
    start_record: Phase8BBridgeStartRecord


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _utc(value: object, *, field: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise ValueError(f"{field} must use UTC")
    return value


def _utc_string(value: datetime) -> str:
    return _utc(value, field="timestamp").isoformat().replace("+00:00", "Z")


def _exact_identity_fields(
    *,
    registration: Mapping[str, object],
    source: Mapping[str, object],
    label: str,
) -> None:
    for field in (
        "registration_fingerprint",
        "champion_set_fingerprint",
        "champion_set_id",
        "strategy_count",
        "strategy_fingerprints",
        "strategies",
        "required_symbols",
        "required_timeframes",
        "provider",
        "transport",
        "connector_protocol",
        "bridge_file_by_symbol",
        "account_fingerprint",
        "server",
        "liveness",
        "slippage_scenarios",
    ):
        expected = (
            registration["registration_fingerprint"]
            if field == "registration_fingerprint"
            else registration[field]
        )
        if source.get(field) != expected:
            raise ValueError(f"Phase 8B readiness {label} {field} mismatch")


def _validate_current_bridge_identities(
    *,
    registration: Mapping[str, object],
    expected_sessions: Mapping[str, object],
    bridge_tails: Mapping[str, Phase8BReadinessTail],
) -> dict[str, dict[str, object]]:
    raw_symbols = registration.get("required_symbols")
    if not isinstance(raw_symbols, list) or not raw_symbols:
        raise ValueError("Phase 8B readiness required symbols are malformed")
    symbols = tuple(str(symbol) for symbol in raw_symbols)
    if set(bridge_tails) != set(symbols):
        raise ValueError("Phase 8B readiness bridge coverage mismatch")
    if set(expected_sessions) != set(symbols):
        raise ValueError("Phase 8B readiness expected session coverage mismatch")

    result: dict[str, dict[str, object]] = {}
    for symbol in symbols:
        start = getattr(bridge_tails[symbol], "start_record", None)
        if not isinstance(start, Phase8BBridgeStartRecord):
            raise ValueError(f"Phase 8B readiness {symbol} requires BRIDGE_START")
        if start.symbol != symbol:
            raise ValueError(f"Phase 8B readiness {symbol} symbol mismatch")
        if start.protocol != registration.get("connector_protocol"):
            raise ValueError(f"Phase 8B readiness {symbol} protocol mismatch")
        if start.account_mode != "DEMO":
            raise ValueError(f"Phase 8B readiness {symbol} is not DEMO")
        if start.account_fingerprint != registration.get("account_fingerprint"):
            raise ValueError(f"Phase 8B readiness {symbol} account mismatch")
        if start.server != registration.get("server"):
            raise ValueError(f"Phase 8B readiness {symbol} server mismatch")
        expected_session = _sha256(
            expected_sessions[symbol],
            field=f"Phase 8B readiness {symbol} expected bridge session",
        )
        if start.bridge_session_id != expected_session:
            raise ValueError(f"Phase 8B readiness {symbol} bridge session mismatch")
        result[symbol] = {
            "bridge_session_id": start.bridge_session_id,
            "account_fingerprint": start.account_fingerprint,
            "server": start.server,
            "account_mode": start.account_mode,
            "bridge_start_time_msc": start.bridge_start_time_msc,
        }
    if len({row["bridge_session_id"] for row in result.values()}) != len(result):
        raise ValueError("Phase 8B readiness bridge sessions collide")
    return result


def _report(
    *,
    outcome: Phase8BCampaignReadinessOutcome,
    inspected_at_utc: datetime,
    registration: Mapping[str, object],
    current_bridges: Mapping[str, object],
    next_action: str | None,
    terminal_present: bool,
    start_authorization_present: bool,
    capture_preflight_present: bool,
    spread_reference_present: bool,
    failure_code: str | None = None,
) -> dict[str, object]:
    ready = outcome is Phase8BCampaignReadinessOutcome.READY
    payload = {
        "protocol": PHASE8B_CAMPAIGN_READINESS_PROTOCOL,
        "decision": PHASE8B_CAMPAIGN_READINESS_DECISION,
        "experiment_id": PHASE8B_CAMPAIGN_READINESS_EXPERIMENT_ID,
        "outcome": outcome.value,
        "inspected_at_utc": _utc_string(inspected_at_utc),
        "registration_fingerprint": registration["registration_fingerprint"],
        "champion_set_fingerprint": registration["champion_set_fingerprint"],
        "required_symbols": list(registration["required_symbols"]),
        "current_bridge_identity_by_symbol": dict(current_bridges),
        "start_authorization_present": start_authorization_present,
        "capture_preflight_present": capture_preflight_present,
        "spread_reference_present": spread_reference_present,
        "campaign_terminal_present": terminal_present,
        "failure_code": failure_code,
        "next_action": next_action,
        "capture_prerequisites_satisfied": ready,
        "readiness_report_is_authorization": False,
        "bridge_liveness_proven": False,
        "quote_freshness_proven": False,
        "live_shadow_segment_started": False,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    return payload | {"readiness_fingerprint": _canonical_digest(payload)}


def validate_phase8b_campaign_readiness(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE8B_CAMPAIGN_READINESS_PROTOCOL:
        raise ValueError("Phase 8B readiness protocol mismatch")
    if value.get("decision") != PHASE8B_CAMPAIGN_READINESS_DECISION:
        raise ValueError("Phase 8B readiness decision mismatch")
    if value.get("experiment_id") != PHASE8B_CAMPAIGN_READINESS_EXPERIMENT_ID:
        raise ValueError("Phase 8B readiness experiment mismatch")
    try:
        outcome = Phase8BCampaignReadinessOutcome(str(value.get("outcome")))
    except ValueError as exc:
        raise ValueError("Phase 8B readiness outcome is invalid") from exc
    _sha256(
        value.get("registration_fingerprint"),
        field="Phase 8B readiness registration fingerprint",
    )
    _sha256(
        value.get("champion_set_fingerprint"),
        field="Phase 8B readiness champion-set fingerprint",
    )
    _sha256(
        value.get("readiness_fingerprint"),
        field="Phase 8B readiness fingerprint",
    )
    inspected = value.get("inspected_at_utc")
    if not isinstance(inspected, str) or not inspected.endswith("Z"):
        raise ValueError("Phase 8B readiness timestamp is invalid")
    try:
        parsed = datetime.fromisoformat(inspected.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Phase 8B readiness timestamp is invalid") from exc
    _utc(parsed, field="Phase 8B readiness timestamp")

    symbols = value.get("required_symbols")
    bridges = value.get("current_bridge_identity_by_symbol")
    if not isinstance(symbols, list) or not symbols:
        raise ValueError("Phase 8B readiness symbols are malformed")
    if not isinstance(bridges, Mapping) or set(bridges) != set(symbols):
        raise ValueError("Phase 8B readiness current bridge coverage mismatch")

    ready = outcome is Phase8BCampaignReadinessOutcome.READY
    if value.get("capture_prerequisites_satisfied") is not ready:
        raise ValueError("Phase 8B readiness prerequisite flag mismatch")
    if value.get("readiness_report_is_authorization") is not False:
        raise ValueError("Phase 8B readiness report must not authorize capture")
    if value.get("bridge_liveness_proven") is not False:
        raise ValueError("Phase 8B readiness must not claim bridge liveness")
    if value.get("quote_freshness_proven") is not False:
        raise ValueError("Phase 8B readiness must not claim quote freshness")
    for field in (
        "live_shadow_segment_started",
        "acceptance_authorized",
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 8B readiness requires {field}=false")

    expected_next = {
        Phase8BCampaignReadinessOutcome.READY: "capture-segment",
        Phase8BCampaignReadinessOutcome.NEEDS_START: "authorize-start",
        Phase8BCampaignReadinessOutcome.NEEDS_SPREAD: "freeze-spread-reference",
        Phase8BCampaignReadinessOutcome.TERMINAL: "none-terminal",
        Phase8BCampaignReadinessOutcome.CONNECTOR_UNAVAILABLE: None,
        Phase8BCampaignReadinessOutcome.CONNECTOR_REJECTED: None,
        Phase8BCampaignReadinessOutcome.PROTOCOL_FAILURE: None,
    }[outcome]
    if value.get("next_action") != expected_next:
        raise ValueError("Phase 8B readiness next action mismatch")

    fingerprint = value["readiness_fingerprint"]
    payload = dict(value)
    payload.pop("readiness_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 8B readiness fingerprint mismatch")


def build_phase8b_campaign_readiness(
    *,
    registration: Mapping[str, object],
    registration_sha256: str,
    start_authorization: Mapping[str, object] | None,
    start_authorization_sha256: str | None,
    capture_preflight: Mapping[str, object] | None,
    spread_reference: Mapping[str, object] | None,
    bridge_tails: Mapping[str, Phase8BReadinessTail],
    inspected_at_utc: datetime,
    campaign_terminal_present: bool,
) -> dict[str, object]:
    validate_phase8b_registration(registration)
    registration_sha = _sha256(
        registration_sha256,
        field="Phase 8B readiness registration SHA-256",
    )
    now = _utc(inspected_at_utc, field="Phase 8B readiness inspection time")
    if not isinstance(campaign_terminal_present, bool):
        raise ValueError("Phase 8B readiness terminal state must be boolean")

    registered_sessions = registration.get("bridge_session_id_by_symbol")
    if not isinstance(registered_sessions, Mapping):
        raise ValueError("Phase 8B readiness registered sessions are malformed")

    expected_sessions: Mapping[str, object] = registered_sessions
    if start_authorization is not None:
        validate_phase8b_campaign_start_authorization(start_authorization)
        if start_authorization.get("registration_sha256") != registration_sha:
            raise ValueError("Phase 8B readiness start registration SHA mismatch")
        _exact_identity_fields(
            registration=registration,
            source=start_authorization,
            label="start authorization",
        )
        raw = start_authorization.get("bridge_session_id_by_symbol")
        if not isinstance(raw, Mapping):
            raise ValueError("Phase 8B readiness start sessions are malformed")
        expected_sessions = raw

    if capture_preflight is not None:
        if start_authorization is None or start_authorization_sha256 is None:
            raise ValueError(
                "Phase 8B readiness preflight requires start authorization"
            )
        validate_phase8b_capture_preflight(capture_preflight)
        start_sha = _sha256(
            start_authorization_sha256,
            field="Phase 8B readiness start-authorization SHA-256",
        )
        if capture_preflight.get("registration_sha256") != registration_sha:
            raise ValueError("Phase 8B readiness preflight registration SHA mismatch")
        if capture_preflight.get("start_authorization_sha256") != start_sha:
            raise ValueError("Phase 8B readiness preflight start SHA mismatch")
        _exact_identity_fields(
            registration=registration,
            source=capture_preflight,
            label="capture preflight",
        )
        if capture_preflight.get("start_authorization_fingerprint") != (
            start_authorization.get("start_authorization_fingerprint")
        ):
            raise ValueError("Phase 8B readiness preflight start fingerprint mismatch")
        raw = capture_preflight.get("bridge_session_id_by_symbol")
        if not isinstance(raw, Mapping):
            raise ValueError("Phase 8B readiness preflight sessions are malformed")
        expected_sessions = raw
    elif start_authorization is not None:
        raise ValueError(
            "Phase 8B readiness start authorization exists without capture preflight"
        )

    if spread_reference is not None:
        if capture_preflight is None:
            raise ValueError(
                "Phase 8B readiness spread reference requires capture preflight"
            )
        validate_phase8b_spread_reference(spread_reference)
        for field in (
            "capture_preflight_fingerprint",
            "champion_set_fingerprint",
            "required_symbols",
            "slippage_scenarios",
        ):
            if spread_reference.get(field) != capture_preflight.get(field):
                raise ValueError(
                    f"Phase 8B readiness spread-reference {field} mismatch"
                )

    if campaign_terminal_present:
        current = {
            str(symbol): {}
            for symbol in registration["required_symbols"]
        }
        result = _report(
            outcome=Phase8BCampaignReadinessOutcome.TERMINAL,
            inspected_at_utc=now,
            registration=registration,
            current_bridges=current,
            next_action="none-terminal",
            terminal_present=True,
            start_authorization_present=start_authorization is not None,
            capture_preflight_present=capture_preflight is not None,
            spread_reference_present=spread_reference is not None,
        )
        validate_phase8b_campaign_readiness(result)
        return result

    try:
        current = _validate_current_bridge_identities(
            registration=registration,
            expected_sessions=expected_sessions,
            bridge_tails=bridge_tails,
        )
    except (FileNotFoundError, OSError):
        result = _report(
            outcome=Phase8BCampaignReadinessOutcome.CONNECTOR_UNAVAILABLE,
            inspected_at_utc=now,
            registration=registration,
            current_bridges={
                str(symbol): {}
                for symbol in registration["required_symbols"]
            },
            next_action=None,
            terminal_present=False,
            start_authorization_present=start_authorization is not None,
            capture_preflight_present=capture_preflight is not None,
            spread_reference_present=spread_reference is not None,
            failure_code="BRIDGE_UNAVAILABLE",
        )
        validate_phase8b_campaign_readiness(result)
        return result
    except ValueError as exc:
        result = _report(
            outcome=Phase8BCampaignReadinessOutcome.CONNECTOR_REJECTED,
            inspected_at_utc=now,
            registration=registration,
            current_bridges={
                str(symbol): {}
                for symbol in registration["required_symbols"]
            },
            next_action=None,
            terminal_present=False,
            start_authorization_present=start_authorization is not None,
            capture_preflight_present=capture_preflight is not None,
            spread_reference_present=spread_reference is not None,
            failure_code=str(exc),
        )
        validate_phase8b_campaign_readiness(result)
        return result

    if start_authorization is None:
        outcome = Phase8BCampaignReadinessOutcome.NEEDS_START
        next_action = "authorize-start"
    elif spread_reference is None:
        outcome = Phase8BCampaignReadinessOutcome.NEEDS_SPREAD
        next_action = "freeze-spread-reference"
    else:
        outcome = Phase8BCampaignReadinessOutcome.READY
        next_action = "capture-segment"

    result = _report(
        outcome=outcome,
        inspected_at_utc=now,
        registration=registration,
        current_bridges=current,
        next_action=next_action,
        terminal_present=False,
        start_authorization_present=start_authorization is not None,
        capture_preflight_present=capture_preflight is not None,
        spread_reference_present=spread_reference is not None,
    )
    validate_phase8b_campaign_readiness(result)
    return result


def load_optional_json_object(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read Phase 8B readiness artifact: {path}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Phase 8B readiness artifact is invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Phase 8B readiness artifact root must be object: {path}")
    return value


def inspect_phase8b_campaign_readiness_directory(
    *,
    campaign_dir: Path,
    inspected_at_utc: datetime,
    bridge_discoverer: Callable[[Sequence[str]], Mapping[str, Path]],
    tail_factory: Callable[[Path, str], Phase8BBridgeFileTail],
) -> dict[str, object]:
    root = Path(campaign_dir)
    registration_path = root / "registration.json"
    try:
        registration_bytes = registration_path.read_bytes()
    except OSError as exc:
        raise ValueError("Phase 8B readiness requires campaign registration") from exc
    try:
        registration = json.loads(registration_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Phase 8B readiness registration is invalid JSON") from exc
    if not isinstance(registration, dict):
        raise ValueError("Phase 8B readiness registration root must be object")
    validate_phase8b_registration(registration)

    start_path = root / "start-authorization.json"
    preflight_path = root / "capture-preflight.json"
    spread_path = root / "spread-reference.json"
    start = load_optional_json_object(start_path)
    preflight = load_optional_json_object(preflight_path)
    spread = load_optional_json_object(spread_path)

    symbols = tuple(str(item) for item in registration["required_symbols"])
    if (root / "campaign-terminal.json").exists():
        tails: dict[str, Phase8BBridgeFileTail] = {}
    else:
        try:
            paths = dict(bridge_discoverer(symbols))
            if set(paths) != set(symbols):
                raise ValueError("Phase 8B readiness bridge discovery coverage mismatch")
            tails = {
                symbol: tail_factory(Path(paths[symbol]), symbol)
                for symbol in symbols
            }
        except (FileNotFoundError, OSError):
            # A lightweight sentinel permits the pure builder to emit the
            # structured connector-unavailable outcome.
            class _Unavailable:
                @property
                def start_record(self):
                    raise FileNotFoundError("bridge unavailable")
            tails = {symbol: _Unavailable() for symbol in symbols}  # type: ignore[assignment]
        except ValueError as exc:
            message = str(exc)
            class _Rejected:
                @property
                def start_record(self):
                    raise ValueError(message)
            tails = {symbol: _Rejected() for symbol in symbols}  # type: ignore[assignment]

    return build_phase8b_campaign_readiness(
        registration=registration,
        registration_sha256=hashlib.sha256(registration_bytes).hexdigest(),
        start_authorization=start,
        start_authorization_sha256=(
            None
            if start is None
            else hashlib.sha256(start_path.read_bytes()).hexdigest()
        ),
        capture_preflight=preflight,
        spread_reference=spread,
        bridge_tails=tails,
        inspected_at_utc=inspected_at_utc,
        campaign_terminal_present=(root / "campaign-terminal.json").exists(),
    )


__all__ = [
    "PHASE8B_CAMPAIGN_READINESS_DECISION",
    "PHASE8B_CAMPAIGN_READINESS_EXPERIMENT_ID",
    "PHASE8B_CAMPAIGN_READINESS_PROTOCOL",
    "Phase8BCampaignReadinessOutcome",
    "build_phase8b_campaign_readiness",
    "inspect_phase8b_campaign_readiness_directory",
    "validate_phase8b_campaign_readiness",
]
