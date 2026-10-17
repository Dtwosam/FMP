# DEC-1488 — Repair stream fixture and fail-closed runtime stream errors

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit forward-only tests/docs child of #1733, exact parent `8956d0f007fd8ec879833d2ef537cc0a736dce1b`. Seven additional synthetic unittest methods; **2,124 proposed source-defined methods**.

#1733's full historical/general CI failed with an `AttributeError` inside the test `test_str_subclass_chunk_fails_type_boundary`: its nested `Fake.read` method referenced `self.bundle`, but `self` was the fake stream rather than the unittest fixture. Move the synthesized JSON value into the enclosing test's closure; keep the intended strict `type(part) is str` rejection. The failure is test-fixture scoping, not a successful source-consistency or annual authorization result.

Also sanitize `RuntimeError` raised by an input stream, including an error after an otherwise valid JSON prefix. Seven more tests cover subclassed EOF, subclassed partial prefixes, safe diagnostics, early/late runtime errors and positive controls for ordinary short reads and empty-string EOF handling. A strict text input failure is a nonauthorizing diagnostic and never echoes stream error messages or evidence.

Own PR head-associated Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 annual run385/attempt1 GitHub server admission remain **BLOCKED**. No protected execution/dispatch/retry, originals/artifacts, installed workflow/security changes, merges, deployments or trading.
