# DEC-1916 — Pre-serialize synthetic Phase3 artifacts before filesystem mutation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2164 at `26c3208727feff971be1f95aca3f7bac190cf9d6`.

The artifact writer previously created the output directory before checking that the run could be serialized. Invalid metrics such as non-finite net profit, a malformed run object, or unsupported identity objects could leave a misleading empty output directory. Require an exact `BacktestRun` record and construct all four evidence payloads before the first directory creation. Existing deterministic payload bytes, manifest hashes and normal output layout are untouched; this does not claim crash-atomic multi-file publication.

Three synthetic no-I/O failure tests cover untyped/hostile run objects, nonfinite metrics, and unserializable identity values, denying filesystem directory creation. **6,910 cumulative proposed source-defined methods**. Own exact-head Phase3 and full historical/general CI plus qualified independent review are required; source-only mocks cannot prove real runner isolation.

All #779/#820/#821 independent Phase8A blockers and eight real security proofs remain MISSING/BLOCKED. Accepted annual research still ends 2022/run384; protected 2023/run385/attempt1, later annual research, Strategy V1 economics, shadow/demo/Phase10/11 brokers/real capital remain forbidden. No protected runs, installed workflows/refs/rulesets/runner or broker changes occurred.
