# DEC-1833 — No writable local opens in seven-source review and saved verification

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2079 at `0a5723c3c2b05e434ed0e28d1b80e0e5ff59ee8b`.

The seven-source BLOCKED security index now supports local construction, JSON/Markdown/compact request rendering, and strict verification of saved full and compact JSON. These operations must not write or create files. Four new unit tests wrap `os.open`, rejecting write/read-write/create/truncate/append flags while permitting the source reader's read-only no-follow dirfd operations. The test scope preserves `os.supports_dir_fd` capability under the mock; otherwise replacing the callable would cause a false negative before any access.

The tests cover direct compilation, saved full JSON verification, saved compact proof request verification and all five valid CLI variants. All must remain permanently BLOCKED (exit 3), produce only stdout and not touch writable files. These tests are **local Python regression guards**, **not a real runner OS UID/caps/mount/credential witness**, proof of current branch/ref protection, externally authenticated evidence or trading authorization. Four new tests (**6,698 proposed source-defined cumulative**).

All independent security proofs, issues #779/#820/#821 and 2023/run385/attempt1 remain MISSING/BLOCKED. No protected research, real workflow/ref/ruleset/security changes, broker/demo/live order, capital or profitability. Exact-head Phase3/full regression CI and qualified independent review required.
