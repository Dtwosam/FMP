# DEC-1736 — Static source identity and repair integrity of Phase 8A review tests

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1982 at `52c99556b2068b3c0b7a28fbd30eb7da5afeaf02`.

Adds **three** source-defined AST tests (**6,022 proposed cumulative methods**) guarding source readability and exact test discovery for DEC-1732 (13 cross-document Phase 8A boundary checks), DEC-1733 (14 adversarial Phase 8A document consistency controls), and DEC-1735 (24 human admin-handoff negative controls). All three modules must parse, contain **51 methods** total, and have unique method names across the files. A separate test confirms the original one-shot no-dispatch and no-synthetic-review gate assertions and the two pristine controls remain discoverable. The final test ensures the DEC-1734 correction swaps Phase 8A and 8B headings instead of removing Phase 8A and triggering the wrong exception type.

**Scope limits:** AST/name-identity is not live CI qualification, effective GitHub ruleset enforcement, privileged runner isolation, one-shot authorization, annual catalogue performance or trading edge. The test only opens local source test files, and never protected historical data, workflow assets, GitHub control APIs or brokers.

All substantive human admin evidence remains independently owned and missing; protected 2023 run385/attempt1 is **BLOCKED** under issue #779, DEC-650/#820 and DEC-651/#821. No production/parser/workflow/security changes, annual dispatch, retry, main/tag/ruleset change, strategy promotion, demo/live orders or real-money trading. Exact-head Phase 3/full historical-general CI and qualified independent review remain mandatory.
