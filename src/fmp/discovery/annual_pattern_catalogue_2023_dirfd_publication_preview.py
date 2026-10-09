from __future__ import annotations

"""DEC-642: inert directory-descriptor publication research, not live CLI code.

This deliberately is not imported by the 23 production audit wrappers. It
explores a no-symlink-parents, no-replace publication contract on POSIX.
"""

import os
from pathlib import Path
import secrets
import stat


def _safe_flags() -> tuple[int, int, int]:
    required = ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")
    if any(not isinstance(getattr(os, name, None), int) for name in required):
        raise RuntimeError("platform cannot enforce no-symlink nonblocking audit output")
    if any(fn not in os.supports_dir_fd for fn in (
        os.open, os.mkdir, os.stat, os.link, os.unlink,
    )):
        raise RuntimeError("platform lacks dir_fd audit report support")
    cloexec = getattr(os, "O_CLOEXEC", 0)
    return (
        os.O_DIRECTORY | os.O_NOFOLLOW | os.O_RDONLY | cloexec,
        os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | cloexec,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | cloexec,
    )


def _open_parent(parent: Path, directory_flags: int) -> int:
    if not parent.is_absolute() or ".." in parent.parts:
        raise ValueError("audit output must have an absolute normalized parent")
    fd = os.open(parent.anchor, directory_flags)
    try:
        for part in parent.parts[1:]:
            try:
                next_fd = os.open(part, directory_flags, dir_fd=fd)
            except FileNotFoundError:
                try:
                    os.mkdir(part, dir_fd=fd)
                except FileExistsError:
                    pass
                next_fd = os.open(part, directory_flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def _assert_identical(
    fd: int, leaf: str, expected: bytes, conflict_message: str, flags: int,
) -> None:
    try:
        opened = os.open(leaf, flags, dir_fd=fd)
        try:
            info = os.fstat(opened)
            identical = (
                stat.S_ISREG(info.st_mode)
                and info.st_size == len(expected)
                and os.read(opened, len(expected) + 1) == expected
            )
        finally:
            os.close(opened)
    except (OSError, UnicodeError):
        raise ValueError(conflict_message) from None
    if not identical:
        raise ValueError(conflict_message)


def preview_write_once_external_report(
    target: Path, content: str, conflict_message: str,
) -> None:
    """Experiment only: never wire into run385, dispatch, or audit CLIs."""
    directory_flags, reader_flags, stage_flags = _safe_flags()
    if not target.is_absolute() or not target.name or ".." in target.parts:
        raise ValueError("audit output must be an absolute normalized file path")
    expected = content.encode("utf-8")
    fd = _open_parent(target.parent, directory_flags)
    try:
        try:
            os.stat(target.name, dir_fd=fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            _assert_identical(fd, target.name, expected, conflict_message, reader_flags)
            return
        staged = ".fmp-audit-" + secrets.token_hex(16) + ".tmp"
        tempfd = os.open(staged, stage_flags, 0o600, dir_fd=fd)
        try:
            with os.fdopen(tempfd, "wb") as output:
                output.write(expected)
                output.flush()
                os.fsync(output.fileno())
            try:
                os.link(
                    staged, target.name, src_dir_fd=fd, dst_dir_fd=fd,
                    follow_symlinks=False,
                )
            except FileExistsError:
                _assert_identical(fd, target.name, expected, conflict_message, reader_flags)
        finally:
            os.unlink(staged, dir_fd=fd)
    finally:
        os.close(fd)
