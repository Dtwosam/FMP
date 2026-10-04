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
            "70f1460f0b5a703b084c40e2c361a229f876898e",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "400e9715a6e3b2dab413ce2ecff0fbce8c46f6b0",
            "b6764addd7b471e65f05428f745fa93051bd8785",
            "b60c03e7f2e18f62df04ec450a36aec5d9985cca",
            "c52a88ff3159de35160c11061403172689433330",
            "0545f0474bdead4e479c07b9af889db842bf00dd",
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
            "4bb008eedc2ca0676cf25dd3cfcebba5eac0eaff",
            text,
        )
        self.assertIn(
            "b564f5a26fdef146fc6080962e7c4762b0b5949a",
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
