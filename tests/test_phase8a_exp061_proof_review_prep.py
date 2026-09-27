from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.proof_executor import proof_execution_evidence
from fmp.discovery.proof_operator import build_proof_plan
from fmp.discovery.proof_review import validate_proof_executor_evidence


HEAD = "a" * 40


class Exp061ProofReviewPrepTests(unittest.TestCase):
    def _executor_evidence(self) -> dict[str, object]:
        plan = build_proof_plan(
            main_branch={"name": "main", "commit": {"sha": HEAD}},
            workflow_runs={"workflow_runs": []},
            expected_head_sha=HEAD,
        )
        return proof_execution_evidence(
            plan=plan,
            executor_head_sha=HEAD,
        )

    def test_executor_evidence_validates_for_read_only_review(self) -> None:
        evidence = self._executor_evidence()
        self.assertIs(
            validate_proof_executor_evidence(
                evidence,
                expected_head_sha=HEAD,
            ),
            evidence,
        )

    def test_executor_evidence_rejects_historical_slot_consumption(self) -> None:
        evidence = self._executor_evidence()
        evidence["historical_result_slot_consumed"] = True
        with self.assertRaisesRegex(ValueError, "cannot consume historical slot"):
            validate_proof_executor_evidence(
                evidence,
                expected_head_sha=HEAD,
            )

    def test_review_cli_has_no_github_write_surface(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "scripts/phase8a_exp061_proof_review.py").read_text()
        self.assertNotIn("gh ", text)
        self.assertNotIn("subprocess", text)
        self.assertNotIn("workflow run", text)
        self.assertNotIn("actions: write", text)


if __name__ == "__main__":
    unittest.main()
