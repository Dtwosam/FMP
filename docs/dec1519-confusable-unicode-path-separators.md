# DEC-1519 — Reject visually confusable Unicode source-path separators

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1764 at `ed86e8dc674bda00895b359bbcc120b87df18077`. Eleven new synthetic unittest methods; **2,431 proposed source-defined methods**.

The offline source-label validator uses ASCII forward slash as its only repository-relative separator and disallows backslash, but still admits Unicode glyphs that visually resemble slashes or backslashes. Such labels can hide path layout from a reviewer without being actual POSIX components. Conservatively refuse U+2044 fraction slash, U+2215 division slash, U+29F8 big solidus, U+FF0F fullwidth solidus, U+2216 set minus, U+29F5 reverse solidus operator and U+FF3C fullwidth reverse solidus. This is a lexical label rule, never a filesystem read or path normalization.

Eleven synthetic tests cover all named confusable separators, both byte-map categories, stdin verdict non-disclosure, and a valid normal POSIX source-only bundle with protected annual authority flags permanently false. It does not confer provider-origin authentication, protected original OS no-write or immutable annual server permission.

Own exact-head Phase 3/full historical-general CI and qualified independent review required. DEC-650/#820 independently witnessed original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected annual execution/retry, original/archive/artifacts, workflow/security settings changes, merges, deployment or trading.
