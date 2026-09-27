from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import unittest

from fmp.discovery.execution_gate import (
    EXP061_WORKFLOW_SOURCE_FROZEN,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    HISTORICAL_SOURCE_OPEN_AUTHORIZED,
    WORKFLOW_DISPATCH_AUTHORIZED,
    build_exp061_workflow_source_gate,
    require_exp061_historical_execution,
    validate_exp061_workflow_sources,
)
from fmp.discovery.run_contract import EXPECTED_CELLS, expected_job_names


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-exp061-discovery.yml"


EXPECTED_ARTIFACTS = {
    ("EURUSD", "5m"): (
        "10752009633",
        "a466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2",
        "10759485253",
        "243824ecfb365a94dbe49442352440ffc3730240b4ca9758b0b94d8e6224534b",
    ),
    ("EURUSD", "15m"): (
        "10753305695",
        "a942b0bf97995cd67e94335435ab3c06ee0da7688f5ac494b79470c1c637b4ee",
        "10759375276",
        "dca7f656c08e7b35c51e3549cdcaf92849b2905d70cbeecc5ff1ed3773eeedd0",
    ),
    ("EURUSD", "1h"): (
        "10753555531",
        "831a1957519714933cc34c12fe126a88aeaf7fa9a359be6399b8569a236ee59e",
        "10759490258",
        "4594975177b8f7b0ff2979ddba85b774d55b65afe3da61491226dc0bb6f1eaf4",
    ),
    ("GBPUSD", "5m"): (
        "10753690116",
        "62bb96d9492fa092cd5aa157223be34dab6c78fb20e381a4d7804adbcec22498",
        "10759375400",
        "69b5a774707fe1bf26e271ad6a89084f22169a9155dc5debcbf5d00c00a2fdf4",
    ),
    ("GBPUSD", "15m"): (
        "10753680126",
        "c5d894f595e85f84670ac66348b0fb40366a80286408c8c1b777549a5dffdc84",
        "10759695313",
        "a04e9a5ffa5faaf8200385fe7a71bf1d9a56aba3021d60bae25c247b537c365f",
    ),
    ("GBPUSD", "1h"): (
        "10753440747",
        "f7c66064a0255585ecf5e4eca6da86bbea3eee58d38bbf9aaeecd04748a8f6f8",
        "10759645383",
        "b2a192ceca9031dc2460194db698318a04b99df9f346b4c32c8e9ba7803d4f49",
    ),
    ("USDJPY", "5m"): (
        "10752846673",
        "d719b40919b1edf1f868352c19579f30528232387df3862c7f85782d8a2a7360",
        "10757827671",
        "42794311c61189b95a130efafab50cc2c9586d00761e053727f7a05ecd66e36f",
    ),
    ("USDJPY", "15m"): (
        "10753781465",
        "5fdec186a2e086e725623682fd8143294d941635a780038070904e15ed2a4a92",
        "10757812657",
        "edc30a8f49b072e6504a82ae0d90d30a1a362b4dd825bf48d0ed1d2b567af2be",
    ),
    ("USDJPY", "1h"): (
        "10752752044",
        "bc8936d2a02bfc6cde9d11eae23330bfc047374f03fe265ed15eaa6d4d0bd3b4",
        "10757692733",
        "aa7fda1ca6e43c3b41a2ee1fb3729de61bb7dc6ea55e98fda70e8434770a8ee4",
    ),
}


class Exp061WorkflowSourceTests(unittest.TestCase):
    def test_source_gate_validates_exact_repository_blobs_and_stays_locked(self) -> None:
        source = validate_exp061_workflow_sources(repository_root=ROOT)
        self.assertTrue(EXP061_WORKFLOW_SOURCE_FROZEN)
        self.assertTrue(source["workflow_source_frozen"])
        self.assertFalse(WORKFLOW_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_SOURCE_OPEN_AUTHORIZED)
        self.assertFalse(HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED)
        self.assertFalse(source["workflow_dispatch_authorized"])
        self.assertFalse(source["historical_source_open_authorized"])
        self.assertFalse(source["historical_discovery_execution_authorized"])
        self.assertEqual(source["authorized_python_version"], "3.12.14")

    def test_execution_gate_fails_before_historical_access(self) -> None:
        with self.assertRaisesRegex(PermissionError, "authorization is locked"):
            require_exp061_historical_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )
        status = build_exp061_workflow_source_gate(repository_root=ROOT)
        self.assertEqual(
            status["stage"],
            "EXP061_WORKFLOW_SOURCE_FROZEN_EXECUTION_LOCKED",
        )
        for field in (
            "workflow_dispatch_authorized",
            "historical_source_open_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
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
            self.assertFalse(status[field], field)

    def test_cli_preflight_fails_before_reading_missing_historical_inputs(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/phase8a_exp061_discovery.py",
                "preflight",
                "--feature-evidence",
                "/definitely/missing/feature-evidence.json",
                "--outcome-evidence",
                "/definitely/missing/outcome-evidence.json",
                "--code-commit",
                "a" * 40,
                "--out",
                "/tmp/should-not-exist-exp061.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "DEC-275 EXP-061 historical discovery execution authorization is locked",
            result.stderr + result.stdout,
        )
        self.assertNotIn("No such file", result.stderr + result.stdout)

    def test_workflow_yaml_parses_and_reserves_exact_job_shape(self) -> None:
        result = subprocess.run(
            ["ruby", "scripts/validate_workflow_yaml.rb", str(WORKFLOW)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-exp061-discovery", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("name: exp061-preflight", text)
        self.assertIn(
            "name: exp061-cell-${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-${{ matrix.dataset.horizon }}m",
            text,
        )
        self.assertIn("name: exp061-aggregate", text)
        self.assertEqual(len(expected_job_names()), 20)

        rows = re.findall(
            r"- \{ symbol: (EURUSD|GBPUSD|USDJPY), timeframe: (5m|15m|1h), "
            r"horizon: (60|240), feature_artifact_id: \"(\d+)\", "
            r"feature_zip_sha256: ([0-9a-f]{64}), outcome_artifact_id: \"(\d+)\", "
            r"outcome_zip_sha256: ([0-9a-f]{64}) \}",
            text,
        )
        self.assertEqual(len(rows), 18)
        identities = {(s, tf, int(h)) for s, tf, h, *_ in rows}
        self.assertEqual(identities, set(EXPECTED_CELLS))

        for symbol, timeframe, _horizon, feature_id, feature_sha, outcome_id, outcome_sha in rows:
            self.assertEqual(
                (feature_id, feature_sha, outcome_id, outcome_sha),
                EXPECTED_ARTIFACTS[(symbol, timeframe)],
            )

    def test_exact_aggregate_evidence_artifacts_are_frozen(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('FEATURE_EVIDENCE_ARTIFACT_ID: "10753455784"', text)
        self.assertIn(
            "FEATURE_EVIDENCE_ZIP_SHA256: "
            "1d3763c3d8ef13ba5157786c019349f1a7fdb22d626800fbc5b41ad779448f04",
            text,
        )
        self.assertIn('OUTCOME_EVIDENCE_ARTIFACT_ID: "10758027876"', text)
        self.assertIn(
            "OUTCOME_EVIDENCE_ZIP_SHA256: "
            "3c360629c8a408e6b0f97ee9c1254ca936c0144964fd1bb74855f394230a4d05",
            text,
        )

    def test_each_job_requires_execution_before_any_artifact_access(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        preflight = text[text.index("  preflight:"):text.index("  cells:")]
        cells = text[text.index("  cells:"):text.index("  aggregate:")]
        aggregate = text[text.index("  aggregate:"):]

        self.assertLess(
            preflight.index("require-execution"),
            preflight.index("actions/artifacts/$artifact_id/zip"),
        )
        self.assertLess(
            cells.index("require-execution"),
            cells.index("actions/download-artifact@v6"),
        )
        self.assertLess(
            cells.index("require-execution"),
            cells.index("actions/artifacts/$artifact_id/zip"),
        )
        self.assertLess(
            aggregate.index("require-execution"),
            aggregate.index("actions/download-artifact@v6"),
        )

    def test_workflow_contains_no_dispatch_retry_or_trading_action(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8").lower()
        for forbidden in (
            "gh workflow run",
            "workflow-rerun",
            "rerun-failed-jobs",
            "broker_order",
            "place_order",
            "live_order",
            "real_money",
            "mt5",
            "oanda",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
