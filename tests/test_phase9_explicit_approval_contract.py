from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fmp.phase9.approval as approval_module
from fmp.phase9.approval import (
    PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_READY,
    PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_RECORDED,
    approval_statement_for_challenge,
    build_phase9_demo_gate_activation_contract,
    build_phase9_first_demo_explicit_approval,
    validate_phase9_demo_gate_activation_contract,
    validate_phase9_first_demo_explicit_approval,
    write_phase9_demo_gate_activation_contract,
    write_phase9_first_demo_explicit_approval,
)
from fmp.phase9.execution_gate import DEMO_EXECUTION_SOURCE_ARMED


UTC = timezone.utc
APPROVAL_TIME = datetime(2026, 9, 22, 19, 5, tzinfo=UTC)
ACTIVATION_TIME = datetime(2026, 9, 22, 19, 6, tzinfo=UTC)
COMMIT = "c" * 40


def _inputs():
    review = {
        "account_mode": "DEMO",
        "account_fingerprint": "1" * 64,
        "server": "FPMarketsSC-Demo",
        "execution_permit_fingerprint": "2" * 64,
        "request_fingerprint": "3" * 64,
        "client_order_id": "fmp9-dec068-fixture",
        "not_before_utc": "2026-09-22T19:00:00Z",
        "launch_preflight_time_utc": "2026-09-22T19:02:00Z",
        "expires_at_utc": "2026-09-22T20:00:00Z",
    }
    packet = {
        "authorization_packet_fingerprint": "4" * 64,
        "authorization_challenge_fingerprint": "5" * 64,
        "review": review,
        "first_demo_authorization_packet_ready": True,
        "explicit_execution_approval_recorded": False,
    }
    return (
        packet,
        {"design": True},
        {"request": True},
        {"session_arm": True},
        {"session_ready": True},
        {"execution_arm": True},
        {"runtime_authority": True},
        {"launch_preflight": True},
        {"execution_permit": True},
    )


def _build_approval():
    inputs = _inputs()
    packet = inputs[0]
    statement = approval_statement_for_challenge(
        packet["authorization_challenge_fingerprint"]
    )
    with patch(
        "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
    ):
        approval = build_phase9_first_demo_explicit_approval(
            packet=inputs[0],
            design=inputs[1],
            request=inputs[2],
            session_arm=inputs[3],
            session_ready=inputs[4],
            execution_arm=inputs[5],
            runtime_authority=inputs[6],
            launch_preflight=inputs[7],
            execution_permit=inputs[8],
            journal_rows=[],
            operator_identity_reference="operator-fixture-068",
            operator_approval_reference="approval-fixture-068",
            approval_statement=statement,
            approval_time_utc=APPROVAL_TIME,
            code_commit=COMMIT,
        )
    return approval, inputs


class Phase9ExplicitApprovalContractTests(unittest.TestCase):
    def test_approval_statement_must_echo_exact_challenge(self) -> None:
        packet = _inputs()[0]
        challenge = packet["authorization_challenge_fingerprint"]
        self.assertEqual(
            approval_statement_for_challenge(challenge),
            f"APPROVE FIRST DEMO ORDER {challenge}",
        )
        inputs = _inputs()
        with patch(
            "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
        ):
            with self.assertRaisesRegex(ValueError, "statement mismatch"):
                build_phase9_first_demo_explicit_approval(
                    packet=inputs[0],
                    design=inputs[1],
                    request=inputs[2],
                    session_arm=inputs[3],
                    session_ready=inputs[4],
                    execution_arm=inputs[5],
                    runtime_authority=inputs[6],
                    launch_preflight=inputs[7],
                    execution_permit=inputs[8],
                    journal_rows=[],
                    operator_identity_reference="operator-fixture-068",
                    operator_approval_reference="approval-fixture-068",
                    approval_statement="APPROVE SOMETHING ELSE",
                    approval_time_utc=APPROVAL_TIME,
                    code_commit=COMMIT,
                )

    def test_source_only_approval_records_binding_but_authorizes_no_send(self) -> None:
        approval, inputs = _build_approval()
        self.assertEqual(
            approval["outcome"],
            PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_RECORDED,
        )
        self.assertTrue(approval["explicit_execution_approval_recorded"])
        self.assertTrue(approval["source_only_approval_record"])
        self.assertTrue(approval["practice_only"])
        self.assertEqual(approval["max_new_orders"], 1)
        for field in (
            "demo_execution_source_armed",
            "runner_activation_wired",
            "demo_execution_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "phase10_authorized",
            "phase11_authorized",
        ):
            self.assertFalse(approval[field])
        with patch(
            "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
        ):
            validate_phase9_first_demo_explicit_approval(
                approval,
                packet=inputs[0],
                design=inputs[1],
                request=inputs[2],
                session_arm=inputs[3],
                session_ready=inputs[4],
                execution_arm=inputs[5],
                runtime_authority=inputs[6],
                launch_preflight=inputs[7],
                execution_permit=inputs[8],
                journal_rows=[],
            )

    def test_approval_time_must_be_after_launch_and_before_expiry(self) -> None:
        inputs = _inputs()
        statement = approval_statement_for_challenge(
            inputs[0]["authorization_challenge_fingerprint"]
        )
        for bad_time in (
            datetime(2026, 9, 22, 19, 1, tzinfo=UTC),
            datetime(2026, 9, 22, 20, 1, tzinfo=UTC),
        ):
            with patch(
                "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
            ):
                with self.assertRaisesRegex(ValueError, "outside approval window"):
                    build_phase9_first_demo_explicit_approval(
                        packet=inputs[0],
                        design=inputs[1],
                        request=inputs[2],
                        session_arm=inputs[3],
                        session_ready=inputs[4],
                        execution_arm=inputs[5],
                        runtime_authority=inputs[6],
                        launch_preflight=inputs[7],
                        execution_permit=inputs[8],
                        journal_rows=[],
                        operator_identity_reference="operator-fixture-068",
                        operator_approval_reference="approval-fixture-068",
                        approval_statement=statement,
                        approval_time_utc=bad_time,
                        code_commit=COMMIT,
                    )

    def test_gate_activation_contract_is_ready_but_gate_stays_false(self) -> None:
        approval, inputs = _build_approval()
        with patch(
            "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
        ):
            contract = build_phase9_demo_gate_activation_contract(
                approval=approval,
                packet=inputs[0],
                design=inputs[1],
                request=inputs[2],
                session_arm=inputs[3],
                session_ready=inputs[4],
                execution_arm=inputs[5],
                runtime_authority=inputs[6],
                launch_preflight=inputs[7],
                execution_permit=inputs[8],
                journal_rows=[],
                activation_time_utc=ACTIVATION_TIME,
                code_commit=COMMIT,
            )
        self.assertEqual(
            contract["outcome"],
            PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_READY,
        )
        self.assertTrue(contract["explicit_execution_approval_recorded"])
        self.assertTrue(contract["operator_gate_activation_contract_ready"])
        self.assertFalse(contract["demo_execution_source_armed"])
        self.assertFalse(contract["runner_activation_wired"])
        self.assertFalse(contract["broker_mutation_authorized"])
        self.assertIs(DEMO_EXECUTION_SOURCE_ARMED, False)

        with patch(
            "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
        ):
            validate_phase9_demo_gate_activation_contract(
                contract,
                approval=approval,
                packet=inputs[0],
                design=inputs[1],
                request=inputs[2],
                session_arm=inputs[3],
                session_ready=inputs[4],
                execution_arm=inputs[5],
                runtime_authority=inputs[6],
                launch_preflight=inputs[7],
                execution_permit=inputs[8],
                journal_rows=[],
            )

    def test_activation_must_follow_approval_and_remain_inside_window(self) -> None:
        approval, inputs = _build_approval()
        for bad_time, message in (
            (APPROVAL_TIME - timedelta(seconds=1), "precedes approval"),
            (datetime(2026, 9, 22, 20, 1, tzinfo=UTC), "outside arm window"),
        ):
            with patch(
                "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
            ):
                with self.assertRaisesRegex(ValueError, message):
                    build_phase9_demo_gate_activation_contract(
                        approval=approval,
                        packet=inputs[0],
                        design=inputs[1],
                        request=inputs[2],
                        session_arm=inputs[3],
                        session_ready=inputs[4],
                        execution_arm=inputs[5],
                        runtime_authority=inputs[6],
                        launch_preflight=inputs[7],
                        execution_permit=inputs[8],
                        journal_rows=[],
                        activation_time_utc=bad_time,
                        code_commit=COMMIT,
                    )

    def test_packet_identity_change_invalidates_existing_approval(self) -> None:
        approval, inputs = _build_approval()
        changed_packet = dict(inputs[0])
        changed_packet["authorization_packet_fingerprint"] = "f" * 64
        with patch(
            "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
        ):
            with self.assertRaisesRegex(
                ValueError,
                "authorization_packet_fingerprint mismatch",
            ):
                validate_phase9_first_demo_explicit_approval(
                    approval,
                    packet=changed_packet,
                    design=inputs[1],
                    request=inputs[2],
                    session_arm=inputs[3],
                    session_ready=inputs[4],
                    execution_arm=inputs[5],
                    runtime_authority=inputs[6],
                    launch_preflight=inputs[7],
                    execution_permit=inputs[8],
                    journal_rows=[],
                )

    def test_source_gate_true_fails_closed(self) -> None:
        inputs = _inputs()
        statement = approval_statement_for_challenge(
            inputs[0]["authorization_challenge_fingerprint"]
        )
        with (
            patch(
                "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
            ),
            patch("fmp.phase9.approval.DEMO_EXECUTION_SOURCE_ARMED", True),
        ):
            with self.assertRaisesRegex(ValueError, "source unarmed"):
                build_phase9_first_demo_explicit_approval(
                    packet=inputs[0],
                    design=inputs[1],
                    request=inputs[2],
                    session_arm=inputs[3],
                    session_ready=inputs[4],
                    execution_arm=inputs[5],
                    runtime_authority=inputs[6],
                    launch_preflight=inputs[7],
                    execution_permit=inputs[8],
                    journal_rows=[],
                    operator_identity_reference="operator-fixture-068",
                    operator_approval_reference="approval-fixture-068",
                    approval_statement=statement,
                    approval_time_utc=APPROVAL_TIME,
                    code_commit=COMMIT,
                )

    def test_writers_are_create_only(self) -> None:
        approval, inputs = _build_approval()
        with patch(
            "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
        ):
            contract = build_phase9_demo_gate_activation_contract(
                approval=approval,
                packet=inputs[0],
                design=inputs[1],
                request=inputs[2],
                session_arm=inputs[3],
                session_ready=inputs[4],
                execution_arm=inputs[5],
                runtime_authority=inputs[6],
                launch_preflight=inputs[7],
                execution_permit=inputs[8],
                journal_rows=[],
                activation_time_utc=ACTIVATION_TIME,
                code_commit=COMMIT,
            )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            approval_dir = root / "approval"
            activation_dir = root / "activation"
            with patch(
                "fmp.phase9.approval.validate_phase9_first_demo_authorization_packet"
            ):
                approval_manifest = write_phase9_first_demo_explicit_approval(
                    approval,
                    out_dir=approval_dir,
                    packet=inputs[0],
                    design=inputs[1],
                    request=inputs[2],
                    session_arm=inputs[3],
                    session_ready=inputs[4],
                    execution_arm=inputs[5],
                    runtime_authority=inputs[6],
                    launch_preflight=inputs[7],
                    execution_permit=inputs[8],
                    journal_rows=[],
                )
                activation_manifest = write_phase9_demo_gate_activation_contract(
                    contract,
                    out_dir=activation_dir,
                    approval=approval,
                    packet=inputs[0],
                    design=inputs[1],
                    request=inputs[2],
                    session_arm=inputs[3],
                    session_ready=inputs[4],
                    execution_arm=inputs[5],
                    runtime_authority=inputs[6],
                    launch_preflight=inputs[7],
                    execution_permit=inputs[8],
                    journal_rows=[],
                )
                self.assertFalse(
                    approval_manifest["demo_execution_source_armed"]
                )
                self.assertFalse(
                    activation_manifest["demo_execution_source_armed"]
                )
                with self.assertRaises(FileExistsError):
                    write_phase9_first_demo_explicit_approval(
                        approval,
                        out_dir=approval_dir,
                        packet=inputs[0],
                        design=inputs[1],
                        request=inputs[2],
                        session_arm=inputs[3],
                        session_ready=inputs[4],
                        execution_arm=inputs[5],
                        runtime_authority=inputs[6],
                        launch_preflight=inputs[7],
                        execution_permit=inputs[8],
                        journal_rows=[],
                    )

    def test_source_has_no_execution_or_runner_dependency(self) -> None:
        source = inspect.getsource(approval_module)
        self.assertNotIn("MetaTrader5", source)
        self.assertNotIn("mt5_mutation", source)
        self.assertNotIn("GatedMT5DemoMutationAdapter", source)
        self.assertNotIn("from fmp.phase9.runner", source)
        self.assertNotIn("order_send(", source)
        self.assertNotIn("SEND_ATTEMPTED", source)
        self.assertNotIn("DEMO_EXECUTION_SOURCE_ARMED = True", source)
        self.assertIs(DEMO_EXECUTION_SOURCE_ARMED, False)


if __name__ == "__main__":
    unittest.main()
