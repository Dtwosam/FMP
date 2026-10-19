"""DEC-1764 frozen Phase7 cost replay, never Strategy V1 profitability."""
import contextlib
import copy
from decimal import Decimal
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "dec1764_phase7_historical_cost_stress.py"
MODULE = runpy.run_path(str(SCRIPT))
REPLAY = MODULE["replay_phase7_cost_evidence"]
ORIGINAL = ROOT / "docs" / "phase7-walk-forward-evidence.md"


class Phase7CostStressHistoricalReplayTests(unittest.TestCase):
    def test_exact_frozen_historical_stage2_source_identity(self):
        report = REPLAY()
        self.assertEqual(report["source_git_blob_sha1"],
                         "c1d8fe7f71681f2e06b472c77525a4dd800c896f")
        self.assertEqual(report["phase7_stage2_run"], 35015277625)

    def test_all_three_published_cost_scenarios_preserved(self):
        rows = REPLAY()["observations"]
        self.assertEqual([r["adverse_slippage_pips"] for r in rows],
                         ["0.2", "0.5", "1.0"])
        self.assertEqual([r["historical_net_return_pct"] for r in rows],
                         ["0.757266", "0.262176", "-0.562118"])
        self.assertTrue(all(r["trades"] == 199 for r in rows))

    def test_slippage_sensitivity_and_sign_reversal_are_not_erased(self):
        result = REPLAY()
        self.assertEqual(result["historical_slippage_sign_reversal_bracket_pips"],
                         ["0.5", "1.0"])
        self.assertEqual(result["historical_return_slope_pct_points_per_pip"],
                         ["-1.65030", "-1.648588"])
        self.assertTrue(Decimal(
            result["linear_zero_interpolation_pips_not_observed"]
        ) > Decimal("0.5"))
        self.assertTrue(Decimal(
            result["linear_zero_interpolation_pips_not_observed"]
        ) < Decimal("1.0"))

    def test_interpolated_root_not_misrepresented_as_an_observed_trade(self):
        result = REPLAY()
        self.assertEqual(result["linear_zero_interpolation_pips_not_observed"],
                         "0.659031")
        self.assertIn("illustrative arithmetic", result["caveat"])
        self.assertIn("not an observed", result["caveat"])

    def test_golden_net_pnl_and_profit_factor_keep_negative_cost_case(self):
        rows = REPLAY()["observations"]
        self.assertEqual([r["historical_net_pnl_usd"] for r in rows],
                         ["757.27", "262.18", "-562.12"])
        self.assertEqual([r["historical_profit_factor"] for r in rows],
                         ["1.062731", "1.021310", "0.955760"])

    def test_no_future_strategy_or_broker_authority_ever_claimed(self):
        report = REPLAY()
        self.assertIsNone(report["forward_profit_claim"])
        self.assertEqual(report["allowed_actions"], [])
        for flag in (
            "phase8a_strategy_v1_edge_proven",
            "phase8a_strategy_v1_frozen",
            "protected_2023_run385_authorized",
            "shadow_or_demo_approved",
            "broker_order_authorized",
            "live_trading_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(report[flag], False)

    def test_report_replay_is_byte_equivalent_for_same_source(self):
        a, b = REPLAY(), REPLAY()
        self.assertEqual(json.dumps(a, sort_keys=True),
                         json.dumps(b, sort_keys=True))

    def test_changed_historic_source_even_nonmetric_text_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "source.md"
            path.write_bytes(ORIGINAL.read_bytes() + b"\neditorial change\n")
            with self.assertRaisesRegex(ValueError, "reviewed Git blob"):
                REPLAY(path)


    def test_window_rollup_preserves_all_seven_retrospective_periods(self):
        result = REPLAY()
        rows = result["historical_0_2_pip_windows"]
        self.assertEqual(len(rows), 7)
        self.assertEqual(result["historical_window_trade_count"], 199)
        self.assertEqual(
            [w["window"] for w in rows],
            ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4",
             "2026-Q1", "2026-Q2", "2026-partial-Q3"],
        )

    def test_2025_first_quarter_negative_is_not_erased(self):
        row = REPLAY()["historical_0_2_pip_windows"][0]
        self.assertEqual(row["window"], "2025-Q1")
        self.assertEqual(row["historic_net_return_pct"], "-0.520185")
        self.assertEqual(row["historic_net_pnl_usd"], "-520.18")

    def test_2026_partial_quarter_loss_not_hidden_by_aggregate(self):
        row = REPLAY()["historical_0_2_pip_windows"][-1]
        self.assertEqual(row["window"], "2026-partial-Q3")
        self.assertEqual(row["historic_net_return_pct"], "-0.645978")
        self.assertEqual(row["historic_net_pnl_usd"], "-645.98")
        self.assertEqual(row["trades"], 16)

    def test_two_negative_periods_and_five_positive_are_retained(self):
        result = REPLAY()
        self.assertEqual(
            result["historical_negative_windows"],
            ["2025-Q1", "2026-partial-Q3"],
        )
        self.assertEqual(result["historical_positive_window_count"], 5)

    def test_historic_0_2_pip_window_returns_reconcile_with_rounding(self):
        result = REPLAY()
        summed = Decimal(result["historical_window_returns_sum_pct"])
        published = Decimal(result["observations"][0]["historical_net_return_pct"])
        self.assertLessEqual(abs(summed - published), Decimal("0.00001"))

    def test_both_losing_windows_are_retrospective_not_strategy_v1(self):
        result = REPLAY()
        self.assertEqual(result["historical_positive_window_count"], 5)
        self.assertIs(result["phase8a_strategy_v1_edge_proven"], False)
        self.assertIsNone(result["forward_profit_claim"])
        self.assertEqual(result["allowed_actions"], [])


    def test_frozen_phase7_reader_rejects_symlink_to_valid_document(self):
        with tempfile.TemporaryDirectory() as folder:
            alias = Path(folder) / "old-evidence.md"
            try:
                alias.symlink_to(ORIGINAL)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable in this environment")
            with self.assertRaises(OSError):
                REPLAY(alias)

    def test_phase7_source_reader_rejects_special_fifo_without_hanging(self):
        import os
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO unavailable in this environment")
        with tempfile.TemporaryDirectory() as folder:
            fifo = Path(folder) / "named-pipe.md"
            os.mkfifo(fifo)
            with self.assertRaises(ValueError):
                REPLAY(fifo)

    def test_phase7_source_reader_rejects_oversized_document(self):
        with tempfile.TemporaryDirectory() as folder:
            large = Path(folder) / "large.md"
            large.write_bytes(b" " * (MODULE["MAX_PHASE7_DOCUMENT_BYTES"] + 1))
            with self.assertRaises(ValueError):
                REPLAY(large)

    def test_phase7_source_reader_rejects_empty_document(self):
        with tempfile.TemporaryDirectory() as folder:
            empty = Path(folder) / "empty.md"
            empty.write_bytes(b"")
            with self.assertRaises(ValueError):
                REPLAY(empty)

    def test_phase7_replay_does_not_change_frozen_file(self):
        before = ORIGINAL.read_bytes()
        result = REPLAY()
        self.assertEqual(ORIGINAL.read_bytes(), before)
        self.assertEqual(result["status"], "RETROSPECTIVE_DIAGNOSTIC_NOT_EXECUTION_AUTHORITY")

    def test_phase7_cli_symlink_input_exits_two_without_stdout(self):
        with tempfile.TemporaryDirectory() as folder:
            alias = Path(folder) / "old-evidence.md"
            try:
                alias.symlink_to(ORIGINAL)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable in this environment")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = MODULE["main"](["--phase7-document", str(alias)])
            self.assertEqual(code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("BLOCKED:", stderr.getvalue())


    def test_gross_positive_and_negative_window_pnl_sum_to_original_total(self):
        attribution = REPLAY()["historical_0_2_pip_pnl_attribution"]
        self.assertEqual(attribution["gross_positive_window_pnl_usd"], "1923.43")
        self.assertEqual(attribution["gross_negative_window_pnl_usd"], "-1166.16")
        self.assertEqual(attribution["net_window_pnl_usd"], "757.27")
        self.assertEqual(
            Decimal(attribution["gross_positive_window_pnl_usd"])
            + Decimal(attribution["gross_negative_window_pnl_usd"]),
            Decimal(attribution["net_window_pnl_usd"]),
        )

    def test_historical_losses_consumed_over_sixty_pct_of_winning_pnl(self):
        attribution = REPLAY()["historical_0_2_pip_pnl_attribution"]
        self.assertEqual(attribution["negative_pnl_as_pct_of_positive_pnl"],
                         "60.6292")
        self.assertGreater(
            Decimal(attribution["negative_pnl_as_pct_of_positive_pnl"]),
            Decimal("60"),
        )

    def test_largest_positive_window_and_independent_capital_are_explicit(self):
        attribution = REPLAY()["historical_0_2_pip_pnl_attribution"]
        self.assertEqual(attribution["largest_positive_window_pnl_usd"],
                         "674.39")
        self.assertEqual(attribution["largest_positive_share_of_positive_pnl_pct"],
                         "35.062")
        self.assertEqual(attribution["independent_starting_equity_per_window_usd"],
                         "100000")
        self.assertIs(attribution["not_a_compounded_portfolio_return"], True)

    def test_source_only_attribution_does_not_grant_any_forward_profit(self):
        report = REPLAY()
        self.assertEqual(report["status"],
                         "RETROSPECTIVE_DIAGNOSTIC_NOT_EXECUTION_AUTHORITY")
        self.assertIsNone(report["forward_profit_claim"])
        self.assertIs(report["phase8a_strategy_v1_edge_proven"], False)
        self.assertIs(report["broker_order_authorized"], False)
        self.assertEqual(report["allowed_actions"], [])


    def test_phase7_parent_directory_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "real"
            folder.mkdir()
            copied = folder / "phase7.md"
            copied.write_bytes(ORIGINAL.read_bytes())
            alias = Path(root) / "alias"
            try:
                alias.symlink_to(folder, target_is_directory=True)
            except (NotImplementedError, OSError):
                self.skipTest("directory symlinks unavailable")
            with self.assertRaises(OSError):
                REPLAY(alias / copied.name)

    def test_phase7_parent_symlink_cli_returns_no_report(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "real"
            folder.mkdir()
            (folder / "evidence.md").write_bytes(ORIGINAL.read_bytes())
            alias = Path(root) / "alias"
            try:
                alias.symlink_to(folder, target_is_directory=True)
            except (NotImplementedError, OSError):
                self.skipTest("directory symlinks unavailable")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = MODULE["main"](["--phase7-document", str(alias / "evidence.md")])
            self.assertEqual(code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("BLOCKED:", stderr.getvalue())

    def test_phase7_real_subdirectory_is_accepted_at_retro_exit_three(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "real"
            folder.mkdir()
            copied = folder / "phase7.md"
            copied.write_bytes(ORIGINAL.read_bytes())
            self.assertEqual(REPLAY(copied)["status"],
                             "RETROSPECTIVE_DIAGNOSTIC_NOT_EXECUTION_AUTHORITY")


    def test_leave_one_out_excludes_each_published_period_once(self):
        report = REPLAY()
        rows = report["historical_0_2_pip_leave_one_out"]
        self.assertEqual(len(rows), 7)
        self.assertEqual(
            [r["excluded_historical_window"] for r in rows],
            [w["window"] for w in report["historical_0_2_pip_windows"]])

    def test_removing_strongest_window_leaves_only_small_positive_pnl(self):
        row = REPLAY()["historical_0_2_pip_leave_one_out_min"]
        self.assertEqual(row["excluded_historical_window"], "2025-Q4")
        self.assertEqual(row["remaining_rounded_window_pnl_usd"], "82.88")

    def test_removing_two_strongest_windows_turns_retro_result_negative(self):
        row = REPLAY()["historical_0_2_pip_leave_two_out_min"]
        self.assertEqual(
            row["excluded_historical_windows"], ["2025-Q2", "2025-Q4"])
        self.assertEqual(row["remaining_rounded_window_pnl_usd"], "-591.29")

    def test_all_twenty_one_historical_two_window_exclusions_are_exhaustive(self):
        report = REPLAY()
        combos = report["historical_0_2_pip_leave_two_out"]
        self.assertEqual(len(combos), 21)
        self.assertEqual(
            len({tuple(row["excluded_historical_windows"]) for row in combos}),
            21)
        self.assertEqual(
            sum(Decimal(row["remaining_rounded_window_pnl_usd"]) < 0
                for row in combos), 5)
        self.assertEqual(
            report["historical_0_2_pip_negative_after_two_exclusions_count"],
            5)

    def test_exclusion_arithmetic_is_not_a_confidence_interval_or_strategy(self):
        report = REPLAY()
        self.assertIs(
            report["historical_window_exclusion_is_not_statistical_validation"],
            True)
        self.assertIs(report["phase8a_strategy_v1_edge_proven"], False)
        self.assertIsNone(report["forward_profit_claim"])
        self.assertEqual(report["allowed_actions"], [])

    def test_only_published_cost_scenarios_are_compared(self):
        result = REPLAY()
        rows = result["historical_aggregate_cost_step_changes"]
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            [(r["from_reported_slippage_pips"],
              r["to_reported_slippage_pips"]) for r in rows],
            [("0.2", "0.5"), ("0.5", "1.0")])
        self.assertIs(
            result["no_unreported_slippage_or_per_window_costs_inferred"], True)

    def test_historical_aggregate_return_and_pnl_drop_as_slippage_rises(self):
        rows = REPLAY()["historical_aggregate_cost_step_changes"]
        self.assertEqual(
            [r["observed_aggregate_return_change_percentage_points"]
             for r in rows], ["-0.495090", "-0.824294"])
        self.assertEqual(
            [r["observed_aggregate_pnl_change_usd"] for r in rows],
            ["-495.09", "-824.30"])

    def test_historical_expectancy_drops_and_max_window_drawdown_rises(self):
        rows = REPLAY()["historical_aggregate_cost_step_changes"]
        self.assertEqual(
            [r["observed_expectancy_change_usd_per_trade"] for r in rows],
            ["-2.4879", "-4.1422"])
        self.assertTrue(all(
            Decimal(r["observed_max_window_dd_increase_percentage_points"]) > 0
            for r in rows))

    def test_positive_window_support_weakens_from_five_to_four(self):
        result = REPLAY()
        self.assertEqual(
            result["historical_profitable_window_count_by_reported_slippage"],
            [5, 4, 4])
        self.assertIs(
            result["historical_1_0_pip_return_and_profit_factor_below_zero_or_one"],
            True)

    def test_cost_ladder_is_historical_not_strategy_v1_authority(self):
        result = REPLAY()
        self.assertIs(result["phase8a_strategy_v1_edge_proven"], False)
        self.assertIsNone(result["forward_profit_claim"])
        self.assertIs(result["live_trading_authorized"], False)
        self.assertEqual(result["allowed_actions"], [])

    def test_historical_document_has_separate_pinned_sha256(self):
        report = REPLAY()
        self.assertEqual(
            report["source_document_sha256"],
            "afe93d152e52c5a18b003967f97a411f2a1ac60dd54d913920536faa1863bb75",
        )
        self.assertEqual(
            MODULE["FROZEN_PHASE7_DOC_SHA256"],
            report["source_document_sha256"],
        )
        self.assertNotEqual(
            report["source_document_sha256"],
            report["source_git_blob_sha1"],
        )

    def test_sha256_detects_edit_even_when_git_blob_check_is_stubbed(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as folder:
            tampered = Path(folder) / "phase7.md"
            tampered.write_bytes(ORIGINAL.read_bytes() + b"\nretrospective drift\n")
            with mock.patch.object(MODULE["hashlib"], "sha1") as fake_sha1:
                fake_sha1.return_value.hexdigest.return_value = (
                    MODULE["FROZEN_GIT_BLOB_SHA1"])
                with self.assertRaisesRegex(ValueError, "pinned SHA-256"):
                    REPLAY(tampered)

    def test_sha256_identity_does_not_claim_future_trade_authority(self):
        report = REPLAY()
        self.assertEqual(len(report["source_document_sha256"]), 64)
        self.assertIs(report["protected_2023_run385_authorized"], False)
        self.assertIs(report["live_trading_authorized"], False)
        self.assertIsNone(report["forward_profit_claim"])

    def test_cli_returns_nonzero_even_with_correct_historical_report(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = MODULE["main"]([])
        self.assertEqual(code, 3)
        self.assertEqual(stderr.getvalue(), "")
        self.assertFalse(json.loads(stdout.getvalue())["broker_order_authorized"])

    def test_cli_rejects_untrusted_history_without_output(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "wrong.md"
            path.write_text("# hypothetical profits", encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = MODULE["main"](["--phase7-document", str(path)])
            self.assertEqual(code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("BLOCKED:", stderr.getvalue())
