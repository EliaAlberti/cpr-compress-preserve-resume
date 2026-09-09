#!/usr/bin/env python3
"""Append the raw conversation transcript to a CPR session log.

Usage:
    python3 dump_transcript.py "<session-log-path>" [session-id]
    python3 dump_transcript.py "<session-log-path>" --transcript "<path.jsonl>"

Finds the Claude Code transcript for the current project under
~/.claude/projects/<slug>/ (the given session id, or else the most recently
modified one), and appends a "## Raw Session Log" section to the log file.
Only user and assistant text is kept; thinking, tool calls, tool results and
subagent side chains are skipped. Prints the number of turns written.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpr_common import append_raw_log, extract_turns, find_transcript, mirror_file, resolve_paths  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    log_path = Path(argv[0]).expanduser()
    session_id = None
    transcript = None
    rest = argv[1:]
    while rest:
        arg = rest.pop(0)
        if arg == "--transcript" and rest:
            transcript = Path(rest.pop(0)).expanduser()
        elif not arg.startswith("-"):
            session_id = arg

    if not log_path.is_file():
        print(f"Session log not found: {log_path}", file=sys.stderr)
        return 1

    paths = resolve_paths()
    if transcript is None:
        transcript = find_transcript(session_id, paths["cwd"], paths["project_root"])
    if transcript is None or not transcript.is_file():
        where = " or ".join(str(p) for p in (paths["cwd"], paths["project_root"]))
        print(f"No transcript found for session {session_id or '(latest)'} under {where}", file=sys.stderr)
        return 1

    count = append_raw_log(log_path, extract_turns(transcript))
    mirrored = mirror_file(log_path, paths["mirrors"])
    print(f"Appended {count} turns from {transcript.name} to {log_path}")
    for target in mirrored:
        print(f"Mirrored to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
