from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_workflow_install_preflight import (
    EXPECTED_INSTALL_CONTRACT_BLOB_SHA,
    build_workflow_install_preflight,
    validate_preflight_sources,
    validate_workflow_install_preflight,
)
from fmp.discovery.annual_pattern_catalogue_workflow_source import (
    RESERVED_ACTIVE_WORKFLOW_PATH,
)


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _fingerprint(value: object) -> str:
    return hashlib.sha256(
        (
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    ).hexdigest()


class AnnualPatternCatalogueWorkflowInstallPreflightTests(unittest.TestCase):
    def test_preflight_sources_bind_exact_install_contract_and_absent_target(self) -> None:
        sources = validate_preflight_sources(repository_root=Path("."))

        self.assertEqual(
            sources["install_contract_blob_sha"],
            EXPECTED_INSTALL_CONTRACT_BLOB_SHA,
        )
        self.assertFalse(
            sources["install_sources"]["active_workflow_present"]
        )
        self.assertFalse(Path(RESERVED_ACTIVE_WORKFLOW_PATH).exists())

    def test_build_preflight_is_read_only_and_fingerprinted(self) -> None:
        value = build_workflow_install_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )

        self.assertIs(validate_workflow_install_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-480")
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["active_workflow_present"])
        self.assertEqual(value["expected_head_sha"], HEAD)
        self.assertEqual(
            value["next_gate"],
            (
                "REPOSITORY_HOSTED_READ_ONLY_ANNUAL_PATTERN_CATALOGUE_"
                "WORKFLOW_INSTALL_PREFLIGHT_PROOF"
            ),
        )
        self.assertEqual(
            value["install_action_fingerprint"],
            _fingerprint(value["install_action"]),
        )

    def test_main_head_drift_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_workflow_install_preflight(
                repository_root=Path("."),
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=HEAD,
            )

    def test_non_main_branch_metadata_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires main branch metadata"):
            build_workflow_install_preflight(
                repository_root=Path("."),
                main_branch={"name": "dev", "commit": {"sha": HEAD}},
                expected_head_sha=HEAD,
            )

    def test_refingerprinted_authority_tamper_fails_semantic_validation(self) -> None:
        value = build_workflow_install_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )
        value = dict(value)
        value["workflow_dispatch_authorized"] = True
        value.pop("preflight_fingerprint", None)
        value["preflight_fingerprint"] = _fingerprint(value)

        with self.assertRaisesRegex(
            ValueError,
            "workflow_dispatch_authorized mismatch",
        ):
            validate_workflow_install_preflight(value)

    def test_refingerprinted_nested_target_tamper_fails_semantic_validation(
        self,
    ) -> None:
        value = build_workflow_install_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )
        tampered = copy.deepcopy(value)
        action = tampered["install_action"]
        assert isinstance(action, dict)
        mutation = action["mutation"]
        assert isinstance(mutation, dict)
        mutation["target_path"] = ".github/workflows/other.yml"
        tampered["install_action_fingerprint"] = _fingerprint(action)
        tampered.pop("preflight_fingerprint", None)
        tampered["preflight_fingerprint"] = _fingerprint(tampered)

        with self.assertRaisesRegex(ValueError, "mutation payload mismatch"):
            validate_workflow_install_preflight(tampered)

    def test_refingerprinted_install_sources_tamper_fails_semantic_validation(
        self,
    ) -> None:
        value = build_workflow_install_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )
        tampered = copy.deepcopy(value)
        install_sources = tampered["install_sources"]
        assert isinstance(install_sources, dict)
        source_blobs = install_sources["source_blobs"]
        assert isinstance(source_blobs, dict)
        source_blobs["workflow_source"] = "0" * 40
        tampered.pop("preflight_fingerprint", None)
        tampered["preflight_fingerprint"] = _fingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "install sources payload mismatch",
        ):
            validate_workflow_install_preflight(tampered)

    def test_all_execution_and_trading_authority_remains_false(self) -> None:
        value = build_workflow_install_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )

        for field in (
            "repository_mutation_authorized",
            "workflow_template_install_authorized",
            "workflow_installed",
            "workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "next_segment_execution_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(value[field], field)


if __name__ == "__main__":
    unittest.main()
