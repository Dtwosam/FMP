# DEC-1661 — Decoded nested surrogate errors precede evidence category review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1907 at `631088706955dc6d62b9cbc16dd0c28b6cc3967c`, with **29 new source-defined regression tests (4,099 proposed total)**.

For each of the fourteen required dictionary-valued source/CI evidence categories, this draft injects either an escaped lone **high UTF-16 surrogate as an extra nested key** or an escaped lone **low UTF-16 surrogate as an extra nested string value**. A generic permissive JSON decoder parses these payloads into dictionaries containing invalid Unicode scalar values, and the extra evidence field itself is also not reviewed. The portable strict JSON text and stdin paths must reject `BUNDLE_JSON_UNICODE_UNREVIEWED` during decoded Unicode inspection, before any category field validation or nested reviewer error.

Tests prove decoded lone-surrogate presence, unchanged caller-supplied clean evidence, specific safe refusal code, no synthetic sample-path stdout echo, and false independent-original OS proof, exclusive dispatch proof, and annual-run authorization. One clean source-only nonauthorizing control remains.

Changes are limited to synthetic tests and this document. Exact-head Phase 3/full historical/general CI and qualified independent review required. No production/parser/resource-limit/workflow/security/annual gate changes, protected original/archive/artifact access, annual execution/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
