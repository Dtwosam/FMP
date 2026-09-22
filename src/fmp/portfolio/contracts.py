from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Mapping

from fmp.contracts import Direction, SUPPORTED_SYMBOLS

PHASE8A_EXPERIMENT_ID = "EXP-20260922-012"
SUPPORTED_PORTFOLIO_TIMEFRAMES = frozenset({"5m", "15m", "1h"})
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_FINGERPRINT_RE = re.compile(r"^[0-9a-f]{64}$")


class StrategyLifecycle(str, Enum):
    DISCOVERY = "DISCOVERY"
    CHALLENGER = "CHALLENGER"
    HISTORICAL_QUALIFIED = "HISTORICAL_QUALIFIED"
    SHADOW_CANDIDATE = "SHADOW_CANDIDATE"
    SHADOW_VALIDATED = "SHADOW_VALIDATED"
    DEMO_ELIGIBLE = "DEMO_ELIGIBLE"
    RETIRED = "RETIRED"


class CandidateRejectionCode(str, Enum):
    NOT_CHAMPION = "NOT_CHAMPION"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    STRATEGY_SYMBOL_MISMATCH = "STRATEGY_SYMBOL_MISMATCH"
    DIRECTION_CONFLICT = "DIRECTION_CONFLICT"


def _nonfinite_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _canonical_json_object(value: Mapping[str, object]) -> str:
    try:
        encoded = json.dumps(
            dict(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("strategy parameters must be finite JSON-compatible values") from exc
    return encoded


def _validate_nonempty(value: str, *, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _validate_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


@dataclass(frozen=True, slots=True)
class StrategyVersion:
    family: str
    version: str
    symbol: str
    timeframe: str
    parameters_json: str
    signal_contract_version: str
    code_commit: str

    def __post_init__(self) -> None:
        _validate_nonempty(self.family, field="family")
        _validate_nonempty(self.version, field="version")
        _validate_nonempty(self.signal_contract_version, field="signal_contract_version")
        if self.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"unsupported symbol: {self.symbol!r}")
        if self.timeframe not in SUPPORTED_PORTFOLIO_TIMEFRAMES:
            raise ValueError(f"unsupported timeframe: {self.timeframe!r}")
        if not _COMMIT_RE.fullmatch(self.code_commit):
            raise ValueError("code_commit must be a 40-character lowercase hexadecimal SHA")

        try:
            decoded = json.loads(self.parameters_json, parse_constant=_nonfinite_constant)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("parameters_json must be valid finite JSON") from exc
        if not isinstance(decoded, dict):
            raise ValueError("parameters_json must encode a JSON object")
        canonical = _canonical_json_object(decoded)
        if canonical != self.parameters_json:
            raise ValueError("parameters_json must use canonical sorted compact encoding")

    @classmethod
    def create(
        cls,
        *,
        family: str,
        version: str,
        symbol: str,
        timeframe: str,
        parameters: Mapping[str, object],
        signal_contract_version: str,
        code_commit: str,
    ) -> "StrategyVersion":
        return cls(
            family=family,
            version=version,
            symbol=symbol,
            timeframe=timeframe,
            parameters_json=_canonical_json_object(parameters),
            signal_contract_version=signal_contract_version,
            code_commit=code_commit,
        )

    @property
    def identity_json(self) -> str:
        return json.dumps(
            {
                "code_commit": self.code_commit,
                "family": self.family,
                "parameters": json.loads(self.parameters_json),
                "signal_contract_version": self.signal_contract_version,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "version": self.version,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.identity_json.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class StrategyRecord:
    strategy: StrategyVersion
    lifecycle: StrategyLifecycle
    evidence_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.strategy, StrategyVersion):
            raise TypeError("strategy must be StrategyVersion")
        if not isinstance(self.lifecycle, StrategyLifecycle):
            raise TypeError("lifecycle must be StrategyLifecycle")
        _validate_nonempty(self.evidence_id, field="evidence_id")


@dataclass(frozen=True, slots=True)
class ChampionSet:
    champion_set_id: str
    experiment_id: str
    strategies: tuple[StrategyVersion, ...]

    def __post_init__(self) -> None:
        _validate_nonempty(self.champion_set_id, field="champion_set_id")
        _validate_nonempty(self.experiment_id, field="experiment_id")
        if not self.strategies:
            raise ValueError("champion set must contain at least one strategy")
        fingerprints = tuple(item.fingerprint for item in self.strategies)
        if len(set(fingerprints)) != len(fingerprints):
            raise ValueError("champion set contains duplicate strategy versions")
        if fingerprints != tuple(sorted(fingerprints)):
            raise ValueError("champion strategies must be sorted by fingerprint")

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            {
                "champion_set_id": self.champion_set_id,
                "experiment_id": self.experiment_id,
                "strategy_fingerprints": [item.fingerprint for item in self.strategies],
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class PortfolioCandidate:
    candidate_id: str
    strategy_fingerprint: str
    symbol: str
    direction: Direction
    observed_at_utc: datetime
    requested_risk_fraction: float
    applicability_passed: bool

    def __post_init__(self) -> None:
        _validate_nonempty(self.candidate_id, field="candidate_id")
        if not _FINGERPRINT_RE.fullmatch(self.strategy_fingerprint):
            raise ValueError("strategy_fingerprint must be a 64-character lowercase SHA-256")
        if self.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"unsupported symbol: {self.symbol!r}")
        if not isinstance(self.direction, Direction):
            raise TypeError("direction must be Direction")
        if self.direction is Direction.NO_TRADE:
            raise ValueError("PortfolioCandidate must be directional")
        _validate_utc(self.observed_at_utc, field="observed_at_utc")
        if not math.isfinite(self.requested_risk_fraction) or self.requested_risk_fraction <= 0:
            raise ValueError("requested_risk_fraction must be finite and positive")
        if type(self.applicability_passed) is not bool:
            raise TypeError("applicability_passed must be bool")


@dataclass(frozen=True, slots=True)
class CandidateRejection:
    candidate_id: str
    code: CandidateRejectionCode
    explanation: str


@dataclass(frozen=True, slots=True)
class PortfolioExposure:
    total_requested_risk_fraction: float
    usd_long_requested_risk_fraction: float
    usd_short_requested_risk_fraction: float
    gross_usd_directional_risk_fraction: float
    net_usd_directional_risk_fraction: float


@dataclass(frozen=True, slots=True)
class PortfolioRouteResult:
    champion_set_fingerprint: str
    accepted: tuple[PortfolioCandidate, ...]
    rejected: tuple[CandidateRejection, ...]
    exposure: PortfolioExposure
