from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.shadow.cli import build_parser, main
from fmp.shadow.evidence import EvidenceWriter
from fmp.shadow.mt5_bridge import BridgeStartRecord, BridgeTickRecord
from fmp.shadow.replay import ReplayMismatchError, replay_segment
from fmp.shadow.runner import ShadowRunner


UTC = timezone.utc
START = datetime(2026, 1, 15, 0, 0, tzinfo=UTC)
CODE_COMMIT = "a" * 40
ACCOUNT_FINGERPRINT = "b" * 64
BRIDGE_SESSION_ID = "c" * 64
SERVER = "FPMarketsSC-Demo2"
PROTOCOL = "fmp-mt5-demo-file-bridge-v1"


def bridge_start() -> BridgeStartRecord:
    return BridgeStartRecord(
        protocol=PROTOCOL,
        bridge_session_id=BRIDGE_SESSION_ID,
        symbol="USDJPY",
        server=SERVER,
        account_fingerprint=ACCOUNT_FINGERPRINT,
        account_mode="DEMO",
        bridge_start_time_msc=int(START.timestamp() * 1000) - 1,
    )


def bridge_tick(when: datetime, *, bid: float, ask: float) -> BridgeTickRecord:
    return BridgeTickRecord(
        protocol=PROTOCOL,
        bridge_session_id=BRIDGE_SESSION_ID,
        symbol="USDJPY",
        server=SERVER,
        account_fingerprint=ACCOUNT_FINGERPRINT,
        source_time_msc=int(when.timestamp() * 1000),
        bid=bid,
        ask=ask,
        flags=6,
    )


def build_live_segment(root: Path) -> None:
    writer = EvidenceWriter(
        root,
        code_commit=CODE_COMMIT,
        bridge_source_commit=CODE_COMMIT,
        bridge_session_id=BRIDGE_SESSION_ID,
        server=SERVER,
        account_fingerprint_sha256=ACCOUNT_FINGERPRINT,
        run_start_utc=START,
    )
    runner = ShadowRunner(evidence=writer)
    runner.start(now_utc=START, restarted=False)
    runner.process_bridge_record(
        bridge_start(),
        received_at_utc=START,
        receive_monotonic_ns=0,
    )

    for minute in range(497):
        when = START + timedelta(minutes=minute)
        if minute < 240:
            bid, ask = 139.80, 139.82
        elif minute < 480:
            bid, ask = 140.00, 140.02
        elif minute < 496:
            bid, ask = 140.40, 140.42
        else:
            bid, ask = 140.90, 140.92
        runner.process_bridge_record(
            bridge_tick(when, bid=bid, ask=ask),
            received_at_utc=when,
            receive_monotonic_ns=(minute + 1) * 1_000_000_000,
        )

    runner.disconnect(now_utc=START + timedelta(minutes=497), reason="bridge_end")


def jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class Phase8ReplayTests(unittest.TestCase):
    def test_replay_reproduces_all_deterministic_derived_artifacts_and_financial_metrics(self) -> None:
        with TemporaryDirectory() as tmp:
            segment = Path(tmp) / "segment"
            build_live_segment(segment)
            original = {
                name: (segment / name).read_bytes()
                for name in (
                    "normalized.jsonl",
                    "bars.jsonl",
                    "decisions.jsonl",
                    "scenarios.jsonl",
                )
            }

            first = replay_segment(segment)
            first_replay_bytes = (segment / "replay.json").read_bytes()
            first_manifest_bytes = (segment / "manifest.json").read_bytes()
            second = replay_segment(segment)

            self.assertEqual(first, second)
            self.assertTrue(first["match"])
            self.assertEqual(first["compared_files"], sorted(original))
            self.assertEqual(len(first["replay_result_digest"]), 64)
            self.assertEqual((segment / "replay.json").read_bytes(), first_replay_bytes)
            self.assertEqual((segment / "manifest.json").read_bytes(), first_manifest_bytes)
            self.assertEqual(
                {name: (segment / name).read_bytes() for name in original},
                original,
            )

            scenario_records = jsonl(segment / "scenarios.jsonl")
            metrics = [record for record in scenario_records if record.get("event") == "financial_metrics"]
            self.assertEqual(len(metrics), 3)
            self.assertEqual({record["slippage_pips"] for record in metrics}, {0.2, 0.5, 1.0})
            self.assertTrue(all(record["metrics"]["trade_count"] == 1 for record in metrics))

            manifest = json.loads((segment / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["protocol"], "fmp-phase8-shadow-evidence-v2")
            self.assertEqual(manifest["bridge_session_id"], BRIDGE_SESSION_ID)
            self.assertEqual(manifest["server"], SERVER)
            self.assertEqual(manifest["replay_result_digest"], first["replay_result_digest"])

    def test_replay_refuses_acceptance_when_a_derived_artifact_was_tampered(self) -> None:
        with TemporaryDirectory() as tmp:
            segment = Path(tmp) / "segment"
            build_live_segment(segment)
            decisions = segment / "decisions.jsonl"
            decisions.write_bytes(decisions.read_bytes() + b'{"tampered":true}\n')

            with self.assertRaises(ReplayMismatchError):
                replay_segment(segment)
            self.assertFalse((segment / "manifest.json").exists())
            replay_record = json.loads((segment / "replay.json").read_text(encoding="utf-8"))
            self.assertFalse(replay_record["match"])
            self.assertIn("decisions.jsonl", replay_record["mismatched_files"])

    def test_replay_ignores_runtime_receive_wall_clock_for_decision_and_financial_bytes(self) -> None:
        with TemporaryDirectory() as tmp:
            segment = Path(tmp) / "segment"
            build_live_segment(segment)
            raw_records = jsonl(segment / "raw.jsonl")
            for index, record in enumerate(raw_records):
                record["received_at_utc"] = (
                    START + timedelta(seconds=index)
                ).isoformat().replace("+00:00", "Z")
            (segment / "raw.jsonl").write_text(
                "".join(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n" for record in raw_records),
                encoding="utf-8",
            )

            result = replay_segment(segment, allow_normalized_metadata_difference=True)
            self.assertTrue(result["match"])
            self.assertEqual(result["semantic_files"], ["bars.jsonl", "decisions.jsonl", "scenarios.jsonl"])

    def test_replay_cli_is_offline_and_requires_no_broker_credentials(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["replay", "--segment-dir", "segment"])
        self.assertEqual(args.command, "replay")
        self.assertEqual(args.segment_dir, Path("segment"))

        calls: list[Path] = []
        rc = main(
            ["replay", "--segment-dir", "segment"],
            environ={},
            replay_command=lambda segment_dir: calls.append(segment_dir) or {"match": True},
        )
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [Path("segment")])

    def test_replay_module_reuses_live_pipeline_and_has_no_network_strategy_or_simulator_clone(self) -> None:
        source = Path("src/fmp/shadow/replay.py").read_text(encoding="utf-8")
        self.assertIn("ShadowRunner", source)
        self.assertIn("parse_bridge_line", source)
        for forbidden in (
            "OandaPracticePricingStream",
            "HTTPSConnection",
            "generate_session_breakout_candidates",
            "candidate_to_decision",
            "class ReplaySimulator",
            "class ReplayStrategy",
            "process_provider_message(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
