#!/usr/bin/env python3
"""Append the raw conversation transcript to a CPR session log.

Usage:
    python3 scripts/dump_transcript.py "<session-log-path>" [session-id]

Reads the Claude Code transcript for the current project from
~/.claude/projects/<slug>/<session-id>.jsonl (or the most recently
modified .jsonl if no session id is given) and appends a
"## Raw Session Log" section to the given log file. Only user and
assistant text is kept; thinking, tool calls and tool results are skipped.
"""

import json
import os
import sys
from pathlib import Path

SKIP_PREFIXES = ("<local-command", "<system-reminder", "<command-name")


def project_dir() -> Path:
    slug = os.getcwd().replace("/", "-")
    return Path.home() / ".claude" / "projects" / slug


def pick_transcript(session_id: str | None) -> Path:
    folder = project_dir()
    if not folder.is_dir():
        sys.exit(f"No Claude Code project folder found at {folder}")
    if session_id:
        candidate = folder / f"{session_id}.jsonl"
        if not candidate.is_file():
            sys.exit(f"No transcript found for session id {session_id} in {folder}")
        return candidate
    files = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        sys.exit(f"No .jsonl transcripts found in {folder}")
    return files[0]


def extract_turns(transcript: Path):
    with transcript.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = obj.get("type")
            if kind not in ("user", "assistant"):
                continue
            content = (obj.get("message") or {}).get("content")
            if kind == "user":
                if not isinstance(content, str):
                    continue  # tool results, not a typed message
                text = content.strip()
                if not text or text.startswith(SKIP_PREFIXES):
                    continue
                yield "User", text
            else:
                if not isinstance(content, list):
                    continue
                parts = [
                    b.get("text", "").strip()
                    for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                ]
                text = "\n\n".join(p for p in parts if p)
                if text:
                    yield "Assistant", text


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    log_path = Path(sys.argv[1])
    session_id = sys.argv[2] if len(sys.argv) > 2 else None
    if not log_path.is_file():
        sys.exit(f"Session log not found: {log_path}")

    transcript = pick_transcript(session_id)
    turns = list(extract_turns(transcript))

    existing = log_path.read_text(encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as out:
        if not existing.endswith("\n"):
            out.write("\n")
        out.write("\n---\n\n## Raw Session Log\n\n")
        for role, text in turns:
            out.write(f"**{role}:**\n{text}\n\n")

    print(f"Appended {len(turns)} turns from {transcript.name} to {log_path}")


if __name__ == "__main__":
    main()
