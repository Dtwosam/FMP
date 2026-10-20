# DEC-1909 — Canonical risk-state public API admission

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child #2157 at `c1e88e10c44f418786e84c083fb86e0aa8f14d23`.

Risk-policy entry points `roll_utc_day`, `reserve_risk`, `release_risk` and `record_realized_pnl` previously trusted that callers had supplied a real `RiskState`. A malformed, subclassed or hostile object could produce an incidental AttributeError or invoke arbitrary property getters during risk-day management, reservations or realized PnL. Require the exact validated `RiskState` dataclass before dereferencing state fields, preserving the existing validated UTC, ID and config precedence.

Three synthetic regression methods cover null/opaque/container/hostile state inputs with refused attribute getters, and valid original risk state operations (reservation/release and realized PnL) remaining unchanged. Total **6,892 cumulative proposed source-defined test methods**. Exact-head Phase3/full historical-general CI and independent review are required; local tests do not prove runner sandboxing or positive strategy expectancy.

Phase8A remains BLOCKED by #779/#820/#821 and eight independent administrator/ref/source/runner OS/provenance/fresh one-shot/human proof packages. Protected 2023/run385/attempt1, later annual research, Strategy V1 economics, shadow/demo, Phase10/11 and live trading or funds remain forbidden. No protected run, installed GitHub workflow/ref/ruleset/runner modification, broker order or money action.
