# Token Savings Analysis

This document models the token cost of working on a typical software project across multiple Claude Code sessions, **with and without CPR**, and quantifies the savings.

The numbers are **analytical estimates**, not telemetry. All assumptions are stated explicitly so you can substitute your own values.

---

## TL;DR

Under the modelled assumptions below, **CPR saves ~24% of session-transition tokens in the low case, ~55% in the median case, and ~68% in the high case**. On a 10-session project, that translates to roughly **~83,250 tokens saved at the median**, rising to **~535,800 tokens** in the largest modelled case (20 sessions, high-context profile).

CPR is **net negative** under the modelled assumptions for single-session work or trivial one-off bugs. The breakeven point, where avoided rework exceeds CPR's own overhead, is reached as soon as a follow-up session would otherwise repeat ~3,700 tokens of context-rebuild work. For most multi-session projects this happens by session #2, but it depends on how much cross-session context exists.

> **How the headline numbers are derived:** the percentages come directly from the per-transition Savings table further down (`Savings ÷ Without-CPR cost`). The project totals come from `Savings per transition × (Sessions − 1)`. All inputs are stated as low/median/high ranges, not point estimates. Substitute your own values to recompute.

**What this analysis excludes:**
- Human time saved (or added) by CPR's prompts at session boundaries.
- Any overlap with Claude Code's built-in `/compact` summarisation.
- Savings lost to stale, incomplete, or topic-misaligned CPR logs.

---

## Baseline Scenario

A **typical multi-session software project**:

| Variable | Low | Median | High |
|---|---|---|---|
| Sessions over 1-4 weeks | 5 | 10 | 20 |
| Session length | 45 min | 90 min | 120 min |
| Active files | 20 | 40 | 80 |
| Prior-context depth (sessions back) | 1 | 2 | 3 |

The cost we're modelling is **session transition**: what it costs to move from one session to the next. The cost of the actual work inside each session is roughly equal in both cases and is not part of the comparison.

---

## Without CPR: Session-Restart Cost

Each new session, the user has no durable memory of prior sessions. They must rebuild context from scratch.

| Cost component | Low | Median | High |
|---|---|---|---|
| User re-explains goals, constraints, prior progress (chat input) | 150 | 450 | 1,200 |
| Claude re-reads relevant source files | 3,000 | 12,000 | 30,000 |
| Claude re-derives architecture, invariants, prior decisions | 500 | 2,000 | 5,000 |
| Conversation rebuild + back-and-forth clarification | 1,000 | 1,500 | 2,500 |
| Repetition: forgotten conventions, prior rejected approaches | 200 | 800 | 2,500 |
| **Total per transition** | **4,850** | **16,750** | **41,200** |

### Notes on each component

- **Re-explanation** assumes ~150 words at the low end (a quick reminder), ~300 words at median (a focused brief), ~800 words at high end (a full context dump). Tokens estimated at ~1.5 per word.
- **Re-reading files** assumes 3-5 small files at low, 8-12 medium files at median, 15-25 files at high. Average source file ≈ 200-500 lines ≈ 1,000-3,000 tokens.
- **Re-deriving** captures the inference cost of Claude rebuilding its mental model: invariants, design choices, debugging hypotheses already worked through.
- **Conversation rebuild** captures questions Claude has to ask the user that prior sessions had already answered, plus the tokens to handle those answers.
- **Repetition** captures cases where the same convention or a previously-rejected approach gets re-tried because it was forgotten.

---

## With CPR: Session-Transition Cost

Each transition costs `/compress` at the end of the previous session, and `/resume` at the start of the next.

| Cost component | Low | Median | High |
|---|---|---|---|
| `/compress` at end of prior session (summarisation + write + AskUserQuestion) | 1,500 | 2,500 | 4,000 |
| `/preserve` durable learnings write (occasional, amortised) | 0 | 500 | 1,500 |
| `/resume` at start of next session (read CLAUDE.md + 1-3 logs) | 2,000 | 4,000 | 7,000 |
| Reconciliation, light search, parse | 200 | 500 | 500 |
| **Total per transition** | **3,700** | **7,500** | **13,000** |

### Notes on each component

- **/compress** runs once at end of session: it summarises the conversation, asks the user what to preserve, writes the structured log. Most of the cost is inference (summarisation), not file I/O. The raw conversation archive is appended by `scripts/dump_transcript.py` from the Claude Code transcript on disk, so it costs zero model output tokens. Before v1.2.0 the model re-typed it: measured across 42 real sessions of 20+ turns, that was a median of ~4,300 output tokens per `/compress` (upper quartile ~9,900, largest ~640,000), on top of the figures above.
- **/preserve** is optional and used less often than `/compress`, usually only when a durable project-level learning emerges. Cost amortised.
- **/resume** reads `CLAUDE.md` (typically 1,000-3,000 tokens) and 1-3 recent session log summaries (typically 500-1,500 tokens each, of which only the summary section is needed).
- **Reconciliation** covers any extra tokens needed when log content needs to be reconciled with current code state.

---

## Savings

```
Savings per transition = Without-CPR cost − With-CPR cost
```

| Case | Without CPR | With CPR | Savings | % saved |
|---|---|---|---|---|
| Low | 4,850 | 3,700 | **1,150** | **24%** |
| Median | 16,750 | 7,500 | **9,250** | **55%** |
| High | 41,200 | 13,000 | **28,200** | **68%** |

### Across a project

A project has `(N − 1)` transitions for `N` sessions.

| Project size | Sessions | Transitions | Median savings |
|---|---|---|---|
| Small | 5 | 4 | **~37,000 tokens** |
| Medium | 10 | 9 | **~83,250 tokens** |
| Large | 20 | 19 | **~175,750 tokens (median) / ~535,800 tokens (high)** |

---

## Breakeven and When CPR Doesn't Help

CPR has a fixed cost per transition (the `/compress` + `/resume` pair). Savings appear only when the avoided rework exceeds that cost.

CPR is **net negative** for:

- **Single-session projects**, where there's no next session to amortise the `/compress` cost into.
- **One-off bug fixes** completed in a single session.
- **Throwaway scripts** with no cross-session continuity.
- Projects where `CLAUDE.md` and session logs become **stale or incorrect**. Wrong context can cost more than no context.

Under the modelled assumptions, CPR tends to be **net positive** for:

- **Multi-session features** spanning 3+ sessions.
- **Long-running refactors** with accumulated decisions.
- **Projects with conventions** that need consistent enforcement across sessions.
- **Onboarding work** where prior decisions and rejected approaches matter.

The breakeven is reached as soon as the next session avoids ~3,700 tokens of context-rebuild work, which is roughly the cost of re-reading 1-2 source files plus a brief user re-explanation. Most multi-session projects cross this threshold by session #2, but the actual breakeven point depends on the specific work, file sizes, and how much context is preserved between sessions.

---

## Caveats

1. **These are estimates, not measurements.** Real-world variance is wide. Substitute your own component values to model your specific workflow.
2. **Token costs vary with file size, language, and conversation style.** A Markdown-heavy doc project will read differently than a Rust codebase.
3. **Quality of `/compress` and `/resume` output matters.** Bad summaries can cost more than they save. The `/compress` skill's structured log format and `/resume`'s confidence-keyword scanning are designed to keep summaries useful.
4. **CPR adds friction at session boundaries.** The `/compress` step asks the user a few questions before saving. This is intentional, but adds ~30 seconds of human time per transition.
5. **The numbers above don't account for `/compact`.** Claude Code's built-in `/compact` summarises the current conversation but doesn't persist across sessions. CPR sits *alongside* `/compact`, not as a replacement.

---

## Methodology

The cost ranges in this analysis come from the following heuristics:

- **Token-per-word ratio:** ~1.3-1.5 for English prose, used for chat-input estimates.
- **Token-per-line ratio:** ~5-8 for typical source code, used for file-read estimates.
- **Inference cost for summarisation:** estimated at 1.5-2× the size of the output, since the model reads the full conversation to produce the summary. The raw log is excluded: it is copied from disk by script, not generated.
- **Raw log size:** measured with `scripts/dump_transcript.py` over 42 local Claude Code sessions of 20+ turns, at ~4 characters per token.
- **CLAUDE.md and session log size:** based on observed sizes in real CPR-using projects (1,000-3,000 tokens for CLAUDE.md, 500-1,500 tokens per log summary section).

All estimates are stated as Low / Median / High ranges to avoid single-point claims. For your own project, plug in the values that match your context and recompute.

---

*Last updated alongside CPR v1.2.0. Methodology may evolve as real-world usage data becomes available.*
