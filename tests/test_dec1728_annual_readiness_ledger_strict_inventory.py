"""DEC-1728: fail-closed schema inventory for source-only annual ledger.

These tests inspect a nonauthorizing documentation JSON file. They do not
validate GitHub server-side state, authorize protected work or run trading.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest


PATH = (Path(__file__).resolve().parents[1] /
        "docs/dec1726-phase8a-sourceonly-segment-gate-ledger.json")
ROOT_FIELDS = frozenset((
    "schema", "decision", "description", "capture_date",
    "live_administration_evidence_verified",
    "live_annual_run_385_inventory_verified",
    "main_branch_last_public_observation", "previous_annual_freeze",
    "yearly_catalogue_status", "next_protected_segment",
    "required_external_gates", "external_gate_status",
    "economic_evidence", "phase8a_strategy_v1_frozen",
    "phase8a_economic_edge_proven", "fresh_prospective_shadow_accepted",
    "demo_trading_approved", "live_trading_approved",
    "authority_flags", "authorized_actions", "caveat",
))
FLAGS = frozenset((
    "annual_workflow_dispatch_authorized",
    "protected_history_access_authorized",
    "run385_authorized", "run385_executed",
    "retry_or_rerun_authorized", "later_years_research_authorized",
    "cross_year_synthesis_authorized", "strategy_promotion_authorized",
    "phase8b_authorized", "broker_mutation_authorized",
    "demo_orders_authorized", "real_money_authorized",
    "live_orders_authorized", "trading_authorized",
))
GATE_FIELDS = frozenset((
    "segment", "research_evidence", "promotion_eligible",
))
EXPECTED_LATER = (
    ("2023", "BLOCKED_UNVERIFIED_CURRENT_RUN_INVENTORY"),
    ("2024", "BLOCKED_NO_AUTHORIZED_PRIOR_2023_FREEZE"),
    ("2025", "BLOCKED_NO_AUTHORIZED_PRIOR_2024_FREEZE"),
    ("2026_YTD_TO_2026_08_20",
     "BLOCKED_NO_AUTHORIZED_PRIOR_2025_FREEZE"),
)


def _no_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate Phase8A ledger key")
        value[key] = item
    return value


class Phase8AReadinessLedgerStrictInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = PATH.read_text(encoding="utf-8")
        cls.data = json.loads(cls.document,
                              object_pairs_hook=_no_duplicate_keys)

    def test_exact_top_level_field_inventory(self):
        self.assertEqual(set(self.data), ROOT_FIELDS)

    def test_exact_authority_name_inventory_and_bool_types(self):
        flags = self.data["authority_flags"]
        self.assertEqual(set(flags), FLAGS)
        self.assertTrue(all(type(v) is bool and v is False
                            for v in flags.values()))

    def test_historical_rows_have_no_extra_claims_or_statuses(self):
        rows = self.data["yearly_catalogue_status"]
        self.assertEqual(len(rows), 12)
        for i, year in enumerate(range(2015, 2023)):
            row = rows[i]
            with self.subTest(year=year):
                self.assertEqual(set(row), GATE_FIELDS)
                self.assertEqual(row["segment"], str(year))
                self.assertEqual(row["research_evidence"],
                                 "HISTORICALLY_FROZEN")
                self.assertIs(row["promotion_eligible"], False)

    def test_later_rows_preserve_exact_blocked_reasons(self):
        rows = self.data["yearly_catalogue_status"][8:]
        self.assertEqual(len(rows), 4)
        for i, (segment, reason) in enumerate(EXPECTED_LATER):
            row = rows[i]
            with self.subTest(segment=segment):
                expected = GATE_FIELDS | (
                    {"expected_run_number", "expected_attempt"}
                    if i == 0 else set()
                )
                self.assertEqual(set(row), expected)
                self.assertEqual(row["segment"], segment)
                self.assertEqual(row["research_evidence"], reason)
                self.assertIs(row["promotion_eligible"], False)

    def test_2023_one_shot_is_strict_integer_not_boolean(self):
        row = self.data["yearly_catalogue_status"][8]
        self.assertIs(type(row["expected_run_number"]), int)
        self.assertIs(type(row["expected_attempt"]), int)
        self.assertEqual(row["expected_run_number"], 385)
        self.assertEqual(row["expected_attempt"], 1)

    def test_prior_freeze_inventory_is_only_historical(self):
        prior = self.data["previous_annual_freeze"]
        self.assertEqual(set(prior), {
            "segment", "run_number", "run_id", "source_provenance",
        })
        self.assertEqual(prior["segment"], "2022")
        self.assertIs(type(prior["run_number"]), int)
        self.assertIs(type(prior["run_id"]), int)
        self.assertEqual(prior["run_number"], 384)
        self.assertEqual(prior["run_id"], 37663157285)
        self.assertEqual(
            prior["source_provenance"],
            "HISTORICALLY_ACCEPTED_NOT_REAUTHENTICATED_FOR_DISPATCH",
        )

    def test_observed_branch_does_not_masquerade_as_current_admin_proof(self):
        branch = self.data["main_branch_last_public_observation"]
        self.assertEqual(set(branch), {
            "sha", "protected", "is_current_at_action_time",
            "proves_exclusive_no_bypass_lock",
        })
        self.assertEqual(branch["sha"],
                         "53e203133bbc141b2f48c7b8b8241d56b35166a3")
        for name in ("protected", "is_current_at_action_time",
                     "proves_exclusive_no_bypass_lock"):
            self.assertIs(branch[name], False)

    def test_economic_status_and_action_list_are_strictly_denied(self):
        self.assertIs(type(self.data["authorized_actions"]), list)
        self.assertEqual(self.data["authorized_actions"], [])
        self.assertEqual(self.data["external_gate_status"], "BLOCKED")
        self.assertEqual(self.data["next_protected_segment"], "2023")
        self.assertEqual(
            self.data["economic_evidence"],
            "PHASE7_HISTORICAL_BENCHMARK_ONLY",
        )
        self.assertTrue(
            all(self.data[key] is False for key in (
                "phase8a_strategy_v1_frozen",
                "phase8a_economic_edge_proven",
                "fresh_prospective_shadow_accepted",
                "demo_trading_approved",
                "live_trading_approved",
                "live_administration_evidence_verified",
                "live_annual_run_385_inventory_verified",
            ))
        )
