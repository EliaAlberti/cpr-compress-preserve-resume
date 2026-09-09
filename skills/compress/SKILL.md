---
name: compress
description: Save this session to a searchable CPR log with a curated summary plus the raw transcript. Run before /compact or before ending a session. Add "quick" to skip the questions.
argument-hint: "[quick] [topic-name]"
disable-model-invocation: true
allowed-tools: Read, Write, AskUserQuestion, Bash(python3 *), Bash(mkdir *)
---

# /cpr:compress

Save this conversation as a session log that a future session can load in seconds and search by topic. The log has two parts: a structured summary you write, and the raw transcript a script appends. Run it before `/compact` or before ending the session. The CPR hooks also autosave the raw transcript before every compaction, so this skill is where the curated summary comes from.

## Where this log goes

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cpr_paths.py"`

Session id for the raw transcript: `${CLAUDE_SESSION_ID}`

## Arguments

`$ARGUMENTS`

- Contains `quick`: skip the three questions below. Include every section that has real content, and derive the topic name yourself.
- Any other words: use them as the topic name (lowercase, hyphens), and still ask the first two questions.
- Empty: run all three questions.

## The questions

Ask them with AskUserQuestion, one call each. The tool adds its own free-text option, so never add an "Other" option and never fall back to a plain-text prompt.

1. **What to preserve.** Multi-select, header "Preserve". Options: Key Learnings, Solutions & Fixes, Decisions Made, Files Modified, Setup & Config, Pending Tasks, Errors & Workarounds. Recommend the ones this session actually produced.
2. **Custom note.** Single-select, header "Custom note", exactly two options: `Skip` and `Add a custom note`. A free-text answer is the note, kept verbatim.
3. **Topic name.** Derive a 3-5 word, lowercase, hyphenated topic first (for example `api-auth-refactor`). Single-select, header "Topic name", exactly two options: `Accept: {suggested-name}` and `Provide a different name`. A free-text answer is the topic, normalised to lowercase and hyphens.

## Write the log

Filename: `{timestamp_slug}-{topic}.md` inside `logs_dir` from the block above. Create the folder if it is missing. Write only the sections the user chose, plus the three that are always present: Quick Reference, Quick Resume Context, and Custom Notes.

```markdown
# Session Log: {timestamp_display} - {topic}

## Quick Reference (for AI scanning)
**Confidence keywords:** {10-20 search terms: project names, technologies, actions, identifiers, people relevant to decisions}
**Projects:** {project names or references mentioned}
**Outcome:** {one sentence}

## Decisions Made
- {decision and the reason}

## Key Learnings
- {learning}

## Solutions & Fixes
- {what was broken, what fixed it, the command or code if short}

## Files Modified
- `{path}`: {what changed}

## Setup & Config
- {exact values: paths, flags, env names. Never paraphrase an identifier}

## Pending Tasks
- [ ] {unfinished work, next steps, blockers}

## Errors & Workarounds
- {error and the workaround}

## Key Exchanges
- {notable exchange, one line}

## Custom Notes
{the note from question 2, or "None"}

---

## Quick Resume Context
{2-3 sentences a future session needs before touching anything. This paragraph is what the SessionStart hook shows at the start of every new session, so make it carry the state.}
```

Keep bullets short and concrete. Preserve exact values. Keywords matter more than they look: `/cpr:resume <topic>` searches them.

## Append the raw transcript

Do not type the conversation yourself. After the file is saved, run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/dump_transcript.py" "{logs_dir}/{filename}" ${CLAUDE_SESSION_ID}
```

It appends `## Raw Session Log` with every user message and assistant reply, skips tool calls and thinking, mirrors the file if routing is configured, and prints the number of turns written. The archive costs zero model output tokens.

## Confirm

```markdown
## Session Saved

`{logs_dir}/{filename}`

- **Project:** {project_name}
- **Topic:** {topic}
- **Sections:** {chosen sections}
- **Keywords:** {keywords}
- **Raw log:** {N} turns appended

Next: `/compact` if you are continuing, or just close the session. `/cpr:resume` loads this back next time.
```
