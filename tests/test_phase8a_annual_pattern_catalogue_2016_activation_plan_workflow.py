from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/phase8a-annual-catalogue-2016-activation-plan.yml"
)


class AnnualCatalogue2016ActivationPlanWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_dec513_successor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2016-activation-plan",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn(
            "      - phase8a-annual-catalogue-2015-replacement-runtime-evidence",
            text,
        )
        self.assertIn("github.event.workflow_run.conclusion == 'success'", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("  push:", text)

    def test_workflow_pins_exact_dec502_to_dec507_chain(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "4d5813b301ab8e22fb2e1e9da36517dfe99f25bb",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "c50442443018922d32f4a19f9d2a31e70e1f53d6",
            "c1a6dcaf5feb005c543097d56901612bff04878c",
            "c03a539c3c54fe7744c82d60f84b1dbd2cba9020",
            "776ec2e50afb4bf2d7ef6807b43ff91fdb31f732",
            "ce2d4ab0ca348bc009277b2b03bdf32fcb703700",
            "2170a62c5d5ad91507796d10cfd7cf8d0c1e52f7",
            "b4fd008939440791e52de0ae7c0015c4ee9576b8",
            "5af3c5787c8904e3371f7840d2a71aa588f16eb9",
            "07e883796cc2a6fea33df3891bc6595bd5270a81",
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        ):
            self.assertIn(blob, text)

    def test_workflow_builds_existing_chain_in_order(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        dec503 = text.index(
            "phase8a_annual_pattern_catalogue_2016_execution_preflight.py"
        )
        dec504 = text.index(
            "phase8a_annual_pattern_catalogue_2016_execution_authorization.py"
        )
        dec506 = text.index(
            "phase8a_annual_pattern_catalogue_2016_runtime_authorization_install_preflight.py"
        )
        dec507 = text.index(
            "phase8a_annual_pattern_catalogue_2016_runtime_authorization_install_action.py"
        )
        self.assertLess(dec503, dec504)
        self.assertLess(dec504, dec506)
        self.assertLess(dec506, dec507)
        self.assertIn('assert preflight["decision"] == "DEC-503"', text)
        self.assertIn('assert authorization["decision"] == "DEC-504"', text)
        self.assertIn('assert install_preflight["decision"] == "DEC-506"', text)
        self.assertIn('assert action["decision"] == "DEC-507"', text)

    def test_compiled_action_is_exact_two_file_and_unexecuted(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert action["action_count"] == 2', text)
        self.assertIn(
            "annual_pattern_catalogue_2016_runtime_authorization.py",
            text,
        )
        self.assertIn("annual_pattern_catalogue_runtime.py", text)
        self.assertIn(
            "1110d07741863649a1cd3ec454bda555d5703bc0",
            text,
        )
        self.assertIn(
            "7979ac17ebcaa13f0c8da5ca5632a8064196d28f",
            text,
        )
        self.assertIn(
            'assert action["repository_mutation_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert action["runtime_authorization_installed"] is False',
            text,
        )
        self.assertIn('assert action["runtime_gate_active"] is False', text)
        self.assertIn(
            'assert action["annual_workflow_dispatch_authorized"] is False',
            text,
        )
        self.assertIn('assert action["trading_authorized"] is False', text)

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
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
