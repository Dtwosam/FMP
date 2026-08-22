from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .types import RawChunkKey


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status: int
    body: bytes


class HttpTransport(Protocol):
    def get(self, url: str, timeout_seconds: float) -> HttpResponse: ...


class UrllibTransport:
    """Small standard-library transport so Phase 1 has no runtime dependency."""

    USER_AGENT = "FMP/0.1 (+https://github.com/Dtwosam/FMP)"

    def get(self, url: str, timeout_seconds: float) -> HttpResponse:
        request = Request(url, headers={"User-Agent": self.USER_AGENT, "Accept": "*/*"})
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                return HttpResponse(status=int(response.status), body=response.read())
        except HTTPError as exc:
            return HttpResponse(status=int(exc.code), body=exc.read())
        except URLError as exc:
            raise ConnectionError(str(exc.reason)) from exc


@dataclass(frozen=True, slots=True)
class DukascopySource:
    base_url: str = "https://datafeed.dukascopy.com/datafeed"

    def url_for(self, key: RawChunkKey) -> str:
        return (
            f"{self.base_url}/{key.pair}/{key.day.year:04d}/"
            f"{key.zero_based_month:02d}/{key.day.day:02d}/{key.filename}"
        )
