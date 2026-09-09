#!/usr/bin/env python3
"""Print the session summaries the resume skill needs, in one shot.

Usage:
    python3 resume_context.py [N] [topic words...]

Prints the summary section (everything above "## Raw Session Log") of the
last N logs, newest first, then any other logs whose summary or raw log
mentions the topic. The model renders the report from this output and
never has to open a file itself.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpr_common import is_autosave, list_logs, read_summary, resolve_paths  # noqa: E402

DEFAULT_N = 3
MAX_N = 50
MAX_MATCHES = 10


def parse_args(argv: list[str]) -> tuple[int, str]:
    n = DEFAULT_N
    words = []
    for arg in argv:
        if arg.isdigit() and n == DEFAULT_N and not words:
            n = max(1, min(MAX_N, int(arg)))
        else:
            words.append(arg)
    return n, " ".join(words).strip()


def snippet(text: str, needle: re.Pattern, width: int = 140) -> str:
    m = needle.search(text)
    if not m:
        return ""
    start = max(0, m.start() - width // 2)
    end = min(len(text), m.end() + width // 2)
    piece = text[start:end].replace("\n", " ")
    return re.sub(r"\s+", " ", piece).strip()


def main(argv: list[str]) -> int:
    n, topic = parse_args(argv)
    paths = resolve_paths()
    logs = list_logs(paths["logs_dir"])
    autosaves = [row for row in logs if is_autosave(row[0].name)]
    curated = [row for row in logs if not is_autosave(row[0].name)]

    print("=== CPR RESUME DATA ===")
    print(f"project_root: {paths['project_root']}")
    print(f"logs_dir: {paths['logs_dir']}")
    print(f"logs: {len(logs)} total, {len(curated)} curated, {len(autosaves)} autosaved")
    if not logs:
        print("No session logs yet. Run /cpr:compress at the end of a session to start building history.")
        print("=== END ===")
        return 0

    recent = curated[:n] if curated else logs[:n]
    shown = set()
    print(f"requested: last {n}" + (f", topic \"{topic}\"" if topic else ""))
    for idx, (path, when, topic_name) in enumerate(recent, 1):
        shown.add(path)
        print(f"\n--- LOG {idx} of {len(recent)}: {path.name} ({when:%Y-%m-%d %H:%M}, topic: {topic_name.replace('-', ' ')}) ---")
        print(read_summary(path) or "(empty summary)")

    newer_autosaves = [row for row in autosaves if recent and row[1] > recent[0][1]]
    if newer_autosaves:
        print(f"\n--- AUTOSAVES newer than the last curated log: {len(newer_autosaves)} ---")
        for path, when, _ in newer_autosaves[:5]:
            print(f"- {path.name} ({when:%Y-%m-%d %H:%M}), raw transcript only, no curated summary")

    if topic:
        needle = re.compile(re.escape(topic), re.I)
        matches = []
        for path, when, topic_name in logs:
            if path in shown:
                continue
            summary = read_summary(path)
            where = None
            hit_text = ""
            if needle.search(path.name) or needle.search(summary):
                where = "summary"
                hit_text = snippet(summary, needle) or f"filename matched: {path.name}"
            else:
                try:
                    full = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    full = ""
                if needle.search(full):
                    where = "raw log"
                    hit_text = snippet(full, needle)
            if where:
                matches.append((path, when, topic_name, where, hit_text))
            if len(matches) >= MAX_MATCHES:
                break
        print(f"\n=== TOPIC MATCHES for \"{topic}\" ({len(matches)} shown, newest first) ===")
        if not matches:
            print("(none)")
        for path, when, topic_name, where, hit_text in matches:
            print(f"- {when:%Y-%m-%d} {topic_name.replace('-', ' ')} [{where}] {hit_text}")
            if where == "summary":
                outcome = re.search(r"\*\*Outcome:\*\*\s*(.+)", read_summary(path))
                if outcome:
                    print(f"  outcome: {outcome.group(1).strip()}")

    print("\n=== END ===")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
