# DEC-1697 — Malformed delimiters inside mandatory evidence arrays

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1943 at `12163cf30698fa18536dd343727a38ef2cf4e3eb`.

Adds **49 source-defined methods** (**5,387 proposed total**): eight malformed JSON array separator/bracket forms across six array-containing evidence paths—runs, jobs, comparison files, Phase 3 scenarios, full-tree entries and merge parents—plus a clean control. A deep copy receives a unique last array member and then one malformed separator or bracket spelling, covering missing/double/semicolon/colon comma separators, trailing comma, missing/extra closing bracket and JavaScript-style comments. All must refuse at `BUNDLE_JSON_GRAMMAR_UNREVIEWED` in strict JSON-text and offline stdin before evidence review.

Original fixture remains immutable, verdict fields exact and safe, synthetic marker/changed paths not echoed, and independent-original-OS proof, server-dispatch and annual authority flags false. Own exact-head Phase 3/full historical-general CI plus qualified independent review required. Only tests/docs; no parser/production/workflow/security changes, protected originals/archive/artifacts, annual dispatch/retry, merging/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
