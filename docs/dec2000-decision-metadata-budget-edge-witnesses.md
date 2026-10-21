# DEC-2000 — Boundary witnesses for decision-metadata node and byte budgets

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2248 at `d0f89eb2c7f519ee53090fc158c7dddf736f83f0`.

DEC-1998 added an opt-in audited source metadata tree with an 8192-node budget and 64KiB canonical compact JSON bound. This test-only draft adds adversarial exact-boundary witnesses without changing the writer or auditor implementation. `decision_config={"values":[0]*8190}` consumes exactly 8192 nodes (root + list + 8190 leaves) and must pass; a list with 8191 leaves consumes 8193 and must fail with the controlled node budget error. A Unicode string with 11000 `é` characters must fail the 64KiB ASCII-escaped serialized metadata limit even though its raw UTF-8 byte length is smaller. The generic digest verifier still passes these writer-output fixture files; the optional audit rejects the two source-incompatible claims.

Three new source-defined test methods. Proposed cumulative inventory **7,101 methods**. Own exact-head Phase3 + full historical/general tests required; no full-pass assertion without those outcomes. Historical CI failures remain failures. All changes source tests/docs only, no production code in this draft.

Phase8A security #779/#820/#821 and eight independently provided proof packages remain unsatisfied. Protected annual run385 and later research, installed runner/ref/workflow mutation, merges, broker orders and capital blocked.
