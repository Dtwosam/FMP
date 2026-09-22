from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.portfolio.challenger_discovery import build_exp015_challengers
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.portfolio.registry import (
    freeze_shadow_champion_set,
    transition_strategy,
)
from fmp.portfolio.contracts import StrategyLifecycle, StrategyRecord
from fmp.phase8b.design import (
    BRIDGE_FILE_BY_SYMBOL,
    PHASE8B_DESIGN_FROZEN,
    PHASE8B_DESIGN_PROTOCOL,
    build_phase8b_design,
    validate_phase8b_design,
    write_phase8b_design_artifacts,
)


ACCEPTANCE_COMMIT = "a" * 40
DESIGN_COMMIT = "b" * 40
ACCEPTANCE_EVIDENCE_ID = (
    "EXP-20260922-016:PHASE8A_ACCEPT_SHADOW_CANDIDATE"
)


def _accepted_artifact() -> dict[str, object]:
    baseline = next(
        item
        for item in build_phase4_baseline_inventory()
        if item.lifecycle is StrategyLifecycle.HISTORICAL_QUALIFIED
    )
    challenger_source = next(
        item
        for item in build_exp015_challengers(code_commit="c" * 40)
        if item.strategy.symbol != baseline.strategy.symbol
        and item.strategy.family != baseline.strategy.family
    )
    challenger = StrategyRecord(
        strategy=challenger_source.strategy,
        lifecycle=StrategyLifecycle.HISTORICAL_QUALIFIED,
        evidence_id="EXP-20260922-015:FINAL_SHORTLIST",
    )
    before = (baseline, challenger)
    transitioned = tuple(
        transition_strategy(
            item,
            StrategyLifecycle.SHADOW_CANDIDATE,
            evidence_id=ACCEPTANCE_EVIDENCE_ID,
        )
        for item in before
    )
    champion = freeze_shadow_champion_set(
        transitioned,
        champion_set_id="phase8a-exp016-test",
    )
    before_by_fp = {
        item.strategy.fingerprint: item
        for item in before
    }
    rows = []
    for item in transitioned:
        prior = before_by_fp[item.strategy.fingerprint]
        rows.append(
            {
                "fingerprint": item.strategy.fingerprint,
                "identity_json": item.strategy.identity_json,
                "family": item.strategy.family,
                "symbol": item.strategy.symbol,
                "timeframe": item.strategy.timeframe,
                "parameters_json": item.strategy.parameters_json,
                "code_commit": item.strategy.code_commit,
                "prior_lifecycle": prior.lifecycle.value,
                "prior_evidence_id": prior.evidence_id,
                "lifecycle": item.lifecycle.value,
                "evidence_id": item.evidence_id,
            }
        )
    return {
        "protocol": "fmp-phase8a-acceptance-v1",
        "experiment_id": "EXP-20260922-016",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
        "dec042_preflight_sha256": "1" * 64,
        "dec042_selection_sha256": "2" * 64,
        "dec042_runner_code_commit": "d" * 40,
        "acceptance_code_commit": ACCEPTANCE_COMMIT,
        "baseline_strategy_fingerprint": baseline.strategy.fingerprint,
        "baseline_control_02": {},
        "baseline_control_05": {},
        "outcome": "PHASE8A_SHADOW_CANDIDATE_ACCEPTED",
        "rejection_reason": None,
        "shadow_candidate_authorized": True,
        "phase8b_design_authorized": True,
        "selected_strategy_fingerprints": [
            item.strategy.fingerprint
            for item in transitioned
        ],
        "economic_improvement_gate_passed": True,
        "shadow_candidate": {
            "champion_set_id": champion.champion_set_id,
            "champion_set_experiment_id": champion.experiment_id,
            "champion_set_fingerprint": champion.fingerprint,
            "strategy_fingerprints": [
                item.fingerprint
                for item in champion.strategies
            ],
            "strategies": sorted(
                rows,
                key=lambda item: str(item["fingerprint"]),
            ),
        },
    }


class Phase8BDesignTests(unittest.TestCase):
    def test_design_derives_exact_required_symbols_and_fixed_files(self) -> None:
        acceptance = _accepted_artifact()
        design = build_phase8b_design(
            acceptance=acceptance,
            acceptance_sha256="3" * 64,
            code_commit=DESIGN_COMMIT,
        )
        self.assertEqual(design["protocol"], PHASE8B_DESIGN_PROTOCOL)
        self.assertEqual(design["outcome"], PHASE8B_DESIGN_FROZEN)
        self.assertEqual(design["phase8b_design_code_commit"], DESIGN_COMMIT)
        self.assertGreaterEqual(design["strategy_count"], 2)
        expected_symbols = sorted(
            {
                item["symbol"]
                for item in acceptance["shadow_candidate"]["strategies"]
            }
        )
        self.assertEqual(design["required_symbols"], expected_symbols)
        self.assertEqual(
            design["connector"]["bridge_file_by_symbol"],
            {
                symbol: BRIDGE_FILE_BY_SYMBOL[symbol]
                for symbol in expected_symbols
            },
        )
        self.assertTrue(design["connector"]["one_ea_per_required_symbol"])
        self.assertTrue(design["connector"]["auto_trading_required_off"])
        self.assertFalse(design["connector"]["broker_order_surface_allowed"])
        self.assertFalse(design["campaign_registration_authorized"])
        self.assertFalse(design["campaign_start_authorized"])
        self.assertFalse(design["demo_order_authorized"])
        self.assertFalse(design["live_order_authorized"])
        self.assertFalse(design["real_money_authorized"])
        validate_phase8b_design(design)

    def test_rejected_acceptance_cannot_compile_design(self) -> None:
        acceptance = _accepted_artifact()
        acceptance["outcome"] = "PHASE8A_RESEARCH_REJECTED"
        acceptance["shadow_candidate_authorized"] = False
        acceptance["phase8b_design_authorized"] = False
        acceptance["shadow_candidate"] = None
        with self.assertRaisesRegex(ValueError, "accepted shadow candidate"):
            build_phase8b_design(
                acceptance=acceptance,
                acceptance_sha256="3" * 64,
                code_commit=DESIGN_COMMIT,
            )

    def test_tampered_champion_set_fails_closed(self) -> None:
        acceptance = _accepted_artifact()
        acceptance["shadow_candidate"]["champion_set_fingerprint"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "champion-set fingerprint"):
            build_phase8b_design(
                acceptance=acceptance,
                acceptance_sha256="3" * 64,
                code_commit=DESIGN_COMMIT,
            )

    def test_design_fingerprint_detects_mutation(self) -> None:
        design = build_phase8b_design(
            acceptance=_accepted_artifact(),
            acceptance_sha256="3" * 64,
            code_commit=DESIGN_COMMIT,
        )
        tampered = dict(design)
        tampered["campaign_start_authorized"] = True
        with self.assertRaises(ValueError):
            validate_phase8b_design(tampered)

    def test_design_artifacts_are_deterministic(self) -> None:
        design = build_phase8b_design(
            acceptance=_accepted_artifact(),
            acceptance_sha256="3" * 64,
            code_commit=DESIGN_COMMIT,
        )
        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            left_manifest = write_phase8b_design_artifacts(design, left)
            right_manifest = write_phase8b_design_artifacts(design, right)
            self.assertEqual(
                (left / "design.json").read_bytes(),
                (right / "design.json").read_bytes(),
            )
            self.assertEqual(left_manifest, right_manifest)


if __name__ == "__main__":
    unittest.main()
