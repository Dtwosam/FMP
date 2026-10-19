# DEC-1663 — Nested decoded duplicate supplementary Unicode object keys

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit test/docs child of #1909 at `e68ed9c530fc5d4a8e10c348f491a960a7d05c86`; 29 new methods (**4,145 proposed source-defined tests**).

For each of the fourteen required dictionary-valued source/CI evidence categories, this draft appends two lexically distinct members of one JSON object: a literal supplementary Unicode character (U+1F680) and its valid escaped UTF-16 surrogate-pair representation (`\\ud83d\\ude80`). Python's permissive JSON decoding treats both as the **same key**, preserving only the final value. Both mutation orders are included (null first or null last). Strict bounded JSON-text and stdin ingress must reject this semantic duplicate at `BUNDLE_JSON_GRAMMAR_UNREVIEWED`, not misclassify a *valid surrogate pair* as invalid Unicode or defer to downstream evidence review.

Tests assert correct permissive-decoding controls, exact safe diagnostics, unchanged clean caller inputs, no source-path echo, and no independent-original OS proof, exclusive dispatch proof or annual-run authority. One clean source-only control remains.

Own exact-head Phase 3/full general CI and qualified independent review required. Tests/docs only; no production/parser/resource-limit/workflow/security code, protected originals/archive/artifacts, annual execution/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
