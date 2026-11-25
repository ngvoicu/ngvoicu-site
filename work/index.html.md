---
title: "Work: AI agents, ZeeSpire and open source — Gabriel Voicu"
description: "Enterprise AI agents and application security, my company ZeeSpire, and open source: Specmint, Kluris, ConsensFlow, providers.dev, Provimux, pi-cache-keeper."
canonical: https://ngvoicu.dev/work/
author: Gabriel Voicu
---

# Work

## Enterprise work

### Agents that fix security findings

![A list of warnings goes to two small robots that patch a page of code, which then passes through a pipeline to a green check mark](https://ngvoicu.dev/images/work/remediation-agents-800.webp)

**What it is.** Security scanners find problems faster than teams can fix them, and most of the fixes are repetitive. On a cross-team initiative, we built agents that take a static-analysis finding all the way to a merge request and through the project’s pipeline. They now open merge requests for teams across the organization, and another team built them into its own agent platform.

**My part.** I was one of the lead engineers. I built the remediation agents and shaped how they stay safe and how their work gets checked. Every finding is sorted first: the agent may fix it, a developer gets guidance for the fix, or it’s outside what the agent may touch. The security owners carry the risk, so we agreed with them what the agent may do on its own. The model has no credentials and can’t push code; plain, deterministic code does those steps. Tool checks and a separate verification agent look at every fix, and a failed check guides the next attempt. Then a second loop works on whatever breaks in the project’s own CI.

> “The challenge was not simply to have AI generate a fix, but to build a workflow that engineering and security could trust.”

Director of software engineering and distinguished engineer, about automating vulnerability fixes

**Stack:** AI agents, static analysis, merge requests, CI pipelines.

### The shared security library and SDK

![A tangle of separate gatekeeper boxes fades away behind a tidy grid of six services, each with the same small shield and lock inside](https://ngvoicu.dev/images/work/security-sdk-800.webp)

**What it is.** My department’s services used to check security in different places: in proxies in front of them, and in small services that did nothing but validate requests. Every fix had to be made more than once. Now one library inside each service does it, with an annotation for each kind of authentication, from OpenID Connect with enterprise identity providers to HMAC between services, device validation and role checks. The same endpoint can serve clients that send different kinds of tokens.

**My part.** With a colleague, I rewrote the library and integrated the identity providers into it. I led the work on the SDK around it, which puts security, auditing, error handling and secrets in one place, with a shared bill of materials so dependency upgrades happen once for every service. I proposed moving the checks out of the proxies and into the services, then delivered the change and removed the proxy layer. The rewrite helped close findings from penetration tests and let us retire the validation services. Separately, I built a proof of concept for securing Java applications with OAuth, and another part of the company adopted it for all of its Java applications.

> “Excellent work rewriting the Security Library covering multiple authentication and authorization needs in a single library which can be integrated to any application to secure the endpoints.”

A senior colleague, about the library a colleague and I rewrote

**Stack:** OAuth 2.0, OpenID Connect, JWT, HMAC, Vault for secrets, a shared bill of materials.

### MCP agents for an internal platform

![A person at a laptop asks a question in a speech bubble; a coordinator robot passes it to three worker robots, each plugged into a different service](https://ngvoicu.dev/images/work/platform-agents-800.webp)

**What it is.** Agents in front of an internal platform, so teams can ask for what they need in plain language. The platform has many capabilities, each behind its own API, and every team that used it had to learn them one at a time. This was the first multi-agent setup in that stack.

**My part.** I built it: MCP servers in front of two of the platform’s services, a worker agent for each, and an orchestrator agent that keeps the session and coordinates them. Calls are authenticated, with tokens checked against the identity provider’s published keys, and audit-logged. On my own initiative I also built a desktop tool for the Kubernetes clusters our services run on: sign-in across clusters, the logs of every pod in a deployment in one filtered view, AI agents to help read them, and a read-only mode. It does the work of two tools developers used to switch between.

**Stack:** MCP, multi-agent orchestration, JWT and JWKS, audit logging, Kubernetes.

### Moving a department to AI-native work

![Four colleagues around a table with laptops and a shared checklist, helped by two small robots](https://ngvoicu.dev/images/work/ai-native-800.webp)

**What it is.** When generative AI arrived, a few people in my department tried it on the side. Some worried it would replace them. Others didn’t trust AI-written code in production. Both worries were fair. Today spec-driven development is the department’s standard way of building software with AI.

**My part.** I was given the role of driving the move. Before I asked anyone to adopt spec-driven development, I proved it on a real modernization project, with Specmint and later Kluris. I made it a one-command install, answered questions in a channel set up for them, and gave talks and hands-on demos, tailored to other teams’ applications when they asked. I also wrote a skill, tested by its own evaluation suite, that teaches coding agents the company’s design-system components, and curated knowledge bases for the systems we own. When the whole department had to pick up Go, I set up a coding dojo and we learned it together.

**Stack:** Specmint, Kluris, spec-driven development, agent skills with evaluation suites.

- [Consulting](https://ngvoicu.dev/consulting/)
- [The AI-native guide](https://ngvoicu.dev/becoming-an-ai-native-company/)

### Rebuilding the services that deliver software to devices

![A tangle of old wiring fades out behind three clean service blocks that send small packages to a sensor, a box-like device and a screen](https://ngvoicu.dev/images/work/modernization-800.webp)

**What it is.** The services I work on send software and files out to devices in the field. When something goes wrong there, customers feel it, and issues used to be fixed one at a time as they came in. We rebuilt the services on a simpler architecture with clearer, reusable API contracts. They’re now simpler to run and to change.

**My part.** I analyzed the components and recommended the rebuild, then built many of the new services myself: access, upload, retrieval, audit, email and antivirus scanning, several with reusable clients. I moved the gateway from Zuul to Spring Cloud Gateway, with caching and a Spring Security upgrade, added pagination where consumers needed it, and retired old endpoints in stages so no consumer broke. Along the way we moved the services to the company’s Kubernetes platform, and I helped build a shared OpenTelemetry logging framework. I also worked on modernizing a log-processing suite and helped design a multi-year migration of stored data between storage platforms.

**Stack:** Spring Cloud Gateway, Spring Security, Kubernetes, OpenTelemetry, Angular, Python, Kafka.

### Earlier work

**What it is.** Two earlier roles, in 2020 and 2021.

**My part.**

- In 2020, at the same technology company, we built tools for configuring enterprise storage systems and delivered one in time for its product’s launch. I brought its data import down from 40 minutes to under 40 seconds with careful Hibernate and JPA work.
- In 2021, at a financial-services company, I rebuilt the microservice template that new services started from, with modern patterns, standard configuration and tests built in, and wrote a generator that set up a new service in minutes. I also re-engineered two troublesome services, including a move to a different database.

**Stack:** Java, Hibernate and JPA, microservices.

## ZeeSpire

[ZeeSpire](https://zeespire.com/) is my software company, which I co-founded. It started in 2016, when I began taking on Java work as a freelancer. Today we build AI integrations and custom software for clients, and products of our own.

### Atlas

![Three documents pulled from a stack of papers feed the answer in a chat window](https://ngvoicu.dev/images/work/atlas-800.webp)

**What it is.** An enterprise chat assistant built on retrieval-augmented generation, with multi-stage retrieval.

**My part.** It’s one of my own products. I built it end to end.

**Stack:** Google Agent Development Kit for the agents, Qdrant for vector search, Keycloak for sign-in.

### Burn The Burnout

![A short check-in form beside a gauge running from yellow to green, with a rising trend line and a potted plant](https://ngvoicu.dev/images/work/burn-the-burnout-800.webp)

**What it is.** A platform for regular wellbeing check-ins, burnout risk tracking and follow-up support at work. Employees answer short questionnaires and get scores, a color-coded risk level and personal recommendations. When the risk is high, it can suggest or start a structured support plan with activities over a set period. Managers see risk levels and trends for their direct reports, and HR sees teams and the organization as heatmaps. Those views show scores and risk levels, without individual questionnaire responses. An in-app assistant answers questions about the platform and burnout from a curated knowledge base, with access scoped to the person’s role.

**My part.** It’s my product. I designed it, built it end to end and run it in production, and I make its product and engineering decisions. I designed it around separate company tenants, with tenant-scoped queries, database constraints, and privileged-role checks against both the token and the database. The evaluation flow includes backend checks for explicit employee consent. I designed the assistant to stay within its source material, say when it doesn’t know, and avoid diagnosis. It’s live at burntheburnout.ro, in Romanian and English.

**Stack:** Kotlin, Spring Boot 4, PostgreSQL, Next.js 16, React 19, Keycloak, a small TypeScript service for the assistant, Testcontainers.

- [Visit burntheburnout.ro](https://burntheburnout.ro/en)

### InYourMind

![A comfortable armchair beside a simple web page with a contact form, and an envelope flying out of it](https://ngvoicu.dev/images/work/inyourmind-800.webp)

**What it is.** A presentation and intake site for a psychotherapy and psychiatry practice, in Romanian and English. Visitors find the practice and send an intake or contact request, which reaches the practice by email. There is no application database.

**My part.** We built it at ZeeSpire.

**Stack:** Astro, as a static site on Cloudflare Pages, with forms sent through Resend.

- [Visit inyourmind.ro](https://inyourmind.ro)

### AI-native talks and consulting

![Gabriel at a whiteboard, running a workshop for a small team of developers](https://ngvoicu.dev/images/consulting/workshop-800.webp)

**What it is.** Talks and workshops, from “what is an LLM?” all the way to AI-native companies, software factories and AgentOS, and hands-on training for developers.

**My part.** I give them myself, on-site or remotely, and I can join a team and set it up in its own repositories.

- [Consulting](https://ngvoicu.dev/consulting/)
- [The AI-native guide](https://ngvoicu.dev/becoming-an-ai-native-company/)

## Open source

Six MIT-licensed tools for AI coding agents and the models behind them, all from 2026. I build them and use them in my own work.

### Specmint

![Two hands pass a checklist document from one terminal window to another, like a baton](https://ngvoicu.dev/images/work/specmint-800.webp)

**What it is.** Coding agents lose their plan when the session ends. Specmint keeps it. It researches your codebase, interviews you, then writes a spec with phases, tasks, a decision log and resume context into `.specs/`. The next session picks it up, in whichever tool you open.

**My part.** I wrote it. It comes as four skills: core and test-first, each writing specs as Markdown or HTML. The test-first variants work red, green, refactor.

**Stack:** Agent Skills. Works with Claude Code, Codex, Cursor, Windsurf, Cline and Gemini CLI.

**Install:**

```
npx skills add ngvoicu/specmint-core -g
```

**Three more variants**

- ```
  npx skills add ngvoicu/specmint-tdd -g
  ```

  Test-first.

- ```
  npx skills add ngvoicu/specmint-core-html -g
  ```

  Specs as HTML, with diagrams, diffs and mockups.

- ```
  npx skills add ngvoicu/specmint-tdd-html -g
  ```

  Test-first, as HTML.

- [specmint.ngvoicu.dev](https://specmint.ngvoicu.dev)
- [The article](https://ngvoicu.dev/articles/specmint-persistent-ai-coding-specs/)
- [The video](https://www.youtube.com/watch?v=QSI-C57bt78)

### Kluris

![A brain drawn as linked note cards, with three robot terminals reading from it and a person ticking a new note with a check mark](https://ngvoicu.dev/images/work/kluris-800.webp)

**What it is.** Agents start every session knowing nothing about your team. Kluris gives them one shared brain: a git repository of Markdown notes, organized as lobes, neurons and synapses, that agents search with ranked keyword search. Agents propose new knowledge, and a person approves every write.

**My part.** I wrote it. It’s a single binary, written in Rust, that installs each brain as a skill in your coding agents, among them Claude Code, Codex, Cursor, Copilot and Hermes. Every command keeps the brain in step with your team through git.

**Stack:** Rust, Markdown in git, BM25 keyword search. Runs on macOS, Linux and Windows.

**Install:**

```
curl -fsSL https://kluris.ngvoicu.dev/install.sh | sh
```

**On Windows**

- ```
  irm https://kluris.ngvoicu.dev/install.ps1 | iex
  ```

  In PowerShell.

- [kluris.ngvoicu.dev](https://kluris.ngvoicu.dev)
- [The article](https://ngvoicu.dev/articles/the-sme-your-team-never-had/)
- [The video](https://www.youtube.com/watch?v=ei1F0ZbNX3o)

### ConsensFlow

![A person at a board of task cards, handing cards to three terminal windows: a coding robot, a reviewer with a magnifier and a tester with a check mark](https://ngvoicu.dev/images/work/consensflow-800.webp)

**What it is.** A desktop app that runs a team of AI coding agents on your project. You talk to a Chief of Staff, which plans the work and puts tasks on a board. Workers do the tasks, advisors answer questions, reviewers check the work and testers run it, each in its own terminal of Claude Code, Codex, OpenCode, Pi or Devin. It works with your own logins, stores no passwords and needs no API keys. You can make every message between agents wait for your approval.

**My part.** I wrote it. It started in July 2026 as a Claude Code plugin and a Pi extension that let your agent ask a different model for a second opinion. It’s now this desktop app.

**Stack:** Rust, Tauri, xterm.js. Runs on a Mac with Apple silicon (macOS 13.5 or later) and on Windows 10 or 11, 64-bit.

- [consensflow.ngvoicu.dev](https://consensflow.ngvoicu.dev)
- [Download for Mac or Windows](https://github.com/ngvoicu/consensflow/releases)
- [Source on GitHub](https://github.com/ngvoicu/consensflow)

### The providers.dev family

A second family, since November 2026, under its own name: the models behind the agents, as each provider and access method really exposes them, and tools to use them well.

#### providers.dev

![A ledger of model cards fed by four windows; a robot times an hourglass with a stopwatch, and a person with a magnifying glass looks at two pinned notes with a small warning sign between them](https://ngvoicu.dev/images/work/providers-dev-800.webp)

**What it is.** The real context window, maximum output, price and cache lifetime of a model for the way you actually reach it: an API key, a reseller or a subscription login such as Claude Code, Devin or Google Antigravity. Your tools size their conversations and their compaction from these numbers: with too small a window they compact too early, and without the cache’s real lifetime they can’t keep it warm or compact before it goes cold. Each quantity has one value, measured where it can be measured, with every source’s own figure beside it and a warning where they disagree. Every model, provider and entry has its own page, and Provimux and pi-cache-keeper read the same data.

**My part.** I built it, and groundtruth, the tool that does its measuring:

- The subscription logins and other providers the imported catalogue doesn’t list, and corrections to single fields, each with its reason and its source. A release date only from the lab’s own sources.
- The rule that gives each quantity one safe value (input window, maximum output, the short and the long cache lifetime, price): measurements first, then the corrections, every source kept beside it.
- groundtruth, which measures how long prompt caches really live and how large the limits really are, per endpoint, model and route. A subscription login is measured first through the vendor’s own client (Claude Code, Codex CLI, Devin CLI, Muse Code), driven as its user drives it.
- Each provider’s model list as the vendor itself gives it to a signed-in account, read every day.
- The site and the API: a page for every model, provider and entry, and a read-only JSON API with no key, one contract every object keeps, an OpenAPI document and versions.

**Stack:** TypeScript and Astro on Cloudflare Workers. groundtruth is TypeScript on Node, with no runtime dependencies, and Python to drive the vendors’ clients.

**Try the API:**

```
curl https://providers.dev/api/v1/models/anthropic/claude-opus-5-5
```

- [providers.dev](https://providers.dev)
- [The API](https://providers.dev/docs/api/)
- [Source on GitHub](https://github.com/ngvoicu/providers.dev)
- [groundtruth on GitHub](https://github.com/ngvoicu/groundtruth)

#### Provimux

![Three robot terminals and a person at a laptop, each holding the same small golden key, send lines into one stone archway with a key in its lock; lines run on to six windows holding keys and badges, and a small tag flies back from the second](https://ngvoicu.dev/images/work/provimux-800.webp)

**What it is.** Every AI account you pay for, behind one key. Provimux is a self-hosted AI gateway: your subscriptions and API keys behind one OpenAI-, Claude- and Gemini-compatible endpoint, for you or your whole team, each person with a client key of their own. The accounts behind a model are tried in the order you set, under names of your own. It keeps the prompt cache in use, so you pay for a prompt once and read it after that, and its Savings page shows what prompt caching was worth. It shows which accounts serve each model, which one answered and why a route is paused. On a team, the accounts behind it are API keys and cloud accounts: a subscription login is for your own use, where its provider allows it.

**My part.** I build it, as my distribution of [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI):

- Pools: one name of your own on every account that can serve a model, made in one save, and the switch “Serve only my names”, which serves only the names you chose.
- The console’s own pages: Accounts (every subscription and key, and whether it works now), Models (every name, the accounts behind it in the order they are tried, their cooldowns) and Savings (what prompt caching was worth, and use by the name a tool sent).
- Who answered: every response names its account (a login or an API key, the provider and host), and the model list names the accounts behind each model, in the order they are tried.
- The right limits: models you declare under an API key report their real context window and output limit, and a name that several accounts serve reports the smallest of their limits.
- Live model lists: Claude, Codex, Meta and Devin logins and your API keys serve what their own accounts list, kept up to date by themselves, so retired models go and new ones appear the day they are listed.
- The prompt cache kept in use: on OpenRouter, cache markers and one upstream per conversation, with each model’s real limits and reasoning levels; on OpenAI keys, the caller’s longer cache lifetime; on a Codex WebSocket, no double bill for a replay.
- Devin: each model’s real output limit, and a quota pause on the one model that ran out, not on the whole login.
- pi-provimux, its Pi extension: each model in Pi’s `/model` says which accounts serve it, other extensions learn which one answered, and Claude models go in Claude’s own format, which brings Anthropic’s 1-hour cache.

**Stack:** Go, with a React and TypeScript console. Runs on macOS, Linux, Windows and FreeBSD, and in Docker.

**Install:**

```
brew install ngvoicu/tap/provimux
brew services start provimux
```

**With Docker, or from a release archive**

- ```
  docker run -d --name provimux -p 8317:8317 \
    -v "$PWD/config.yaml:/CLIProxyAPI/config.yaml" \
    -v "$PWD/auths:/root/.cli-proxy-api" \
    ghcr.io/ngvoicu/provimux:latest
  ```

  For linux/amd64 and linux/arm64. Archives for macOS, Windows, Linux and FreeBSD are on [the releases page](https://github.com/ngvoicu/provimux/releases).

- [provimux.providers.dev](https://provimux.providers.dev)
- [Source on GitHub](https://github.com/ngvoicu/provimux)
- [The console, provimux-ui](https://github.com/ngvoicu/provimux-ui)
- [pi-provimux](https://github.com/ngvoicu/pi-provimux)

#### pi-cache-keeper

![A long scroll from a robot’s terminal runs through a warm, glowing jar of rolled pages, and robot hands fold its end into one short card; an hourglass runs low, a small robot tends the flame under the jar, and a person walks off with a coffee mug](https://ngvoicu.dev/images/work/pi-cache-keeper-800.webp)

**What it is.** A Pi extension that makes a long session cost less. Pi compacts at its last 16k tokens, at full price, and a break lets the prompt cache expire, so your next message pays to write the whole session again. pi-cache-keeper compacts at the right moment instead: from the cache the session already built, which the provider reads at about a tenth of the input price, when the context gets full (on a 984k-token Opus session, about $0.45 instead of $4.20) and just before the cache expires when you step away; and with a cheaper model you pick when the cache is already cold. It can keep the cache warm through a break, and stops once that has cost as much as one cache miss. The summary is written from the full tool output, not 2,000-character excerpts, and the footer shows how long the cache stays warm and the price. What Pi doesn’t know about a model, it fills in from providers.dev.

**My part.** It grew from Nico Bailon’s [pi-cached-compaction](https://github.com/nicobailon/pi-cached-compaction). I added:

- Compacting early, when the context is full: at 90% of the window or a token cap you set, while a summary still fits. Pi waits for its last 16k tokens, too little room for a summary on a big model, so its own compaction runs at full price.
- A fallback model: when the cache is cold, the summary would cost your session model’s full input price, so a model you pick (a cheaper one, or one on a login with quota to spare) writes it instead, and the session goes on with its own model. It steps in too when your model refuses the summary or can no longer hold the conversation.
- Keeping the cache warm through a break, so your next message reads the session instead of paying to write it again: for as long as you choose, until refreshing has cost as much as one cache miss; `/cache-keeper-stop` stops it in every window at once.
- The footer: the countdown and what it means for cost, the cache lifetimes and the tier in use, what the last request asked for, the price, whether a subscription or an API key answered, and what went wrong, fitted to the terminal’s width.
- Model data from providers.dev: one safe value for each model’s input window, output limit, cache lifetimes and prices, measured values first.
- `/cache-keeper-settings`: a menu for every setting, and settings per session over the defaults.

**Stack:** TypeScript, as a Pi extension, with no runtime dependencies. Needs Pi 1.6.0 or newer.

**Install**, then run `/reload` in Pi:

```
pi install npm:pi-cache-keeper
```

- [pi-cache-keeper.providers.dev](https://pi-cache-keeper.providers.dev)
- [Source on GitHub](https://github.com/ngvoicu/pi-cache-keeper)

### Pools for CLIProxyAPI

![Five windows, each holding a key, send lines into one round green pool, and one line runs on to a laptop where a robot works; a person guides the last line into the pool](https://ngvoicu.dev/images/work/cpa-pools-800.webp)

**Deprecated and archived:** no further releases. Pools are now part of [Provimux](https://ngvoicu.dev/work/#provimux), above: a pool there is one name of your own on every account that can serve a model, made on the console’s Models page, and the switch “Serve only my names” takes the place of the plugin’s pools-only view. See [Pools on provimux.providers.dev](https://provimux.providers.dev/#pools). The plugin stays here as the place where pools began.

**What it is.** A plugin for [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI), the open-source proxy that serves your AI subscriptions and API keys as one local API. Every provider names the same model differently, so the same model from different accounts never shares the load. The plugin adds a Pools page to the proxy’s console: pick a model, and every account and key that serves it joins one pool under the model’s plain name. New accounts join on their own, and model lists drop provider labels such as “(Devin)”.

**My part.** I wrote it. It saves pools as the proxy’s own model aliases, so routing stays with the proxy and the pools keep working without the plugin. It was submitted to the CLIProxyAPI plugin store.

**Stack:** Rust, a CLIProxyAPI plugin with a plain JavaScript page. Runs on macOS, Linux and Windows.

- [The article](https://ngvoicu.dev/articles/cliproxyapi-model-pools/)
- [Source on GitHub](https://github.com/ngvoicu/cpa-pools-and-aliases)
