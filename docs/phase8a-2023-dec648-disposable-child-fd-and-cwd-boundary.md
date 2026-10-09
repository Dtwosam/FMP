# DEC-648 — Disposable child cwd and inherited-descriptor boundary (DRAFT / NEVER MERGE)

This **source-only negative security experiment** is stacked on [DEC-647 draft #817](https://github.com/Dtwosam/FMP/pull/817), source base `1af1b6e4264c0ad0cea499e00ac8b83cc7d27224`. Only the DEC-647 disposable test module and this documentation file change. The real annual runner, workflow YAML, audit CLIs, external report implementation, permissions, protected evidence, trading, and main are untouched.

## Concrete gap

Explicit environment-variable allowlisting and a UID/GID/capability drop do **not** by themselves isolate a subprocess from the parent's **already-open descriptors** or inherited current working directory. A restricted process can read a descriptor passed to it without reopening a root-owned file by path; a different working directory may expose otherwise reachable relative paths. Those are distinct channels from environment inheritance and filesystem namespace reparenting.

## New bounded witnesses

All new filesystem reads/writes use only `tempfile.TemporaryDirectory` synthetic fixtures, never a real checkout or secret.

1. The normal restricted test child is now explicitly started with `cwd=self.root` and `close_fds=True`, in addition to the previous three-key explicit environment and `setpriv --no-new-privs --bounding-set=-all --reuid=65534 --regid=65534 --clear-groups`.
2. The child confirms its current directory is its disposable fixture, not the test parent's original checkout directory.
3. A synthetic, root-owned `0600` canary cannot be read by path as UID 65534.
4. Even when the parent marks an open canary descriptor inheritable, the ordinary `actor()` invocation closes it, and the child reports `closed`.
5. **Deliberate counterexample:** a *separate test-only subprocess* explicitly configured with `pass_fds=(fd,)` receives that same synthetic descriptor after the UID drop and reads the canary. This is evidence of a failure mode, **not** a secure pattern to deploy.
6. An always-run source test guards the ordinary actor against removal of its explicit `cwd`, `close_fds`, and environment allowlist.

The DEC-647 test module now contains **15 test methods** (11 under the existing root+`setpriv` skip gate, four always-run/static). The root-only cases **must skip** in nonroot GitHub CI; passing CI with skips is not evidence that the real Ubuntu annual jobs run in a sandbox.

## Local proof and CI interpretation

The four key behaviors (path denied, inherited descriptor closed, explicitly passed descriptor readable, child cwd confined to a synthetic directory) were reproduced in an existing isolated Linux root test container using synthetic-only data. The exact committed file's full regression and the GitHub PR synthetic merge still require separate verification. Run the module only in the existing unit-test workflow, which does **not** escalate privileges, or in an already-authorized disposable root test container:

```sh
python -B -m unittest -v tests/test_phase8a_annual_pattern_catalogue_2023_dec647_least_privilege_uid_boundary.py
```

A `pass_fds` test demonstrates why neither `NoNewPrivs=1` nor `CapEff=0`, an environment allowlist, or a file's `0600` mode establishes secrecy if the parent intentionally or accidentally hands down a readable descriptor. Closing ordinary descriptors in this *test harness* is defense-in-depth, **not** proof of production credential isolation.

## Independent-review acceptance gates

Before anyone considers actual annual execution, reviewers must independently establish the trust boundary in **all three workflow jobs** and evaluate inherited FDs, process arguments, `cwd`, readable checkout aliases, writable/mount aliases, network credentials, privilege escalation paths (including sudo), namespace and ownership changes, protected artifacts, and runner-specific resource access. The fixture neither tests all such channels nor installs any protection. In particular, a child confined by Unix ownership alone remains vulnerable if it retains reparent/remount or privilege-restoration authority.

The original #796–800 still require independent security reviews; [issue #779](https://github.com/Dtwosam/FMP/issues/779) tracks the unprotected mutable-main race and annual run 385. All stacked research branches #809–818 remain **DRAFT / NEVER MERGE**. No protected-data reads, dispatch/retry, ruleset or tag changes, broker operation, live/demo order, strategy promotion, or annual-run consumption are authorized.
