# DEC-1673 — Malformed JSON escapes inside array-contained evidence fail closed

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1919 at `4bc04a478e755851b5c154b535bf719cb3ae24ce`. Adds 25 source-defined regression methods (**4,427 proposed**).

Extends DEC-1672's bad JSON escapes into six paths containing arrays of evidence dictionaries: runs, jobs-by-run, comparison files, Phase 3 scenarios, Git-tree entries and merge parents. Each is tested with invalid `\\q`, `\\x00`, `\\u00G0` and `\\u12` string escape spellings, giving 24 negative cases plus an untouched synthetic control. The malformed member is inserted only at the chosen nested path. Both the standard Python JSON parser and strict portable JSON-text/stdin reviewer must refuse at grammar ingress (`BUNDLE_JSON_GRAMMAR_UNREVIEWED`) before any nested evidence check.

All cases protect caller input immutability, exact safe verdict fields, no sample source-path echo and false independent-original OS, exclusive server dispatch and annual-run flags. Own exact-head Phase 3/full historical-general CI and qualified independent review required. No production/parser/limits/workflow/security changes, protected originals/archives/artifacts, annual execution/retry, merge/deployment or trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
