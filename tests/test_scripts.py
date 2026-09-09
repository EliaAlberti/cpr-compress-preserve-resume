"""Smoke tests for the CPR scripts. Run with: python3 -m unittest discover tests"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import cpr_common as cc  # noqa: E402


def write_transcript(path: Path) -> None:
    rows = [
        {"type": "user", "message": {"content": "<local-command-stdout>ignored</local-command-stdout>"}},
        {"type": "user", "message": {"content": "Hello there<system-reminder>hidden</system-reminder>"}},
        {"type": "assistant", "message": {"content": [
            {"type": "thinking", "thinking": "secret"},
            {"type": "text", "text": "Hi! Let me look."},
            {"type": "tool_use", "name": "Read", "input": {}},
        ]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "content": "file body"}]}},
        {"type": "user", "isSidechain": True, "message": {"content": "subagent prompt"}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "Done."}]}},
        {"type": "attachment", "message": {"content": "meta"}},
    ]
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


class TranscriptTests(unittest.TestCase):
    def test_extract_turns_keeps_only_main_thread_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp) / "s.jsonl"
            write_transcript(t)
            turns = list(cc.extract_turns(t))
        self.assertEqual(turns, [("User", "Hello there"), ("Assistant", "Hi! Let me look."), ("Assistant", "Done.")])

    def test_dump_transcript_appends_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp) / "s.jsonl"
            write_transcript(t)
            log = Path(tmp) / "2026-09-09-10_00-topic.md"
            log.write_text("# Session Log\n\n## Quick Resume Context\nx\n", encoding="utf-8")
            out = subprocess.run(
                [sys.executable, str(SCRIPTS / "dump_transcript.py"), str(log), "--transcript", str(t)],
                capture_output=True, text=True, cwd=tmp, env={**os.environ, "CPR_CONFIG": "/nonexistent"},
            )
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertIn("Appended 3 turns", out.stdout)
            text = log.read_text(encoding="utf-8")
        self.assertIn(cc.RAW_MARKER, text)
        self.assertIn("**User:**\nHello there", text)
        self.assertNotIn("secret", text)


class NamingTests(unittest.TestCase):
    def test_parses_iso_and_legacy_names_and_sorts_by_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for name in ("02-01-2026-09_00-old-year.md", "2026-09-09-10_00-new.md", "31-12-2025-23_59-older.md"):
                (d / name).write_text("# x\n", encoding="utf-8")
            rows = cc.list_logs(d)
        self.assertEqual([r[0].name for r in rows], ["2026-09-09-10_00-new.md", "02-01-2026-09_00-old-year.md", "31-12-2025-23_59-older.md"])

    def test_autosave_detection(self):
        self.assertTrue(cc.is_autosave("2026-09-09-10_00-autosave-auto-compact-abcd1234.md"))
        self.assertFalse(cc.is_autosave("2026-09-09-10_00-api-auth.md"))


class RoutingTests(unittest.TestCase):
    def test_default_paths_use_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "CLAUDE.md").write_text("# p\n", encoding="utf-8")
            sub = root / "a" / "b"
            sub.mkdir(parents=True)
            old = cc.CONFIG_PATH
            cc.CONFIG_PATH = Path("/nonexistent")
            try:
                paths = cc.resolve_paths(sub)
            finally:
                cc.CONFIG_PATH = old
        self.assertEqual(paths["project_root"], root)
        self.assertEqual(paths["logs_dir"], root / cc.LOG_DIR_NAME)
        self.assertEqual(paths["mirrors"], [])

    def test_route_overrides_logs_dir_and_mirrors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            cfg = root / "cpr.json"
            cfg.write_text(json.dumps({"routes": [{
                "when_cwd_startswith": str(root / "vault"),
                "logs_dir": str(root / "desk"),
                "mirror_to": [str(root / "mirror")],
            }]}), encoding="utf-8")
            (root / "vault" / "x").mkdir(parents=True)
            old = cc.CONFIG_PATH
            cc.CONFIG_PATH = cfg
            try:
                paths = cc.resolve_paths(root / "vault" / "x")
            finally:
                cc.CONFIG_PATH = old
        self.assertEqual(paths["logs_dir"], root / "desk")
        self.assertEqual(paths["mirrors"], [root / "mirror"])


class HookTests(unittest.TestCase):
    def run_hook(self, script: str, payload: dict, cwd: str):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script)], input=json.dumps(payload), capture_output=True,
            text=True, cwd=cwd, env={**os.environ, "CPR_CONFIG": "/nonexistent"},
        )

    def test_precompact_writes_one_autosave_per_session_and_session_start_reads_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / ".git").mkdir()
            t = root / "s.jsonl"
            write_transcript(t)
            payload = {"session_id": "abcd1234-ffff", "transcript_path": str(t), "cwd": str(root), "trigger": "auto"}
            first = self.run_hook("precompact_save.py", payload, str(root))
            second = self.run_hook("precompact_save.py", payload, str(root))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            files = list((root / cc.LOG_DIR_NAME).glob("*.md"))
            self.assertEqual(len(files), 1)
            self.assertIn("autosave-auto-compact-abcd1234", files[0].name)

            curated = root / cc.LOG_DIR_NAME / "2026-09-09-09_00-curated-topic.md"
            curated.write_text(
                "# Session Log: 2026-09-09 09:00 - curated-topic\n\n## Quick Reference (for AI scanning)\n"
                "**Confidence keywords:** a, b\n**Outcome:** Shipped the thing\n\n## Pending Tasks\n- [ ] Next step one\n\n---\n\n"
                "## Quick Resume Context\nWe shipped the thing. Next is step one.\n\n---\n\n## Raw Session Log\n\nhidden\n",
                encoding="utf-8",
            )
            brief = self.run_hook("session_start.py", {"cwd": str(root)}, str(root))
            self.assertEqual(brief.returncode, 0, brief.stderr)
        self.assertIn("Outcome: Shipped the thing", brief.stdout)
        self.assertIn("Next step one", brief.stdout)
        self.assertIn("autosaved transcript", brief.stdout)
        self.assertNotIn("hidden", brief.stdout)

    def test_session_start_is_silent_without_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.run_hook("session_start.py", {"cwd": tmp}, tmp)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout, "")


class ResumeContextTests(unittest.TestCase):
    def test_topic_search_and_recent_summaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / ".git").mkdir()
            logs = root / cc.LOG_DIR_NAME
            logs.mkdir()
            (logs / "2026-09-01-10_00-alpha.md").write_text("# a\n**Outcome:** alpha done\n\n## Raw Session Log\n\nzebra secret\n", encoding="utf-8")
            (logs / "2026-09-02-10_00-beta.md").write_text("# b\n**Outcome:** beta done\n\n## Raw Session Log\n\nnothing\n", encoding="utf-8")
            out = subprocess.run(
                [sys.executable, str(SCRIPTS / "resume_context.py"), "1", "zebra"],
                capture_output=True, text=True, cwd=str(root), env={**os.environ, "CPR_CONFIG": "/nonexistent"},
            )
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("LOG 1 of 1: 2026-09-02-10_00-beta.md", out.stdout)
        self.assertIn("[raw log]", out.stdout)
        self.assertIn("alpha", out.stdout)


if __name__ == "__main__":
    unittest.main()
