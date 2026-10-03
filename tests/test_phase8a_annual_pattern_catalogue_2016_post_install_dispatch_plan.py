from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-annual-catalogue-2016-runtime-install-executor.yml"
)


class AnnualCatalogue2016PostInstallDispatchPlanTests(unittest.TestCase):
    def _post_install_job(self) -> str:
        text = WORKFLOW.read_text(encoding="utf-8")
        marker = "  compile-post-install-dispatch-plan:\n"
        next_marker = "  dispatch-exact-2016-run-377:\n"
        self.assertIn(marker, text)
        self.assertIn(next_marker, text)
        return text.split(marker, 1)[1].split(next_marker, 1)[0]

    def test_dec519_is_read_only_second_job_after_dec518(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "  compile-post-install-dispatch-plan:\n"
            "    needs: install-runtime-authorization\n"
            "    permissions:\n"
            "      contents: read\n"
            "      actions: read",
            text,
        )
        job = self._post_install_job()
        self.assertNotIn("contents: write", job)
        self.assertNotIn("actions: write", job)

    def test_dec519_consumes_exact_dec518_install_evidence(self) -> None:
        job = self._post_install_job()
        self.assertIn(
            "annual-catalogue-2016-dec518-runtime-install-",
            job,
        )
        for name in (
            "dec508-install-receipt.json",
            "runtime-binding.json",
            "install-commit-sha.txt",
        ):
            self.assertIn(name, job)
        self.assertIn(
            'test "$(git hash-object '
            'src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py)" '
            '= "e6ef74733669ceb8cab13a1e0d25a236526266e3"',
            job,
        )
        self.assertIn(
            'test "$(git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "995bb46ddd95563f904243c78ae4fc3cf3308968"',
            job,
        )

    def test_dec519_rebuilds_dec509_to_dec511_in_order(self) -> None:
        job = self._post_install_job()
        d509 = job.index(
            "phase8a_annual_pattern_catalogue_2016_dispatch_preflight.py"
        )
        d510 = job.index(
            "phase8a_annual_pattern_catalogue_2016_dispatch_authorization.py"
        )
        d511 = job.index(
            "phase8a_annual_pattern_catalogue_2016_dispatch_action_preflight.py"
        )
        self.assertLess(d509, d510)
        self.assertLess(d510, d511)
        self.assertIn('assert p509["decision"] == "DEC-509"', job)
        self.assertIn('assert a510["decision"] == "DEC-510"', job)
        self.assertIn('assert p511["decision"] == "DEC-511"', job)
        self.assertIn('assert p511["expected_run_number"] == 377', job)
        self.assertIn('assert p511["expected_run_attempt"] == 1', job)

    def test_dec519_freezes_run3_without_dispatch(self) -> None:
        job = self._post_install_job()
        self.assertIn('assert p511["dispatch_ref"] == "main"', job)
        self.assertIn(
            'assert p511["dispatch_input_annual_segment_label"] == "2016"',
            job,
        )
        self.assertIn('assert p511["dispatch_parameters_frozen"] is True', job)
        self.assertIn(
            'assert p511["annual_workflow_dispatch_authorized"] is True',
            job,
        )
        self.assertIn('assert p511["dispatch_command_present"] is False', job)
        self.assertIn('assert p511["dispatch_action_executed"] is False', job)
        self.assertIn(
            'assert p511["fourth_or_later_run_authorized"] is False',
            job,
        )
        self.assertIn('assert p511["trading_authorized"] is False', job)
        self.assertIn(
            "annual-catalogue-2016-dec519-dispatch-plan-",
            job,
        )

    def test_dec519_job_has_no_mutation_or_dispatch_command(self) -> None:
        job = self._post_install_job()
        for forbidden in (
            "gh workflow run ",
            "gh run rerun",
            "git push",
            "git commit",
            "git add ",
            "gh api --method POST",
            "gh api --method PUT",
            "gh api --method PATCH",
            "order_send(",
            "MetaTrader5",
            "mt5.",
        ):
            self.assertNotIn(forbidden, job)


if __name__ == "__main__":
    unittest.main()
