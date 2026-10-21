# DEC-1984 — Match writer JSON tree depth and Unicode constraints in audit

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2232 `ad4b6cf3a781e7c13330eca9c9ff2251772e4ae1`.

The optional read-only artifact audit rejects forged numeric overflow and deep JSON parser recursion, but until now it could still accept rehashed ignored metric properties with object keys containing control characters, strings with escaped UTF-16 surrogate code points or JSON nesting deeper than the deterministic writer's 64-level limit. Such content cannot be produced by the canonical source serializer.

Walk every parsed JSON document with a depth cap and validate printable object keys and surrogate-free strings, matching the writer's deterministic source contract. Apply to summary, metrics and JSONL records, even in otherwise ignored metadata. Keep legal text values with ordinary whitespace; restrict only object keys to printable Unicode.

Three source-defined tests forge and rehash a control-character key, lone-surrogate string and 70-level nested metric, each passing low-level manifest SHA256 verification while the optional audit refuses. Proposed cumulative inventory **7,053 methods** (+3), not a verified CI pass count.

Independent exact-head Phase3/full historical-general regression and reviewer signoff required; past full failures still FAILED. Phase8A #779/#820/#821 and eight external proof packages remain missing; no protected 2023/run385/attempt1, annual research, Strategy V1, installed refs/workflows/runners, broker trading, merges or real capital.
