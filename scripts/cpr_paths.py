#!/usr/bin/env python3
"""Print where the current session's log should go.

Used by the compress and preserve skills through shell injection, so the
model never has to re-derive the project root or the timestamp.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpr_common import display_stamp, list_logs, resolve_paths, timestamp_slug  # noqa: E402


def main() -> int:
    paths = resolve_paths()
    logs = list_logs(paths["logs_dir"])
    print(f"project_root: {paths['project_root']}")
    print(f"project_name: {paths['project_root'].name}")
    print(f"logs_dir: {paths['logs_dir']}")
    print(f"mirrors: {', '.join(str(m) for m in paths['mirrors']) or 'none'}")
    print(f"existing_logs: {len(logs)}")
    print(f"timestamp_slug: {timestamp_slug()}")
    print(f"timestamp_display: {display_stamp()}")
    print(f"claude_md: {'present' if (paths['project_root'] / 'CLAUDE.md').is_file() else 'absent'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
