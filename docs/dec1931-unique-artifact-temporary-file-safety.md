# DEC-1931 — Unique artifact temporary files and failure cleanup

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of PR #2179 at `d8367d5eff242d4aac8e1b6d99d88406e795ae4b`.

`_atomic_write` formerly wrote into predictable `.<artifact>.tmp` paths via `Path.write_bytes`. A pre-existing symlink at that path could redirect writes outside the intended artifact directory. Use a uniquely, atomically created destination-directory temporary file via `tempfile.NamedTemporaryFile`, then `os.replace` to the requested output path. Clean up the uniquely created temporary path on success or error. Existing final artifact filenames, deterministic bytes/hashes, manifest format and per-file atomic replacement remain unchanged. This is not OS-level isolation and does not claim multi-file transaction atomicity or malicious-root defense.

Two synthetic source-defined regression methods plant a predictable temporary symlink and verify its target was not overwritten; and simulate a failed replacement verifying temporary cleanup. **6,953 cumulative proposed source-defined methods.** Own exact-head Phase3 and full historical/general CI and qualified independent file-security review mandatory. The review must not conflate temp-path hardening with verified privileged runner OS controls.

Phase8A #779/#820/#821 and eight independent security proof packages remain MISSING/BLOCKED. Protected 2023/run385/attempt1, subsequent discovery, Strategy V1 economics, shadow/demo/Phase10/11 brokers/live capital and installed GitHub workflows/rulesets/refs/runners remain unauthorized. No protected run, broker order or money action.
