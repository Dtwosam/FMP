# DEC-1824 — No-process and no-network regression for seven-source index

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2070 `480e7188f263aa79681a885588c8f894a63df6c5`.

The seven-source proof packet must be an entirely offline, documentary operation. Existing source-only tests check the underlying six-source compiler, but not the integrated seven-source index or its CLI formats. Three focused negative-control tests now deny Python `subprocess.Popen` and `socket.socket` during index construction and during both valid CLI formats. Any unexpected process spawn or socket creation fails a test instead of silently generating a report.

These are **unit-test guards**, not real privileged runner OS, publisher or network isolation attestations. No actual administrator review, protected market source access, broker API, workflow dispatch or one-shot research is performed. The tests only ensure code retains its offline contract on the tested paths. Valid output remains BLOCKED exit 3, invalid source fails 2 without JSON.

Three additional source-defined tests (6,668 cumulative proposed). External #779/#820/#821 and eight independent proof packages remain MISSING/BLOCKED; protected 2023/run385/attempt1 and later annual research, Strategy V1, demo/live trading and any real-money activity are not authorized. Exact-head Phase3/full CI and qualified review required.
