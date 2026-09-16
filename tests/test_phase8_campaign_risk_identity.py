from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fmp.shadow.campaign import register_campaign


CODE_COMMIT = "c" * 40
REFERENCE_SHA = "d" * 64
EXPECTED_RISK_POLICY = {
    "default_risk_fraction": 0.0025,
    "max_risk_fraction": 0.005,
    "max_simultaneous_risk_fraction": 0.01,
    "daily_loss_halt_fraction": 0.015,
}


class Phase8CampaignRiskIdentityTests(unittest.TestCase):
    def test_registration_freezes_exact_existing_risk_config(self) -> None:
        reference = {
            "method_version": "fmp-phase8-spread-reference-v1",
            "phase7_checkpoint_tag": "fmp-v1-phase7-walk-forward",
            "phase7_checkpoint_sha": "b6fb0176555b071fef6d1070edf3407b03cd60c9",
            "phase7_stage2_run_id": 35015277625,
            "phase2_artifact_id": 10327600628,
            "processed_manifest_sha256": "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
        }
        with TemporaryDirectory() as campaign_tmp:
            campaign_dir = Path(campaign_tmp)
            with patch(
                "fmp.shadow.campaign._load_reference",
                return_value=(reference, REFERENCE_SHA),
            ):
                record = register_campaign(
                    reference_dir=Path("unused-reference"),
                    campaign_dir=campaign_dir,
                    code_commit=CODE_COMMIT,
                    campaign_start_utc=datetime(2026, 9, 16, 10, 30, tzinfo=timezone.utc),
                )

            self.assertEqual(record["risk_policy"], EXPECTED_RISK_POLICY)
            persisted = json.loads(
                (campaign_dir / "registration.json").read_text(encoding="utf-8")
            )
            self.assertEqual(persisted["risk_policy"], EXPECTED_RISK_POLICY)


if __name__ == "__main__":
    unittest.main()
