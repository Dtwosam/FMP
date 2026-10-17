# DEC-1483 — Deterministic JSON nesting admission in offline CI bundle review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Forward-only one-commit tests/docs child of #1728 at `f949ca64ae2b024b1f5ebc6733b3306bbee3adc8`. Ten additional synthetic unittest methods; **2,079 proposed source-defined test methods**.

## Observed failure

Full historical/general CI on #1727 and #1728 failed in `test_excessively_nested_json_is_diagnostic_not_recursionerror`: 1,600 levels of JSON arrays returned `BUNDLE_SHAPE_UNREVIEWED` rather than `BUNDLE_JSON_GRAMMAR_UNREVIEWED`. Python's JSON parsing recursion limit depends on process state, including earlier tests that adjust `sys.setrecursionlimit`; catching `RecursionError` alone does not enforce a portable maximum JSON nesting policy. Phase 3 acceptance passed on each PR but does not override failed general CI.

## Correction

Before `json.loads`, scan caller-provided JSON text at most once and reject more than 512 nested array/object containers with the existing safe grammar diagnostic. Count only structural brackets outside quoted JSON strings and respect escape/backslash runs. Reject unmatched closing brackets early; delegate full syntax, mismatched delimiters, duplicate keys and nonfinite constants to the existing decoder. Existing text-length and resource limits still run first. No untrusted payload appears in diagnostics.

Ten regression methods exercise arrays, objects, mixed containers, exact nesting boundary, quoted brackets, escaped quotes/backslashes, bad closing delimiters and a valid synthetic envelope. The offline verdict still grants **no protected annual authority** even when source-consistent. This is a source-evidence review behavior fix, not provenance or authenticity proof.

Own head-associated PR merge-tree Phase 3/full historical/general CI and independent review required. DEC-650/#820 protected original OS no-write and DEC-651/#821/#779 exclusive immutable one-shot 2023 run385/attempt1 server admission remain **BLOCKED**. No protected run/dispatch/retry, protected data/artifacts, installed workflow/security changes, merge, deployment or trading.
