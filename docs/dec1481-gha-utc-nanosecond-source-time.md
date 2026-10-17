# DEC-1481 — Preserve GitHub Actions UTC log time through nanoseconds

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child #1717 DEC-1480 at `4f96496312da9489f78c014c4e97b7897dd9f135`. Adds **16 source-defined unit methods**; **2068 proposed methods**.

The DEC-1454, DEC-1462, DEC-1466 and DEC-1477 checkout/index/run-window source reviewers parse GitHub Actions timestamps such as `2026-10-17T11:49:18.7726359Z` with standard-library `datetime.fromisoformat`. Python stores a maximum of six fractional decimal digits, truncating the seventh digit. Two valid Actions stage times 100 nanoseconds apart may be incorrectly collapsed to equality. This is a source-review false-negative risk, not evidence of an annual execution breach.

This standalone helper converts strict calendar-valid UTC-Z timestamps with 0–9 decimal digits into an **exact integer number of Unix epoch nanoseconds**, avoiding floats and calendar ambiguities. It rejects offset forms, nonexistent dates, missing timezone and more than nine fractional digits. Sixteen tests cover the actual seven-digit Actions format, 1-nanosecond and 100-nanosecond chronology, and fail-closed malformed input.

This PR only introduces the helper. A later reviewed child can use it across all four existing parsers so every stage and run-window comparison remains consistent. The helper does not authenticate original GitHub logs, prove OS no-write or authorize protected annual dispatch. Its own head-associated Phase3/full historical PR merge-source-tree CI and external qualified review are required.

DEC-650/#820 independently observed protected original OS no-write and DEC-651/#821/#779 exclusive immutable 2023 annual run385/attempt1 server admission remain **BLOCKED**. No protected run/retry, originals/archives, installed workflow/settings changes, merge, deployment or trading.