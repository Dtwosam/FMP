# DEC-644 — Output-directory reparenting counterexample (DRAFT / NEVER MERGE)

This is a negative-witness-only documentation/test branch stacked on #813. It changes **no live writer, CLI wrapper, installed workflow, annual runtime, or one-shot run385**. All manipulated directories are disposable under TemporaryDirectory. Do not merge.

## What DEC-642 and DEC-643 proved

Directory-descriptor anchoring holds the original directory inode when its pathname is replaced with a symlink. The existing positive tests demonstrate that particular property. However, that is not a comprehensive guarantee that nothing can ever be written inside checkout.

## Adversarial reparent counterexample

An actor with permission to rename the already-open external report directory INTO the checkout can change the filesystem location of the very inode the report writer pinned. Stage creation and `os.link` relative to that descriptor subsequently publish the report in the renamed directory now **inside a synthetic checkout**. This was reproduced locally and is now captured as a deterministic source-only negative regression using the actual shared helper.

A further `Path.resolve()`, `realpath()`, `/proc/self/fd` or directory pathname check can be raced by another rename after checking; do not describe those as complete solutions.

## Threat-model and review gates

An adversary able to rename into the checkout already needs destination-directory permissions and may be able to write there directly. Nevertheless **the unconditional checkout-inventory invariant is false under that threat model**. Independent security review must decide the trusted checkout permissions/ownership, whether a read-only checkout mount or separate filesystem identity is required, and how to enforce/report that boundary without affecting source-only audit usability.

The DEC-643 anchored writer remains a security experiment with a documented unresolved residual risk. Parent drafts #809–813 and this #814 are NEVER MERGE. #796–800 still lack independent review, main remains unprotected with no rulesets at last read, and annual run385 remains unconsumed. No workflow dispatch/retry, branch/ruleset/tag mutation, protected dataset access, broker, live trade or merge is authorized.
