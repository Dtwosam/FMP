from __future__ import annotations

import base64
import json
import unittest
from datetime import date
from unittest.mock import patch

from fmp.data.cloud_audit import (
    CloudAuditError,
    GithubAuditOidcTokenProvider,
    SupabaseRawAuditClient,
    verify_cloud_keys,
)
from fmp.data.types import RawChunkKey


class StaticTokenProvider:
    def get_token(self) -> str:
        return "oidc-token"


class FakePostTransport:
    def __init__(self, payload: dict[str, object], status: int = 200) -> None:
        self.payload = payload
        self.status = status
        self.calls: list[tuple[str, bytes, dict[str, str], float]] = []

    def post(
        self,
        url: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ):
        from fmp.data.cloud import CloudHttpResponse

        self.calls.append((url, body, headers, timeout_seconds))
        return CloudHttpResponse(self.status, json.dumps(self.payload).encode())


class FakeAuditClient:
    def __init__(self, objects: dict[str, dict[str, object]]) -> None:
        self.objects = objects
        self.calls: list[list[str]] = []

    def audit_paths(self, paths: list[str]) -> list[dict[str, object]]:
        self.calls.append(list(paths))
        return [self.objects[path] for path in paths]


def manifest_payload(key: RawChunkKey, *, status: str = "complete") -> dict[str, object]:
    source_url = (
        f"https://datafeed.dukascopy.com/datafeed/{key.pair}/"
        f"{key.day.year:04d}/{key.day.month - 1:02d}/{key.day.day:02d}/"
        f"{key.side}_candles_min_1.bi5"
    )
    complete = status == "complete"
    return {
        "manifest_version": 1,
        "retrieval_method": "dukascopy-public-daily-m1-bi5-v1",
        "source": "dukascopy",
        "source_url": source_url,
        "pair": key.pair,
        "side": key.side,
        "date_utc": key.day.isoformat(),
        "granularity": "1m",
        "source_format": "bi5-lzma-daily-candles",
        "record_size_bytes": 24,
        "month_indexing": "zero_based_in_source_url",
        "status": status,
        "http_status": 200 if complete else 404,
        "sha256": "a" * 64 if complete else None,
        "compressed_size_bytes": 123 if complete else None,
        "records": 1440 if complete else None,
        "retrieved_at_utc": "2026-09-09T10:00:00+00:00",
    }


def audit_manifest(path: str, manifest: dict[str, object] | None) -> dict[str, object]:
    return {
        "path": path,
        "kind": "manifest",
        "sha256": "b" * 64,
        "size_bytes": 400,
        "manifest_json": manifest,
        "manifest_parse_error": manifest is None,
    }


def audit_raw(path: str, *, sha256: str = "a" * 64, size: int = 123) -> dict[str, object]:
    return {
        "path": path,
        "kind": "raw",
        "sha256": sha256,
        "size_bytes": size,
    }


class FakeGetTransport:
    def __init__(self, tokens: list[str]) -> None:
        self.tokens = list(tokens)
        self.calls: list[tuple[str, dict[str, str], float]] = []

    def get(self, url: str, headers: dict[str, str], timeout_seconds: float):
        from fmp.data.cloud import CloudHttpResponse

        self.calls.append((url, headers, timeout_seconds))
        token = self.tokens.pop(0)
        return CloudHttpResponse(200, json.dumps({"value": token}).encode())


def fake_jwt(exp: int) -> str:
    payload = base64.urlsafe_b64encode(
        json.dumps({"exp": exp}).encode()
    ).decode().rstrip("=")
    return f"header.{payload}.signature"


class AuditOidcTests(unittest.TestCase):
    def test_requests_audit_specific_audience_and_caches_until_near_expiry(self) -> None:
        now = [100.0]
        transport = FakeGetTransport([fake_jwt(1000), fake_jwt(2000)])
        provider = GithubAuditOidcTokenProvider(
            "https://actions.example/oidc?base=1",
            "request-token",
            transport=transport,
            clock=lambda: now[0],
        )

        first = provider.get_token()
        second = provider.get_token()
        self.assertEqual(first, second)
        self.assertEqual(len(transport.calls), 1)
        self.assertIn("audience=fmp-supabase-raw-audit", transport.calls[0][0])

        now[0] = 950.0
        refreshed = provider.get_token()
        self.assertNotEqual(refreshed, first)
        self.assertEqual(len(transport.calls), 2)


class CloudAuditClientTests(unittest.TestCase):
    def test_client_posts_canonical_batch_with_oidc(self) -> None:
        path = "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json"
        payload = {
            "status": "audited",
            "count": 1,
            "objects": [audit_manifest(path, {})],
        }
        transport = FakePostTransport(payload)
        client = SupabaseRawAuditClient(
            endpoint="https://example.supabase.co/functions/v1/fmp-raw-audit",
            token_provider=StaticTokenProvider(),
            transport=transport,
        )

        objects = client.audit_paths([path])

        self.assertEqual(len(objects), 1)
        _, body, headers, _ = transport.calls[0]
        self.assertEqual(json.loads(body), {"paths": [path]})
        self.assertEqual(headers["Authorization"], "Bearer oidc-token")

    def test_client_rejects_malformed_response(self) -> None:
        client = SupabaseRawAuditClient(
            endpoint="https://example.supabase.co/functions/v1/fmp-raw-audit",
            token_provider=StaticTokenProvider(),
            transport=FakePostTransport({"status": "audited", "count": 2, "objects": []}),
        )
        with self.assertRaises(CloudAuditError):
            client.audit_paths([
                "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json"
            ])


class CloudSnapshotVerifierTests(unittest.TestCase):
    def test_complete_and_not_found_manifests_verify(self) -> None:
        complete = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))
        not_found = RawChunkKey("EURUSD", "ASK", date(2024, 1, 6))
        complete_manifest_path = "manifests/" + complete.relative_manifest_path.as_posix()
        not_found_manifest_path = "manifests/" + not_found.relative_manifest_path.as_posix()
        raw_path = "raw/" + complete.relative_raw_path.as_posix()
        client = FakeAuditClient(
            {
                complete_manifest_path: audit_manifest(
                    complete_manifest_path, manifest_payload(complete)
                ),
                not_found_manifest_path: audit_manifest(
                    not_found_manifest_path, manifest_payload(not_found, status="not_found")
                ),
                raw_path: audit_raw(raw_path),
            }
        )

        report = verify_cloud_keys([complete, not_found], client, batch_size=100)

        self.assertTrue(report["ready"])
        self.assertEqual(report["planned_chunks"], 2)
        self.assertEqual(report["complete"], 1)
        self.assertEqual(report["not_found"], 1)
        self.assertEqual(report["issues"], 0)
        self.assertEqual(
            report["plan_sha256"],
            "1fef91c801d1d09c286cb3bf27cc5e75a8d261fa505dac3029224107cc27afa8",
        )
        reversed_report = verify_cloud_keys(
            [not_found, complete], FakeAuditClient(client.objects), batch_size=100
        )
        self.assertEqual(reversed_report["plan_sha256"], report["plan_sha256"])
        self.assertEqual(client.calls[0], [complete_manifest_path, not_found_manifest_path])
        self.assertEqual(client.calls[1], [raw_path])

    def test_raw_checksum_mismatch_fails_closed(self) -> None:
        key = RawChunkKey("USDJPY", "ASK", date(2025, 4, 2))
        manifest_path = "manifests/" + key.relative_manifest_path.as_posix()
        raw_path = "raw/" + key.relative_raw_path.as_posix()
        client = FakeAuditClient(
            {
                manifest_path: audit_manifest(manifest_path, manifest_payload(key)),
                raw_path: audit_raw(raw_path, sha256="c" * 64),
            }
        )

        report = verify_cloud_keys([key], client)

        self.assertFalse(report["ready"])
        self.assertEqual(report["raw_checksum_mismatch"], 1)

    def test_manifest_identity_mismatch_fails_closed_without_raw_request(self) -> None:
        key = RawChunkKey("GBPUSD", "BID", date(2023, 8, 8))
        manifest_path = "manifests/" + key.relative_manifest_path.as_posix()
        bad = manifest_payload(key)
        bad["pair"] = "EURUSD"
        client = FakeAuditClient(
            {manifest_path: audit_manifest(manifest_path, bad)}
        )

        report = verify_cloud_keys([key], client)

        self.assertFalse(report["ready"])
        self.assertEqual(report["invalid_manifest"], 1)
        self.assertEqual(len(client.calls), 1)


class FinalCloudAuditWorkflowTests(unittest.TestCase):
    def test_manual_workflow_is_source_free_and_persists_report(self) -> None:
        from pathlib import Path

        workflow = Path(".github/workflows/phase1-final-cloud-audit.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("schedule:", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("verify-cloud", workflow)
        self.assertIn("2015-01-01", workflow)
        self.assertIn("2026-08-21", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertIn("phase1-cloud-provenance.json", workflow)
        self.assertIn('for status in queued waiting pending in_progress; do', workflow)
        self.assertIn('runs?status=${status}&per_page=1', workflow)
        self.assertIn("active=$((active + count))", workflow)
        self.assertIn("id: acquisition-baseline", workflow)
        self.assertIn("latest_run_id=", workflow)
        self.assertIn("steps.acquisition-baseline.outputs.latest_run_id", workflow)
        self.assertIn("Refuse audit if acquisition changed during verification", workflow)
        self.assertGreaterEqual(
            workflow.count("actions/workflows/phase1-full-acquisition.yml/runs?per_page=1"),
            2,
        )


if __name__ == "__main__":
    unittest.main()
