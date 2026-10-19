# DEC-1670 — Unescaped JSON control characters inside array-contained evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit test/docs child of #1916 at `8a0e3cf653eecdf82051aabe4e2540fe40de9654`, adding 25 regression methods (**4,320 proposed**).

Six nested array pathways (run entries, job records, PR comparison files, Phase 3 scenarios, Git-tree entries and merge-parent records) are each tested with four illegal raw JSON string encodings: NUL in a key, LF in a value, CR in a key and TAB in a value. These bytes are forbidden unless escaped. Both the ordinary Python JSON parser and the offline strict JSON-text/stdin reviewer must reject malformed input with a specific `BUNDLE_JSON_GRAMMAR_UNREVIEWED` verdict before source-evidence review.

The serializer traverses only the intended nested object and preserves all other members. All cases check unchanged clean caller evidence, exact safe verdict fields, no sample-path echo, and false protected OS/dispatch/annual-run authority. One clean control is retained.

Own exact-head Phase 3 and historical/general CI, plus independent qualified review, required. Tests/docs only; no production/parser/limit/workflow/security changes, protected originals/archive/artifact access, annual execution/retry, merge/deploy/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
