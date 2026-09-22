from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from fmp.portfolio.challenger_round1 import (
    EXP013_STAGE_A_AUTHORIZATION_PROTOCOL,
    aggregate_exp013_stage_a_gates,
    write_exp013_stage_a_cell_artifacts,
    write_exp013_stage_a_authorization_artifacts,
)


COMMIT = "a" * 40


def _gate(symbol: str, timeframe: str, *, survivors: tuple[str, ...] = ()) -> dict[str, object]:
    cell_index = (
        ("EURUSD", "GBPUSD", "USDJPY").index(symbol) * 3
        + ("5m", "15m", "1h").index(timeframe)
    )
    fingerprints = tuple(
        f"{cell_index * 10 + index:064x}" for index in range(1, 5)
    )
    return {
        "protocol": "fmp-phase8a-exp013-stage-a-gate-v1",
        "experiment_id": "EXP-20260922-013",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "runner_code_commit": COMMIT,
        "survivor_fingerprints": list(survivors),
        "config_gates": {
            fingerprint: {
                "parameters": {
                    "body_fraction_threshold": 0.5 if index < 3 else 0.7,
                    "target_r_multiple": 1.0 if index % 2 else 1.5,
                },
                "mandatory_profitability_drawdown_pass": fingerprint in survivors,
                "sample_pass": fingerprint in survivors,
                "neighbor_pass": fingerprint in survivors,
                "passing_neighbor_fingerprints": [],
                "stage_a_survivor": fingerprint in survivors,
            }
            for index, fingerprint in enumerate(fingerprints, start=1)
        },
    }


class Phase8AExp013StageAArtifactsTests(unittest.TestCase):
    def test_cell_artifacts_are_deterministic_and_bind_both_frozen_splits(self) -> None:
        development = {
            "protocol": "fmp-phase8a-exp013-stage-a-cell-v1",
            "split_name": "development",
            "range_start": "2015-01-01",
            "range_end_exclusive": "2021-01-01",
            "runner_code_commit": COMMIT,
            "promotion_authorized": False,
        }
        validation = {
            "protocol": "fmp-phase8a-exp013-stage-a-cell-v1",
            "split_name": "validation",
            "range_start": "2021-01-01",
            "range_end_exclusive": "2024-01-01",
            "runner_code_commit": COMMIT,
            "promotion_authorized": False,
        }
        gate = _gate("EURUSD", "15m")

        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            left_manifest = write_exp013_stage_a_cell_artifacts(
                development=development,
                validation=validation,
                gate=gate,
                out_dir=left,
            )
            right_manifest = write_exp013_stage_a_cell_artifacts(
                development=development,
                validation=validation,
                gate=gate,
                out_dir=right,
            )
            for name in ("development.json", "validation.json", "gate.json", "manifest.json"):
                self.assertEqual((left / name).read_bytes(), (right / name).read_bytes())
            self.assertEqual(left_manifest, right_manifest)
            self.assertEqual(
                left_manifest["protocol"],
                "fmp-phase8a-exp013-stage-a-cell-artifacts-v1",
            )

    def test_authorization_requires_exact_nine_cells_and_same_runner_commit(self) -> None:
        gates = [
            _gate(symbol, timeframe)
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
        ]
        result = aggregate_exp013_stage_a_gates(gates)
        self.assertEqual(result["protocol"], EXP013_STAGE_A_AUTHORIZATION_PROTOCOL)
        self.assertEqual(result["cell_count"], 9)
        self.assertEqual(result["strategy_identity_count"], 36)
        self.assertEqual(result["survivor_count"], 0)
        self.assertFalse(result["stage_b_source_open_authorized"])
        self.assertFalse(result["promotion_authorized"])

        with self.assertRaises(ValueError):
            aggregate_exp013_stage_a_gates(gates[:-1])

        bad = list(gates)
        bad[-1] = dict(bad[-1]) | {"runner_code_commit": "b" * 40}
        with self.assertRaises(ValueError):
            aggregate_exp013_stage_a_gates(bad)

    def test_authorization_is_bound_to_exact_survivor_fingerprints(self) -> None:
        survivor = f"{1:064x}"
        gates = [
            _gate(
                symbol,
                timeframe,
                survivors=(survivor,) if (symbol, timeframe) == ("EURUSD", "5m") else (),
            )
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
        ]
        result = aggregate_exp013_stage_a_gates(gates)
        self.assertTrue(result["stage_b_source_open_authorized"])
        self.assertEqual(result["survivor_fingerprints"], [survivor])
        self.assertEqual(result["survivor_count"], 1)

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_exp013_stage_a_authorization_artifacts(result, root)
            stored = json.loads((root / "authorization.json").read_text(encoding="utf-8"))
            self.assertEqual(stored["survivor_fingerprints"], [survivor])
            self.assertFalse(stored["promotion_authorized"])
            self.assertEqual(
                manifest["protocol"],
                "fmp-phase8a-exp013-stage-a-authorization-artifacts-v1",
            )


if __name__ == "__main__":
    unittest.main()
