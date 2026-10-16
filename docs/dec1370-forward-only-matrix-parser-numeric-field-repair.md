# DEC-1370 — Forward-only matrix field-name parser repair

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit forward repair of #1593 DEC-1369 at `c68fbc2dc3bad04eb16e02c3572e4224f2e4903a`. Exactly one character-class correction in a **tests-only source parser** and this docs-only receipt, **1,042 source-defined unittest methods unchanged**.

## Exact-head CI failure evidence

Full historical CI at each of original #1589, #1590, #1591, #1592 and #1593 completed **FAILURE**, despite Phase 3 success. CI logs showed the same new DEC-1365 parser dropping both digest keys `feature_zip_sha256` and `outcome_zip_sha256` from all 18 rows because the test parser's regular expression captured only `[a-z_]+` rather than keys with digits. This produced missing-field assertions, `KeyError` in digest tests, and false matrix diagnostic failures. There was no evidence from these failures that real archive digests or actual protected annual sources were corrupt: parsing the exact **committed workflow text** with digits preserved yields 18 unique cells, all seven required fields, positive decimal IDs and 64-character lower-case hexadecimal checksum literals. This is a test-parser repair, not a runtime data repair.

The one-line change makes the field-name regex `[a-z0-9_]+` for indented checked-in YAML fields. It retains strict downstream required-key, row-count, pair-consistency, SHA shape and tamper checks. New exact-head Phase 3 and full historical CI are required before this fix is considered verified; **never rewrite failed original #1589–#1593 SHA verdicts**. Note that #1590 also contained an invalid 2015 whitespace assertion, corrected only in its later strict forward child #1591; do not mark original #1590 green.

## Separate protected admission

The existing installed annual workflow, real archive fetch/unzip, protected runner, CLI/runtime gate, account, trading and GitHub rulesets remain unmodified. No protected annual data/evidence was accessed, no annual run, retry, replacement or dispatch was attempted. Independent OS-enforced original source no-write DEC-650/#820 = **BLOCKED**. Immutable server-side single-authority 2023 run385/attempt1 admission DEC-651/#821/#779 = **BLOCKED**. Green source CI is not external security sign-off or one-shot dispatch approval. No merges or promotions.
