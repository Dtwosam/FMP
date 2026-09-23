from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from fmp.market_learning.contracts import EVIDENCE_LABEL
from fmp.market_learning.model_artifacts import (
    compile_model_result_evidence,
)
from fmp.market_learning.model_protocol import (
    MODEL_CELLS,
    MODEL_PROTOCOL_DECISION,
    MODEL_PROTOCOL_VERSION,
)
from fmp.market_learning.model_result_evidence import (
    MODEL_RESULT_VALIDATION_DECISION,
    load_model_result_evidence,
    validate_model_result_evidence,
)
from fmp.market_learning.model_training import (
    MODEL_TRAINING_CORE_DECISION,
    MODEL_TRAINING_CORE_VERSION,
    MODEL_TRAINING_REPAIR_DECISION,
    MODEL_TRAINING_REPAIR_VERSION,
)
from fmp.market_learning.model_artifacts import (
    AUTHORITATIVE_PROTOCOL_FINGERPRINT,
)


COMMIT = "f" * 40


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def _cell_results() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for index, cell in enumerate(MODEL_CELLS):
        if index % 3 == 0:
            selection = {"status": "NO_MODEL_CHALLENGER"}
            validation = {"status": "LOCKED_NO_SELECTION"}
            holdout = {"status": "LOCKED_NO_SELECTION"}
        elif index % 3 == 1:
            selection = {"status": "SELECTED"}
            validation = {"status": "REJECT"}
            holdout = {"status": "LOCKED_VALIDATION_REJECT"}
        else:
            selection = {"status": "SELECTED"}
            validation = {"status": "PASS"}
            holdout = {"status": "PASS"}

        identity = (
            f"{cell.symbol}|{cell.timeframe}|{cell.horizon_minutes}|{index}"
        )
        out.append(
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
                "selection": selection,
                "validation": validation,
                "retrospective_holdout": holdout,
                "result_fingerprint": _sha256(
                    identity.encode("utf-8")
                ),
                "promotion_authorized": False,
                "shadow_authorized": False,
                "demo_order_authorized": False,
                "broker_mutation_authorized": False,
                "live_order_authorized": False,
                "real_money_authorized": False,
            }
        )
    return out


def _evidence() -> dict[str, object]:
    return compile_model_result_evidence(
        _cell_results(),
        code_commit=COMMIT,
    )


def _recompute_fingerprint(value: dict[str, object]) -> None:
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    value["evidence_fingerprint"] = _sha256(
        _canonical_json(unsigned)
    )


class Exp044ModelResultEvidenceTests(unittest.TestCase):
    def test_complete_evidence_revalidates_and_remains_non_promotional(self) -> None:
        summary = validate_model_result_evidence(
            _evidence(),
            expected_code_commit=COMMIT,
        )
        self.assertEqual(
            MODEL_RESULT_VALIDATION_DECISION,
            "DEC-093",
        )
        self.assertTrue(
            summary["model_result_evidence_verified"]
        )
        self.assertEqual(summary["verified_cell_count"], 18)
        self.assertEqual(summary["selected_cell_count"], 12)
        self.assertEqual(summary["validation_pass_count"], 6)
        self.assertEqual(
            summary["retrospective_holdout_pass_count"],
            6,
        )
        self.assertIs(summary["promotion_authorized"], False)
        self.assertIs(summary["shadow_authorized"], False)
        self.assertIs(summary["demo_order_authorized"], False)
        self.assertIs(summary["broker_mutation_authorized"], False)
        self.assertIs(summary["live_order_authorized"], False)
        self.assertIs(summary["real_money_authorized"], False)
        self.assertIs(summary["trading_authorized"], False)

    def test_content_tamper_fails_fingerprint_revalidation(self) -> None:
        evidence = _evidence()
        evidence["verified_cell_count"] = 17
        with self.assertRaisesRegex(
            ValueError,
            "content fingerprint mismatch",
        ):
            validate_model_result_evidence(
                evidence,
                expected_code_commit=COMMIT,
            )

    def test_impossible_status_chain_fails_even_with_valid_fingerprint(self) -> None:
        evidence = _evidence()
        cells = evidence["cells"]
        assert isinstance(cells, list)
        target = next(
            cell
            for cell in cells
            if isinstance(cell, dict)
            and cell.get("selection_status")
            == "NO_MODEL_CHALLENGER"
        )
        target["validation_status"] = "PASS"
        _recompute_fingerprint(evidence)
        with self.assertRaisesRegex(
            ValueError,
            "no-challenger cell must keep validation locked",
        ):
            validate_model_result_evidence(
                evidence,
                expected_code_commit=COMMIT,
            )

    def test_wrong_execution_commit_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "code_commit mismatch",
        ):
            validate_model_result_evidence(
                _evidence(),
                expected_code_commit="e" * 40,
            )

    def test_file_loader_revalidates_before_returning(self) -> None:
        evidence = _evidence()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model-result-evidence.json"
            path.write_text(
                json.dumps(
                    evidence,
                    sort_keys=True,
                    indent=2,
                    allow_nan=False,
                )
                + "\n",
                encoding="utf-8",
            )
            loaded = load_model_result_evidence(
                path,
                expected_code_commit=COMMIT,
            )
            self.assertEqual(
                loaded["evidence_fingerprint"],
                evidence["evidence_fingerprint"],
            )


if __name__ == "__main__":
    unittest.main()
