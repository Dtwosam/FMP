# DEC-1765 — Preserve Phase7 historical losing windows and trade count

**DRAFT / NEVER MERGE / NEVER PROMOTE** — exact-parent source-only child of PR #2011 at `a742e91fe9cbb87362f6b2e3701480310483f51d`.

The retrospective Phase7 cost replay (DEC-1764) already showed the aggregate after-cost sign reversal. This extension also parses the **original seven 0.2-pip Stage 2 windows**, verifies window identities/order, their distinct scored ranges and metric columns, reconciles 199 trades, and preserves both losing windows instead of showing only a small aggregate positive result. This addresses the governing research emphasis on negative periods, instability, support and historical concentration, while **not** conducting a new annual catalogue or a fresh unconsumed experiment.

Of the seven previously published windows, **5 were positive and 2 were negative** at the original 0.2-pip diagnostic assumption. `2025-Q1` returned **−0.520185% (−$520.18)**; `2026-partial-Q3` returned **−0.645978% (−$645.98)**. The sum of rounded published window returns is within 0.00001 percentage points of the published +0.757266% aggregate, and seven window trade counts add to 199. That aggregation does **not** constitute fresh independent OOS evidence for a new Strategy V1.

Adds 6 focused source-only methods (6433 cumulative proposed), retains deterministic report output and nonzero exit status **3**, and preserves the frozen source Git blob identity. No protected annual history accessed, new result experiment, trade, broker order, demo or live risk, annual run385 dispatch, workflow/runner or GitHub security mutation. #779/#820/#821 remain BLOCKED. Phase3/full historical/general exact-head CI and qualified independent review required.
