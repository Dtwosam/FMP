# DEC-1973 — Repair first-payload size-before-hash regression

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Source/tests/docs child of PR #2221 at exact parent `73a442828124a49b5b7d425588f0114611a9bd0b`. No protected research, GitHub security/admin workflow mutation, strategy promotion, broker activity or capital movement.

## Confirmed failing historical check

Full-regression run [39509307220](https://github.com/Dtwosam/FMP/actions/runs/39509307220) for PR #2212 failed one source-defined test: `test_verifier_refuses_forged_payload_length_before_hashing`. The mock forbade every `hashlib.sha256` call while the forged size was in `trades.jsonl`, the last canonical evidence payload. Earlier, correctly sized files were allowed to hash; therefore this assertion was ill-scoped. The implementation also created a digest object *before* checking its pinned descriptor size.

Repair the test to forge `metrics.json`, the first canonical payload, and move the verifier's hash initialization after the pinned `fstat` size comparison. This checks the intended invariant: **no hashing of a size-invalid first payload**, while unaffected files still hash normally.

The previously failed CI run remains **FAILED** permanently. This draft must pass its own exact-commit Phase3 and historical/general suites; Phase3 green alone is not full regression proof.

## Unchanged gates

Phase8A remains blocked on issues #779, #820, #821 and eight independent external proof requirements. Accepted annual research ends at 2022/run384. Protected 2023/run385/attempt1, later research, Strategy V1 economic validation, shadow/demo/live trading and real capital are not authorized.
