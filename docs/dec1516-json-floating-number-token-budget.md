# DEC-1516 — Bound JSON floating-point token length before conversion

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1761 at `8c0388ef78fcbb3cc9a04ffd7287c81f17f5ecc3`. Ten new synthetic methods; **2,399 proposed source-defined tests**.

DEC-1492 rejects non-finite decoded floats and integers exceeding 64 digits, but its custom `parse_float` callback still passes a caller-controlled floating-point token of up to 2,000,000 characters directly to `float()`. A bounded offline evidence parser should reject overly long numerical tokens before allocation/conversion even if they would decode as ordinary finite numbers. Cap floating-point JSON token text at 128 characters in `_finite_json_float`; retain the separate finite-number check and existing JSON, nesting and integer bounds. Violations produce the sanitized `BUNDLE_JSON_GRAMMAR_UNREVIEWED` code without echoing data.

Ten tests cover exact/over decimal, negative decimal, exponent token limits, nested oversized decimals, short non-finite overflow, normal scientific decimals, stdout non-disclosure, and clean positive source consistency. No protected annual authority or GitHub provider-origin proof is conferred.

Exact-head Phase 3/full historical-general CI and qualified independent review mandatory. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected dispatch/retry, original/archive/artifacts, installed workflow/security changes, merges, deployment or trading.
