# DEC-1678 — Valid finite JSON numbers defer to category and schema type validation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1924 at `1407838985ae2319390a3dd020775f49b48dd231`; 81 new source-defined methods (**4,688 proposed**).

The companion to DEC-1677 distinguishes malformed numeric lexemes from valid but semantically wrong values. Five valid numeric representations — `0`, `-0`, `1.0`, `1e+0`, and `1E-0` — replace each of sixteen required category values independently. Strict JSON parsing must accept the finite numeric token. Subsequent review must refuse exactly `BUNDLE_SCHEMA_UNREVIEWED` for the schema field or `BUNDLE_CATEGORY_TYPE_UNREVIEWED` for other categories, rather than incorrectly claiming a grammar failure.

Each test also asserts unchanged clean caller evidence, safe stdin verdict shape, no synthetic source path echo, and no elevation of protected original OS proof, exclusive dispatch gate or annual-run authority. One clean source-only control remains, as does the test-name uniqueness guard.

Exact-head Phase 3/full historical-general CI and independent qualified review required. Tests/docs only; no production/parser/resources/workflow/security changes, protected originals/archives/artifacts, annual execution/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
