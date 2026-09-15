from __future__ import annotations

import hashlib
import json
import re
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from fmp.walkforward.contracts import (
    EXPERIMENT_ID,
    FROZEN_CANDIDATES,
    PHASE6_CHECKPOINT_SHA,
    STAGE1_WINDOW,
    STAGE2_WINDOWS,
    USDJPY_PHASE2_ARTIFACT_ID,
    USDJPY_PHASE2_ZIP_SHA256,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)
from fmp.walkforward.gates import stage1_gate, stage2_gate


UTC = timezone.utc


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=UTC)


def fake_window(
    *,
    candidate_id: str,
    window_name: str,
    slippage: float,
    start: datetime,
    end: datetime,
    pnl: float = 100.0,
    trades: int = 40,
):
    gross_profit = max(pnl, 0.0) + 200.0
    gross_loss = gross_profit - pnl
    return SimpleNamespace(
        candidate_id=candidate_id,
        window_name=window_name,
        slippage_pips=slippage,
        candidate_count=50,
        scored_candidate_count=45,
        directional_candidate_count=40,
        trade_count=trades,
        net_pnl_usd=pnl,
        net_return=pnl / 100_000.0,
        expectancy_usd=pnl / trades if trades else None,
        gross_profit_usd=gross_profit,
        gross_loss_usd=gross_loss,
        profit_factor=gross_profit / gross_loss if gross_loss else None,
        max_drawdown_fraction=0.04,
        warmup_range=(start - timedelta(days=7), start),
        opened_partition_keys=(
            f"15m:{(start - timedelta(days=7)).year:04d}-{(start - timedelta(days=7)).month:02d}",
            f"15m:{start.year:04d}-{start.month:02d}",
        ),
        scored_start_utc=start,
        scored_end_utc=end,
        refit_status="NOT_APPLICABLE_FIXED_RULE",
    )


def stage1_results(candidate_id: str = "session_breakout"):
    start = dt(2024, 1, 1)
    end = dt(2025, 1, 1)
    return {
        slippage: fake_window(
            candidate_id=candidate_id,
            window_name=STAGE1_WINDOW.name,
            slippage=slippage,
            start=start,
            end=end,
            pnl=1_000.0,
            trades=40,
        )
        for slippage in (0.2, 0.5, 1.0)
    }


def stage2_results(candidate_id: str = "session_breakout"):
    out = {}
    pnls = (100.0, 100.0, 100.0, 100.0, -10.0, -10.0, -10.0)
    for slippage in (0.2, 0.5, 1.0):
        rows = []
        for window, pnl in zip(STAGE2_WINDOWS, pnls, strict=True):
            start = datetime(window.start.year, window.start.month, window.start.day, tzinfo=UTC)
            end = datetime(
                window.end_exclusive.year,
                window.end_exclusive.month,
                window.end_exclusive.day,
                tzinfo=UTC,
            )
            rows.append(
                fake_window(
                    candidate_id=candidate_id,
                    window_name=window.name,
                    slippage=slippage,
                    start=start,
                    end=end,
                    pnl=pnl,
                    trades=15,
                )
            )
        out[slippage] = tuple(rows)
    return out


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Phase7ArtifactTests(unittest.TestCase):
    def test_stage1_evidence_records_exact_identity_gate_and_file_digests(self) -> None:
        from fmp.walkforward.artifacts import write_stage1_evidence

        rows = stage1_results()
        gate = stage1_gate(rows)
        self.assertTrue(gate.passed)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_stage1_evidence(
                out_dir=root,
                candidate_id="session_breakout",
                code_commit="abc123",
                results_by_slippage=rows,
                gate=gate,
            )
            stage1 = load_json(root / "stage1.json")
            result = load_json(root / "result.json")
            disk_manifest = load_json(root / "manifest.json")
            self.assertEqual(manifest, disk_manifest)

            for payload in (stage1, result, disk_manifest):
                self.assertEqual(payload["experiment_id"], EXPERIMENT_ID)
                self.assertEqual(payload["code_commit"], "abc123")
                self.assertEqual(payload["phase6_checkpoint_tag"], "fmp-v1-phase6-models")
                self.assertEqual(payload["phase6_checkpoint_sha"], PHASE6_CHECKPOINT_SHA)
                self.assertEqual(payload["phase2_artifact_id"], USDJPY_PHASE2_ARTIFACT_ID)
                self.assertEqual(payload["phase2_zip_sha256"], USDJPY_PHASE2_ZIP_SHA256)
                self.assertEqual(
                    payload["processed_manifest_sha256"], USDJPY_PROCESSED_MANIFEST_SHA256
                )
                self.assertEqual(payload["canonical_schema_version"], "fmp-canonical-1m-v1")
                self.assertEqual(payload["candidate"]["candidate_id"], "session_breakout")
                self.assertEqual(payload["candidate"]["strategy_version"], 1)
                self.assertEqual(payload["candidate"]["symbol"], "USDJPY")
                self.assertEqual(payload["candidate"]["timeframe"], "15m")
                self.assertEqual(
                    payload["candidate"]["parameters"],
                    dict(FROZEN_CANDIDATES["session_breakout"].parameters),
                )

            self.assertEqual(stage1["requested_risk_fraction"], 0.0025)
            self.assertEqual(stage1["starting_equity_usd"], 100_000.0)
            self.assertEqual(stage1["slippage_scenarios"], [0.2, 0.5, 1.0])
            self.assertEqual(stage1["commission_model"], {"model": "zero_commission"})
            self.assertEqual(stage1["financing_model"], {"model": "zero_financing"})
            self.assertEqual(stage1["scored_range"], {
                "start_utc": "2024-01-01T00:00:00Z",
                "end_exclusive_utc": "2025-01-01T00:00:00Z",
            })
            self.assertEqual(stage1["gate"]["passed"], True)
            self.assertEqual(stage1["gate"]["criteria"], dict(gate.criteria))
            self.assertEqual(stage1["status"], "STAGE1_PASS")
            self.assertEqual(result["status"], "STAGE1_PASS")
            self.assertEqual(result["candidate_statuses"], {"session_breakout": "PASS"})
            self.assertTrue(result["stage2_authorized"])

            records = {item["path"]: item for item in disk_manifest["artifacts"]}
            self.assertEqual(set(records), {"result.json", "stage1.json"})
            for name, record in records.items():
                self.assertEqual(record["sha256"], file_sha(root / name))
                self.assertEqual(record["size_bytes"], (root / name).stat().st_size)

    def test_stage1_rejection_is_durable_evidence_not_writer_failure(self) -> None:
        from fmp.walkforward.artifacts import write_stage1_evidence

        rows = stage1_results()
        rows[0.2].trade_count = 39
        gate = stage1_gate(rows)
        self.assertFalse(gate.passed)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_stage1_evidence(
                out_dir=root,
                candidate_id="session_breakout",
                code_commit="abc123",
                results_by_slippage=rows,
                gate=gate,
            )
            result = load_json(root / "result.json")
            self.assertEqual(result["status"], "STAGE1_REJECT")
            self.assertEqual(result["candidate_statuses"], {"session_breakout": "REJECT"})
            self.assertFalse(result["stage2_authorized"])

    def test_stage2_evidence_preserves_stage1_identity_windows_aggregates_and_decision(self) -> None:
        from fmp.walkforward.artifacts import write_stage2_evidence

        rows = stage2_results()
        gate = stage2_gate(rows)
        self.assertTrue(gate.passed)
        stage1_identity = {
            "experiment_id": EXPERIMENT_ID,
            "candidate_id": "session_breakout",
            "status": "STAGE1_PASS",
            "code_commit": "stage1abc",
            "phase6_checkpoint_sha": PHASE6_CHECKPOINT_SHA,
            "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
            "manifest_sha256": "a" * 64,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_stage2_evidence(
                out_dir=root,
                candidate_id="session_breakout",
                code_commit="def456",
                results_by_slippage=rows,
                gate=gate,
                stage1_identity=stage1_identity,
            )
            windows = load_json(root / "windows.json")
            result = load_json(root / "result.json")
            manifest = load_json(root / "manifest.json")
            self.assertEqual(windows["stage1_identity"], stage1_identity)
            self.assertEqual(result["stage1_identity"], stage1_identity)
            self.assertEqual(manifest["stage1_identity"], stage1_identity)
            self.assertEqual(len(windows["windows_by_slippage"]["0.2"]), 7)
            self.assertEqual(
                [row["window_name"] for row in windows["windows_by_slippage"]["0.2"]],
                [window.name for window in STAGE2_WINDOWS],
            )
            self.assertEqual(windows["gate"]["criteria"], dict(gate.criteria))
            self.assertIn("aggregate_by_slippage", windows)
            self.assertEqual(result["status"], "PHASE7_PROMOTE_TO_SHADOW_DESIGN")
            self.assertEqual(result["candidate_statuses"], {"session_breakout": "PASS"})
            records = {item["path"]: item for item in manifest["artifacts"]}
            self.assertEqual(set(records), {"result.json", "windows.json"})
            for name, record in records.items():
                self.assertEqual(record["sha256"], file_sha(root / name))

    def test_stage2_rejection_is_complete_reject_not_execution_error(self) -> None:
        from fmp.walkforward.artifacts import write_stage2_evidence

        rows = stage2_results()
        rows[0.2] = tuple(
            SimpleNamespace(**{**row.__dict__, "trade_count": 1}) for row in rows[0.2]
        )
        gate = stage2_gate(rows)
        self.assertFalse(gate.passed)
        stage1_identity = {
            "experiment_id": EXPERIMENT_ID,
            "candidate_id": "session_breakout",
            "status": "STAGE1_PASS",
            "code_commit": "stage1abc",
            "phase6_checkpoint_sha": PHASE6_CHECKPOINT_SHA,
            "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
            "manifest_sha256": "b" * 64,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_stage2_evidence(
                out_dir=root,
                candidate_id="session_breakout",
                code_commit="def456",
                results_by_slippage=rows,
                gate=gate,
                stage1_identity=stage1_identity,
            )
            result = load_json(root / "result.json")
            self.assertEqual(result["status"], "PHASE7_COMPLETE_REJECT")
            self.assertEqual(result["candidate_statuses"], {"session_breakout": "REJECT"})

    def test_evidence_is_byte_deterministic_and_contains_no_runtime_ephemera(self) -> None:
        from fmp.walkforward.artifacts import write_stage1_evidence

        rows = stage1_results()
        gate = stage1_gate(rows)
        with tempfile.TemporaryDirectory() as left_tmp, tempfile.TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            for root in (left, right):
                write_stage1_evidence(
                    out_dir=root,
                    candidate_id="session_breakout",
                    code_commit="abc123",
                    results_by_slippage=rows,
                    gate=gate,
                )
            for name in ("stage1.json", "result.json", "manifest.json"):
                left_bytes = (left / name).read_bytes()
                right_bytes = (right / name).read_bytes()
                self.assertEqual(left_bytes, right_bytes)
                text = left_bytes.decode("utf-8")
                self.assertNotIn(left.as_posix(), text)
                self.assertNotIn(right.as_posix(), text)
                self.assertNotRegex(
                    text,
                    re.compile(
                        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
                        r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
                    ),
                )
                self.assertNotIn("generated_at", text)
                self.assertNotIn("hostname", text)


if __name__ == "__main__":
    unittest.main()
