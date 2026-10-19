# DEC-1654 — Nested Unicode-decoded JSON duplicate keys refuse at grammar ingress

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit, test/docs-only child of #1900 at `21585cb1df84ab477a3e4c04262449d574d79157`. Fifteen proposed test methods (**3,981 total source-defined methods**).

The portable JSON decoder installs a bounded `object_pairs_hook` for *every* JSON object, not only the 16 top-level envelope categories. This draft exercises each of the 14 required dictionary-valued categories with a syntactically valid **inner duplicate**: the original child key has `null` first, and an equivalent Unicode-escaped key carries its original value second. Naive last-key-wins parsing reconstructs exactly the clean original envelope. Strict JSON/text and stdin ingress must instead fail at `BUNDLE_JSON_GRAMMAR_UNREVIEWED`, before nested source-evidence evaluation or any annual-run authority. Each test also checks safe verdict shape, no source-path output echo, and all three protected admission flags false.

Root-only member assembly from DEC-1653 avoids accidental mutation of same-named fields in other nested categories. One clean synthetic control proves source consistency alone is still nonauthorizing. No production or parser change.

Own exact-head Phase 3/general CI and qualified review still required. No production/runtime/workflow/security changes, protected originals/archive/artifacts, annual execution/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
