# DEC-1969 — Audit serialized checkpoint chronology and finite equity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source/tests/docs child of PR #2217 at `9f9276f2b72fe02b3104574d52b87e0630ad1b66`.

The optional structural audit previously matched only `summary.equity_checkpoint_count` against the number of stored checkpoint objects. A self-rehashed folder could replace a numeric equity with a Boolean or reorder chronological checkpoints while retaining internally consistent SHA256 digests. Check each checkpoint is exactly a JSON object with `timestamp_utc` and `realized_risk_equity_usd`, parse exact UTC-marked ISO datetime strings, require ordinary finite numeric equity and enforce nondecreasing timestamp order. Preserve legitimate equal-time checkpoints and negative-but-finite equity snapshots (if any) as the report writer does. The low-level checksum verifier is unchanged.

Two synthetic methods forge and rehash an equity Boolean and a reverse-ordered pair of valid checkpoints, each refused by the stored-evidence audit. **7,013 cumulative proposed source-defined tests**. Own exact-head Phase3/full historical/general CI and qualified independent source review mandatory; not proof of real market provenance or trading economics.

All historical CI failures remain failed. Phase8A #779/#820/#821 and eight independent external administrator/ref/installed workflow/real OS isolation/DEC609–610 provenance/fresh one-shot 2023 inventory/human proof packages remain MISSING/BLOCKED. Accepted catalogue ends 2022/run384. Protected 2023/run385/attempt1, later annual research, Strategy V1 economics, shadow/demo/live broker funds and installed GitHub ref/workflow/ruleset/runner mutation blocked. No protected dispatch, merge, broker order or real capital.
