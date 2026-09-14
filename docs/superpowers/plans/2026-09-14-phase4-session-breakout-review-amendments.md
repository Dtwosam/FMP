# Phase 4 Session-Breakout Plan Self-Review Amendments

This file is authoritative over `2026-09-14-phase4-session-breakout.md` where they differ. It records issues found during the required writing-plans self-review before any implementation begins.

## 1. Session continuity after incomplete-bar exclusion

The processed-data loader may exclude rows with `is_complete == false`, but the session strategy must never interpret the remaining subset as a complete session automatically.

For each London-local session date and configured timeframe `W`:

- range construction is eligible only when every expected bar label from 00:00 inclusive through 08:00 exclusive exists at exact `W` cadence;
- a breakout observed on label `T` is eligible only when every expected breakout-window label from 08:00 through `T` inclusive exists at exact `W` cadence, so a missing earlier bar cannot hide the true first breakout;
- a no-breakout `NO_TRADE` conclusion is valid only when every expected label from 08:00 inclusive through 12:00 exclusive exists;
- the 16:00 London-local scheduled-exit label must exist exactly;
- any failed continuity condition produces an explicit non-trade/rejection reason such as `INCOMPLETE_SESSION`, never a silently shortened range/window.

`tests/test_phase4_session_breakout.py` must cover one missing range bar, one missing pre-signal breakout bar, and one missing exact 16:00 exit bar.

## 2. True signal-known time for left-labelled bars

Phase 2 derived bars are left-labelled. For timeframe width `W`, a bar labelled `T` is not fully known until `T + W`.

`SignalCandidate` therefore includes both:

- `observation_bar_timestamp_utc = T`;
- `signal_known_timestamp_utc = T + W`.

The next supplied complete bar label used for execution must equal `signal_known_timestamp_utc`. The Phase 4 adapter keeps the accepted Phase 3 scheduling convention by setting `Decision.decision_timestamp_utc = T` and `earliest_executable_timestamp_utc = T + W`, while the candidate/benchmark evidence preserves the true known-at timestamp. `DEC-018` must document this bridge explicitly so it is auditable and cannot be mistaken for same-bar knowledge.

## 3. Exact research-reporting interface

Replace Task 6's metric signature with:

```python
def compute_research_metrics(
    run: BacktestRun,
    *,
    starting_equity_usd: float,
    requested_risk_fraction: float,
    candidate_metadata: Mapping[str, Mapping[str, object]],
    eligible_utc_dates: Sequence[date],
) -> dict[str, object]:
    ...
```

`candidate_metadata` is keyed by `decision_id` and supplies London session date/setup metadata for session breakdowns without changing `TradeRecord`.

Reward/risk per executed trade is:

`net_pnl_usd / (risk_equity_before_usd * requested_risk_fraction)`.

Daily realized return for UTC date `D` is:

`sum(net_pnl_usd for trades exiting on D) / risk_equity_at_start_of_D`.

`eligible_utc_dates` is the ordered set of UTC dates containing at least one loaded complete research bar; dates with zero realized PnL receive return `0.0`. Day-start equity rolls forward from prior realized PnL. Sharpe uses sample standard deviation of this daily series and annualization `sqrt(252)`; if fewer than two daily observations or zero standard deviation, Sharpe is `null`. Sortino uses the same mean and `sqrt(252)` divided by sample standard deviation of negative daily returns; if fewer than two negative daily observations or zero downside deviation, Sortino is `null`.

Tests must hand-calculate the daily series, Sharpe/Sortino null rules, reward/risk values, calendar-year grouping, and London-session grouping.

## 4. DEC-018 scope

Task 8's DEC-018 must freeze all of the following before the first serious experiment runs:

- development/validation/final date boundaries;
- final-test access lock;
- left-labelled bar timing bridge described above;
- session-breakout 9-point parameter grid;
- slippage scenarios 0.2/0.5/1.0 pips;
- zero commission/zero financing assumption for the mandatory-intraday-flat family;
- Phase 3 risk settings unchanged.

## 5. Source-free workflow download contract

Task 9's workflow uses the exact accepted Phase 2 artifact identities:

- EURUSD artifact `10325737935`, ZIP SHA-256 `db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3`;
- GBPUSD artifact `10326096831`, ZIP SHA-256 `fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2`;
- USDJPY artifact `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`.

Workflow permissions are exactly:

```yaml
permissions:
  contents: read
  actions: read
```

The download step sets `GH_TOKEN: ${{ github.token }}`, downloads `repos/${GITHUB_REPOSITORY}/actions/artifacts/<id>/zip`, recomputes SHA-256 before extraction, and fails closed on mismatch. The workflow has no `id-token`, Supabase call, source acquisition command, or raw-storage mutation.

These amendments close the plan's continuity, timing-audit, reporting-definition, decision-log, and artifact-download gaps. No implementation has started.