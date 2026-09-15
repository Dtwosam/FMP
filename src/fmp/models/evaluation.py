from __future__ import annotations

import math
from statistics import median
from typing import Sequence

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def _validated_classification_inputs(
    labels: Sequence[int],
    scores: Sequence[float],
    candidate_ids: Sequence[str],
) -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    y = np.asarray(tuple(labels), dtype=np.int64)
    s = np.asarray(tuple(scores), dtype=np.float64)
    ids = tuple(candidate_ids)

    if y.ndim != 1 or s.ndim != 1 or len(y) != len(s) or len(y) != len(ids):
        raise ValueError("Phase 6 diagnostic labels, scores, and candidate_ids must align")
    if len(y) == 0:
        raise ValueError("Phase 6 diagnostics require non-empty inputs")
    if len(set(ids)) != len(ids):
        raise ValueError("Phase 6 diagnostic candidate_ids must be unique")
    if any(not isinstance(candidate_id, str) or not candidate_id for candidate_id in ids):
        raise ValueError("Phase 6 diagnostic candidate_ids must be non-empty strings")
    if not np.isfinite(s).all():
        raise ValueError("Phase 6 diagnostic scores must be finite")
    if np.any(s < 0.0) or np.any(s > 1.0):
        raise ValueError("Phase 6 diagnostic scores must be in [0, 1]")
    classes = set(np.unique(y).tolist())
    if classes != {0, 1}:
        raise ValueError("Phase 6 diagnostics require both label classes; one class is invalid")
    return y, s, ids


def _reliability_bins(
    labels: np.ndarray,
    scores: np.ndarray,
    candidate_ids: tuple[str, ...],
) -> tuple[dict[str, object], ...]:
    ordered = sorted(
        zip(scores.tolist(), candidate_ids, labels.tolist(), strict=True),
        key=lambda item: (item[0], item[1]),
    )
    bin_count = min(10, len(ordered))
    base, extra = divmod(len(ordered), bin_count)
    out: list[dict[str, object]] = []
    offset = 0
    for index in range(bin_count):
        size = base + (1 if index < extra else 0)
        chunk = ordered[offset : offset + size]
        offset += size
        chunk_scores = [float(item[0]) for item in chunk]
        chunk_labels = [int(item[2]) for item in chunk]
        out.append(
            {
                "row_count": size,
                "mean_model_score": float(sum(chunk_scores) / size),
                "observed_positive_rate": float(sum(chunk_labels) / size),
            }
        )
    return tuple(out)


def classification_diagnostics(
    labels: Sequence[int],
    scores: Sequence[float],
    candidate_ids: Sequence[str],
) -> dict[str, object]:
    y, s, ids = _validated_classification_inputs(labels, scores, candidate_ids)
    score_values = tuple(float(value) for value in s.tolist())
    result = {
        "roc_auc": float(roc_auc_score(y, s)),
        "average_precision": float(average_precision_score(y, s)),
        "brier_score": float(brier_score_loss(y, s)),
        "prevalence": float(np.mean(y)),
        "score_min": min(score_values),
        "score_max": max(score_values),
        "score_mean": float(sum(score_values) / len(score_values)),
        "score_median": float(median(score_values)),
        "reliability_bins": _reliability_bins(y, s, ids),
    }
    numeric_values = tuple(
        float(result[key])
        for key in (
            "roc_auc",
            "average_precision",
            "brier_score",
            "prevalence",
            "score_min",
            "score_max",
            "score_mean",
            "score_median",
        )
    )
    if any(not math.isfinite(value) for value in numeric_values):
        raise ValueError("Phase 6 classification diagnostics produced non-finite metrics")
    return result
