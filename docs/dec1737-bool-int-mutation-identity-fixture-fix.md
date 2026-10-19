# DEC-1737 — Boolean-vs-integer synthetic mutation identity repair

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent test/docs-only correction of #1983 at `e537e13172bb31274ee38c0a70d47cb8bf7d9a14`.

## Source of repeated historical/general CI failures

Completed full historical/general runs for #1977–#1983 reported the same single failure in `test_denies_boolean_attempt_one_type_confusion` from DEC-1729. The adversarial fixture changes the expected 2023/run385 `attempt` from strict integer `1` to Boolean `true`; Python's normal deep dictionary equality regards `True == 1`. The fixture's generic `assertNotEqual(modified, before)` therefore **fails before invoking** the independent strict-type test `test_2023_one_shot_is_strict_integer_not_boolean`. The underlying strict-type guard is correct.

## Narrow repair

Replace **only** the synthetic mutation-presence comparison with serialization to **strict, canonical JSON bytes as Python strings** under `json.dumps(..., sort_keys=True, separators=(",", ":"))`, checked for inequality. JSON preserves the difference between `1` and `true`, unlike Python equality. This does not loosen any of DEC-1728's actual validation or allow additional authority: the unchanged `with self.assertRaises(AssertionError): getattr(case, guard)()` still requires the target ledger guard itself to reject every forged approval, missing/extra field, wrong run identity or Boolean attempt. The unmodified original ledger remains unchanged and stays fully blocked.

Adds **zero source-defined test methods**; proposed total remains **6,022**. No source-of-truth, parser/runtime, workflow/security, GitHub ruleset/tag, protected history, annual run385, retry, broker/demo/live or trading change. Own exact-head Phase 3/full historical-general CI and qualified independent review required. This corrects fixture assertions; prior green Phase 3 does not certify full historical/general CI.
