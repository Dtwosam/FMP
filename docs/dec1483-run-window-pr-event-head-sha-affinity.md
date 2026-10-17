# DEC-1483 — Run-window evidence requires PR event and shared head association

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit source-only tests/docs child #1706 DEC-1482 at `58fe6017fa99c82c70f5cdd74fd19fba87ce19b7`. Five new unit test methods, **2,054 proposed source-defined methods**.

The standalone DEC-1478 workflow-run lifecycle reviewer checks exact supported workflows, positive run IDs, first-attempt success and UTC source-log time boundaries. It did not by itself reject a `workflow_dispatch` event or two green workflow runs whose `head_sha` metadata refers to different PR heads. Other reviewers in the full DEC-1440 composite check those associations, but standalone timeline consistency must not imply a single tested PR source when the run metadata disagrees.

Both runs now require `event=pull_request`, their head SHA must be exact lowercase 40-hex, and the two required workflows must share the same PR-head **association**. The observed unprotected successful #1698 run fixture adds its actual PR event and head `fa1cabab52e547b5f0a6f4cf39749df818529b59`; five tests reject event/head inconsistencies. This is not proof the runners directly checked out that head: both actually checked out a different PR merge commit with identical source tree in the inspected case.

No protected 2023 annual dispatch/retry or original data/archive/artifact downloads, and no installed workflows, GitHub security policy, deployments, merging or trading. DEC-650/#820 real OS protected-original no-write and DEC-651/#821/#779 exclusive immutable preallocation one-shot **2023 run385/attempt1** admission remain **BLOCKED**. Own head-associated PR merge-source-tree Phase3/full historical CI and qualified external review required.
