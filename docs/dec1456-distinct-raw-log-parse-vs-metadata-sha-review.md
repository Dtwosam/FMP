# DEC-1456 — Distinguish malformed checkout log from contradictory SHA

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test/docs child #1679 DEC-1455 at 2da5194a283d90290d91b3f1a151e615ea66369e. Two newly defined tests, now **1,823 proposed source-defined methods**.

The DEC-1455 raw-runner-log composite added a negative fixture that altered the full fetched immutable merge SHA but left the following short HEAD checkout abbreviation unchanged. Such a log is invalid on its face: the DEC-1454 parser correctly rejects it with RUNNER_LOG_CHECKOUT_SHA_MISMATCH before the composite can produce the fixture's originally asserted RAW_CI_RUNNER_LOG_METADATA_MISMATCH. The negative test therefore conflated two distinct fail-closed stages.

This forward-only correction changes the original fixture to use a **coherently changed full and abbreviated SHA**, which passes syntax parsing but still differs from independently supplied expected merge metadata; the originally intended cross-evidence mismatch diagnostic then applies. Two additional regressions assert that an internally contradictory log is rejected at parse stage and a validly formatted but different Phase3 merge log is rejected at metadata-comparison stage. This is a source-test fixture correction, not a weakening of the checks. Original #1679 CI findings remain unchanged.

Own PR merge-source-tree Phase3/full historical CI and qualified review required. DEC-650/#820 real protected original OS no-write and DEC-651/#821/#779 exclusive immutable one-shot 2023 run385/attempt1 admission remain **BLOCKED**. No protected annual execution/retry, originals/archives, installed workflow/branch/ruleset/security changes, merge, deployment or trading.
