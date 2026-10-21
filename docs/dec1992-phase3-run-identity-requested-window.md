# DEC-1992 — Optional source requested-interval integrity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2240 at `11d9b95a6eea4cae1f8b589950321e293a009038`.

The Phase3 engine's BacktestConfig requires two UTC request endpoints and refuses `requested_end_utc < requested_start_utc`; its source run identity serializes both datetimes in writer-canonical ISO `Z` form. The read-only artifact auditor checked stored trades/rejections/checkpoints chronology, but had no equivalent consistency checks on the reported requested interval in summary.run_identity.

If either source request endpoint is included, require both, parse each as exact writer-canonical UTC, and reject a requested end earlier than requested start. Preserve valid synthetic reporting evidence without either optional field, and do not infer that trade prices, market data or upstream provenance are authenticated by self-consistent source windows.

Four synthetic source-defined methods cover valid source window, self-rehashed backdated end, noncanonical UTC spelling and missing one endpoint. **7,071 cumulative proposed methods** (+4). Source-only; own Phase3 and full historical/general CI required, previous failures remain FAILED, full CI unverified at proposal time.

Phase8A #779/#820/#821 eight independent external proofs unresolved. No protected 2023/run385/attempt1 research, broker/demo/live orders, strategy promotion, installed GitHub runner/ref/workflow mutation, merge or real funds.
