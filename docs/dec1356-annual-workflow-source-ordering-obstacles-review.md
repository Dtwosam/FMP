# DEC-1356 — Source-only ordering audit of the existing three-job annual workflow

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit child of #1579 DEC-1355 at `453319ed04243a8e6fcfc5e3bbf33fb14105f9bf`. Adds one **pure source-text analyzer**, seven source-defined unit tests and reviewer documentation; **983 proposed test methods**.

Unlike symbolic trust claims, this audit reads the *actual checked-in source* `.github/workflows/phase8a-annual-pattern-catalogue.yml` **only inside the test**, without dispatching, fetching protected evidence, installing packages, or running a historical job. The production runtime/installed workflow is never modified. `scripts/dec1356_annual_workflow_source_order_audit.py::audit_annual_workflow_source` accepts a string and returns **BLOCKED on every input**; it identifies actual source ordering:

- `annual_preflight`, `annual_cell`, `annual_freeze` all place **Checkout** first, followed by a `GITHUB_REF=refs/heads/main` test, not an independently verifiable admission **before** checkout.
- All three install Python requirements and the package **before** separately checking `require-execution`.
- `annual_preflight` calls **Fetch exact accepted EXP-044 source snapshots** (metadata) **before** its execution authorization check.
- The existing matrix source lists exactly 18 cells, but a source-level matrix count cannot authenticate reviewed workflow identity or authorize the nonretriable unique run.
- Missing/duplicated jobs, changed matrix size, missing/late checks and nontext inputs remain negative. Even inserting a hypothetical precheckout step into a *string* can never prove a real GitHub server-side lock or independent protected storage no-write.

The static audit's exact *step names* and source section parsing are intentionally narrow to the existing checked-in workflow; it is not a general YAML validator and does **not** authenticate the installed server-side workflow version. The real fix would require independently reviewed OS/storage policy under DEC-650/#820 and a separately installed server-enforced immutable admission contract under DEC-651/#821/#779, potentially changing workflow order and staging after prior independent authorization. No such change occurs in this draft.

Each exact SHA requires completed successful Phase3 AND full historical CI, qualified independent security review and retained prior failed SHA verdicts. Protected annual **run385 attempt1 = DO NOT DISPATCH**; no protected data access, workflow/ruleset/permission mutation, broker/trading, merges or promotions.
