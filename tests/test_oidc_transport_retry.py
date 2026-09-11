from __future__ import annotations

import json
import unittest

from fmp.data.cloud import CloudHttpResponse, CloudMirrorError, GithubOidcTokenProvider


class SequencedGetTransport:
    def __init__(self, outcomes: list[CloudHttpResponse | BaseException]) -> None:
        self.outcomes = list(outcomes)
        self.calls = 0

    def get(
        self,
        url: str,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> CloudHttpResponse:
        self.calls += 1
        if not self.outcomes:
            raise AssertionError("unexpected extra OIDC request")
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class OidcTransportRetryTests(unittest.TestCase):
    def test_oidc_provider_retries_timeout_then_succeeds(self) -> None:
        transport = SequencedGetTransport(
            [
                TimeoutError("timed out"),
                CloudHttpResponse(200, json.dumps({"value": "oidc-token"}).encode()),
            ]
        )
        sleeps: list[float] = []
        provider = GithubOidcTokenProvider(
            request_url="https://actions.example/oidc",
            request_token="request-token",
            transport=transport,
            max_attempts=3,
            retry_delay_seconds=0.25,
            sleep_fn=sleeps.append,
        )

        self.assertEqual(provider.get_token(), "oidc-token")
        self.assertEqual(transport.calls, 2)
        self.assertEqual(sleeps, [0.25])

    def test_oidc_provider_fails_after_bounded_transport_errors(self) -> None:
        transport = SequencedGetTransport(
            [TimeoutError("one"), ConnectionError("two"), OSError("three")]
        )
        sleeps: list[float] = []
        provider = GithubOidcTokenProvider(
            request_url="https://actions.example/oidc",
            request_token="request-token",
            transport=transport,
            max_attempts=3,
            retry_delay_seconds=0.25,
            sleep_fn=sleeps.append,
        )

        with self.assertRaisesRegex(CloudMirrorError, "after 3 attempts"):
            provider.get_token()

        self.assertEqual(transport.calls, 3)
        self.assertEqual(sleeps, [0.25, 0.25])


if __name__ == "__main__":
    unittest.main()
