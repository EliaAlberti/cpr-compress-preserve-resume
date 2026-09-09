#!/usr/bin/env python3
"""PreCompact hook: save the raw transcript before any compaction.

Claude Code runs this before both manual /compact and automatic compaction,
passing a JSON object on stdin with session_id, transcript_path, cwd and
trigger. The script writes (or refreshes) one autosave log per session in
the project's CC-Session-Logs folder. Nothing is lost even when the user
forgets to run /cpr:compress. Exit code is always 0 so it never blocks.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpr_common import (  # noqa: E402
    AUTOSAVE_TAG,
    display_stamp,
    extract_turns,
    find_transcript,
    mirror_file,
    read_hook_input,
    render_raw_section,
    resolve_paths,
    timestamp_slug,
)


def build_header(stamp: str, trigger: str, session_id: str, turns: int) -> str:
    return (
        f"# Session Log: {stamp} - autosave before {trigger} compaction\n\n"
        "## Quick Reference (for AI scanning)\n"
        f"**Confidence keywords:** {AUTOSAVE_TAG}, {trigger}-compact\n"
        f"**Session:** {session_id or 'unknown'}\n"
        f"**Outcome:** Raw transcript saved automatically before {trigger} compaction "
        f"({turns} turns). No curated summary was written.\n\n"
        "---\n\n"
        "## Quick Resume Context\n"
        "This log was written by the CPR PreCompact hook, not by /cpr:compress. It holds the full "
        "conversation for search but no decisions or learnings. Run /cpr:compress in the session "
        "to add a curated summary, or search this file by topic with /cpr:resume <topic>.\n"
    )


def main() -> int:
    data = read_hook_input()
    cwd = data.get("cwd") or None
    session_id = str(data.get("session_id") or "")
    trigger = str(data.get("trigger") or "unknown")
    transcript_path = data.get("transcript_path")

    try:
        paths = resolve_paths(cwd)
        transcript = Path(transcript_path).expanduser() if transcript_path else None
        if transcript is None or not transcript.is_file():
            transcript = find_transcript(session_id or None, paths["cwd"], paths["project_root"])
        if transcript is None:
            print("cpr: no transcript found, nothing saved", file=sys.stderr)
            return 0

        turns = list(extract_turns(transcript))
        if not turns:
            return 0

        logs_dir = paths["logs_dir"]
        logs_dir.mkdir(parents=True, exist_ok=True)
        short = (session_id or transcript.stem)[:8]
        existing = sorted(logs_dir.glob(f"*-{AUTOSAVE_TAG}-*-{short}.md"))
        if existing:
            target = existing[-1]
            stamp = f"{target.name[0:10]} {target.name[11:13]}:{target.name[14:16]}"
        else:
            target = logs_dir / f"{timestamp_slug()}-{AUTOSAVE_TAG}-{trigger}-compact-{short}.md"
            stamp = display_stamp()

        content = build_header(stamp, trigger, session_id, len(turns)) + render_raw_section(turns)
        target.write_text(content, encoding="utf-8")
        mirror_file(target, paths["mirrors"])
        print(f"cpr: saved {len(turns)} turns to {target}")
    except Exception as exc:  # never block compaction
        print(f"cpr: autosave failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
