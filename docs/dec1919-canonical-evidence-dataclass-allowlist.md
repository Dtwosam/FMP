# DEC-1919 — Allowlist deterministic evidence dataclass serialization

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2167 at `bb860c5b9248d9be0b98be6277788e6794ac9e1c`.

The private canonical serializer previously treated **any** caller-defined dataclass instance as evidence, enumerating and reading fields through `getattr`. An opaque dataclass with custom getters in `run_identity` could execute those getters during publication or create noncanonical data. Admit only exact source-defined `TradeRecord`, `RejectionRecord` or `EquityCheckpoint` dataclasses at this conversion boundary; the top-level `BacktestRun` remains separately validated at writer ingress. Invalid nested dataclasses fail with controlled `ValueError` before filesystem changes. Existing supported source record serialization and JSON schema are unchanged.

Three synthetic source-defined tests cover hostile dataclass getter denial, nested unsupported `BacktestRun` identity value, and valid canonical checkpoint/rejection output. **6,919 cumulative proposed test methods.** Exact-head Phase3/full historical-general CI and independent review required. No independent actual runner OS proof or Strategy V1 economic evidence is implied.

External Phase8A #779/#820/#821 security blockers and eight independent proof packages remain MISSING; accepted catalogue ends 2022/run384. Protected 2023/run385/attempt1, later years, Strategy V1 economics, shadow/demo/live brokers/funds and installed ref/workflow/ruleset/runner changes BLOCKED. No protected execution, trades or real capital.
