from __future__ import annotations

"""DEC-635: exclusive-create leaf-report helper (not an authorization gate).

Callers enforce source-checkout boundaries before invoking this helper.
This does not protect parent-directory/symlink replacement races.
"""

from pathlib import Path


def write_once_external_report(target: Path, content: str, conflict_message: str) -> None:
    """Write a new report once, never truncate an already-existing report.

    An identical existing report is returned without modification. O_EXCL
    semantics from Path.open('x') prevent a concurrent new leaf file from
    being truncated between initial exists() and creation. This does not
    atomically publish a fully written file or lock parent paths.
    """
    if target.exists():
        try:
            identical = target.read_text(encoding="utf-8") == content
        except (OSError, UnicodeError):
            raise ValueError(conflict_message) from None
        if not identical:
            raise ValueError(conflict_message)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("x", encoding="utf-8") as output:
            output.write(content)
    except FileExistsError:
        try:
            identical = target.read_text(encoding="utf-8") == content
        except (OSError, UnicodeError):
            raise ValueError(conflict_message) from None
        if not identical:
            raise ValueError(conflict_message) from None
