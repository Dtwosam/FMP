from __future__ import annotations

from collections.abc import Iterable

from fmp.contracts import Direction

from .contracts import (
    CandidateRejection,
    CandidateRejectionCode,
    ChampionSet,
    PortfolioCandidate,
    PortfolioExposure,
    PortfolioRouteResult,
)


def _candidate_sort_key(candidate: PortfolioCandidate) -> tuple[object, ...]:
    return (
        candidate.observed_at_utc,
        candidate.symbol,
        candidate.strategy_fingerprint,
        candidate.candidate_id,
    )


def _usd_direction(candidate: PortfolioCandidate) -> Direction:
    if candidate.symbol in {"EURUSD", "GBPUSD"}:
        return Direction.SHORT if candidate.direction is Direction.LONG else Direction.LONG
    if candidate.symbol == "USDJPY":
        return candidate.direction
    raise ValueError(f"unsupported USD exposure symbol: {candidate.symbol!r}")


def _summarize_exposure(candidates: tuple[PortfolioCandidate, ...]) -> PortfolioExposure:
    total = sum(item.requested_risk_fraction for item in candidates)
    usd_long = sum(
        item.requested_risk_fraction
        for item in candidates
        if _usd_direction(item) is Direction.LONG
    )
    usd_short = sum(
        item.requested_risk_fraction
        for item in candidates
        if _usd_direction(item) is Direction.SHORT
    )
    return PortfolioExposure(
        total_requested_risk_fraction=total,
        usd_long_requested_risk_fraction=usd_long,
        usd_short_requested_risk_fraction=usd_short,
        gross_usd_directional_risk_fraction=usd_long + usd_short,
        net_usd_directional_risk_fraction=usd_long - usd_short,
    )


def route_shadow_candidates(
    champion_set: ChampionSet,
    candidates: Iterable[PortfolioCandidate],
) -> PortfolioRouteResult:
    if not isinstance(champion_set, ChampionSet):
        raise TypeError("champion_set must be ChampionSet")

    materialized = tuple(candidates)
    ids = [item.candidate_id for item in materialized]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate portfolio candidate_id")

    champions = {item.fingerprint: item for item in champion_set.strategies}
    eligible: list[PortfolioCandidate] = []
    rejected: list[CandidateRejection] = []

    for candidate in sorted(materialized, key=_candidate_sort_key):
        if not isinstance(candidate, PortfolioCandidate):
            raise TypeError("candidates must contain PortfolioCandidate")
        strategy = champions.get(candidate.strategy_fingerprint)
        if strategy is None:
            rejected.append(
                CandidateRejection(
                    candidate_id=candidate.candidate_id,
                    code=CandidateRejectionCode.NOT_CHAMPION,
                    explanation="candidate strategy is not in the frozen champion set",
                )
            )
            continue
        if candidate.symbol != strategy.symbol:
            rejected.append(
                CandidateRejection(
                    candidate_id=candidate.candidate_id,
                    code=CandidateRejectionCode.STRATEGY_SYMBOL_MISMATCH,
                    explanation="candidate symbol does not match frozen strategy identity",
                )
            )
            continue
        if not candidate.applicability_passed:
            rejected.append(
                CandidateRejection(
                    candidate_id=candidate.candidate_id,
                    code=CandidateRejectionCode.NOT_APPLICABLE,
                    explanation="strategy applicability/regime gate did not pass",
                )
            )
            continue
        eligible.append(candidate)

    directions_by_bucket: dict[tuple[object, str], set[Direction]] = {}
    for candidate in eligible:
        bucket = (candidate.observed_at_utc, candidate.symbol)
        directions_by_bucket.setdefault(bucket, set()).add(candidate.direction)
    conflicting_buckets = {
        bucket for bucket, directions in directions_by_bucket.items() if len(directions) > 1
    }

    accepted: list[PortfolioCandidate] = []
    for candidate in eligible:
        bucket = (candidate.observed_at_utc, candidate.symbol)
        if bucket in conflicting_buckets:
            rejected.append(
                CandidateRejection(
                    candidate_id=candidate.candidate_id,
                    code=CandidateRejectionCode.DIRECTION_CONFLICT,
                    explanation="opposing champion signals exist for the same symbol and signal-time bucket",
                )
            )
        else:
            accepted.append(candidate)

    accepted_tuple = tuple(sorted(accepted, key=_candidate_sort_key))
    rejected_tuple = tuple(sorted(rejected, key=lambda item: item.candidate_id))
    return PortfolioRouteResult(
        champion_set_fingerprint=champion_set.fingerprint,
        accepted=accepted_tuple,
        rejected=rejected_tuple,
        exposure=_summarize_exposure(accepted_tuple),
    )
