<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-Plugin-5A67D8?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQxIDAtOC0zLjU5LTgtOHMzLjU5LTggOC04IDggMy41OSA4IDgtMy41OSA4LTggOHoiLz48L3N2Zz4=&logoColor=white" alt="Claude Code Plugin" />
  <img src="https://img.shields.io/badge/Version-2.0.0-E74C3C?style=for-the-badge" alt="Version 2.0.0" />
  <img src="https://img.shields.io/badge/Skills-3%20%2B%202%20hooks-blue?style=for-the-badge" alt="3 skills and 2 hooks" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License" />
  <img src="https://img.shields.io/badge/Token%20Savings-~66%25%20median-brightgreen?style=for-the-badge" alt="Token Savings ~66% median" />
</p>

<h1 align="center">🩺 CPR for Claude Code</h1>
<h3 align="center"><em>Compress, Preserve & Resume</em></h3>

<p align="center">
  <strong>Persistent memory across sessions. Never lose context again.</strong><br>
  <em>Estimated ~66% reduction in session-restart token cost (analytical model, range 51-74%).</em>
</p>

<table>
  <tr>
    <td align="center" width="33%">
      <strong>/cpr:preserve</strong><br>
      <sub>Save key learnings to CLAUDE.md</sub><br><br>
      <video src="https://github.com/user-attachments/assets/3c7e0f30-dea0-4c67-a990-021db84b6d81" width="100%" controls></video>
    </td>
    <td align="center" width="33%">
      <strong>/cpr:compress</strong><br>
      <sub>Capture the full session to a searchable log</sub><br><br>
      <video src="https://github.com/user-attachments/assets/a31fe4b7-483e-47c1-8d78-01850482244f" width="100%" controls></video>
    </td>
    <td align="center" width="33%">
      <strong>/cpr:resume</strong><br>
      <sub>Restore context from past sessions</sub><br><br>
      <video src="https://github.com/user-attachments/assets/1a3aff44-904d-463a-8f4e-6af6925e8a7a" width="100%" controls></video>
    </td>
  </tr>
</table>

<p align="center">
  Three skills and two hooks that save, search, and restore your conversation context, so you can pick up exactly where you left off.
</p>

<p align="center">
  <a href="#is-cpr-for-me">Is it for me?</a> &bull;
  <a href="#the-problem">Problem</a> &bull;
  <a href="#the-solution">Solution</a> &bull;
  <a href="#why-it-saves-tokens">Why It Saves Tokens</a> &bull;
  <a href="#installation">Installation</a> &bull;
  <a href="#usage">Usage</a> &bull;
  <a href="#recommended-workflow">Workflow</a> &bull;
  <a href="#upgrading-from-v1">Upgrading</a> &bull;
  <a href="#faq">FAQ</a>
</p>

---

## What Is CPR?

CPR is a **Claude Code plugin**. It adds three slash commands and two hooks:

| Piece | What it does |
|-------|--------------|
| `/cpr:compress` | Writes a structured, searchable session log. A script appends the raw transcript. |
| `/cpr:preserve` | Updates CLAUDE.md with the learnings every future session should start with. |
| `/cpr:resume` | Loads recent session summaries and searches past sessions by topic. |
| **PreCompact hook** | Saves the raw transcript before every compaction, manual or automatic. |
| **SessionStart hook** | Hands the model a short memory brief when a session starts or compacts. |

No build step, no dependencies beyond Python 3.10, and every file is plain markdown or a small script you can read.

---

## Is CPR For Me?

**Yes** if you work on the same project across several Claude Code sessions and find yourself re-explaining what happened last time, or if you want the full conversation kept on disk and searchable by topic rather than flattened into a compaction summary.

**No** if your sessions are one-off fixes or throwaway scripts. There is no next session to pay the save back.

CPR sits next to CLAUDE.md and Claude Code's auto memory rather than replacing them. CLAUDE.md holds instructions, auto memory holds preferences, CPR holds the state of the work. Install takes one line, and removing it is `/plugin uninstall cpr@cpr`.

---

## The Problem

Claude Code has **no memory of the work between sessions**. When you close a conversation, the decisions, the fixes, the paths and the reasons go with it.

It gets worse:

| Problem | Impact |
|---------|--------|
| **Compaction flattens details** | When the context window fills up, history is summarised and specific values, file paths and nuanced decisions get lost |
| **Long sessions lose early context** | That critical decision from the first 10 minutes? Gone by hour two |
| **New session = blank slate** | Re-explaining your project, re-discovering paths, re-making decisions every time |
| **Past work is unsearchable** | No way to look up what you discussed three sessions ago |
| **CLAUDE.md and auto memory aren't enough** | They hold instructions and preferences, not the state of the work, the errors, or the solutions |

---

## The Solution

```
During work  ──> PreCompact hook  ──> raw transcript autosaved before any compaction
End session  ──> /cpr:preserve    ──> CLAUDE.md updated (optional)
                 /cpr:compress    ──> curated session log saved
New session  ──> SessionStart hook──> latest Quick Resume Context injected automatically
                 /cpr:resume      ──> last N summaries + topic search ──> full context restored
```

The skills are where the curated summaries come from. The hooks are the safety net for the sessions you forget to save.

### CPR next to Claude Code's own memory

Claude Code now has auto memory and re-injects CLAUDE.md after compaction. CPR is built to sit next to both, not replace them:

| | CLAUDE.md | Auto memory | CPR session logs |
|---|---|---|---|
| Holds | Instructions and conventions | Preferences and corrections | Decisions, fixes, errors, pending work, the full transcript |
| Written by | You (and `/cpr:preserve`) | Claude Code | `/cpr:compress` and the hooks |
| Shared with the team | Yes, via git | No, machine-local | Yes, if you commit `CC-Session-Logs/` |
| Searchable by topic | No | No | Yes, `/cpr:resume <topic>` |

---

## Works With Auto-Compact

Earlier versions of CPR told you to disable auto-compact. You no longer need to. The PreCompact hook runs before both `/compact` and automatic compaction, receives the transcript path from Claude Code, and writes one autosave log per session into `CC-Session-Logs/`. After compaction, the SessionStart hook puts the latest Quick Resume Context back into context.

You still get the best results by running `/cpr:compress` before `/compact`, because that is where the curated summary comes from. The autosave only guarantees you never lose the raw conversation.

---

## Why It Saves Tokens

Re-establishing context at the start of every session is expensive. The user re-explains the project, Claude re-reads files, prior decisions get re-derived, and conversations rebuild from scratch. CPR replaces that with a compact log of what mattered.

Across the modelled range, **session-restart token cost drops by 51% in the low case, 66% in the median case, and 74% in the high case**. On a 10-session project that's roughly **~99,450 tokens saved at the median**. On a 20-session, high-context project it's **~579,500 tokens saved**.

| Case | Without CPR | With CPR | Savings | % saved |
|---|---|---|---|---|
| Low | 4,850 | 2,400 | 2,450 | **51%** |
| Median | 16,750 | 5,700 | 11,050 | **66%** |
| High | 41,200 | 10,700 | 30,500 | **74%** |

Two things make v2.0 cheaper than v1. The raw archive is appended by script, and the PreCompact hook does the same before any compaction, so none of it is model output. And `/cpr:resume` no longer opens files or re-reads CLAUDE.md, which Claude Code already loads: a script injects the summaries straight into the skill, and the session-start brief costs about 200 tokens.

These are analytical estimates, not telemetry. CPR is net positive for multi-session projects with cross-session context, and net negative for one-off bug fixes or single-session work. The breakeven is reached when the next session would otherwise repeat ~2,400 tokens of context-rebuild work, which most multi-session projects cross by session #2.

Full methodology, baseline scenarios, and per-component cost breakdown: [`docs/token-savings-analysis.md`](docs/token-savings-analysis.md).

---

## The Session Log System

Every `/cpr:compress` creates a structured markdown file in `CC-Session-Logs/` at your project root. The hooks add autosave files to the same folder.

**Filename format:** `YYYY-MM-DD-HH_MM-topic-name.md`, so files sort chronologically in any listing.

<details>
<summary><strong>Log structure (click to expand)</strong></summary>

```markdown
# Session Log: 2026-03-05 14:20 - api-auth-refactor

## Quick Reference (for AI scanning)
**Confidence keywords:** auth, JWT, refresh-tokens, middleware
**Projects:** my-saas-app
**Outcome:** Replaced cookie-based auth with JWT + refresh tokens

## Decisions Made
- JWT over session cookies, stateless scales better

## Key Learnings
- Redis EX flag is cleaner than separate EXPIRE calls

## Solutions & Fixes
- Login race condition fixed with SETNX

## Files Modified
- `src/middleware/auth.ts`: JWT verification

## Pending Tasks
- [ ] Add refresh token rotation

---
## Quick Resume Context
2-3 sentence summary. This is what the SessionStart hook shows next time.

---
## Raw Session Log
{Full conversation archive, appended by script, searchable but never loaded by /cpr:resume}
```

</details>

**The key insight:** `/cpr:resume` only reads the summary sections (everything above "Raw Session Log"). The raw conversation is there for searchability, but it never wastes tokens during context loading.

**And it's free to write, too.** The raw log is appended by `scripts/dump_transcript.py`, which reads the Claude Code transcript straight from `~/.claude/projects/`. Only the structured sections are model output.

See [`examples/session-log-example.md`](examples/session-log-example.md) for a complete example.

---

## Installation

### Prerequisites

- [Claude Code](https://code.claude.com/docs) with plugin support. Verified on v2.1.266.
- Python 3.10 or newer on your PATH as `python3`

### Option A: plugin marketplace (recommended)

Inside Claude Code:

```
/plugin marketplace add EliaAlberti/cpr-compress-preserve-resume
/plugin install cpr@cpr
```

Or from your shell:

```bash
claude plugin marketplace add EliaAlberti/cpr-compress-preserve-resume
claude plugin install cpr@cpr
```

The install wires the skills and both hooks. Run `/reload-plugins` or restart Claude Code if you installed from inside a session. Updates arrive when the plugin version is bumped; `/plugin` shows what is installed and lets you update or uninstall.

### Option B: skills directory

Clone the repo into your personal skills folder and Claude Code loads it as a plugin on the next start, hooks included:

```bash
git clone https://github.com/EliaAlberti/cpr-compress-preserve-resume.git ~/.claude/skills/cpr
```

`git pull` in that folder updates it. Edits to a `SKILL.md` apply immediately; changes to the hooks need `/reload-plugins` or a restart. If you prefer to keep a development clone elsewhere, a symlink at `~/.claude/skills/cpr` pointing at it works the same way.

### Option C: try it without installing

```bash
claude --plugin-dir /path/to/cpr-compress-preserve-resume
```

The skills and hooks are active for that session only. Pass the flag again next time.

### Check it works

```
You: /cpr:compress
```

If the "What to preserve" selector appears, it's working. The hooks are active whenever the plugin is enabled: the next time you start a session in a project that already has logs, the memory brief is there before your first message.

One detail: the skills are user-invoked only, so they don't appear when you ask the model to list its skills. Type them.

### Model

The skills run on whatever model your session uses. CPR is written for the current Claude 5 family and does not pin a model.

---

## Usage

### End of session: save your work

```
You: /cpr:compress
Claude: What would you like to preserve? [multi-select]
You: Key Learnings, Solutions & Fixes, Decisions Made, Files Modified
Claude: Anything specific to highlight? [Skip / Add a custom note]
You: Skip
Claude: Topic name: "api-auth-refactor" [Accept / Provide a different name]
You: Accept
Claude: Session Saved
        CC-Session-Logs/2026-03-05-17_30-api-auth-refactor.md
        Raw log: 84 turns appended
```

In a hurry? `/cpr:compress quick` skips the questions and saves every section that has content.

### Update CLAUDE.md: preserve key learnings

```
You: /cpr:preserve
Claude: What should be preserved? [multi-select]
You: Key Decisions, Next Steps
Claude: CLAUDE.md updated
        - Added JWT auth decision rationale
        - Updated next steps with token rotation
        CLAUDE.md is now 185 lines (target: under 200)
```

### Starting a new session: restore context

The moment a session starts, the SessionStart hook has already added the latest log's Quick Resume Context and pending tasks. For the full picture:

```
You: /cpr:resume
Claude:
══════════════════════════════════════════════
 RESUMING: my-saas-app
══════════════════════════════════════════════

CONTEXT:
- JWT auth flow implemented, tests passing
- Redis used for refresh token storage

MOST RECENT SESSION: 2026-03-05 17:30
Topic: api-auth-refactor
...

READY TO:
- Add refresh token rotation
- Set up token blacklist for logout
══════════════════════════════════════════════
```

### Search past sessions by topic

```
You: /cpr:resume auth
Claude: [Shows recent sessions + RELATED SESSIONS matching "auth"]

══════════════════════════════════════════════
 RELATED SESSIONS (topic: "auth")
══════════════════════════════════════════════

- 2026-03-05: api-auth-refactor, JWT + refresh tokens
- 2026-02-28: oauth-google-setup, Google OAuth integration
══════════════════════════════════════════════
```

`/cpr:resume 10 migration` reads the last 10 sessions and searches for "migration". Topic search covers the raw logs too, so a detail you only mentioned in passing is still findable.

---

## Recommended Workflow

```
┌──────────────────────────────────────────────────────────┐
│  1. Start session                                        │
│     └── (brief injected)  then /cpr:resume if you need   │
│                           the last few sessions in full  │
│                                                          │
│  2. Do work...                                           │
│     └── compaction happens? the PreCompact hook has      │
│         already saved the raw transcript                 │
│                                                          │
│  3. Before ending or before /compact                     │
│     ├── /cpr:preserve     Update CLAUDE.md (optional)    │
│     └── /cpr:compress     Save the curated session log   │
└──────────────────────────────────────────────────────────┘
```

**When to `/cpr:preserve`:**
- After making important architectural decisions
- When you discover patterns you'll need in future sessions
- When project phase or status changes

**When to `/cpr:compress`:**
- Before ending a session
- Before `/compact`, so the summary is written from the full conversation
- After completing a significant chunk of work

---

## Customisation

<details>
<summary><strong>Session log storage path and mirroring</strong></summary>

By default, logs go to `{project_root}/CC-Session-Logs/`. The project root is the nearest parent directory containing `CLAUDE.md` or `.git`, falling back to the current directory.

To route logs elsewhere for some projects, or mirror them to a second folder, create `~/.claude/cpr.json`:

```json
{
  "routes": [
    {
      "when_cwd_startswith": "/Users/me/vault",
      "logs_dir": "/Users/me/Desktop/Session Logs",
      "mirror_to": ["/Users/me/vault/Areas/CC-Session-Logs"]
    }
  ]
}
```

The longest matching prefix wins. Every skill and hook honours it. Set `CPR_CONFIG` to use a different config file.

</details>

<details>
<summary><strong>CLAUDE.md line target</strong></summary>

`/cpr:preserve` aims to keep CLAUDE.md under 200 lines, which is what Claude Code recommends for adherence. Change the number in `skills/preserve/SKILL.md`.

</details>

<details>
<summary><strong>Protected and archivable sections</strong></summary>

Mark any section in your CLAUDE.md as immune to archiving:

```markdown
## My Important Section (PROTECTED)
```

Or mark sections as safe to archive:

```markdown
## Old Notes (ARCHIVABLE)
```

Archived content goes to `CLAUDE-Archive.md` next to your CLAUDE.md.

</details>

<details>
<summary><strong>Turning the hooks off</strong></summary>

Delete the entry you don't want from `hooks/hooks.json` in your installed copy, or disable the plugin with `/plugin`. The skills work without the hooks.

</details>

---

## Upgrading From v1

- **Your logs keep working.** `/cpr:resume` reads the old `DD-MM-YYYY` filenames and the new ISO ones, and sorts them by real date.
- **Remove the old command files.** Delete `compress.md`, `preserve.md` and `resume.md` from `~/.claude/commands/` (or `.claude/commands/`) and the `~/.claude/scripts/dump_transcript.py` copy. Otherwise you have two of each.
- **The commands are namespaced now.** `/cpr:compress`, `/cpr:preserve`, `/cpr:resume`. Claude Code ships its own `/resume` session picker, which is why CPR's version moved.
- **You can turn auto-compact back on.** See [Works With Auto-Compact](#works-with-auto-compact).

---

## How It Scales

| Session logs | Behaviour |
|-------------|-----------|
| Any count | `/cpr:resume` reads summaries only, never raw logs, so it stays cheap at any scale |
| Any count | Topic search is done by a script, across summaries first and raw logs second, capped at 10 matches |
| Autosaves | One file per session, refreshed on each compaction, so they never pile up |

---

## FAQ

<details>
<summary><strong>Do I need all three skills?</strong></summary>

`/cpr:compress` + `/cpr:resume` is the minimum viable setup. `/cpr:preserve` is optional but recommended. It keeps your CLAUDE.md up to date without manual editing. The hooks come with the plugin and need no setup.

</details>

<details>
<summary><strong>Where are logs stored?</strong></summary>

`{project_root}/CC-Session-Logs/`. Project root is the nearest parent directory containing `CLAUDE.md` or `.git`. If neither is found, it falls back to the current working directory. See Customisation for routing.

</details>

<details>
<summary><strong>Will this work with any project?</strong></summary>

Yes. The skills auto-detect your project root and create the `CC-Session-Logs/` folder on first use. No configuration needed.

</details>

<details>
<summary><strong>How big do logs get?</strong></summary>

A full session log with the raw conversation can be several hundred KB. But the raw part is appended by script, not generated as model output, and `/cpr:resume` only reads the summary header (typically 30-80 lines), so token usage stays low regardless of log size.

</details>

<details>
<summary><strong>Should I commit session logs to git?</strong></summary>

Up to you. They're useful for team knowledge sharing but can be large. Consider adding `CC-Session-Logs/` to `.gitignore` if you prefer to keep them local.

</details>

<details>
<summary><strong>What if I forget to /cpr:compress before /compact?</strong></summary>

The PreCompact hook saved the raw transcript for you. You lose the curated summary for that stretch, but the conversation is on disk and `/cpr:resume <topic>` can search it. Run `/cpr:compress` after compaction to write a summary from what remains in context.

</details>

<details>
<summary><strong>Does the transcript parsing break when Claude Code changes?</strong></summary>

It can. Claude Code documents the transcript format as internal. CPR reads it defensively, takes the path from the hook input rather than guessing, and skips anything it doesn't recognise. If a release changes the layout, the raw log may come out shorter until the parser is updated. The curated summary never depends on it.

</details>

<details>
<summary><strong>Can I use this with CLAUDE.md files in subdirectories?</strong></summary>

The skills look for CLAUDE.md at the project root. If you have multiple CLAUDE.md files (e.g., monorepo), run from the relevant subdirectory.

</details>

---

## Development

`llms.txt` at the repo root is the AI-readable summary of the project. Keep it in step with this README.

```bash
python3 -m unittest discover -s tests -v   # script tests
claude plugin validate .                    # manifest check
claude --plugin-dir .                       # try the working copy
```

---

## Credits

Created by [Elia Alberti](https://github.com/EliaAlberti). Built with and for [Claude Code](https://code.claude.com/docs).

---

## License

MIT. See [LICENSE](LICENSE).
