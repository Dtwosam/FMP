# DEC-1938 — Reject symlinked Phase3 artifact output roots

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit source/tests/docs child of PR #2186 at `429f18cf45090be57c7c8c4d21636b5dda5c5806`.

`write_backtest_artifacts` previously accepted a symlink as `out_dir` and transparently followed it, potentially writing apparently local evidence into an unintended directory. After run prevalidation and before directory creation, explicitly reject an existing symlink **at the output-directory leaf** with `ValueError`. Preserve ordinary direct existing and new output directories. This narrow check does not prevent symlinks in ancestor directories or a malicious concurrent swap and does not demonstrate independent runner mount/UID isolation. Prior unique temporary-file protection remains in force.

Two synthetic source-defined tests cover denied output-root symlink without touching a sentinel in its target and compatibility with a normal existing directory. **6,968 cumulative proposed methods.** Own exact-head Phase3/full historical-general CI and independent qualified file-security review mandatory.

Phase8A issues #779/#820/#821 and eight administrator/ref/installed workflow/real privileged OS isolation/provenance/fresh one-shot/human proof packages remain MISSING/BLOCKED. Protected 2023/run385/attempt1 and later annual research, Strategy V1 economics, shadow/demo/Phase10/11 and live broker funds, installed GitHub ref/workflow/ruleset/runner changes remain unauthorized. No protected dispatch, trading or money.
