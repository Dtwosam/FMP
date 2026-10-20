# DEC-1906 — Fail-closed RiskConfig preflight for realized PnL

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs commit on #2154 at `72342af4dde8254cf8096ea1750a8b83abc7a069`.

`record_realized_pnl` previously applied realized-equity and UTC-day mutations before reading `config.daily_loss_halt_fraction`. A non-`RiskConfig` object could therefore trigger an incidental AttributeError or an arbitrary property getter **after** partially updating risk state. Require the exact validated `RiskConfig` dataclass before any state mutation. Preserve valid configured realized PnL and daily loss halt behavior, including existing UTC and finite-PnL guards.

Two synthetic regression tests reject malformed config types and hostile getter objects, confirming that risk equity, UTC date, daily realized PnL, reservations and halt flags are unchanged. **6,884 cumulative proposed source-defined tests.** Own exact-head Phase3/full historical-general CI and independent risk review remain required; previous-head successes are not evidence for this SHA.

Phase 8A remains BLOCKED pending all eight independent security proofs and #779/#820/#821. The protected 2023/run385/attempt1 annual unit, future research, Strategy V1 economics, shadow, demo, Phase10/11 and any broker/live funds remain unauthorized. No protected run, file/network workflow, installed GitHub control or trading activity was performed.
