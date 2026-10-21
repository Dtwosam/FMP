# DEC-1981 — Audit stored rejection domains and printable bounded IDs

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2229 `94fa06e49ff01c49fe0368dc8be52f7b085e2b6b`.

The optional read-only Phase3 auditor now validates canonical trade fields, values and chronology. A self-rehashed rejection JSONL could still declare an unsupported symbol, invented RejectionCode or malformed explanation while retaining canonical field names, valid timestamps and matching digests. Similarly it could bypass the writer's bounded printable decision/trade identifiers.

Enforce exact supported FX symbol membership, RejectionCode enum value, bounded printable nonempty explanation (4096 chars), and bounded printable nonempty trade_id and decision_id (512 chars). The original writer already enforces those limits. Keep legitimate ordinary rejection records accepted. Four new synthetic tests cover rejection symbol/code, invalid/oversized explanation, invalid decision IDs, and invalid trade IDs after rehash.

Proposed source-defined inventory **7,044 methods** (+4) pending own exact-head Phase3/full historical/general suites; this does not establish independently sourced market truth. Older failed full regressions #2221–#2224 remain recorded as failed. Phase8A #779/#820/#821 and eight independent external security proof packages are missing; protected research, trading, installed refs/workflows/runners, merges and real capital remain blocked.
