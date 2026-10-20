# DEC-1914 — Canonical metric-source trade and checkpoint admission

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of PR #2162 at `81629cb0040d83752da84d221db520325fe566ad`.

The Phase3 `compute_backtest_metrics` path previously assumed that the supplied trade and equity-checkpoint sequences and financial fields were canonical. Untyped records could call hostile getters or raise incidental Python errors, and Boolean trade costs or PnL could silently count as 1. Require ordinary list/tuple of exact `TradeRecord` and `EquityCheckpoint` values. Validate finite built-in numeric net PnL, slippage, commission and financing costs (slippage/commission nonnegative, financing credit still permitted), and typed UTC checkpoint timestamps / finite equity before computing metrics. Existing chronological ordering and aggregate finiteness checks are preserved.

Three synthetic regression methods cover malformed collections and hostile members, untyped/nonfinite/negative financial costs with the permitted credit control, and malformed checkpoint values. **6,907 cumulative proposed source-defined methods.** Own exact-head Phase3 and historical/general CI, qualified financial evidence review required, and no parent check inherited.

Phase8A security blockers #779/#820/#821 and eight independent administrator/ref/runner/provenance/fresh inventory/human proofs remain MISSING. Protected 2023/run385/attempt1, later discovery, Strategy V1 economics, shadow/demo/Phase10/11, installed workflow/ref/ruleset/runner changes and broker/live capital still BLOCKED. No protected data, dispatch, trade or profit claim.
