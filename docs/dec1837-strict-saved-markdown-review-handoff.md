# DEC-1837 — Independently revalidate saved BLOCKED Markdown review handoffs

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2083 at `f57cd2a64a29eca969d2c542fc1451841b007751`.

The offline tool previously revalidated saved full JSON and saved compact proof requests, but not the human Markdown form. Add `--verify-markdown FILE`, using the existing bounded no-follow regular-file reader, to compare saved **exact CLI Markdown bytes** with a fresh canonical human report derived from all seven pinned historical materials. The CLI's final newline is included deliberately. This denies altered approval wording, CRLF changes, extra content and symlink/oversized files, even if a saved JSON fingerprint was recalculated.

Valid canonical saved Markdown returns the same human review packet, still **BLOCKED and exit 3**. Invalid evidence or combinations with other verification modes or source overrides return 2 with no stdout. Five tests (6,706 cumulative proposed source-defined) cover exact round-tripping, approval/format tampering, filesystem safety, incompatible arguments and offline/read-only behavior. No external review evidence has been accepted; neither this Markdown check nor local SHA-256 identity is an independently signed attestation.

External issues #779/#820/#821 and all eight independently authenticated proofs remain MISSING. Protected 2023/run385/attempt1, later research, Strategy V1 economics, shadow/demo/Phase10/Phase11 broker/live trading remain BLOCKED. No installed GitHub ref/workflow/ruleset/runner modification, protected data read or order. Exact-head Phase3/full regression CI and qualified review required.
