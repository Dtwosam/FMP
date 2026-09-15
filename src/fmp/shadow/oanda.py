from __future__ import annotations

import http.client
import re
from collections.abc import Iterator

from .contracts import (
    PRACTICE_STREAM_HOST,
    PRACTICE_STREAM_PATH_TEMPLATE,
    PROVIDER_INSTRUMENT,
)


_ACCOUNT_ID = re.compile(r"^[A-Za-z0-9-]{1,128}$")
_STREAM_QUERY = (
    f"instruments={PROVIDER_INSTRUMENT}&snapshot=true&includeHomeConversions=false"
)


class OandaPracticeStreamError(RuntimeError):
    """Fail-closed public error for the fixed Practice pricing stream."""


class OandaPracticePricingStream:
    __slots__ = ("_account_id", "_token")

    def __init__(self, *, account_id: str, token: str) -> None:
        if not isinstance(account_id, str) or not _ACCOUNT_ID.fullmatch(account_id):
            raise ValueError("account_id is invalid")
        if (
            not isinstance(token, str)
            or not token.strip()
            or "\r" in token
            or "\n" in token
        ):
            raise ValueError("token is invalid")
        self._account_id = account_id
        self._token = token

    def iter_lines(self) -> Iterator[bytes]:
        connection: http.client.HTTPSConnection | None = None
        response: http.client.HTTPResponse | None = None
        try:
            connection = http.client.HTTPSConnection(PRACTICE_STREAM_HOST)
            path = PRACTICE_STREAM_PATH_TEMPLATE.format(account_id=self._account_id)
            connection.request(
                "GET",
                f"{path}?{_STREAM_QUERY}",
                body=None,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Accept": "application/json",
                },
            )
            response = connection.getresponse()
            if response.status != 200:
                raise OandaPracticeStreamError(
                    f"OANDA Practice pricing stream returned HTTP {response.status}"
                )

            while True:
                line = response.readline()
                if not line:
                    break
                line = line.rstrip(b"\r\n")
                if line:
                    yield line
        except OandaPracticeStreamError:
            raise
        except Exception:
            raise OandaPracticeStreamError(
                "OANDA Practice pricing stream transport failed"
            ) from None
        finally:
            if response is not None:
                try:
                    response.close()
                except Exception:
                    pass
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass


__all__ = ["OandaPracticePricingStream", "OandaPracticeStreamError"]
