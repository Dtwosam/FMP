from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fmp.shadow import campaign
from fmp.shadow.runner import run_live_shadow_capture


CODE_COMMIT = "c" * 40
REFERENCE_SHA = "d" * 64
REFERENCE = {
    "method_version": "fmp-phase8-spread-reference-v1",
    "phase7_checkpoint_tag": "fmp-v1-phase7-walk-forward",
    "phase7_checkpoint_sha": "b6fb0176555b071fef6d1070edf3407b03cd60c9",
    "phase7_stage2_run_id": 35015277625,
    "phase2_artifact_id": 10327600628,
    "processed_manifest_sha256": "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
}


class Phase8CampaignRegistrationGuardTests(unittest.TestCase):
    def _register(self, root: Path) -> dict[str, object]:
        with patch(
            "fmp.shadow.campaign._load_reference",
            return_value=(REFERENCE, REFERENCE_SHA),
        ):
            return campaign.register_campaign(
                reference_dir=root / "unused-reference",
                campaign_dir=root,
                code_commit=CODE_COMMIT,
                campaign_start_utc=datetime(2026, 9, 16, 10, 30, tzinfo=timezone.utc),
            )

    def test_loader_accepts_only_canonical_registration_for_current_code(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = self._register(root)
            loaded = campaign.load_campaign_registration(root, code_commit=CODE_COMMIT)
            self.assertEqual(loaded, expected)

            with self.assertRaisesRegex(ValueError, "code_commit"):
                campaign.load_campaign_registration(root, code_commit="e" * 40)

    def test_loader_rejects_tampered_risk_boundary_and_noncanonical_bytes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._register(root)
            path = root / "registration.json"
            original = json.loads(path.read_text(encoding="utf-8"))

            tampered_risk = dict(original)
            tampered_risk["risk_policy"] = dict(original["risk_policy"])
            tampered_risk["risk_policy"]["default_risk_fraction"] = 0.005
            path.write_text(
                json.dumps(tampered_risk, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "risk_policy"):
                campaign.load_campaign_registration(root, code_commit=CODE_COMMIT)

            tampered_path = dict(original)
            tampered_path["path_template"] = "/v3/accounts/{account_id}/orders"
            path.write_text(
                json.dumps(tampered_path, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "path_template"):
                campaign.load_campaign_registration(root, code_commit=CODE_COMMIT)

            path.write_text(
                json.dumps(original, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "canonical"):
                campaign.load_campaign_registration(root, code_commit=CODE_COMMIT)

    def test_live_capture_validates_registration_before_stream_construction(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "registration.json").write_text("{}\n", encoding="utf-8")
            stream_constructed = False

            def forbidden_stream_factory(**_: object) -> object:
                nonlocal stream_constructed
                stream_constructed = True
                raise AssertionError("stream must not be constructed for invalid registration")

            with self.assertRaisesRegex(ValueError, "registration"):
                run_live_shadow_capture(
                    account_id="101-001-1234567-001",
                    token="test-token",
                    campaign_dir=root,
                    code_commit=CODE_COMMIT,
                    utc_now=lambda: datetime(2026, 9, 16, 10, 31, tzinfo=timezone.utc),
                    monotonic_ns=lambda: 1,
                    stream_factory=forbidden_stream_factory,
                )
            self.assertFalse(stream_constructed)
            self.assertEqual(tuple(root.glob("segment-*")), ())


if __name__ == "__main__":
    unittest.main()
