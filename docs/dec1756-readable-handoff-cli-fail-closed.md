# DEC-1756 — Correct offline human handoff Markdown and CLI failure semantics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2002 at a32eee0e5a60dbd80563b7ae7d9be23e04c99938.

A reviewable document needs actual Markdown code spans, not escaped backticks. The first source-only human-readable renderer emitted backslash-escaped backticks around its SHA/proof/stage identifiers. This draft corrects the emitted Markdown while keeping stable report content and zero execution authority.

Also places both report validation and Markdown rendering inside the same fail-closed CLI error boundary. Invalid source documents now yield the same explicit BLOCKED stderr error, return code 2 and no partial stdout regardless of JSON or Markdown output. After DEC-1761, a normally rendered but still BLOCKED report prints to stdout and exits **3**, not 0; malformed input exits **2** and prints no stdout. A standard shell `if` or `set -e` cannot mistake successful report generation for a green annual research or trading gate.

Adds 4 behavioral integration checks, 6364 proposed source-defined cumulative, exercising clean Markdown formatting and malformed/forged annual source via the actual CLI. No network, GitHub permission/ref/ruleset/workflow mutation, protected market read or run385, broker/real-money path, trader decisions, Phase8B or Strategy V1 profitability claim. Exact-head Phase3/full historical-general CI and qualified review required. Issue #779/#820/#821 remains blocked.
