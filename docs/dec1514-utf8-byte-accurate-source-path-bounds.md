# DEC-1514 — Byte-accurate UTF-8 source path component limits

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1759 at `260ab22cfe2e9e112486fb1cb6753ffad131a321`. Adds **10 synthetic unittest methods**, bringing lineage to **2,380 proposed source-defined methods**.

Previous DEC-1495 bounded source path lengths in Python code points, not UTF-8 bytes. A path with multibyte Unicode may be short in code points yet exceed common filesystem component limits. Add conservative lexical UTF-8 byte budgets (255 bytes per component, 4096 bytes per complete relative path), in addition to existing 4096-code-point source length, NFC, forbidden Unicode controls/variation selectors, casefold aliases and mapped-source checks. Reject malformed/unencodable Python strings with the existing `BUNDLE_SOURCE_PATH_UNREVIEWED` code. No file is ever opened or resolved.

Ten tests cover ASCII and Unicode exact/over per-component thresholds, total UTF-8 path overflow, changed-source and CI-workflow map rejection, surrogate refusal, safe stdin output and clean synthetic source-only consistency. These conventions intentionally prioritize portable evidence labels and never establish provider provenance, independently witnessed original OS no-write or protected annual-run admission.

Exact-head Phase 3 and full historical/general CI and independent qualified review required. DEC-650/#820 witnessed protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected annual runs/retries, original/archive/artifact reads, installed workflow/security changes, merges, deployment or trading.
