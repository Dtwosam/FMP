from __future__ import annotations

import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.shadow import PRACTICE_STREAM_HOST
from fmp.shadow.oanda import OandaPracticePricingStream, OandaPracticeStreamError


class _FakeResponse:
    def __init__(self, lines: list[bytes], *, status: int = 200, reason: str = "OK") -> None:
        self._lines = list(lines)
        self.status = status
        self.reason = reason
        self.closed = False

    def readline(self) -> bytes:
        if not self._lines:
            return b""
        return self._lines.pop(0)

    def close(self) -> None:
        self.closed = True


class _FakeConnection:
    instances: list["_FakeConnection"] = []
    response_factory = staticmethod(
        lambda: _FakeResponse([b'{"type":"PRICE"}\n', b"\n", b'{"type":"HEARTBEAT"}\r\n'])
    )

    def __init__(self, host: str) -> None:
        self.host = host
        self.requests: list[tuple[str, str, object, dict[str, str]]] = []
        self.response = self.response_factory()
        self.closed = False
        self.__class__.instances.append(self)

    def request(
        self,
        method: str,
        url: str,
        body: object = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.requests.append((method, url, body, dict(headers or {})))

    def getresponse(self) -> _FakeResponse:
        return self.response

    def close(self) -> None:
        self.closed = True


class Phase8OandaTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        _FakeConnection.instances.clear()
        _FakeConnection.response_factory = staticmethod(
            lambda: _FakeResponse(
                [b'{"type":"PRICE"}\n', b"\n", b'{"type":"HEARTBEAT"}\r\n']
            )
        )

    def test_constructor_exposes_only_account_id_and_token_as_keyword_inputs(self) -> None:
        parameters = inspect.signature(OandaPracticePricingStream).parameters
        self.assertEqual(tuple(parameters), ("account_id", "token"))
        self.assertTrue(all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in parameters.values()))
        for forbidden in ("host", "base_url", "method", "path", "instrument"):
            self.assertNotIn(forbidden, parameters)
        self.assertFalse(hasattr(OandaPracticePricingStream, "request"))

    def test_iter_lines_uses_exact_practice_get_boundary_and_in_memory_bearer_token(self) -> None:
        with patch("fmp.shadow.oanda.http.client.HTTPSConnection", _FakeConnection):
            stream = OandaPracticePricingStream(
                account_id="101-001-12345678-001",
                token="secret-token",
            )
            self.assertEqual(
                list(stream.iter_lines()),
                [b'{"type":"PRICE"}', b'{"type":"HEARTBEAT"}'],
            )

        self.assertEqual(len(_FakeConnection.instances), 1)
        connection = _FakeConnection.instances[0]
        self.assertEqual(connection.host, PRACTICE_STREAM_HOST)
        self.assertTrue(connection.closed)
        self.assertTrue(connection.response.closed)
        self.assertEqual(len(connection.requests), 1)
        method, url, body, headers = connection.requests[0]
        self.assertEqual(method, "GET")
        self.assertEqual(
            url,
            "/v3/accounts/101-001-12345678-001/pricing/stream"
            "?instruments=USD_JPY&snapshot=true&includeHomeConversions=false",
        )
        self.assertIsNone(body)
        self.assertEqual(headers["Authorization"], "Bearer secret-token")

    def test_invalid_account_or_token_is_rejected_without_echoing_secret_values(self) -> None:
        cases = (
            {"account_id": "../orders", "token": "secret-token"},
            {"account_id": "101-001-12345678-001?x=y", "token": "secret-token"},
            {"account_id": "101-001-12345678-001", "token": "   "},
            {"account_id": "101-001-12345678-001", "token": "bad\r\ntoken"},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError) as caught:
                OandaPracticePricingStream(**kwargs)
            message = str(caught.exception)
            self.assertNotIn(kwargs["account_id"], message)
            self.assertNotIn(kwargs["token"], message)

    def test_non_200_and_redirect_responses_fail_closed_without_secrets(self) -> None:
        for status in (301, 302, 307, 308, 401, 403, 404, 429, 500, 503):
            _FakeConnection.instances.clear()
            _FakeConnection.response_factory = staticmethod(
                lambda status=status: _FakeResponse([], status=status, reason="failure")
            )
            with self.subTest(status=status), patch(
                "fmp.shadow.oanda.http.client.HTTPSConnection", _FakeConnection
            ):
                stream = OandaPracticePricingStream(
                    account_id="101-001-12345678-001",
                    token="secret-token",
                )
                with self.assertRaises(OandaPracticeStreamError) as caught:
                    list(stream.iter_lines())
                message = str(caught.exception)
                self.assertIn(str(status), message)
                self.assertNotIn("secret-token", message)
                self.assertNotIn("101-001-12345678-001", message)

    def test_transport_exceptions_are_redacted(self) -> None:
        class ExplodingConnection(_FakeConnection):
            def request(self, method, url, body=None, headers=None):  # type: ignore[no-untyped-def]
                raise RuntimeError("secret-token 101-001-12345678-001")

        with patch("fmp.shadow.oanda.http.client.HTTPSConnection", ExplodingConnection):
            stream = OandaPracticePricingStream(
                account_id="101-001-12345678-001",
                token="secret-token",
            )
            with self.assertRaises(OandaPracticeStreamError) as caught:
                list(stream.iter_lines())
        self.assertEqual(str(caught.exception), "OANDA Practice pricing stream transport failed")

    def test_runtime_shadow_source_contains_no_production_or_mutation_endpoint_surface(self) -> None:
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(Path("src/fmp/shadow").glob("*.py"))
        )
        forbidden = (
            "stream-fxtrade.oanda.com",
            "api-fxtrade.oanda.com",
            "/orders",
            "/trades",
            "/positions",
            "order_send",
        )
        for item in forbidden:
            self.assertNotIn(item, source)


if __name__ == "__main__":
    unittest.main()
