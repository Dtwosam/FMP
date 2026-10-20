# DEC-1853 — Detect saved three-format review file drift with a second read

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2099 `be24c1d5572e1ac64dafcdc10b2a83d69995fc9e`.

The prior three-file verifier checked full JSON, compact MISSING requests and human Markdown sequentially. That rejected edits to a *later* file before its check, but a malicious or accidental edit to the **already verified first file** could occur between checks and escape detection. Add an initial and final bounded, no-follow, read-only byte snapshot of all three input paths around the existing canonical verifiers, and reject when any byte differs. Existing canonical source and eight independent MISSING-proof checks are unchanged.

**This is not an atomic lock or proof of future file custody.** A file may still change after the second read or change-and-revert between reads; the verdict explicitly retains `sequential_snapshot_not_atomic_or_future_file_lock=true`. The best-effort second pass just reduces a demonstrated check-then-change exposure.

Four new regression methods (**6,748 cumulative proposed source-defined**) simulate edits to already verified full/compact files, a late-edit CLI path (must exit 2 without stdout), and read-only/no-process/no-network normal BLOCKED operation. No authenticated current GitHub admin/ruleset enforcement, privileged runner OS witness, source-freeze reauthentication, fresh run385 inventory or separate human approval. All eight external proofs and #779/#820/#821 remain MISSING/BLOCKED. Protected 2023/run385/attempt1, later research, installed workflow/ref/ruleset mutation, broker/demo/live trading and real money remain blocked. Exact-head Phase3/full regression CI and qualified independent review required.
