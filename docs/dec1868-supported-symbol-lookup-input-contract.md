# DEC-1868 — Strict symbol lookup for pure backtester cost contracts

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2115 `e12c275bc8ad67f611e9251a244ed192e1d13b8f`.

`pip_size(symbol)` relied on direct dictionary indexing and only translated `KeyError` into a controlled ValueError. A malformed list or mapping passed as a pair symbol instead raises raw `TypeError: unhashable type`. Reject every value where `type(symbol) is not str` before lookup. Supported string values remain the exact three FX pairs (EURUSD, GBPUSD, USDJPY); case folding, unsupported pairs, bytes, booleans or list-of-symbol aliases do **not** become accepted.

Three new Phase 3 test methods (**6,786 cumulative proposed source-defined**) exercise malformed symbols, malformed symbol propagation via `apply_adverse_slippage`, and frozen pip-size behavior for all three supported pairs. This is cost-helper input hardening only, with no access to protected annual data, live quotes or broker controls. All changes are proposed unmerged drafts requiring own exact-head Phase3/full regression and independent cost review.

Phase8A annual-first catalogue accepted through 2022/run384 only; 2023/run385/attempt1 and later research, Strategy V1 approval, shadow/demo/live broker orders and real capital are BLOCKED. Security #779/#820/#821 and eight independently obtained proofs remain MISSING. No installed workflow/ref/ruleset or runner mutation or demonstrated profitability.
