---
context: conversation
description: Smart Conversation Compression with Session Logging
model: opus
allowed-tools: Read, Write, Bash, AskUserQuestion
---

# /compress - Smart Conversation Compression

Prepares preservation notes for conversation compaction AND saves the full session to searchable logs. Run this BEFORE `/compact`.

**Workflow:** `/preserve` (optional) → `/compress` → answer questions → session saved → `/compact` (always last)

## Instructions for Claude

When the user runs `/compress`, follow these steps:

### Step 1: Ask What to Preserve

Use the AskUserQuestion tool with the following multi-select question:

**Question:** "What would you like to preserve from this conversation?"

**Options (multi-select enabled):**
1. **Key Learnings:** Technical insights, new knowledge, "aha" moments
2. **Solutions & Fixes:** Code solutions, bug fixes, commands that worked
3. **Decisions Made:** Choices, trade-offs, why we chose X over Y
4. **Files Modified:** List of files created/edited with brief descriptions
5. **Setup & Config:** Environment setup, credentials, paths, configurations
6. **Pending Tasks:** Unfinished work, next steps, blockers
7. **Errors & Workarounds:** Problems encountered and how they were solved

### Step 2: Ask for Custom Preservation (Optional)

**Contract:** Call AskUserQuestion with exactly 2 options. Do not add an "Other" option manually; the tool adds it automatically. No plain-text prompt is permitted. AskUserQuestion is always the entry point — the free-text path activates only after the tool renders, never instead of it.

Call AskUserQuestion with:
- **question:** "Anything specific you want to highlight or remember from this session?"
- **header:** "Custom note"
- **multiSelect:** false
- **options:**
  1. `{ label: "Skip", description: "No custom notes, continue with session log" }`
  2. `{ label: "Add a custom note", description: "Provide a custom note to preserve" }`

If the user selects "Skip", set custom notes to "None". If the user selects the auto-added free-text path and provides input, treat that input as the user's custom note verbatim.

### Step 3: Confirm Topic Name

**Contract:** Call AskUserQuestion with exactly 2 options. Do not add an "Other" option manually; the tool adds it automatically. No plain-text prompt is permitted. AskUserQuestion is always the entry point — the free-text path activates only after the tool renders, never instead of it.

First, analyse the conversation and derive a concise topic name (3-5 words, lowercase, hyphens) — e.g., `api-auth-refactor`.

Then call AskUserQuestion with:
- **question:** `Topic name for this session log: "{suggested-name}". Confirm or provide a different one?`
- **header:** "Topic name"
- **multiSelect:** false
- **options:**
  1. `{ label: "Accept: {suggested-name}", description: "Use the suggested topic name" }`
  2. `{ label: "Provide a different name", description: "Use a custom topic name instead" }`

Substitute `{suggested-name}` with the actual derived name. If the user selects "Accept", use the suggested name as-is. If the user selects the auto-added free-text path and provides input, treat that input as the chosen topic name (normalised to lowercase + hyphens).

### Step 4: Generate Session Log

Create the session log content with this structure:

```markdown
# Session Log: DD-MM-YYYY HH:MM - {Topic Name}

## Quick Reference (for AI scanning)
**Confidence keywords:** {extracted keywords from conversation}
**Projects:** {project names or references mentioned}
**Outcome:** {1-sentence outcome summary}

## Decisions Made
- {Decision 1 with brief rationale}
- {Decision 2 with brief rationale}

## Key Learnings
- {Learning 1}
- {Learning 2}

## Solutions & Fixes
- {Solution 1}
- {Solution 2}

## Files Modified
- `{path/to/file}`: {what changed}

## Setup & Config
- {Config item if selected}

## Pending Tasks
- {Pending item if selected}

## Errors & Workarounds
- {Error and fix if selected}

## Key Exchanges
- {Notable exchange 1, brief summary}
- {Notable exchange 2, brief summary}

## Custom Notes
{User's custom notes from Step 2, or "None"}

---

## Quick Resume Context
{2-3 sentences that would help resume this work in a future session}

---

## Raw Session Log

{FULL CONVERSATION - Copy the entire conversation history here, preserving all user messages and assistant responses. This is the searchable archive.}
```

**IMPORTANT:** Only include sections the user selected in Step 1. Always include:
- Quick Reference (for AI scanning)
- Quick Resume Context
- Raw Session Log

### Step 5: Detect Project Root & Save

**Generate filename:**
```
DD-MM-YYYY-HH_MM-{topic-name}.md
```
Example: `05-03-2026-17_30-api-auth-refactor.md`

**Detect project root:**

```
1. Get current working directory (pwd)
2. Find project root: walk up from pwd looking for CLAUDE.md or .git
3. If found: project_root = that directory
4. If not found: project_root = pwd
5. Session logs path: {project_root}/CC-Session-Logs/
6. Create folder if it doesn't exist: mkdir -p "{project_root}/CC-Session-Logs/"
7. Write session log there
```

**Save the session log:**
```bash
# Create folder if needed
mkdir -p "{project_root}/CC-Session-Logs/"

# Write session log
Write tool -> {project_root}/CC-Session-Logs/{filename}
```

### Step 6: Confirm and Instruct

Output confirmation:

```markdown
## Session Saved Successfully

### File Created

**Session Log:**
`{project_root}/CC-Session-Logs/{filename}`

### Session Summary
- **Project:** {project_root basename}
- **Topic:** {topic-name}
- **Sections preserved:** {list of selected sections}
- **Keywords:** {confidence keywords}

---

**Next step:** Run `/compact` to compress the conversation context (always last).

The session log is saved locally. Use `/resume` to load context from recent sessions.
```

---

## Guidelines

- **Be concise:** Each bullet should be actionable or informative
- **Use code blocks** for commands, paths, and code snippets
- **Include file paths** with line numbers where relevant
- **Preserve exact values:** Don't paraphrase credentials, IDs, or specific configs
- **Link context:** If something depends on something else, note the relationship
- **Extract keywords:** The "Confidence keywords" field is critical for future AI scanning
- **Full raw log:** The Raw Session Log must contain the COMPLETE conversation for searchability

---

## Confidence Keywords Extraction

When generating the "Confidence keywords" field, extract:
- Project names (my-api, user-dashboard)
- Technical terms (auth, middleware, migration, deploy)
- Action types (refactor, fix, create, update, delete)
- Tool/framework names (React, PostgreSQL, Docker)
- People mentioned (if relevant to decisions)
- Specific identifiers (issue numbers, ticket IDs)

These keywords enable the `/resume` skill to find relevant sessions via search.

---

## Example Output

```markdown
## Session Saved Successfully

### File Created

**Session Log:**
`/home/user/my-project/CC-Session-Logs/05-03-2026-17_30-api-auth-refactor.md`

### Session Summary
- **Project:** my-project
- **Topic:** api-auth-refactor
- **Sections preserved:** Decisions Made, Key Learnings, Files Modified
- **Keywords:** auth, JWT, middleware, refresh-tokens, session-management
```
