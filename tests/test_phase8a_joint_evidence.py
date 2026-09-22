from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from fmp.portfolio.evidence import (
    JOINT_EVIDENCE_PROTOCOL,
    build_joint_evidence_envelope,
    resolve_historical_strategy_records,
    write_joint_evidence_artifacts,
)
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.portfolio import StrategyLifecycle


class Phase8AJointEvidenceTests(unittest.TestCase):
    def test_resolver_requires_exact_known_unique_fingerprints(self) -> None:
        inventory = build_phase4_baseline_inventory()
        known = inventory[0]
        resolved = resolve_historical_strategy_records(
            [known.strategy.fingerprint]
        )
        self.assertEqual(len(resolved), 1)
        self.assertEqual(
            resolved[0].strategy.fingerprint,
            known.strategy.fingerprint,
        )

        with self.assertRaises(ValueError):
            resolve_historical_strategy_records(
                [known.strategy.fingerprint, known.strategy.fingerprint]
            )
        with self.assertRaises(ValueError):
            resolve_historical_strategy_records(["f" * 64])

    def test_resolver_preserves_retired_and_qualified_historical_status(self) -> None:
        inventory = build_phase4_baseline_inventory()
        retired = next(
            item
            for item in inventory
            if item.lifecycle is StrategyLifecycle.RETIRED
        )
        qualified = next(
            item
            for item in inventory
            if item.lifecycle is StrategyLifecycle.HISTORICAL_QUALIFIED
        )
        resolved = resolve_historical_strategy_records(
            [qualified.strategy.fingerprint, retired.strategy.fingerprint]
        )
        states = {
            item.strategy.fingerprint: item.lifecycle
            for item in resolved
        }
        self.assertEqual(
            states[retired.strategy.fingerprint],
            StrategyLifecycle.RETIRED,
        )
        self.assertEqual(
            states[qualified.strategy.fingerprint],
            StrategyLifecycle.HISTORICAL_QUALIFIED,
        )

    def test_evidence_envelope_cannot_authorize_promotion_or_mutate_status(self) -> None:
        record = build_phase4_baseline_inventory()[0]
        joint_result = {
            "protocol": "fmp-phase8a-joint-portfolio-v1",
            "strategy_fingerprints": [record.strategy.fingerprint],
            "promotion_authorized": False,
            "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
            "untouched_oos": False,
            "run_identity": {
                "requested_start_utc": datetime(2024, 1, 1, tzinfo=timezone.utc),
            },
        }
        envelope = build_joint_evidence_envelope(
            joint_result=joint_result,
            strategy_records=(record,),
        )
        self.assertEqual(envelope["protocol"], JOINT_EVIDENCE_PROTOCOL)
        self.assertFalse(envelope["promotion_authorized"])
        self.assertFalse(envelope["historical_status_mutation_authorized"])
        self.assertEqual(
            envelope["historical_strategy_status"][0]["lifecycle"],
            record.lifecycle.value,
        )
        self.assertEqual(
            envelope["historical_strategy_status"][0]["evidence_id"],
            record.evidence_id,
        )

        with self.assertRaises(ValueError):
            build_joint_evidence_envelope(
                joint_result=joint_result | {"promotion_authorized": True},
                strategy_records=(record,),
            )

    def test_artifact_writer_is_deterministic_and_serializes_utc(self) -> None:
        record = build_phase4_baseline_inventory()[0]
        envelope = build_joint_evidence_envelope(
            joint_result={
                "protocol": "fmp-phase8a-joint-portfolio-v1",
                "strategy_fingerprints": [record.strategy.fingerprint],
                "promotion_authorized": False,
                "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
                "untouched_oos": False,
                "run_identity": {
                    "requested_start_utc": datetime(
                        2024, 1, 1, tzinfo=timezone.utc
                    ),
                },
            },
            strategy_records=(record,),
        )
        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            left_manifest = write_joint_evidence_artifacts(envelope, left)
            right_manifest = write_joint_evidence_artifacts(envelope, right)

            self.assertEqual(
                (left / "joint-evidence.json").read_bytes(),
                (right / "joint-evidence.json").read_bytes(),
            )
            self.assertEqual(left_manifest, right_manifest)
            stored = json.loads(
                (left / "joint-evidence.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                stored["joint_result"]["run_identity"]["requested_start_utc"],
                "2024-01-01T00:00:00Z",
            )
            self.assertEqual(
                left_manifest["protocol"],
                "fmp-phase8a-joint-evidence-artifacts-v1",
            )


if __name__ == "__main__":
    unittest.main()
