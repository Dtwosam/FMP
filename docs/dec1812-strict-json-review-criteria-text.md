# DEC-1812 — Reject injected executable reviewer criteria in JSON output

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2058 `9a3391b862fd120b1aa71dc50e1f8e23f95243bd`.

The Markdown renderer enforced some textual restrictions on external proof acceptance criteria, while the JSON compiler previously verified only eight ordered nonempty strings. A locally drifted criterion could embed a Markdown table approval row or a concrete workflow/broker command and be returned as machine-readable evidence despite all actual proofs still MISSING. This is a **presentation-integrity** issue, not runtime authorization.

Require all source-defined external proof criteria in the JSON compiler to be exact nonempty strings without Markdown table delimiters, line breaks or backticks, and reject representative direct execution fragments `gh workflow run`, `git push`, `order_send(`, and `broker.order_send(`. Keep the canonical eight IDs/roles, MISSING status and BLOCKED report unchanged. These lexical checks cannot replace qualified review or enforce GitHub permissions.

Four adversarial test methods (6,632 cumulative proposed source-defined): multiline/table injections, direct workflow/broker command requests, malformed Boolean criterion and failure of both CLI formats without stdout (invalid input exit 2; valid BLOCKED exit 3). No protected 2023/run385/attempt1 research, GitHub ref/workflow/ruleset mutation, broker/demo/live execution, real-money or strategy profitability. Independent external proofs #779/#820/#821 remain MISSING/BLOCKED; exact-head CI and qualified review required.
