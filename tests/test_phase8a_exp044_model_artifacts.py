from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import polars as pl

from fmp.features.schema import FEATURE_COLUMNS, FEATURE_VALUE_COLUMNS
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL,
    MARKET_FEATURE_SET_VERSION,
)
from fmp.market_learning.model_artifacts import (
    AUTHORITATIVE_FEATURE_ARTIFACTS,
    AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED,
    AUTHORITATIVE_OUTCOME_ARTIFACTS,
    AUTHORITATIVE_PROTOCOL_FINGERPRINT,
    AUTHORITATIVE_READINESS_FINGERPRINT,
    MODEL_ARTIFACT_RUNNER_DECISION,
    MODEL_ARTIFACT_RUNNER_VERSION,
    compile_model_result_evidence,
    load_verified_feature_cell,
    load_verified_outcome_cell,
    run_authoritative_model_bundle,
    validate_authoritative_readiness,
)
from fmp.market_learning.model_protocol import (
    MODEL_CELLS,
    MODEL_PROTOCOL_DECISION,
    MODEL_PROTOCOL_VERSION,
)
from fmp.market_learning.model_training import (
    MODEL_TRAINING_CORE_DECISION,
    MODEL_TRAINING_CORE_VERSION,
    MODEL_TRAINING_REPAIR_DECISION,
    MODEL_TRAINING_REPAIR_VERSION,
)
from fmp.market_learning.outcomes import (
    MARKET_OUTCOME_SET_VERSION,
    OUTCOME_COLUMNS,
)


UTC = timezone.utc
FEATURE_COMMIT = "a" * 40
OUTCOME_COMMIT = "b" * 40
PROCESSED = "c" * 64


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _schema_sha256(frame: pl.DataFrame) -> str:
    return _sha256(
        _canonical_json(
            [(name, str(dtype)) for name, dtype in frame.schema.items()]
        )
    )


def _write_partition(
    root: Path,
    relative: str,
    frame: pl.DataFrame,
) -> dict[str, object]:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(
        path,
        compression="zstd",
        compression_level=3,
        statistics=True,
    )
    raw = path.read_bytes()
    return {
        "path": relative,
        "sha256": _sha256(raw),
        "size_bytes": len(raw),
        "row_count": frame.height,
    }


def _write_manifest(
    root: Path,
    manifest: dict[str, object],
) -> str:
    payload = (
        json.dumps(
            manifest,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    (root / "manifest.json").write_bytes(payload)
    return _sha256(payload)


def _fixture_roots(root: Path) -> tuple[Path, Path, str, str]:
    feature_root = root / "feature"
    outcome_root = root / "outcome"
    feature_root.mkdir()
    outcome_root.mkdir()

    base = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
    feature_rows: list[dict[str, object]] = []
    for index in range(3):
        bar_start = base + timedelta(minutes=5 * index)
        available = bar_start + timedelta(minutes=5)
        row: dict[str, object] = {
            "symbol": "EURUSD",
            "timeframe": "5m",
            "bar_start_utc": bar_start,
            "bar_end_utc": available,
            "available_at_utc": available,
            "feature_set_version": MARKET_FEATURE_SET_VERSION,
            "processed_manifest_sha256": PROCESSED,
        }
        for feature_index, name in enumerate(FEATURE_VALUE_COLUMNS):
            row[name] = float(index + feature_index / 1000.0)
        feature_rows.append(row)

    features = pl.DataFrame(feature_rows).select(list(FEATURE_COLUMNS))
    feature_artifact = _write_partition(
        feature_root,
        "data/features/fmp-market-feature-v1/EURUSD/5m/2020/01.parquet",
        features,
    )
    feature_manifest = {
        "manifest_version": 1,
        "experiment_id": "EXP-20260923-044",
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "base_feature_definition_version": "fmp-feature-v1",
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "model_training_authorized": False,
        "promotion_authorized": False,
        "code_commit": FEATURE_COMMIT,
        "processed_manifest_sha256": PROCESSED,
        "symbol": "EURUSD",
        "timeframe": "5m",
        "opened_source_months": ["2020-01"],
        "row_count": features.height,
        "unique_key_count": features.height,
        "schema_columns": list(FEATURE_COLUMNS),
        "schema_sha256": _schema_sha256(features),
        "artifacts": [feature_artifact],
    }
    feature_manifest_sha = _write_manifest(
        feature_root,
        feature_manifest,
    )

    outcome_rows: list[dict[str, object]] = []
    for feature in feature_rows:
        for horizon in (60, 240):
            available = feature["available_at_utc"]
            assert isinstance(available, datetime)
            outcome_rows.append(
                {
                    "symbol": "EURUSD",
                    "timeframe": "5m",
                    "bar_start_utc": feature["bar_start_utc"],
                    "available_at_utc": available,
                    "exit_timestamp_utc": available
                    + timedelta(minutes=horizon),
                    "horizon_minutes": horizon,
                    "future_mid_move_pips": 4.0,
                    "long_net_pips_0p2": 3.0,
                    "short_net_pips_0p2": -5.0,
                    "best_direction_0p2": "LONG",
                    "long_net_pips_0p5": 2.4,
                    "short_net_pips_0p5": -5.6,
                    "best_direction_0p5": "LONG",
                    "long_net_pips_1p0": 1.4,
                    "short_net_pips_1p0": -6.6,
                    "best_direction_1p0": "LONG",
                    "feature_set_version": MARKET_FEATURE_SET_VERSION,
                    "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
                    "evidence_label": EVIDENCE_LABEL,
                    "processed_manifest_sha256": PROCESSED,
                }
            )
    outcomes = pl.DataFrame(outcome_rows).select(list(OUTCOME_COLUMNS))
    outcome_artifact = _write_partition(
        outcome_root,
        "data/outcomes/fmp-market-outcome-grid-v1/EURUSD/5m/2020/01.parquet",
        outcomes,
    )
    outcome_manifest = {
        "manifest_version": 1,
        "experiment_id": "EXP-20260923-044",
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "code_commit": OUTCOME_COMMIT,
        "feature_manifest_sha256": feature_manifest_sha,
        "feature_evidence_fingerprint": "d" * 64,
        "processed_manifest_sha256": PROCESSED,
        "symbol": "EURUSD",
        "timeframe": "5m",
        "horizons_minutes": [60, 240],
        "slippage_pips_per_fill": [0.2, 0.5, 1.0],
        "source_feature_rows": features.height,
        "labeled_rows": outcomes.height,
        "schema_columns": list(OUTCOME_COLUMNS),
        "schema_sha256": _schema_sha256(outcomes),
        "artifacts": [outcome_artifact],
    }
    outcome_manifest_sha = _write_manifest(
        outcome_root,
        outcome_manifest,
    )
    return (
        feature_root,
        outcome_root,
        feature_manifest_sha,
        outcome_manifest_sha,
    )


def _authoritative_readiness() -> dict[str, object]:
    cells = [
        ("EURUSD", "15m", "9af3c7987b4ab8e76e2e07c477195f2b1930e5707dc5401053fa879e5fcf67f6", "662fd1c39c3254bc9b1a856954635475146685d93ac9a36b82d62f78617249ef", "fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a", 407999, 815978),
        ("EURUSD", "1h", "430c4b53c2d4d7e60147d35490125de587e8c48c224dc32f2ee16ea8e4a4678d", "64f7c2e8c8999db57aac4ba40a9ea7a8daa09628169dbdc59e297053368962bb", "fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a", 101999, 203993),
        ("EURUSD", "5m", "a41b21e466cf352b462ec28ad2279343099f1e49d6b7082aafaa9a048414bd02", "e34b4266986076e6b92ad6f557d22391decc82e3abf602c77f6114916f79c09c", "fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a", 1223999, 2447938),
        ("GBPUSD", "15m", "f9f2139bab42d9b5f6e949ae63cb39294d76a6380e17f40cd3823ba04da0f4c3", "258601400d56b5fb7e714917fe6201fa81cd81c776b5a3da30a6cd22acd8fc4d", "a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94", 407999, 815978),
        ("GBPUSD", "1h", "c98bdf4377dba14056a8b8699e565baa0db7cdf64411f27df0a893569e029ac3", "37a19430b3681b8703629d6cfea66e7c6631a57f6d72545eaa18b22b90145da5", "a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94", 101999, 203993),
        ("GBPUSD", "5m", "c428b2b9890db5c6cc2e8dcf3ff3d2bc093b5186de123fa07ac88c23544e340b", "fa22ce486a455be8b109870002dc8fd4da708b58f46a7ed32abaef88d0b79dcf", "a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94", 1223999, 2447938),
        ("USDJPY", "15m", "4ddadc9ed61db9a06f202205fac118b5b1ad41fbc4e3f97b1e7640cfae916359", "cd79d03eb3c5b070c7efe1c3c71270ab8c978adbda83e957a5015cde189bb9ad", "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d", 407999, 815978),
        ("USDJPY", "1h", "79619e9a582bc86e074a6d91016a17e6693a5daaadf7fe5a86226fed82824fb5", "56e3f3bb0b86ed238c610e7132aa9fad92e39c76c4c0e7513779f3c74eaa29df", "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d", 101999, 203993),
        ("USDJPY", "5m", "28fcbb63deb5ef27ae95313c04595c9b18df47f4180958a91cc0a4f5b557a44f", "ee62d53bb94d08845752196cb19ad942d7affced59b14fce88c0676f76ed783c", "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d", 1223999, 2447938),
    ]
    value: dict[str, object] = {
        "broker_mutation_authorized": False,
        "cells": [
            {
                "feature_manifest_sha256": feature_sha,
                "feature_row_count": feature_rows,
                "labeled_outcome_rows": outcome_rows,
                "outcome_manifest_sha256": outcome_sha,
                "processed_manifest_sha256": processed_sha,
                "symbol": symbol,
                "timeframe": timeframe,
            }
            for (
                symbol,
                timeframe,
                feature_sha,
                outcome_sha,
                processed_sha,
                feature_rows,
                outcome_rows,
            ) in cells
        ],
        "data_preparation_complete": True,
        "demo_order_authorized": False,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "experiment_id": "EXP-20260923-044",
        "feature_code_commit": "b71912e254d2a597c0ef55b5e1b3b87b052039ea",
        "feature_evidence_fingerprint": "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815",
        "feature_set_version": "fmp-market-feature-v1",
        "live_order_authorized": False,
        "model_fit_authorized": False,
        "model_protocol_result_authorized": False,
        "model_protocol_source_open_authorized": True,
        "outcome_code_commit": "edeb43bb4de88923e3349caa8ace36350839ccb8",
        "outcome_evidence_fingerprint": "b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117",
        "outcome_set_version": "fmp-market-outcome-grid-v1",
        "promotion_authorized": False,
        "readiness_version": "fmp-market-learning-readiness-v1",
        "real_money_authorized": False,
        "shadow_authorized": False,
        "verified_cell_count": 9,
    }
    value["readiness_fingerprint"] = _sha256(_canonical_json(value))
    assert value["readiness_fingerprint"] == AUTHORITATIVE_READINESS_FINGERPRINT
    return value


def _fake_cell_results() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for cell in MODEL_CELLS:
        identity = f"{cell.symbol}|{cell.timeframe}|{cell.horizon_minutes}"
        rows.append(
            {
                "training_core_version": MODEL_TRAINING_CORE_VERSION,
                "training_core_decision": MODEL_TRAINING_CORE_DECISION,
                "training_repair_version": MODEL_TRAINING_REPAIR_VERSION,
                "training_repair_decision": MODEL_TRAINING_REPAIR_DECISION,
                "protocol_decision": MODEL_PROTOCOL_DECISION,
                "protocol_version": MODEL_PROTOCOL_VERSION,
                "protocol_fingerprint": AUTHORITATIVE_PROTOCOL_FINGERPRINT,
                "evidence_label": EVIDENCE_LABEL,
                "untouched_oos": False,
                "cell": {
                    "symbol": cell.symbol,
                    "timeframe": cell.timeframe,
                    "horizon_minutes": cell.horizon_minutes,
                },
                "selection": {"status": "NO_MODEL_CHALLENGER"},
                "validation": {"status": "LOCKED_NO_SELECTION"},
                "retrospective_holdout": {
                    "status": "LOCKED_NO_SELECTION"
                },
                "result_fingerprint": _sha256(identity.encode("utf-8")),
                "promotion_authorized": False,
                "shadow_authorized": False,
                "demo_order_authorized": False,
                "broker_mutation_authorized": False,
                "live_order_authorized": False,
                "real_money_authorized": False,
            }
        )
    return rows


class Exp044ModelArtifactRunnerTests(unittest.TestCase):
    def test_authoritative_inventory_and_execution_lock_are_frozen(self) -> None:
        self.assertEqual(len(AUTHORITATIVE_FEATURE_ARTIFACTS), 9)
        self.assertEqual(len(AUTHORITATIVE_OUTCOME_ARTIFACTS), 9)
        self.assertEqual(
            set(AUTHORITATIVE_FEATURE_ARTIFACTS),
            set(AUTHORITATIVE_OUTCOME_ARTIFACTS),
        )
        self.assertIs(
            AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED,
            False,
        )
        with self.assertRaisesRegex(
            PermissionError,
            "non-executable",
        ):
            run_authoritative_model_bundle(
                readiness={},
                feature_roots={},
                outcome_roots={},
                code_commit="e" * 40,
            )

    def test_readiness_content_is_cryptographically_revalidated(self) -> None:
        readiness = _authoritative_readiness()
        indexed = validate_authoritative_readiness(readiness)
        self.assertEqual(len(indexed), 9)

        tampered = json.loads(json.dumps(readiness))
        tampered["cells"][0]["feature_row_count"] += 1
        with self.assertRaisesRegex(
            ValueError,
            "content fingerprint mismatch",
        ):
            validate_authoritative_readiness(tampered)

    def test_low_level_loaders_verify_manifest_and_partition_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (
                feature_root,
                outcome_root,
                feature_manifest_sha,
                outcome_manifest_sha,
            ) = _fixture_roots(Path(tmp))

            features, _ = load_verified_feature_cell(
                root=feature_root,
                symbol="EURUSD",
                timeframe="5m",
                expected_manifest_sha256=feature_manifest_sha,
                expected_processed_manifest_sha256=PROCESSED,
                expected_row_count=3,
                expected_code_commit=FEATURE_COMMIT,
                expected_artifact_count=1,
            )
            outcomes, _ = load_verified_outcome_cell(
                root=outcome_root,
                symbol="EURUSD",
                timeframe="5m",
                expected_manifest_sha256=outcome_manifest_sha,
                expected_feature_manifest_sha256=feature_manifest_sha,
                expected_feature_evidence_fingerprint="d" * 64,
                expected_processed_manifest_sha256=PROCESSED,
                expected_source_feature_rows=3,
                expected_labeled_rows=6,
                expected_code_commit=OUTCOME_COMMIT,
                expected_artifact_count=1,
            )
            self.assertEqual(features.height, 3)
            self.assertEqual(outcomes.height, 6)

            partition = next(
                feature_root.rglob("*.parquet")
            )
            raw = bytearray(partition.read_bytes())
            raw[-1] ^= 1
            partition.write_bytes(bytes(raw))
            with self.assertRaisesRegex(
                ValueError,
                "partition sha256 mismatch",
            ):
                load_verified_feature_cell(
                    root=feature_root,
                    symbol="EURUSD",
                    timeframe="5m",
                    expected_manifest_sha256=feature_manifest_sha,
                    expected_processed_manifest_sha256=PROCESSED,
                    expected_row_count=3,
                    expected_code_commit=FEATURE_COMMIT,
                    expected_artifact_count=1,
                )

    def test_aggregate_model_result_evidence_is_complete_and_deterministic(self) -> None:
        first = compile_model_result_evidence(
            _fake_cell_results(),
            code_commit="f" * 40,
        )
        second = compile_model_result_evidence(
            tuple(reversed(_fake_cell_results())),
            code_commit="f" * 40,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["runner_version"],
            MODEL_ARTIFACT_RUNNER_VERSION,
        )
        self.assertEqual(
            first["runner_decision"],
            MODEL_ARTIFACT_RUNNER_DECISION,
        )
        self.assertEqual(first["verified_cell_count"], 18)
        self.assertEqual(len(first["cells"]), 18)
        self.assertEqual(len(first["evidence_fingerprint"]), 64)
        self.assertIs(first["model_fit_authorized"], False)
        self.assertIs(first["promotion_authorized"], False)
        self.assertIs(first["real_money_authorized"], False)

    def test_incomplete_aggregate_evidence_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "incomplete"):
            compile_model_result_evidence(
                _fake_cell_results()[:-1],
                code_commit="f" * 40,
            )


if __name__ == "__main__":
    unittest.main()
