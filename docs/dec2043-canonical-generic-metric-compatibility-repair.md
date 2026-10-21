# DEC-2043 — Canonical generic metric rehash test-fixture repair

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2291 `a98917ae9cdd64302b9100c4cce66ba3c3753c85`.

Later full historical/general suite failures exposed three additional generic-metric compatibility test errors in the #2287–#2289 lineage: `gross_profit_usd`, `win_rate` and possibly the same pattern for optional `max_drawdown_usd`. Those fixtures passed already-inconsistent synthetic metrics directly into `write_backtest_artifacts`; the writer correctly refuses forged economic summary claims before writing. This does not prove the generic *auditor* tolerance is wrong, because that auditor was never invoked.

Replace four generic tolerance fixtures—gross profit, win rate, maximum drawdown and net return—with canonical baseline writing followed by a **writer-format-preserving** metric mutation and manifest rehash. Verify `verify_backtest_artifacts` accepts the modified digest before invoking `audit_backtest_artifact_structure`. The helper emits `metrics.json` using `json.dumps(sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)` plus one trailing LF. Two additional source-defined test methods verify a large generic win-rate deviation is still refused and a small deviation within the legacy tolerance is accepted.

**7,245 cumulative proposed source-defined test methods** (+2). No production source changes. The earlier full-suite failures remain failed; this exact child requires its own Phase3 and full historical/general CI. Generic tolerance is confined to synthetic/alternate-version reports and must not authorize false installed-source claims.

Phase8A #779/#820/#821 and eight independent external security proof packages remain blocked. No protected research, installed workflow/ref/runner changes, merges, strategy promotion, broker orders or real capital.
