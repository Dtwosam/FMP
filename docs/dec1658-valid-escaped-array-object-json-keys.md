# DEC-1658 — Valid Unicode-escaped keys inside array-contained JSON evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1904 at `662ee00ec1201fcf6c10b80e71039a35adbf32e6`, adding thirteen synthetic regression methods (**4,037 proposed methods**).

The negative tests in DEC-1656 refuse decoded duplicate JSON keys inside objects under arrays. Here a single original object-member name in an array element is instead written with a legal Unicode escape for the first or last character. Six evidence paths are checked: runs, jobs, comparison files, Phase 3 scenarios, Git tree entries and merge-parent records. There is no duplicate. JSON/text and stdin must agree exactly with clean direct-memory review, source consistency is true, diagnostics are empty, and no annual-run authority becomes true.

The path-specific serializer preserves other objects and avoids accidental replacement in nested keys with the same spelling. One unmodified synthetic control is included. Own Phase 3/full general CI and qualified independent review required.

Tests/docs only. No production/parser/resource-limit/workflow/security change, protected originals/artifacts, annual dispatch/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
