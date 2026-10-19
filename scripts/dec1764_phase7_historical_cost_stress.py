"""DEC-1764: replay *published Phase 7* adverse-slippage evidence offline.

This historical artifact has no market-data reads, broker integration, strategy
selection, forward performance claim, or execution authorization. An estimated
interpolation zero is NOT a live quote, observed break-even or trading gate.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import re
import stat
import sys


PHASE7_DOC = Path(__file__).resolve().parents[1] / "docs" / "phase7-walk-forward-evidence.md"
FROZEN_GIT_BLOB_SHA1 = "c1d8fe7f71681f2e06b472c77525a4dd800c896f"
FROZEN_PHASE7_DOC_SHA256 = "afe93d152e52c5a18b003967f97a411f2a1ac60dd54d913920536faa1863bb75"
PIPS = ("0.2", "0.5", "1.0")
EXPECTED_NET_RETURN_PCT = ("0.757266", "0.262176", "-0.562118")
EXPECTED_PNL_USD = ("757.27", "262.18", "-562.12")
EXPECTED_EXPECTANCY_USD = ("3.8054", "1.3175", "-2.8247")
EXPECTED_PROFIT_FACTOR = ("1.062731", "1.021310", "0.955760")

# Historic documentary claims only; none of these artifacts are downloaded,
# refreshed or independently reauthenticated by this static replay.
HISTORIC_STAGE2_PROVENANCE = {
    "stage1_survivor_artifact_id": "10414407590",
    "stage1_survivor_zip_sha256": "d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb",
    "phase2_processed_artifact_id": "10327600628",
    "phase2_processed_zip_sha256": "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72",
    "phase6_checkpoint_commit": "5d387b7ca93d04c498eb04c376e0dd92f1fe1953",
    "stage2_result_artifact_id": "10414817824",
    "stage2_result_zip_sha256": "2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4",
    "result_json_sha256": "ce7ef3f732bf2da7cd9c0df5e5d695dcdadd63e309c9428a6f572801fcb197b7",
    "windows_json_sha256": "66a1d35b12b68a0762dd98cd6838a2befcaf57ef9ae43bce181241fe4d23a4f0",
}

PHASE7_RUN = "35015277625"
STAGE2_SHA = "a1f8a0466463c79fdbceb9d6ebad9e3ea809474d"


def _require(ok, reason):
    if not ok:
        raise ValueError(reason)


def _signed_decimal(text, suffix=""):
    _require(isinstance(text, str), "numeric source must be string")
    if suffix:
        _require(text.endswith(suffix), "expected numeric unit " + suffix)
        text = text[:-len(suffix)]
    text = text.replace("$", "")
    try:
        value = Decimal(text)
    except Exception as exc:
        raise ValueError("invalid source numeric value") from exc
    _require(value.is_finite(), "non-finite historic metric")
    return value


MAX_PHASE7_DOCUMENT_BYTES = 65535


def _read_frozen_phase7_regular_file(path):
    """Use pinned directory FDs: never follow an ancestor or leaf symlink."""
    required = ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")
    _require(
        all(hasattr(os, name) for name in required)
        and os.open in os.supports_dir_fd,
        "this OS does not provide fail-closed source directory admission",
    )
    absolute = Path(os.path.abspath(os.fspath(path)))
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    if hasattr(os, "O_CLOEXEC"):
        directory_flags |= os.O_CLOEXEC
        file_flags |= os.O_CLOEXEC
    dirs = []
    try:
        dirs.append(os.open(absolute.anchor, directory_flags))
        for component in absolute.parts[1:-1]:
            dirs.append(os.open(component, directory_flags, dir_fd=dirs[-1]))
        with os.fdopen(os.open(absolute.name, file_flags, dir_fd=dirs[-1]), "rb") as handle:
            opened = os.fstat(handle.fileno())
            _require(
                stat.S_ISREG(opened.st_mode),
                "Phase7 evidence input must be a regular file",
            )
            _require(
                0 < opened.st_size <= MAX_PHASE7_DOCUMENT_BYTES,
                "Phase7 evidence input exceeds bounded source file limit",
            )
            payload = handle.read(MAX_PHASE7_DOCUMENT_BYTES + 1)
            _require(
                len(payload) == opened.st_size,
                "Phase7 source changed length during a bounded read",
            )
            return payload
    finally:
        for directory_fd in reversed(dirs):
            os.close(directory_fd)



# The exact period boundaries are documentary observations, not queries for
# market bars; validation cannot show that a historical runner observed them.
EXPECTED_SCORED_PERIODS = (
    ("2025-Q1", "2025-01-01", "2025-04-01"),
    ("2025-Q2", "2025-04-01", "2025-07-01"),
    ("2025-Q3", "2025-07-01", "2025-10-01"),
    ("2025-Q4", "2025-10-01", "2026-01-01"),
    ("2026-Q1", "2026-01-01", "2026-04-01"),
    ("2026-Q2", "2026-04-01", "2026-07-01"),
    ("2026-partial-Q3", "2026-07-01", "2026-08-21"),
)


def audit_published_window_schedule(windows):
    """Verify documentary period partitions and derive seven-day warm-ups.

    This does not inspect actual training data, labels, scored predictions or
    bar timestamps; it must not be called evidence of leak-free execution.
    """
    _require(
        type(windows) is list and len(windows) == len(EXPECTED_SCORED_PERIODS),
        "expected exactly seven published consecutive Phase7 periods",
    )
    audit = []
    previous_end = None
    for row, expected in zip(windows, EXPECTED_SCORED_PERIODS):
        _require(
            type(row) is dict and type(row.get("window")) is str
            and type(row.get("scored_range")) is str
            and row["window"] == expected[0],
            "published Phase7 window identity/order changed",
        )
        start = date.fromisoformat(expected[1])
        end = date.fromisoformat(expected[2])
        expected_range = f"{expected[1]} to {expected[2]} exclusive"
        _require(
            row["scored_range"] == expected_range
            and start < end
            and (previous_end is None or start == previous_end),
            "scored period cutoffs are missing, changed, overlapping or gapped",
        )
        warmup_start = start - timedelta(days=7)
        warmup_end = start
        _require(
            warmup_start < warmup_end and warmup_end <= start,
            "published warm-up must end before scored context begins",
        )
        audit.append({
            "window": row["window"],
            "scored_start_inclusive": start.isoformat(),
            "scored_end_exclusive": end.isoformat(),
            "reported_warmup_start_inclusive": warmup_start.isoformat(),
            "reported_warmup_end_exclusive": warmup_end.isoformat(),
            "warmup_calendar_days": 7,
            "reported_warmup_is_not_a_scored_period": True,
            "actual_bars_and_no_leakage_not_reauthenticated": True,
        })
        previous_end = end
    _require(
        audit[0]["scored_start_inclusive"] == "2025-01-01"
        and audit[-1]["scored_end_exclusive"] == "2026-08-21",
        "exact historical Stage2 coverage changed",
    )
    return audit


def replay_phase7_cost_evidence(doc_path: Path = PHASE7_DOC) -> dict[str, object]:
    raw = _read_frozen_phase7_regular_file(Path(doc_path))
    blob = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()
    _require(blob == FROZEN_GIT_BLOB_SHA1,
             "historic phase7 source differs from reviewed Git blob")
    source_sha256 = hashlib.sha256(raw).hexdigest()
    _require(
        source_sha256 == FROZEN_PHASE7_DOC_SHA256,
        "historic phase7 source differs from independently pinned SHA-256",
    )
    text = raw.decode("utf-8")
    for required in (
        "**Experiment:** `EXP-20260915-008`",
        "**Stage 2 code SHA:** `" + STAGE2_SHA + "`",
        "run `" + PHASE7_RUN + "`",
        "**Candidate:** USDJPY 15m `session_breakout`",
        "**Final Stage 2 status:** `PHASE7_PROMOTE_TO_SHADOW_DESIGN`",
        "The 1.0-pip diagnostic is negative",
    ):
        _require(required in text, "frozen historical evidence identity changed")

    for historical_claim in (
        "Stage 1 artifact `" + HISTORIC_STAGE2_PROVENANCE["stage1_survivor_artifact_id"]
            + "`, ZIP SHA-256 `" + HISTORIC_STAGE2_PROVENANCE["stage1_survivor_zip_sha256"] + "`",
        "Phase 2 USDJPY artifact `" + HISTORIC_STAGE2_PROVENANCE["phase2_processed_artifact_id"]
            + "`, ZIP SHA-256 `" + HISTORIC_STAGE2_PROVENANCE["phase2_processed_zip_sha256"] + "`",
        "`" + HISTORIC_STAGE2_PROVENANCE["phase6_checkpoint_commit"] + "`",
        "artifact `" + HISTORIC_STAGE2_PROVENANCE["stage2_result_artifact_id"] + "`",
        "ZIP SHA-256 is `" + HISTORIC_STAGE2_PROVENANCE["stage2_result_zip_sha256"] + "`",
        "SHA-256 `" + HISTORIC_STAGE2_PROVENANCE["result_json_sha256"] + "`",
        "SHA-256 `" + HISTORIC_STAGE2_PROVENANCE["windows_json_sha256"] + "`",
    ):
        _require(
            historical_claim in text,
            "frozen historical stage2 artifact lineage citation changed",
        )

    rows = [
        line for line in text.splitlines()
        if re.match(r"^\| (0\.2|0\.5|1\.0) pips \|", line)
    ]
    _require(len(rows) == 3, "historical cost table missing or duplicated")
    observations = []
    for index, line in enumerate(rows):
        cols = [item.strip() for item in line.strip("|").split("|")]
        _require(len(cols) == 9 and cols[0] == PIPS[index] + " pips",
                 "wrong historical cost table identity/order")
        net_pct = _signed_decimal(cols[1], "%")
        pnl_usd = _signed_decimal(cols[2])
        _require(re.fullmatch(r"[0-9]+", cols[3]) is not None,
                 "trade count must be an integer")
        trades = int(cols[3])
        expectancy = _signed_decimal(cols[4])
        profit_factor = _signed_decimal(cols[5])
        max_dd_pct = _signed_decimal(cols[6], "%")
        positive_windows = cols[7]
        positive_share_pct = _signed_decimal(cols[8], "%")
        _require(
            net_pct == Decimal(EXPECTED_NET_RETURN_PCT[index])
            and pnl_usd == Decimal(EXPECTED_PNL_USD[index])
            and trades == 199
            and expectancy == Decimal(EXPECTED_EXPECTANCY_USD[index])
            and profit_factor == Decimal(EXPECTED_PROFIT_FACTOR[index])
            and max_dd_pct >= 0
            and positive_windows in {"5 of 7", "4 of 7"}
            and 0 <= positive_share_pct <= 100,
            "published Phase 7 source values changed",
        )
        observations.append({
            "adverse_slippage_pips": str(Decimal(PIPS[index])),
            "historical_net_return_pct": str(net_pct),
            "historical_net_pnl_usd": str(pnl_usd),
            "trades": trades,
            "historical_expectancy_per_trade_usd": str(expectancy),
            "historical_profit_factor": str(profit_factor),
            "max_independent_window_drawdown_pct": str(max_dd_pct),
            "positive_windows": positive_windows,
            "max_positive_window_share_pct": str(positive_share_pct),
        })


    # Observed aggregate cost ladder only: never infer individual trades,
    # window-level costs, continuous slippage response or future fills.
    required_window_status = ("5 of 7", "4 of 7", "4 of 7")
    required_window_shares = ("35.061843", "39.223270", "49.394868")
    required_max_dd = ("1.140640", "1.170046", "1.219045")
    for index, row in enumerate(observations):
        _require(
            row["positive_windows"] == required_window_status[index]
            and Decimal(row["max_positive_window_share_pct"])
                == Decimal(required_window_shares[index])
            and Decimal(row["max_independent_window_drawdown_pct"])
                == Decimal(required_max_dd[index]),
            "published aggregate cost-window risk evidence changed",
        )
    historical_cost_changes = []
    for earlier, later in zip(observations, observations[1:]):
        return_delta = (
            Decimal(later["historical_net_return_pct"])
            - Decimal(earlier["historical_net_return_pct"])
        )
        pnl_delta = (
            Decimal(later["historical_net_pnl_usd"])
            - Decimal(earlier["historical_net_pnl_usd"])
        )
        expectancy_delta = (
            Decimal(later["historical_expectancy_per_trade_usd"])
            - Decimal(earlier["historical_expectancy_per_trade_usd"])
        )
        dd_increase = (
            Decimal(later["max_independent_window_drawdown_pct"])
            - Decimal(earlier["max_independent_window_drawdown_pct"])
        )
        share_increase = (
            Decimal(later["max_positive_window_share_pct"])
            - Decimal(earlier["max_positive_window_share_pct"])
        )
        _require(
            return_delta < 0 and pnl_delta < 0
            and expectancy_delta < 0 and dd_increase > 0
            and share_increase > 0,
            "published adverse-cost stress cannot imply improved economics",
        )
        historical_cost_changes.append({
            "from_reported_slippage_pips": earlier["adverse_slippage_pips"],
            "to_reported_slippage_pips": later["adverse_slippage_pips"],
            "observed_aggregate_return_change_percentage_points": str(return_delta),
            "observed_aggregate_pnl_change_usd": str(pnl_delta),
            "observed_expectancy_change_usd_per_trade": str(expectancy_delta),
            "observed_max_window_dd_increase_percentage_points": str(dd_increase),
            "observed_max_positive_window_share_change_percentage_points": str(
                share_increase),
        })
    _require(
        observations[0]["positive_windows"] == "5 of 7"
        and observations[1]["positive_windows"] == "4 of 7"
        and observations[2]["positive_windows"] == "4 of 7"
        and Decimal(observations[1]["historical_net_return_pct"]) > 0
        and Decimal(observations[2]["historical_net_return_pct"]) < 0
        and Decimal(observations[1]["historical_profit_factor"]) > 1
        and Decimal(observations[2]["historical_profit_factor"]) < 1,
        "positive-window support falls and profit-factor/return sign reverses",
    )

    # These are the published 0.2-pip benchmark subperiods, not fresh years
    # or independent prospective strategy tests. Retain losing windows.
    window_names = (
        "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4",
        "2026-Q1", "2026-Q2", "2026-partial-Q3",
    )
    window_lines = [
        line for line in text.splitlines()
        if re.match(
            r"^\| (?:2025-Q[1-4]|2026-Q[12]|2026-partial-Q3) \|",
            line,
        )
    ]
    _require(len(window_lines) == len(window_names),
             "published historical loss/win windows missing or duplicated")
    windows = []
    for index, line in enumerate(window_lines):
        parts = [col.strip() for col in line.strip("|").split("|")]
        _require(len(parts) == 8 and parts[0] == window_names[index],
                 "Phase7 window identity, order or evidence columns changed")
        _require(parts[1].endswith(" exclusive"),
                 "Phase7 window cutoff cannot be changed")
        ret = _signed_decimal(parts[2], "%")
        pnl = _signed_decimal(parts[3])
        _require(re.fullmatch(r"[0-9]+", parts[4]) is not None,
                 "window trade count must be a real integer")
        count = int(parts[4])
        expectancy = _signed_decimal(parts[5])
        factor = _signed_decimal(parts[6])
        drawdown = _signed_decimal(parts[7], "%")
        _require(count > 0 and drawdown >= 0 and factor >= 0,
                 "bad Phase7 window performance evidence")
        windows.append({
            "window": parts[0],
            "scored_range": parts[1],
            "historic_net_return_pct": str(ret),
            "historic_net_pnl_usd": str(pnl),
            "trades": count,
            "historic_expectancy_per_trade_usd": str(expectancy),
            "historic_profit_factor": str(factor),
            "historic_max_drawdown_pct": str(drawdown),
        })
    historical_schedule = audit_published_window_schedule(windows)
    _require(sum(w["trades"] for w in windows) == 199,
             "historical windows must reconcile to all 199 trades")
    ret_total = sum(
        (Decimal(w["historic_net_return_pct"]) for w in windows),
        Decimal("0"))
    # Source window/aggregate percentage values have published rounding.
    _require(abs(ret_total - Decimal("0.757266")) <= Decimal("0.00001"),
             "window returns do not reconcile with published aggregate")
    negatives = [
        w for w in windows
        if Decimal(w["historic_net_return_pct"]) < 0
    ]
    positives = [
        w for w in windows
        if Decimal(w["historic_net_return_pct"]) > 0
    ]
    _require(
        len(negatives) == 2
        and len(positives) == 5
        and [w["window"] for w in negatives]
            == ["2025-Q1", "2026-partial-Q3"]
        and Decimal(negatives[-1]["historic_net_return_pct"])
            == Decimal("-0.645978"),
        "historical failure windows must remain visible",
    )


    # Only the reported 0.2-pip seven-window PnLs permit this breakdown;
    # do not attribute it to the 0.5/1.0 pip aggregates or to live trading.
    positive_pnl = sum(
        (Decimal(w["historic_net_pnl_usd"]) for w in positives),
        Decimal("0"),
    )
    negative_pnl = sum(
        (Decimal(w["historic_net_pnl_usd"]) for w in negatives),
        Decimal("0"),
    )
    observed_net_pnl = positive_pnl + negative_pnl
    _require(
        positive_pnl > 0
        and negative_pnl < 0
        and observed_net_pnl == Decimal(EXPECTED_PNL_USD[0]),
        "0.2-pip source window PnL must reconcile exactly to published net",
    )
    gross_loss_as_share_of_gross_gain = (
        -negative_pnl / positive_pnl * Decimal(100)
    ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    largest_positive_pnl = max(
        Decimal(w["historic_net_pnl_usd"]) for w in positives
    )
    largest_positive_share = (
        largest_positive_pnl / positive_pnl * Decimal(100)
    ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    # Deterministic removal sensitivity on published rounded 0.2-pip window
    # PnLs. No resampling distribution, significance, inferred independence,
    # cost interpolation per window, forecast, or trading decision is implied.
    original_window_net = observed_net_pnl
    drop_one = [
        {
            "excluded_historical_window": row["window"],
            "remaining_rounded_window_pnl_usd": str(
                original_window_net - Decimal(row["historic_net_pnl_usd"])
            ),
        }
        for row in windows
    ]
    drop_two = [
        {
            "excluded_historical_windows": [left["window"], right["window"]],
            "remaining_rounded_window_pnl_usd": str(
                original_window_net
                - Decimal(left["historic_net_pnl_usd"])
                - Decimal(right["historic_net_pnl_usd"])
            ),
        }
        for left, right in combinations(windows, 2)
    ]
    _require(
        len(drop_one) == 7
        and len(drop_two) == 21,
        "all historical window exclusion combinations must be preserved",
    )
    worst_pair = min(
        drop_two,
        key=lambda row: Decimal(row["remaining_rounded_window_pnl_usd"]),
    )
    single_worst = min(
        drop_one,
        key=lambda row: Decimal(row["remaining_rounded_window_pnl_usd"]),
    )
    pair_loss_count = sum(
        Decimal(row["remaining_rounded_window_pnl_usd"]) < 0
        for row in drop_two
    )
    _require(
        worst_pair["excluded_historical_windows"] == ["2025-Q2", "2025-Q4"]
        and Decimal(worst_pair["remaining_rounded_window_pnl_usd"])
            == Decimal("-591.29")
        and single_worst["excluded_historical_window"] == "2025-Q4"
        and Decimal(single_worst["remaining_rounded_window_pnl_usd"])
            == Decimal("82.88")
        and pair_loss_count == 5,
        "historical cost-window exclusion concentration changed",
    )

    # Simple interpolation of two reported retrospective table endpoints.
    # Not a new empirical run or a usable predictive execution threshold.
    left = Decimal(PIPS[1])
    right = Decimal(PIPS[2])
    left_result = Decimal(EXPECTED_NET_RETURN_PCT[1])
    right_result = Decimal(EXPECTED_NET_RETURN_PCT[2])
    _require(left_result > 0 > right_result, "no historical sign reversal")
    zero = left + (Decimal(0) - left_result) * (
        right - left) / (right_result - left_result)
    _require(left < zero < right, "interpolated crossing outside observed bracket")
    slope01 = (Decimal(EXPECTED_NET_RETURN_PCT[1])
               - Decimal(EXPECTED_NET_RETURN_PCT[0])) / (
                   Decimal(PIPS[1]) - Decimal(PIPS[0]))
    slope12 = (right_result - left_result) / (right - left)
    _require(slope01 < 0 and slope12 < 0,
             "historical cost sensitivity must not be presented as improving")

    return {
        "schema": "fmp_dec1764_phase7_offline_cost_stress_replay_v1",
        "status": "RETROSPECTIVE_DIAGNOSTIC_NOT_EXECUTION_AUTHORITY",
        "source_file": "docs/phase7-walk-forward-evidence.md",
        "source_git_blob_sha1": blob,
        "source_document_sha256": source_sha256,
        "phase7_stage2_run": int(PHASE7_RUN),
        "phase7_stage2_code_sha": STAGE2_SHA,
        "published_historic_artifact_lineage": dict(HISTORIC_STAGE2_PROVENANCE),
        "historic_artifact_bytes_not_downloaded_or_reauthenticated": True,
        "external_current_provenance_witness": None,
        "historic_candidate": "USDJPY 15m session_breakout",
        "observations": observations,
        "historical_aggregate_cost_step_changes": historical_cost_changes,
        "historical_profitable_window_count_by_reported_slippage": [5, 4, 4],
        "historical_1_0_pip_return_and_profit_factor_below_zero_or_one": True,
        "no_unreported_slippage_or_per_window_costs_inferred": True,
        "historical_0_2_pip_windows": windows,
        "published_historical_window_schedule": historical_schedule,
        "historic_schedule_is_documentary_not_data_leakage_witness": True,
        "historical_negative_windows": [w["window"] for w in negatives],
        "historical_positive_window_count": len(positives),
        "historical_window_trade_count": sum(w["trades"] for w in windows),
        "historical_window_returns_sum_pct": str(ret_total),

        "historical_0_2_pip_pnl_attribution": {
            "gross_positive_window_pnl_usd": str(positive_pnl),
            "gross_negative_window_pnl_usd": str(negative_pnl),
            "net_window_pnl_usd": str(observed_net_pnl),
            "negative_pnl_as_pct_of_positive_pnl": str(gross_loss_as_share_of_gross_gain),
            "largest_positive_window_pnl_usd": str(largest_positive_pnl),
            "largest_positive_share_of_positive_pnl_pct": str(largest_positive_share),
            "independent_starting_equity_per_window_usd": "100000",
            "not_a_compounded_portfolio_return": True,
        },
        "historical_0_2_pip_leave_one_out": drop_one,
        "historical_0_2_pip_leave_two_out": drop_two,
        "historical_0_2_pip_leave_one_out_min": single_worst,
        "historical_0_2_pip_leave_two_out_min": worst_pair,
        "historical_0_2_pip_negative_after_two_exclusions_count": pair_loss_count,
        "historical_window_exclusion_is_not_statistical_validation": True,
        "historical_slippage_sign_reversal_bracket_pips": ["0.5", "1.0"],
        "linear_zero_interpolation_pips_not_observed": str(
            zero.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)),
        "historical_return_slope_pct_points_per_pip": [
            str(slope01), str(slope12)
        ],
        "caveat": "The interpolated zero is illustrative arithmetic between "
                  "historical published aggregate points, not an observed "
                  "fill-cost threshold, forecast, forward return, executable "
                  "strategy or approval; the Phase 7 result is not Strategy V1.",
        "phase8a_strategy_v1_edge_proven": False,
        "phase8a_strategy_v1_frozen": False,
        "forward_profit_claim": None,
        "protected_2023_run385_authorized": False,
        "shadow_or_demo_approved": False,
        "broker_order_authorized": False,
        "live_trading_authorized": False,
        "allowed_actions": [],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Offline historical Phase 7 cost stress replay; never authorization")
    parser.add_argument("--phase7-document", type=Path, default=PHASE7_DOC)
    args = parser.parse_args(argv)
    try:
        report = replay_phase7_cost_evidence(args.phase7_document)
    except (ValueError, OSError, UnicodeError, TypeError) as exc:
        print("BLOCKED: historic evidence could not be verified: " + str(exc),
              file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 3  # RETROSPECTIVE ONLY: nonzero to prevent shell gate confusion.


if __name__ == "__main__":
    raise SystemExit(main())
