from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_dispatch_authorization import (
    build_2023_dispatch_authorization,
    validate_2023_dispatch_authorization,
    validate_2023_dispatch_authorization_sources,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/phase8a_dec608_2023_dispatch_preflight.json"
HEAD = "a" * 40


def _preflight() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _refingerprint(value: dict[str, object], field: str) -> None:
    unsigned = dict(value)
    unsigned.pop(field, None)
    value[field] = hashlib.sha256(_canonical(unsigned)).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-609 requires DEC-607-installed protected 2023 runtime",
)
class AnnualCatalogue2023DispatchAuthorizationTests(unittest.TestCase):
    def test_fixture_is_the_exact_frozen_dec608_artifact(self) -> None:
        p = _preflight()
        self.assertEqual(p["decision"], "DEC-608")
        self.assertEqual(p["expected_head_sha"], "d9194944f53d311a9030deaf3ee37bff465634ed")
        self.assertEqual(
            hashlib.sha256(_canonical(p)).hexdigest(),
            "6044191b89bbd6b33338b86077715be7d925d30ac14cd38845c948523f6ae651",
        )
        self.assertEqual(p["preflight_fingerprint_sha256"], "9f1533d5993c28c86f53d2c7bd0f219178465da2c0eb987ae923ac9af8aca695")

    def test_sources_pin_dec608_and_installed_runtime(self) -> None:
        v = validate_2023_dispatch_authorization_sources(repository_root=ROOT)
        self.assertEqual(v["dispatch_preflight_source_blob_sha"], "fb4f8fa390e94a75a8d52c99cbc041e9bf1e8164")
        self.assertEqual(v["installed_gate_blob_sha"], "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191")
        self.assertEqual(v["installed_runtime_blob_sha"], "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3")

    def test_authorization_is_2023_protected_and_source_only(self) -> None:
        value = build_2023_dispatch_authorization(
            _preflight(), repository_root=ROOT, authorization_head_sha=HEAD
        )
        self.assertIs(validate_2023_dispatch_authorization(value), value)
        for name, expected in {
            "decision": "DEC-609",
            "source_preflight_decision": "DEC-608",
            "authorization_head_sha": HEAD,
            "annual_segment_label": "2023",
            "prior_segment_label": "2022",
            "authorization_scope": "2023_run_385_attempt_1_only",
            "expected_run_number": 385,
            "expected_run_attempt": 1,
            "previous_annual_freeze_run_id": 37663157285,
            "source_preflight_workflow_run_id": 37766405383,
            "source_preflight_artifact_id": 11544233443,
            "source_preflight_fingerprint_sha256": "9f1533d5993c28c86f53d2c7bd0f219178465da2c0eb987ae923ac9af8aca695",
            "annual_workflow_dispatch_authorized": True,
            "historical_artifact_read_authorized": True,
            "historical_catalogue_execution_authorized": True,
            "historical_result_production_authorized": True,
            "protected_history_access_authorized": True,
            "authorization_contract_validated": True,
            "source_only_authorization": True,
            "dispatch_command_present": False,
            "dispatch_action_executed": False,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
            "run_386_or_later_authorized": False,
            "next_segment_execution_authorized": False,
            "cross_year_comparison_authorized": False,
            "cross_year_result_production_authorized": False,
            "strategy_v1_synthesis_authorized": False,
            "promotion_authorized": False,
            "phase8b_authorized": False,
            "demo_order_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "trading_authorized": False,
        }.items():
            self.assertEqual(value[name], expected, name)

    def test_protected_provenance_is_required(self) -> None:
        changed = _preflight()
        changed["source_authorization_protected_history_access_authorized"] = False
        _refingerprint(changed, "preflight_fingerprint_sha256")
        with self.assertRaises(ValueError):
            build_2023_dispatch_authorization(changed, repository_root=ROOT, authorization_head_sha=HEAD)

    def test_refingerprinted_protected_scope_mutations_are_rejected(self) -> None:
        value = build_2023_dispatch_authorization(
            _preflight(), repository_root=ROOT, authorization_head_sha=HEAD
        )
        for field in (
            "source_authorization_protected_history_access_authorized",
            "protected_catalogue_segment",
            "governing_method_decision",
            "governing_protocol_decision",
            "protocol_full_collection_catalogue_use_authorized",
            "protocol_2023_2026_catalogue_use_authorized",
        ):
            for operation in ("modify", "remove"):
                with self.subTest(field=field, operation=operation):
                    changed = copy.deepcopy(value)
                    if operation == "remove":
                        changed.pop(field)
                    elif type(changed[field]) is bool:
                        changed[field] = False
                    else:
                        changed[field] = "DEC-000"
                    _refingerprint(changed, "authorization_fingerprint_sha256")
                    with self.assertRaisesRegex(ValueError, f"{field} mismatch"):
                        validate_2023_dispatch_authorization(changed)

    def test_refingerprinted_numeric_boolean_provenance_is_rejected(self) -> None:
        value = build_2023_dispatch_authorization(
            _preflight(), repository_root=ROOT, authorization_head_sha=HEAD
        )
        for field in (
            "source_authorization_protected_history_access_authorized",
            "protected_catalogue_segment",
            "protocol_full_collection_catalogue_use_authorized",
            "protocol_2023_2026_catalogue_use_authorized",
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(value)
                changed[field] = 1
                _refingerprint(changed, "authorization_fingerprint_sha256")
                with self.assertRaisesRegex(ValueError, f"{field} mismatch"):
                    validate_2023_dispatch_authorization(changed)

    def test_refingerprinted_run386_authority_is_rejected(self) -> None:
        value = build_2023_dispatch_authorization(
            _preflight(), repository_root=ROOT, authorization_head_sha=HEAD
        )
        changed = copy.deepcopy(value)
        changed["run_386_or_later_authorized"] = True
        _refingerprint(changed, "authorization_fingerprint_sha256")
        with self.assertRaisesRegex(ValueError, "run_386_or_later_authorized mismatch"):
            validate_2023_dispatch_authorization(changed)

    def test_refingerprinted_cross_year_authority_is_rejected(self) -> None:
        value = build_2023_dispatch_authorization(
            _preflight(), repository_root=ROOT, authorization_head_sha=HEAD
        )
        changed = copy.deepcopy(value)
        changed["cross_year_comparison_authorized"] = True
        _refingerprint(changed, "authorization_fingerprint_sha256")
        with self.assertRaises(ValueError):
            validate_2023_dispatch_authorization(changed)

    def test_cli_only_supports_authorize(self) -> None:
        script = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_dispatch_authorization.py").read_text()
        self.assertIn('subparsers.add_parser("authorize")', script)
        for forbidden in ('subparsers.add_parser("dispatch")', 'subparsers.add_parser("execute")', "gh workflow run ", "git push"):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
