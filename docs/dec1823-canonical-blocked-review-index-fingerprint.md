# DEC-1823 — Deterministic SHA-256 identity for the blocked reviewer index

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2069 `586ebb5a2b1ca505a56bf8187344d94452a0703e`.

To let independent reviewers refer to the *same exact static review request*, the seven-source index now carries `offline_request_fingerprint_sha256`, computed from canonical sorted, compact, UTF-8 strict JSON of every other index field. A local validator re-computes the digest, rejects unsupported/nonfinite fields and detects accidental edits. Both JSON and human Markdown present the same digest, labeled **NOT an attestation**. The canonical renderer still separately re-derives the entire source-only bundle from the pinned historical documents.

This is **not a digital signature, current GitHub control-plane witness, evidence verification, future no-bypass lock or trading approval**; anyone able to rewrite a packet can recompute its digest. All eight independent proofs remain MISSING, the 2023/run385/attempt1 action is BLOCKED, and all downstream research and brokers remain gated.

Four new tests (6,665 cumulative proposed source-defined) check canonical digest equality, deterministic rebuilds, corrupted/nonfinite edits and identical digest presentation in both formats. Valid report exits nonzero 3 (BLOCKED); invalid input fails 2 without stdout. No installed ref/ruleset/workflow mutation, protected data read, orders, demo/live trading, capital or profit. Independent review and exact-head Phase3/full CI required.
