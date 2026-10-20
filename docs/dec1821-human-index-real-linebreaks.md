# DEC-1821 — Render actual newline-delimited human security handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2067 `eaf7c85c5daadb60aab6f33557e74dd80eb51285`.

The initial seven-source Markdown renderer joined lines using a printable backslash-plus-n string, leaving the human reviewer packet on a single physical line. Replace the separator with an explicit LF bytepoint through `chr(10)`. This changes **presentation only** and does not relax canonical full-JSON report comparison, MISSING owner roles or the permanent BLOCKED result. A new test verifies actual Markdown headings and multiple real lines, preventing this regression.

One added test method, **6,657 cumulative proposed source-defined methods**. Valid reports remain BLOCKED with nonzero exit 3; forged upstream or tampered worksheets still fail exit 2 with empty stdout. No protected 2023/run385/attempt1 access, installed GitHub ref/workflow/ruleset/runner changes, broker/demo/live execution, real money or profitability. Issues #779/#820/#821 and all eight external independent proof packages remain MISSING/BLOCKED. Own exact-head CI and independent review required.
