from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fmp.walkforward.artifacts import write_stage1_evidence
from fmp.walkforward.contracts import (
    EXPERIMENT_ID,
    PHASE6_CHECKPOINT_SHA,
    STAGE1_WINDOW,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)
from fmp.walkforward.gates import stage1_gate


UTC = timezone.utc


def stage1_rows(candidate_id: str = "session_breakout"):
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2025, 1, 1, tzinfo=UTC)
    rows = {}
    for slippage in (0.2, 0.5, 1.0):
        rows[slippage] = SimpleNamespace(
            candidate_id=candidate_id,
            window_name=STAGE1_WINDOW.name,
            slippage_pips=slippage,
            candidate_count=50,
            scored_candidate_count=45,
            directional_candidate_count=40,
            trade_count=40,
            net_pnl_usd=1_000.0,
            net_return=0.01,
            expectancy_usd=25.0,
            gross_profit_usd=2_000.0,
            gross_loss_usd=1_000.0,
            profit_factor=2.0,
            max_drawdown_fraction=0.04,
            warmup_range=(start - timedelta(days=7), start),
            opened_partition_keys=("15m:2023-12", "15m:2024-01"),
            scored_start_utc=start,
            scored_end_utc=end,
            refit_status="NOT_APPLICABLE_FIXED_RULE",
        )
    return rows


def write_valid_stage1(root: Path, candidate_id: str = "session_breakout") -> None:
    rows = stage1_rows(candidate_id)
    write_stage1_evidence(
        out_dir=root,
        candidate_id=candidate_id,
        code_commit="stage1abc",
        results_by_slippage=rows,
        gate=stage1_gate(rows),
    )


def rewrite_json(path: Path, mutate) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    mutate(value)
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n",
        encoding="utf-8",
    )


class Phase7CliTests(unittest.TestCase):
    def test_parsers_expose_no_free_form_date_parameter_symbol_or_final_bypass(self) -> None:
        from fmp.walkforward.cli import build_stage1_parser, build_stage2_parser

        forbidden = (
            "--start",
            "--end",
            "--buffer-pips",
            "--range-multiplier",
            "--timeframe",
            "--symbol",
            "--allow-final",
        )
        stage1_base = [
            "--dataset-root", "/data",
            "--processed-manifest", "/data/manifest.json",
            "--candidate", "session_breakout",
            "--out", "/out",
            "--code-commit", "abc",
        ]
        stage2_base = [*stage1_base, "--stage1-evidence", "/stage1"]
        for flag in forbidden:
            with self.assertRaises(SystemExit):
                build_stage1_parser().parse_args([*stage1_base, flag, "x"])
            with self.assertRaises(SystemExit):
                build_stage2_parser().parse_args([*stage2_base, flag, "x"])

    def test_stage1_runs_exact_three_costs_for_one_frozen_candidate(self) -> None:
        from fmp.walkforward.cli import run_stage1

        loaded = object()
        evaluations = []
        with tempfile.TemporaryDirectory() as tmp, patch(
            "fmp.walkforward.cli.load_phase7_bars", return_value=loaded
        ) as loader, patch(
            "fmp.walkforward.cli.evaluate_phase7_window"
        ) as evaluator, patch(
            "fmp.walkforward.cli.write_stage1_evidence", return_value={"ok": True}
        ) as writer:
            evaluator.side_effect = lambda **kwargs: evaluations.append(kwargs) or SimpleNamespace(
                candidate_id="session_breakout",
                window_name="stage1-2024",
                slippage_pips=kwargs["slippage_pips"],
                trade_count=40,
                net_return=0.01,
                expectancy_usd=1.0,
                profit_factor=2.0,
                max_drawdown_fraction=0.01,
            )
            run_stage1(
                dataset_root=Path(tmp),
                processed_manifest_path=Path(tmp) / "manifest.json",
                candidate_id="session_breakout",
                out_dir=Path(tmp) / "out",
                code_commit="abc",
            )
            loader.assert_called_once_with(
                dataset_root=Path(tmp),
                manifest_path=Path(tmp) / "manifest.json",
                candidate_id="session_breakout",
                window_name="stage1-2024",
            )
            self.assertEqual([call["slippage_pips"] for call in evaluations], [0.2, 0.5, 1.0])
            self.assertTrue(all(call["loaded"] is loaded for call in evaluations))
            writer.assert_called_once()

    def test_stage2_valid_stage1_pass_is_verified_before_any_window_load(self) -> None:
        from fmp.walkforward.cli import run_stage2

        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "stage1"
            write_valid_stage1(evidence)

            def loader(**kwargs):
                calls.append(("load", kwargs["window_name"]))
                return object()

            def evaluator(**kwargs):
                calls.append(("eval", kwargs["window_name"], kwargs["slippage_pips"]))
                return SimpleNamespace(
                    candidate_id="session_breakout",
                    window_name=kwargs["window_name"],
                    slippage_pips=kwargs["slippage_pips"],
                    trade_count=20,
                    net_return=0.01,
                    net_pnl_usd=100.0,
                    expectancy_usd=5.0,
                    gross_profit_usd=200.0,
                    gross_loss_usd=100.0,
                    profit_factor=2.0,
                    max_drawdown_fraction=0.01,
                )

            with patch("fmp.walkforward.cli.load_phase7_bars", side_effect=loader), patch(
                "fmp.walkforward.cli.evaluate_phase7_window", side_effect=evaluator
            ), patch("fmp.walkforward.cli.write_stage2_evidence", return_value={"ok": True}):
                run_stage2(
                    dataset_root=root,
                    processed_manifest_path=root / "manifest.json",
                    candidate_id="session_breakout",
                    stage1_evidence_dir=evidence,
                    out_dir=root / "stage2",
                    code_commit="def",
                )
            self.assertEqual([item[1] for item in calls if item[0] == "load"], [
                "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4",
                "2026-Q1", "2026-Q2", "2026-partial-Q3",
            ])
            self.assertEqual(len([item for item in calls if item[0] == "eval"]), 21)

    def test_stage2_rejects_invalid_or_tampered_stage1_before_data_io(self) -> None:
        from fmp.walkforward.cli import run_stage2

        cases = {
            "missing": None,
            "reject": lambda root: rewrite_json(root / "result.json", lambda v: v.update(status="STAGE1_REJECT")),
            "wrong_experiment": lambda root: rewrite_json(root / "stage1.json", lambda v: v.update(experiment_id="wrong")),
            "wrong_candidate": lambda root: rewrite_json(root / "stage1.json", lambda v: v["candidate"].update(candidate_id="volatility_breakout")),
            "wrong_manifest_sha": lambda root: rewrite_json(root / "stage1.json", lambda v: v.update(processed_manifest_sha256="0" * 64)),
            "wrong_phase6_sha": lambda root: rewrite_json(root / "stage1.json", lambda v: v.update(phase6_checkpoint_sha="0" * 40)),
            "tampered_constituent": lambda root: (root / "stage1.json").write_text("{}\n", encoding="utf-8"),
            "malformed_manifest": lambda root: (root / "manifest.json").write_text("{}\n", encoding="utf-8"),
            "wrong_range": lambda root: rewrite_json(root / "stage1.json", lambda v: v.update(scored_range={
                "start_utc": "2024-02-01T00:00:00Z",
                "end_exclusive_utc": "2025-01-01T00:00:00Z",
            })),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                evidence = root / "stage1"
                if name != "missing":
                    write_valid_stage1(evidence)
                    assert mutate is not None
                    mutate(evidence)
                opened = []
                with patch(
                    "fmp.walkforward.cli.load_phase7_bars",
                    side_effect=lambda **kwargs: opened.append(kwargs) or object(),
                ):
                    with self.assertRaises(ValueError):
                        run_stage2(
                            dataset_root=root,
                            processed_manifest_path=root / "manifest.json",
                            candidate_id="session_breakout",
                            stage1_evidence_dir=evidence,
                            out_dir=root / "stage2",
                            code_commit="def",
                        )
                self.assertEqual(opened, [])

    def test_stage1_verifier_returns_bound_authorization_identity(self) -> None:
        from fmp.walkforward.cli import verify_stage1_evidence

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_stage1(root)
            identity = verify_stage1_evidence(root, candidate_id="session_breakout")
            self.assertEqual(identity["experiment_id"], EXPERIMENT_ID)
            self.assertEqual(identity["candidate_id"], "session_breakout")
            self.assertEqual(identity["status"], "STAGE1_PASS")
            self.assertEqual(identity["phase6_checkpoint_sha"], PHASE6_CHECKPOINT_SHA)
            self.assertEqual(identity["processed_manifest_sha256"], USDJPY_PROCESSED_MANIFEST_SHA256)
            self.assertRegex(identity["manifest_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
