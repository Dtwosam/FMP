# DEC-1662 — Decoded nested JSON duplicate keys outrank lone-surrogate Unicode errors

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1908 at `f3fa7cc65e0ee99b6f3ffe524eecdc09bfe170b6`, adding 17 methods (**4,116 proposed source-defined methods**).

Four required evidence categories (`pr`, `tree`, `raw_ci_log_receipts`, `phase3_evidence_snapshot`) are each supplied with a Unicode-decoded **duplicate child key** and a second defect: a lone high surrogate in another key or a lone low surrogate in a value. Both placement orders are exercised (extra surrogate member first or last). A permissive decoder reconstructs a nested dictionary with invalid Unicode, but bounded strict decoding must reject `BUNDLE_JSON_GRAMMAR_UNREVIEWED` first, before walking for surrogate values or performing category evidence checks. This pins down a deterministic failure order across JSON text and stdin.

No caller fixture is modified. The emitted verdict retains only allowlisted fields and no synthetic changed source path, with false independent-original OS proof, exclusive dispatch-gate proof and annual-run authorization. The untouched synthetic control remains source-only and nonauthorizing.

Own exact-head Phase 3 and full historical/general CI, plus independent qualified review, required. Tests/docs only. No production/parser/limit/workflow/security changes, protected originals/archive/artifacts, annual dispatch/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
