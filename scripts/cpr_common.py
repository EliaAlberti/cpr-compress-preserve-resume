"""Shared helpers for the CPR scripts.

Everything here is standard library only. Python 3.10 or newer.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

LOG_DIR_NAME = "CC-Session-Logs"
RAW_MARKER = "## Raw Session Log"
AUTOSAVE_TAG = "autosave"

# Optional routing config. Lets a path prefix send logs somewhere other than
# {project_root}/CC-Session-Logs and mirror them to extra folders.
CONFIG_PATH = Path(os.environ.get("CPR_CONFIG", str(Path.home() / ".claude" / "cpr.json")))

ISO_NAME = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(\d{2})_(\d{2})-(.+)\.md$")
LEGACY_NAME = re.compile(r"^(\d{2})-(\d{2})-(\d{4})-(\d{2})_(\d{2})-(.+)\.md$")

SKIP_USER_PREFIXES = (
    "<local-command",
    "<system-reminder",
    "<command-name",
    "<command-message",
    "<task-notification",
)
SYSTEM_REMINDER_BLOCK = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)


# --------------------------------------------------------------------------
# Config and paths
# --------------------------------------------------------------------------

def load_config() -> dict:
    try:
        with CONFIG_PATH.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def find_project_root(start: Path) -> Path:
    """Walk up from start looking for CLAUDE.md or .git. Fall back to start."""
    start = start.resolve()
    for candidate in (start, *start.parents):
        if (candidate / "CLAUDE.md").is_file() or (candidate / ".git").exists():
            return candidate
    return start


def resolve_paths(cwd: str | os.PathLike | None = None) -> dict:
    """Return project_root, logs_dir and mirrors for the given working directory.

    Routing rules come from ~/.claude/cpr.json:

        {
          "routes": [
            {
              "when_cwd_startswith": "/Users/me/vault",
              "logs_dir": "/Users/me/Desktop/Session Logs",
              "mirror_to": ["/Users/me/vault/Areas/CC-Session-Logs"]
            }
          ]
        }

    The longest matching prefix wins. Without a match, logs go to
    {project_root}/CC-Session-Logs and nothing is mirrored.
    """
    cwd_path = Path(cwd or os.getcwd()).expanduser().resolve()
    project_root = find_project_root(cwd_path)
    logs_dir = project_root / LOG_DIR_NAME
    mirrors: list[Path] = []

    best = None
    for route in load_config().get("routes", []) or []:
        prefix = str(route.get("when_cwd_startswith", "")).strip()
        if not prefix:
            continue
        prefix_path = Path(prefix).expanduser()
        if str(cwd_path).startswith(str(prefix_path)):
            if best is None or len(str(prefix_path)) > len(str(best[0])):
                best = (prefix_path, route)

    if best is not None:
        route = best[1]
        if route.get("logs_dir"):
            logs_dir = Path(str(route["logs_dir"])).expanduser()
        raw_mirrors = route.get("mirror_to") or []
        if isinstance(raw_mirrors, str):
            raw_mirrors = [raw_mirrors]
        mirrors = [Path(str(m)).expanduser() for m in raw_mirrors if str(m).strip()]

    return {"project_root": project_root, "logs_dir": logs_dir, "mirrors": mirrors, "cwd": cwd_path}


def mirror_file(path: Path, mirrors: list[Path]) -> list[Path]:
    written = []
    for folder in mirrors:
        try:
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / path.name
            shutil.copyfile(path, target)
            written.append(target)
        except OSError as exc:
            print(f"cpr: could not mirror to {folder}: {exc}", file=sys.stderr)
    return written


# --------------------------------------------------------------------------
# Log file names
# --------------------------------------------------------------------------

def timestamp_slug(when: dt.datetime | None = None) -> str:
    when = when or dt.datetime.now()
    return when.strftime("%Y-%m-%d-%H_%M")


def display_stamp(when: dt.datetime | None = None) -> str:
    when = when or dt.datetime.now()
    return when.strftime("%Y-%m-%d %H:%M")


def parse_log_name(name: str) -> tuple[dt.datetime, str] | None:
    """Parse both the v2 ISO name and the v1 day-first name."""
    m = ISO_NAME.match(name)
    if m:
        y, mo, d, h, mi, topic = m.groups()
    else:
        m = LEGACY_NAME.match(name)
        if not m:
            return None
        d, mo, y, h, mi, topic = m.groups()
    try:
        when = dt.datetime(int(y), int(mo), int(d), int(h), int(mi))
    except ValueError:
        return None
    return when, topic


def is_autosave(name: str) -> bool:
    parsed = parse_log_name(name)
    return bool(parsed and parsed[1].startswith(AUTOSAVE_TAG))


def list_logs(logs_dir: Path) -> list[tuple[Path, dt.datetime, str]]:
    """All logs in logs_dir, newest first. Unparseable names sort by mtime."""
    if not logs_dir.is_dir():
        return []
    rows = []
    for path in logs_dir.glob("*.md"):
        parsed = parse_log_name(path.name)
        if parsed:
            when, topic = parsed
        else:
            when = dt.datetime.fromtimestamp(path.stat().st_mtime)
            topic = path.stem
        rows.append((path, when, topic))
    rows.sort(key=lambda r: r[1], reverse=True)
    return rows


def read_summary(path: Path) -> str:
    """Everything above the Raw Session Log marker."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    cut = text.find(RAW_MARKER)
    return text[:cut].rstrip() if cut > 0 else text.rstrip()


def read_section(summary: str, heading: str) -> str:
    """Return the body of a '## heading' section from a summary, or ''."""
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |^---\s*$|\Z)", re.S | re.M)
    m = pattern.search(summary)
    return m.group(1).strip() if m else ""


# --------------------------------------------------------------------------
# Transcripts
# --------------------------------------------------------------------------

def project_slug(path: Path) -> str:
    """Claude Code's transcript folder name for a working directory."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def transcript_dir_candidates(cwd: Path, project_root: Path) -> list[Path]:
    base = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))) / "projects"
    seen = []
    for folder in (cwd, project_root):
        candidate = base / project_slug(folder.resolve())
        if candidate not in seen:
            seen.append(candidate)
    return seen


def find_transcript(session_id: str | None, cwd: Path, project_root: Path) -> Path | None:
    for folder in transcript_dir_candidates(cwd, project_root):
        if not folder.is_dir():
            continue
        if session_id:
            candidate = folder / f"{session_id}.jsonl"
            if candidate.is_file():
                return candidate
            continue
        files = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            return files[0]
    return None


def _clean_user_text(text: str) -> str:
    text = SYSTEM_REMINDER_BLOCK.sub("", text).strip()
    return text


def extract_turns(transcript: Path):
    """Yield (role, text) for the main-thread user and assistant messages.

    Thinking, tool calls, tool results, subagent side chains and Claude Code's
    own injected messages are skipped. The JSONL layout is internal to Claude
    Code, so every access is defensive.
    """
    with transcript.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            kind = obj.get("type")
            if kind not in ("user", "assistant"):
                continue
            if obj.get("isSidechain") or obj.get("isMeta"):
                continue
            message = obj.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content")

            if kind == "user":
                if isinstance(content, str):
                    parts = [content]
                elif isinstance(content, list):
                    parts = [
                        b.get("text", "")
                        for b in content
                        if isinstance(b, dict) and b.get("type") == "text"
                    ]
                else:
                    continue
                text = _clean_user_text("\n\n".join(p for p in parts if p))
                if not text or text.startswith(SKIP_USER_PREFIXES):
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


def render_raw_section(turns) -> str:
    out = [f"\n---\n\n{RAW_MARKER}\n\n"]
    for role, text in turns:
        out.append(f"**{role}:**\n{text}\n\n")
    return "".join(out)


def append_raw_log(log_path: Path, turns) -> int:
    turns = list(turns)
    existing = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    with log_path.open("a", encoding="utf-8") as out:
        if existing and not existing.endswith("\n"):
            out.write("\n")
        out.write(render_raw_section(turns))
    return len(turns)


def read_hook_input() -> dict:
    """Hook scripts receive one JSON object on stdin."""
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}
