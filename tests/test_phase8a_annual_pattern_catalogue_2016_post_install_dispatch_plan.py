from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-annual-catalogue-2016-post-install-dispatch-plan.yml"
)


class AnnualCatalogue2016PostInstallDispatchPlanTests(unittest.TestCase):
    def test_workflow_is_read_only_successor_to_dec515(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2016-post-install-dispatch-plan",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn(
            "      - phase8a-annual-catalogue-2016-runtime-install-executor",
            text,
        )
        self.assertIn(
            "github.event.workflow_run.conclusion == 'success'",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  contents: write", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("  push:", text)

    def test_workflow_pins_exact_post_install_chain(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "537e435e1ba095815c424ee9b7be7a9ba05c9722",
            "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
            "ab15723683f0fa37f5cc4511168cf264f47063c0",
            "730c05c2572fe3397bbcb5c9a5b3874a08032f8c",
            "8de76c1d3a576d365a3d99f15336868165123dd0",
            "925c981e4f6df95f1cbba565bfcfacf40353ba54",
            "301214231775b83df99d1ff9f878f916ec76a07e",
            "6c25446bb7816a4993c2790ae494474e571567c9",
            "87c00381c5c12a0593378f565e6be4bad003514f",
            "d7d3713cb3259e793c448153fd75ca043f511389",
        ):
            self.assertIn(blob, text)

    def test_workflow_requires_digest_verified_dec515_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2016-dec515-runtime-install-",
            text,
        )
        self.assertIn("if length == 1 then .[0].id else empty end", text)
        self.assertIn("if length == 1 then .[0].digest else empty end", text)
        self.assertIn('case "$artifact_digest" in sha256:*)', text)
        self.assertIn('test "$actual_sha" = "$expected_sha"', text)
        for name in (
            "dec508-install-receipt.json",
            "runtime-binding.json",
            "install-commit-sha.txt",
        ):
            self.assertIn(name, text)

    def test_workflow_rebuilds_dec509_to_dec511_in_order(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        d509 = text.index(
            "phase8a_annual_pattern_catalogue_2016_dispatch_preflight.py"
        )
        d510 = text.index(
            "phase8a_annual_pattern_catalogue_2016_dispatch_authorization.py"
        )
        d511 = text.index(
            "phase8a_annual_pattern_catalogue_2016_dispatch_action_preflight.py"
        )
        self.assertLess(d509, d510)
        self.assertLess(d510, d511)
        self.assertIn('assert p509["decision"] == "DEC-509"', text)
        self.assertIn('assert a510["decision"] == "DEC-510"', text)
        self.assertIn('assert p511["decision"] == "DEC-511"', text)
        self.assertIn('assert p511["expected_run_number"] == 3', text)
        self.assertIn('assert p511["expected_run_attempt"] == 1', text)

    def test_final_plan_freezes_exact_run3_inputs_without_execution(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert p511["dispatch_ref"] == "main"', text)
        self.assertIn(
            'assert p511["dispatch_input_annual_segment_label"] == "2016"',
            text,
        )
        self.assertIn(
            'assert p511["dispatch_parameters_frozen"] is True',
            text,
        )
        self.assertIn(
            'assert p511["annual_workflow_dispatch_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert p511["dispatch_command_present"] is False',
            text,
        )
        self.assertIn(
            'assert p511["dispatch_action_executed"] is False',
            text,
        )
        self.assertIn(
            'assert p511["fourth_or_later_run_authorized"] is False',
            text,
        )
        self.assertIn('assert p511["trading_authorized"] is False', text)

    def test_workflow_has_no_mutation_or_dispatch_command(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
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
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
