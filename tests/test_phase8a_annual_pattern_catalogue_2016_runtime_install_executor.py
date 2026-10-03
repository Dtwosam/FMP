from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-annual-catalogue-2016-runtime-install-executor.yml"
)


class AnnualCatalogue2016RuntimeInstallExecutorTests(unittest.TestCase):
    def _install_job(self) -> str:
        text = WORKFLOW.read_text(encoding="utf-8")
        marker = "  install-runtime-authorization:\n"
        next_marker = "  compile-post-install-dispatch-plan:\n"
        self.assertIn(marker, text)
        self.assertIn(next_marker, text)
        return text.split(marker, 1)[1].split(next_marker, 1)[0]

    def test_workflow_is_success_only_dec514_installer(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        install_job = self._install_job()
        self.assertIn(
            "name: phase8a-annual-catalogue-2016-runtime-install-executor",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn(
            "      - phase8a-annual-catalogue-2016-activation-plan",
            text,
        )
        self.assertIn(
            "github.event.workflow_run.conclusion == 'success'",
            text,
        )
        self.assertIn("      contents: write", install_job)
        self.assertIn("      actions: read", install_job)
        self.assertNotIn("      actions: write", install_job)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("  push:", text)

    def test_installer_pins_exact_frozen_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "3b81c15f77b024c1e777e4cb9a9a80ded18f2277",
            "e5bb5dce82111a29997783fcdc4df0f70883700e",
            "7da956910e24e788a2f2a60834c04048a660bc75",
            "7d355784598c48d39ac0d3964145b46b878d18a3",
            "e6ef74733669ceb8cab13a1e0d25a236526266e3",
            "995bb46ddd95563f904243c78ae4fc3cf3308968",
            "457c1ffe9cd012041a3d6c3a5568776d8c6fe68a",
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        ):
            self.assertIn(blob, text)

    def test_installer_requires_unique_digest_verified_dec514_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2016-dec514-activation-plan-",
            text,
        )
        self.assertIn("if length == 1 then .[0].id else empty end", text)
        self.assertIn("if length == 1 then .[0].digest else empty end", text)
        self.assertIn('case "$artifact_digest" in sha256:*)', text)
        self.assertIn('test "$actual_zip_sha" = "$expected_zip_sha"', text)
        self.assertIn("dec507-install-action.json", text)
        self.assertIn("runtime-binding.json", text)

    def test_installer_mutates_exactly_two_frozen_paths(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        gate = (
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2016_runtime_authorization.py"
        )
        runtime = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        self.assertIn(gate, text)
        self.assertIn(runtime, text)
        self.assertIn(
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_2016_runtime_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2016_authorization.py.disabled",
            text,
        )
        self.assertIn(
            'test "$(git diff --cached --name-only | wc -l | tr -d \' \')" = "2"',
            text,
        )
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("git push --force", text)

    def test_installer_rechecks_main_before_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            text.count('test "$(git rev-parse origin/main)" = "$SOURCE_HEAD_SHA"'),
            2,
        )
        self.assertIn('test "$(git rev-parse HEAD)" = "$SOURCE_HEAD_SHA"', text)
        self.assertIn('test -z "$(git status --porcelain)"', text)

    def test_installer_builds_concrete_dec508_receipt(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2016_runtime_authorization_install_receipt.py",
            text,
        )
        self.assertIn('assert receipt["decision"] == "DEC-508"', text)
        self.assertIn(
            'assert receipt["runtime_authorization_installed"] is True',
            text,
        )
        self.assertIn('assert receipt["runtime_gate_active"] is True', text)
        self.assertIn(
            'assert receipt["annual_workflow_dispatch_authorized"] is False',
            text,
        )
        self.assertIn('assert receipt["trading_authorized"] is False', text)

    def test_installer_has_no_dispatch_or_trading_command(self) -> None:
        text = self._install_job()
        for forbidden in (
            "gh workflow run ",
            "gh run rerun",
            "rerun-failed-jobs",
            "order_send(",
            "MetaTrader5",
            "mt5.",
            "broker_order",
            "live_order(",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
