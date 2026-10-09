from __future__ import annotations

"""DEC-628: actual CLI subprocess tests of checkout-local report-output denial."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "phase8a_annual_pattern_catalogue_2023_"
DECISIONS = {
    "main_lock_readiness": "DEC-612",
    "immutable_tag_feasibility": "DEC-615",
    "tag_ruleset_static_review": "DEC-616",
    "tag_ref_guard_rehearsal": "DEC-617",
}
SHA = "a" * 40


def _input_args(suffix: str, missing: Path) -> list[str]:
    if suffix == "main_lock_readiness":
        result = []
        for flag in (
            "dec611-audit-json", "main-branch-json", "annual-workflow-runs-json",
            "branch-protection-json", "effective-branch-rules-json", "inherited-rulesets-json",
        ):
            result += ["--" + flag, str(missing)]
        return result + ["--expected-head-sha", SHA]
    if suffix == "immutable_tag_feasibility":
        return [
            "--dec614-handoff-json", str(missing),
            "--main-branch-json", str(missing),
            "--annual-workflow-runs-json", str(missing),
            "--expected-head-sha", SHA,
        ]
    if suffix == "tag_ruleset_static_review":
        return [
            "--tag-ref", "refs/tags/fmp/phase8a/2023/run385/dec628-test-only",
            "--reviewed-commit-sha", SHA,
            "--git-ref-json", str(missing),
            "--rulesets-json", str(missing),
        ]
    if suffix == "tag_ref_guard_rehearsal":
        return [
            "--candidate-tag-ref", "refs/tags/fmp/phase8a/2023/run385/dec628-test-only",
            "--reviewed-commit-sha", SHA,
        ]
    raise ValueError("unexpected DEC-628 test CLI")


def _file_hashes(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-628 requires frozen installed annual workflow source",
)
class CheckoutReportOutputLockTests(unittest.TestCase):
    def test_four_guard_locations_precede_any_input_read(self):
        self.assertEqual(len(DECISIONS), 4)
        for suffix, decision in DECISIONS.items():
            source = (ROOT / "scripts" / f"{PREFIX}{suffix}.py").read_text()
            with self.subTest(decision=decision):
                guard = 'if target.is_relative_to(checkout):'
                self.assertEqual(source.count(guard), 1)
                self.assertIn(f'{decision} refuses audit output inside checkout', source)
                self.assertIn('target = args.out.resolve()', source)
                self.assertIn('checkout = Path(__file__).resolve().parents[1]', source)
                self.assertNotIn('checkout = Path.cwd().resolve()', source)
                self.assertIn('sys.dont_write_bytecode = True', source)
                self.assertLess(source.index(guard), source.index('    value = build_') if decision == "DEC-612"
                                else source.index('    result = build_') if decision in {"DEC-615", "DEC-617"}
                                else source.index('    report = inspect_'))
                self.assertIn('write_once_external_report(target,', source)
                self.assertIn(
                    'from fmp.discovery.annual_pattern_catalogue_2023_external_report_create '
                    'import write_once_external_report', source,
                )
                self.assertNotIn('target.write_text(', source)
                self.assertLess(source.index(guard), source.index('write_once_external_report(target,'))
                self.assertNotIn('args.out.write_text(', source)

    def test_cli_rejects_relative_absolute_and_symlinked_checkout_outputs_first(self):
        with tempfile.TemporaryDirectory(prefix="dec628-outside-checkout-") as tmp:
            parent = Path(tmp)
            checkout = parent / "checkout"
            shutil.copytree(
                ROOT / "src" / "fmp",
                checkout / "src" / "fmp",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            scripts = checkout / "scripts"
            scripts.mkdir()
            for suffix in DECISIONS:
                filename = f"{PREFIX}{suffix}.py"
                shutil.copy2(ROOT / "scripts" / filename, scripts / filename)
            workflow = checkout / ".github" / "workflows" / "phase8a-annual-pattern-catalogue.yml"
            workflow.parent.mkdir(parents=True)
            shutil.copy2(ROOT / ".github" / "workflows" / workflow.name, workflow)

            reports = checkout / "reports"
            reports.mkdir()
            sentinel = reports / "existing.json"
            sentinel.write_text("DO NOT OVERWRITE\n")
            outside_link = parent / "alias-to-checkout"
            outside_link.symlink_to(checkout, target_is_directory=True)
            missing = parent / "nonexistent-input.json"
            self.assertFalse(missing.exists())
            baseline = _file_hashes(checkout)
            env = os.environ.copy()
            env["PYTHONPATH"] = str(checkout / "src")
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            for suffix, decision in DECISIONS.items():
                name = f"{PREFIX}{suffix}.py"
                attempts = (
                    ("relative", "reports/rejected.json", checkout),
                    ("absolute", str(reports / "rejected.json"), checkout),
                    ("parent_relative", "../checkout/reports/rejected.json", checkout),
                    ("symlink_alias", str(outside_link / "reports" / "rejected.json"), checkout),
                    ("existing_file", str(sentinel), checkout),
                    # The old Path.cwd() guard would accept these locations,
                    # even though the source is still under the same checkout.
                    ("subdir_to_parent", "../reports/rejected.json", scripts),
                    ("subdir_parent_sibling", "../../checkout/reports/rejected.json", scripts),
                    ("outside_cwd_absolute", str(reports / "rejected.json"), parent),
                    ("subdir_existing", str(sentinel), scripts),
                )
                for label, out, workdir in attempts:
                    with self.subTest(decision=decision, mode=label):
                        cmd = [
                            sys.executable, str(scripts / name), "assess",
                            *_input_args(suffix, missing), "--out", out,
                        ]
                        completed = subprocess.run(
                            cmd, cwd=workdir, env=env, text=True, capture_output=True,
                            timeout=40, check=False,
                        )
                        self.assertNotEqual(completed.returncode, 0)
                        self.assertIn(f"{decision} refuses audit output inside checkout", completed.stderr)
                        self.assertEqual(sentinel.read_text(), "DO NOT OVERWRITE\n")
                        self.assertEqual(_file_hashes(checkout), baseline)
                        self.assertEqual(list(checkout.rglob("*.pyc")), [])
            self.assertFalse(missing.exists())

    def test_real_assess_can_write_external_report_and_remains_denied(self):
        """Successful offline audits still work without touching source files."""
        with tempfile.TemporaryDirectory(prefix="dec628-positive-") as tmp:
            parent = Path(tmp)
            checkout = parent / "checkout"
            shutil.copytree(
                ROOT / "src" / "fmp",
                checkout / "src" / "fmp",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            scripts = checkout / "scripts"
            scripts.mkdir()
            for suffix in ("tag_ruleset_static_review", "tag_ref_guard_rehearsal"):
                name = f"{PREFIX}{suffix}.py"
                shutil.copy2(ROOT / "scripts" / name, scripts / name)
            workflow = checkout / ".github" / "workflows" / "phase8a-annual-pattern-catalogue.yml"
            workflow.parent.mkdir(parents=True)
            shutil.copy2(ROOT / ".github" / "workflows" / workflow.name, workflow)
            ref = "refs/tags/fmp/phase8a/2023/run385/dec628-test-only"
            ref_path = parent / "untrusted-ref.json"
            ref_path.write_text(json.dumps({"ref": ref, "object": {"type": "commit", "sha": SHA}}))
            rules_path = parent / "untrusted-rulesets.json"
            rules_path.write_text("[]")
            baseline = _file_hashes(checkout)
            env = os.environ.copy()
            env["PYTHONPATH"] = str(checkout / "src")
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            commands = (
                (
                    "tag_ruleset_static_review",
                    [
                        "--tag-ref", ref, "--reviewed-commit-sha", SHA,
                        "--git-ref-json", str(ref_path), "--rulesets-json", str(rules_path),
                    ],
                    "DEC-616",
                ),
                (
                    "tag_ref_guard_rehearsal",
                    ["--candidate-tag-ref", ref, "--reviewed-commit-sha", SHA],
                    "DEC-617",
                ),
            )
            for suffix, flags, decision in commands:
                with self.subTest(decision=decision):
                    name = f"{PREFIX}{suffix}.py"
                    out = parent / f"{suffix}.json"
                    command = [
                        sys.executable, str(scripts / name), "assess",
                        *flags, "--out", str(out),
                    ]
                    # Repeated output must not rewrite even metadata on the same inode.
                    for attempt in range(2):
                        completed = subprocess.run(
                            command, cwd=checkout, env=env, text=True,
                            capture_output=True, timeout=40, check=False,
                        )
                        self.assertEqual(completed.returncode, 0, completed.stderr)
                        report = json.loads(out.read_text(encoding="utf-8"))
                        self.assertEqual(report["decision"], decision)
                        self.assertIs(report["dispatch_blocked"], True)
                        self.assertIs(report["trading_authorized"], False)
                        if attempt == 0:
                            # A checkout hard link shares the external report inode.
                            # Content inventories alone miss timestamp-only rewrites.
                            linked = checkout / f"linked-{suffix}.json"
                            os.link(out, linked)
                            old_ns = 1_600_000_000_000_000_000
                            os.utime(out, ns=(old_ns, old_ns))
                            expected_mtime_ns = out.stat().st_mtime_ns
                            baseline = _file_hashes(checkout)
                        else:
                            self.assertEqual(out.stat().st_mtime_ns, expected_mtime_ns)
                            self.assertEqual(linked.stat().st_mtime_ns, expected_mtime_ns)
                        self.assertEqual(_file_hashes(checkout), baseline)
                        self.assertEqual(list(checkout.rglob("*.pyc")), [])

    def test_resolved_external_output_is_not_rejected_as_checkout_local(self):
        with tempfile.TemporaryDirectory(prefix="dec628-outside-") as tmp:
            checkout = Path(tmp) / "checkout"
            checkout.mkdir()
            outside = Path(tmp) / "result.json"
            self.assertFalse(outside.resolve().is_relative_to(checkout.resolve()))
            self.assertTrue((checkout / "result.json").resolve().is_relative_to(checkout.resolve()))


if __name__ == "__main__":
    unittest.main()
