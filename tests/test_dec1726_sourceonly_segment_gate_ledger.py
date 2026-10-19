"""DEC-1726: bounded nonauthorizing Phase 8A segment readiness manifest.

Static historical/source labels only; no network or protected asset I/O.
"""
import json
from pathlib import Path
import unittest


PATH = (Path(__file__).resolve().parents[1] /
        "docs/dec1726-phase8a-sourceonly-segment-gate-ledger.json")
EXPECTED = (
    "2015", "2016", "2017", "2018", "2019", "2020", "2021",
    "2022", "2023", "2024", "2025", "2026_YTD_TO_2026_08_20",
)
GATES = (
    "independent_admin_no_bypass_lock_continuity",
    "independent_reviewed_ref_sha_workflow_runtime_identity",
    "installed_precheckout_preinstall_preaccess_three_job_gates",
    "actual_privileged_runner_os_isolation_and_publisher_witness",
    "fresh_authoritative_annual_run_inventory",
    "separate_human_one_shot_2023_run385_attempt1_decision",
)


def _unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate manifest member")
        result[key] = value
    return result


def _read():
    return json.loads(PATH.read_text(encoding="utf-8"),
                      object_pairs_hook=_unique_members)


class Phase8ASourceOnlySegmentGateLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = _read()

    def test_strict_source_only_schema(self):
        self.assertEqual(
            self.data["schema"],
            "fmp_phase8a_sourceonly_readiness_not_authorizing_v1",
        )
        self.assertEqual(self.data["decision"], "DEC-1726")

    def test_explicit_capture_date_and_not_live(self):
        self.assertEqual(self.data["capture_date"], "2026-10-19")
        self.assertIs(self.data["live_administration_evidence_verified"], False)
        self.assertIs(self.data["live_annual_run_385_inventory_verified"], False)

    def test_exact_annual_segment_sequence(self):
        segments = self.data["yearly_catalogue_status"]
        self.assertEqual(tuple(s["segment"] for s in segments), EXPECTED)
        self.assertEqual(len(segments), 12)

    def test_historical_frozen_eight_years_never_imply_promotion(self):
        for year in self.data["yearly_catalogue_status"][:8]:
            self.assertEqual(year["research_evidence"], "HISTORICALLY_FROZEN")
            self.assertIs(year["promotion_eligible"], False)

    def test_2023_and_later_are_explicitly_blocked(self):
        for segment in self.data["yearly_catalogue_status"][8:]:
            self.assertTrue(segment["research_evidence"].startswith("BLOCKED_"))
            self.assertIs(segment["promotion_eligible"], False)

    def test_2022_predecessor_is_not_live_dispatch_evidence(self):
        prior = self.data["previous_annual_freeze"]
        self.assertEqual(prior["segment"], "2022")
        self.assertEqual(prior["run_number"], 384)
        self.assertEqual(prior["run_id"], 37663157285)
        self.assertEqual(
            prior["source_provenance"],
            "HISTORICALLY_ACCEPTED_NOT_REAUTHENTICATED_FOR_DISPATCH",
        )

    def test_one_shot_2023_identity_is_not_authorized(self):
        row = self.data["yearly_catalogue_status"][8]
        self.assertEqual(row["segment"], "2023")
        self.assertEqual(row["expected_run_number"], 385)
        self.assertEqual(row["expected_attempt"], 1)
        self.assertEqual(self.data["next_protected_segment"], "2023")
        self.assertIs(self.data["authority_flags"]["run385_authorized"], False)
        self.assertIs(self.data["authority_flags"]["run385_executed"], False)

    def test_observed_main_unprotected_is_not_current_lock_proof(self):
        state = self.data["main_branch_last_public_observation"]
        self.assertEqual(
            state["sha"], "53e203133bbc141b2f48c7b8b8241d56b35166a3"
        )
        self.assertIs(state["protected"], False)
        self.assertIs(state["is_current_at_action_time"], False)
        self.assertIs(state["proves_exclusive_no_bypass_lock"], False)

    def test_separately_owned_external_gates_are_never_implied(self):
        self.assertEqual(
            tuple(self.data["required_external_gates"]), GATES
        )
        self.assertEqual(self.data["external_gate_status"], "BLOCKED")
        self.assertIs(self.data["live_administration_evidence_verified"], False)

    def test_all_authority_flags_are_exact_false(self):
        flags = self.data["authority_flags"]
        self.assertEqual(len(flags), 14)
        self.assertTrue(all(type(value) is bool and value is False
                            for value in flags.values()))
        self.assertEqual(self.data["authorized_actions"], [])

    def test_phase8a_has_no_frozen_economic_strategy_or_forward_proof(self):
        self.assertEqual(
            self.data["economic_evidence"],
            "PHASE7_HISTORICAL_BENCHMARK_ONLY",
        )
        for name in (
            "phase8a_strategy_v1_frozen",
            "phase8a_economic_edge_proven",
            "fresh_prospective_shadow_accepted",
            "demo_trading_approved",
            "live_trading_approved",
        ):
            self.assertIs(self.data[name], False)

    def test_strict_json_duplicate_key_denied(self):
        with self.assertRaises(ValueError):
            json.loads('{"run385_authorized":false,'
                       '"run385_authorized":true}',
                       object_pairs_hook=_unique_members)

    def test_authority_data_has_no_executable_endpoint(self):
        serialized = PATH.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", serialized)
        self.assertNotIn("gh api --method POST", serialized)
        self.assertNotIn("api_key", serialized)
        self.assertIn("can never authorize any execution", serialized)
