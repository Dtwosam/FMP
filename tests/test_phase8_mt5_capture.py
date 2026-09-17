from __future__ import annotations

import inspect
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fmp.shadow.mt5_bridge import BridgeFileTail, BridgeStartRecord, BridgeTickRecord
from fmp.shadow.runner import run_live_shadow_capture


UTC = timezone.utc
START = datetime(2026, 9, 17, 20, 0, tzinfo=UTC)
CODE_COMMIT = "c" * 40
SESSION = "a" * 64
FINGERPRINT = "b" * 64
SERVER = "FPMarketsSC-Demo2"
PROTOCOL = "fmp-mt5-demo-file-bridge-v1"


def start_record(*, session: str = SESSION) -> dict[str, object]:
    return {
        "protocol": PROTOCOL,
        "record_type": "BRIDGE_START",
        "bridge_session_id": session,
        "symbol": "USDJPY",
        "server": SERVER,
        "account_fingerprint": FINGERPRINT,
        "account_mode": "DEMO",
        "bridge_start_time_msc": int(START.timestamp() * 1000),
    }


def tick_record(index: int, *, session: str = SESSION) -> dict[str, object]:
    bid = 147.100 + index * 0.001
    return {
        "protocol": PROTOCOL,
        "record_type": "TICK",
        "bridge_session_id": session,
        "symbol": "USDJPY",
        "server": SERVER,
        "account_fingerprint": FINGERPRINT,
        "source_time_msc": int((START + timedelta(seconds=index)).timestamp() * 1000),
        "bid": bid,
        "ask": bid + 0.002,
        "flags": 6,
    }


def line(record: dict[str, object]) -> bytes:
    return (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()


def jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(item) for item in path.read_text(encoding="utf-8").splitlines() if item]


class StopAfterIdle:
    def __call__(self, _: float) -> None:
        raise KeyboardInterrupt


class WrongSessionTail:
    def __init__(self) -> None:
        self.start_record = BridgeStartRecord(
            protocol=PROTOCOL,
            bridge_session_id=SESSION,
            symbol="USDJPY",
            server=SERVER,
            account_fingerprint=FINGERPRINT,
            account_mode="DEMO",
            bridge_start_time_msc=int(START.timestamp() * 1000),
        )
        self._done = False

    def read_available(self):  # type: ignore[no-untyped-def]
        if self._done:
            return ()
        self._done = True
        return (
            BridgeTickRecord(
                protocol=PROTOCOL,
                bridge_session_id="d" * 64,
                symbol="USDJPY",
                server=SERVER,
                account_fingerprint=FINGERPRINT,
                source_time_msc=int((START + timedelta(seconds=1)).timestamp() * 1000),
                bid=147.1,
                ask=147.102,
                flags=6,
            ),
        )


class Phase8Mt5CaptureTests(unittest.TestCase):
    def test_capture_api_has_only_bound_tail_campaign_and_internal_clock_hooks(self) -> None:
        parameters = inspect.signature(run_live_shadow_capture).parameters
        self.assertIn("bridge_tail", parameters)
        self.assertIn("campaign_dir", parameters)
        self.assertIn("code_commit", parameters)
        self.assertIn("sleep", parameters)
        for forbidden in (
            "account_id",
            "token",
            "server",
            "path",
            "filename",
            "instrument",
            "stream_factory",
        ):
            self.assertNotIn(forbidden, parameters)

    def test_capture_records_active_start_and_only_post_reader_ticks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = root / "campaign"
            campaign.mkdir()
            bridge = root / "phase8-usdjpy-feed.jsonl"
            bridge.write_bytes(line(start_record()) + line(tick_record(1)))
            tail = BridgeFileTail(bridge)
            with bridge.open("ab") as handle:
                handle.write(line(tick_record(2)))

            now = START + timedelta(seconds=10)
            with patch("fmp.shadow.runner.load_campaign_registration", return_value={"registration_version": 2}):
                rc = run_live_shadow_capture(
                    bridge_tail=tail,
                    campaign_dir=campaign,
                    code_commit=CODE_COMMIT,
                    utc_now=lambda: now,
                    monotonic_ns=lambda: 10_000_000_000,
                    sleep=StopAfterIdle(),
                )

            self.assertEqual(rc, 0)
            segments = tuple(campaign.glob("segment-*"))
            self.assertEqual(len(segments), 1)
            raw = jsonl(segments[0] / "raw.jsonl")
            self.assertEqual(len(raw), 2)
            self.assertEqual(raw[0]["provider_object"]["record_type"], "BRIDGE_START")
            self.assertEqual(raw[1]["provider_object"]["record_type"], "TICK")
            self.assertEqual(raw[1]["provider_object"]["source_time_msc"], tick_record(2)["source_time_msc"])
            self.assertNotEqual(raw[1]["provider_object"]["source_time_msc"], tick_record(1)["source_time_msc"])
            self.assertFalse((segments[0] / "manifest.json").exists())

    def test_capture_fails_closed_on_session_change_and_persists_rejection(self) -> None:
        with TemporaryDirectory() as tmp:
            campaign = Path(tmp)
            now = START + timedelta(seconds=10)
            with patch("fmp.shadow.runner.load_campaign_registration", return_value={"registration_version": 2}):
                rc = run_live_shadow_capture(
                    bridge_tail=WrongSessionTail(),
                    campaign_dir=campaign,
                    code_commit=CODE_COMMIT,
                    utc_now=lambda: now,
                    monotonic_ns=lambda: 10_000_000_000,
                    sleep=StopAfterIdle(),
                )

            self.assertEqual(rc, 4)
            segment = next(campaign.glob("segment-*"))
            operational = jsonl(segment / "operational.jsonl")
            rejections = [row for row in operational if row.get("event") == "rejection"]
            self.assertTrue(rejections)
            self.assertEqual(rejections[-1]["reason"], "bridge_record_rejected")
            self.assertFalse((segment / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
