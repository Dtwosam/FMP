# DEC-647 — Disposable least-privilege UID containment proof (DRAFT / NEVER MERGE)

**Entirely offline proof, not a deployment recipe or privileged runner change.** Stacked on [DEC-646 draft #816](https://github.com/Dtwosam/FMP/pull/816). Two new files (one eight-method synthetic test module and this document); no installed workflow, 23 audit wrappers, runtime, trading API, tag/ruleset or annual history change.

## Why this proof matters

DEC-644 showed that dirfd anchored audit output can be relocated into a synthetic checkout when the actor can rename a directory there. DEC-646 showed that the same Unix file owner can restore a temporary `chmod 0555` checkout to writable and repeat that attack. This source-only experiment shows **a different, enforced identity boundary** can prevent the reparent rename under a deliberately restricted actor in a disposable fixture.

## Exact disposable fixture semantics

When the current test process is already root in an isolated local test environment **and** `setpriv` is installed, it creates two throwaway directories inside `TemporaryDirectory`: a root-owned mode-0755 **synthetic** checkout with a sentinel file and an external report parent owned by UID/GID 65534. A child interpreter launches through `setpriv --no-new-privs --bounding-set=-all --reuid=65534 --regid=65534 --clear-groups` and never receives the parent/root identity.

Six scoped child checks verify: (1) restricted actor **cannot** reparent an external directory into root-owned checkout; (2) when synthetic checkout becomes mode 0777, the same actor **can** reparent it, proving the test is not falsely denying all renames; (3) restricted actor can still write an allowed external report; (4) it cannot chmod root-owned checkout to 0777; (5) it cannot restore root-owned mode-0555 checkout to writable; and (6) its `/proc/self/status` reports `NoNewPrivs: 1` and zero effective capabilities. Every test checks that the synthetic inventory sentinel is unchanged.

Two additional nonprivileged/static tests always run: inspect the frozen annual workflow and observe it does not explicitly drop runner UID capabilities before its three ordinary checkouts, and check this test module contains no workflow-dispatch, broker-order, sudo, token or real-checkout write primitives. The six child checks **skip** on GitHub's ordinary unprivileged `ubuntu-latest` test runners rather than seeking sudo or escalating. Consequently, **a passing GitHub suite may have six skips**; those skips must not be mistaken for GitHub-runner isolation evidence.

## Evidence and limits

In the local isolated root test container, **8/8 methods passed**. The published Git blob of the tested Python source is `086b20be355bc982725dae8f6cd8ee48f90ba917`. No real source checkout or protected annual data was accessed or mutated. Source and sink parents are created under disposable TempDirectory, never at a real repository path. The local check proves **only** that an unprivileged actor under this fixture's Unix ownership and capability constraints lacks the ability to rename a directory into checkout while preserving output-parent writes.

This is not a claim that the current GitHub runner is isolated: GitHub-hosted Ubuntu VMs provide passwordless sudo to their ordinary runner identity, and `GITHUB_WORKSPACE` can be modified by steps (https://docs.github.com/en/actions/reference/runners/github-hosted-runners). If an untrusted script can regain privilege, access writable checkout aliases or remount, the fixture proof does not apply. A trustworthy setup, privilege drop and mount ownership boundary must be independently specified, installed and verified **for each annual job** before asserting checkout immutability. No such installation occurs here.

## Hard gates

Original #796–800 lack independent security reviews; main remains unprotected with zero rulesets at last observation; annual run385 remains unconsumed. None of the source-only stacked draft PRs #809–817 is authorized for merge, annual dispatch/retry, protected evidence reads, brokerage, trading or privilege changes. These tests are evidence of a possible **threat-model restriction**, not a complete security gate.

## DEC-648 experimental environment isolation follow-up (candidate, not yet branch head)

The initial DEC-647 `setpriv` subprocess dropped UID/GID and capabilities but inherited its parent process environment by default. That did **not** prove that credentials or sensitive environment variables would be absent from the restricted child. A candidate follow-up supplies a three-key environment allowlist (`PATH` from `os.defpath`, a disposable synthetic `HOME`, and `PYTHONDONTWRITEBYTECODE=1`) to the child, plus tests demonstrating that a synthetic parent-only secret is not visible inside the dropped-privilege child and that the allowlist contains no unexpected keys. In an isolated local root sandbox, the explicit-environment pattern preserved `NoNewPrivs=1`, zero effective capabilities and withheld the synthetic canary. This does not certify secret isolation for actual GitHub-hosted annual jobs: file descriptors, process arguments, host-level credentials and network are separate threat channels requiring review. Neither this documentation nor author-side tests authorizes running or merging the annual workflow.
