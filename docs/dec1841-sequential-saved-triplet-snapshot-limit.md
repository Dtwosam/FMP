# DEC-1841 — Sequential review verification is a snapshot, not a file lock

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2087 `c51a2500f9e0e983ef6d8fe65845f42e5dbc2eeb`.

The three-format review verifier reads full JSON, compact proof requests and human Markdown sequentially. Each file is checked against the freshly rebuilt frozen source packet, so a mutation of a **later** file during earlier checks must be rejected. This is **not an atomic snapshot**: there is no filesystem lock, and a previously checked file can change after verification or after the CLI exits. Add explicit `sequential_snapshot_not_atomic_or_future_file_lock=true` metadata to every valid triplet verdict so external reviewers cannot misinterpret a local consistency check as permanent custody or GitHub policy attestation.

Four new source-defined tests (**6,721 proposed cumulative methods**) verify the non-atomic caveat and simulate tampering of human/compact files between sequential checks; both direct compiler and CLI reject the injected approval, with no stdout on invalid input. Valid output is always `BLOCKED_NO_EXECUTION_PERMISSION` and nonzero exit 3, never dispatch/trading permission. Signed evidence custody and independent administrator/security review remain external.

This does not establish the exclusive mutable-main lock, installed runner OS isolation, frozen provenance, fresh 2023/run385/attempt1 inventory or separate human approval. All eight external proof packages #779/#820/#821 remain MISSING; no protected annual data/dispatch, ref/workflow/ruleset edits, broker/demo/live order, money or profit. Exact-head Phase3/full regression CI and qualified review required.
