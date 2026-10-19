# DEC-1668 — Literal raw JSON control characters in nested evidence are grammar errors

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1914 at `0cfd7d501129737be5ef233cc6f0deee5c6ac713`. 29 new test methods (**4,266 proposed methods**).

Strict JSON forbids unescaped control characters inside string keys and values. Across all fourteen dictionary-valued evidence categories, these tests append either a child key with a literal U+0000 NUL or a child string value containing an unescaped U+000A line feed. Python's strict `json.loads` rejects both cases. The portable JSON-text and stdin paths must return the exact `BUNDLE_JSON_GRAMMAR_UNREVIEWED` diagnosis before nested source/evidence validation.

The tests construct only the selected root category and leave unrelated nested keys untouched, assert the original synthetic evidence remains clean, the fixed verdict field inventory, no changed-source-path echo and false independent-original OS, exclusive dispatch and annual-run flags. The 29th method is an untouched source-only control.

Own exact-head Phase 3/full historical/general CI and independent qualified review required. Tests/docs only. No production/parser/resource/workflow/security changes, protected originals/archive/artifacts, annual execution/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
