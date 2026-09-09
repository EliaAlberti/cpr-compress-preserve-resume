#!/usr/bin/env python3
"""SessionStart hook: hand the model a short memory brief.

Whatever this prints on stdout is added to the model's context when a
session starts, after /clear, and after compaction. It stays small on
purpose: the Quick Resume Context and pending tasks of the latest curated
log, plus a pointer to /cpr:resume for the full picture. Prints nothing
when the project has no session logs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpr_common import is_autosave, list_logs, read_hook_input, read_section, read_summary, resolve_paths  # noqa: E402

MAX_PENDING = 5


def main() -> int:
    data = read_hook_input()
    try:
        paths = resolve_paths(data.get("cwd") or None)
        logs = list_logs(paths["logs_dir"])
        if not logs:
            return 0
        curated = [row for row in logs if not is_autosave(row[0].name)]
        autosaves = [row for row in logs if is_autosave(row[0].name)]

        lines = [f"CPR session memory: {len(logs)} logs in {paths['logs_dir']}."]
        if curated:
            path, when, topic = curated[0]
            summary = read_summary(path)
            lines.append(f"Latest curated session: {when:%Y-%m-%d %H:%M}, topic \"{topic.replace('-', ' ')}\".")
            outcome = re.search(r"\*\*Outcome:\*\*\s*(.+)", summary)
            if outcome:
                lines.append(f"Outcome: {outcome.group(1).strip()}")
            context = read_section(summary, "Quick Resume Context")
            if context:
                lines.append("Quick Resume Context: " + re.sub(r"\s+", " ", context))
            pending = read_section(summary, "Pending Tasks")
            if pending:
                items = [ln.strip() for ln in pending.splitlines() if ln.strip().startswith(("-", "*"))]
                if items:
                    lines.append("Pending tasks: " + " | ".join(i.lstrip("-* ").strip() for i in items[:MAX_PENDING]))
            newer = [row for row in autosaves if row[1] > when]
            if newer:
                lines.append(f"{len(newer)} autosaved transcript(s) are newer than that log and have no curated summary.")
        else:
            lines.append("Only autosaved transcripts exist so far; none has a curated summary.")
        lines.append("Run /cpr:resume for the last three session summaries, or /cpr:resume <topic> to search past sessions.")
        print("\n".join(lines))
    except Exception as exc:
        print(f"cpr: session brief failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
