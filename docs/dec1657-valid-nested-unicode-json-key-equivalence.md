# DEC-1657 — Valid escaped nested JSON keys preserve reviewed source-only identity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1903 at `fb74f81cb80d815fd3f775b2ae13705342d056c6`. Fifteen new source-defined test methods (**4,024 proposed**).

The DEC-1654/1655 negative cases reject nested decoded-key duplicates. Here, an otherwise clean bundle uses a *single* Unicode escape for one child key inside each of the fourteen required dictionary-valued evidence categories, with no duplicate. The object is assembled at the category-member boundary; no global string substitution is used. JSON parsing must give an identical dictionary, and direct-memory/JSON-text/stdin review must agree on source consistency with an empty diagnostic list.

The caller's original envelope is not modified; a clean synthetic control remains nonauthorizing. Every test asserts the three protected annual-run authority flags stay false, and stdout does not echo the synthetic changed source paths.

Own Phase 3/full general CI and qualified independent review required. Tests/docs only; no production/parser/resource-limit/workflow/security changes, protected originals/archives/artifacts, annual execution or retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
