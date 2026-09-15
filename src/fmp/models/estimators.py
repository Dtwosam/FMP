from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import struct
import warnings
from typing import Any, Sequence

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

from .contracts import ModelFamily


EXPERIMENT_SEED = 20260915


@dataclass(frozen=True, slots=True)
class FittedEstimator:
    family: ModelFamily
    estimator: Any


def build_estimator(family: ModelFamily):
    try:
        normalized = ModelFamily(family)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unsupported Phase 6 model family: {family!r}") from exc

    if normalized is ModelFamily.LOGISTIC_REGRESSION:
        return LogisticRegression(
            penalty="l2",
            C=1.0,
            solver="lbfgs",
            tol=1e-8,
            fit_intercept=True,
            class_weight=None,
            max_iter=2000,
            warm_start=False,
        )
    if normalized is ModelFamily.HIST_GRADIENT_BOOSTING:
        return HistGradientBoostingClassifier(
            loss="log_loss",
            learning_rate=0.05,
            max_iter=100,
            max_leaf_nodes=15,
            max_depth=3,
            min_samples_leaf=20,
            l2_regularization=1.0,
            max_features=1.0,
            max_bins=255,
            early_stopping=False,
            warm_start=False,
            class_weight=None,
            random_state=EXPERIMENT_SEED,
        )
    raise ValueError(f"unsupported Phase 6 model family: {family!r}")


def _validate_training_arrays(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    features = np.asarray(X, dtype=np.float64)
    labels = np.asarray(y)
    if features.ndim != 2 or features.shape[0] == 0 or features.shape[1] == 0:
        raise ValueError("Phase 6 estimator requires a non-empty 2D feature matrix")
    if not np.isfinite(features).all():
        raise ValueError("Phase 6 estimator features must be finite after preprocessing")
    if labels.ndim != 1 or labels.shape[0] != features.shape[0]:
        raise ValueError("Phase 6 estimator labels must align one-to-one with feature rows")
    if set(np.unique(labels).tolist()) != {0, 1}:
        raise ValueError("Phase 6 estimator fit requires both binary label classes")
    return features, labels.astype(np.int64, copy=False)


def fit_estimator(family: ModelFamily, X: np.ndarray, y: np.ndarray) -> FittedEstimator:
    normalized = ModelFamily(family)
    features, labels = _validate_training_arrays(X, y)
    estimator = build_estimator(normalized)

    if normalized is ModelFamily.LOGISTIC_REGRESSION:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", ConvergenceWarning)
                estimator.fit(features, labels)
        except ConvergenceWarning as exc:
            raise RuntimeError("Phase 6 logistic regression failed to converge") from exc
    else:
        estimator.fit(features, labels)

    return FittedEstimator(family=normalized, estimator=estimator)


def score_estimator(fitted: FittedEstimator, X: np.ndarray) -> np.ndarray:
    features = np.asarray(X, dtype=np.float64)
    if features.ndim != 2:
        raise ValueError("Phase 6 scoring requires a 2D feature matrix")
    if not np.isfinite(features).all():
        raise ValueError("Phase 6 scoring features must be finite after preprocessing")
    probabilities = np.asarray(fitted.estimator.predict_proba(features), dtype=np.float64)
    if probabilities.ndim != 2 or probabilities.shape[0] != features.shape[0] or probabilities.shape[1] != 2:
        raise ValueError("Phase 6 estimator must emit binary predict_proba scores")
    scores = probabilities[:, 1].copy()
    if not np.isfinite(scores).all() or np.any(scores < 0.0) or np.any(scores > 1.0):
        raise ValueError("Phase 6 estimator emitted invalid positive-class scores")
    return scores


def score_digest(candidate_ids: Sequence[str], scores: Sequence[float]) -> str:
    ids = tuple(candidate_ids)
    values = tuple(float(value) for value in scores)
    if len(ids) != len(values):
        raise ValueError("Phase 6 score digest requires one candidate_id per score")
    if len(set(ids)) != len(ids):
        raise ValueError("Phase 6 score digest candidate_ids must be unique")

    digest = hashlib.sha256()
    for candidate_id, score in zip(ids, values, strict=True):
        if not isinstance(candidate_id, str) or not candidate_id:
            raise ValueError("Phase 6 score digest candidate_id must be non-empty")
        if not math.isfinite(score):
            raise ValueError("Phase 6 score digest cannot contain non-finite scores")
        encoded = candidate_id.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, byteorder="big", signed=False))
        digest.update(encoded)
        digest.update(struct.pack(">d", score))
    return digest.hexdigest()
