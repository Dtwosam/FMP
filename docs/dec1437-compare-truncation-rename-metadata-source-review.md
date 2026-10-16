# DEC-1437 — Exact diff truncation and rename metadata fail closed

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test/docs child #1660 DEC-1436 at acfcfe53facecf3b097cf965007625310ee33e8c. Adds **nine source-defined tests**, now **1,612 proposed methods**.

The DEC-1433 compare review accepted compare.too_large value zero by equality with Python False when using membership in (None, False); a malformed integer false could therefore be mistaken for a reviewed Boolean untruncated flag. Its rename path review also allowed a status=renamed entry with no previous_filename, or a non-renamed entry carrying an unexpected previous_filename.

This forward-only fix checks compare.too_large using strict identity (only None/False), requires an explicitly distinct valid docs/tests previous path for status=renamed and rejects a previous_filename on other statuses. Nine pure in-memory regression fixtures exercise number/list impostors, correct explicit False, missing/equal/empty rename origins, non-rename previous filename and valid distinct documentation renames. The parent source test case still admits canonical source-only changes and blocks production/annual workflow paths.

The test-only reviewer consumes untrusted caller snapshots, does not independently authenticate GitHub, is not a runtime OS isolation proof, and cannot enforce or authorize a 2023 annual one-shot dispatch. Exact-head Phase3/full historical/general CI and independent qualified review are required. DEC-650/#820 actual OS original no-write and DEC-651/#821/#779 immutable exclusive 2023 run385/attempt1 admission remain **BLOCKED**. No protected originals/artifacts, annual dispatch/retry, installed YAML/branch/ruleset/permissions, merge, production or broker/trading work.
