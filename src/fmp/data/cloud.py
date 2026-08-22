from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .acquire import AcquisitionResult, AcquisitionStatus

OIDC_AUDIENCE = "fmp-supabase-raw-ingest"


class CloudMirrorError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class CloudHttpResponse:
    status: int
    body: bytes


class CloudGetTransport(Protocol):
    def get(
        self, url: str, headers: dict[str, str], timeout_seconds: float
    ) -> CloudHttpResponse: ...


class CloudPutTransport(Protocol):
    def put(
        self,
        url: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> CloudHttpResponse: ...


class UrllibCloudTransport:
    @staticmethod
    def _send(request: urllib.request.Request, timeout_seconds: float) -> CloudHttpResponse:
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                return CloudHttpResponse(int(response.status), response.read())
        except urllib.error.HTTPError as exc:
            return CloudHttpResponse(int(exc.code), exc.read())

    def get(
        self, url: str, headers: dict[str, str], timeout_seconds: float
    ) -> CloudHttpResponse:
        return self._send(urllib.request.Request(url, headers=headers, method="GET"), timeout_seconds)

    def put(
        self,
        url: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> CloudHttpResponse:
        return self._send(
            urllib.request.Request(url, data=body, headers=headers, method="PUT"),
            timeout_seconds,
        )


class GithubOidcTokenProvider:
    def __init__(
        self,
        request_url: str,
        request_token: str,
        *,
        transport: CloudGetTransport | None = None,
        timeout_seconds: float = 15.0,
    ) -> None:
        if not request_url or not request_token:
            raise CloudMirrorError("GitHub OIDC request URL/token are required")
        self.request_url = request_url
        self.request_token = request_token
        self.transport = transport or UrllibCloudTransport()
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_environment(cls) -> "GithubOidcTokenProvider":
        return cls(
            os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", ""),
            os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", ""),
        )

    def get_token(self) -> str:
        separator = "&" if "?" in self.request_url else "?"
        url = self.request_url + separator + urllib.parse.urlencode({"audience": OIDC_AUDIENCE})
        response = self.transport.get(
            url,
            {"Authorization": f"Bearer {self.request_token}", "Accept": "application/json"},
            self.timeout_seconds,
        )
        if not 200 <= response.status < 300:
            raise CloudMirrorError(f"GitHub OIDC token request failed with HTTP {response.status}")
        try:
            value = json.loads(response.body.decode("utf-8"))["value"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise CloudMirrorError("GitHub OIDC token response was malformed") from exc
        if not isinstance(value, str) or not value:
            raise CloudMirrorError("GitHub OIDC token response did not contain a token")
        return value


class SupabaseRawMirror:
    def __init__(
        self,
        endpoint: str,
        token_provider: GithubOidcTokenProvider | Protocol,
        *,
        transport: CloudPutTransport | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        if not endpoint.startswith("https://"):
            raise CloudMirrorError("Supabase ingest endpoint must use HTTPS")
        self.endpoint = endpoint
        self.token_provider = token_provider
        self.transport = transport or UrllibCloudTransport()
        self.timeout_seconds = timeout_seconds

    def put_object(self, object_path: str, body: bytes) -> str:
        digest = hashlib.sha256(body).hexdigest()
        token = self.token_provider.get_token()  # type: ignore[attr-defined]
        response = self.transport.put(
            self.endpoint,
            body,
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/octet-stream",
                "x-fmp-object-path": object_path,
                "x-fmp-sha256": digest,
            },
            self.timeout_seconds,
        )
        try:
            payload = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CloudMirrorError(
                f"Supabase raw mirror returned malformed HTTP {response.status} response"
            ) from exc
        status = payload.get("status") if isinstance(payload, dict) else None
        if 200 <= response.status < 300 and status in {"stored", "already_verified"}:
            return str(status)
        raise CloudMirrorError(
            f"Supabase raw mirror failed with HTTP {response.status}: {payload}"
        )


def mirror_acquisition_result(
    root: Path,
    result: AcquisitionResult,
    mirror: SupabaseRawMirror,
) -> list[str]:
    key = result.key
    mirrored: list[str] = []

    if result.status is not AcquisitionStatus.NOT_FOUND:
        raw_path = root / "raw" / key.relative_raw_path
        if not raw_path.is_file():
            raise CloudMirrorError(f"raw file missing before cloud mirror: {raw_path}")
        object_path = "raw/" + key.relative_raw_path.as_posix()
        mirror.put_object(object_path, raw_path.read_bytes())
        mirrored.append(object_path)

    manifest_path = root / "manifests" / key.relative_manifest_path
    if not manifest_path.is_file():
        raise CloudMirrorError(f"manifest missing before cloud mirror: {manifest_path}")
    manifest_object_path = "manifests/" + key.relative_manifest_path.as_posix()
    mirror.put_object(manifest_object_path, manifest_path.read_bytes())
    mirrored.append(manifest_object_path)
    return mirrored
