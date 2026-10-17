# DEC-1499 — Correct internal-space filename test contract after CI

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict forward-only one-commit tests/docs child of #1744, exact parent `979ef6371ec6a9aa5295cbf7b2d247a992e40b07`. Nine synthetic regression tests: **2,235 proposed source-defined methods**.

#1740 and #1743 both completed Phase 3 successfully but the full historical/general suite failed the inherited DEC-1494 test `test_trailing_space_in_segment_is_rejected`. Its list incorrectly labeled `tests/module .py` as a **trailing** space. In fact its component ends in `.py`: the space precedes the extension. The existing cross-platform validator intentionally rejects whitespace at the **end of a component** and accepts internal spaces. This is a false test assertion, not evidence of admitted traversal or protected execution.

Replace the incorrect test case with a truly trailing whitespace component and add nine regression tests for internal spaces before extensions, ordinary multi-word filenames, space-only components, multiple trailing spaces, trailing dot components, and all protected annual authorization flags permanently false. Preserve the original validator unchanged; do not weaken its trailing-space rule.

Own exact-head Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 independently witnessed original-file OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No annual dispatch/retry, protected originals/archive/artifacts, installed workflows/security settings changes, merges, deployment or trading.
