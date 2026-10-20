# DEC-1796 — Strict eight-proof reviewer identity in offline JSON handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent source-only child of #2042 at `6b0422b5caeaf6998c496c8d649a2e96eaafb08c`.

The DEC-1782 compiler formerly checked proof IDs and MISSING statuses, but not the full reviewer-role-and-field contract before its **JSON** output. The Markdown presentation later checked the complete frozen proof rows. That asymmetry could allow malformed nested rows or forged reviewer roles to reach an apparently official-looking machine-readable BLOCKED packet if the documentary report producer were changed. In particular, a non-object row could throw outside the intended controlled InvalidHandoff path.

Both formats now share a compiler-level strict check: exactly eight known proof IDs, exactly eight source-defined reviewer roles, fields **id / review_role / status only**, exact dictionary shape, correct ordering, and permanent status **MISSING**. Malformed non-object rows fail with controlled InvalidHandoff. Markdown retains its independent pinned-source canonical comparison.

Four added methods test tampered reviewer roles, approval-key injection, malformed rows and both CLI formats returning **2 with empty stdout** on forged proof data (**6,584 cumulative proposed source-defined test methods**). Normal valid handoffs remain BLOCKED exit 3. This is strictly local source-only presentation validation: no actual external attestation, ruleset, installed workflow, main ref, protected 2023/run385 attempt1 read or dispatch, orders, demo/live trading, money or profitability. #779/#820/#821 still MISSING/BLOCKED. Exact-head Phase3 and full regression CI and qualified independent review required.
