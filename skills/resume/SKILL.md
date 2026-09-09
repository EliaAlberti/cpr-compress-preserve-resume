---
name: resume
description: Load context from recent CPR session logs, and search past sessions by topic. Use at the start of a session or when you need to know what happened before.
argument-hint: "[N] [topic]"
disable-model-invocation: true
allowed-tools: Read, Bash(python3 *)
---

# /cpr:resume

Bring this session up to speed from the project's session logs. The data below was collected by a script, so there is nothing to open or list: read it, then write the report.

Usage: `/cpr:resume` for the last 3 sessions, `/cpr:resume 5` for the last 5, `/cpr:resume auth` to also search every log for "auth", `/cpr:resume 10 migration` for both. CLAUDE.md is already in your context; do not re-read it.

## Session data

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/resume_context.py" $ARGUMENTS`

## Report

Write the report from the data above, in this shape. Keep each bullet to one line, and keep exact values from the logs: paths, identifiers, flags.

```
══════════════════════════════════════════════
 RESUMING: {project name}
══════════════════════════════════════════════

CONTEXT:
- {what was last worked on}
- {important project state from the logs and CLAUDE.md}

BLOCKERS:
- {from the logs, or "None"}

══════════════════════════════════════════════
 MOST RECENT SESSION: {date time}
 Topic: {topic}
══════════════════════════════════════════════

**Keywords:** {confidence keywords}
**Outcome:** {outcome}

**Key points:**
- {decision, learning or fix}
- {pending task}

══════════════════════════════════════════════
 PREVIOUS SESSIONS ({count})
══════════════════════════════════════════════

- {date}: {topic}, {outcome in a few words}

══════════════════════════════════════════════
 RELATED SESSIONS (topic: "{topic}")      only when a topic was given
══════════════════════════════════════════════

- {date}: {topic}, {why it matched}

══════════════════════════════════════════════
 READY TO:
══════════════════════════════════════════════

- {next step from CLAUDE.md or the latest log}
- {pending task}
══════════════════════════════════════════════
```

If the data says there are no logs yet, say so in two lines and point to `/cpr:compress`. If it lists autosaved transcripts newer than the last curated log, mention them once: they hold the full conversation but no summary, and `/cpr:resume <topic>` searches them.

Read a raw log only when the user asks a question the summaries cannot answer; the summaries exist so that the raw archives never have to be loaded.
