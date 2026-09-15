from __future__ import annotations

import math
from typing import Mapping, Sequence

from fmp.contracts import Direction
from fmp.strategies.contracts import SignalCandidate

from .contracts import FEATURE_SET_VERSION, ModelFamily
from .thresholds import ScoreCutoff


def filter_candidates(
    candidates: Sequence[SignalCandidate],
    score_by_candidate_id: Mapping[str, float],
    cutoff: ScoreCutoff,
    model_id: str,
) -> tuple[SignalCandidate, ...]:
    try:
        normalized_model_id = ModelFamily(model_id).value
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unsupported Phase 6 model_id: {model_id!r}") from exc

    directional_ids = {
        candidate.candidate_id
        for candidate in candidates
        if candidate.direction in {Direction.LONG, Direction.SHORT}
    }
    if set(score_by_candidate_id) != directional_ids:
        missing = sorted(directional_ids - set(score_by_candidate_id))
        extra = sorted(set(score_by_candidate_id) - directional_ids)
        raise ValueError(
            "Phase 6 score mapping must match directional candidates exactly; "
            f"missing scores={missing}, extra scores={extra}"
        )

    out: list[SignalCandidate] = []
    for candidate in candidates:
        if candidate.direction is Direction.NO_TRADE:
            out.append(candidate)
            continue
        if candidate.direction not in {Direction.LONG, Direction.SHORT}:
            raise ValueError("Phase 6 filtering supports only LONG, SHORT, or NO_TRADE candidates")

        score = float(score_by_candidate_id[candidate.candidate_id])
        if not math.isfinite(score) or score < 0.0 or score > 1.0:
            raise ValueError("Phase 6 model score must be finite and in [0, 1]")
        if cutoff.admits(score):
            out.append(candidate)
            continue

        metadata = dict(candidate.metadata)
        metadata.update(
            {
                "model_id": normalized_model_id,
                "model_score": score,
                "cutoff": cutoff.score,
                "retained_fraction": cutoff.retained_fraction,
                "original_direction": candidate.direction.value,
                "strategy_candidate_id": candidate.candidate_id,
                "feature_set_version": FEATURE_SET_VERSION,
                "feature_row_identity": {
                    "symbol": candidate.symbol,
                    "bar_start_utc": candidate.observation_bar_timestamp_utc,
                    "available_at_utc": candidate.signal_known_timestamp_utc,
                },
                "original_stop_price": candidate.stop_price,
                "original_target_price": candidate.target_price,
                "original_latest_exit_timestamp_utc": candidate.latest_exit_timestamp_utc,
                "original_reason_code": candidate.reason_code,
            }
        )
        out.append(
            SignalCandidate(
                candidate_id=candidate.candidate_id,
                symbol=candidate.symbol,
                observation_bar_timestamp_utc=candidate.observation_bar_timestamp_utc,
                signal_known_timestamp_utc=candidate.signal_known_timestamp_utc,
                direction=Direction.NO_TRADE,
                stop_price=None,
                target_price=None,
                latest_exit_timestamp_utc=None,
                reason_code="ML_FILTER_REJECTED",
                metadata=metadata,
            )
        )

    return tuple(out)
