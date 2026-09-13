from __future__ import annotations

import base64
import json
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from fmp.data.cloud import CloudHttpResponse
from fmp.data.phase2.raw_reader import GithubRawReadOidcTokenProvider


def _jwt(exp: int = 2_000_000_000) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
    return f"x.{payload}.y"


class SlowTransport:
    def __init__(self, token: str) -> None:
        self.token = token
        self.calls = 0
        self.lock = threading.Lock()

    def get(self, url: str, headers: dict[str, str], timeout_seconds: float) -> CloudHttpResponse:
        with self.lock:
            self.calls += 1
        time.sleep(0.05)
        return CloudHttpResponse(200, json.dumps({"value": self.token}).encode())


class OidcConcurrencyTests(unittest.TestCase):
    def test_concurrent_callers_share_one_cached_refresh(self) -> None:
        token = _jwt()
        transport = SlowTransport(token)
        provider = GithubRawReadOidcTokenProvider(
            "https://token.actions.example/id",
            "request-token",
            transport=transport,
            sleep_fn=lambda _: None,
            clock=lambda: 1_700_000_000,
        )
        with ThreadPoolExecutor(max_workers=4) as executor:
            values = list(executor.map(lambda _: provider.get_token(), range(4)))
        self.assertEqual(values, [token] * 4)
        self.assertEqual(transport.calls, 1)


if __name__ == "__main__":
    unittest.main()
