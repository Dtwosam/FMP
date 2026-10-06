from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/phase8a-annual-catalogue-2021-runtime-install-action.yml"
)


class AnnualPatternCatalogue2021RuntimeInstallActionWorkflowTests(
    unittest.TestCase
):
    def test_builder_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-runtime-install-action",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)

    def test_builder_pins_exact_dec583_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37486048003",
            "0925e7d51d9c1d513cb737c6b9a00809bad61080",
            "11423396654",
            "4a9de7f416f2297ce315b43f6869a17db34341686c12deced02000fda5342e79",
            "54bb157ee055a5c625f1cb05094e7c4f8228f48766ccdfb163e4d2b07223d575",
            "0798fd16435012b319e4507b48dbd93e95951f0b9986e921340ec4d5d736d77f",
            "9ea8f4574ed1a85cbf0b95031a7450cc4f7fa705",
            "fe600e0eda57a144e81519deab53412a7354e92f",
            "b8ba899634fe1b45ee7a50dc13da97440c3d45d0",
            "de1643991d85cd63e5505401b871e3c02315e0e9",
        ):
            self.assertIn(value, text)

    def test_builder_rechecks_runtime_and_run383_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        current_check = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "4e124365430672fa63825b272001937c60151644"'
        )
        self.assertEqual(text.count(current_check), 2)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2021_runtime_authorization.py",
            text,
        )
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        self.assertIn('382: (37443770076, "success")', text)
        self.assertIn('row["run_number"] >= 383', text)

    def test_builder_freezes_exact_two_file_action_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["action_count"] == 2', text)
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_2021_runtime_authorization.py"',
            text,
        )
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_runtime.py"',
            text,
        )
        self.assertIn(
            '"cac68c905bedf3105aa7e766eaa968c87bff6ce9"',
            text,
        )
        self.assertIn(
            '"d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"',
            text,
        )
        self.assertIn('value["repository_mutation_authorized"] is True', text)
        self.assertIn('"runtime_authorization_installed",', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)

    def test_builder_has_no_stale_prior_decision_names(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for stale in ("dec559", "dec560", "DEC559", "DEC560"):
            self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main()
