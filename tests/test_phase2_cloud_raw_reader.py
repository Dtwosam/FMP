from __future__ import annotations

import base64
import hashlib
import json
import unittest
from datetime import date

from fmp.data.cloud import CloudHttpResponse
from fmp.data.phase2.raw_reader import (
    CloudRawChunkReader,
    CloudRawReadResponse,
    GithubRawReadOidcTokenProvider,
    RawReadError,
)
from fmp.data.types import RawChunkKey


def _jwt(exp: int = 2_000_000_000) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
    return f"x.{payload}.y"


class GetTransport:
    def __init__(self, responses: list[object]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, dict[str, str], float]] = []

    def get(self, url: str, headers: dict[str, str], timeout_seconds: float) -> CloudHttpResponse:
        self.calls.append((url, headers, timeout_seconds))
        item = self.responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item  # type: ignore[return-value]


class PostTransport:
    def __init__(self, responses: list[object]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, bytes, dict[str, str], float]] = []

    def post(self, url: str, body: bytes, headers: dict[str, str], timeout_seconds: float) -> CloudRawReadResponse:
        self.calls.append((url, body, headers, timeout_seconds))
        item = self.responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item  # type: ignore[return-value]


class TokenProvider:
    def __init__(self, token: str = "oidc") -> None:
        self.token = token
        self.calls = 0

    def get_token(self) -> str:
        self.calls += 1
        return self.token


class GithubRawReadOidcTests(unittest.TestCase):
    def test_requests_exact_audience_and_caches_unexpired_token(self) -> None:
        token = _jwt()
        transport = GetTransport([CloudHttpResponse(200, json.dumps({"value": token}).encode())])
        provider = GithubRawReadOidcTokenProvider(
            "https://token.actions.example/id?x=1",
            "request-token",
            transport=transport,
            sleep_fn=lambda _: None,
            clock=lambda: 1_700_000_000,
        )
        self.assertEqual(provider.get_token(), token)
        self.assertEqual(provider.get_token(), token)
        self.assertEqual(len(transport.calls), 1)
        url, headers, _ = transport.calls[0]
        self.assertIn("audience=fmp-supabase-raw-read", url)
        self.assertEqual(headers["Authorization"], "Bearer request-token")

    def test_retries_only_transient_oidc_failures(self) -> None:
        sleeps: list[float] = []
        token = _jwt()
        provider = GithubRawReadOidcTokenProvider(
            "https://token.actions.example/id",
            "request-token",
            transport=GetTransport([
                TimeoutError("slow"),
                CloudHttpResponse(429, b"busy"),
                CloudHttpResponse(200, json.dumps({"value": token}).encode()),
            ]),
            sleep_fn=sleeps.append,
        )
        self.assertEqual(provider.get_token(), token)
        self.assertEqual(sleeps, [1.0, 1.0])

        permanent = GetTransport([CloudHttpResponse(403, b"no")])
        provider = GithubRawReadOidcTokenProvider(
            "https://token.actions.example/id", "request-token", transport=permanent, sleep_fn=lambda _: None
        )
        with self.assertRaises(RawReadError):
            provider.get_token()
        self.assertEqual(len(permanent.calls), 1)


class CloudRawChunkReaderTests(unittest.TestCase):
    key = RawChunkKey("EURUSD", "BID", date(2020, 1, 2))

    @staticmethod
    def complete(body: bytes, **overrides: str) -> CloudRawReadResponse:
        headers = {
            "content-type": "application/octet-stream",
            "x-fmp-protocol": "fmp-raw-read-v1",
            "x-fmp-pair": "EURUSD",
            "x-fmp-side": "BID",
            "x-fmp-date-utc": "2020-01-02",
            "x-fmp-sha256": hashlib.sha256(body).hexdigest(),
            "x-fmp-size-bytes": str(len(body)),
            "x-fmp-manifest-status": "complete",
        }
        headers.update(overrides)
        return CloudRawReadResponse(200, body, headers)

    def test_complete_read_posts_identity_only_and_verifies_body(self) -> None:
        body = b"bi5-bytes"
        transport = PostTransport([self.complete(body)])
        reader = CloudRawChunkReader(
            "https://project.supabase.co/functions/v1/fmp-raw-read",
            TokenProvider(),
            transport=transport,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(reader.read(self.key), body)
        _, request_body, headers, _ = transport.calls[0]
        self.assertEqual(json.loads(request_body), {"pair": "EURUSD", "side": "BID", "date_utc": "2020-01-02"})
        self.assertEqual(headers["Authorization"], "Bearer oidc")
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_verified_not_found_returns_none(self) -> None:
        payload = {"status": "not_found", "protocol": "fmp-raw-read-v1", "pair": "EURUSD", "side": "BID", "date_utc": "2020-01-02"}
        response = CloudRawReadResponse(404, json.dumps(payload).encode(), {"content-type": "application/json"})
        self.assertIsNone(CloudRawChunkReader("https://project.supabase.co/f", TokenProvider(), transport=PostTransport([response])).read(self.key))

    def test_integrity_or_identity_failure_is_not_retried(self) -> None:
        body = b"bi5-bytes"
        cases = [
            self.complete(body, **{"x-fmp-protocol": "wrong"}),
            self.complete(body, **{"x-fmp-pair": "GBPUSD"}),
            self.complete(body, **{"x-fmp-sha256": "0" * 64}),
            self.complete(body, **{"x-fmp-size-bytes": "999"}),
            CloudRawReadResponse(200, body, {"content-type": "application/json"}),
        ]
        for response in cases:
            with self.subTest(response=response):
                transport = PostTransport([response])
                reader = CloudRawChunkReader("https://project.supabase.co/f", TokenProvider(), transport=transport, sleep_fn=lambda _: None)
                with self.assertRaises(RawReadError):
                    reader.read(self.key)
                self.assertEqual(len(transport.calls), 1)

    def test_permanent_4xx_not_found_schema_error_is_not_retried(self) -> None:
        for response in [
            CloudRawReadResponse(401, b"{}", {"content-type": "application/json"}),
            CloudRawReadResponse(404, b"{}", {"content-type": "application/json"}),
        ]:
            transport = PostTransport([response])
            reader = CloudRawChunkReader("https://project.supabase.co/f", TokenProvider(), transport=transport, sleep_fn=lambda _: None)
            with self.assertRaises(RawReadError):
                reader.read(self.key)
            self.assertEqual(len(transport.calls), 1)

    def test_retries_connection_429_and_5xx_only(self) -> None:
        body = b"ok"
        sleeps: list[float] = []
        transport = PostTransport([
            ConnectionError("down"),
            CloudRawReadResponse(500, b"oops", {}),
            self.complete(body),
        ])
        reader = CloudRawChunkReader("https://project.supabase.co/f", TokenProvider(), transport=transport, sleep_fn=sleeps.append)
        self.assertEqual(reader.read(self.key), body)
        self.assertEqual(sleeps, [1.0, 1.0])

    def test_endpoint_and_retry_settings_fail_closed(self) -> None:
        with self.assertRaises(RawReadError):
            CloudRawChunkReader("http://project.example/f", TokenProvider())
        with self.assertRaises(RawReadError):
            CloudRawChunkReader("https://project.example/f", TokenProvider(), max_attempts=0)


if __name__ == "__main__":
    unittest.main()
