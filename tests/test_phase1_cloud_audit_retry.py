from __future__ import annotations

import json
import unittest

from fmp.data.cloud import CloudHttpResponse
from fmp.data.cloud_audit import (
    CloudAuditError,
    GithubAuditOidcTokenProvider,
    SupabaseRawAuditClient,
)


class StaticTokenProvider:
    def get_token(self) -> str:
        return "oidc-token"


class SequenceGetTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def get(self, url, headers, timeout_seconds):
        self.calls += 1
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class SequencePostTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0
        self.bodies = []

    def post(self, url, body, headers, timeout_seconds):
        self.calls += 1
        self.bodies.append(body)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class AuditRetryTests(unittest.TestCase):
    path = "raw/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.bi5"

    def audited_payload(self):
        return {"status": "audited", "count": 1, "objects": [{
            "path": self.path,
            "kind": "raw",
            "sha256": "a" * 64,
            "size_bytes": 123,
        }]}

    def test_oidc_retries_timeout_then_succeeds(self):
        transport = SequenceGetTransport([
            TimeoutError("temporary"),
            CloudHttpResponse(200, b'{"value":"token"}'),
        ])
        provider = GithubAuditOidcTokenProvider(
            "https://actions.example/oidc",
            "request-token",
            transport=transport,
            max_attempts=2,
            retry_delay_seconds=0,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(provider.get_token(), "token")
        self.assertEqual(transport.calls, 2)

    def test_oidc_exhausts_transient_failures_at_exact_attempt_limit(self):
        transport = SequenceGetTransport([TimeoutError("temporary")] * 3)
        provider = GithubAuditOidcTokenProvider(
            "https://actions.example/oidc", "request-token", transport=transport,
            max_attempts=3, retry_delay_seconds=0, sleep_fn=lambda _: None,
        )
        with self.assertRaisesRegex(CloudAuditError, "after 3 attempts"):
            provider.get_token()
        self.assertEqual(transport.calls, 3)

    def test_retry_delay_must_be_numeric(self):
        with self.assertRaises(CloudAuditError):
            SupabaseRawAuditClient(
                "https://example.supabase.co/functions/v1/fmp-raw-audit",
                StaticTokenProvider(), retry_delay_seconds="one",  # type: ignore[arg-type]
            )

    def test_preflight_retries_503_then_succeeds(self):
        transport = SequenceGetTransport([
            CloudHttpResponse(503, b'{"error":"busy"}'),
            CloudHttpResponse(200, b'{"status":"ready","protocol":"fmp-raw-audit-v1"}'),
        ])
        client = SupabaseRawAuditClient(
            "https://example.supabase.co/functions/v1/fmp-raw-audit",
            StaticTokenProvider(),
            get_transport=transport,
            max_attempts=2,
            retry_delay_seconds=0,
            sleep_fn=lambda _: None,
        )
        client.preflight()
        self.assertEqual(transport.calls, 2)

    def test_audit_post_retries_429_then_succeeds(self):
        payload = self.audited_payload()
        transport = SequencePostTransport([
            CloudHttpResponse(429, b'{"error":"rate_limited"}'),
            CloudHttpResponse(200, json.dumps(payload).encode()),
        ])
        client = SupabaseRawAuditClient(
            "https://example.supabase.co/functions/v1/fmp-raw-audit",
            StaticTokenProvider(),
            transport=transport,
            max_attempts=2,
            retry_delay_seconds=0,
            sleep_fn=lambda _: None,
        )
        self.assertEqual(client.audit_paths([self.path]), payload["objects"])
        self.assertEqual(transport.calls, 2)

    def test_audit_post_retries_timeout_then_succeeds_with_identical_body(self):
        payload = self.audited_payload()
        transport = SequencePostTransport([
            TimeoutError("temporary"), CloudHttpResponse(200, json.dumps(payload).encode()),
        ])
        client = SupabaseRawAuditClient(
            "https://example.supabase.co/functions/v1/fmp-raw-audit", StaticTokenProvider(),
            transport=transport, max_attempts=2, retry_delay_seconds=0, sleep_fn=lambda _: None,
        )
        self.assertEqual(client.audit_paths([self.path]), payload["objects"])
        self.assertEqual(transport.calls, 2)
        self.assertEqual(transport.bodies, [transport.bodies[0], transport.bodies[0]])

    def test_audit_post_exhausts_transient_failures_at_exact_attempt_limit(self):
        transport = SequencePostTransport([CloudHttpResponse(503, b'{"error":"busy"}')] * 3)
        client = SupabaseRawAuditClient(
            "https://example.supabase.co/functions/v1/fmp-raw-audit", StaticTokenProvider(),
            transport=transport, max_attempts=3, retry_delay_seconds=0, sleep_fn=lambda _: None,
        )
        with self.assertRaisesRegex(CloudAuditError, "HTTP 503"):
            client.audit_paths([self.path])
        self.assertEqual(transport.calls, 3)

    def test_malformed_successful_audit_response_is_not_retried(self):
        transport = SequencePostTransport([CloudHttpResponse(200, b"not-json")])
        client = SupabaseRawAuditClient(
            "https://example.supabase.co/functions/v1/fmp-raw-audit", StaticTokenProvider(),
            transport=transport, max_attempts=3, retry_delay_seconds=0, sleep_fn=lambda _: None,
        )
        with self.assertRaisesRegex(CloudAuditError, "malformed HTTP 200"):
            client.audit_paths([self.path])
        self.assertEqual(transport.calls, 1)

    def test_audit_post_does_not_retry_permanent_401(self):
        transport = SequencePostTransport([
            CloudHttpResponse(401, b'{"error":"unauthorized"}'),
        ])
        client = SupabaseRawAuditClient(
            "https://example.supabase.co/functions/v1/fmp-raw-audit",
            StaticTokenProvider(),
            transport=transport,
            max_attempts=3,
            retry_delay_seconds=0,
            sleep_fn=lambda _: None,
        )
        with self.assertRaisesRegex(CloudAuditError, "HTTP 401"):
            client.audit_paths([self.path])
        self.assertEqual(transport.calls, 1)


if __name__ == "__main__":
    unittest.main()
