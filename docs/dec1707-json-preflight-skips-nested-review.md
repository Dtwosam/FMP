# DEC-1707 — Strict grammar ingress must skip nested evidence reviewers

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1953 at `b6abe8a6b6854c935fa52cbc25b7e7e8f869b405`.

Adds **37 source-defined methods** (**5,679 proposed**): six malformed JSON tokens inside six array-contained evidence object paths, plus a clean synthetic control. Explicitly replaces the nested source-evidence reviewer with a patched guard during strict JSON-text and stdin parsing and verifies it was **never invoked**. This is stronger than merely checking the returned diagnostic: malformed data must be refused before nested semantic review, including permissive Python nonfinite constants.

Exact `BUNDLE_JSON_GRAMMAR_UNREVIEWED`, safe verdict inventory, clean caller fixture unchanged, no synthetic marker, source path or reviewer exception echo, and false independent-OS/dispatch/annual authority fields. Test and documentation changes only. Own exact-head Phase 3/full historical-general CI and qualified independent review required. No production/parser/resource/workflow/security updates, protected originals/archive/artifacts, annual execution/dispatch/retry, merging/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
