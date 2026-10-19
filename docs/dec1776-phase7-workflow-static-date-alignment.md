# DEC-1776 — Historical Phase 7 workflow/source date-boundary alignment

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent child of PR #2022, SHA `be89b2f6750e59c133b889d30199ebfa6749322a`.

DEC-1775 validated the seven date partitions printed in the frozen Phase7 Markdown. DEC-1776 independently compares those dates to the **actual static `expected_windows` literal** in `.github/workflows/phase7-walk-forward.yml`, pinned to Git blob `2ab8bd26a82a4561a24e6efc179552df8b919284`. It uses **`ast.literal_eval` of the narrow extracted list only**, never executes YAML, Python snippets, or any workflow. The audit requires the historic source's runtime checks for 7-day preceding warm-ups, exclusive scored end boundaries, exact partition keys, no later date than 2026-08-21, and recomputed frozen Stage2 gates to remain present.

This cross-file consistency test can catch a documentary/source cutoff discrepancy even if one file alone looks coherent, including an extra day accidentally extending partial 2026 Q3. It cannot reauthenticate actual 2025/2026 market data, executed runner code/privileged OS, bar timestamps, source artifact checksums, or absence of future-information leakage: those are separate live/historical execution evidence requirements.

Adds **7** source-level tests (**6486 cumulative proposed**); historical Phase7 cost stress, dual-pinned Markdown and recorded Stage2 artifact values remain unchanged. No new Phase8A annual research, protected 2023/run385/attempt1, market I/O, workflow dispatch, Github admin policy, brokerage, shadow/demo/live trading or earnings claim. #779/#820/#821 remain BLOCKED. Exact-head Phase 3/full historical-general CI and qualified independent review required.
