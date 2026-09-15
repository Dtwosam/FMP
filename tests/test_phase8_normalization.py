from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import unittest

from fmp.shadow import HeartbeatEvent, NormalizedQuote
from fmp.shadow.normalization import (
    ProviderMessageError,
    StreamSegmentNormalizer,
    normalize_provider_message,
)
from fmp.shadow.oanda import OandaPracticeStreamError, parse_provider_line


UTC = timezone.utc
RECEIVED = datetime(2026, 9, 15, 12, 0, 0, 100_000, tzinfo=UTC)


def price_message(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "type": "PRICE",
        "time": "2026-09-15T12:00:00.000000000Z",
        "instrument": "USD_JPY",
        "tradeable": True,
        "bids": [
            {"price": "140.001", "liquidity": 10_000_000},
            {"price": "140.003", "liquidity": 1},
            {"price": "140.002", "liquidity": 50},
        ],
        "asks": [
            {"price": "140.008", "liquidity": 1},
            {"price": "140.006", "liquidity": 10_000_000},
            {"price": "140.007", "liquidity": 50},
        ],
        "unitsAvailable": {"default": {"long": "999", "short": "999"}},
        "closeoutBid": "1",
        "closeoutAsk": "2",
    }
    value.update(overrides)
    return value


class Phase8NormalizationTests(unittest.TestCase):
    def test_parse_provider_line_requires_json_object_without_echoing_payload(self) -> None:
        parsed = parse_provider_line(b'{"type":"HEARTBEAT","time":"2026-09-15T12:00:00Z"}')
        self.assertEqual(parsed["type"], "HEARTBEAT")
        for invalid in (b"not-json", b"[]", b'"secret-token"'):
            with self.subTest(invalid=invalid), self.assertRaises(OandaPracticeStreamError) as caught:
                parse_provider_line(invalid)
            self.assertEqual(str(caught.exception), "OANDA Practice stream message is invalid")
            self.assertNotIn("secret-token", str(caught.exception))

    def test_price_selects_best_sides_without_trusting_ladder_order_or_liquidity(self) -> None:
        event = normalize_provider_message(
            price_message(),
            received_at_utc=RECEIVED,
            receive_monotonic_ns=100,
        )
        self.assertIsInstance(event, NormalizedQuote)
        assert isinstance(event, NormalizedQuote)
        self.assertEqual(event.symbol, "USDJPY")
        self.assertEqual(event.bid, 140.003)
        self.assertEqual(event.ask, 140.006)
        self.assertTrue(event.tradeable)
        self.assertEqual(
            event.source_time_utc,
            datetime(2026, 9, 15, 12, 0, tzinfo=UTC),
        )
        self.assertFalse(hasattr(event, "liquidity"))
        self.assertFalse(hasattr(event, "unitsAvailable"))
        self.assertFalse(hasattr(event, "closeoutBid"))

    def test_nontradeable_price_is_preserved_as_nonexecutable_quote(self) -> None:
        event = normalize_provider_message(
            price_message(tradeable=False),
            received_at_utc=RECEIVED,
            receive_monotonic_ns=101,
        )
        self.assertIsInstance(event, NormalizedQuote)
        assert isinstance(event, NormalizedQuote)
        self.assertFalse(event.tradeable)

    def test_heartbeat_has_only_timing_metadata(self) -> None:
        event = normalize_provider_message(
            {
                "type": "HEARTBEAT",
                "time": "2026-09-15T12:00:05Z",
                "account_id": "101-001-secret",
                "token": "secret-token",
            },
            received_at_utc=RECEIVED,
            receive_monotonic_ns=102,
        )
        self.assertIsInstance(event, HeartbeatEvent)
        self.assertNotIn("secret", repr(event))

    def test_unknown_or_malformed_message_types_fail_closed(self) -> None:
        for raw in (
            {},
            {"type": "ORDER", "time": "2026-09-15T12:00:00Z"},
            {"type": 1, "time": "2026-09-15T12:00:00Z"},
        ):
            with self.subTest(raw=raw), self.assertRaises(ProviderMessageError):
                normalize_provider_message(
                    raw,
                    received_at_utc=RECEIVED,
                    receive_monotonic_ns=103,
                )

    def test_wrong_instrument_invalid_sides_and_crossed_quote_fail_closed(self) -> None:
        invalid = (
            price_message(instrument="EUR_USD"),
            price_message(bids=[]),
            price_message(asks=[]),
            price_message(bids=[{"price": "0"}]),
            price_message(asks=[{"price": str(math.inf)}]),
            price_message(bids=[{"price": "nan"}]),
            price_message(
                bids=[{"price": "140.010"}],
                asks=[{"price": "140.009"}],
            ),
            price_message(bids=[{"liquidity": 1}]),
            price_message(asks="not-a-ladder"),
            price_message(tradeable="true"),
        )
        for raw in invalid:
            with self.subTest(raw=raw), self.assertRaises(ProviderMessageError):
                normalize_provider_message(
                    raw,
                    received_at_utc=RECEIVED,
                    receive_monotonic_ns=104,
                )

    def test_provider_timestamp_must_be_utc(self) -> None:
        for value in (
            "2026-09-15T13:00:00+01:00",
            "2026-09-15T12:00:00",
            "not-a-time",
            123,
        ):
            with self.subTest(value=value), self.assertRaises(ProviderMessageError):
                normalize_provider_message(
                    price_message(time=value),
                    received_at_utc=RECEIVED,
                    receive_monotonic_ns=105,
                )

    def test_segment_fails_on_source_time_regression(self) -> None:
        segment = StreamSegmentNormalizer()
        segment.accept(
            price_message(time="2026-09-15T12:00:05Z"),
            received_at_utc=RECEIVED,
            receive_monotonic_ns=200,
        )
        with self.assertRaises(ProviderMessageError):
            segment.accept(
                price_message(time="2026-09-15T12:00:04Z"),
                received_at_utc=RECEIVED + timedelta(milliseconds=1),
                receive_monotonic_ns=201,
            )

    def test_exact_duplicate_price_dedupes_but_conflicting_duplicate_fails(self) -> None:
        segment = StreamSegmentNormalizer()
        first = segment.accept(
            price_message(),
            received_at_utc=RECEIVED,
            receive_monotonic_ns=300,
        )
        duplicate = segment.accept(
            price_message(),
            received_at_utc=RECEIVED + timedelta(milliseconds=1),
            receive_monotonic_ns=301,
        )
        self.assertIsInstance(first, NormalizedQuote)
        self.assertIsNone(duplicate)

        with self.assertRaises(ProviderMessageError):
            segment.accept(
                price_message(bids=[{"price": "140.004"}]),
                received_at_utc=RECEIVED + timedelta(milliseconds=2),
                receive_monotonic_ns=302,
            )

    def test_error_text_and_normalized_output_never_preserve_secret_extra_fields(self) -> None:
        raw = price_message(
            instrument="WRONG",
            token="secret-token",
            account_id="101-001-secret",
        )
        with self.assertRaises(ProviderMessageError) as caught:
            normalize_provider_message(
                raw,
                received_at_utc=RECEIVED,
                receive_monotonic_ns=400,
            )
        self.assertNotIn("secret-token", str(caught.exception))
        self.assertNotIn("101-001-secret", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
