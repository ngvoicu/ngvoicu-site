---
title: "Becoming an AI Native Company: A Guide — Gabriel Voicu"
description: "How an engineering team goes from using AI on the side to building with agents: session context, specs, a shared knowledge base and cross-model review."
canonical: https://ngvoicu.dev/becoming-an-ai-native-company/
author: Gabriel Voicu
published: 2026-07-04
updated: 2026-11-26
---

# Becoming an AI Native Company

A practitioner’s guide, from my workshop

By Gabriel Voicu, published 4 July 2026, updated 26 November 2026

Most companies use AI on the side. Someone opens a chatbot, pastes in a question and copies the answer back into their real work. That helps, but the work itself stays the same.

In an AI-native company, AI steps are built into how the work gets done. A simple test: take the AI out, and the workflow stops working.

I build software with AI agents every day, and I help engineering teams do the same. This guide is the workshop I give, written down.

## What is an AI-native company?

An AI-native company redesigns how it builds software, and how it keeps what it knows, so that people and agents work together as one system.

I find it useful to separate two terms.

**AI-enhanced:** people use AI tools by hand, each in their own way. It helps, and the work goes faster. Remove the AI and everyone goes back to how they worked before.

**AI-native:** the workflow has AI steps built in on purpose. Those steps run the same way every time and leave a record you can check, so you can scale them safely. The agents write the drafts and do the routine work. People stay in the loop: they decide whether the work is correct and whether a risk is worth taking, and they set the direction.

The rest of this guide covers how a team gets there.

## The engine and the harness

Start with the parts. Most of the confusion I see in companies comes from mixing them up.

A large language model (LLM) predicts the next token. At scale that turns into useful work: it can explain, summarize, plan, write code and reason through a problem. On its own, though, an LLM can’t read your files or run your tests, and it doesn’t remember what you said ten minutes ago.

A **harness** wraps the LLM in what it needs to work as an agent: tools it can call, a file system, permissions, a context window, session memory and an interface. The model does the reasoning, and the harness lets it act.

I think of the LLM as the engine and the harness as the car around it. Together they make an agent.

The difference matters in practice. Claude Code, Cursor and Codex are harnesses, and the same model can run inside several of them. The harness you pick changes how the work feels. For serious work in a repository, the command-line harnesses are usually the most capable, and desktop apps are the easiest place to start. You’ll switch between models and harnesses depending on the task, and that’s normal. Pick the model for the domain, then set the effort for how hard the task is.

## Session context

Every session starts empty. The agent knows nothing about you or your project until something is loaded into its context, which is its working memory.

Context is measured in tokens, and English runs about 1.3 tokens per word. During a session it only grows. The harness loads a starting set when it launches, and every turn adds more: your prompts, the agent’s replies, whole files it has read, tool output, stack traces, and the dead ends you backed out of ten turns ago.

Most teams lose quality here without noticing. Every turn sends the whole session to the model again, so a heavy session gets slower and more expensive, and it uses up your limits faster. **Accuracy drops too.** The agent picks up old plans that no longer apply, and its answers get vague because the important facts are buried under logs and abandoned attempts.

The fix is context hygiene, and it’s worth teaching to the whole team:

- **Compact** when the goal hasn’t changed but the chat has gotten heavy. Compress the history into decisions and open tasks.
- **Start new** when the goal changes or the session gets confused. A new task should get fresh working memory and a short handoff.
- **Prefer file references** over pasting large chunks into the chat.
- **Re-read the source of truth** when accuracy matters. Have the agent read the current files again.

A bigger context window helps less than you’d think. Even a million-token window works better when what’s in it is clean and on topic.

## Project files and a knowledge base

Because each session starts empty, the first real setup step is to teach the agent about your project once, in files it reads every time.

**CLAUDE.md** and **AGENTS.md** are those files. They’re plain files in your repo, like a README written for the AI. They hold the tech stack, the folder structure, your conventions and the rules that must never be broken, such as “always write tests first,” “never modify the schema directly” or “SQL uses snake_case.” The agent reads them at the start of every session. Commit them to git and every agent on the team works from the same rules. New people also get going faster, because the agent already knows the project.

On top of those files, agents now keep their own auto-memory: notes they write and read back by themselves. It’s handy, but recall is *probabilistic*. The agent may bring back the right note, or it may not. So put anything that **must** be followed in CLAUDE.md and AGENTS.md, and leave the nice-to-remember details to auto-memory.

Neither of those is the place for your team’s knowledge. Architecture decisions and the reasons behind them, or the production issue you debugged last quarter, belong in a knowledge base the whole team shares, kept in git.

For this I built **[Kluris, a git-backed knowledge base for coding agents](https://kluris.ngvoicu.dev)**. It’s an open-source CLI, a single binary written in Rust, that creates knowledge repositories called brains. Each piece of knowledge is a Markdown file called a neuron, and neurons are grouped into lobes and linked by synapses. Any coding agent can search the brain with BM25 keyword search, so there are no embeddings to maintain. Agents learn from it and propose additions, and a person approves every write. Nothing is saved automatically.

Once something is in the brain, every teammate’s agent can find it in its next session.

## Vibe coding and specs

There are two ways to work with a coding agent, and mixing them up is the most expensive mistake I see.

**Vibe coding** means you describe what you want in plain language and steer by feel while the agent builds. There’s no formal spec; you react to what shows up. It’s fast, and it’s the right tool for prototypes, throwaway demos and trying UI ideas while the requirements are still fuzzy.

Stop vibe coding once decisions need to stick: in production code with real users, in work several people have to understand, in anything that touches security, payments or data integrity, and in anything you can’t afford to start over.

In both cases you won’t get it right in one prompt. You prompt, the agent drafts, you review and refine, and a few turns later it does what you meant. A person steers every turn of that loop while the agent types.

When the work has to stick, start the loop from a plan you’ve reviewed. **Plan mode** is the first step. The agent stops, looks through the repo, explains what it wants to do and points out the risks, then waits for your approval before it changes any file.

**Spec-driven development** takes plan mode further. A plan from plan mode lives in the chat and is gone when the session ends. A spec is a file in the repo, and it stays there. You draft it, review it, update it and implement it, and later sessions pick it up again.

To do this, I wrote **[Specmint, spec-driven development for AI coding agents](https://specmint.ngvoicu.dev)**. It installs as a skill in your coding agent and handles a spec from start to finish. Before it writes anything, it researches your codebase and interviews you. It saves the spec in `.specs/`, where a later session can resume it, and its test-first variants work through the spec red, green, refactor. It works with Claude Code, Cursor, Windsurf, Cline, Codex and Gemini CLI, and it’s free and MIT-licensed. The implementation and the reviews both go back to the spec as the one source of truth.

## Cross-LLM adversarial review

Put the pieces so far together and you get a workflow you can repeat. I call it the Forge Flow, and it’s the first working shape of an AI-native team.

People make the decisions, and the AI does the writing. The tests and CI check what it wrote. You write the spec and the knowledge base together with the agent, and both stay in the repo. The steps: receive the requirements, create a branch, write the spec (a person with AI help), implement with tests (the AI), review and polish (a person with AI help), run CI, update the knowledge base, archive the spec.

The next addition, review by other models, improves the quality of everything else. No single model is best at everything, and an author model can’t see its own blind spots.

So write the spec with one strong author model. Then give the same work to one or more *different* models, each in a fresh session, and ask them to find what’s wrong with it. Feed the best critiques back to the author, and implement only what you and the author agree is right. A model from another family finds the holes the author can’t see, like a missing dedupe window, an index that will crawl under load, or an edge case nobody wrote down.

### The Enhanced Forge Flow

The full loop, with both review gates in place. One model writes the spec with you. Then one to four other models review it, each in a fresh session, from the same model family or a different one. The author model gets the best critiques back, and you implement only what you and the author model agree on. The code goes through the same review.

1. Receive\
   Requirements Human

2. Create\
   Branch Human

3. Write Spec research, interview one LLM, e.g. Claude Opus Author LLM + Human

   [Kluris memory brain](https://kluris.ngvoicu.dev) [Specmint spec engine](https://specmint.ngvoicu.dev)

4. Review Spec 1–4 fresh LLM sessions Adversarial review

   [ConsensFlow](https://consensflow.ngvoicu.dev)
   - GPT 5.5
   - DeepSeek 4.3 Pro
   - Claude Fable
   - Claude Opus

5. Implement\
   \+ Tests accepted feedback Author LLM

6. Review\
   & Polish AI-assisted Human

7. Review\
   Implementation 1–4 fresh LLM sessions Adversarial review

   [ConsensFlow](https://consensflow.ngvoicu.dev)
   - GPT 5.5
   - DeepSeek 4.3 Pro
   - Claude Fable
   - Claude Opus

8. Run Tests\
   CI / CD CI/CD

9. Update\
   Memory knowledge base AI-assisted Human

   [Kluris memory brain](https://kluris.ngvoicu.dev)

10. Archive\
    Spec Human

Doing this by hand means switching tools and losing context, so I built **[ConsensFlow, a desktop app that runs a team of AI coding agents on your project](https://consensflow.ngvoicu.dev)**. You talk to one agent, the Chief of Staff. It plans the work and puts tasks on a board. Its staff of workers, advisors, reviewers and testers take the tasks, each in its own terminal of Claude Code, Codex, Pi, Devin or Muse Code, with your own logins. Put the author on one harness and the reviewers on others, and the review above runs in fresh sessions of different models, with the handoff done for you and every finding back on the board. Advisors and reviewers never change a file, and if you turn on approval, every message between agents waits for you to pass it on.

## Harnesses everywhere

Almost everything so far has been about coding harnesses. The bigger idea is that *every repeatable workflow can get its own harness*.

A harness gives an LLM context, tools, data, guardrails, memory and a loop to run in. A company becomes AI-native by building small systems like that around its work. Better prompting is only a small part of it.

Take a payments team. One harness runs all the time. It reads production logs and traces, asks an LLM to explain each failure and stores the analysis. A second harness reads that analysis and the team’s Kluris brain, which holds the domain decisions and business rules. It patches the code, runs the tests and opens a merge request. Then a person reviews the diff and decides what ships, including whether the business risk is acceptable. The harnesses run as one flow, and the human check sits where the risk is.

**Skills** make those harnesses predictable. AI is probabilistic: ask the same thing twice and it may take two different paths. A skill is a set of Markdown instructions with steps, constraints, examples, reference files and success criteria, and it narrows the path before the agent acts. Wrap a business API in a small CLI, then write a skill that says which command to run, in what order and what to check first. Then the agent operates your systems by following the procedure.

This scales because skills are plain files. Put them in a shared repo and every team’s agent follows the same review rules, release checklist and incident runbook. When someone finds a better way, you edit the skill once, and from the next session the whole company works the new way. New hires get the same playbook on their first day.

Each spec, decision, review, lesson, skill and brain neuron is written down in a file that outlives the session that created it. Together they add up to what the company knows.

## Teaching your people

Getting a whole engineering team to change how it works is harder than choosing the tools. It has to happen without chaos, and without anyone feeling replaced.

I’ve learned a few things helping teams make this change.

**Teach the mental model before the tools.** Engineers who understand the engine and the harness, context hygiene, and when to vibe code and when to write a spec make good decisions in any tool. People who memorized one tool’s buttons are lost as soon as it changes.

**Say out loud that people keep the decisions.** The quickest way to lose people is to make them feel the AI is grading them or replacing them. Tell them plainly that the agent writes and they decide. The rest of the approach depends on it.

**Start with one project.** Pick it this week. Write its CLAUDE.md, plan before you build, write one spec and save one neuron of real knowledge. Let the loop run on that project, then let the people who worked in it teach the next team.

**Make the wins last.** Put your effort into files that stay after the session, like a committed CLAUDE.md, a spec in `.specs/`, a brain neuron or a shared skill, because every later session can use them.

A team becomes AI-native one workflow at a time. You redesign each one so people and agents work as one system, and you write down what you learn so the next loop starts from it.

## Work with me

If your engineering team wants to move from AI-enhanced to AI-native, I can help in three ways:

- **The workshop:** the hands-on session this guide comes from. It takes your team from first principles to a working Forge Flow.
- **Team training:** the mental models and daily habits that work in any tool, such as context hygiene, spec-driven development, cross-LLM review and writing knowledge down.
- **Adoption engagements:** I join your team, design the workflows with you and set up the tools. We also write the knowledge base and the skills your team keeps using.

When an engagement ends, the work stays in your repositories: a committed CLAUDE.md the whole team shares, a first spec in `.specs/` and a first brain neuron of real team knowledge. Your team can keep running the Forge Flow from there after I leave.

The tools I mention in this guide, [Specmint](https://specmint.ngvoicu.dev), [Kluris](https://kluris.ngvoicu.dev) and [ConsensFlow](https://consensflow.ngvoicu.dev), are free and open source, and you can start with them on your own.

To work with me, email [office@ngvoicu.dev](mailto:office@ngvoicu.dev) or call [+40 734 704 910](tel:+40734704910).

Gabriel Voicu

I’m a software engineer. I build AI agents that work inside large systems, and I write open-source tools for coding agents.

[More about me](https://ngvoicu.dev/about/)
