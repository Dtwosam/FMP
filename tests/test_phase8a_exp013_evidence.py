from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.portfolio.challenger_round1 import (
    EXP013_STAGE_A_CELL_PROTOCOL,
    EXP013_STAGE_A_GATE_PROTOCOL,
)
from fmp.portfolio.challenger_round1_evidence import (
    EXP013_STAGE_A_AUTHORIZATION_PROTOCOL,
    EXP013_STAGE_A_CELL_EVIDENCE_PROTOCOL,
    build_exp013_stage_a_authorization,
    build_exp013_stage_a_cell_evidence,
    write_exp013_stage_a_authorization,
    write_exp013_stage_a_cell_evidence,
)
from fmp.portfolio.challengers import (
    EXP013_ID,
    build_opening_range_momentum_challengers,
)
from fmp.portfolio.research_data import PHASE8A_RETROSPECTIVE_LABEL


COMMIT = "a" * 40


def _cell(symbol: str, timeframe: str, split_name: str) -> dict[str, object]:
    records = [
        item
        for item in build_opening_range_momentum_challengers(code_commit=COMMIT)
        if item.strategy.symbol == symbol and item.strategy.timeframe == timeframe
    ]
    rows = []
    for record in records:
        for slippage in (0.2, 0.5, 1.0):
            rows.append(
                {
                    "strategy_fingerprint": record.strategy.fingerprint,
                    "strategy_identity_json": record.strategy.identity_json,
                    "family": record.strategy.family,
                    "version": record.strategy.version,
                    "parameters_json": record.strategy.parameters_json,
                    "historical_lifecycle": record.lifecycle.value,
                    "historical_evidence_id": record.evidence_id,
                    "slippage_pips": slippage,
                    "candidate_sha256": "c" * 64,
                    "run_identity": {
                        "requested_start_utc": datetime(
                            2015 if split_name == "development" else 2021,
                            1,
                            1,
                            tzinfo=timezone.utc,
                        ),
                        "code_commit": COMMIT,
                    },
                    "metrics": {
                        "trade_count": 120,
                        "phase3_metrics": {
                            "net_return": 0.02,
                            "expectancy_usd": 2.0,
                            "profit_factor": 1.10,
                            "max_drawdown_fraction": 0.02,
                        },
                    },
                }
            )
    return {
        "protocol": EXP013_STAGE_A_CELL_PROTOCOL,
        "experiment_id": EXP013_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "split_name": split_name,
        "range_start": "2015-01-01" if split_name == "development" else "2021-01-01",
        "range_end_exclusive": "2021-01-01" if split_name == "development" else "2024-01-01",
        "runner_code_commit": COMMIT,
        "processed_manifest_sha256": {"EURUSD": "e", "GBPUSD": "g", "USDJPY": "u"}[symbol] * 64,
        "opened_artifact_months": ["fixture"],
        "strategy_identity_count": 4,
        "scenario_run_count": 12,
        "slippage_scenarios": [0.2, 0.5, 1.0],
        "rows": rows,
    }


def _gate(symbol: str, timeframe: str, survivors: list[str]) -> dict[str, object]:
    records = [
        item
        for item in build_opening_range_momentum_challengers(code_commit=COMMIT)
        if item.strategy.symbol == symbol and item.strategy.timeframe == timeframe
    ]
    return {
        "protocol": EXP013_STAGE_A_GATE_PROTOCOL,
        "experiment_id": EXP013_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "runner_code_commit": COMMIT,
        "survivor_fingerprints": survivors,
        "config_gates": {
            item.strategy.fingerprint: {
                "stage_a_survivor": item.strategy.fingerprint in survivors,
            }
            for item in records
        },
    }


def _cell_evidence(symbol: str, timeframe: str, survivor_count: int = 1) -> dict[str, object]:
    records = [
        item
        for item in build_opening_range_momentum_challengers(code_commit=COMMIT)
        if item.strategy.symbol == symbol and item.strategy.timeframe == timeframe
    ]
    survivors = [item.strategy.fingerprint for item in records[:survivor_count]]
    return build_exp013_stage_a_cell_evidence(
        development=_cell(symbol, timeframe, "development"),
        validation=_cell(symbol, timeframe, "validation"),
        gate=_gate(symbol, timeframe, survivors),
    )


class Phase8AExp013EvidenceTests(unittest.TestCase):
    def test_cell_evidence_binds_both_splits_gate_and_exact_four_identities(self) -> None:
        evidence = _cell_evidence("EURUSD", "15m", survivor_count=2)

        self.assertEqual(evidence["protocol"], EXP013_STAGE_A_CELL_EVIDENCE_PROTOCOL)
        self.assertEqual(evidence["experiment_id"], EXP013_ID)
        self.assertFalse(evidence["promotion_authorized"])
        self.assertFalse(evidence["untouched_oos"])
        self.assertEqual(evidence["symbol"], "EURUSD")
        self.assertEqual(evidence["timeframe"], "15m")
        self.assertEqual(evidence["strategy_identity_count"], 4)
        self.assertEqual(len(evidence["strategy_fingerprints"]), 4)
        self.assertEqual(len(evidence["survivor_fingerprints"]), 2)
        self.assertEqual(evidence["runner_code_commit"], COMMIT)

    def test_cell_evidence_rejects_gate_survivor_not_in_exact_cell(self) -> None:
        with self.assertRaises(ValueError):
            build_exp013_stage_a_cell_evidence(
                development=_cell("EURUSD", "15m", "development"),
                validation=_cell("EURUSD", "15m", "validation"),
                gate=_gate("EURUSD", "15m", ["f" * 64]),
            )

    def test_authorization_requires_all_nine_cells_and_all_36_identities(self) -> None:
        cells = [
            _cell_evidence(symbol, timeframe, survivor_count=1)
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
        ]
        authorization = build_exp013_stage_a_authorization(cells)

        self.assertEqual(
            authorization["protocol"],
            EXP013_STAGE_A_AUTHORIZATION_PROTOCOL,
        )
        self.assertEqual(authorization["cell_count"], 9)
        self.assertEqual(authorization["strategy_identity_count"], 36)
        self.assertEqual(authorization["survivor_count"], 9)
        self.assertEqual(len(authorization["survivor_fingerprints"]), 9)
        self.assertTrue(authorization["stage_b_source_open_authorized"])
        self.assertFalse(authorization["promotion_authorized"])
        self.assertEqual(
            set(authorization["processed_manifest_sha256_by_symbol"]),
            {"EURUSD", "GBPUSD", "USDJPY"},
        )

    def test_authorization_fails_closed_for_missing_or_duplicate_cell(self) -> None:
        cells = [
            _cell_evidence(symbol, timeframe)
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
        ]
        with self.assertRaises(ValueError):
            build_exp013_stage_a_authorization(cells[:-1])
        with self.assertRaises(ValueError):
            build_exp013_stage_a_authorization(cells[:-1] + [cells[0]])

    def test_zero_survivors_does_not_authorize_stage_b_source_open(self) -> None:
        cells = [
            _cell_evidence(symbol, timeframe, survivor_count=0)
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
        ]
        authorization = build_exp013_stage_a_authorization(cells)
        self.assertEqual(authorization["survivor_count"], 0)
        self.assertFalse(authorization["stage_b_source_open_authorized"])

    def test_artifact_writers_are_deterministic_and_utc_safe(self) -> None:
        cell = _cell_evidence("USDJPY", "1h")
        cells = [
            _cell_evidence(symbol, timeframe)
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
        ]
        authorization = build_exp013_stage_a_authorization(cells)

        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            cell_left = write_exp013_stage_a_cell_evidence(cell, left / "cell")
            cell_right = write_exp013_stage_a_cell_evidence(cell, right / "cell")
            auth_left = write_exp013_stage_a_authorization(
                authorization,
                left / "auth",
            )
            auth_right = write_exp013_stage_a_authorization(
                authorization,
                right / "auth",
            )

            self.assertEqual(cell_left, cell_right)
            self.assertEqual(auth_left, auth_right)
            self.assertEqual(
                (left / "cell" / "cell-evidence.json").read_bytes(),
                (right / "cell" / "cell-evidence.json").read_bytes(),
            )
            stored = json.loads(
                (left / "cell" / "cell-evidence.json").read_text(encoding="utf-8")
            )
            first_row = stored["development"]["rows"][0]
            self.assertEqual(
                first_row["run_identity"]["requested_start_utc"],
                "2015-01-01T00:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
