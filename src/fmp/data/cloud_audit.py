from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Any, Iterable, Protocol

from .cloud import CloudGetTransport, CloudHttpResponse, UrllibCloudTransport
from .dukascopy import DukascopySource
from .types import RawChunkKey

AUDIT_OIDC_AUDIENCE = "fmp-supabase-raw-audit"
AUDIT_PROTOCOL = "fmp-raw-audit-v1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_MANIFEST_FIELDS = {
    "manifest_version",
    "retrieval_method",
    "source",
    "source_url",
    "pair",
    "side",
    "date_utc",
    "granularity",
    "source_format",
    "record_size_bytes",
    "month_indexing",
    "status",
    "http_status",
    "sha256",
    "compressed_size_bytes",
    "records",
    "retrieved_at_utc",
}


class CloudAuditError(RuntimeError):
    pass


class CloudAuditPostTransport(Protocol):
    def post(
        self,
        url: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> CloudHttpResponse: ...


class UrllibCloudAuditTransport:
    @staticmethod
    def post(
        url: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> CloudHttpResponse:
        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                return CloudHttpResponse(int(response.status), response.read())
        except urllib.error.HTTPError as exc:
            return CloudHttpResponse(int(exc.code), exc.read())


class GithubAuditOidcTokenProvider:
    def __init__(
        self,
        request_url: str,
        request_token: str,
        *,
        transport: CloudGetTransport | None = None,
        timeout_seconds: float = 15.0,
        clock: callable = time.time,
    ) -> None:
        if not request_url or not request_token:
            raise CloudAuditError("GitHub OIDC request URL/token are required")
        self.request_url = request_url
        self.request_token = request_token
        self.transport = transport or UrllibCloudTransport()
        self.timeout_seconds = timeout_seconds
        self.clock = clock
        self._cached_token: str | None = None
        self._cached_expiry: float | None = None

    @classmethod
    def from_environment(cls) -> "GithubAuditOidcTokenProvider":
        return cls(
            os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", ""),
            os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", ""),
        )

    @staticmethod
    def _token_expiry(token: str) -> float | None:
        try:
            payload_segment = token.split(".")[1]
            padding = "=" * (-len(payload_segment) % 4)
            payload = json.loads(
                base64.urlsafe_b64decode(payload_segment + padding).decode("utf-8")
            )
            expiry = payload.get("exp")
            if isinstance(expiry, (int, float)) and not isinstance(expiry, bool):
                return float(expiry)
        except (IndexError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
            return None
        return None

    def get_token(self) -> str:
        now = float(self.clock())
        if (
            self._cached_token
            and self._cached_expiry is not None
            and now < self._cached_expiry - 60.0
        ):
            return self._cached_token

        separator = "&" if "?" in self.request_url else "?"
        url = self.request_url + separator + urllib.parse.urlencode(
            {"audience": AUDIT_OIDC_AUDIENCE}
        )
        response = self.transport.get(
            url,
            {
                "Authorization": f"Bearer {self.request_token}",
                "Accept": "application/json",
            },
            self.timeout_seconds,
        )
        if not 200 <= response.status < 300:
            raise CloudAuditError(
                f"GitHub OIDC audit token request failed with HTTP {response.status}"
            )
        try:
            value = json.loads(response.body.decode("utf-8"))["value"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise CloudAuditError("GitHub OIDC audit token response was malformed") from exc
        if not isinstance(value, str) or not value:
            raise CloudAuditError("GitHub OIDC audit token response did not contain a token")

        self._cached_token = value
        self._cached_expiry = self._token_expiry(value)
        return value


class SupabaseRawAuditClient:
    def __init__(
        self,
        endpoint: str,
        token_provider: Protocol,
        *,
        transport: CloudAuditPostTransport | None = None,
        get_transport: CloudGetTransport | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not endpoint.startswith("https://"):
            raise CloudAuditError("Supabase audit endpoint must use HTTPS")
        self.endpoint = endpoint
        self.token_provider = token_provider
        self.transport = transport or UrllibCloudAuditTransport()
        self.get_transport = get_transport or UrllibCloudTransport()
        self.timeout_seconds = timeout_seconds

    def preflight(self) -> None:
        token = self.token_provider.get_token()  # type: ignore[attr-defined]
        response = self.get_transport.get(
            self.endpoint,
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            self.timeout_seconds,
        )
        try:
            payload = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CloudAuditError(
                f"Supabase raw audit preflight returned malformed HTTP {response.status} response"
            ) from exc
        if (
            not 200 <= response.status < 300
            or not isinstance(payload, dict)
            or set(payload) != {"status", "protocol"}
            or payload.get("status") != "ready"
            or payload.get("protocol") != AUDIT_PROTOCOL
        ):
            raise CloudAuditError(
                f"Supabase raw audit preflight failed with HTTP {response.status}: {payload}"
            )

    def audit_paths(self, paths: list[str]) -> list[dict[str, object]]:
        if not 1 <= len(paths) <= 100:
            raise CloudAuditError("cloud audit batch must contain 1..100 paths")
        if len(set(paths)) != len(paths):
            raise CloudAuditError("cloud audit batch contains duplicate paths")

        token = self.token_provider.get_token()  # type: ignore[attr-defined]
        body = json.dumps({"paths": paths}, separators=(",", ":")).encode("utf-8")
        response = self.transport.post(
            self.endpoint,
            body,
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            self.timeout_seconds,
        )
        try:
            payload = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CloudAuditError(
                f"Supabase raw audit returned malformed HTTP {response.status} response"
            ) from exc

        if not 200 <= response.status < 300:
            raise CloudAuditError(
                f"Supabase raw audit failed with HTTP {response.status}: {payload}"
            )
        if not isinstance(payload, dict) or set(payload) != {"status", "count", "objects"}:
            raise CloudAuditError("Supabase raw audit response schema was invalid")
        if payload.get("status") != "audited":
            raise CloudAuditError("Supabase raw audit response status was invalid")
        objects = payload.get("objects")
        count = payload.get("count")
        if (
            not isinstance(count, int)
            or isinstance(count, bool)
            or not isinstance(objects, list)
            or count != len(paths)
            or len(objects) != len(paths)
        ):
            raise CloudAuditError("Supabase raw audit response count was invalid")

        validated: list[dict[str, object]] = []
        for expected_path, item in zip(paths, objects, strict=True):
            if not isinstance(item, dict):
                raise CloudAuditError("Supabase raw audit object was not a JSON object")
            expected_kind = "manifest" if expected_path.endswith(".json") else "raw"
            expected_fields = {"path", "kind", "sha256", "size_bytes"}
            if expected_kind == "manifest":
                expected_fields |= {"manifest_json", "manifest_parse_error"}
            if set(item) != expected_fields:
                raise CloudAuditError("Supabase raw audit object schema was invalid")
            if item.get("path") != expected_path:
                raise CloudAuditError("Supabase raw audit response path/order mismatch")
            if item.get("kind") != expected_kind:
                raise CloudAuditError("Supabase raw audit response kind mismatch")
            digest = item.get("sha256")
            size = item.get("size_bytes")
            if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
                raise CloudAuditError("Supabase raw audit response had invalid SHA-256")
            if not isinstance(size, int) or isinstance(size, bool) or size < 0:
                raise CloudAuditError("Supabase raw audit response had invalid size")
            if expected_kind == "manifest":
                parse_error = item.get("manifest_parse_error")
                manifest_json = item.get("manifest_json")
                if not isinstance(parse_error, bool):
                    raise CloudAuditError(
                        "Supabase raw audit manifest parse flag was invalid"
                    )
                if parse_error:
                    if manifest_json is not None:
                        raise CloudAuditError(
                            "Supabase raw audit malformed manifest response was inconsistent"
                        )
                elif not isinstance(manifest_json, dict):
                    raise CloudAuditError(
                        "Supabase raw audit parsed manifest response was invalid"
                    )
            validated.append(item)
        return validated


def _plan_sha256(keys: Iterable[RawChunkKey]) -> str:
    canonical = "\n".join(
        f"{key.day.isoformat()}|{key.pair}|{key.side}"
        for key in sorted(keys, key=lambda key: (key.day, key.pair, key.side))
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _iter_batches(items: list[str], batch_size: int) -> Iterable[list[str]]:
    for offset in range(0, len(items), batch_size):
        yield items[offset : offset + batch_size]


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() == timedelta(0)


def _validate_manifest(
    key: RawChunkKey,
    manifest: object,
) -> tuple[str, str | None, int | None] | None:
    if not isinstance(manifest, dict) or set(manifest) != _REQUIRED_MANIFEST_FIELDS:
        return None

    manifest_version = manifest.get("manifest_version")
    if (
        not isinstance(manifest_version, int)
        or isinstance(manifest_version, bool)
        or manifest_version != 1
    ):
        return None

    source = DukascopySource()
    fixed = {
        "retrieval_method": "dukascopy-public-daily-m1-bi5-v1",
        "source": "dukascopy",
        "source_url": source.url_for(key),
        "pair": key.pair,
        "side": key.side,
        "date_utc": key.day.isoformat(),
        "granularity": "1m",
        "source_format": "bi5-lzma-daily-candles",
        "record_size_bytes": 24,
        "month_indexing": "zero_based_in_source_url",
    }
    if any(manifest.get(field) != expected for field, expected in fixed.items()):
        return None
    if not _valid_timestamp(manifest.get("retrieved_at_utc")):
        return None

    status = manifest.get("status")
    http_status = manifest.get("http_status")
    sha256 = manifest.get("sha256")
    compressed_size = manifest.get("compressed_size_bytes")
    records = manifest.get("records")

    if status == "complete":
        if (
            not isinstance(http_status, int)
            or isinstance(http_status, bool)
            or not 200 <= http_status < 300
            or not isinstance(sha256, str)
            or not _SHA256_RE.fullmatch(sha256)
            or not isinstance(compressed_size, int)
            or isinstance(compressed_size, bool)
            or compressed_size <= 0
            or not isinstance(records, int)
            or isinstance(records, bool)
            or not 1 <= records <= 1440
        ):
            return None
        return ("complete", sha256, compressed_size)

    if status == "not_found":
        if http_status != 404 or sha256 is not None or compressed_size is not None or records is not None:
            return None
        return ("not_found", None, None)

    return None


def verify_cloud_keys(
    keys: Iterable[RawChunkKey],
    client: Protocol,
    *,
    batch_size: int = 100,
    issue_sample_limit: int = 20,
) -> dict[str, Any]:
    planned = list(keys)
    if not planned:
        raise ValueError("cloud verification requires at least one planned chunk")
    if len(set(planned)) != len(planned):
        raise ValueError("cloud verification plan contains duplicate chunks")
    if not 1 <= batch_size <= 100:
        raise ValueError("cloud audit batch_size must be between 1 and 100")

    counts = {
        "planned_chunks": len(planned),
        "complete": 0,
        "not_found": 0,
        "invalid_manifest": 0,
        "raw_checksum_mismatch": 0,
        "raw_size_mismatch": 0,
        "invalid_raw_audit": 0,
    }
    issue_samples: list[dict[str, str]] = []

    def add_issue(kind: str, key: RawChunkKey, detail: str) -> None:
        counts[kind] += 1
        if len(issue_samples) < issue_sample_limit:
            issue_samples.append(
                {
                    "kind": kind,
                    "pair": key.pair,
                    "side": key.side,
                    "date_utc": key.day.isoformat(),
                    "detail": detail,
                }
            )

    manifest_paths = ["manifests/" + key.relative_manifest_path.as_posix() for key in planned]
    manifest_objects: list[dict[str, object]] = []
    for batch in _iter_batches(manifest_paths, batch_size):
        manifest_objects.extend(client.audit_paths(batch))  # type: ignore[attr-defined]

    raw_expectations: list[tuple[RawChunkKey, str, str, int]] = []
    for key, expected_path, audited in zip(planned, manifest_paths, manifest_objects, strict=True):
        if audited.get("path") != expected_path or audited.get("kind") != "manifest":
            add_issue("invalid_manifest", key, "manifest audit identity mismatch")
            continue
        if audited.get("manifest_parse_error") is True:
            add_issue("invalid_manifest", key, "manifest JSON parse failure")
            continue
        validated = _validate_manifest(key, audited.get("manifest_json"))
        if validated is None:
            add_issue("invalid_manifest", key, "manifest schema/provenance mismatch")
            continue

        status, expected_sha, expected_size = validated
        if status == "not_found":
            counts["not_found"] += 1
            continue

        counts["complete"] += 1
        raw_path = "raw/" + key.relative_raw_path.as_posix()
        raw_expectations.append((key, raw_path, str(expected_sha), int(expected_size)))

    raw_paths = [item[1] for item in raw_expectations]
    raw_objects: list[dict[str, object]] = []
    for batch in _iter_batches(raw_paths, batch_size):
        raw_objects.extend(client.audit_paths(batch))  # type: ignore[attr-defined]

    for (key, expected_path, expected_sha, expected_size), audited in zip(
        raw_expectations, raw_objects, strict=True
    ):
        if audited.get("path") != expected_path or audited.get("kind") != "raw":
            add_issue("invalid_raw_audit", key, "raw audit identity mismatch")
            continue
        if audited.get("sha256") != expected_sha:
            add_issue("raw_checksum_mismatch", key, expected_path)
        if audited.get("size_bytes") != expected_size:
            add_issue("raw_size_mismatch", key, expected_path)

    issue_total = sum(
        counts[name]
        for name in (
            "invalid_manifest",
            "raw_checksum_mismatch",
            "raw_size_mismatch",
            "invalid_raw_audit",
        )
    )
    return {
        "report_version": 1,
        "source": "dukascopy",
        "granularity": "1m",
        "scope": "cloud_snapshot_provenance",
        "plan_sha256": _plan_sha256(planned),
        **counts,
        "issues": issue_total,
        "issue_samples": issue_samples,
        "ready": issue_total == 0
        and counts["complete"] + counts["not_found"] == counts["planned_chunks"],
        "note": (
            "Cloud provenance only: manifest schema/identity and raw SHA-256/size are verified. "
            "Phase 2 still determines quote/data cleanliness."
        ),
    }
