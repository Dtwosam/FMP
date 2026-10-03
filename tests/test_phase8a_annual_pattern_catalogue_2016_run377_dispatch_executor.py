from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-annual-catalogue-2016-runtime-install-executor.yml"
)


class AnnualCatalogue2016Run377DispatchExecutorTests(unittest.TestCase):
    def _dispatch_job(self) -> str:
        text = WORKFLOW.read_text(encoding="utf-8")
        marker = "  dispatch-exact-2016-run-377:\n"
        self.assertIn(marker, text)
        return text.split(marker, 1)[1]

    def test_dec521_runs_only_after_install_and_read_only_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "  dispatch-exact-2016-run-377:\n"
            "    needs:\n"
            "      - install-runtime-authorization\n"
            "      - compile-post-install-dispatch-plan",
            text,
        )
        job = self._dispatch_job()
        self.assertIn("      contents: read", job)
        self.assertIn("      actions: write", job)
        self.assertNotIn("      contents: write", job)

    def test_dec521_consumes_exact_dec519_plan_and_installed_blobs(self) -> None:
        job = self._dispatch_job()
        self.assertIn(
            "annual-catalogue-2016-dec519-dispatch-plan-",
            job,
        )
        for name in (
            "install-commit-sha.txt",
            "runtime-binding.json",
            "dec509-dispatch-preflight.json",
            "dec510-dispatch-authorization.json",
            "dec511-dispatch-action-preflight.json",
        ):
            self.assertIn(name, job)
        for blob in (
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "e6ef74733669ceb8cab13a1e0d25a236526266e3",
            "995bb46ddd95563f904243c78ae4fc3cf3308968",
        ):
            self.assertIn(blob, job)
        self.assertIn(
            'test "$(git rev-parse HEAD)" = "$INSTALL_COMMIT_SHA"',
            job,
        )
        self.assertIn(
            'test "$(git rev-parse origin/main)" = "$INSTALL_COMMIT_SHA"',
            job,
        )

    def test_dec521_requires_exact_376_to_377_slot(self) -> None:
        job = self._dispatch_job()
        self.assertIn(
            'assert max(row["run_number"] for row in all_runs) == 376',
            job,
        )
        self.assertIn(
            'assert not any(row["run_number"] >= 377 for row in all_runs)',
            job,
        )
        self.assertIn("assert len(dispatch_runs) == 2", job)
        self.assertIn('row.get("run_number") == 376', job)
        self.assertIn('first[0]["id"] == 37126711695', job)
        self.assertIn('first[0]["conclusion"] == "failure"', job)
        self.assertIn(
            "select(.run_number >= 377)",
            job,
        )

    def test_dec521_dispatches_exactly_one_2016_run_377(self) -> None:
        job = self._dispatch_job()
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(job.count(command), 1)
        self.assertIn("--ref main", job)
        self.assertIn("-f annual_segment_label=2016", job)
        self.assertIn(
            '-f previous_annual_freeze_run_id="$PREVIOUS_RUN_ID"',
            job,
        )
        self.assertIn('row.get("run_number") == 377', job)
        self.assertIn('row.get("run_attempt") == 1', job)
        self.assertIn('row.get("run_number") >= 378', job)
        self.assertNotIn("-f annual_segment_label=2015", job)

    def test_dec521_receipt_keeps_later_authority_locked(self) -> None:
        job = self._dispatch_job()
        self.assertIn('"decision": "DEC-521"', job)
        self.assertIn(
            '"stage": "ANNUAL_CATALOGUE_2016_RUN_377_DISPATCH_SUBMITTED"',
            job,
        )
        self.assertIn('"dispatch_submitted": True', job)
        self.assertIn('"result_claimed": False', job)
        for field in (
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_378_or_later_authorized",
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
            self.assertIn(f'"{field}": False', job)

    def test_dec521_has_no_rerun_or_trading_surface(self) -> None:
        job = self._dispatch_job()
        for forbidden in (
            "gh run rerun",
            "rerun-failed-jobs",
            "git push",
            "git commit",
            "git add ",
            "order_send(",
            "MetaTrader5",
            "mt5.",
            "broker_order",
            "live_order(",
        ):
            self.assertNotIn(forbidden, job)


if __name__ == "__main__":
    unittest.main()
