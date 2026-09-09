---
name: preserve
description: Write this session's durable learnings into the project's CLAUDE.md, keeping it short and archiving stale sections. Run after important decisions or when the project's status changes.
argument-hint: "[quick]"
disable-model-invocation: true
allowed-tools: Read, Edit, Write, Glob, AskUserQuestion, Bash(python3 *), Bash(wc *)
---

# /cpr:preserve

Update the project's CLAUDE.md with what this session taught that every future session should know from the first message. CLAUDE.md is loaded at the start of every session and re-injected after compaction, so it is the right home for status, decisions, conventions and next steps, and the wrong home for narrative or anything the code already says.

## Project

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cpr_paths.py"`

`$ARGUMENTS` containing `quick` means: skip the question, preserve every category that has real content.

## Find CLAUDE.md

Look in `project_root` for `CLAUDE.md`, `Claude.md`, or `.claude/CLAUDE.md`. If none exists, ask with AskUserQuestion whether to create one at `{project_root}/CLAUDE.md` or to print the notes into the conversation instead. If the user chooses the conversation, write the same content as a short markdown block and stop.

## What to preserve

Ask once with AskUserQuestion, multi-select, header "Preserve". Options: Phase/Status Changes, Key Decisions, New Files/Structure, Patterns/Insights, Blockers/Warnings, Next Steps. Recommend the ones this session produced.

## Read, then edit

Read the current CLAUDE.md and match its structure and voice. Update existing sections in place rather than appending duplicates. Every addition should be something a future session would otherwise have to rediscover or be told again:

- Status changes as one line each.
- Decisions with the reason, in a table if the file already uses tables.
- New directories or files as a short list, not a tree of everything.
- Next steps as a checklist.

Leave out implementation detail, full file contents, timestamps, and anything the code or git history already records. Point to files instead of copying them. Keep exact values for paths, flags and identifiers.

Edit the file directly, then report:

```
CLAUDE.md updated

Preserved:
- {what changed}

CLAUDE.md is now {X} lines (target: under 200)
```

## Keep it short

Claude Code recommends CLAUDE.md files under 200 lines for adherence. After editing, check `wc -l`. If the file is over 200 lines:

1. Find archivable content: `## Session Notes (DATE)` sections older than 7 days, `## Completed Projects`, and any section whose heading contains `(ARCHIVABLE)`.
2. Show the user what archiving those would remove and the resulting line count, and ask with AskUserQuestion: archive now, or keep everything.
3. If it is still over 200 after that, list the remaining non-core sections and ask which to archive.
4. Never propose archiving a section whose heading contains `(PROTECTED)`, or the core sections: Approach, Philosophy, Paths, Structure, Key References, Links, Skills, Commands, Key Patterns, Conventions. Adapt the list to the names the file actually uses.

Archived sections go to `{project_root}/CLAUDE-Archive.md`, appended under a `## Archived: {date}` heading, and are removed from CLAUDE.md. Create the archive file with a one-line intro if it does not exist.

## No CLAUDE.md and the user declined to create one

Print a compact preservation block to the conversation with the selected categories and a two-sentence resume context, then suggest creating a CLAUDE.md so it persists.
