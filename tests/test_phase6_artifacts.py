from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

from fmp.models.contracts import (
    EXPERIMENT_ID,
    FEATURE_SET_VERSION,
    PHASE5_CHECKPOINT_SHA,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)


def result_fixture() -> dict[str, object]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "strategy_id": "session_breakout",
        "code_commit": "abc123",
        "selection": {
            "experiment_id": EXPERIMENT_ID,
            "strategy_id": "session_breakout",
            "code_commit": "abc123",
            "feature_set_version": FEATURE_SET_VERSION,
            "phase5_checkpoint_sha": PHASE5_CHECKPOINT_SHA,
            "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
            "fit_split": {"start": "2015-01-01", "end_exclusive": "2019-01-01"},
            "selection_split": {"start": "2019-01-01", "end_exclusive": "2021-01-01"},
            "fit_dataset_digest": "a" * 64,
            "models": {
                "logistic_regression": {"fit_score_digest": "b" * 64},
                "hist_gradient_boosting": {"fit_score_digest": "c" * 64},
            },
            "variants": [],
            "selected_variant": "NO_ML_CHALLENGER",
        },
        "validation": {
            "status": "NO_ML_CHALLENGER",
            "validation_loaded": False,
        },
    }


class Phase6ArtifactTests(unittest.TestCase):
    def test_identical_results_produce_byte_identical_selection_result_and_manifest(self) -> None:
        from fmp.models.artifacts import write_phase6_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first"
            second = Path(tmp) / "second"
            first_manifest = write_phase6_artifacts(result_fixture(), first)
            second_manifest = write_phase6_artifacts(result_fixture(), second)
            for name in ("selection.json", "result.json", "manifest.json"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())

        self.assertEqual(first_manifest, second_manifest)
        records = {row["path"]: row for row in first_manifest["artifacts"]}
        self.assertEqual(set(records), {"selection.json", "result.json"})
        for row in records.values():
            self.assertEqual(len(row["sha256"]), 64)
            self.assertGreater(row["size_bytes"], 0)
        self.assertEqual(
            set(first_manifest["runtime_versions"]),
            {"python", "scikit_learn", "numpy", "scipy", "polars"},
        )

    def test_writer_rejects_wrong_identity_model_nonfinite_and_2024_evidence(self) -> None:
        from fmp.models.artifacts import write_phase6_artifacts

        mutations = []
        wrong_checkpoint = result_fixture()
        wrong_checkpoint["selection"]["phase5_checkpoint_sha"] = "bad"
        mutations.append((wrong_checkpoint, "checkpoint"))

        wrong_processed = result_fixture()
        wrong_processed["selection"]["processed_manifest_sha256"] = "bad"
        mutations.append((wrong_processed, "processed"))

        wrong_feature = result_fixture()
        wrong_feature["selection"]["feature_set_version"] = "bad-feature"
        mutations.append((wrong_feature, "feature"))

        wrong_model = result_fixture()
        wrong_model["selection"]["models"]["neural_network"] = {}
        mutations.append((wrong_model, "model"))

        nonfinite = result_fixture()
        nonfinite["validation"]["diagnostic"] = math.inf
        mutations.append((nonfinite, "finite"))

        final_timestamp = result_fixture()
        final_timestamp["validation"]["opened_at"] = "2024-01-01T00:00:00Z"
        mutations.append((final_timestamp, "2024|final"))

        final_path = result_fixture()
        final_path["validation"]["path"] = "data/features/USDJPY/15m/2024/01.parquet"
        mutations.append((final_path, "2024|final"))

        with tempfile.TemporaryDirectory() as tmp:
            for index, (payload, message) in enumerate(mutations):
                with self.subTest(index=index):
                    with self.assertRaisesRegex((ValueError, TypeError), message):
                        write_phase6_artifacts(payload, Path(tmp) / str(index))

    def test_manifest_json_matches_returned_manifest(self) -> None:
        from fmp.models.artifacts import write_phase6_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase6_artifacts(result_fixture(), root)
            self.assertEqual(json.loads((root / "manifest.json").read_text()), manifest)


if __name__ == "__main__":
    unittest.main()
