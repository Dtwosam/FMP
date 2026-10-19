# DEC-1700 — JSON integer digit boundary in nested evidence objects

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1946 at `ac8aa3607f21acd3b8d75acea3e1fcb652c76f01`.

Adds **25 source-defined methods** (**5,510 proposed total**): positive/negative integers with exactly `MAX_JSON_INTEGER_DIGITS` digits (64) or one above (65) in each of six array-contained evidence dictionaries, plus a clean control. At the 64-digit bound, strict JSON-text/stdin must agree with decoded direct-memory review and avoid false grammar refusal. At 65 digits, strict grammar ingress must reject `BUNDLE_JSON_GRAMMAR_UNREVIEWED` before constructing an unreviewed oversized integer, regardless of nested category validation. Negative signs do not count as digits.

All evidence is synthetic and deep-copied; caller remains immutable, exact safe stdout field inventory and no source-path/marker echo. Independent original OS proof, server dispatch and annual-run authority remain false. Own exact-head Phase 3/full historical-general CI and qualified independent review required. Tests/docs only, no production/parser/workflow/security updates, protected originals/archive/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
