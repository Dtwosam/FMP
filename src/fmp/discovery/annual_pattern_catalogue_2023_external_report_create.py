from __future__ import annotations

"""DEC-643 DRAFT: invoke inode-anchored external report publication.

The 23 audit CLI wrappers retain their explicit source-checkout path guards.
This is an unmerged integration rehearsal, never annual dispatch authority.
"""

import os  # Retain patchable primitive for focused failure/race regressions.
from pathlib import Path

from fmp.discovery.annual_pattern_catalogue_2023_dirfd_publication_preview import (
    preview_write_once_external_report,
)


def write_once_external_report(target: Path, content: str, conflict_message: str) -> None:
    """Publish only through the nofollow directory-descriptor implementation."""
    preview_write_once_external_report(target, content, conflict_message)
