# DEC-1694 — Non-JSON whitespace at nested evidence token boundaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests/docs-only child of #1940 at `d15e1bfd17ebbac3ef1042bc8be26f55b8e1d93c`.

Adds **49 source-defined methods** (**5,240 proposed total**): eight disallowed whitespace/control characters placed immediately after the colon of a synthetic value in each of six array-contained evidence objects, plus a clean control. Inputs include vertical tab, form feed, NUL, NBSP, em space, Unicode line/paragraph separators and BOM. The JSON grammar permits only space, tab, CR and LF between tokens; non-JSON whitespace must fail `BUNDLE_JSON_GRAMMAR_UNREVIEWED` through both text and offline stdin, rather than triggering category/schema review or successful decoding.

No private or protected evidence is read. Caller fixture remains immutable, stdout is confined to safe verdict fields, no synthetic evidence path or marker is echoed, and original OS proof, server dispatch and annual authorization stay false. Own exact-head Phase 3/full historical-general CI plus qualified independent review required. No production/parser/limits/workflow/security updates, protected originals/archives/artifacts, annual dispatch/retry, merge, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
