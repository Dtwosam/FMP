# DEC-1651 — JSON float token length: parser limit versus ordinary category-type failure

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1897 at `653f44c711475aa0e6bfc9f891b13ca72173ac08`. Fourteen synthetic regression tests (**3,947 proposed source-defined methods**).

A finite floating-point number can be expressed with arbitrarily many insignificant decimal zeroes. Ten negative cases substitute an otherwise finite `0.00…0` literal with exactly **one token character past** `MAX_JSON_FLOAT_LITERAL_CHARS`; the bounded parser must reject at grammar ingress as `BUNDLE_JSON_GRAMMAR_UNREVIEWED`, independent of source data. Three controls use the exact allowed 128-character token, proving the parser accepts the numeric literal and only then rejects the resulting wrong required category type as `BUNDLE_CATEGORY_TYPE_UNREVIEWED`. Verify bounded JSON-text/stdin parity, no sensitive source echo and all protected-run flags false. One untouched clean direct-memory control remains nonauthorizing.

Own exact-head Phase 3 and general CI and independent qualified review required. Tests/docs only, no production/parser/limits/workflow/security/gate changes, protected originals/archives/artifacts, annual execution/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
