from __future__ import annotations

import base64
import hashlib
import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from fmp.data.cloud import CloudGetTransport, CloudHttpResponse, UrllibCloudTransport
from fmp.data.manifest import load_manifest, validate_manifest_for_key
from fmp.data.types import RawChunkKey

RAW_READ_OIDC_AUDIENCE = "fmp-supabase-raw-read"
RAW_READ_PROTOCOL = "fmp-raw-read-v1"


class RawChunkReader(Protocol):
    def read(self, key: RawChunkKey) -> bytes | None: ...


class RawReadError(RuntimeError):
    pass


class LocalRawChunkReader:
    def __init__(self, root: Path) -> None:
        self._root = Path(root)

    def read(self, key: RawChunkKey) -> bytes | None:
        raw_path = self._root / "raw" / key.relative_raw_path
        manifest_path = self._root / "manifests" / key.relative_manifest_path
        if not manifest_path.exists():
            raise RawReadError(f"missing Phase 1 manifest: {manifest_path}")

        try:
            manifest = load_manifest(manifest_path)
        except (OSError, ValueError) as exc:
            raise RawReadError(f"invalid Phase 1 manifest: {manifest_path}") from exc
        validated = validate_manifest_for_key(key, manifest)
        if validated is None:
            raise RawReadError(f"Phase 1 manifest failed validation: {manifest_path}")

        if validated.status == "not_found":
            if raw_path.exists():
                raise RawReadError(f"raw object present beside not_found manifest: {raw_path}")
            return None

        if validated.status != "complete":
            raise RawReadError(f"unsupported Phase 1 manifest status for local raw read: {validated.status}")
        if not raw_path.exists():
            raise RawReadError(f"missing Phase 1 raw object: {raw_path}")

        body = raw_path.read_bytes()
        if validated.compressed_size_bytes != len(body):
            raise RawReadError(f"Phase 1 raw size mismatch: {raw_path}")
        if validated.sha256 != hashlib.sha256(body).hexdigest():
            raise RawReadError(f"Phase 1 raw checksum mismatch: {raw_path}")
        return body


@dataclass(frozen=True, slots=True)
class CloudRawReadResponse:
    status: int
    body: bytes
    headers: dict[str, str]


class CloudRawReadPostTransport(Protocol):
    def post(
        self,
        url: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> CloudRawReadResponse: ...


class UrllibCloudRawReadTransport:
    def post(
        self,
        url: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> CloudRawReadResponse:
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                return CloudRawReadResponse(
                    int(response.status),
                    response.read(),
                    {str(k).lower(): str(v) for k, v in response.headers.items()},
                )
        except urllib.error.HTTPError as exc:
            return CloudRawReadResponse(
                int(exc.code),
                exc.read(),
                {str(k).lower(): str(v) for k, v in exc.headers.items()},
            )


def _validate_retry_settings(max_attempts: int, retry_delay_seconds: float) -> None:
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts <= 0:
        raise RawReadError("cloud raw read max attempts must be a positive integer")
    if (
        not isinstance(retry_delay_seconds, (int, float))
        or isinstance(retry_delay_seconds, bool)
        or not math.isfinite(retry_delay_seconds)
        or retry_delay_seconds < 0
    ):
        raise RawReadError("cloud raw read retry delay must be a finite non-negative number")


class GithubRawReadOidcTokenProvider:
    def __init__(
        self,
        request_url: str,
        request_token: str,
        *,
        transport: CloudGetTransport | None = None,
        timeout_seconds: float = 15.0,
        max_attempts: int = 3,
        retry_delay_seconds: float = 1.0,
        sleep_fn: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if not request_url or not request_token:
            raise RawReadError("GitHub OIDC request URL/token are required")
        _validate_retry_settings(max_attempts, retry_delay_seconds)
        self.request_url = request_url
        self.request_token = request_token
        self.transport = transport or UrllibCloudTransport()
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.sleep_fn = sleep_fn
        self.clock = clock
        self._cached_token: str | None = None
        self._cached_expiry: float | None = None

    @classmethod
    def from_environment(cls) -> "GithubRawReadOidcTokenProvider":
        return cls(
            os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", ""),
            os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", ""),
        )

    @staticmethod
    def _token_expiry(token: str) -> float | None:
        try:
            segment = token.split(".")[1]
            padding = "=" * (-len(segment) % 4)
            payload = json.loads(base64.urlsafe_b64decode(segment + padding).decode("utf-8"))
            expiry = payload.get("exp")
            if isinstance(expiry, (int, float)) and not isinstance(expiry, bool):
                return float(expiry)
        except (IndexError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
            return None
        return None

    def get_token(self) -> str:
        now = float(self.clock())
        if self._cached_token and self._cached_expiry is not None and now < self._cached_expiry - 60.0:
            return self._cached_token

        separator = "&" if "?" in self.request_url else "?"
        url = self.request_url + separator + urllib.parse.urlencode({"audience": RAW_READ_OIDC_AUDIENCE})
        headers = {"Authorization": f"Bearer {self.request_token}", "Accept": "application/json"}

        response: CloudHttpResponse | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.transport.get(url, headers, self.timeout_seconds)
            except (ConnectionError, TimeoutError, OSError) as exc:
                if attempt == self.max_attempts:
                    raise RawReadError(f"GitHub OIDC raw read token request failed after {self.max_attempts} attempts") from exc
                self.sleep_fn(self.retry_delay_seconds)
                continue
            if 200 <= response.status < 300:
                break
            transient = response.status == 429 or 500 <= response.status < 600
            if not transient:
                raise RawReadError(f"GitHub OIDC raw read token request failed with HTTP {response.status}")
            if attempt == self.max_attempts:
                raise RawReadError(f"GitHub OIDC raw read token request failed with HTTP {response.status} after {self.max_attempts} attempts")
            self.sleep_fn(self.retry_delay_seconds)

        assert response is not None
        try:
            value = json.loads(response.body.decode("utf-8"))["value"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise RawReadError("GitHub OIDC raw read token response was malformed") from exc
        if not isinstance(value, str) or not value:
            raise RawReadError("GitHub OIDC raw read token response did not contain a token")
        self._cached_token = value
        self._cached_expiry = self._token_expiry(value)
        return value


class CloudRawChunkReader:
    def __init__(
        self,
        endpoint: str,
        token_provider: Protocol,
        *,
        transport: CloudRawReadPostTransport | None = None,
        timeout_seconds: float = 30.0,
        max_attempts: int = 3,
        retry_delay_seconds: float = 1.0,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        if not endpoint.startswith("https://"):
            raise RawReadError("Supabase raw read endpoint must use HTTPS")
        _validate_retry_settings(max_attempts, retry_delay_seconds)
        self.endpoint = endpoint
        self.token_provider = token_provider
        self.transport = transport or UrllibCloudRawReadTransport()
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.sleep_fn = sleep_fn

    def read(self, key: RawChunkKey) -> bytes | None:
        token = self.token_provider.get_token()  # type: ignore[attr-defined]
        request_payload = {"pair": key.pair, "side": key.side, "date_utc": key.day.isoformat()}
        body = json.dumps(request_payload, separators=(",", ":")).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/octet-stream, application/json",
        }

        response: CloudRawReadResponse | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.transport.post(self.endpoint, body, headers, self.timeout_seconds)
            except (ConnectionError, TimeoutError, OSError) as exc:
                if attempt == self.max_attempts:
                    raise RawReadError(f"Supabase raw read failed after {self.max_attempts} attempts") from exc
                self.sleep_fn(self.retry_delay_seconds)
                continue
            transient = response.status == 429 or 500 <= response.status < 600
            if transient and attempt < self.max_attempts:
                self.sleep_fn(self.retry_delay_seconds)
                continue
            if transient:
                raise RawReadError(f"Supabase raw read failed with HTTP {response.status} after {self.max_attempts} attempts")
            break

        assert response is not None
        normalized_headers = {str(k).lower(): str(v) for k, v in response.headers.items()}

        if response.status == 404:
            return self._validate_not_found(key, response.body)
        if not 200 <= response.status < 300:
            raise RawReadError(f"Supabase raw read failed with HTTP {response.status}")
        return self._validate_complete(key, response.body, normalized_headers)

    @staticmethod
    def _validate_not_found(key: RawChunkKey, body: bytes) -> None:
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RawReadError("Supabase raw read not_found response was malformed") from exc
        expected = {
            "status": "not_found",
            "protocol": RAW_READ_PROTOCOL,
            "pair": key.pair,
            "side": key.side,
            "date_utc": key.day.isoformat(),
        }
        if payload != expected:
            raise RawReadError("Supabase raw read not_found identity/protocol mismatch")
        return None

    @staticmethod
    def _validate_complete(key: RawChunkKey, body: bytes, headers: dict[str, str]) -> bytes:
        if headers.get("content-type") != "application/octet-stream":
            raise RawReadError("Supabase raw read complete response content type was invalid")
        expected = {
            "x-fmp-protocol": RAW_READ_PROTOCOL,
            "x-fmp-pair": key.pair,
            "x-fmp-side": key.side,
            "x-fmp-date-utc": key.day.isoformat(),
            "x-fmp-manifest-status": "complete",
        }
        for name, value in expected.items():
            if headers.get(name) != value:
                raise RawReadError(f"Supabase raw read complete response {name} mismatch")
        digest = headers.get("x-fmp-sha256")
        size_value = headers.get("x-fmp-size-bytes")
        if digest is None or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise RawReadError("Supabase raw read complete response SHA-256 header was invalid")
        try:
            expected_size = int(size_value or "")
        except ValueError as exc:
            raise RawReadError("Supabase raw read complete response size header was invalid") from exc
        if expected_size <= 0 or expected_size != len(body):
            raise RawReadError("Supabase raw read complete response size mismatch")
        if hashlib.sha256(body).hexdigest() != digest:
            raise RawReadError("Supabase raw read complete response SHA-256 mismatch")
        return body
