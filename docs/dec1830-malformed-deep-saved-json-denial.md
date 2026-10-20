# DEC-1830 — Controlled rejection of deeply nested or malformed saved JSON

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of #2076, `42d040410a197769fea977042af8c3cf77fc54f8`.

A deeply nested but small saved JSON file can cause Python's JSON parser to throw `RecursionError`, potentially escaping the offline verifier and CLI instead of producing a controlled BLOCKED exit. Extend the read-only JSON serialization/parsing guards to include `RecursionError` and `OverflowError` where relevant, and the CLI exception boundary, without accepting additional data shapes.

Four focused tests (**6,686 cumulative proposed source-defined methods**) exercise over-depth JSON, duplicate keys nested inside a proof-like row, invalid UTF-8 and multiple JSON roots, and a directory passed as a purported regular file. The verifier still requires byte-size-bound no-follow source reads and exact equality with freshly reconstructed seven-source BLOCKED evidence. On valid sources exit 3 (BLOCKED); malformed input exits 2 with no stdout, including recursion errors.

This does not validate external evidence, installed GitHub administrator/ruleset scope, actual runner OS isolation, mutable-main race remediation, fresh protected run385 inventory, or human approval. No protected 2023/run385/attempt1 read or dispatch, broker/demo/live action, money/profit, or ref/workflow/ruleset mutation. Issues #779/#820/#821 and all eight independently acquired proofs remain MISSING/BLOCKED. Exact-head Phase3/full CI and qualified review required.
