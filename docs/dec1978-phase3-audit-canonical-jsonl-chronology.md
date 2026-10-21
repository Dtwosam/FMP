# DEC-1978 — Canonical stored trade and rejection chronology

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2226 `8907f58fba0edf6b9256c115ec8457d8f5789e75`.

Writer serializes `trades.jsonl` ordered by (exit_timestamp_utc, trade_id), and `rejections.jsonl` by (evaluated_timestamp_utc, decision_id). The optional audit formerly accepted self-rehashed reversed rows as long as individual entry/exit chronology, trade IDs, count and digests were valid.

Enforce the writer's nondecreasing lexicographic record order during audit. Three source-defined tests forge and rehash reversed exit-time trades, reversed rejection evaluations and equal-time trade_id tie-break reversal. Keep legitimate equal-time records in canonical identifier order, and preserve low-level digest verifier behavior.

Proposed cumulative inventory **7,032 methods** (+3). Own Phase3/full historical/general CI required, with earlier #2221–#2224 failures remaining failed. This is stored-evidence internal consistency only.

Phase8A #779/#820/#821 and eight external independent security proofs remain missing. No protected 2023/run385/attempt1, later annual research, Strategy V1, demo/live broker, real capital, installed refs/workflows/runners or mergers.
