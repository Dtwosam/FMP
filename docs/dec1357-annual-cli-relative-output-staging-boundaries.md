# DEC-1357 — Concrete checkout-relative write locations across the installed-source annual CLI and jobs

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test+docs child of #1580 DEC-1356 at `7a5935101cc4ff38d0511d319fd9c52db56efcfb`, proposed **989 source-defined test methods** (+6). Tests read **tracked source only**, do not invoke the annual CLI, workflow, GitHub API or market-data artifacts.

The current CLI's `_write_json` and `_write_bytes` create parent directories and write passed destination files. The **three-job checked-in** `.github/workflows/phase8a-annual-pattern-catalogue.yml` uses checkout-relative output and staging directories:

- **Preflight**: `.preflight/preflight.json`, `.preflight/prior-freeze.json`, `.prior-freeze/artifact` and captured source-snapshot metadata; the source invokes `mkdir -p` and `gh api` before the later separate execution gate.
- **18 cell invocations**: `.downloads`, `.feature`, `.outcome`, `.feature-evidence`, `.outcome-evidence` and `.result/{cell-evidence.json,catalogue-payload.json}`; artifacts are staged/extracted into checkout-relative paths.
- **Freeze**: `.cell-results` download path, compile output `.annual-freeze/annual-freeze.json`, and upload. The CLI's `_cmd_freeze` performs its own require-execution check before opening the cell summaries, but the workflow **already performed checkout and runtime install** before its separate recheck.

Six regression methods pin these concrete source code/read-write paths and ordering. They do **not** access the actual relative directories, run code against protected annual data, simulate successful annual execution or attest server-installed workflow identity. They exist because DEC-650/#820's proposed trusted staging→OS-restricted child→trusted uploader architecture requires the runner to relocate *all legitimate writable scratch/output* separately from the independently protected original checkout/input. Simply mounting the current checkout read-only would break the current CLI's expected output writes.

Protected original no-write DEC-650/#820 and immutable independent 2023 run385/attempt1 admission DEC-651/#821/#779 remain **BLOCKED**. These source-only tests and green CI cannot prove kernel-denied writes or fix the main-ref race. Each exact SHA needs successful completed Phase3 AND full historical tests and qualified independent review; prior historical failed SHA classifications retained. No protected annual source/evidence access, run/test/retry/rerun/dispatch, workflow/ruleset/permission install, trading, broker actions, merges or promotion.
