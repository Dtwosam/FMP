# DEC-1479 — Local stdin-only review of portable offline CI evidence JSON

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child #1724 DEC-1478 at `64eea94fafa950ea2230cde8c3282e2532893827`. Adds **12 source-defined methods**; proposed total **2052**.

The portable offline source bundle from DEC-1478 can now be reviewed through a simple, deterministic **local stdin-only command**, without any GitHub API, browser, network connection, protected artifact fetch or workflow dispatch:

```sh
python tests/test_dec1479_offline_ci_bundle_stdin_command.py < bundle.json
```

The command reads at most the DEC-1478 capped number of characters, validates JSON/category/binary source/run-key structure, runs the existing fifteen-source composite consistency check, and writes only a compact JSON verdict to stdout. It never echoes input logs, blobs, secrets or archive content and does not accept command-line paths or URLs. Exit status **0 means only that caller-supplied evidence is internally source-consistent**. Exit **2** means malformed, incomplete or inconsistent evidence. **Neither exit code is permission to run protected research.**

Twelve new synthetic unittest methods cover clean input, empty/null/malformed/duplicate JSON, missing categories, bad run map keys, tampered source bytes and job logs, input-size cap and permanently false independent OS/server/annual authorization flags. The stdin adapter does not authenticate the identity, source or integrity of the provider: independent qualified GitHub job and immutable object observations are still mandatory.

Its own head-associated PR merge-source-tree Phase3/full historical/general CI and qualified independent review required. DEC-650/#820 actual protected original OS no-write and DEC-651/#821/#779 immutable exclusive server-side 2023 annual run385/attempt1 admission remain **BLOCKED**. No protected originals/archive access, annual dispatch/retry, installed workflow/security mutations, merge, deployment, trading.
