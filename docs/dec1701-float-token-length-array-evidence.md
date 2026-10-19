# DEC-1701 — Finite JSON float literal length at nested evidence boundaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent tests/docs child of #1947 at `f2046a6e56ba1cad0d25f58200d8cbb233f93af7`.

Adds **25 source-defined methods** (**5,535 proposed total**): positive and negative finite decimal numeric tokens at exactly `MAX_JSON_FLOAT_LITERAL_CHARS` (128) and one character above (129), embedded in each of six array-contained evidence paths, plus one clean control. Both 128-character forms must decode finitely and preserve strict JSON-text/stdin versus direct-memory review parity; 129-character forms must refuse at `BUNDLE_JSON_GRAMMAR_UNREVIEWED`, even though the stock JSON decoder can parse them into finite floats. This separates lexical-budget correctness from semantic nested evidence admission.

Synthetic caller unchanged; no synthetic marker/source path echo, stdout confined to safe fields, false original-OS, exclusive dispatch and annual authority proof. Own exact-head Phase 3/full historical-general CI and qualified independent review required. Tests/docs only, no parser/production/workflow/security updates, protected originals/archives/artifacts, annual execution/dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
