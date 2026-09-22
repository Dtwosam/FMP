from __future__ import annotations

import hashlib
import inspect
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fmp.phase9.approval as approval_module
import fmp.phase9.arming as arming_module
import fmp.phase9.authorization_packet as packet_module
import fmp.phase9.permit as permit_module
import fmp.phase9.runtime_authority as authority_module
from fmp.phase9.approved_runtime import (
    PHASE9_APPROVED_DEMO_RUNTIME_PROTOCOL,
    run_phase9_approved_demo_one_shot,
    validate_phase9_approved_demo_runtime,
)
from fmp.phase9.protocol import DemoExecutionLockedError
from fmp.phase9.session import Phase9DemoSessionJournal


UTC = timezone.utc
NOW = datetime(2026, 9, 22, 19, 10, tzinfo=UTC)


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _inputs():
    activation = {
        "gate_activation_contract_fingerprint": "a" * 64,
        "authorization_packet_fingerprint": "b" * 64,
        "authorization_challenge_fingerprint": "c" * 64,
        "explicit_approval_fingerprint": "d" * 64,
        "execution_permit_fingerprint": "e" * 64,
        "request_fingerprint": "f" * 64,
        "client_order_id": "fmp9-dec069-fixture",
        "account_fingerprint": "1" * 64,
        "server": "FPMarketsSC-Demo",
        "not_before_utc": "2026-09-22T19:00:00Z",
        "expires_at_utc": "2026-09-22T20:00:00Z",
        "approval_time_utc": "2026-09-22T19:04:00Z",
        "activation_time_utc": "2026-09-22T19:05:00Z",
        "practice_only": True,
        "max_new_orders": 1,
        "explicit_execution_approval_recorded": True,
        "operator_gate_activation_contract_ready": True,
    }
    approval = {"explicit_approval_fingerprint": "d" * 64}
    packet = {
        "authorization_packet_fingerprint": "b" * 64,
        "authorization_challenge_fingerprint": "c" * 64,
        "review": {"fixture": True},
    }
    design = {
        "execution_path": {
            "account_fingerprint": "1" * 64,
            "server": "FPMarketsSC-Demo",
        }
    }
    request = {
        "request_fingerprint": "f" * 64,
        "client_order_id": "fmp9-dec069-fixture",
    }
    execution_permit = {"execution_permit_fingerprint": "e" * 64}
    return {
        "activation_contract": activation,
        "approval": approval,
        "packet": packet,
        "design": design,
        "request": request,
        "session_arm": {"fixture": "arm"},
        "session_ready": {"fixture": "ready"},
        "execution_arm": {"fixture": "execution-arm"},
        "runtime_authority": {"fixture": "authority"},
        "launch_preflight": {"fixture": "launch"},
        "execution_permit": execution_permit,
    }


class FakeBackend:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def order_send(self, mt5_request):
        self.calls.append("order_send")
        raise AssertionError("wrapper test must not call backend directly")

    def broker_orders(self):
        self.calls.append("broker_orders")
        return []

    def broker_positions(self):
        self.calls.append("broker_positions")
        return []


class Phase9ApprovedRuntimeWiringTests(unittest.TestCase):
    def _journal(self, root: Path):
        return Phase9DemoSessionJournal(
            path=root / "session.jsonl",
            arm={"session_arm_fingerprint": "8" * 64},
            request={
                "request_fingerprint": "f" * 64,
                "client_order_id": "fmp9-dec069-fixture",
            },
        )

    def test_source_gate_blocks_before_runner_or_backend(self) -> None:
        inputs = _inputs()
        backend = FakeBackend()
        with TemporaryDirectory() as tmp:
            with self._journal(Path(tmp)) as journal:
                with (
                    patch(
                        "fmp.phase9.approved_runtime.validate_phase9_demo_gate_activation_contract"
                    ),
                    patch(
                        "fmp.phase9.approved_runtime.run_phase9_demo_one_shot"
                    ) as run_one_shot,
                ):
                    with self.assertRaises(DemoExecutionLockedError):
                        run_phase9_approved_demo_one_shot(
                            **inputs,
                            journal=journal,
                            backend=backend,
                            now_utc=NOW,
                            daily_halt_active=False,
                        )
                    run_one_shot.assert_not_called()
                    self.assertEqual(journal.rows, ())
        self.assertEqual(backend.calls, [])

    def test_simulated_armed_path_delegates_exactly_once(self) -> None:
        inputs = _inputs()
        backend = FakeBackend()
        one_shot = {
            "one_shot_run_fingerprint": "9" * 64,
            "outcome": "PHASE9_DEMO_ONE_SHOT_COMPLETED",
            "arm_spent": True,
            "send_attempt_count": 1,
        }
        with TemporaryDirectory() as tmp:
            with self._journal(Path(tmp)) as journal:
                with (
                    patch(
                        "fmp.phase9.approved_runtime.validate_phase9_demo_gate_activation_contract"
                    ),
                    patch(
                        "fmp.phase9.approved_runtime.DEMO_EXECUTION_SOURCE_ARMED",
                        True,
                    ),
                    patch(
                        "fmp.phase9.approved_runtime.run_phase9_demo_one_shot",
                        return_value=one_shot,
                    ) as run_one_shot,
                    patch(
                        "fmp.phase9.approved_runtime.validate_phase9_demo_one_shot_run"
                    ),
                ):
                    result = run_phase9_approved_demo_one_shot(
                        **inputs,
                        journal=journal,
                        backend=backend,
                        now_utc=NOW,
                        daily_halt_active=False,
                    )
                    self.assertEqual(run_one_shot.call_count, 1)

        self.assertEqual(result["protocol"], PHASE9_APPROVED_DEMO_RUNTIME_PROTOCOL)
        self.assertEqual(
            result["gate_activation_contract_fingerprint"],
            inputs["activation_contract"]["gate_activation_contract_fingerprint"],
        )
        self.assertEqual(
            result["one_shot_run_fingerprint"],
            one_shot["one_shot_run_fingerprint"],
        )
        self.assertEqual(
            result["one_shot_outcome"],
            "PHASE9_DEMO_ONE_SHOT_COMPLETED",
        )
        self.assertTrue(result["approved_runner_wiring_used"])
        self.assertTrue(result["arm_spent"])
        self.assertEqual(result["send_attempt_count"], 1)
        self.assertFalse(result["live_order_authorized"])
        self.assertFalse(result["real_money_authorized"])
        self.assertFalse(result["phase10_authorized"])
        self.assertFalse(result["phase11_authorized"])
        validate_phase9_approved_demo_runtime(result)

    def test_runtime_time_and_daily_halt_fail_before_gate(self) -> None:
        inputs = _inputs()
        backend = FakeBackend()
        with TemporaryDirectory() as tmp:
            with self._journal(Path(tmp)) as journal:
                with patch(
                    "fmp.phase9.approved_runtime.validate_phase9_demo_gate_activation_contract"
                ):
                    with self.assertRaisesRegex(ValueError, "daily halt"):
                        run_phase9_approved_demo_one_shot(
                            **inputs,
                            journal=journal,
                            backend=backend,
                            now_utc=NOW,
                            daily_halt_active=True,
                        )
                    with self.assertRaisesRegex(ValueError, "precedes activation"):
                        run_phase9_approved_demo_one_shot(
                            **inputs,
                            journal=journal,
                            backend=backend,
                            now_utc=datetime(
                                2026, 9, 22, 19, 4, 59, tzinfo=UTC
                            ),
                            daily_halt_active=False,
                        )
                    with self.assertRaisesRegex(ValueError, "outside arm window"):
                        run_phase9_approved_demo_one_shot(
                            **inputs,
                            journal=journal,
                            backend=backend,
                            now_utc=datetime(
                                2026, 9, 22, 20, 1, tzinfo=UTC
                            ),
                            daily_halt_active=False,
                        )
        self.assertEqual(backend.calls, [])

    def test_refingerprinted_wrapper_result_tamper_fails(self) -> None:
        inputs = _inputs()
        payload = {
            "protocol": PHASE9_APPROVED_DEMO_RUNTIME_PROTOCOL,
            "experiment_id": "EXP-20260922-040",
            "decision": "DEC-069",
            "gate_activation_contract_fingerprint": "a" * 64,
            "explicit_approval_fingerprint": "d" * 64,
            "authorization_packet_fingerprint": "b" * 64,
            "authorization_challenge_fingerprint": "c" * 64,
            "execution_permit_fingerprint": "e" * 64,
            "request_fingerprint": "f" * 64,
            "client_order_id": "fmp9-dec069-fixture",
            "activation_time_utc": inputs["activation_contract"][
                "activation_time_utc"
            ],
            "runtime_time_utc": "2026-09-22T19:10:00Z",
            "one_shot_run_fingerprint": "9" * 64,
            "one_shot_outcome": "PHASE9_DEMO_ONE_SHOT_COMPLETED",
            "arm_spent": True,
            "send_attempt_count": 1,
            "approved_runner_wiring_used": True,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "phase10_authorized": False,
            "phase11_authorized": False,
        }
        result = payload | {"approved_runtime_fingerprint": _digest(payload)}
        validate_phase9_approved_demo_runtime(result)

        changed = dict(result)
        changed["send_attempt_count"] = 2
        changed.pop("approved_runtime_fingerprint")
        changed["approved_runtime_fingerprint"] = _digest(changed)
        with self.assertRaisesRegex(ValueError, "exactly one attempt"):
            validate_phase9_approved_demo_runtime(changed)

    def test_artifact_validators_are_gate_state_independent(self) -> None:
        validators = (
            arming_module.validate_phase9_demo_execution_arm,
            authority_module.validate_phase9_demo_runtime_authority,
            permit_module.validate_phase9_demo_execution_permit,
            packet_module.validate_phase9_first_demo_authorization_packet,
            approval_module.validate_phase9_first_demo_explicit_approval,
            approval_module.validate_phase9_demo_gate_activation_contract,
        )
        for validator in validators:
            self.assertNotIn(
                "DEMO_EXECUTION_SOURCE_ARMED",
                inspect.getsource(validator),
                validator.__name__,
            )

        self.assertIn(
            "require_source_unarmed=True",
            inspect.getsource(arming_module.build_phase9_demo_execution_arm),
        )
        self.assertIn(
            "require_source_unarmed=True",
            inspect.getsource(
                authority_module.build_phase9_demo_runtime_authority
            ),
        )
        self.assertIn(
            "require_source_unarmed=True",
            inspect.getsource(permit_module.build_phase9_demo_execution_permit),
        )
        self.assertIn(
            "DEMO_EXECUTION_SOURCE_ARMED",
            inspect.getsource(
                packet_module.build_phase9_first_demo_authorization_packet
            ),
        )
        self.assertIn(
            "require_source_unarmed=True",
            inspect.getsource(
                approval_module.build_phase9_first_demo_explicit_approval
            ),
        )
        self.assertIn(
            "DEMO_EXECUTION_SOURCE_ARMED",
            inspect.getsource(
                approval_module.build_phase9_demo_gate_activation_contract
            ),
        )


if __name__ == "__main__":
    unittest.main()
