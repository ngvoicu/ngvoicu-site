---
title: "Specmint: persistent AI coding specs across sessions"
description: "Specmint replaces ephemeral AI coding plans with persistent specs in .specs/, working across Claude Code, Cursor, Windsurf, Cline, Codex, and Gemini CLI."
canonical: https://ngvoicu.dev/articles/specmint-persistent-ai-coding-specs/
author: Gabriel Voicu
published: 2026-03-02
updated: 2026-07-14
---

# Specmint: Persistent AI Coding Specs That Survive Across Sessions and Tools

By Gabriel Voicu, 2 March 2026

Also published on Medium.

[Specmint: AI coding specs that survive the session](https://www.youtube.com/watch?v=QSI-C57bt78)

*Prefer watching? The 3-minute video above covers the whole workflow (watch it on its own page: [Specmint: AI coding specs that survive the session](https://ngvoicu.dev/videos/specmint-ai-coding-specs/)) — or read on.*

Every AI coding tool ships with some version of "plan mode." You describe a feature, the agent thinks for a moment, and it produces a plan. Sometimes the plan is good. Sometimes it's great. But it always has the same fatal flaw: **close the terminal and the plan is gone.**

That plan you spent twenty minutes refining? The research the agent did into your codebase, the architecture decisions you talked through together, the specific file paths and function names it discovered? All of it evaporates when the session ends. Start a new session tomorrow and you're back to square one, re-explaining context that your AI already understood yesterday.

This is the problem Specmint solves — and it's why spec-driven development is becoming one of the most important practices in AI-assisted coding.

## What Is Specmint?

Specmint is an open-source tool that replaces ephemeral AI coding plans with persistent, structured specs. These specs live in a `.specs/` directory at your project root. They survive across sessions, across days, across tools.

Specmint installs as a skill — no plugin, no slash commands to memorize — and works with **Claude Code, Cursor, Windsurf, Cline, Codex, and Gemini CLI** through a single `npx` command. Every tool reads and writes to the same `.specs/` directory, so you can start a spec in Claude Code and pick it up in Cursor without losing a single line of context.

The key insight is simple: a coding plan shouldn't live in a chat window. It should live in your project, right next to your code, versioned alongside it, readable by any tool — or any human — that opens the file.

## The Problem With Plan Mode

If you've used Claude Code's plan mode, Cursor's Composer agent, or Windsurf's Cascade, you already know the pattern. You ask the AI to plan a feature. It scans some files, produces a list of steps, and starts implementing. It works well enough inside a single session.

But software development doesn't happen in single sessions.

You get interrupted. You context-switch to a different feature. You close your laptop and pick up the work on Monday. And every time, you lose the plan. Not just the bullet points — the entire context the agent built up: which files it read, what patterns it noticed in your codebase, the decisions you made together about approach, the exact point where implementation stopped.

The result is a frustrating cycle. You start explaining the same feature again. The agent asks questions you already answered. It proposes approaches you already rejected. It misses patterns in your codebase that the previous session had already discovered.

Specmint breaks this cycle by turning plans into files.

## How Specmint Works

### The Forge Workflow

The core of Specmint is the forge workflow, triggered with natural language — "forge a spec for X" or "create a spec for user authentication" — in any tool. Instead of jumping straight to a list of bullet points, Specmint runs a six-phase workflow that treats planning as real work.

**Deep research** comes first. The forge workflow reads actual files in your codebase — not just file names, but implementations. It maps your directory structure, reads your `package.json` or `Cargo.toml`, follows dependency chains, checks how similar features are currently built, and searches the web for best practices on the specific technologies involved. All of this gets saved to a research file inside `.specs/`.

**Iterative interviews** come next. Based on what the research found, Specmint asks you targeted questions — not generic ones like "what do you want to build?" but specific ones like "I see you're using Express middleware at `src/middleware/`. Should the new auth middleware follow the same pattern?" Multiple rounds of questions continue until every task in the upcoming spec can be described concretely. Each round of questions and answers is saved to an interview file.

**Spec writing** synthesizes all the research and interviews into a structured spec with phases, concrete tasks, a decision log, and resume context.

**Implementation** works through the spec task by task, checking off completed items, updating progress, and logging any decisions or deviations along the way.

### TDD Variants

Specmint ships in four variants so you can match it to how you work: `core` and `core-html` for straightforward spec-driven development, and `tdd` and `tdd-html` for a strict test-driven flow. In the TDD variants, every task starts with a failing test, production code exists only to make tests pass, and refactoring happens under green — the spec tracks the red-green-refactor state of each task as you go. The `-html` variants render your specs as professional HTML documents, with diagrams and syntax-highlighted diffs, instead of plain markdown.

### What a Spec Looks Like

A spec has phases (like "Foundation," "OAuth Integration," "Testing") each containing concrete, checkable tasks. Every task has a unique code like `[AUTH-01]`, and the currently active task is marked so any tool can find it instantly.

The most important part is **resume context** — a detailed description of exactly where implementation stopped, which files were being modified, what the next step is, and any blockers. It reads like a handoff note from one developer to another:

> Finished Google OAuth. GitHub OAuth callback handler is in progress at `src/auth/oauth/github.ts`. The authorization URL redirect works but the callback endpoint needs to exchange the code for tokens. Use the same pattern as Google in `src/auth/oauth/google.ts` lines 45-82.

When you come back a week later and say "resume," any AI tool that understands Specmint can read that context and pick up from the exact spot — no re-explanation needed.

### A Decision Log That Actually Persists

Every non-obvious technical choice gets recorded in the spec's decision log: library selections, architecture patterns, tradeoffs you evaluated. When a future session (or a different AI tool, or a new team member) reads the spec, they understand not just *what* was built but *why* it was built that way.

Similarly, a deviations table tracks places where implementation diverged from the original plan, so the spec stays useful as documentation even after the code is written.

## Cross-Tool Compatibility: One Spec Format, Any AI Coding Tool

This is where Specmint stands apart from tool-specific solutions. The `.specs/` directory is just plain files. Any AI tool that can read and write them can work with your specs.

Install the skill for whichever tools you use with a single command each, using the `-g` flag to make it globally available:

```
npx skills add ngvoicu/specmint-core -g
npx skills add ngvoicu/specmint-core-html -g
npx skills add ngvoicu/specmint-tdd -g
npx skills add ngvoicu/specmint-tdd-html -g
```

Pick one variant, or install several and let the natural-language triggers route to the right one. Once installed, the same commands work everywhere — forge, resume, pause, switch, list, and status are all plain-English triggers, not tool-specific syntax.

The practical impact: you can start a spec in Claude Code using the deep forge workflow, pause it, and then resume it in Cursor or Codex the next day. The spec — with all its research, decisions, and progress — is right there in `.specs/`, tool-agnostic and human-readable.

## Why Specs Over Plans?

### Persistence

Plans live in chat context and disappear. Specs live in your filesystem and persist forever. They diff cleanly in git. They survive session boundaries, tool switches, and team handoffs.

### Depth of Research

Plan mode typically reads a handful of files and produces a plan. Specmint's forge workflow reads through your codebase, searches the web, pulls library documentation, and then interviews you over multiple rounds before writing anything. The resulting spec reflects a level of understanding that a quick plan mode pass simply cannot match.

### Resumability

When you say "resume" in a tool configured with Specmint, it reads the active spec's resume context and picks up from the exact task, in the exact file, at the exact function where work stopped. No re-explaining. No re-scanning the codebase.

### Multi-Spec Management

Real development involves juggling multiple features. Specmint lets you pause one spec, switch to another, and come back later. A registry file tracks all your specs with their status and progress, so you can list everything at a glance.

### Accountability

The decision log and deviation tracking mean the spec doesn't just describe what to build — it documents why decisions were made and where the implementation diverged from the plan. This is useful for code reviews, for onboarding new team members, and for your future self trying to remember why you chose JWT over sessions.

### A Bonus: OpenAPI Generation

Specmint can also generate an OpenAPI specification from your codebase — scanning your routes and schemas to produce a full API document — so the same tool that plans your work can describe its surface.

## Spec-Driven Development: A Growing Practice

Specmint arrives at a moment when the industry is converging on a broader idea: spec-driven development. [GitHub released Spec Kit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/), [JetBrains documented spec-driven workflows](https://blog.jetbrains.com/junie/2025/10/how-to-use-a-spec-driven-approach-for-coding-with-ai/) with Junie, and [Thoughtworks identified it as one of 2025's key new engineering practices](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices).

The common thread is that **specifications as durable artifacts** outperform ephemeral prompts and chat-based plans for AI-assisted development. When the spec lives in a file, it becomes a shared contract between you and the AI, surviving context resets and tool boundaries.

Specmint takes this philosophy and makes it practical. You don't need to manually write spec files or learn a new template format. The forge workflow handles the research, the interviews, and the spec writing. You just describe what you want to build and answer questions.

## Getting Started in Five Minutes

Install the variant you want, then start naturally:

```
npx skills add ngvoicu/specmint-tdd-html -g
# Then in any tool: "forge a spec for user authentication with OAuth"
```

The agent will research your codebase, ask you targeted questions, and write a spec you can resume from any session, any day, any tool.

## What Specmint Is Not

Specmint is not a project management tool. It doesn't replace Jira or Linear. Specs are focused on implementation — phases, tasks, file paths, function names, technical decisions. They're meant to guide an AI coding session (or a series of sessions), not to track sprints and stakeholder requirements.

It's also not a documentation generator. While specs are readable and informative, their primary audience is the AI agent that will resume the work. They're optimized for machine-readable context, not for external stakeholders.

## Conclusion

The biggest bottleneck in AI-assisted coding isn't the model's intelligence — it's context loss between sessions. Specmint eliminates that bottleneck by moving your plans out of ephemeral chat windows and into persistent, structured files that any AI tool can read.

If you've ever closed a terminal and lost twenty minutes of planning, or re-explained the same feature to an AI for the third time, give Specmint a try. It's open source, it's free, and it works with the tools you're already using.

**Site:** [specmint.ngvoicu.dev](https://specmint.ngvoicu.dev) **Install:** `npx skills add ngvoicu/specmint-<variant> -g` (variants: `core`, `core-html`, `tdd`, `tdd-html`) **License:** MIT

---

*Specmint is created by Gabriel Voicu and is available as an open-source, universal AI coding skill.*

Gabriel Voicu

I’m a software engineer. I build AI agents that work inside large systems, and I write open-source tools for coding agents.

[More about me](https://ngvoicu.dev/about/)
