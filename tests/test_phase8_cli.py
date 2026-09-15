from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from fmp.shadow.cli import build_parser, main


ACCOUNT_ID = "101-001-12345678-001"
TOKEN = "secret-token"


def price_line(index: int) -> bytes:
    minute, second = divmod(index, 60)
    return (
        '{"type":"PRICE","time":"2026-09-15T12:%02d:%02dZ",'
        '"instrument":"USD_JPY","tradeable":true,'
        '"bids":[{"price":"140.001"}],"asks":[{"price":"140.003"}]}'
        % (minute, second)
    ).encode("utf-8")


def heartbeat_line(second: int) -> bytes:
    return (
        '{"type":"HEARTBEAT","time":"2026-09-15T12:00:%02dZ"}' % second
    ).encode("utf-8")


class FakeStream:
    def iter_lines(self):  # type: ignore[no-untyped-def]
        heartbeats = {10, 20, 30, 40, 50, 59}
        for index in range(100):
            yield price_line(index)
            if index in heartbeats:
                yield heartbeat_line(index)


class Phase8CliTests(unittest.TestCase):
    def test_parser_exposes_only_qualify_and_out_not_credentials_or_transport_overrides(self) -> None:
        parser = build_parser()
        help_text = parser.format_help()
        self.assertIn("qualify", help_text)
        for forbidden in (
            "--account-id",
            "--token",
            "--host",
            "--base-url",
            "--method",
            "--path",
            "--instrument",
        ):
            self.assertNotIn(forbidden, help_text)

        for forbidden in ("--account-id", "--token", "--host", "--instrument"):
            with self.subTest(forbidden=forbidden), self.assertRaises(SystemExit):
                parser.parse_args(["qualify", "--out", "out", forbidden, "x"])

    def test_missing_env_credentials_fail_before_stream_construction(self) -> None:
        called = False

        def factory(*, account_id: str, token: str):  # type: ignore[no-untyped-def]
            nonlocal called
            called = True
            raise AssertionError("must not construct stream")

        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit) as caught:
            main(
                ["qualify", "--out", tmp],
                environ={},
                stream_factory=factory,
            )
        self.assertEqual(caught.exception.code, 2)
        self.assertFalse(called)

    def test_qualify_reads_credentials_only_from_env_and_persists_no_plain_secret(self) -> None:
        captured: dict[str, str] = {}

        def factory(*, account_id: str, token: str):  # type: ignore[no-untyped-def]
            captured["account_id"] = account_id
            captured["token"] = token
            return FakeStream()

        with tempfile.TemporaryDirectory() as tmp:
            rc = main(
                ["qualify", "--out", tmp],
                environ={
                    "OANDA_PRACTICE_ACCOUNT_ID": ACCOUNT_ID,
                    "OANDA_PRACTICE_TOKEN": TOKEN,
                },
                stream_factory=factory,
            )
            self.assertEqual(rc, 0)
            self.assertEqual(captured, {"account_id": ACCOUNT_ID, "token": TOKEN})

            path = Path(tmp) / "qualification.json"
            self.assertTrue(path.is_file())
            raw = path.read_text(encoding="utf-8")
            self.assertNotIn(ACCOUNT_ID, raw)
            self.assertNotIn(TOKEN, raw)
            record = json.loads(raw)
            self.assertEqual(record["outcome"], "PASS")
            self.assertEqual(record["price_count"], 100)
            self.assertEqual(record["heartbeat_count"], 6)
            self.assertEqual(
                record["account_fingerprint"],
                hashlib.sha256(ACCOUNT_ID.encode("utf-8")).hexdigest(),
            )
            self.assertEqual(record["boundary_audit"]["method"], "GET")
            self.assertEqual(
                record["boundary_audit"]["host"],
                "stream-fxpractice.oanda.com",
            )

    def test_script_delegates_to_shadow_cli_and_contains_no_order_surface(self) -> None:
        source = Path("scripts/phase8_shadow.py").read_text(encoding="utf-8")
        self.assertIn("from fmp.shadow.cli import main", source)
        self.assertIn("raise SystemExit(main())", source)
        for forbidden in ("order_send", "/orders", "/trades", "/positions"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
