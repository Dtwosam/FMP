# DEC-1930 — Exact allowed enums and datetimes in deterministic artifact JSON

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit source/tests/docs child of PR #2178 at `ee6fc92e444bd3c6b8fb18b67ab376b1766c8cfa`.

The deterministic serializer previously accepted arbitrary caller-defined `Enum` and datetime-subclass objects in `run_identity` and `metrics`, including unvalidated enum member values and overridden datetime methods. Only canonical `Direction`, `ExitReason`, `RejectionCode` enums are now unwrapped and recursively checked; unsupported enums and datetime subclasses are refused with controlled `ValueError` before output directory creation. Genuine builtin UTC datetime and source-defined enum serialization remain compatible.

Three synthetic methods cover denied opaque enums, datetime subclasses with hostile getters, and positive canonical enum/UTC identity values. **6,951 cumulative proposed source-defined test methods.** Own exact-head Phase3/full historical-general CI and independent evidence review mandatory. Source-only code checks are not authenticated OS/provenance or demonstrated profitable strategy evidence.

Phase8A #779/#820/#821 plus eight independent external security proofs remain MISSING; accepted annual catalogue through 2022/run384, protected 2023/run385/attempt1 and future years, Strategy V1 economics, shadow/demo/Phase10/11 and brokers/live capital all remain BLOCKED. No protected dispatch, installed GitHub workflow/ref/ruleset/runner change, trading or real money.
