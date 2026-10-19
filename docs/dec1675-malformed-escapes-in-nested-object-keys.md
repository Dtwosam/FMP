# DEC-1675 — Malformed escapes in nested JSON object keys

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1921 at `1199c780af0de9a41bf852bd3ab2ece5155553b2`. 57 new source-defined unittest methods (**4,485 proposed**).

DEC-1672/1673 exercise invalid escapes inside string *values*. This companion tests strict grammar rejection inside a string **member name**. The four invalid forms are `\\q`, `\\x00`, `\\u00G0`, and `\\u12`. Each is injected into one extra key within each of the 14 dictionary-valued top-level evidence categories. The ordinary strict Python JSON decoder must raise `JSONDecodeError`, and JSON-text/stdin review must refuse with the exact `BUNDLE_JSON_GRAMMAR_UNREVIEWED` diagnostic, before any nested evidence or annual authority review.

Each case verifies the original synthetic source remains untouched and source-consistent, stdout includes no sample source path, the emitted verdict contains exactly the required fields, and all three protected flags are false. One untouched clean control is included. The source-level uniqueness test from DEC-1674 remains active.

Own exact-head Phase 3/full historical/general CI and independent qualified review required. Tests/docs only; no production/parser/resource-limit/workflow/security changes, protected original/archive/artifact access, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
