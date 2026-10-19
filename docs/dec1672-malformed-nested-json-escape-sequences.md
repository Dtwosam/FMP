# DEC-1672 — Malformed nested JSON escape sequences refuse at grammar ingress

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1918 at `0cd6cf15e7b7115dc30923e01f729b0627e569dc`. Adds **57 source-defined regression methods (4,402 proposed total)**.

Each of fourteen mandatory dictionary-valued evidence categories is given four malformed JSON string escape spellings in an additional nested value: unknown backslash escape `\\q`, invalid hexadecimal-style `\\x00`, non-hex `\\u00G0`, and too-short `\\u12`. None is valid JSON, including the superficially Unicode-looking cases. The strict bounded JSON text/stdin path must refuse `BUNDLE_JSON_GRAMMAR_UNREVIEWED` before category shape checking, source validation or protected-run authority. Python `json.loads` refusal acts as a control.

Tests assert original evidence remains untouched, exact safe verdict inventory, no synthetic changed-source-path output and false original OS proof, exclusive dispatch proof and annual-run flags. One clean source-only nonauthorizing control completes the 57.

Own exact-head Phase 3 and full historical/general CI and qualified independent review required. Tests/docs only; no production/parser/resource limit/workflow/security changes, protected originals/archives/artifacts, annual execution/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
