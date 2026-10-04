# Phase 8A — Explicit Successor Installer Recovery

**Date:** 2026-10-04  
**Status:** SOURCE-READY REPAIR / ANNUAL RUN 378 UNCONSUMED  
**Decision:** DEC-530

## Live failure

DEC-529 explicitly recovered the missed successor chain after successful 2015
annual run 377.

The manual successor runs were:

- DEC-513 reviewer run `37200350839`: success;
- DEC-514 activation-plan run `37200374023`: success;
- DEC-518→521 installer run `37200408776`: failure;
- DEC-529 orchestrator run `37200339487`: failure because the installer failed.

The installer copied the exact two authorized runtime files and verified both
resulting blobs, but its mutation inventory used only
`git diff --name-only`. Git does not report the newly created, untracked 2016
runtime gate through that command, so the guard observed only the modified
runtime file and failed before commit or push.

No repository mutation reached main and annual run 378 was not dispatched.

## Repair

DEC-530 keeps the two-file mutation contract unchanged and changes only the
inventory proof to combine:

- tracked modifications from `git diff --name-only`; and
- untracked files from `git ls-files --others --exclude-standard`.

The combined set is sorted and must still equal exactly the two authorized
paths.

The explicit successor orchestrator is rebound to exact workflow run 2 /
attempt 1. Before any action it proves the exact failed DEC-529 orchestrator,
successful first DEC-513 and DEC-514 manual runs, and failed first installer
run. It then creates fresh manual successor runs on the repaired main rather
than rerunning any failed workflow attempt.

Manual installer recovery is limited to installer workflow run 2 / attempt 1
and a fresh successful DEC-514 workflow-dispatch run 2.

DEC-522 is also rebound so its unique successful installer may have originated
from either the normal `workflow_run` path or the explicit
`workflow_dispatch` recovery path. More than one successful installer still
fails closed.

## Authority boundary

No annual workflow dispatch is performed by DEC-530 itself. The only annual
run-378 dispatch remains inside the existing DEC-518→521 installer chain after
the exact runtime install, post-install planning, and live inventory checks.

No rerun/retry of failed installer run 1, no annual run 379+, no 2017+
execution, no strategy synthesis or promotion, no broker mutation, no order
placement, no real-money action, and no trading authority is added.
