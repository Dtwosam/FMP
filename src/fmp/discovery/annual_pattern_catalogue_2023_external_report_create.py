from __future__ import annotations

"""DEC-640: publish complete external leaf reports without replacing existing files.

Callers enforce source-checkout boundaries before invoking this helper.
Parent-directory replacement and process-crash temporary-file cleanup are
outside this narrowly scoped filesystem contract.
"""

import os
import stat
from pathlib import Path
import tempfile


def _require_identical(target: Path, content: str, conflict_message: str) -> None:
    """Read only a regular existing report, bounded by expected report bytes.

    O_NONBLOCK prevents a FIFO/device from blocking at open, O_NOFOLLOW rejects
    last-component symlinks, and descriptor-based fstat avoids reading a file
    type different from the one opened. All failures are output conflicts.
    """
    expected = content.encode("utf-8")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    try:
        fd = os.open(target, flags)
        with os.fdopen(fd, "rb") as existing:
            info = os.fstat(existing.fileno())
            identical = (
                stat.S_ISREG(info.st_mode)
                and info.st_size == len(expected)
                and existing.read(len(expected) + 1) == expected
            )
    except (OSError, UnicodeError):
        raise ValueError(conflict_message) from None
    if not identical:
        raise ValueError(conflict_message)


def write_once_external_report(target: Path, content: str, conflict_message: str) -> None:
    """Publish an entire new report atomically at its leaf without clobbering.

    Build a private complete sibling first, sync it, then create the final
    filename via a same-directory hard link. The final name is never visible
    with partly written content from *this writer*, even to concurrent readers.
    Existing identical content is accepted without rewriting the inode;
    conflicting, unreadable or dangling-symlink leaves fail closed.

    This does not pin parent-directory identity or provide a durable directory
    fsync across crashes. An interrupted process may leave a private sibling.
    """
    if target.exists():
        _require_identical(target, content, conflict_message)
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(
        prefix=".fmp-audit-", suffix=".tmp", dir=target.parent
    )
    staged = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        try:
            # Link creation has no overwrite mode and is atomic at the leaf.
            os.link(staged, target)
        except FileExistsError:
            _require_identical(target, content, conflict_message)
    finally:
        staged.unlink(missing_ok=True)
