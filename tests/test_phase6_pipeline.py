from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import polars as pl

from fmp.contracts import Direction
from fmp.models.contracts import ModelFamily
from fmp.models.data import MODEL_INPUT_COLUMNS
from fmp.models.evaluation import FinancialResult, GateResult
from fmp.models.labels import LabelResult
from fmp.strategies.contracts import SignalCandidate

UTC = timezone.utc


def _candidates(split_name: str, *, count: int = 40) -> tuple[SignalCandidate, ...]:
    year = {"fit": 2017, "selection": 2019, "validation": 2021}[split_name]
    base = datetime(year, 1, 2, 10, 0, tzinfo=UTC)
    out = []
    for index in range(count):
        observation = base + timedelta(minutes=30 * index)
        direction = Direction.LONG if index % 2 == 0 else Direction.SHORT
        out.append(
            SignalCandidate(
                candidate_id=f"{split_name.upper()}-{index:03d}",
                symbol="USDJPY",
                observation_bar_timestamp_utc=observation,
                signal_known_timestamp_utc=observation + timedelta(minutes=15),
                direction=direction,
                stop_price=149.0 if direction is Direction.LONG else 151.0,
                target_price=151.0 if direction is Direction.LONG else 149.0,
                latest_exit_timestamp_utc=observation + timedelta(hours=2),
                reason_code="SETUP",
                metadata={"split": split_name},
            )
        )
    return tuple(out)


def _model_frame(candidates: tuple[SignalCandidate, ...], *, offset: float = 0.0) -> pl.DataFrame:
    rows = []
    for index, candidate in enumerate(candidates):
        row: dict[str, object] = {"candidate_id": candidate.candidate_id}
        for column_index, name in enumerate(MODEL_INPUT_COLUMNS):
            if name == "signal_direction":
                row[name] = 1 if candidate.direction is Direction.LONG else -1
            else:
                row[name] = float(index + 1) + float(column_index) / 100.0 + offset
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


def _financial(candidates: tuple[SignalCandidate, ...], slippage_pips: float) -> FinancialResult:
    directional = sum(candidate.direction in {Direction.LONG, Direction.SHORT} for candidate in candidates)
    metrics = {
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
    }
    return FinancialResult(
        slippage_pips=slippage_pips,
        candidate_count=len(candidates),
        directional_candidate_count=directional,
        metrics=metrics,
        run_identity={"synthetic": True, "slippage_pips": slippage_pips},
    )


class Phase6PipelineTests(unittest.TestCase):
    def test_selection_is_frozen_before_validation_and_models_fit_exactly_once(self) -> None:
        import fmp.models.evaluation as evaluation
        from fmp.models.estimators import fit_estimator as real_fit_estimator

        events: list[str] = []
        candidates_by_split = {name: _candidates(name) for name in ("fit", "selection", "validation")}

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"

            def bars_loader(**kwargs):
                split = kwargs["split"]
                events.append(f"bars:{split.name}")
                if split.name == "validation":
                    self.assertTrue((out_dir / "selection.json").is_file())
                return SimpleNamespace(bars=(split.name,), excluded_incomplete_count=0, eligible_utc_dates=())

            def feature_loader(**kwargs):
                split = kwargs["split"]
                events.append(f"features:{split.name}")
                if split.name == "validation":
                    self.assertTrue((out_dir / "selection.json").is_file())
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
                return _model_frame(tuple(candidates), offset={"fit": 0.0, "selection": 10.0, "validation": 20.0}[split_name])

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

            self.assertEqual(fit_spy.call_count, 2)
            self.assertEqual(events[:4], ["bars:fit", "features:fit", "bars:selection", "features:selection"])
            self.assertIn("bars:validation", events)
            self.assertGreater(events.index("bars:validation"), events.index("features:selection"))
            self.assertTrue((out_dir / "selection.json").is_file())
            selected = result["selection"]["selected_variant"]
            self.assertIn(selected["model_family"], {family.value for family in ModelFamily})
            self.assertIn(selected["retained_fraction"], {0.75, 0.50, 0.25})
            self.assertEqual(result["validation"]["status"], "PROMOTE_ML_FILTER")


if __name__ == "__main__":
    unittest.main()
