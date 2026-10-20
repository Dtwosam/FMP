# DEC-1853 — Final re-read of every source-only saved review input

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2099, `be24c1d5572e1ac64dafcdc10b2a83d69995fc9e`.

The DEC-1839 three-file security review check validated full JSON, compact requests and Markdown sequentially. A file already checked could change before the later checks finished and the function would still return a BLOCKED consistency verdict. This proposal takes bounded no-follow byte snapshots of all three saved input files before the three existing strict canonical verifiers, then reads all three again **just before** returning the verdict. Any byte difference fails with an invalid-evidence exception, CLI exit 2 and no stdout. It also catches whitespace-only edits that remain semantically equivalent JSON.

This is **not** a transaction, file lock, exclusive custody attestation or a guarantee that an attacker cannot change a file after the final check; the previously explicit `sequential_snapshot_not_atomic_or_future_file_lock=true` remains unchanged. A mutation-and-restore between reads can still escape detection. Four adversarial tests, including two edits to already-validated files, a CLI failure path and a no-write/no-process/no-network canonical success case, bring proposed source-defined test methods to **6,748**.

A valid review remains **BLOCKED** exit 3. No installed workflow/security/ref changes, protected 2023/run385/attempt1, broker/demo/live order, real capital, strategy returns or external authorization. Eight independent administrator/runner/inventory/human proofs and issues #779/#820/#821 remain MISSING/BLOCKED. Own exact-head Phase3/full regression CI and independent qualified review required.
