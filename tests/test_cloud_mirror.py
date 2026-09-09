from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from fmp.data.acquire import AcquisitionResult, AcquisitionStatus
from fmp.data.cli import build_parser, process_fetch_plan
from fmp.data.cloud import (
    CloudHttpResponse,
    CloudMirrorError,
    GithubOidcTokenProvider,
    SupabaseRawMirror,
    mirror_acquisition_result,
)
from fmp.data.types import RawChunkKey


class FakeGetTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str], float]] = []

    def get(self, url: str, headers: dict[str, str], timeout_seconds: float) -> CloudHttpResponse:
        self.calls.append((url, headers, timeout_seconds))
        return CloudHttpResponse(200, json.dumps({"value": "oidc-token"}).encode())


class SequencedGetTransport:
    def __init__(self, responses: list[CloudHttpResponse]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, dict[str, str], float]] = []

    def get(
        self, url: str, headers: dict[str, str], timeout_seconds: float
    ) -> CloudHttpResponse:
        self.calls.append((url, headers, timeout_seconds))
        if not self.responses:
            raise AssertionError("unexpected extra OIDC request")
        return self.responses.pop(0)


class FakePutTransport:
    def __init__(self, status: int = 201, response_status: str = "stored") -> None:
        self.status = status
        self.response_status = response_status
        self.calls: list[tuple[str, bytes, dict[str, str], float]] = []

    def put(
        self,
        url: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> CloudHttpResponse:
        self.calls.append((url, body, headers, timeout_seconds))
        return CloudHttpResponse(
            self.status,
            json.dumps({"status": self.response_status, "path": headers["x-fmp-object-path"]}).encode(),
        )


class FakeMirrorTransport(FakePutTransport):
    def __init__(
        self,
        *,
        get_status: int = 200,
        get_payload: dict[str, object] | None = None,
    ) -> None:
        super().__init__()
        self.get_status = get_status
        self.get_payload = get_payload or {
            "status": "ready",
            "protocol": "fmp-raw-ingest-v2",
        }
        self.get_calls: list[tuple[str, dict[str, str], float]] = []

    def get(
        self,
        url: str,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> CloudHttpResponse:
        self.get_calls.append((url, headers, timeout_seconds))
        return CloudHttpResponse(
            self.get_status,
            json.dumps(self.get_payload).encode(),
        )


class StaticTokenProvider:
    def get_token(self) -> str:
        return "oidc-token"


class FakeObjectMirror:
    def __init__(self) -> None:
        self.paths: list[str] = []

    def put_object(self, object_path: str, body: bytes) -> str:
        self.paths.append(object_path)
        return "stored"


class CloudMirrorTests(unittest.TestCase):
    def test_oidc_provider_requests_expected_audience_with_request_token(self) -> None:
        transport = FakeGetTransport()
        provider = GithubOidcTokenProvider(
            request_url="https://actions.example/oidc?base=1",
            request_token="request-token",
            transport=transport,
        )
        self.assertEqual(provider.get_token(), "oidc-token")
        self.assertEqual(len(transport.calls), 1)
        url, headers, timeout = transport.calls[0]
        self.assertIn("audience=fmp-supabase-raw-ingest", url)
        self.assertEqual(headers["Authorization"], "Bearer request-token")
        self.assertGreater(timeout, 0)

    def test_oidc_provider_retries_transient_503_then_succeeds(self) -> None:
        transport = SequencedGetTransport(
            [
                CloudHttpResponse(503, b'{"error":"temporary"}'),
                CloudHttpResponse(503, b'{"error":"temporary"}'),
                CloudHttpResponse(200, b'{"value":"oidc-token"}'),
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
        self.assertEqual(len(transport.calls), 3)
        self.assertEqual(sleeps, [0.25, 0.25])

    def test_oidc_provider_does_not_retry_auth_failure(self) -> None:
        transport = SequencedGetTransport(
            [
                CloudHttpResponse(401, b'{"error":"unauthorized"}'),
                CloudHttpResponse(200, b'{"value":"must-not-be-used"}'),
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

        with self.assertRaisesRegex(CloudMirrorError, "HTTP 401"):
            provider.get_token()

        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(sleeps, [])

    def test_oidc_provider_fails_after_bounded_transient_retries(self) -> None:
        transport = SequencedGetTransport(
            [
                CloudHttpResponse(503, b'{}'),
                CloudHttpResponse(503, b'{}'),
                CloudHttpResponse(503, b'{}'),
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

        with self.assertRaisesRegex(CloudMirrorError, "after 3 attempts"):
            provider.get_token()

        self.assertEqual(len(transport.calls), 3)
        self.assertEqual(sleeps, [0.25, 0.25])

    def test_ingest_preflight_accepts_expected_protocol(self) -> None:
        transport = FakeMirrorTransport()
        mirror = SupabaseRawMirror(
            endpoint="https://example.supabase.co/functions/v1/fmp-raw-ingest",
            token_provider=StaticTokenProvider(),
            transport=transport,
        )

        mirror.preflight()

        self.assertEqual(len(transport.get_calls), 1)
        _, headers, _ = transport.get_calls[0]
        self.assertEqual(headers["Authorization"], "Bearer oidc-token")

    def test_ingest_preflight_rejects_old_endpoint_before_source(self) -> None:
        transport = FakeMirrorTransport(
            get_status=405,
            get_payload={"error": "method_not_allowed"},
        )
        mirror = SupabaseRawMirror(
            endpoint="https://example.supabase.co/functions/v1/fmp-raw-ingest",
            token_provider=StaticTokenProvider(),
            transport=transport,
        )

        with self.assertRaisesRegex(CloudMirrorError, "preflight"):
            mirror.preflight()

    def test_cli_runs_ingest_preflight_before_source(self) -> None:
        args = build_parser().parse_args(
            [
                "fetch",
                "--pair",
                "EURUSD",
                "--start",
                "2024-01-01",
                "--end",
                "2024-01-02",
                "--out",
                ".phase1-preflight",
                "--mirror-url",
                "https://example.supabase.co/functions/v1/fmp-raw-ingest",
            ]
        )

        with (
            patch(
                "fmp.data.cli.GithubOidcTokenProvider.from_environment",
                return_value=StaticTokenProvider(),
            ),
            patch(
                "fmp.data.cli.SupabaseRawMirror.preflight",
                side_effect=CloudMirrorError("ingest preflight failed"),
            ) as preflight,
            patch("fmp.data.cli.acquire_chunk") as acquire,
        ):
            with self.assertRaisesRegex(CloudMirrorError, "preflight"):
                args.func(args)

        preflight.assert_called_once_with()
        acquire.assert_not_called()

    def test_put_object_sends_path_checksum_and_oidc_token(self) -> None:
        transport = FakePutTransport()
        mirror = SupabaseRawMirror(
            endpoint="https://example.supabase.co/functions/v1/fmp-raw-ingest",
            token_provider=StaticTokenProvider(),
            transport=transport,
        )
        body = b"immutable bytes"
        result = mirror.put_object("raw/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.bi5", body)
        self.assertEqual(result, "stored")
        _, sent_body, headers, _ = transport.calls[0]
        self.assertEqual(sent_body, body)
        self.assertEqual(headers["Authorization"], "Bearer oidc-token")
        self.assertEqual(headers["x-fmp-sha256"], hashlib.sha256(body).hexdigest())

    def test_already_verified_is_success(self) -> None:
        mirror = SupabaseRawMirror(
            endpoint="https://example.supabase.co/functions/v1/fmp-raw-ingest",
            token_provider=StaticTokenProvider(),
            transport=FakePutTransport(status=200, response_status="already_verified"),
        )
        self.assertEqual(
            mirror.put_object("manifests/dukascopy/v1/USDJPY/2024/00/02/ASK_candles_min_1.json", b"{}"),
            "already_verified",
        )

    def test_not_found_acquisition_mirrors_manifest_only(self) -> None:
        key = RawChunkKey("GBPUSD", "ASK", date(2024, 1, 6))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifests" / key.relative_manifest_path
            manifest.parent.mkdir(parents=True)
            manifest.write_text('{"status":"not_found"}\n')
            transport = FakePutTransport()
            mirror = SupabaseRawMirror(
                endpoint="https://example.supabase.co/functions/v1/fmp-raw-ingest",
                token_provider=StaticTokenProvider(),
                transport=transport,
            )
            result = AcquisitionResult(key, AcquisitionStatus.NOT_FOUND, None, None, None, 404)
            mirrored = mirror_acquisition_result(root, result, mirror)
            self.assertEqual(mirrored, ["manifests/" + key.relative_manifest_path.as_posix()])
            self.assertEqual(len(transport.calls), 1)

    def test_raw_conflict_aborts_before_manifest_upload(self) -> None:
        key = RawChunkKey("USDJPY", "BID", date(2022, 12, 17))
        raw_object = "raw/" + key.relative_raw_path.as_posix()
        manifest_object = "manifests/" + key.relative_manifest_path.as_posix()

        class RawConflictMirror:
            def __init__(self) -> None:
                self.paths: list[str] = []

            def put_object(self, object_path: str, body: bytes) -> str:
                self.paths.append(object_path)
                if object_path == raw_object:
                    raise CloudMirrorError("immutable raw conflict")
                if object_path == manifest_object:
                    raise AssertionError("manifest must not be uploaded after raw conflict")
                raise AssertionError(f"unexpected object path: {object_path}")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_path = root / "raw" / key.relative_raw_path
            manifest_path = root / "manifests" / key.relative_manifest_path
            raw_path.parent.mkdir(parents=True)
            manifest_path.parent.mkdir(parents=True)
            raw_path.write_bytes(b"refetched raw")
            manifest_path.write_bytes(b'{"status":"complete"}\n')
            result = AcquisitionResult(
                key,
                AcquisitionStatus.COMPLETE,
                "x",
                1,
                len(b"refetched raw"),
                200,
            )
            mirror = RawConflictMirror()

            with self.assertRaisesRegex(CloudMirrorError, "immutable raw conflict"):
                mirror_acquisition_result(root, result, mirror)

            self.assertEqual(mirror.paths, [raw_object])

    def test_fetch_plan_mirrors_result_before_advancing(self) -> None:
        key = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))
        mirror = FakeObjectMirror()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def fake_acquire(planned_key: RawChunkKey, planned_root: Path) -> AcquisitionResult:
                self.assertEqual(planned_key, key)
                raw = planned_root / "raw" / key.relative_raw_path
                manifest = planned_root / "manifests" / key.relative_manifest_path
                raw.parent.mkdir(parents=True)
                manifest.parent.mkdir(parents=True)
                raw.write_bytes(b"raw")
                manifest.write_bytes(b"manifest")
                return AcquisitionResult(key, AcquisitionStatus.COMPLETE, "x", 1, 3, 200)

            results = process_fetch_plan([key], root, fake_acquire, mirror)
            self.assertEqual(len(results), 1)
            self.assertEqual(
                mirror.paths,
                [
                    "raw/" + key.relative_raw_path.as_posix(),
                    "manifests/" + key.relative_manifest_path.as_posix(),
                ],
            )

    def test_fetch_plan_applies_delay_between_source_chunks(self) -> None:
        keys = [
            RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
            RawChunkKey("EURUSD", "ASK", date(2024, 1, 2)),
        ]
        sleeps: list[float] = []

        def fake_acquire(key: RawChunkKey, root: Path) -> AcquisitionResult:
            return AcquisitionResult(key, AcquisitionStatus.COMPLETE, "x", 1, 1, 200)

        with tempfile.TemporaryDirectory() as tmp:
            results = process_fetch_plan(
                keys,
                Path(tmp),
                fake_acquire,
                source_delay_seconds=2.5,
                sleep_fn=sleeps.append,
            )

        self.assertEqual(len(results), 2)
        self.assertEqual(sleeps, [2.5])

    def test_cloud_mirrored_recheck_not_found_fails_before_oidc_or_source(self) -> None:
        args = build_parser().parse_args(
            [
                "fetch",
                "--pair",
                "EURUSD",
                "--start",
                "2024-01-01",
                "--end",
                "2024-01-02",
                "--out",
                ".phase1-recheck",
                "--mirror-url",
                "https://example.supabase.co/functions/v1/fmp-raw-ingest",
                "--recheck-not-found",
            ]
        )

        with (
            patch("fmp.data.cli.GithubOidcTokenProvider.from_environment") as oidc,
            patch("fmp.data.cli.acquire_chunk") as acquire,
        ):
            with self.assertRaisesRegex(ValueError, "cloud-mirrored"):
                args.func(args)

        oidc.assert_not_called()
        acquire.assert_not_called()

    def test_fetch_parser_accepts_source_delay(self) -> None:
        args = build_parser().parse_args(
            [
                "fetch",
                "--pair",
                "EURUSD",
                "--start",
                "2024-01-01",
                "--end",
                "2024-01-02",
                "--source-delay",
                "2.5",
            ]
        )
        self.assertEqual(args.source_delay, 2.5)


if __name__ == "__main__":
    unittest.main()
