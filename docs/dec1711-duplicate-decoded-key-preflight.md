# DEC-1711 — Decoded duplicate-key aliases fail before nested reviewer

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1957 at `05738aba70e3b8f9cedc17f280f9d9f7cc213ffa`.

Adds **25 source-defined methods** (**5,779 proposed**): duplicate nested object keys in six array-contained evidence locations, with four spellings (literal duplicate plus Unicode escapes in first letter, underscore and final letter), and a clean control. Standard Python JSON decoding can silently keep the last duplicate, but strict parsing must reject the decoded equality as `BUNDLE_JSON_GRAMMAR_UNREVIEWED`. A patched composite reviewer must **never be invoked** in direct JSON-text or offline stdin paths. The test asserts the pair hook catches duplicate names after Unicode key decoding.

Original synthetic caller fixture is immutable, stdout has exact safe verdict fields and echoes no source path, marker or nested exception; original-OS proof, exclusive server dispatch and annual authority false. Own exact-head Phase 3/full historical-general CI and qualified independent review mandatory. Test/docs only; no production/parser/limits/workflow/security modifications, protected originals/archive/artifacts, annual execution/dispatch/retry, merging/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
