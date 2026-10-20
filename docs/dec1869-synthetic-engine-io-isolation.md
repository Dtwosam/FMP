# DEC-1869 — Synthetic engine cannot read files or contact external systems

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only test child of PR #2116 `9e134590b571985d95b7089058059fad5a5b6cd3`.

The DEC-1865 and DEC-1867 after-cost regressions exercise the actual Phase3 backtest engine on invented EURUSD bars, not real exchange quotes. To help prevent accidental boundary crossing as this test fixture evolves, three new tests deny `subprocess.Popen`, `socket.socket`, `builtins.open` and `os.open` while running the invented-bars test, and verify the produced identity uses an explicit synthetic manifest and non-Strategy-V1 marker. Any attempted file/process/network access on these paths fails the unit test instead of silently making a protected source available.

The tests are local Python mocks and **not a privileged runner OS, GitHub action, broker or filesystem isolation attestation**. They cannot establish that the user has a profitable forex system or validate cross-year annual economics. Three new source-defined methods (**6,789 cumulative proposed**) are test-only; no changes to actual orders or market-source readers. Scoped human cost-model review and own exact-head CI remain mandatory before any promotion.

Accepted annual-first evidence ends at 2022/run384; protected 2023/run385/attempt1 and later research, Strategy V1 selection, shadow/demo/live and real-money trading remain BLOCKED. All eight independent security/provenance/inventory/human packages under #779/#820/#821 remain missing, and no ref/workflow/ruleset/runner installed control was changed.
