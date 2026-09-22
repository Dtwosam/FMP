from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fmp.shadow import campaign
from fmp.shadow.evidence import CONNECTOR_PROTOCOL, EVIDENCE_PROTOCOL, EvidenceWriter


UTC = timezone.utc
START = datetime(2026, 9, 17, 20, 0, tzinfo=UTC)
CODE_COMMIT = "c" * 40
BRIDGE_SOURCE_COMMIT = "d" * 40
SESSION = "a" * 64
FINGERPRINT = "b" * 64
SERVER = "FPMarketsSC-Demo2"
REFERENCE_SHA = "e" * 64
REFERENCE = {
    "method_version": "fmp-phase8-spread-reference-v1",
    "phase7_checkpoint_tag": "fmp-v1-phase7-walk-forward",
    "phase7_checkpoint_sha": "b6fb0176555b071fef6d1070edf3407b03cd60c9",
    "phase7_stage2_run_id": 35015277625,
    "phase2_artifact_id": 10327600628,
    "processed_manifest_sha256": "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
}


class Phase8Mt5EvidenceV2Tests(unittest.TestCase):
    def test_evidence_protocol_and_manifest_are_mt5_v2_only(self) -> None:
        self.assertEqual(EVIDENCE_PROTOCOL, "fmp-phase8-shadow-evidence-v2")
        self.assertEqual(CONNECTOR_PROTOCOL, "fmp-mt5-demo-file-bridge-v1")

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            writer = EvidenceWriter(
                root,
                code_commit=CODE_COMMIT,
                bridge_source_commit=BRIDGE_SOURCE_COMMIT,
                bridge_session_id=SESSION,
                server=SERVER,
                account_fingerprint_sha256=FINGERPRINT,
                run_start_utc=START,
            )
            writer.append_raw(
                {
                    "protocol": CONNECTOR_PROTOCOL,
                    "record_type": "BRIDGE_HEARTBEAT",
                    "bridge_session_id": SESSION,
                    "symbol": "USDJPY",
                    "server": SERVER,
                    "account_fingerprint": FINGERPRINT,
                    "bridge_emitted_time_msc": 1_789_667_205_000,
                    "last_tick_time_msc": None,
                },
                received_at_utc=START,
                receive_monotonic_ns=1,
            )
            manifest = writer.finalize(
                run_end_utc=START + timedelta(seconds=1),
                replay_result_digest="f" * 64,
            )

        self.assertEqual(manifest["protocol"], "fmp-phase8-shadow-evidence-v2")
        self.assertEqual(manifest["connector_protocol"], "fmp-mt5-demo-file-bridge-v1")
        self.assertEqual(manifest["provider"], "FP_MARKETS_MT5_DEMO")
        self.assertEqual(manifest["provider_instrument"], "USDJPY")
        self.assertEqual(manifest["transport"], "MT5_FILE_COMMON_JSONL")
        self.assertEqual(manifest["bridge_file"], "FMP/phase8-usdjpy-feed.jsonl")
        self.assertEqual(
            manifest["allowed_servers"],
            ["FPMarketsSC-Demo", "FPMarketsSC-Demo2"],
        )
        self.assertEqual(manifest["bridge_session_id"], SESSION)
        self.assertEqual(manifest["server"], SERVER)
        self.assertEqual(manifest["account_fingerprint_sha256"], FINGERPRINT)
        self.assertEqual(manifest["bridge_source_commit"], BRIDGE_SOURCE_COMMIT)
        for forbidden in (
            "connector_boundary",
            "practice_host",
            "method",
            "host",
            "path_template",
            "snapshot",
            "include_home_conversions",
        ):
            self.assertNotIn(forbidden, manifest)

    def test_evidence_writer_rejects_unapproved_server_or_identity(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                EvidenceWriter(
                    Path(tmp),
                    code_commit=CODE_COMMIT,
                    bridge_source_commit=BRIDGE_SOURCE_COMMIT,
                    bridge_session_id=SESSION,
                    server="FPMarketsSC-Live",
                    account_fingerprint_sha256=FINGERPRINT,
                    run_start_utc=START,
                )

    def test_campaign_registration_is_exact_mt5_v2_identity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch(
                "fmp.shadow.campaign._load_reference",
                return_value=(REFERENCE, REFERENCE_SHA),
            ):
                record = campaign.register_campaign(
                    reference_dir=root / "unused-reference",
                    campaign_dir=root,
                    code_commit=CODE_COMMIT,
                    campaign_start_utc=START,
                )

            self.assertEqual(record["registration_version"], 2)
            self.assertEqual(record["phase8_experiment"], "EXP-20260922-011")
            self.assertEqual(record["provider"], "FP_MARKETS_MT5_DEMO")
            self.assertEqual(record["connector_protocol"], "fmp-mt5-demo-file-bridge-v1")
            self.assertEqual(record["transport"], "MT5_FILE_COMMON_JSONL")
            self.assertEqual(record["bridge_file"], "FMP/phase8-usdjpy-feed.jsonl")
            self.assertEqual(
                record["allowed_servers"],
                ["FPMarketsSC-Demo", "FPMarketsSC-Demo2"],
            )
            self.assertEqual(record["provider_instrument"], "USDJPY")
            for forbidden in ("host", "path_template", "instrument"):
                self.assertNotIn(forbidden, record)

            loaded = campaign.load_campaign_registration(root, code_commit=CODE_COMMIT)
            self.assertEqual(loaded, record)

    def test_campaign_loader_rejects_mixed_or_tampered_connector_identity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch(
                "fmp.shadow.campaign._load_reference",
                return_value=(REFERENCE, REFERENCE_SHA),
            ):
                campaign.register_campaign(
                    reference_dir=root / "unused-reference",
                    campaign_dir=root,
                    code_commit=CODE_COMMIT,
                    campaign_start_utc=START,
                )

            path = root / "registration.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            record["connector_protocol"] = "oanda-v20-fxtrade-practice-pricing-stream-v1"
            payload = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
            path.write_text(payload, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "connector_protocol"):
                campaign.load_campaign_registration(root, code_commit=CODE_COMMIT)

    def test_plain_account_secrets_never_persist_in_v2(self) -> None:
        secret = "broker-password-never-persist"
        plain_account = "12345678"
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            writer = EvidenceWriter(
                root,
                code_commit=CODE_COMMIT,
                bridge_source_commit=BRIDGE_SOURCE_COMMIT,
                bridge_session_id=SESSION,
                server=SERVER,
                account_fingerprint_sha256=FINGERPRINT,
                run_start_utc=START,
            )
            writer.append_operational(
                {
                    "event": "diagnostic",
                    "password": secret,
                    "account_id": plain_account,
                }
            )
            writer.finalize(
                run_end_utc=START + timedelta(seconds=1),
                replay_result_digest=hashlib.sha256(b"replay").hexdigest(),
            )
            persisted = b"".join(path.read_bytes() for path in root.iterdir())
            self.assertNotIn(secret.encode(), persisted)
            self.assertNotIn(plain_account.encode(), persisted)


if __name__ == "__main__":
    unittest.main()
