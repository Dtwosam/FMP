from __future__ import annotations

import hashlib
import inspect
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fmp.phase9.authorization_packet as packet_module
from fmp.phase9.authorization_packet import (
    PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_PROTOCOL,
    PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_READY,
    build_phase9_first_demo_authorization_packet,
    validate_phase9_first_demo_authorization_packet,
    write_phase9_first_demo_authorization_packet,
)


COMMIT = "c" * 40


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
    design = {
        "demo_design_fingerprint": "1" * 64,
        "champion_set_fingerprint": "2" * 64,
        "strategies": [
            {
                "fingerprint": "3" * 64,
                "family": "session-breakout",
                "symbol": "EURUSD",
                "timeframe": "15m",
            }
        ],
        "execution_path": {
            "provider": "MetaTrader5",
            "account_fingerprint": "4" * 64,
            "server": "FPMarketsSC-Demo",
        },
    }
    request = {
        "request_fingerprint": "5" * 64,
        "strategy_fingerprint": "3" * 64,
        "client_order_id": "fmp9-authorization-fixture",
        "decision_id": "decision-067",
        "symbol": "EURUSD",
        "broker_symbol": "EURUSD",
        "direction": "LONG",
        "units": 10_000,
        "reserved_risk_usd": 100.0,
        "stop_price": 1.095,
        "target_price": 1.11,
        "reference_entry_price": 1.10,
        "decision_timestamp_utc": "2026-09-22T18:45:00Z",
        "earliest_executable_timestamp_utc": "2026-09-22T18:46:00Z",
    }
    session_arm = {"session_arm_fingerprint": "6" * 64}
    session_ready = {"session_ready_fingerprint": "7" * 64}
    execution_arm = {
        "execution_arm_fingerprint": "8" * 64,
        "not_before_utc": "2026-09-22T18:50:00Z",
        "expires_at_utc": "2026-09-22T20:00:00Z",
        "operator_approval_reference": "session-approval-fixture-067",
    }
    runtime_authority = {"runtime_authority_fingerprint": "9" * 64}
    mt5_request = {
        "action": "TRADE_ACTION_DEAL",
        "symbol": "EURUSD",
        "volume": 0.1,
        "type": "ORDER_TYPE_BUY",
        "price": 1.1002,
        "sl": 1.095,
        "tp": 1.11,
        "deviation": 0,
        "type_time": "ORDER_TIME_GTC",
        "type_filling": "ORDER_FILLING_RETURN",
        "comment": "fmp9-authorization-fixture",
    }
    launch_preflight = {
        "launch_preflight_fingerprint": "a" * 64,
        "launch_preflight_time_utc": "2026-09-22T18:55:00Z",
        "order_check_request": {
            "order_check_request_fingerprint": "b" * 64,
            "mt5_request": mt5_request,
        },
    }
    execution_permit = {
        "execution_permit_fingerprint": "c" * 64,
        "checked_mt5_request_sha256": _digest(mt5_request),
        "demo_execution_permit_artifact_ready": True,
        "send_attempt_count": 0,
        "practice_only": True,
        "max_new_orders": 1,
    }
    return (
        design,
        request,
        session_arm,
        session_ready,
        execution_arm,
        runtime_authority,
        launch_preflight,
        execution_permit,
    )


class Phase9FirstDemoAuthorizationPacketTests(unittest.TestCase):
    def _build(self, *, code_commit=COMMIT):
        inputs = _inputs()
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch_preflight,
            execution_permit,
        ) = inputs
        with patch(
            "fmp.phase9.authorization_packet.validate_phase9_demo_execution_permit"
        ):
            result = build_phase9_first_demo_authorization_packet(
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                runtime_authority=runtime_authority,
                launch_preflight=launch_preflight,
                execution_permit=execution_permit,
                journal_rows=[],
                code_commit=code_commit,
            )
        return result, inputs

    def test_packet_exposes_exact_review_and_authorizes_nothing(self) -> None:
        result, inputs = self._build()
        _, request, _, _, execution_arm, _, launch, permit = inputs
        self.assertEqual(
            result["protocol"],
            PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_PROTOCOL,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_READY,
        )
        review = result["review"]
        self.assertEqual(review["symbol"], "EURUSD")
        self.assertEqual(review["direction"], "LONG")
        self.assertEqual(review["units"], 10_000)
        self.assertEqual(review["volume_lots"], 0.1)
        self.assertEqual(review["reserved_risk_usd"], 100.0)
        self.assertEqual(review["checked_mt5_price"], 1.1002)
        self.assertEqual(review["protective_stop_price"], 1.095)
        self.assertEqual(review["target_price"], 1.11)
        self.assertEqual(review["client_order_id"], request["client_order_id"])
        self.assertEqual(
            review["execution_permit_fingerprint"],
            permit["execution_permit_fingerprint"],
        )
        self.assertEqual(
            review["expires_at_utc"],
            execution_arm["expires_at_utc"],
        )
        self.assertEqual(
            review["checked_mt5_request_sha256"],
            permit["checked_mt5_request_sha256"],
        )
        self.assertEqual(
            review["demo_acceptance_obligations"]["min_completed_trades"],
            40,
        )
        self.assertEqual(
            review["demo_acceptance_obligations"]["min_represented_pairs"],
            2,
        )
        self.assertEqual(
            review["demo_acceptance_obligations"][
                "max_p95_adverse_entry_slippage_pips"
            ],
            1.0,
        )
        self.assertTrue(result["first_demo_authorization_packet_ready"])
        for field in (
            "explicit_execution_approval_recorded",
            "demo_execution_source_armed",
            "demo_execution_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "phase10_authorized",
            "phase11_authorized",
        ):
            self.assertFalse(result[field])

        with patch(
            "fmp.phase9.authorization_packet.validate_phase9_demo_execution_permit"
        ):
            validate_phase9_first_demo_authorization_packet(
                result,
                design=inputs[0],
                request=inputs[1],
                session_arm=inputs[2],
                session_ready=inputs[3],
                execution_arm=inputs[4],
                runtime_authority=inputs[5],
                launch_preflight=inputs[6],
                execution_permit=inputs[7],
                journal_rows=[],
            )

    def test_challenge_is_order_identity_not_builder_commit_identity(self) -> None:
        first, _ = self._build(code_commit="c" * 40)
        second, _ = self._build(code_commit="d" * 40)
        self.assertEqual(
            first["authorization_challenge_fingerprint"],
            second["authorization_challenge_fingerprint"],
        )
        self.assertNotEqual(
            first["authorization_packet_fingerprint"],
            second["authorization_packet_fingerprint"],
        )

    def test_refingerprinted_review_tamper_still_fails(self) -> None:
        result, inputs = self._build()
        changed = dict(result)
        changed["review"] = dict(result["review"])
        changed["review"]["units"] = 20_000
        changed["authorization_challenge_fingerprint"] = _digest(
            {
                "protocol": changed["protocol"],
                "decision": changed["decision"],
                "review": changed["review"],
            }
        )
        changed.pop("authorization_packet_fingerprint")
        changed["authorization_packet_fingerprint"] = _digest(changed)
        with patch(
            "fmp.phase9.authorization_packet.validate_phase9_demo_execution_permit"
        ):
            with self.assertRaisesRegex(ValueError, "review mismatch"):
                validate_phase9_first_demo_authorization_packet(
                    changed,
                    design=inputs[0],
                    request=inputs[1],
                    session_arm=inputs[2],
                    session_ready=inputs[3],
                    execution_arm=inputs[4],
                    runtime_authority=inputs[5],
                    launch_preflight=inputs[6],
                    execution_permit=inputs[7],
                    journal_rows=[],
                )

    def test_checked_request_tamper_fails_independently(self) -> None:
        inputs = list(_inputs())
        launch = dict(inputs[6])
        launch["order_check_request"] = dict(launch["order_check_request"])
        launch["order_check_request"]["mt5_request"] = dict(
            launch["order_check_request"]["mt5_request"]
        )
        launch["order_check_request"]["mt5_request"]["volume"] = 0.2
        inputs[6] = launch
        with patch(
            "fmp.phase9.authorization_packet.validate_phase9_demo_execution_permit"
        ):
            with self.assertRaisesRegex(ValueError, "checked request mismatch"):
                build_phase9_first_demo_authorization_packet(
                    design=inputs[0],
                    request=inputs[1],
                    session_arm=inputs[2],
                    session_ready=inputs[3],
                    execution_arm=inputs[4],
                    runtime_authority=inputs[5],
                    launch_preflight=inputs[6],
                    execution_permit=inputs[7],
                    journal_rows=[],
                    code_commit=COMMIT,
                )

    def test_armed_source_fails_before_packet_construction(self) -> None:
        inputs = _inputs()
        with (
            patch(
                "fmp.phase9.authorization_packet.validate_phase9_demo_execution_permit"
            ),
            patch(
                "fmp.phase9.authorization_packet.DEMO_EXECUTION_SOURCE_ARMED",
                True,
            ),
        ):
            with self.assertRaisesRegex(ValueError, "source unarmed"):
                build_phase9_first_demo_authorization_packet(
                    design=inputs[0],
                    request=inputs[1],
                    session_arm=inputs[2],
                    session_ready=inputs[3],
                    execution_arm=inputs[4],
                    runtime_authority=inputs[5],
                    launch_preflight=inputs[6],
                    execution_permit=inputs[7],
                    journal_rows=[],
                    code_commit=COMMIT,
                )

    def test_writer_is_create_only(self) -> None:
        result, inputs = self._build()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch(
                "fmp.phase9.authorization_packet.validate_phase9_demo_execution_permit"
            ):
                manifest = write_phase9_first_demo_authorization_packet(
                    result,
                    out_dir=root,
                    design=inputs[0],
                    request=inputs[1],
                    session_arm=inputs[2],
                    session_ready=inputs[3],
                    execution_arm=inputs[4],
                    runtime_authority=inputs[5],
                    launch_preflight=inputs[6],
                    execution_permit=inputs[7],
                    journal_rows=[],
                )
                self.assertTrue(
                    (root / "first-demo-authorization-packet.json").is_file()
                )
                self.assertTrue((root / "manifest.json").is_file())
                self.assertFalse(
                    manifest["explicit_execution_approval_recorded"]
                )
                self.assertFalse(manifest["demo_execution_source_armed"])
                with self.assertRaises(FileExistsError):
                    write_phase9_first_demo_authorization_packet(
                        result,
                        out_dir=root,
                        design=inputs[0],
                        request=inputs[1],
                        session_arm=inputs[2],
                        session_ready=inputs[3],
                        execution_arm=inputs[4],
                        runtime_authority=inputs[5],
                        launch_preflight=inputs[6],
                        execution_permit=inputs[7],
                        journal_rows=[],
                    )

    def test_packet_source_has_no_broker_or_runner_dependency(self) -> None:
        source = inspect.getsource(packet_module)
        self.assertNotIn("MetaTrader5", source)
        self.assertNotIn("GatedMT5DemoMutationAdapter", source)
        self.assertNotIn("mt5_mutation", source)
        self.assertNotIn("runner", source)
        self.assertNotIn("order_send(", source)
        self.assertNotIn("SEND_ATTEMPTED", source)


if __name__ == "__main__":
    unittest.main()
