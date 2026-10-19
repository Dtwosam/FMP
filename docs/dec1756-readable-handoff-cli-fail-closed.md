# DEC-1756 — Correct offline human handoff Markdown and CLI failure semantics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2002 at a32eee0e5a60dbd80563b7ae7d9be23e04c99938.

A reviewable document needs actual Markdown code spans, not escaped backticks. The first source-only human-readable renderer emitted backslash-escaped backticks around its SHA/proof/stage identifiers. This draft corrects the emitted Markdown while keeping stable report content and zero execution authority.

Also places both report validation and Markdown rendering inside the same fail-closed CLI error boundary. Invalid source documents now yield the same explicit BLOCKED stderr error, return code 2 and no partial stdout regardless of JSON or Markdown output. A success code 0 means only that source documentation was rendered; never a security or trading permit.

Adds 4 behavioral integration checks, 6364 proposed source-defined cumulative, exercising clean Markdown formatting and malformed/forged annual source via the actual CLI. No network, GitHub permission/ref/ruleset/workflow mutation, protected market read or run385, broker/real-money path, trader decisions, Phase8B or Strategy V1 profitability claim. Exact-head Phase3/full historical-general CI and qualified review required. Issue #779/#820/#821 remains blocked.
