# Phase 1 Full Acquisition Trigger

This file exists only as a controlled GitHub Actions trigger surface for Phase 1 raw-data persistence.

- Ordinary edits/creation without `[phase1-full]` in the commit message run the bounded cloud smoke only.
- A commit whose message contains `[phase1-full]` starts the sharded full-history acquisition.
- Do not use the full trigger until the main-branch cloud smoke and private-bucket observation gates pass.

**Full-history trigger issued:** 2026-08-22 after the main-branch OIDC cloud smoke PASS and independent private-bucket observation.
