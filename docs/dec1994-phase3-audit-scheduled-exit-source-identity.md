# DEC-1994 — Audit scheduled exit source identity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2242 at `26a3746e3be6dc86973c5e6ef439eb6658b7edbc`.

The Phase3 engine emits an optional `summary.run_identity.scheduled_exits` list in deterministic (timestamp_utc, symbol, decision_id) order. An attached local checksum manifest does not independently authenticate those claims. Until now the read-only auditor checked the JSON tree and summary's outer structure but could accept synthetic/rehashed scheduled exit entries with unsupported FX symbols, altered ordering or duplicate decision identifiers.

When that source-defined field is present, require a nonempty list of exact descriptor dictionaries (decision_id, symbol, timestamp_utc); accept only bounded printable IDs and supported symbols, exact canonical UTC timestamps, unique decisions and writer-canonical order. Synthetic evidence without the field remains accepted. Four source-defined tests exercise normal writer-compatible descriptors, unsupported symbol, reversed order and duplicated decision. No schema changes for real Phase3 runs.

**7,079 cumulative proposed source-defined test methods** (+4). All exact-head Phase3/full historical and general CI must be verified before claiming regression validity. Old failed runs remain failed.

Phase8A #779/#820/#821 and eight independently supplied security/approval proofs still blocked; no protected annual run385 research, strategy promotion, broker or real capital, installed refs/workflows/runners changes, or merges.
