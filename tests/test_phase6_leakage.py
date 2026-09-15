from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import polars as pl

from fmp.contracts import Direction
from fmp.models.data import MODEL_INPUT_COLUMNS
from fmp.models.evaluation import FinancialResult, GateResult
from fmp.models.labels import LabelResult
from fmp.strategies.contracts import SignalCandidate

UTC = timezone.utc


def _candidates(split_name: str, *, count: int = 40) -> tuple[SignalCandidate, ...]:
    year = {"fit": 2017, "selection": 2019, "validation": 2021}[split_name]
    base = datetime(year, 2, 1, 9, 0, tzinfo=UTC)
    return tuple(
        SignalCandidate(
            candidate_id=f"{split_name.upper()}-{index:03d}",
            symbol="USDJPY",
            observation_bar_timestamp_utc=base + timedelta(minutes=30 * index),
            signal_known_timestamp_utc=base + timedelta(minutes=30 * index + 15),
            direction=Direction.LONG if index % 2 == 0 else Direction.SHORT,
            stop_price=149.0 if index % 2 == 0 else 151.0,
            target_price=151.0 if index % 2 == 0 else 149.0,
            latest_exit_timestamp_utc=base + timedelta(minutes=30 * index + 120),
            reason_code="SETUP",
            metadata={"split": split_name},
        )
        for index in range(count)
    )


def _frame(candidates: tuple[SignalCandidate, ...], *, offset: float) -> pl.DataFrame:
    rows = []
    for index, candidate in enumerate(candidates):
        row: dict[str, object] = {"candidate_id": candidate.candidate_id}
        for column_index, name in enumerate(MODEL_INPUT_COLUMNS):
            if name == "signal_direction":
                row[name] = 1 if candidate.direction is Direction.LONG else -1
            else:
                row[name] = float(index + 1) + column_index / 100.0 + offset
        rows.append(row)
    return pl.DataFrame(rows).select(["candidate_id", *MODEL_INPUT_COLUMNS])


def _labels(candidates: tuple[SignalCandidate, ...]) -> tuple[LabelResult, ...]:
    return tuple(
        LabelResult(
            candidate_id=candidate.candidate_id,
            label=index % 2,
            reason_code="TARGET_BEFORE_STOP" if index % 2 else "STOP_BEFORE_TARGET",
            resolved_timestamp_utc=candidate.signal_known_timestamp_utc + timedelta(minutes=15),
        )
        for index, candidate in enumerate(sorted(candidates, key=lambda item: item.candidate_id))
    )


def _financial(candidates: tuple[SignalCandidate, ...], slippage: float) -> FinancialResult:
    directional = sum(candidate.direction in {Direction.LONG, Direction.SHORT} for candidate in candidates)
    return FinancialResult(
        slippage_pips=slippage,
        candidate_count=len(candidates),
        directional_candidate_count=directional,
        metrics={
            "phase3_metrics": {
                "trade_count": directional,
                "net_return": 0.02,
                "expectancy_usd": 20.0,
                "profit_factor": 1.5,
                "max_drawdown_fraction": 0.05,
            },
            "calendar_year_breakdown": {
                "2021": {"net_pnl_usd": 100.0},
                "2022": {"net_pnl_usd": 100.0},
                "2023": {"net_pnl_usd": 100.0},
            },
        },
        run_identity={"synthetic": True},
    )


class Phase6LeakageTests(unittest.TestCase):
    def _run(self, *, future_offset: float, out_dir: Path):
        import fmp.models.evaluation as evaluation
        from fmp.models.estimators import fit_estimator as real_fit_estimator

        candidates_by_split = {name: _candidates(name) for name in ("fit", "selection", "validation")}

        def bars_loader(**kwargs):
            split = kwargs["split"]
            return SimpleNamespace(bars=(split.name,), excluded_incomplete_count=0, eligible_utc_dates=())

        def feature_loader(**kwargs):
            split = kwargs["split"]
            return SimpleNamespace(
                frame=pl.DataFrame(),
                feature_manifest_sha256=f"feature-{split.name}",
                processed_manifest_sha256="processed",
                phase5_checkpoint_sha="checkpoint",
                phase5_code_commit="phase5",
                opened_artifacts=(),
            )

        def generate(_strategy_id, bars):
            return candidates_by_split[str(bars[0])]

        def join(candidates, _features):
            split_name = str(candidates[0].metadata["split"])
            offset = 0.0 if split_name == "fit" else future_offset
            return _frame(tuple(candidates), offset=offset)

        def label_batch(candidates, _bars):
            return _labels(tuple(candidates))

        def backtest(**kwargs):
            return _financial(tuple(kwargs["candidates"]), float(kwargs["slippage_pips"]))

        always_pass = GateResult(passed=True, criteria={"synthetic": True})
        with (
            patch.object(evaluation, "load_processed_bars_for_split", side_effect=bars_loader),
            patch.object(evaluation, "load_phase6_feature_frame", side_effect=feature_loader),
            patch.object(evaluation, "generate_frozen_candidates", side_effect=generate),
            patch.object(evaluation, "join_directional_candidates_to_features", side_effect=join),
            patch.object(evaluation, "label_candidates", side_effect=label_batch),
            patch.object(evaluation, "run_candidate_backtest", side_effect=backtest),
            patch.object(evaluation, "selection_gate", return_value=always_pass),
            patch.object(evaluation, "validation_gate", return_value=always_pass),
            patch.object(evaluation, "fit_estimator", wraps=real_fit_estimator) as fit_spy,
        ):
            result = evaluation.run_phase6_strategy_cell(
                dataset_root=Path("/synthetic/processed"),
                processed_manifest_path=Path("/synthetic/processed-manifest.json"),
                feature_root=Path("/synthetic/features"),
                feature_manifest_path=Path("/synthetic/feature-manifest.json"),
                strategy_id="session_breakout",
                out_dir=out_dir,
                code_commit="abc123",
            )
        return result, fit_spy.call_count

    def test_future_perturbation_cannot_change_fit_state_scores_or_cutoffs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first, first_fit_count = self._run(future_offset=10.0, out_dir=root / "a")
            second, second_fit_count = self._run(future_offset=100000.0, out_dir=root / "b")

        self.assertEqual(first_fit_count, 2)
        self.assertEqual(second_fit_count, 2)
        for family in ("logistic_regression", "hist_gradient_boosting"):
            left = first["selection"]["models"][family]
            right = second["selection"]["models"][family]
            self.assertEqual(left["preprocessing"], right["preprocessing"])
            self.assertEqual(left["fit_score_digest"], right["fit_score_digest"])
            self.assertEqual(left["cutoffs"], right["cutoffs"])


if __name__ == "__main__":
    unittest.main()
