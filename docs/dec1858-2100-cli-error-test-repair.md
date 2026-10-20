# DEC-1858 — Repair historical/general test assertion for CLI fail-closed prevalidation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only test repair of PR #2104 at `de12321aca7f0d237eb5d52977e58c3e0b8e0db4`.

The full historical/general suite for PR #2100 definitively **FAILED** with two subtest assertion failures in `test_argparse_rejects_control_chars_without_echoing_them`. The earlier DEC-1852 C0/DEL prevalidation correctly returns `BLOCKED: unsafe or non-string review argument` for an embedded newline or ANSI Escape character before argparse is invoked; the existing DEC-1850 test asserted the narrower `BLOCKED: invalid` message. Both paths were still status 2, empty stdout and a single safe diagnostic line. Keep this historical failure recorded.

Replace the over-specific assertion with a shared `BLOCKED:` check and conditional exact message assertions for C0/DEL versus ordinary invalid argparse input. This is **test-only** and does not loosen any CLI guard, process permission, protected-market constraint or backtesting cost contract. No new test methods; the #2104 lineage remains **6,756 proposed source-defined methods**.

All eight independent external security packages and #779/#820/#821 remain MISSING/BLOCKED. Protected 2023/run385/attempt1, downstream economic selection, shadow/demo/live broker orders, workflow/ref/ruleset changes and real money remain unauthorized. Own exact-head Phase3 and full historical/general regression CI and qualified review required.
