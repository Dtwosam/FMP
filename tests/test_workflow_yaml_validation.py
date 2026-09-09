from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


class WorkflowYamlValidationTests(unittest.TestCase):
    def test_all_repository_workflows_parse(self) -> None:
        result = subprocess.run(
            ["ruby", "scripts/validate_workflow_yaml.rb", ".github/workflows"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_validator_rejects_malformed_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = root / "bad.yml"
            bad.write_text("name: bad\njobs:\n  broken: [\n", encoding="utf-8")
            result = subprocess.run(
                ["ruby", "scripts/validate_workflow_yaml.rb", str(bad)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
