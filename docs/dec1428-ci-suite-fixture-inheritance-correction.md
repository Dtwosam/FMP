# DEC-1428 — Keep CI job-step suite test counts auditable

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit source-test/docs child of #1651 DEC-1427 at 173188292cea4d0575bd5394fb0125a784b4aacf, three new methods, **1,526 proposed source-defined methods** in the draft lineage.

The DEC-1426 source-only test class originally inherited from the DEC-1425 synthetic PR snapshot test class just to reuse its setUp fixture. Python unittest also inherited all 18 of that parent class's tests, making the job-step test module *execute additional, unintentional duplicates* beyond its 16 new methods. DEC-1427 retained that accidental collection.

This forward-only correction uses unittest.TestCase as the job-step class base and calls the parent fixture's setUp method explicitly. It retains the actual DEC-1426/1427 24 job-step tests but prevents another execution of the DEC-1425 parent tests in that subclass. Three regression methods test the independence of the class, its 24 local test functions and the validity of the borrowed in-memory fixture.

This is a suite-structure cleanup, not evidence that either protected annual-run security blocker is solved. No installed workflow, GitHub settings, protected original or archive, annual dispatch/retry, merge or trading is involved. Own exact-head Phase3, full historical/general CI and independent review required. DEC-650/#820 OS original no-write and DEC-651/#821/#779 immutable exclusive one-shot 2023 run385/attempt1 admission remain **BLOCKED**.
