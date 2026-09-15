from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.contracts import QuoteBar
from fmp.risk import RiskConfig
from fmp.shadow.contracts import NormalizedQuote
from fmp.shadow.evidence import EvidenceWriter


UTC = timezone.utc
START = datetime(2026, 1, 15, 8, 0, tzinfo=UTC)
ACCOUNT_FINGERPRINT = hashlib.sha256(b"practice-account").hexdigest()


def normalized_quote() -> NormalizedQuote:
    return NormalizedQuote(
        source_time_utc=START,
        received_at_utc=START + timedelta(milliseconds=10),
        receive_monotonic_ns=123,
        symbol="USDJPY",
        bid=139.99,
        ask=140.01,
        tradeable=True,
    )


def quote_bar() -> QuoteBar:
    return QuoteBar(
        timestamp_utc=START,
        symbol="USDJPY",
        bid_open=139.99,
        bid_high=140.00,
        bid_low=139.98,
        bid_close=139.995,
        ask_open=140.01,
        ask_high=140.02,
        ask_low=140.00,
        ask_close=140.015,
    )


def write_fixture(root: Path) -> dict[str, object]:
    writer = EvidenceWriter(
        root,
        code_commit="a" * 40,
        account_fingerprint_sha256=ACCOUNT_FINGERPRINT,
        run_start_utc=START,
    )
    writer.append_raw(
        {
            "type": "PRICE",
            "time": "2026-01-15T08:00:00.000000000Z",
            "instrument": "USD_JPY",
            "tradeable": True,
            "bids": [{"price": "139.990"}],
            "asks": [{"price": "140.010"}],
        },
        received_at_utc=START + timedelta(milliseconds=10),
        receive_monotonic_ns=123,
    )
    writer.append_normalized(normalized_quote())
    writer.append_bar("1m", quote_bar())
    writer.append_bar("15m", quote_bar())
    writer.append_decision({"event": "decision", "decision_id": "d-1", "direction": "LONG"})
    writer.append_scenario({"event": "position_opened", "decision_id": "d-1", "slippage_pips": 0.2})
    writer.append_operational({"event": "connect", "status": "ok"})
    return writer.finalize(
        run_end_utc=START + timedelta(hours=1),
        replay_result_digest="b" * 64,
    )


class Phase8EvidenceTests(unittest.TestCase):
    def test_segment_writes_all_append_only_streams_and_sha_bound_manifest(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_fixture(root)
            expected_files = {
                "raw.jsonl",
                "normalized.jsonl",
                "bars.jsonl",
                "decisions.jsonl",
                "scenarios.jsonl",
                "operational.jsonl",
                "manifest.json",
            }
            self.assertEqual({path.name for path in root.iterdir()}, expected_files)
            for name in expected_files - {"manifest.json"}:
                data = (root / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertEqual(
                    manifest["file_sha256"][name],
                    hashlib.sha256(data).hexdigest(),
                )

            self.assertEqual(manifest["code_commit"], "a" * 40)
            self.assertEqual(manifest["phase7_checkpoint_tag"], "fmp-v1-phase7-walk-forward")
            self.assertEqual(manifest["phase7_checkpoint_sha"], "b6fb0176555b071fef6d1070edf3407b03cd60c9")
            self.assertEqual(manifest["phase7_experiment"], "EXP-20260915-008")
            self.assertEqual(manifest["phase7_outcome"], "PASS / PROMOTE")
            self.assertEqual(
                manifest["strategy"],
                {
                    "id": "session_breakout",
                    "symbol": "USDJPY",
                    "timeframe": "15m",
                    "buffer_pips": 5,
                    "target_range_multiple": 1.5,
                },
            )
            self.assertEqual(manifest["practice_host"], "stream-fxpractice.oanda.com")
            self.assertEqual(manifest["provider_instrument"], "USD_JPY")
            self.assertEqual(manifest["account_fingerprint_sha256"], ACCOUNT_FINGERPRINT)
            self.assertEqual(manifest["slippage_scenarios"], [0.2, 0.5, 1.0])
            self.assertEqual(manifest["risk_policy"], RiskConfig().to_config())
            self.assertEqual(manifest["replay_result_digest"], "b" * 64)

    def test_identical_events_write_byte_identical_artifacts(self) -> None:
        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            write_fixture(left)
            write_fixture(right)
            self.assertEqual(
                {path.name: path.read_bytes() for path in left.iterdir()},
                {path.name: path.read_bytes() for path in right.iterdir()},
            )

    def test_append_calls_preserve_existing_prefix_and_finalize_seals_writer(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            writer = EvidenceWriter(
                root,
                code_commit="c" * 40,
                account_fingerprint_sha256=ACCOUNT_FINGERPRINT,
                run_start_utc=START,
            )
            writer.append_operational({"event": "connect"})
            prefix = (root / "operational.jsonl").read_bytes()
            writer.append_operational({"event": "heartbeat"})
            combined = (root / "operational.jsonl").read_bytes()
            self.assertTrue(combined.startswith(prefix))
            self.assertGreater(len(combined), len(prefix))
            writer.finalize(run_end_utc=START + timedelta(minutes=1), replay_result_digest="d" * 64)
            with self.assertRaises(RuntimeError):
                writer.append_operational({"event": "late-write"})

    def test_raw_records_include_receive_metadata_and_normalized_records_are_canonical(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            writer = EvidenceWriter(
                root,
                code_commit="e" * 40,
                account_fingerprint_sha256=ACCOUNT_FINGERPRINT,
                run_start_utc=START,
            )
            writer.append_raw(
                {"type": "HEARTBEAT", "time": "2026-01-15T08:00:00Z"},
                received_at_utc=START + timedelta(milliseconds=12),
                receive_monotonic_ns=555,
            )
            writer.append_normalized(normalized_quote())
            raw = json.loads((root / "raw.jsonl").read_text(encoding="utf-8"))
            normalized = json.loads((root / "normalized.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(raw["receive_monotonic_ns"], 555)
            self.assertEqual(raw["received_at_utc"], "2026-01-15T08:00:00.012000Z")
            self.assertEqual(raw["provider_object"]["type"], "HEARTBEAT")
            self.assertEqual(normalized["symbol"], "USDJPY")
            self.assertEqual(normalized["source_time_utc"], "2026-01-15T08:00:00Z")

    def test_sensitive_headers_tokens_and_plain_account_ids_never_reach_persisted_bytes(self) -> None:
        secret_token = "token-value-should-never-persist"
        plain_account = "001-011-12345678-001"
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            writer = EvidenceWriter(
                root,
                code_commit="f" * 40,
                account_fingerprint_sha256=ACCOUNT_FINGERPRINT,
                run_start_utc=START,
            )
            writer.append_operational(
                {
                    "event": "transport_error",
                    "Authorization": f"Bearer {secret_token}",
                    "token": secret_token,
                    "account_id": plain_account,
                    "message": f"Authorization: Bearer {secret_token}; account={plain_account}",
                }
            )
            writer.append_raw(
                {
                    "type": "PRICE",
                    "time": "2026-01-15T08:00:00Z",
                    "instrument": "USD_JPY",
                    "token": secret_token,
                    "accountID": plain_account,
                },
                received_at_utc=START,
                receive_monotonic_ns=1,
            )
            writer.finalize(run_end_utc=START + timedelta(seconds=1), replay_result_digest="1" * 64)
            persisted = b"".join(path.read_bytes() for path in root.iterdir())
            self.assertNotIn(secret_token.encode(), persisted)
            self.assertNotIn(plain_account.encode(), persisted)
            self.assertNotIn(b"Bearer", persisted)

    def test_invalid_identity_digests_fail_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                EvidenceWriter(
                    Path(tmp),
                    code_commit="abc",
                    account_fingerprint_sha256="not-a-sha",
                    run_start_utc=START,
                )


if __name__ == "__main__":
    unittest.main()
