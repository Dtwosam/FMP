from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp044-model-training.yml"
)
SCRIPT = ROOT / "scripts/phase8a_exp044_model_run.py"


class Exp044ModelWorkflowSourceTests(unittest.TestCase):
    def test_workflow_is_manual_main_only_and_has_no_user_inputs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("inputs:", text)
        self.assertNotIn("push:", text)
        self.assertIn(
            'test "$GITHUB_REF" = "refs/heads/main"',
            text,
        )
        self.assertIn(
            'test "$GITHUB_EVENT_NAME" = "workflow_dispatch"',
            text,
        )

    def test_workflow_enforces_first_manual_main_run_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        guard = text.index("Reject any prior manual main model run")
        authorization = text.index(
            "Require separately authorized result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/phase8a-exp044-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-044 model run exists",
            text,
        )

    def test_authorization_preflight_blocks_every_result_job(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        authorization = text.index("authorization-preflight:")
        cells = text.index("model-cells:")
        aggregate = text.index("aggregate-model-evidence:")
        self.assertLess(authorization, cells)
        self.assertLess(cells, aggregate)
        self.assertIn(
            "needs: authorization-preflight",
            text[cells:aggregate],
        )
        self.assertIn(
            "needs: model-cells",
            text[aggregate:],
        )

        first_require = text.index(
            "Require separately authorized result execution"
        )
        first_download = text.index(
            "Download exact frozen feature, outcome, and readiness artifacts"
        )
        self.assertLess(first_require, first_download)

    def test_workflow_pins_exact_model_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(text.count('python-version: "3.12.14"'), 3)
        self.assertEqual(
            text.count(
                "python -m pip install -r "
                "requirements/exp044-model-run.txt -e ."
            ),
            3,
        )
        requirements = (
            ROOT / "requirements/exp044-model-run.txt"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            requirements,
            "numpy==2.5.3\n"
            "scipy==1.18.1\n"
            "scikit-learn==1.9.1\n"
            "joblib==1.6.0\n"
            "threadpoolctl==3.7.0\n"
            "cloudpickle==3.1.2\n"
            "narwhals==2.26.0\n"
            "polars==1.44.2\n"
            "polars-runtime-32==1.44.2\n",
        )

    def test_workflow_freezes_exact_nine_cell_artifact_inventory(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for artifact_id in (
            "10752009633",
            "10753305695",
            "10753555531",
            "10753690116",
            "10753680126",
            "10753440747",
            "10752846673",
            "10753781465",
            "10752752044",
            "10759485253",
            "10759375276",
            "10759490258",
            "10759375400",
            "10759695313",
            "10759645383",
            "10757827671",
            "10757812657",
            "10757692733",
            "10757578276",
        ):
            with self.subTest(artifact_id=artifact_id):
                self.assertIn(artifact_id, text)

        self.assertEqual(
            text.count("feature_artifact_id:"),
            9,
        )
        self.assertEqual(
            text.count("outcome_artifact_id:"),
            9,
        )
        self.assertEqual(
            text.count("feature_zip_sha256:"),
            9,
        )
        self.assertEqual(
            text.count("outcome_zip_sha256:"),
            9,
        )

    def test_workflow_runs_only_frozen_60m_and_240m_cells(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn(
            '--horizon-minutes "$horizon"',
            text,
        )
        self.assertEqual(
            text.count("          - symbol:"),
            9,
        )

    def test_workflow_does_not_regenerate_market_data(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for forbidden in (
            "phase8a_market_feature_pair.py",
            "phase8a_market_outcome_pair.py",
            "fmp.data",
            "Dukascopy",
            "supabase",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_cli_has_no_bypass_around_execution_gate(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_model_execution("
        )
        readiness_load = text.index(
            "load_training_readiness(args.readiness)"
        )
        model_run = text.index("run_model_cell_core(")
        aggregate = text.index("compile_model_result_evidence(")
        self.assertLess(require_call, readiness_load)
        self.assertLess(require_call, model_run)
        self.assertLess(require_call, aggregate)
        self.assertIn(
            'raise SystemExit(str(exc)) from exc',
            text,
        )


if __name__ == "__main__":
    unittest.main()
