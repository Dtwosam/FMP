from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-exp062-adapter-proof.yml"


class Exp062AdapterProofWorkflowTests(unittest.TestCase):
    def test_workflow_is_push_main_read_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-exp062-adapter-proof", text)
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_workflow_pins_exact_repair_and_source_boundaries(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/historical_failure_result_decision.py": (
                "676116f34693f9a5a8f8403aaa93f28ac1c5bb46"
            ),
            "src/fmp/discovery/market_learning_adapter.py": (
                "51096a72671fe28ac14044afb0bd8aa125416891"
            ),
            "src/fmp/discovery/range_limited_loader.py": (
                "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
            ),
            "src/fmp/discovery/exp062_adapter_probe.py": (
                "579cf4ee01646e8abb686a9b060b53029527f441"
            ),
            "scripts/phase8a_exp062_adapter_probe.py": (
                "40e0c90c41fd53cb8ce42416af8c7c5f2b60d138"
            ),
            "requirements/exp061-discovery-run.txt": (
                "1ff32214dee10d877a067e750cd69ffad96d5fe5"
            ),
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(blob, text)

    def test_matrix_has_exact_nine_pair_timeframe_probes(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            for timeframe in ("5m", "15m", "1h"):
                with self.subTest(symbol=symbol, timeframe=timeframe):
                    self.assertIn(f"symbol: {symbol}", text)
                    self.assertIn(f"timeframe: {timeframe}", text)
        self.assertEqual(text.count("feature_artifact_id:"), 9)
        self.assertEqual(text.count("outcome_artifact_id:"), 9)

    def test_workflow_runs_adapter_probe_not_pattern_mining(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp062_adapter_probe.py cell",
            text,
        )
        self.assertIn(
            "python scripts/phase8a_exp062_adapter_probe.py aggregate",
            text,
        )
        self.assertNotIn("phase8a_exp061.py cell", text)
        self.assertNotIn("run_in_memory_discovery", text)
        self.assertNotIn("gh workflow run", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_probe_output_survives_cleanup_and_is_uploaded(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        cleanup = (
            "rm -rf .downloads .feature .outcome "
            ".feature-evidence .outcome-evidence"
        )
        self.assertIn(cleanup, text)
        self.assertNotIn(
            "rm -rf .downloads .feature .outcome "
            ".feature-evidence .outcome-evidence .probe",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/probe/probe.json",
            text,
        )
        self.assertIn(
            '--out "$RUNNER_TEMP/probe/probe.json"',
            text,
        )

    def test_aggregate_requires_real_nonfinite_case_and_all_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["cell_count"] == 9', text)
        self.assertIn(
            'assert value["all_nine_real_data_adapter_probes_successful"] is True',
            text,
        )
        self.assertIn(
            'assert value["total_raw_nonfinite_value_count"] > 0',
            text,
        )
        for field in (
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIn(field, text)
        self.assertIn(
            "exp062-dec294-adapter-proof-${{ github.sha }}",
            text,
        )


if __name__ == "__main__":
    unittest.main()
