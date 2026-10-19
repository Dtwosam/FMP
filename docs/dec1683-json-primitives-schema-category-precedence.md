# DEC-1683 — Legal JSON Boolean and null syntax preserves schema/category type refusals

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent tests/docs child of #1929 at `1c37063c732e665c30594e8254680aadaca7768a`. Adds 49 methods (**4,822 proposed source-defined tests**).

For each of the sixteen required top-level bundle evidence categories, this draft substitutes one of three ordinary JSON primitive tokens (`true`, `false` or `null`). Each is valid JSON and must parse cleanly as a Python `bool` or `None`. Because none is the expected schema string or required category container, the strict reviewer must refuse specifically `BUNDLE_SCHEMA_UNREVIEWED` for the schema field or `BUNDLE_CATEGORY_TYPE_UNREVIEWED` for the remaining categories—not `BUNDLE_JSON_GRAMMAR_UNREVIEWED`. The strict stdin verdict must agree.

All 48 negative cases verify the source-only clean fixture remains untouched, no sample changed-source path is emitted, exact safe verdict field inventory, and false protected original OS proof, exclusive dispatch proof and annual-run admission. One clean control and the DEC-1674 method-name guard remain.

Own Phase 3/full historical-general CI and independent qualified review required for the exact new head. Tests/docs only. No production/parser/resource-limit/workflow/security change, protected originals/archive/artifacts, annual execution/retry, merging/deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
