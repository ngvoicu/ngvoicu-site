---
title: "Rust for Java Developers: A Field Guide — Gabriel Voicu"
description: "A field guide to Rust for Java developers: cargo vs Maven, ownership without a GC, axum vs Spring Boot, sqlx vs JDBC and JPA, and a worked service."
canonical: https://ngvoicu.dev/articles/rust-for-java-developers/
author: Gabriel Voicu
published: 2026-10-22
---

# Rust for Java Developers

Why the next decade of software will be built differently, and how to be ready for it.

By Gabriel Voicu, 22 October 2026

From zero to hero: tools, projects, executables, memory, crates, Spring, JDBC, Kafka, cloud.

17 chapters, 4 labs and a printable cheat sheet.

## 0. Why Rust, why now

Before the tools and the code, here's why this is worth your time.

### We never really picked our languages

Look inside almost any company and you'll find a patchwork. The AI team writes Python because that's where the models and libraries live. The core platform is Java because someone started it fifteen years ago and it still works. There's a C++ service nobody wants to touch, a PHP admin panel, a Node backend-for-frontend, and in older banks, COBOL still moves the money.

- **Python** "the AI libraries were there"
- **Java** "the team already knew it"
- **C++** "too risky to rewrite"
- **PHP** "it was the quickest option"
- **Node.js** "the frontend devs could help"
- **COBOL** "nobody left who can move it"

Hardly any of this was a technical decision. We picked languages based on who we could hire, which framework someone knew, which legacy system we couldn't afford to rewrite, and which deadline left no room for anything new. Those were sensible choices, because rewriting is expensive and good developers have always been the scarcest thing in software.

At least, they *were* the scarcest thing.

### The bill we stopped reading

Every one of those choices comes with a running cost, and we've gotten used to paying it.

The biggest cost is **bugs that become security holes**. In big C and C++ codebases, roughly 70% of serious vulnerabilities come from memory-safety mistakes. Both Microsoft and Google's Chromium team have reported that number. Java fixed that decades ago with a garbage collector, but it paid in other ways: a virtual machine in every container, hundreds of megabytes of RAM per service, slow starts, and servers sized for the worst GC pause.

**One service** a runtime, hundreds of MB of RAM, warm-up time, GC headroom

×

**Thousands of services** across the company, every environment

×

**24 h × 365 days** running around the clock

\=

**Hardware · money · electricity** spent on overhead, not on real work

Multiply that by thousands of services running around the clock, and you get a lot of hardware, money and electricity spent on *overhead* instead of *real work*.

70%

of serious security bugs in large C/C++ codebases are memory-safety bugs\
Microsoft, Google Chromium

1,000×

lower memory-safety vulnerability density in Rust than in C/C++ on Android\
Google, Nov 2025

−70%

CPU, and 67% less memory, for Cloudflare's Rust proxy compared with the NGINX-and-Lua service it replaced (language and architecture changes together)\
Cloudflare, September 2022, 1 trillion+ requests/day

\~945 TWh

projected data-centre electricity use by 2030 in the IEA's Base Case, up from 415 TWh in 2024\
IEA, Energy and AI, April 2025

### What changed: writing code is no longer the hard part

AI agents can now write a working service in an afternoon. They're not perfect and they need supervision, but they're good enough that the bottleneck has moved. Typing code is no longer the hard part. The hard part is deciding what to build, how the pieces fit together, and proving the result is correct and safe.

### Your new job: architect, reviewer, operator

That changes your job. The agent does most of the typing. You do the part that was always the hardest: **deciding what the system is**, checking that it stays that way, and keeping it healthy in production.

1. **Web & mobile** clients
2. REST · OpenAPI
3. TRUST BOUNDARY · money moves here · audited
   1. **API gateway** auth · rate limit

   2. **Payments service**
      - api
      - domain
      - storage

      3 crates · domain is pub · storage is pub(crate)

   3. **payments DB** owned by payments only

   4. gRPC

   5. **Ledger** append-only timeout + retry

   6. **ledger DB**
4. publish
5. **Kafka · payment-events** contract: event schema
6. consume
7. **Notifications** email · push

- you design: components, boundaries, contracts, data ownership, failure rules
- the agent writes: the code inside each box

**You draw the boxes and the arrows. The agent fills in the boxes.**

As the **architect**, you decide how the system is cut into pieces and how those pieces talk. These decisions are the hardest to change later, and the ones an agent can't make for you, because they depend on your business, your risks and your people:

- **Components** Which services exist, what each one is responsible for, and what it must never do. One clear job per component.
- **Modules inside them** How a service is split into crates and modules (api, domain, storage), and what's `pub` versus private between them.
- **Contracts** How components interact: a REST API, a gRPC `.proto`, a Kafka event schema. Contracts are promises, and they outlive the code behind them.
- **Data ownership** Which service owns which data. Nobody else writes to the payments table; they ask the payments service.
- **Failure behavior** What happens when a dependency is slow or down: timeouts, retries, idempotency, fallbacks, and what the user sees.
- **Trust boundaries** Where authentication happens, where money moves, what must be encrypted and audited, and who is allowed to call what.

Here's the part that makes Rust special for this role: **your architecture stops being a wiki page and becomes something the compiler enforces.** A module marked private can't be reached into, even by an agent in a hurry. A crate that doesn't list a dependency can't use it. A payment state modeled as an `enum` can't be put into a state that doesn't exist. The agent can write thousands of lines, and it still can't break the boundaries you drew.

- **Architect** Designs components, modules, contracts and data flow. Writes down the rules (and encodes them in types and visibility).
- **Reviewer** Checks each change against those rules. Does it respect the contract? Does it touch data it shouldn't? Do the tests test the right thing? Auth and payment code always gets a human security review.
- **Operator** Watches the system live: metrics, traces, logs, errors, cost and energy. Turns what production teaches into better designs.

### Why Rust, specifically

It also changes which language makes sense.

The idea behind this guide

When people wrote every line by hand, Rust's strict compiler felt like a tax.

When an AI writes the code, that strictness becomes the most valuable thing you have.

1. unchecked code, written in seconds
2. **AI agent** writes fast
3. **rustc**
   - ✗ possible null
   - ✗ data race
   - ✗ use after free
4. only code the compiler can prove safe
5. **Your review** → production

1. **YOU** architect · reviewer operator

2. 1 · design, rules, requirements

3. **AI AGENT** writes the code and the tests

4. 2 · submits code

5. **RUST COMPILER** rejects whole classes of bugs, every build

   ✗ error + exact fix hint → agent retries

6. 3 · only code that compiles

7. **reaches your review**

Safe Rust: valid references, no data races or use-after-free · unused Result: compiler warning

The new development loop. The compiler acts as a tireless, strict reviewer that sits between the agent and you.

Here's why Rust and AI agents work so well together. The agent writes code, and the Rust compiler refuses safe code that could dereference a null, corrupt memory, or let two threads race over the same data. The error message points to the exact line and often suggests the fix, so the agent reads it and tries again. By the time the code reaches you, a whole category of bugs is already gone. In Python or JavaScript, the same mistakes run fine until they fail in production.

### The big players are already moving

1. 2018 **AWS** launches Firecracker, the Rust virtualization layer behind Lambda and Fargate. Rust later spreads into S3, EC2 and CloudFront.
2. 2022 **Cloudflare** replaces its NGINX-and-Lua proxy with Pingora, written in Rust: over a trillion requests a day with about 70% less CPU and 67% less memory than the old service. Cloudflare credits both the more efficient Rust code and a new architecture, including fewer new connections.
3. 2022 **Linux 6.1** ships with Rust support.
4. 2025 **OpenAI** rewrites its Codex coding-agent CLI from TypeScript/Node to Rust, for easier installs, lower memory use and safer sandboxing.
5. 2025 **Google** reports Rust in Android has about 1000× fewer memory-safety bugs per line than C/C++, and its Rust changes are rolled back about 4× less often.
6. 2025 **Linux maintainers** make Rust permanent: "the experiment is done, i.e. Rust is here to stay."
7. 2026 **Microsoft** ships the Azure SDK for Rust as generally available. AWS and Google Cloud already have official Rust SDKs.

Even the AI world, famous for Python, is moving underneath. Hugging Face's tokenizers, Polars, Pydantic's core, and the uv and Ruff tools are all written in Rust. Python stays on top as the friendly interface, but the fast, critical parts increasingly run in Rust.

### AI eats energy. It can also help save it.

AI is hungry. The International Energy Agency's April 2025 *Energy and AI* report estimated that data centres used about 415 TWh of electricity in 2024, around 1.5% of all the electricity in the world, and projected in its Base Case that this would more than double to around 945 TWh by 2030, with AI as the main driver.

But AI can pay some of that back. Most software in production runs on languages that burn far more energy than they need to. In a widely cited study comparing 27 languages on the same tasks, Rust used about the same energy as C, about half of Java, and roughly 75 times less than Python:

Energy used to solve the same benchmark tasks (C = 1.00, lower is better)

C

1.00×

Rust

1.03×

C++

1.34×

Java

1.98×

Go

3.23×

JavaScript

4.45×

PHP

29.30×

Python

75.88×

**Show as table**

| Language | Relative energy |
|---|---|
| C | 1.00 |
| Rust | 1.03 |
| C++ | 1.34 |
| Java | 1.98 |
| Go | 3.23 |
| JavaScript | 4.45 |
| PHP | 29.30 |
| Python | 75.88 |

Source: Pereira et al., "Energy Efficiency across Programming Languages" (2017). These are lab benchmarks, not your production system, but the direction is clear.

\~100× less memory and CPU

From the field

I saw this myself. An application was rewritten from Java to Rust, with the same consumers and the same functionality, and it came out around **100× more efficient in both memory and CPU**.

Why so much more than the 2× in the chart? A benchmark measures only the language. In production you also stop paying for the JVM, the garbage collector's headroom, the framework's startup and reflection, and the oversized containers that all of that requires. Your exact numbers will depend on the workload, but gaps like this are what make the business case.

If agents help us move even part of our existing software to leaner languages, the hardware and energy saved could offset a real share of what AI itself consumes. Cloudflare's move to Pingora shows how large such savings can be at scale, although part of them came from its new architecture and not from the language alone.

### Security: what Rust gives you over Java, specifically

Let's be precise here. Java is already memory-safe, so moving from Java to Rust isn't the huge leap that C++ teams see. You won't get a "1000×" headline against Java. What Rust does is close doors that Java leaves open:

- **No null references** Rust references must be non-null. `Option` represents an absent value. Raw pointers can be null; dereferencing them requires `unsafe` code and the programmer must ensure they are valid.
- **No data races in safe code** Safe Rust's borrowing and `Send`/`Sync` rules prevent data races. Immutable data can be shared between threads; shared mutation needs a safe synchronization strategy. Deadlocks and other logic races remain possible, and `unsafe` code must uphold Rust's rules.
- **No runtime reflection** Rust has no runtime reflection of the Java kind; libraries such as serde generate (de)serialization code at compile time. That does not make injection bugs impossible: [Log4Shell](https://logging.apache.org/security.html#CVE-2021-44228) came from a logging library resolving attacker-controlled JNDI lookups.
- **Smaller attack surface** One small binary, no JVM, a minimal container with very little else to patch.
- **Errors you have to see** Functions returning `Result` make failure explicit, and the compiler warns when a `Result` is unused. You can still discard one on purpose with `let _ = …`, or turn it into a panic with `.unwrap()`, but that choice is visible in the code and in review.
- **Less to run** Fewer resources per service means smaller servers, lower bills and less energy, every hour of every day.

### Where this is heading

Will everything move to Rust? Not tomorrow, and not all of it. Java will be around for a long time, Python will stay the language of AI research, and some legacy systems will probably outlive all of us.

But the reasons we chose other languages are fading one by one. "There aren't enough Rust developers": agents change that. "A rewrite is too expensive": agents change that too. What's left is the result itself: software that's faster, cheaper to run, uses less energy, has fewer bugs and fewer ways to be attacked.

The best time to understand how Rust works is before you need it.

About this guide

**Not a syntax tutorial.** This guide teaches you how the Rust world works: the tools, why they exist, how a project is laid out, how code becomes an executable, how a Rust program runs on the machine, and why it's fast. Every concept is mapped back to something you already know from Java, up to the Spring Boot, JdbcTemplate/JPA, Kafka, AWS and Vault world (chapters 12–14).

- rustup ≈ SDKMAN
- cargo ≈ Maven + Gradle
- crate ≈ JAR
- crates.io ≈ Maven Central
- axum ≈ Spring MVC
- sqlx ≈ JdbcTemplate
- no JVM, no GC

- [New to Rust?](https://ngvoicu.dev/articles/rust-for-java-developers/#big-picture) Start at chapter 1 and do the labs.
- [Want the core idea?](https://ngvoicu.dev/articles/rust-for-java-developers/#memory) Chapter 8: memory without a garbage collector.
- [Building services?](https://ngvoicu.dev/articles/rust-for-java-developers/#spring) Chapters 12–14: Spring, JDBC, a real service.

## 1. The big picture

Before any tooling: understand the one fundamental difference between Java and Rust. Everything else follows from it.

In Java, you compile your code to **bytecode** (`.class` files). Bytecode is not something your CPU understands. It's instructions for an imaginary computer, the **Java Virtual Machine**. When you run your program, the JVM starts up, loads your bytecode, interprets it, watches which parts are "hot", and compiles those to real machine code while the program runs (the JIT compiler). A garbage collector runs alongside, cleaning up objects you no longer use.

In Rust, there is no virtual machine. The compiler turns your source code straight into **native machine code** for a specific CPU and operating system. The output is a regular executable file, just like `ls` or `git`. You run it, the operating system loads it, and the CPU executes your instructions directly. There's no interpreter, no JIT and no garbage collector.

JAVA compile once, needs a JVM everywhere

1. **Hello.java** source
2. javac
3. **Hello.class** bytecode (portable)
4. java
5. **JVM (runtime, \~tens of MB)**
   - Interpreter
   - JIT compiler
   - Garbage coll.
6. **CPU**

RUST compile per target, runs directly

1. **main.rs** source
2. rustc + LLVM
3. (slow, thorough)
4. **hello (executable)** native machine code, \~0.4 MB
5. ./hello (OS loads it, nothing in between)
6. **CPU**

Java puts a runtime between your code and the CPU. Rust does all the hard work at compile time, so nothing sits between your code and the CPU.

Hold onto this picture. It explains almost every "why" in this guide:

| Question | Answer that follows from the picture |
|---|---|
| Why does Rust compile slowly? | The compiler does work the JVM would do at runtime (optimization) *plus* work nobody in Java does (proving memory safety). |
| Why is a Rust program a single file I can just copy? | It's native code. There's no runtime to install, so there's no "requires Java 21" step. |
| Why must I build separately for Mac, Linux, Windows? | Machine code is CPU- and OS-specific. Java's bytecode is portable because the JVM is the thing that differs per platform. |
| Why does Rust start in \~1 ms? | No JVM to boot, no classes to load, no JIT warm-up. |
| Why is the compiler so strict? | Without a GC watching memory at runtime, the compiler must prove at compile time that memory is used correctly (chapter 8). |

Java parallel

The closest thing in the Java world is **GraalVM native-image**: AOT-compile your Java app to a native binary with instant startup. In Rust, that's not an option you turn on. It's the only way things work.

## 2. Setting up your environment

One installer, a handful of tools. Here's what each tool is for and why you need it.

### The cast of characters

In Java you assemble a toolchain from separate projects: a JDK from some vendor, SDKMAN to switch JDKs, Maven or Gradle to build, Checkstyle/Spotless for formatting, SpotBugs or Sonar for linting, IntelliJ for code intelligence. Rust ships an **official, integrated toolchain** where every piece comes from the same project and works together out of the box.

1. **rustup** installs & switches toolchains · Java: SDKMAN
2. a toolchain, e.g. stable-aarch64-apple-darwin (Java: "a JDK")
   - **cargo** build, deps, test, run, publish Java: Maven / Gradle
   - **rustc** the compiler (cargo calls it) Java: javac
   - **rust-std** standard library, precompiled Java: java.base / JDK classes
   - **clippy** linter, 700+ checks Java: SpotBugs / Sonar / PMD
   - **rustfmt** the one official formatter Java: Spotless / google-java-format
   - **rustdoc + rust-docs** doc generator + offline docs Java: javadoc

- **rust-analyzer (in your editor)** autocomplete, go-to-def, inline types, errors Java: IntelliJ's built-in code intelligence
- **crates.io (online registry)** where cargo downloads libraries from Java: Maven Central

rustup installs a toolchain; a toolchain bundles everything. cargo is the tool you'll type 95% of the time.

#### Why each one exists

| Tool | Why you need it |
|---|---|
| **rustup** | Rust releases a new stable version **every 6 weeks**. rustup keeps you updated (`rustup update`), lets you install several versions side by side (`stable`, `beta`, `nightly`, or pinned like `1.90.0`), and adds **compile targets** for other platforms. You don't need it to compile code, but you need it to manage the compiler. |
| **cargo** | Your everything-tool: creates projects, downloads dependencies, calls `rustc` with the right flags, runs tests, builds docs, publishes libraries. You almost never call `rustc` directly, the same way you rarely call `javac` by hand. |
| **rustc** | The compiler itself. It uses **LLVM** (the same backend as Clang/Swift) to produce optimized machine code. |
| **clippy** | Catches non-idiomatic or suspicious code and explains the better way. For a beginner it's like a senior reviewer sitting next to you. Run it constantly. |
| **rustfmt** | One standard style for the whole ecosystem, so there are no style debates. Every Rust codebase looks the same. |
| **rust-analyzer** | The language server that powers your IDE. Without it, an editor is just a text editor. |
| **A C linker** | rustc produces object files, but the *system linker* glues them into an executable. On macOS that comes from Xcode Command Line Tools. This is the one piece Rust doesn't ship itself. |

### Install it (macOS)

1. **Install the linker** (skip if you already have Xcode or its CLI tools, e.g. because you use git or Homebrew):

   ```
   xcode-select --install
   ```

2. **Install rustup**, which installs everything else. This is the official installer from [rustup.rs](https://rustup.rs); accept the default option:

   ```
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

   It puts tools in `~/.cargo/bin` and toolchains in `~/.rustup`, and adds `~/.cargo/bin` to your PATH. Nothing is installed system-wide and no sudo is needed. Open a new terminal afterwards.

3. **Verify:**

   ```
   rustc --version     # rustc 1.9x.0 (...)
   cargo --version
   rustup show         # which toolchain is active, and which targets
   ```

4. **Set up the editor.** Two good choices:
   - **RustRover** (JetBrains): feels like home if you live in IntelliJ. Check the license terms for commercial/work use with your team.
   - **VS Code + the "rust-analyzer" extension**: free and the most widely used. Add "CodeLLDB" if you want a debugger.

Java parallel

`~/.cargo/registry` is your `~/.m2/repository`: the local cache of downloaded libraries. `~/.cargo/bin` is where globally installed Rust CLI tools go (`cargo install ripgrep` puts a `rg` binary there).

#### Pinning a version per project

Like a `.sdkmanrc` or Gradle toolchains, put a `rust-toolchain.toml` in the project root and rustup automatically switches to (and downloads) that version when you're in that folder:

*rust-toolchain.toml*

```
[toolchain]
channel = "1.90.0"
components = ["clippy", "rustfmt"]
```

Good to know

**Editions vs versions.** You'll see `edition = "2024"` in projects. An edition (2015, 2018, 2021, 2024) is a set of language rules that every new compiler supports, so you get new compilers without breaking old code. Crates on different editions link together fine. It's like Java's `--release` flag, except old editions never stop compiling.

## 3. Anatomy of a project

Create one and look inside. A Rust project is much smaller than a Maven one.

```
cargo new hello_rust        # an application (binary)
cargo new --lib my_utils     # a library
cd hello_rust
```

`cargo new` also runs `git init` and writes a `.gitignore` containing just `/target`. Here's everything it creates, plus what appears after the first build:

Rust (cargo)

```
hello_rust/
├── Cargo.toml        # project manifest
├── Cargo.lock        # exact resolved versions (after 1st build)
├── .gitignore        # "/target"
├── src/
│   └── main.rs       # entry point
└── target/           # all build output (git-ignored)
    ├── debug/
    │   └── hello_rust   # ← your executable
    └── release/
```

Java (Maven)

```
hello-java/
├── pom.xml
│
├── .gitignore
├── src/
│   ├── main/java/com/acme/App.java
│   ├── main/resources/
│   └── test/java/com/acme/AppTest.java
└── target/
    ├── classes/
    └── hello-java-1.0.jar
```

### Cargo.toml: your pom.xml

The manifest is written in **TOML**, a simple config format (think `.properties` with sections). Compare:

Cargo.toml

```
[package]
name = "hello_rust"
version = "0.1.0"
edition = "2024"

[dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }

[dev-dependencies]   # test scope
mockall = "0.15"
```

pom.xml

```
<groupId>com.acme</groupId>
<artifactId>hello-java</artifactId>
<version>0.1.0</version>
<properties><maven.compiler.release>21...
<dependencies>
  <dependency>
    <groupId>com.fasterxml.jackson.core...
    <artifactId>jackson-databind</...
    <version>2.17.0</version>
  </dependency>
  ... <scope>test</scope> ...
```

There's no `groupId`. Crate names on crates.io are a single global namespace (first come, first served), so `serde` is just `serde`.

### Cargo.lock: the exact versions

`Cargo.toml` says "serde version 1-something". `Cargo.lock` records exactly which version was picked (e.g. `1.0.219`) for every dependency, including transitive ones, with checksums. It's generated automatically and you never edit it by hand. **Commit it to git**, so every developer and every CI build uses identical versions. Java has no built-in equivalent; it's like Gradle dependency locking or a fully pinned BOM.

### src/main.rs: the entry point

*src/main.rs*

```
fn main() {
    println!("Hello, world!");
}
```

That's the whole program. There's no class, no `public static void`, no `String[] args` (you get arguments through `std::env::args()`). By convention, cargo knows that `src/main.rs` means "build an executable" and `src/lib.rs` means "build a library". There's no XML telling it where sources are. **Convention over configuration**, like Maven's `src/main/java`, but stricter.

### target/: build output

Same idea as Maven's `target/`: throwaway, git-ignored, can grow to gigabytes because it caches compiled dependencies. `cargo clean` wipes it.

Lab · 5 minutes

Run `cargo new hello_rust && cd hello_rust && cargo run`. Then run `ls -lh target/debug/` and find your executable. Run it directly with `./target/debug/hello_rust`, without cargo. That file *is* your program.

## 4. The daily dev loop

The cargo commands you'll actually use, and the order you'll use them in.

| You want to… | Rust | Java (Maven-ish) |
|---|---|---|
| Check it compiles (fast, no output binary) | `cargo check` | `mvn compile` |
| Build (debug) | `cargo build` | `mvn package` |
| Build + run | `cargo run` | `mvn exec:java` / `spring-boot:run` |
| Pass args to your program | `cargo run -- --port 8080` | `-Dexec.args="..."` |
| Run tests | `cargo test` | `mvn test` |
| Lint | `cargo clippy` | SpotBugs / Sonar |
| Format | `cargo fmt` | `mvn spotless:apply` |
| Add a dependency | `cargo add serde --features derive` | edit pom.xml |
| See dependency tree | `cargo tree` | `mvn dependency:tree` |
| Update deps (within semver) | `cargo update` | `versions:use-latest-…` |
| Generate & open docs (incl. all deps!) | `cargo doc --open` | `mvn javadoc:javadoc` |
| Optimized production build | `cargo build --release` | `mvn package -P prod` |
| Install a CLI tool globally | `cargo install <name>` | no real equivalent |

1. **edit code** rust-analyzer live
2. **cargo check** seconds · most often
3. compiler error? fix & re-check
4. **cargo clippy** idiomatic? safe?
5. **cargo test** correct?
6. **cargo run** try it for real

repeat · before committing: cargo fmt && cargo clippy && cargo test

The inner loop. `cargo check` is your best friend: it runs every analysis (types, borrow checker) but skips code generation, so it's much faster than a full build.

Pro tip

Want hot-reload-like feedback? Install **bacon** (`cargo install --locked bacon`) and run `bacon` in a side terminal. It re-runs check/clippy/test every time you save. It's the closest thing to IntelliJ's continuous compilation.

### Reading the compiler is part of the job

Java devs often skim compiler errors. In Rust, **the compiler is a teacher**. Its errors show the exact spot, explain what's wrong, and often include the fix:

```
error[E0382]: borrow of moved value: `name`
 --> src/main.rs:4:20
  |
2 |     let name = String::from("Gabriel");
  |         ---- move occurs because `name` has type `String`, which does not implement the `Copy` trait
3 |     let other = name;
  |                 ---- value moved here
4 |     println!("{}", name);
  |                    ^^^^ value borrowed here after move
  |
help: consider cloning the value if the performance cost is acceptable
  |
3 |     let other = name.clone();
  |                     ++++++++
```

Every error has a code; `rustc --explain E0382` prints a full article with examples. Expect to spend your first weeks "fighting the borrow checker". That's normal, and it's the compiler catching bugs that would have been runtime problems in Java.

### Tests live next to the code

Unlike Java's separate `src/test/java` tree, Rust unit tests usually sit **in the same file** as the code, in a module that only compiles during `cargo test`. That's why `cargo new --lib` generates this:

*src/lib.rs*

```
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]          // ← compiled ONLY for `cargo test` (never in your binary)
mod tests {
    use super::*;      // ← tests can see private functions too

    #[test]             // ← like JUnit's @Test
    fn it_works() {
        assert_eq!(add(2, 2), 4);
    }
}
```

| Test type | Where | Java equivalent |
|---|---|---|
| Unit tests | `#[cfg(test)] mod tests` inside each `.rs` file | JUnit in `src/test/java` |
| Integration tests | `tests/*.rs` at project root; they see only your public API | Failsafe `*IT.java` |
| Doc tests | Code examples inside `///` doc comments are compiled and run | none; Javadoc examples can go stale |
| Benchmarks | `benches/` with the `criterion` crate | JMH |

## 5. Compiling & building executables

What happens when you hit build, the difference between debug and release, and how to ship.

### Inside `cargo build`

rustc front-end: understand & PROVE (this is where your errors come from)

1. **.rs files** your crate
2. **Parse** + expand macros
3. **Type check** traits, generics
4. **Borrow check** memory safety proof

cargo check stops here: all the errors, none of the slow part

(this is why it's so much faster than cargo build)

LLVM back-end: optimize & emit

1. **LLVM IR** + optimize
2. **Machine** code (.o)

debug: minimal optimization

release: full optimization,

inlining, vectorization

1. **your .o + deps' .rlib + std** all pre-compiled pieces
2. **linker**
3. **target/…/hello_rust** one self-contained executable

The compile pipeline. Dependencies are compiled once and cached in `target/`; later builds only recompile what changed (incremental compilation).

A key difference from Java: **dependencies are compiled from source**. Maven downloads ready-made `.jar` files. Cargo downloads source code from crates.io and compiles it on your machine with your settings, so the optimizer can inline across library boundaries. This is why the first build of a project with 200 dependencies takes minutes, while later builds are fast because the compiled deps are cached.

### Debug vs release

Cargo has build **profiles**. Real numbers for the hello-world above, built on Linux x86-64:

|  | `cargo build` (dev profile) | `cargo build --release` |
|---|---|---|
| Output | `target/debug/hello_rust` | `target/release/hello_rust` |
| Optimization | Minimal: fast to compile, slow to run | Full (`opt-level = 3`): slow to compile, fast to run |
| Debug info | Yes (for debuggers) | No |
| Integer overflow | Panics (crashes loudly) | Wraps silently (like Java) |
| Size (hello world) | 4.2 MB | 435 KB |
| Speed difference | Release is often **10–100× faster** for heavy code. Never benchmark a debug build! | Release is often **10–100× faster** for heavy code. Never benchmark a debug build! |

Tune profiles in `Cargo.toml`, similar to Maven profiles but for compiler settings:

*Cargo.toml*

```
[profile.release]
lto = true           # link-time optimization across all crates
codegen-units = 1     # slower build, better optimization
strip = true         # remove symbols → smaller binary
panic = "abort"      # don't unwind on panic → smaller, slightly faster
```

### Shipping your executable

The release binary is your deployable. Copy it to a machine with the same OS/CPU and run it. There's no JRE to install, no `-Xmx` to tune, no classpath. A few things to know:

#### Targets: one binary per platform

Every platform has a **target triple**: `arch-vendor-os(-abi)`. Your Apple-silicon Mac is `aarch64-apple-darwin`. A typical Linux server is `x86_64-unknown-linux-gnu`.

```
rustup target list --installed
rustup target add x86_64-unknown-linux-musl              # add a target (downloads its std)
cargo build --release --target x86_64-unknown-linux-musl  # → target/x86_64-unknown-linux-musl/release/
```

Cross-compiling Mac → Linux also needs a Linux-capable linker. The easy paths are `cargo-zigbuild` or `cross` (which runs the build in Docker), or simply building inside a Docker container, which is what most CI pipelines do.

gnu vs musl

`-linux-gnu` binaries link dynamically to the system's C library (glibc), so they need a compatible Linux. `-linux-musl` binaries are **fully static**: they run on any Linux, even an empty container.

#### Docker: the payoff

Rust: multi-stage, tiny image

*Dockerfile*

```
FROM rust:1 AS build
WORKDIR /app
COPY . .
RUN cargo build --release

FROM gcr.io/distroless/cc-debian12
COPY --from=build /app/target/release/myapp /
USER nonroot
ENTRYPOINT ["/myapp"]
# image: ~25–40 MB total. With musl + FROM scratch:
# just the binary (a few MB)
```

Java: needs a runtime in the image

*Dockerfile*

```
FROM maven:3-eclipse-temurin-21 AS build
...
RUN mvn -q package

FROM eclipse-temurin:21-jre
COPY --from=build /app/target/app.jar /
ENTRYPOINT ["java","-jar","/app.jar"]
# image: ~200+ MB (JRE + OS + jar)
# memory at idle: often 100s of MB
```

If your binary links extra C libraries (for example, the Kafka client in [chapter 14](https://ngvoicu.dev/articles/rust-for-java-developers/#service) needs zlib), use a slim Debian image such as `debian:bookworm-slim` as the runtime stage instead, built from the matching `rust:1-bookworm` image so the glibc versions match.

Lab · 10 minutes

In your hello project: run `cargo build` and `cargo build --release`, compare `ls -lh target/*/hello_rust`, then run `time ./target/release/hello_rust` (it should take about 1 ms). Add the `[profile.release]` block above and rebuild to see the binary shrink. Sizes depend on the platform. The table above was measured on Linux x86-64. On macOS, Cargo keeps debug information outside the executable by default (`split-debuginfo = "unpacked"`), so the gap is much smaller there: in one check on Apple silicon with rustc 1.99.0, a debug hello world was about 475 KB, a release build about 435 KB, and about 302 KB with the `[profile.release]` block above.

## 6. How code is organized

Workspace → package → crate → module → item. Four words that confuse every newcomer, explained with Java equivalents.

WORKSPACE (optional) several packages, one Cargo.lock, one target/

PACKAGE = a folder with a Cargo.toml

- **CRATE (binary)** root: src/main.rs → executable
  - **module cli**
    - **module args** fn parse() struct Args
  - **fn main()** items: fn, struct, enum, trait, impl, const…
- **CRATE (library)** root: src/lib.rs → reusable code
  - **module payments** pub struct Payment pub fn validate() fn helper() ← private
  - **module storage**
    - **module postgres** pub struct Repo

JAVA EQUIVALENT

- **Workspace ≈ multi-module build** parent pom / settings.gradle
- **Package ≈ a Maven module** one pom.xml (not a Java "package"!)
- **Crate ≈ a JAR** the unit of compilation & sharing
- **Module ≈ a Java package** namespace + visibility boundary
- **Item ≈ class / method / field** but functions can live outside types

The nesting. Watch out: a Rust **package** is like a Maven *module*, while a Rust **module** is like a Java *package*. The words are swapped.

### Crate: the most important word

A **crate** is what the compiler compiles in one go. It always has a **root file**: `src/main.rs` for an executable (binary crate) or `src/lib.rs` for a library (library crate). When people say "crate" in conversation, they usually mean a library you can depend on, like "the serde crate".

A package can contain **one library crate and any number of binary crates**. A very common pattern is to put all logic in `lib.rs` (testable, reusable) and keep `main.rs` thin: parse args, call into the lib. Extra executables go in `src/bin/`:

```
my_service/
├── Cargo.toml
└── src/
    ├── lib.rs             # library crate "my_service": all the real logic
    ├── main.rs            # binary "my_service": thin, calls the lib
    └── bin/
        └── migrate.rs     # second binary "migrate" → cargo run --bin migrate
```

### Modules: explicit, not folder-magic

Here's the part that surprises Java developers most. In Java, a file at `com/acme/payments/Payment.java` automatically belongs to package `com.acme.payments`. In Rust, **a file is ignored until a parent module declares it** with `mod`. The module tree starts at the crate root and is built explicitly:

Files

```
src/
├── lib.rs
├── payments.rs
└── storage/
    ├── mod.rs        # or: src/storage.rs
    └── postgres.rs
```

Declarations that wire them

```
// src/lib.rs (crate root)
pub mod payments;   // loads payments.rs
pub mod storage;    // loads storage/mod.rs

// src/storage/mod.rs
pub mod postgres;   // loads storage/postgres.rs
```

Then you refer to things by path, the way you'd use a fully-qualified Java name, and `use` works like `import`:

```
use crate::storage::postgres::Repo;   // crate:: = "from the root of THIS crate"
use serde::Deserialize;              // from an external crate (a dependency)
use std::collections::HashMap;       // from the standard library (like java.util)
```

Classic beginner trap

"I created `src/utils.rs` but the compiler says it doesn't exist." You forgot `mod utils;` in `main.rs` or `lib.rs`. No declaration means the file isn't part of the crate.

### Visibility: private by default

| Rust | Visible to | Closest Java |
|---|---|---|
| *(nothing)* | Current module and its children | private / package-private |
| `pub(super)` | Parent module | (no equivalent) |
| `pub(crate)` | Anywhere in this crate, but not to users of your library | package-private across the whole JAR (or a non-exported JPMS package) |
| `pub` | Everyone, including other crates | public |

Struct fields are private by default too. A `pub struct` with private fields is Rust's version of encapsulation: outsiders must use your constructor and methods.

### Try it: who can see this function?

Pick a visibility for `calc_fee`, defined in module `payments::fees`, and watch which parts of the code can call it.

```
// src/payments/fees.rs
fn calc_fee(amount: Decimal) -> Decimal { ... }
```

YOUR CRATE (my_service)

- **crate root** src/lib.rs

  *✗*

- **mod payments** parent

  *✗*

- **mod storage** sibling module

  *✗*

- **mod api** sibling module

  *✗*

- **mod fees ★** calc_fee lives here

  *✓*

- **mod tests** child of fees

  *✓*

ANOTHER CRATE

- **other_crate** depends on your library

  *✗*

The diagram shows the default. What each choice means:

**`(nothing)`**

**Private (the default).** Visible in `fees`, where it is defined, and in its child modules, such as `fees::tests`. Not even the parent `payments` can call it.

Java: closest to `private`, except child modules (like your tests) can also see it.

**`pub(super)`**

**pub(super).** Also visible to the parent module, `payments`. Handy for helpers that the parent uses but nobody else should.

Java: no direct equivalent.

**`pub(crate)`**

**pub(crate).** Visible anywhere inside your crate, but invisible to anyone who uses your library. The most common choice for internal code.

Java: like package-private, but across the whole JAR (or a non-exported JPMS package).

**`pub`**

**pub.** Visible everywhere, including other crates, as long as every module on the path is also `pub` (here: `pub mod payments` and `pub mod fees`). Now it is part of your public API.

Java: `public` (in an exported package).

### Workspaces: multi-module projects

For a larger system with several crates, like a Maven multi-module build, make a workspace. All members share one `Cargo.lock` (consistent versions) and one `target/` (shared compile cache):

```
platform/
├── Cargo.toml          # [workspace]
├── Cargo.lock
├── crates/
│   ├── domain/         # lib
│   ├── persistence/    # lib, depends on domain
│   └── api-server/     # bin, depends on both
└── target/
```

*platform/Cargo.toml*

```
[workspace]
members = ["crates/*"]
resolver = "3"

[workspace.dependencies]  # like <dependencyManagement>
serde = "1"
tokio = { version = "1", features = ["full"] }
```

A member then writes `serde = { workspace = true }` and depends on a sibling with `domain = { path = "../domain" }`.

## 7. Crates & the ecosystem

How dependencies work, where they come from, and which crates replace the Java libraries you know.

### From Cargo.toml to compiled dependency

1. **Cargo.toml** serde = "1" "any 1.x ≥ 1.0"
2. **crates.io index** resolve newest compatible versions
3. **Cargo.lock** serde 1.0.219 + checksum, pinned
4. **\~/.cargo/registry** download source (like \~/.m2)
5. **target/** compiled .rlib reused next build

Next build: Cargo.lock exists, so the exact same versions are used. cargo update re-resolves on purpose.

Unlike Maven, two different major versions of one crate can coexist in a build, so there's no classpath conflict.

Dependency flow. All of it happens automatically on `cargo build`.

### Version requirements (semver)

| You write | Means |
|---|---|
| `"1.2.3"` or `"^1.2.3"` | ≥ 1.2.3 and \< 2.0.0 (compatible updates allowed). This is the default. |
| `"0.4.1"` | ≥ 0.4.1 and \< 0.5.0. Before 1.0, the *minor* number is the breaking one. |
| `"~1.2.3"` | ≥ 1.2.3 and \< 1.3.0 |
| `"=1.2.3"` | exactly 1.2.3 (rarely needed; the lock file already pins) |

### Features: optional parts of a crate

Crates can have **features**: optional functionality you switch on, which is compiled only if you ask for it. It's like choosing between `spring-boot-starter-*` modules, but inside a single dependency. For example, `serde = { version = "1", features = ["derive"] }` turns on the ability to auto-generate (de)serialization code. If you get "cannot find derive macro", you probably forgot a feature.

### Macros: Rust's Lombok and annotation processors

You'll see `#[derive(Debug, Clone, Serialize)]` above structs. Derive macros **generate code at compile time**, much like Lombok's `@Data` or an annotation processor. Function-like macros end in `!` (`println!`, `vec!`) and also expand at compile time, with no runtime reflection. Rust's standard library offers **limited runtime type information** through `Any` and `TypeId`, rather than Java-style inspection of fields and annotations. Libraries such as serde use derive macros to generate implementations at compile time; traits and explicit composition cover many other framework tasks.

### The Java → Rust library map

| Need | Java | Rust crate(s) |
|---|---|---|
| JSON / serialization | Jackson, Gson | **serde** + serde_json |
| Async runtime / event loop | Netty, virtual threads | **tokio** |
| Web framework / REST | Spring Web, Javalin | **axum**, actix-web |
| HTTP client | java.net.http, OkHttp | **reqwest** |
| SQL database | JDBC, jOOQ / JPA | **sqlx** (SQL checked at compile time), diesel, SeaORM |
| Logging / tracing | SLF4J + Logback, OpenTelemetry | **tracing** + tracing-subscriber |
| Error handling | exception hierarchy | **thiserror** (libraries), **anyhow** (apps) |
| CLI argument parsing | picocli | **clap** |
| Parallel data processing | parallel streams, ForkJoin | **rayon** |
| gRPC / Protobuf | grpc-java | **tonic** + prost |
| Configuration | Spring @ConfigurationProperties | **config**, figment |
| Testing / mocking | JUnit, Mockito | built-in `#[test]`, mockall, proptest |
| Date/time | java.time | **chrono**, jiff, time |
| Crypto / TLS | JCA, BouncyCastle | **rustls**, ring / aws-lc-rs, RustCrypto |

This is the short version. [Chapter 12](https://ngvoicu.dev/articles/rust-for-java-developers/#spring) covers frameworks, messaging, cloud and secrets in depth, and [chapter 13](https://ngvoicu.dev/articles/rust-for-java-developers/#data) covers databases (JDBC, JdbcTemplate, JPA, drivers including Oracle).

Discover crates on [crates.io](https://crates.io) and read docs for *any* published version on [docs.rs](https://docs.rs). Docs are auto-generated for every crate, which is one of the ecosystem's best features.

Supply-chain hygiene (important in fintech)

Rust projects often pull in 100–300 transitive crates. Treat them like Maven deps under your security policy:

- `cargo install cargo-audit`, then `cargo audit` checks `Cargo.lock` against the RustSec vulnerability database (like OWASP dependency-check).
- `cargo-deny` enforces allowed licenses, banned crates and trusted sources in CI.
- Build with `cargo build --locked` in CI so the build fails if `Cargo.lock` would change.
- Prefer widely used, maintained crates and check download counts and recent releases on crates.io.

## 8. How Rust runs: memory without a garbage collector

This is the heart of Rust. If you understand this chapter, the compiler's strictness stops feeling arbitrary.

### First: what's actually running?

A running Java service

- **Your code (bytecode → JIT'd machine code)**
- **Frameworks: proxies, reflection, classpath scanning**
- **GC threads**
- **JIT compiler threads**
- **JVM: class loader, interpreter, heap manager**
- **Operating system + CPU**

A running Rust service

- **Your code + libraries, already machine code** (memory freed at exact, compiler-chosen points)
- **tiny std runtime setup + libc (+ tokio, if async)**
- **Operating system + CPU**

Everything in blue on the left is work the Rust compiler did ahead of time, or doesn't need at all.

Runtime layers. Rust's "runtime" is about as small as C's: set up the stack, call `main`, clean up on exit.

### Stack and heap in 60 seconds

Both languages use the same two memory areas:

- **Stack**: fast, automatic, fixed-size slots for each function call's local variables. When a function returns, its stack frame is gone instantly.
- **Heap**: a big pool for data whose size or lifetime isn't known up front (a growing list, a string read from a file). Someone must decide *when to free* each heap allocation.

Who frees heap memory is the core design question of a language:

| Approach | Used by | Cost |
|---|---|---|
| Programmer calls `free()` manually | C, C++ (old style) | Fast, but use-after-free, double free and leaks cause crashes and security holes. |
| Garbage collector finds unreachable objects at runtime | Java, Go, C# | Safe and easy, but uses extra memory and CPU, and pause times are unpredictable. |
| **Compiler inserts the free at exactly the right spot, proven safe** | **Rust** | Fast *and* safe. The cost is paid by you, at compile time, by following the rules below. |

### The ownership rules

**1.** Every value has exactly **one owner** (a variable, a struct field, a collection slot).

**2.** When the owner goes **out of scope**, the value is **dropped** (freed) immediately.

**3.** Ownership can be **moved** to a new owner. The old one can't be used anymore.

Compare what happens in each language when you "copy" a variable holding a string:

JAVA

- String a = "Gabriel";
- String b = a;

- **STACK** a · b
- **HEAP** "Gabriel"

Two references, one object. Who frees it?

Nobody knows statically, so the GC must scan

at runtime to find out when no reference is left.

RUST

- let a = String::from("Gabriel");
- let b = a; // MOVE

- **STACK** a (moved, unusable) · b (owner)
- **HEAP** "Gabriel"

Exactly one owner, known at compile time.

When b goes out of scope, the compiler inserts

the free right there. No GC needed. Using a = compile error.

Move semantics. This is exactly the `E0382` error from chapter 4. Want two independent copies? Call `.clone()` explicitly. Small types like integers are simply copied (they're `Copy`).

### Borrowing: using without owning

Moving everything around would be painful, so you can **borrow** a value with a reference (`&`). It's like handing someone a pointer while you keep ownership. The compiler enforces one rule, the same idea as a `ReadWriteLock` but checked at compile time with zero runtime cost:

EITHER many readers &T

- &data
- &data
- &data

1. **data**

nobody can modify while readers exist

OR

exactly ONE writer &mut T

- &mut data

1. **data**

no one else may even read meanwhile

The borrowing rule. In safe Rust it rules out whole classes of bugs: `ConcurrentModificationException`, data races, and iterator invalidation.

And one more guarantee: **a reference can never outlive the thing it points to**. The compiler tracks this with **lifetimes**. Most of the time it infers them silently. Occasionally you'll annotate one (`'a`) to explain a relationship the compiler can't guess. That's an advanced topic; for now, just know what the word means.

*the same rules, in code*

```
fn total(items: &Vec<u64>) -> u64 { items.iter().sum() }   // borrows: reads only
fn add_fee(items: &mut Vec<u64>) { items.push(150); }       // borrows mutably
fn archive(items: Vec<u64>) { /* takes ownership */ }      // freed when this fn ends

fn main() {
    let mut amounts = vec![1000, 2500];   // main owns the Vec
    add_fee(&mut amounts);                // lend it for writing
    println!("{}", total(&amounts));    // lend it for reading
    archive(amounts);                      // give it away (move)
    // total(&amounts);   ← compile error: amounts was moved
}
```

### Watch it happen: step through a real program

Click **Next** to see what happens in memory, line by line. This exact program compiles and prints "Gabriel" twice; un-commenting line 4 produces the error shown in step 3.

```
fn main() {
    let a = String::from("Gabriel");
    let b = a;              // move
    // println!("{a}");     // ✗ E0382 if uncommented
    let r = &b;             // borrow
    println!("{r}");
    consume(b);             // move into function
}

fn consume(s: String) {
    println!("{s}");
}                           // s dropped here
```

The diagram shows step 1. What happens at each step:

1. `String::from` puts the 7 bytes of "Gabriel" on the **heap**. The variable `a` lives on the **stack**: a pointer, a length and a capacity. `a` is the owner.
2. `let b = a;` copies the 24 bytes on the stack. The text on the heap is **not** copied. Ownership **moves** to `b`, and `a` becomes unusable. Still exactly one owner.
3. Un-comment this line and the build stops with **E0382**. In Java it would compile, with two references to one object. Rust refuses, because two owners would mean two frees.
4. `&b` creates a **borrow**. `r` points to `b` and owns nothing. While `r` is in use, nobody may move or change `b`.
5. This is the last use of `r`, so the borrow **ends right after this line**. The compiler tracks exactly where every borrow starts and stops.
6. `consume(b)` moves ownership into the function. A new stack frame appears and its parameter `s` is now the owner. `b` can no longer be used in `main`.
7. `consume` ends, so `s` goes out of scope. The compiler inserted the **free right here**: the heap memory is released immediately. No garbage collector, no waiting.
8. `main` ends. `a` and `b` were moved away, so there is nothing left to free and no double free. Every allocation was freed **exactly once**, decided at compile time.

Java parallel: drop = automatic try-with-resources

When a value is dropped, its `Drop` implementation runs at that exact moment. Files close, sockets close, locks unlock, DB connections return to the pool. In Java you need `try (var f = ...)` and must remember to use it. In Rust it happens for **every** value, automatically and deterministically. This pattern is called RAII.

Escape hatches exist

Sometimes you really need shared ownership, like a graph or a cache shared between threads. Rust provides `Rc<T>` (reference-counted) and `Arc<T>` (atomic reference-counted, thread-safe). These are opt-in, small "GC-like" tools that you use only where needed. There's also `unsafe` for low-level code the compiler can't verify, which is rarely needed in application code.

## 9. Why Rust is efficient

It's not magic, and Java's JIT is excellent. Rust wins on memory, startup, and predictability, for concrete reasons.

### Reason 1: data is laid out compactly

In Java, almost everything is an object on the heap, every object carries a header, and collections hold *pointers* to objects scattered around memory. Rust stores values **inline** by default:

Java: ArrayList\<Point\> (record Point(int x, int y))

1. **ArrayList obj**

2. **Object\[\]**

3. **header** x=1 y=2

   ⚠ cache miss

4. **header** x=3 y=4

   ⚠ cache miss

5. **header** x=5 y=6

   ⚠ cache miss

each Point: 12–16 B header + 8 B data

→ 24 B, plus a 4–8 B pointer in the array

scattered in heap → cache misses

Rust: Vec\<Point\> (struct Point { x: i32, y: i32 })

1. **Vec (stack)** ptr · len · cap

2. **x=1 y=2 · x=3 y=4 · x=5 y=6**

   ✓ sequential: prefetched, cache-friendly

each Point: exactly 8 bytes, no header

one contiguous block → CPU cache & SIMD friendly

For 1 million points: Rust ≈ 8 MB, one allocation · Java ≈ 28–32 MB, \~1 million allocations for the GC to track

Memory layout: the highlighted box is what the CPU is reading. Java hops from pointer to object to pointer; Rust sweeps one block. Java's Project Valhalla (value classes) aims to close this gap, and Rust has had it from day one.

### Reason 2: no GC, so less memory and no pauses

A garbage collector needs **headroom**: Java heaps commonly run with 2–3× more memory than the live data so the GC can work efficiently, plus background CPU to trace and compact. Rust frees each value the moment its owner goes away, so memory use tracks live data closely and there are **no stop-the-world pauses**. Latency is predictable: p99 looks like p50. That matters for payment APIs with strict SLAs.

### Reason 3: zero-cost abstractions

Rust's motto: *what you don't use, you don't pay for; and what you do use, you couldn't hand-code any better.* An iterator chain like `items.iter().filter(...).map(...).sum()` compiles to the same tight loop you'd write by hand. There's no lambda objects, no boxing, no virtual call per element.

### Reason 4: generics are compiled per type (monomorphization)

Java: type erasure

`List<Integer>` becomes `List<Object>` at runtime. Every int is **boxed** into an `Integer` object, and calls go through interfaces. The JIT can often optimize this, but only after warm-up and only sometimes.

Rust: monomorphization

`Vec<i32>` and `Vec<String>` become two separate, specialized versions of the code at compile time. No boxing, and calls are direct and inlinable. The cost: bigger binaries and longer compiles. (`dyn Trait` gives you Java-style dynamic dispatch when you want it.)

### Reason 5: no warm-up

The JVM starts slow and gets fast as the JIT learns your hot paths. Rust is fully optimized from the first instruction. That matters for CLIs, serverless and lambdas, autoscaling containers, and anything with cold starts.

### The honest scorecard

| Dimension | Rust | Java |
|---|---|---|
| Peak throughput, long-running service | Excellent | Excellent; the JIT is world-class and often close |
| Memory footprint | **Much smaller** (often 5–10× less) | Larger (JVM + GC headroom) |
| Startup time | **\~1 ms** | 100s of ms to seconds (Spring); fast with GraalVM native |
| Latency predictability (p99) | **Very stable** | GC pauses (much better with ZGC/Shenandoah) |
| Compile time | Slow | **Fast** |
| Learning curve | Steep for the first 1–3 months | **Gentle** |
| Ecosystem breadth (enterprise) | Growing fast (see [ch. 12](https://ngvoicu.dev/articles/rust-for-java-developers/#spring)) | **Enormous** (Spring, everything) |
| Memory-safety bugs / data races | **Prevented at compile time in safe Rust** | Memory safe via GC; data races possible |

## 10. Java habits to unlearn

Not syntax, but design reflexes. Each of these will trip you up until it clicks.

### No null references. Use `Option`

Rust has no `null` for references: a reference must always point at a valid value. Raw pointers can be null, and dereferencing one requires `unsafe`. A value that might be absent has the type `Option<T>`, which is either `Some(value)` or `None`. It's like Java's `Optional`, but **mandatory and free**: the compiler won't let you use the inside without handling `None`, so a null dereference can't happen in safe Rust (`.unwrap()` on `None` panics instead).

### No exceptions. Use `Result`

A function that can fail returns `Result<T, E>`: either `Ok(value)` or `Err(error)`. Errors are ordinary return values, visible in the signature like checked exceptions, but without the ceremony. The `?` operator means "if this is an error, return it to my caller":

Java

```
Config load(Path p) throws IOException {
    String txt = Files.readString(p);
    return parse(txt);  // may throw too
}
```

Rust

```
fn load(p: &Path) -> Result<Config, AppError> {
    let txt = fs::read_to_string(p)?;
    parse(&txt)                // returns Result
}
```

**Panics** (`panic!`, `.unwrap()`) exist for *bugs*, the "this should never happen" cases. They're like an unchecked `Error`, not for normal control flow. In production code, prefer `?` over `.unwrap()`.

### No inheritance. Use traits + composition

There are no classes and no `extends`. Data lives in **structs**, behavior goes in **`impl` blocks**, and shared behavior is defined by **traits**, which are like Java interfaces with default methods. Key difference: you can implement a trait for a type *after the fact*, even for types you didn't write, such as adding your own trait to `String`.

### Enums that carry data, plus `match`

Rust enums are much more powerful than Java's. Each variant can hold different data, similar to Java 21's sealed interfaces with records. `match` is checked for exhaustiveness, so if you add a variant, every `match` that forgot it becomes a compile error:

```
enum PaymentStatus {
    Pending,
    Settled { at: DateTime<Utc> },
    Failed { code: u16, reason: String },
}

match status {
    PaymentStatus::Pending => retry_later(),
    PaymentStatus::Settled { at } => log_settled(at),
    PaymentStatus::Failed { code, .. } => alert(code),
}   // forgot a case? → doesn't compile
```

### Immutable by default

`let x = 5;` can't be changed. You must write `let mut x = 5;` to allow it. That's the opposite of Java, where you add `final` to forbid changes.

### Don't fight the borrow checker with Java-style object graphs

Java designs often have objects pointing at each other (parent ↔ child, observers, bidirectional links). That pattern is hard in Rust because ownership must be a tree. Idiomatic Rust prefers data flowing *down* and results flowing *up*, IDs instead of back-pointers, and plain functions over deep object hierarchies. When you feel you're fighting the compiler, the fix is usually to restructure the data, not to add more `clone()`.

## 11. Concurrency in one page

"Fearless concurrency": the ownership rules from chapter 8 also prevent data races in safe code.

Two marker traits, checked automatically by the compiler, decide what's allowed across threads:

- **`Send`**: this value can be *moved* to another thread.
- **`Sync`**: this value can be *shared by reference* between threads.

Try to share a non-thread-safe value (like `Rc` or a plain mutable `Vec`) between threads and you get a **compile error** in safe Rust, not a data race in production at 3 a.m. To share mutable state you wrap it, for example `Arc<Mutex<T>>`. In Rust the data lives *inside* the mutex, so you physically can't touch it without locking. Compare Java, where the lock and the data are separate and nothing stops you forgetting `synchronized`.

| Model | Java | Rust |
|---|---|---|
| OS threads | `new Thread`, ExecutorService | `std::thread::spawn`, scoped threads |
| Data parallelism | `parallelStream()` | `rayon`: `.par_iter()` |
| Massive I/O concurrency | Virtual threads (built-in), reactive | `async`/`await` + a runtime crate (**tokio**) |
| Message passing | `BlockingQueue` | channels: `std::sync::mpsc`, `tokio::sync` |

Async gotcha

Rust's `async` is built into the language, but the **runtime that executes async code is not**. You add one as a dependency, almost always `tokio`, and mark main with `#[tokio::main]`. That's why web frameworks like axum "require tokio". In Java, virtual threads come with the JVM.

## 12. The Spring world in Rust

Spring Boot, Spring MVC, Spring Kafka, Spring Cloud Vault, AWS starters… where are they in Rust? There's no Spring equivalent, and understanding why is the key to the whole Rust backend ecosystem.

### Why there is no "Rust Spring"

Spring's magic is built on three JVM features: **runtime reflection** (inspecting classes and annotations while the program runs), **classpath scanning** (finding every `@Component` at startup), and **dynamic proxies** (wrapping your bean in a generated class, which is how `@Transactional`, `@Cacheable` and `@Async` work).

Rust does not provide Java-style classpath scanning or general runtime reflection over fields and annotations. `Any` and `TypeId` offer limited runtime type information, and Rust also supports runtime dispatch, for example through `dyn Trait` and function pointers. Frameworks commonly use explicit wiring, traits and macros instead of Spring's reflective container. So the ecosystem grew in a different shape:

- **Small, focused libraries that compose**, instead of one framework that controls your program.
- **Compile-time macros** (`#[derive(...)]`, `#[tokio::main]`) where Java would use annotations read at runtime.
- **Explicit wiring in `main()`**: the \~30 lines Spring Boot does invisibly, you write yourself, once.

Spring Boot: a framework calls YOUR code

**ApplicationContext (DI container, auto-config)**

- Spring MVC
- Spring Data / JPA
- Spring Security
- Spring Kafka
- Spring Cloud Vault
- Actuator

reflection · classpath scanning · proxies (at startup & runtime)

1. **your @Controller, @Service…** discovered & wired by the framework

\+ one curated, version-aligned set of starters

\+ conventions everyone shares

Rust: YOUR main() calls libraries

1. **main.rs: you build & wire everything** config → pool → state → router → serve

- **axum** routing (≈ MVC)
- **sqlx / SeaORM** data (≈ JDBC / JPA)
- **rdkafka** Kafka client
- **aws-sdk-\*** S3, SQS, KMS…
- **vaultrs** Vault client
- **tracing, config…** logs, settings

- **tower: middleware (≈ Servlet filters / interceptors)**
- **hyper: HTTP server/client (≈ Tomcat / Netty)**
- **tokio: async runtime: threads, I/O, timers (the "platform")**

nothing discovered at runtime: all wiring is visible code

Upside: nothing hidden, errors at compile time (not at context startup), \~ms startup.

Downside: you assemble the stack and choose libraries; fewer shared conventions.

Inversion of control (Spring) vs explicit composition (Rust). Almost every backend crate is built on **tokio**, which acts as the common platform.

Closest to "Spring Boot experience"

If you want conventions and generators instead of assembling pieces, look at **Loco** (`loco-rs`), a "batteries-included" framework inspired by Ruby on Rails. It's built on axum + SeaORM and comes with project generators, background workers, mailers, auth scaffolding and config per environment. It's the nearest thing to `start.spring.io` in Rust. Most production teams still use the plain axum stack, so learn that first.

### Spring Boot feature by feature

| Spring Boot gives you… | In Rust you… |
|---|---|
| Embedded Tomcat / Netty | Start an **axum** server (on hyper) in `main`: `axum::serve(listener, router)` |
| DI container, `@Autowired`, `@Component` | Construct structs in `main`, share them via `Arc<AppState>` (see below) |
| Starters + auto-configuration | Add a crate + enable its *features* in Cargo.toml; write a few lines of setup |
| `application.yml` + profiles | **config** or **figment** crate: layered TOML/YAML files + env vars |
| `@RestController`, `@GetMapping` | axum `Router::new().route("/x", get(handler))` |
| Filters, interceptors, AOP | **tower** layers (middleware) via `.layer(...)` |
| `@ControllerAdvice` | An error enum that implements `IntoResponse` |
| `@Transactional` | Explicit `pool.begin()` … `tx.commit()`; automatic rollback when dropped (chapter 13) |
| `@Async`, executors | `tokio::spawn(async { ... })` |
| `@Scheduled` | `tokio::time::interval` in a spawned task, or **tokio-cron-scheduler** |
| Bean Validation (`@Valid`, `@NotNull`) | **validator** or **garde** derive macros (+ `axum-valid`) |
| springdoc / Swagger UI | **utoipa** (+ utoipa-swagger-ui) |
| Actuator (health, metrics) | A `/health` route + **metrics**/**opentelemetry** crates |
| Logback + SLF4J + MDC | **tracing** + tracing-subscriber (structured JSON, spans ≈ MDC) |
| Graceful shutdown | `axum::serve(...).with_graceful_shutdown(signal)` |

### Dependency injection without a container

In Spring, the container creates beans and injects them. In Rust you do **constructor injection by hand**, exactly like a plain Java `main()` without Spring. Everything handlers need goes into one "application state" struct, wrapped in `Arc` (a thread-safe shared pointer) so all requests can share it:

Spring

```
@Repository
class PaymentRepo { PaymentRepo(DataSource ds) {...} }

@RestController
class PaymentController {
  private final PaymentRepo repo;
  PaymentController(PaymentRepo repo) { // injected
    this.repo = repo;
  }
}
// the container finds & wires these at startup
```

Rust

```
pub struct AppState {          // your "context"
    pub repo: PaymentRepo,
}

// in main(): wire it yourself, once
let pool  = PgPoolOptions::new().connect(&url).await?;
let state = Arc::new(AppState {
    repo: PaymentRepo::new(pool),
});
let app = http::router(state);  // handlers receive it
```

A handler asks for the state with the `State` extractor: `State(state): State<Arc<AppState>>`. For **testability**, define a **trait** (an interface) for the repository and generate a mock of it with **mockall**, the Mockito equivalent. This is the same "program to an interface" idea you already use in Java.

### REST APIs: Spring MVC → axum

| Framework | Think of it as | When to choose |
|---|---|---|
| **axum** | Spring MVC / WebFlux | **Default choice.** Built by the tokio team, uses tower middleware, biggest momentum. |
| **actix-web** | Spring MVC (very fast) | Mature and extremely fast; its own middleware ecosystem. |
| **Loco** | Spring Boot + generators | You want conventions and scaffolding (built on axum). |
| **poem** | Spring MVC + springdoc | You want OpenAPI generated from code as a first-class feature. |
| **tonic** | grpc-spring-boot-starter | gRPC services. |

Spring MVC

```
@RestController
@RequestMapping("/payments")
class PaymentController {

  @GetMapping("/{id}")
  Payment get(@PathVariable UUID id) {
    return repo.findById(id)
      .orElseThrow(NotFoundException::new);
  }

  @PostMapping
  Payment create(@RequestBody NewPayment body) {
    return repo.create(body);
  }
}
```

axum

```
pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/payments", post(create_payment))
        .route("/payments/{id}", get(get_payment))
        .with_state(state)
}

async fn get_payment(
    State(state): State<Arc<AppState>>,
    Path(id): Path<Uuid>,
) -> Result<Json<Payment>, ApiError> {
    let p = state.repo.find(id).await?
                  .ok_or(ApiError::NotFound)?;
    Ok(Json(p))
}
```

Handler parameters are called **extractors**. They play the role of Spring's argument annotations, but they're plain types checked at compile time:

| Spring | axum extractor |
|---|---|
| `@PathVariable UUID id` | `Path(id): Path<Uuid>` |
| `@RequestParam` / query object | `Query(q): Query<SearchParams>` (a struct with `#[derive(Deserialize)]`) |
| `@RequestBody NewPayment` | `Json(body): Json<NewPayment>` |
| `@RequestHeader` | `headers: HeaderMap` or typed headers |
| injected `@Service` | `State(state): State<Arc<AppState>>` |
| `ResponseEntity<T>` | return `Json<T>`, `(StatusCode, Json<T>)`, or anything `impl IntoResponse` |

1. **HTTP** request

2. **tower layers** trace · timeout · auth cors · rate limit

   Servlet Filters / HandlerInterceptors

3. **Router** path → handler

   DispatcherServlet + @RequestMapping

4. **Extractors** Path · Query · Json State · headers

   argument resolvers (@PathVariable…)

5. **handler** async fn

   controller method

6. **IntoResponse** Ok → 200 + JSON Err → mapped status

   message converters + @ControllerAdvice

Bad input (e.g. invalid JSON) is rejected by the extractor before your handler runs, just like Spring's

HttpMessageNotReadableException, but with an automatic 400/422 response.

The life of a request in axum (orange) and its Spring MVC counterpart (blue).

#### Global error handling (the `@ControllerAdvice` equivalent)

*src/error.rs*

```
#[derive(Debug, thiserror::Error)]
pub enum ApiError {
    #[error("payment not found")]         NotFound,
    #[error("invalid request: {0}")]       BadRequest(String),
    #[error(transparent)]                   Database(#[from] sqlx::Error),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, message) = match &self {
            ApiError::NotFound      => (StatusCode::NOT_FOUND, self.to_string()),
            ApiError::BadRequest(_) => (StatusCode::BAD_REQUEST, self.to_string()),
            ApiError::Database(e)   => {
                tracing::error!(error = %e, "database error");  // log details…
                (StatusCode::INTERNAL_SERVER_ERROR, "internal error".to_string()) // …never leak them
            }
        };
        (status, Json(json!({ "error": message }))).into_response()
    }
}
```

The `#[from]` attribute lets `?` automatically convert a `sqlx::Error` into `ApiError::Database`, the way a Spring `DataAccessException` bubbles up to the advice.

Lesson from testing this guide

The first version of this code returned `self.to_string()` for every error. When tested, a 500 response leaked `relation "payments" does not exist` to the client. Rust's type system won't stop you from leaking information, so map internal errors to generic messages and log the details server-side.

### Configuration: application.yml & profiles

The **config** crate gives you Spring-style layering: a default file, a per-environment file, then environment variables override everything. The settings are deserialized into a typed struct, the equivalent of `@ConfigurationProperties`:

*src/config.rs*

```
#[derive(Debug, Deserialize, Clone)]
pub struct Settings {
    pub server: Server,
    pub database: Database,
    pub kafka: Kafka,
}

impl Settings {
  /// default.toml → {APP_ENV}.toml → APP__* env
  pub fn load() -> Result<Self, ConfigError> {
    let env = std::env::var("APP_ENV")
        .unwrap_or_else(|_| "local".into());
    Config::builder()
      .add_source(File::with_name("config/default"))
      .add_source(File::with_name(&format!("config/{env}"))
                    .required(false))
      .add_source(Environment::with_prefix("APP")
                    .separator("__"))
      .build()?
      .try_deserialize()
  }
}
```

*config/default.toml*

```
[server]
port = 8080

[database]
url = "postgres://app@localhost/payments"
max_connections = 10

[kafka]
brokers  = "localhost:9092"
group_id = "payments-svc"
topic    = "payment-events"
```

| Spring | Rust (this setup) |
|---|---|
| `application.yml` | `config/default.toml` |
| `application-prod.yml` | `config/prod.toml` |
| `SPRING_PROFILES_ACTIVE=prod` | `APP_ENV=prod` |
| `SPRING_DATASOURCE_URL=…` | `APP__DATABASE__URL=…` |

A missing or wrongly typed setting fails at startup with a clear error, the same as a bad `@ConfigurationProperties` binding.

### Messaging: Spring Kafka → rdkafka

The standard Kafka client is **rdkafka**, a Rust wrapper around **librdkafka**, the battle-tested C library that also powers Confluent's Python, Go and .NET clients. Configuration keys are the same ones you know (`bootstrap.servers`, `group.id`, `enable.auto.commit`…). There's a pure-Rust alternative, **rskafka**, but it's minimal.

The big difference: there's no `@KafkaListener` container that manages threads, retries and acknowledgments for you. **You write the consumer loop** and run it as a background task:

Spring Kafka

```
@KafkaListener(topics = "payment-events",
               groupId = "payments-svc")
void onEvent(String payload, Acknowledgment ack) {
    handle(payload);
    ack.acknowledge();
}
// container: threads, polling, retries, DLT
```

rdkafka

```
pub async fn run_consumer(cfg: Kafka) -> anyhow::Result<()> {
    let consumer: StreamConsumer = ClientConfig::new()
        .set("bootstrap.servers", &cfg.brokers)
        .set("group.id", &cfg.group_id)
        .set("enable.auto.commit", "false")
        .create()?;
    consumer.subscribe(&[&cfg.topic])?;
    loop {
        let msg = consumer.recv().await?;
        let payload = msg.payload_view::<str>()
                         .transpose()?.unwrap_or_default();
        // handle(payload) ...
        consumer.commit_message(&msg, CommitMode::Async)?;
    }
}
// in main: tokio::spawn(run_consumer(cfg));
```

What you build yourself (or with small helper crates): retry/back-off (**backon**), dead-letter publishing (a `FutureProducer` to a DLT topic), Avro with Schema Registry (**schema_registry_converter**), and parallelism per partition (spawn tasks). There's **no mature Rust equivalent of Kafka Streams**.

Native dependency alert

rdkafka compiles librdkafka from C source during `cargo build`. When this guide's sample service was built, it first failed with `Package 'libsasl2' not found` and `curl/curl.h: No such file`. The fix was installing `cmake`, `libcurl4-openssl-dev`, `libsasl2-dev`, `libssl-dev`, `zlib1g-dev` and `pkg-config` in the build environment. Pure-Rust crates never need this; crates ending in `-sys` or wrapping C libraries often do. Put these packages in your Docker build stage.

| Messaging need | Java | Rust crate |
|---|---|---|
| Kafka | Spring Kafka, kafka-clients | **rdkafka** (librdkafka), rskafka (pure Rust, minimal) |
| Kafka + Schema Registry (Avro/Protobuf) | Confluent serializers | **schema_registry_converter**, apache-avro, prost |
| RabbitMQ / AMQP | Spring AMQP | **lapin** |
| AWS SQS / SNS | Spring Cloud AWS | **aws-sdk-sqs**, aws-sdk-sns |
| NATS | jnats | **async-nats** (official) |
| MQTT | Eclipse Paho | **rumqttc** |
| Background jobs / queues | JobRunr, Quartz | **apalis** (Redis/Postgres-backed jobs) |

### Cloud & secrets: AWS, Azure, GCP, Vault

| Service | Rust crate | Status |
|---|---|---|
| **AWS** (S3, SQS, KMS, Secrets Manager, DynamoDB…) | **aws-sdk-\*** (one crate per service) + **aws-config** | Official AWS SDK, generally available since late 2023. Same credential chain as the Java SDK (env vars, profiles, IAM roles/IRSA). |
| **Azure** (Blob, Key Vault, Identity, Queues) | **azure_storage_blob**, **azure_security_keyvault_secrets**, **azure_identity** | Official; first stable (GA) wave in May 2026. Cosmos DB and Event Hubs weren't in that wave. |
| **Google Cloud** | **google-cloud-\*** | Official client libraries, 1.0 since 2025. |
| Any object store (S3/GCS/Azure/local) | **object_store** | One API for all clouds (from the Apache Arrow project). Handy for tests with a local filesystem. |
| **HashiCorp Vault** | **vaultrs** | Community-maintained (no official HashiCorp Rust SDK). Supports KV v1/v2, transit, PKI, database secrets, AppRole/Kubernetes auth. |

*S3 upload (official AWS SDK)*

```
let aws = aws_config::load_from_env().await;
let s3  = aws_sdk_s3::Client::new(&aws);
s3.put_object()
    .bucket(bucket)
    .key(key)
    .body(ByteStream::from(bytes))
    .send()
    .await?;
```

*Vault KV v2 read (vaultrs)*

```
let client = VaultClient::new(
    VaultClientSettingsBuilder::default()
        .address(env::var("VAULT_ADDR")?)
        .token(env::var("VAULT_TOKEN")?)  // never hard-code
        .build()?,
)?;
let creds: DbCredentials =
    vaultrs::kv2::read(&client, "secret", "payments/db").await?;
```

Java parallel: Spring Cloud Vault

Spring Cloud Vault injects secrets into your `Environment` as properties automatically and renews leases in the background. In Rust nothing does that implicitly: you read secrets at startup (as above), put them into your `Settings`, and if you use dynamic DB credentials you spawn a task that renews the lease. It's more code, but the flow is easy to follow and audit.

### Cross-cutting concerns: the big map

| Concern | Java / Spring | Rust |
|---|---|---|
| Authentication / JWT / OAuth2 | Spring Security, resource server | **jsonwebtoken**, **openidconnect**, **oauth2**, axum-login; wire as tower middleware or an extractor. There's no all-in-one Spring Security. |
| Password hashing | BCryptPasswordEncoder | **argon2**, bcrypt (RustCrypto) |
| TLS / crypto | JSSE, JCA, BouncyCastle | **rustls**, aws-lc-rs / ring, RustCrypto crates |
| CORS, compression, timeouts | Spring config / filters | **tower-http** layers |
| Rate limiting | Bucket4j, Resilience4j | **tower_governor** |
| Retry / circuit breaker | Resilience4j, Spring Retry | **backon** (retry), **failsafe** (circuit breaker), tower retry/limit layers |
| Validation | Bean Validation | **validator**, **garde** |
| Logging | SLF4J + Logback, MDC | **tracing** + tracing-subscriber (JSON output, spans) |
| Metrics | Micrometer + Prometheus | **metrics** + metrics-exporter-prometheus |
| Distributed tracing | Micrometer Tracing, OTel agent | **opentelemetry** + opentelemetry-otlp + tracing-opentelemetry (no auto-instrumentation agent; you add layers) |
| In-memory cache | Caffeine, `@Cacheable` | **moka** (inspired by Caffeine); no annotation, call it explicitly |
| Distributed cache / Redis | Spring Data Redis, Lettuce | **redis**, **fred** |
| Scheduling | `@Scheduled`, Quartz | `tokio::time::interval`, **tokio-cron-scheduler** |
| HTTP client | RestClient, WebClient, OkHttp | **reqwest** |
| Typed client from OpenAPI | Feign, openapi-generator | **progenitor** |
| OpenAPI docs from code | springdoc | **utoipa** |
| gRPC | grpc-java | **tonic** + prost |
| GraphQL | Spring for GraphQL | **async-graphql** |
| JSON / XML | Jackson, JAXB | **serde_json**; **quick-xml** (with serde). SOAP/WS-\* support is weak. |
| Money / decimals | BigDecimal | **rust_decimal** (never use `f64` for money) |
| Templates / email | Thymeleaf, JavaMail | **askama**, minijinja; **lettre** |

### Testing a service

| Java | Rust |
|---|---|
| JUnit 5, parameterized tests | built-in `#[test]`, `#[tokio::test]` for async, **rstest** for fixtures & parameterized cases |
| Mockito | **mockall** (mocks generated from traits) |
| MockMvc / WebTestClient | call the router directly with tower's `oneshot`, or **axum-test** |
| Testcontainers | **testcontainers** + testcontainers-modules (ready-made Postgres, Kafka, LocalStack… containers) |
| WireMock | **wiremock** |
| Cucumber / AssertJ snapshots | **cucumber**; **insta** (snapshot testing) |

### Where Java's ecosystem still clearly wins

Be realistic when choosing Rust for a service:

- **Oracle database**: no driver as mature as ojdbc and no ORM support (details in chapter 13).
- **Enterprise integration**: SOAP/WS-Security, JMS/IBM MQ, Spring Integration / Camel, Spring Batch, XA/JTA distributed transactions. These are thin or absent.
- **Kafka Streams** and stateful stream processing libraries.
- **Security framework**: nothing as complete as Spring Security; you assemble it from pieces, and auth code needs careful review.
- **Convention & hiring**: every Spring app looks alike, while Rust services vary more between teams.

A common, pragmatic architecture is **polyglot**: keep integration-heavy services in Java/Spring, and use Rust for focused, performance- or cost-critical services (gateways, high-throughput consumers, low-latency APIs, CLIs), talking over REST, gRPC or Kafka.

## 13. Data access: JDBC, JdbcTemplate, JPA → Rust

The part of the stack you touch every day. Some things map one-to-one; some work quite differently. Both are covered here.

### The layers you know, and their Rust counterparts

abstraction level

JAVA

- **Spring Data repositories** interface PaymentRepo extends JpaRepository · findByStatus()
- **JPA / Hibernate (ORM)** @Entity, persistence context, lazy loading, dirty checking
- **jOOQ · QueryDSL · Criteria API** type-safe query builders
- **JdbcTemplate · MyBatis · JDBI** your SQL, less boilerplate, RowMapper
- **HikariCP (pool) + JDBC API (java.sql)**
- **JDBC drivers** ojdbc, pgjdbc, mysql-connector… all speak ONE standard API

RUST

- **(no equivalent: no query derivation)** write a repository struct with explicit methods
- **SeaORM** entities, ActiveModel, relations; no lazy loading
- **Diesel · sea-query** type-safe query DSLs, checked by the compiler
- **sqlx** ≈ JdbcTemplate + HikariCP + drivers in ONE crate your SQL · #\[derive(FromRow)\] · built-in pool optional compile-time SQL checking Postgres · MySQL/MariaDB · SQLite only
- **Database-specific driver crates** tokio-postgres, tiberius, oracle… each has its OWN API

Java has one standard driver interface (JDBC) that everything builds on. Rust has no JDBC: **sqlx** is the closest thing to a common layer, and it bundles the pool and the "JdbcTemplate" part too.

### Seven things that work differently

1. **There is no JDBC.** Java's `java.sql` is a standard every vendor implements, so you can swap drivers. Rust has no such standard. Each database has its own driver crate with its own API. **sqlx** gives you one API for PostgreSQL, MySQL/MariaDB and SQLite; for anything else (Oracle, SQL Server) you use that database's crate directly.
2. **Async by default.** Every query is `.await`-ed. While a query waits for the database, the thread serves other requests instead of blocking, like WebFlux + R2DBC rather than classic JDBC. (Blocking drivers exist too; wrap them in `tokio::task::spawn_blocking`.)
3. **The pool comes with the library.** `PgPool` is your HikariDataSource. You create it once in `main`, it's cheap to clone, and you pass it around.
4. **Row mapping is generated at compile time.** `#[derive(sqlx::FromRow)]` writes the RowMapper for you, like `BeanPropertyRowMapper` but generated during compilation, so there's no reflection.
5. **SQL can be verified at compile time.** With the `query!` macros, a typo in a column name is a *build error*, not a `BadSqlGrammarException` in production (see below).
6. **No persistence context.** No Hibernate session, no lazy loading, no automatic dirty checking, no `LazyInitializationException`, and no hidden N+1 queries. What you query is what you get.
7. **Transactions are explicit values.** There's no `@Transactional` proxy. You hold a transaction object, run queries on it, and commit. If you don't commit (because of an error, an early return or a panic), it **rolls back automatically** when dropped.

### JdbcTemplate ↔ sqlx, operation by operation

Every Rust snippet below is from the sample service built for this guide and compiles against sqlx 0.9.

| JdbcTemplate | sqlx |
|---|---|
| `queryForObject(sql, Long.class, args)` | `query_scalar(sql).bind(..).fetch_one(&pool)` |
| `queryForObject(sql, rowMapper, args)` (throws if no row) | `query_as::<_, T>(sql).bind(..).fetch_one(..)` (error if no row) `.fetch_optional(..)` returns `Option<T>`: no exception for "not found" |
| `query(sql, rowMapper, args)` → `List<T>` | `.fetch_all(..)` → `Vec<T>` |
| `queryForStream` / `RowCallbackHandler` | `.fetch(..)` → an async stream, row by row |
| `int n = update(sql, args)` | `query(sql).bind(..).execute(..).await?.rows_affected()` |
| `batchUpdate(sql, batchArgs)` | `QueryBuilder::push_values` (one multi-row INSERT) |
| `NamedParameterJdbcTemplate` (`:name`) | Positional only: `$1, $2` (Postgres) or `?` (MySQL/SQLite). For dynamic SQL use `QueryBuilder` or sea-query. |
| `RowMapper<T>` / `BeanPropertyRowMapper` | `#[derive(sqlx::FromRow)]` on the struct |
| `DataSource` / HikariCP | `PgPoolOptions::new().max_connections(10).connect(url)` |
| `DataAccessException` hierarchy | one `sqlx::Error` enum (`RowNotFound`, `Database(..)`, `PoolTimedOut`…) |

JdbcTemplate repository

```
@Repository
class PaymentRepo {
  private final JdbcTemplate jdbc;
  private static final RowMapper<Payment> MAPPER =
    (rs, i) -> new Payment(
      rs.getObject("id", UUID.class),
      rs.getBigDecimal("amount"),
      rs.getString("currency"),
      rs.getObject("created_at", OffsetDateTime.class));

  Optional<Payment> find(UUID id) {
    var list = jdbc.query(
      "SELECT id, amount, currency, created_at " +
      "FROM payments WHERE id = ?", MAPPER, id);
    return list.stream().findFirst();
  }

  long countByStatus(String status) {
    return jdbc.queryForObject(
      "SELECT count(*) FROM payments WHERE status = ?",
      Long.class, status);
  }

  int markSettled(UUID id) {
    return jdbc.update(
      "UPDATE payments SET status='SETTLED' WHERE id=?", id);
  }
}
```

sqlx repository

```
#[derive(Debug, Serialize, sqlx::FromRow)]  // ← the RowMapper
pub struct Payment {
    pub id: Uuid,
    pub amount: Decimal,
    pub currency: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Clone)]
pub struct PaymentRepo { pool: PgPool }

impl PaymentRepo {
  pub async fn find(&self, id: Uuid)
      -> sqlx::Result<Option<Payment>> {
    sqlx::query_as::<_, Payment>(
      "SELECT id, amount, currency, created_at
       FROM payments WHERE id = $1")
      .bind(id)
      .fetch_optional(&self.pool)
      .await
  }

  pub async fn count_by_status(&self, s: &str)
      -> sqlx::Result<i64> {
    sqlx::query_scalar(
      "SELECT count(*) FROM payments WHERE status = $1")
      .bind(s).fetch_one(&self.pool).await
  }

  pub async fn mark_settled(&self, id: Uuid)
      -> sqlx::Result<u64> {
    let r = sqlx::query(
      "UPDATE payments SET status='SETTLED' WHERE id=$1")
      .bind(id).execute(&self.pool).await?;
    Ok(r.rows_affected())
  }
}
```

#### Batch insert and streaming

*batchUpdate and queryForStream equivalents*

```
// jdbcTemplate.batchUpdate("INSERT INTO tags ...", rows)  →  one multi-row INSERT
let mut qb: QueryBuilder<Postgres> = QueryBuilder::new("INSERT INTO tags (payment_id, tag) ");
qb.push_values(rows, |mut b, (id, tag)| { b.push_bind(id).push_bind(tag); });
qb.build().execute(pool).await?;

// jdbcTemplate.queryForStream(...)  →  rows arrive one at a time, constant memory
let mut rows = sqlx::query_as::<_, Payment>("SELECT id, amount, currency, created_at FROM payments")
    .fetch(pool);
while let Some(p) = rows.try_next().await? {
    // export p ...
}
```

Always bind, never format

Like `PreparedStatement`, `.bind(value)` sends parameters separately from the SQL, so there's no SQL injection. Never build SQL with `format!("... WHERE id = '{id}'")`. That's the Rust equivalent of string-concatenating SQL in Java.

### Compile-time checked SQL: something Java doesn't have

sqlx's **macros** (`query!`, `query_as!`, `query_scalar!`) check your SQL against a real database schema *while compiling*. They verify table and column names, parameter types, result column types, and nullability (a nullable column must map to `Option<T>`).

1. **query_as!(Payment,** "SELECT … currncy …") in your .rs file
2. **cargo build** macro runs inside the compiler
   - **dev database** via DATABASE_URL
   - **.sqlx/ cache (in git)** for CI: SQLX_OFFLINE=true
3. **compile ERROR** column "currncy" does not exist

Java: the same typo compiles fine and fails at runtime with BadSqlGrammarException, maybe in production.

Closest Java analogue: jOOQ code generation from the schema.

How the `query!` macros verify SQL during the build.

This is the real compiler output from the sample service, with a typo in a column name:

```
error: error returned from database: column "currncy" does not exist
  --> src/jdbc_style.rs:60:5
   |
60 | /     sqlx::query_as!(
61 | |         Payment,
62 | |         "SELECT id, amount, currncy, created_at FROM payments WHERE id = $1",
63 | |         id
64 | |     )
   | |_____^
```

For CI, where there's no database, run `cargo sqlx prepare` (from `cargo install sqlx-cli`). It saves the query metadata into a `.sqlx/` folder that you commit, and builds with `SQLX_OFFLINE=true` use it. The function forms (`sqlx::query_as::<_, T>(..)`, used above) skip compile-time checking; use them for dynamic SQL.

### Transactions: `@Transactional` vs explicit

Spring

```
@Transactional
public Payment create(NewPayment p) {
  Payment saved = repo.insert(p);
  audit.log(saved.id(), "CREATED");
  return saved;
}
// a proxy opens the tx before the call,
// commits after, rolls back on
// RuntimeException (not checked ones!)
// gotcha: self-invocation skips the proxy
```

sqlx

```
pub async fn create(&self, p: &NewPayment)
    -> Result<Payment, sqlx::Error> {
  let mut tx = self.pool.begin().await?;
  let payment = sqlx::query_as::<_, Payment>(
      "INSERT INTO payments (id, amount, currency)
       VALUES ($1,$2,$3) RETURNING id, amount, currency, created_at")
    .bind(Uuid::new_v4()).bind(p.amount).bind(&p.currency)
    .fetch_one(&mut *tx).await?;      // ← on tx, not pool
  sqlx::query("INSERT INTO audit_log (payment_id, action)
               VALUES ($1, 'CREATED')")
    .bind(payment.id).execute(&mut *tx).await?;
  tx.commit().await?;                     // explicit commit
  Ok(payment)
}  // any `?` above returns early → tx dropped → ROLLBACK
```

1. **pool.begin()**
2. **INSERT payment**
3. **INSERT audit**
4. **tx.commit() ✓**

1. on error
2. **tx dropped without commit → ROLLBACK** error via ?, early return, panic: always safe

Transactions use the same "drop" mechanism from chapter 8. The rollback can't be forgotten, and there's no proxy to bypass.

| Spring transaction feature | Rust / sqlx |
|---|---|
| Method in or out of a transaction | Write the function to take any executor (`&mut PgConnection`, or the generic `impl PgExecutor`), then pass `&mut *tx` or `&pool` |
| `Propagation.NESTED` (savepoints) | `sqlx::Connection::begin(&mut *tx)` on an open transaction creates a SAVEPOINT |
| `REQUIRES_NEW` | Simply begin a second, independent transaction from the pool |
| Isolation level | Run `SET TRANSACTION ISOLATION LEVEL …` as the first statement |
| XA / JTA distributed transactions | Not available. Use the outbox pattern / sagas instead. |

### ORMs: JPA, Hibernate and Spring Data → SeaORM and Diesel

JPA + Spring Data

```
@Entity @Table(name = "payments")
class Payment {
  @Id UUID id;
  BigDecimal amount;
  String currency;
  String status;
  OffsetDateTime createdAt;
}

interface PaymentRepo
    extends JpaRepository<Payment, UUID> {
  List<Payment> findByStatusOrderByCreatedAt(String s);
}

// usage
for (var p : repo.findByStatusOrderByCreatedAt("PENDING")) {
  p.setStatus("SETTLED");   // dirty checking
}                           // flushed at commit
```

SeaORM 2

```
#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "payments")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub id: Uuid,
    pub amount: Decimal,
    pub currency: String,
    pub status: String,
    pub created_at: DateTimeUtc,
}

// usage: no derived methods, build the query
let pending = payment::Entity::find()
    .filter(payment::Column::Status.eq("PENDING"))
    .order_by_asc(payment::Column::CreatedAt)
    .all(&db).await?;

for p in pending {
    let mut am: payment::ActiveModel = p.into();
    am.status = Set("SETTLED".to_owned()); // mark changed
    am.update(&db).await?;     // explicit UPDATE
}
```

SeaORM's **ActiveModel** tracks which fields you `Set`, so `update` writes only those columns. It's the closest thing to dirty checking, but it's explicit: nothing is flushed behind your back. SeaORM 2.0 (stable since July 2026) also adds an "entity-first" workflow where it can create tables from your entities, a bit like `hibernate.ddl-auto`.

#### Which one feels like what you use today?

| If in Java you like… | Use in Rust | Why |
|---|---|---|
| JdbcTemplate, MyBatis, JDBI | **sqlx** | You write SQL; mapping is generated. Most popular choice, and the one to learn first. |
| jOOQ, QueryDSL | **Diesel** or **sea-query** | Diesel generates `schema.rs` from your DB and checks every query in the type system. It's synchronous by default (use `diesel-async` for async). sea-query is a standalone dynamic query builder. |
| JPA / Hibernate / Spring Data | **SeaORM** | Entities, relations, ActiveModel, migrations, codegen from an existing DB (`sea-orm-cli generate entity`). |
| Oracle with any of the above | see the drivers table below | None of the three supports Oracle. |

### Database drivers

| Database | Java | Rust crate(s) | Notes |
|---|---|---|---|
| **PostgreSQL** | pgjdbc | **sqlx**, tokio-postgres (+ deadpool-postgres) | Pure Rust, excellent, the best-supported database in Rust. |
| **MySQL / MariaDB** | Connector/J | **sqlx**, mysql_async | Pure Rust. |
| **SQLite** | sqlite-jdbc | **sqlx**, rusqlite | Bundles the C SQLite library. |
| **SQL Server** | mssql-jdbc | **tiberius** | Pure Rust TDS driver. Not in sqlx; Diesel/SeaORM need commercial or third-party add-ons. |
| **Oracle** | ojdbc (thin, pure Java) | **oracle** (rust-oracle), **sibyl**, **oracle-rs** | See the box below. |
| **MongoDB** | mongodb-driver | **mongodb** | Official MongoDB driver. |
| **Redis / Valkey** | Lettuce, Jedis | **redis**, **fred** | Both mature. |
| **Cassandra / ScyllaDB** | DataStax driver | **scylla** | Fully compatible with Cassandra. |
| **Elasticsearch / OpenSearch** | official clients | elasticsearch, **opensearch** | Both official; the Elasticsearch crate is still published as pre-release (alpha) versions. |
| **DynamoDB** | AWS SDK | **aws-sdk-dynamodb** | Official AWS SDK. |
| Anything with ODBC (DB2, etc.) | JDBC-ODBC / vendor | **odbc-api** | Needs the vendor's ODBC driver installed. |

Oracle: the honest picture

Java's ojdbc "thin" driver is pure Java: drop in the JAR and connect. Rust's situation:

- **`oracle`** (rust-oracle): the most established option. It wraps Oracle's ODPI-C library, so it needs the **Oracle client libraries (e.g. Instant Client) installed at runtime**, which makes for a bigger Docker image (check Oracle's license terms). The API is synchronous, so in an async service wrap calls in `tokio::task::spawn_blocking`. It supports bind variables, PL/SQL blocks with OUT parameters, LOBs, batch DML and has a built-in connection pool.
- **`sibyl`**: also built on Oracle's C client (OCI), offering both blocking and async APIs.
- **`oracle-rs`**: new and promising. It's a **pure-Rust, async** implementation of Oracle's network protocol, so no Instant Client is needed, and `deadpool-oracle` provides pooling. But it's at version 0.1.x and maintained by one person, so treat it as early-stage.
- No mainstream ORM or sqlx supports Oracle. You'll write SQL by hand, JdbcTemplate-style.

**Practical advice:** for Oracle-heavy, PL/SQL-heavy domains, Java remains the lower-risk choice. If you do use Rust against Oracle, prototype with your real schema and data types first, and load-test the driver before committing.

### Migrations: Flyway & Liquibase

| Java | Rust | How it works |
|---|---|---|
| Flyway (SQL files, runs on startup) | **sqlx migrate** | `sqlx migrate add create_payments` creates a timestamped `.sql` file. `sqlx::migrate!("./migrations")` embeds the files *into your binary* at compile time; `.run(&pool)` applies pending ones on startup and records them in `_sqlx_migrations`. |
| Flyway (multi-DB) | **refinery** | Flyway-like, SQL or Rust migrations, supports Postgres, MySQL, SQLite, SQL Server. |
| Liquibase changesets in code | **sea-orm-migration** | Migrations written in Rust with a schema-builder API. |
| Liquibase / Flyway CLI in CI | keep using them! | Both are language-independent tools. A Rust service can share the same Liquibase pipeline your Java services already use, which is often the simplest choice in a mixed estate. |

*Flyway-on-startup, Rust style (from the sample service, verified)*

```
let pool = PgPoolOptions::new().max_connections(10).connect(&url).await?;
sqlx::migrate!("./migrations").run(&pool).await?;   // applies migrations/2026…_create_payments.sql
```

## 14. Putting it together: a real service

A small "payments" microservice that combines the last two chapters: REST, PostgreSQL, migrations, Kafka, S3, Vault, config and JSON logging. It was built and run for this guide, and the outputs below are real.

### Project layout

```
payments-svc/
├── Cargo.toml
├── config/
│   └── default.toml        # application.yml
├── migrations/
│   └── 2026…_create_payments.sql  # Flyway V1__
└── src/
    ├── main.rs        # @SpringBootApplication + wiring
    ├── config.rs      # @ConfigurationProperties
    ├── http.rs        # @RestController
    ├── error.rs       # @ControllerAdvice
    ├── repo.rs        # @Repository (sqlx)
    ├── jdbc_style.rs  # JdbcTemplate-style examples
    ├── kafka.rs       # @KafkaListener
    └── cloud.rs       # S3 + Vault clients
```

*Cargo.toml: your starters*

```
[dependencies]
tokio      = { version = "1", features = ["full"] }  # runtime
axum       = "0.8"                    # starter-web
tower-http = { version = "0.7", features = ["trace", "timeout"] }
serde      = { version = "1", features = ["derive"] } # Jackson
serde_json = "1"
sqlx = { version = "0.9", features = ["runtime-tokio",
  "postgres", "migrate", "macros", "uuid",
  "rust_decimal", "chrono"] }      # jdbc + Hikari + Flyway
uuid          = { version = "1", features = ["serde", "v4"] }
rust_decimal  = { version = "1", features = ["serde"] } # BigDecimal
chrono        = { version = "0.4", features = ["serde"] }
config        = "0.15"                 # application.yml
tracing       = "0.1"                  # SLF4J
tracing-subscriber = { version = "0.3", features = ["env-filter", "json"] }
thiserror     = "2"
anyhow        = "1"
futures-util  = "0.3"
rdkafka       = { version = "0.39", features = ["cmake-build"] } # spring-kafka
aws-config    = { version = "1", features = ["behavior-version-latest"] }
aws-sdk-s3    = "1"                    # spring-cloud-aws
vaultrs       = "0.8"                  # spring-cloud-vault
```

### main.rs: the whole "application context"

*src/main.rs*

```
pub struct AppState {
    pub repo: repo::PaymentRepo,
}

#[tokio::main]                                          // starts the async runtime
async fn main() -> anyhow::Result<()> {
    // 1. logging (like logback.xml): RUST_LOG=info,payments_svc=debug
    tracing_subscriber::fmt().with_env_filter(EnvFilter::from_default_env()).json().init();

    // 2. configuration (like application.yml + profiles)
    let settings = config::Settings::load()?;

    // 3. connection pool (like HikariCP) + migrations (like Flyway)
    let pool = PgPoolOptions::new()
        .max_connections(settings.database.max_connections)
        .connect(&settings.database.url)
        .await?;
    sqlx::migrate!("./migrations").run(&pool).await?;

    // 4. wire the "beans" by hand
    let state = Arc::new(AppState { repo: repo::PaymentRepo::new(pool) });

    // 5. background Kafka consumer, runs concurrently with the web server
    tokio::spawn(kafka::run_consumer(settings.kafka.clone()));

    // 6. HTTP server (like embedded Tomcat) with graceful shutdown
    let listener = tokio::net::TcpListener::bind(("0.0.0.0", settings.server.port)).await?;
    axum::serve(listener, http::router(state))
        .with_graceful_shutdown(async { tokio::signal::ctrl_c().await.ok(); })
        .await?;
    Ok(())
}
```

**HTTP clients**

one process · tokio runtime (a few OS threads, many lightweight tasks)

- **HTTP server task (axum)** one lightweight task per request tower: trace, timeout handlers → PaymentRepo
- **Kafka consumer task** tokio::spawn(run_consumer) recv → handle → commit (like a listener container)
- **Arc\<AppState\> → PaymentRepo → PgPool** shared by all tasks, thread-safe (checked by the compiler)

startup only: Settings::load() · Vault read · sqlx::migrate!()

- Kafka brokers
- AWS S3
- PostgreSQL
- Vault

Runtime architecture of the sample service. Everything is ordinary values and tasks you created yourself.

### What happened when it ran

```
$ APP__DATABASE__URL=postgres://app:***@localhost/payments RUST_LOG=info ./payments-svc

$ curl localhost:8080/health
UP
$ curl -X POST localhost:8080/payments -d '{"amount":"125.50","currency":"EUR"}' -H 'content-type: application/json'
{"id":"1b4fa61e-…","amount":"125.5000","currency":"EUR","created_at":"2026-10-21T11:33:20.006238Z"}
$ curl localhost:8080/payments/1b4fa61e-…
{"id":"1b4fa61e-…","amount":"125.5000","currency":"EUR","created_at":"2026-10-21T11:33:20.006238Z"}
$ curl -X POST … -d '{"amount":"-5","currency":"EUR"}'
{"error":"invalid request: amount must be positive"}     # 400
$ curl localhost:8080/payments/00000000-0000-0000-0000-000000000000
{"error":"payment not found"}                            # 404
$ curl -X POST … -d '{"amount":"oops"}'
Failed to deserialize the JSON body into the target type: amount: invalid value: string "oops",
expected a Decimal type …                                # 422, rejected by the Json extractor
```

The migration was recorded in `_sqlx_migrations`, and the payment plus its audit row were committed in one transaction. With no Kafka broker running, the consumer logged structured JSON connection errors (from librdkafka) and the HTTP API was unaffected.

Gotcha: spawned tasks fail silently

If `run_consumer` returns an `Err`, the task simply ends, because nobody looks at the result of `tokio::spawn`. A Spring listener container would log and restart. In production, wrap the consumer in a loop that logs the error, backs off and restarts, or keep the `JoinHandle` and shut the service down so Kubernetes restarts it.

| Measured | Value | Context |
|---|---|---|
| Crates in the dependency tree | **318** | comparable to a Spring Boot app's JAR count; run `cargo audit` |
| First release build (cold) | **\~8 min** | small cloud VM, compiling all 318 crates plus librdkafka from C. Cached afterwards; incremental rebuilds take seconds. |
| Release binary size | **12 MB** | single file; runtime shared libraries needed: only libc and zlib |
| Memory (RSS) running, pool + Kafka consumer | **\~10 MB** | a comparable Spring Boot service typically uses well over 100 MB |

### Shipping it in Docker

*Dockerfile*

```
# ---- build stage: needs C toolchain for librdkafka ----
FROM rust:1-bookworm AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
      cmake pkg-config libcurl4-openssl-dev libsasl2-dev libssl-dev zlib1g-dev
WORKDIR /app
COPY . .
ENV SQLX_OFFLINE=true                 # use committed .sqlx/ query cache, no DB at build time
RUN cargo build --release --locked   # --locked: fail if Cargo.lock would change

# ---- runtime stage: same Debian release as the build (glibc must match) ----
FROM debian:bookworm-slim
RUN useradd --system --uid 10001 app
COPY --from=build /app/target/release/payments-svc /usr/local/bin/
COPY config /config
WORKDIR /
USER app
ENTRYPOINT ["payments-svc"]
# secrets: inject APP__DATABASE__URL / VAULT_TOKEN at runtime, never bake them in
```

Faster CI builds

Compile time is Rust's real cost in CI. The standard fixes: cache `~/.cargo/registry` and `target/` between pipeline runs, use **cargo-chef** in Docker to cache the dependency layer separately from your code, and run `cargo check` + `clippy` + tests before the slow release build.

Lab · your next steps on this service

☐ Add a `GET /payments?status=` endpoint with a `Query` extractor · ☐ Convert one query to `query_as!` and break a column name on purpose · ☐ Add `utoipa` and serve Swagger UI · ☐ Write an integration test using **testcontainers** Postgres · ☐ Make the Kafka handler insert into the DB inside a transaction · ☐ Add a `/metrics` endpoint with metrics-exporter-prometheus · ☐ Run `cargo audit` and `cargo deny check`.

Before production

Code that handles authentication, payments, keys or personal data should go through the same security review you'd require for a Java service, whatever the language. Safe Rust prevents memory-safety bugs, not logic bugs, authorization mistakes or information leaks (like the error-message leak caught in chapter 12).

## 15. Zero → hero roadmap

A realistic path for an experienced Java developer, with time estimates assuming a few hours a week.

1. **1** Tooling & basics week 1–2
2. **2** Ownership clicks week 2–5
3. **3** Traits, errors, modules week 5–8
4. **4** Async + real service month 2–4
5. **5** Hero: lifetimes, perf, unsafe, macros month 4+

The learning curve is steep early and then flattens. Most people describe a moment around week 3–6 when ownership "clicks".

| Stage | Learn | Build |
|---|---|---|
| **1 · Tooling & basics** | Everything in chapters 2–6 of this guide. Variables, functions, structs, enums, `match`, `Vec`, `String` vs `&str`. | Solve exercises with **Rustlings**. A tiny CLI: word counter for a file. |
| **2 · Ownership** | Move, borrow, `&` vs `&mut`, `clone`, slices, why `String` ≠ `&str`. Read every compiler error fully. | A CSV parser that computes totals per category (no crates, then with `csv` + `serde`). |
| **3 · Idiomatic code** | Traits, generics, `Option`/`Result`/`?`, iterators and closures, modules and visibility, `thiserror`/`anyhow`, tests. | A proper CLI with `clap`: subcommands, config file, error handling, unit and integration tests. |
| **4 · Real service** | `async`/`await`, tokio, `Arc`/`Mutex`, axum, sqlx, tracing, workspaces, Docker builds. Chapters 12–14 of this guide are your map. | Extend the chapter 14 service (its lab checklist), then rebuild a small Java service you know and compare memory, startup and code size. |
| **5 · Hero** | Explicit lifetimes, `Box<dyn Trait>` vs generics, performance profiling, writing macros, `unsafe` and FFI, embedded/WASM if curious. | Contribute to an open-source crate. Profile and optimize something with `cargo flamegraph` + `criterion`. |

### The best free resources

| Resource | What it is |
|---|---|
| [**The Rust Programming Language**](https://doc.rust-lang.org/book/) ("the Book") | The official book and the canonical starting point. Read chapters 1–10 slowly; ch. 4 (ownership) twice. |
| [**Rustlings**](https://github.com/rust-lang/rustlings) | Small broken programs you fix, which trains you to read compiler errors. Pairs with the Book. |
| [**Rust by Example**](https://doc.rust-lang.org/rust-by-example/) | The same topics, example-first. Great as a reference. |
| [**Exercism Rust track**](https://exercism.org/tracks/rust) | Exercises with optional human mentor feedback on idiomatic style. |
| [**The Cargo Book**](https://doc.rust-lang.org/cargo/) | Everything about Cargo.toml, profiles, workspaces, features. |
| [**axum examples**](https://github.com/tokio-rs/axum/tree/main/examples) | Dozens of small, runnable apps: auth, databases, WebSockets, testing, graceful shutdown. Your "Spring Guides". |
| [**sqlx**](https://github.com/transact-rs/sqlx) / [**SeaORM docs**](https://www.sea-ql.org/SeaORM/docs/index/) | The two data-access libraries from chapter 13: README, examples, migration and offline-mode guides. |
| [**Loco**](https://loco.rs) | If you want the closest thing to Spring Boot conventions and generators. |
| [**Zero To Production in Rust**](https://www.zero2prod.com/) (paid) | Building a real production web backend (axum/actix, Postgres, CI). Very Java-dev friendly. |

Your first-week checklist

☐ Install rustup and editor support · ☐ `cargo new`, `run`, `build --release`, and run the binary directly · ☐ Make a `lib.rs` + `main.rs` package with two modules · ☐ Add a dependency with `cargo add` and open its docs with `cargo doc --open` · ☐ Write 3 unit tests and run `cargo test` · ☐ Run `cargo clippy` and fix every warning · ☐ Finish Rustlings sections 1–6.

## 16. Java ↔ Rust cheat sheet

Print this table.

| Java | Rust | Note |
|---|---|---|
| Tooling & build |  |  |
| JDK | toolchain | installed by rustup |
| SDKMAN | rustup | `rustup update`, `rust-toolchain.toml` |
| Maven / Gradle | cargo | build + deps + test + run + docs |
| pom.xml | Cargo.toml | TOML, not XML |
| (dependency locking) | Cargo.lock | auto-generated; commit it |
| Maven Central | crates.io | + docs.rs for documentation |
| \~/.m2/repository | \~/.cargo/registry | local download cache |
| JAR | crate | unit of compilation and sharing |
| Maven module | package | folder with Cargo.toml |
| multi-module build | workspace | `[workspace] members` |
| Code structure & language |  |  |
| Java package | module (`mod`) | declared explicitly |
| import | use | `use std::collections::HashMap;` |
| public / package-private / private | pub / pub(crate) / (default) | private by default |
| class (data) | struct | + `impl` block for methods |
| interface | trait | can implement for foreign types |
| sealed interface + records | enum with data | + exhaustive `match` |
| null / Optional | Option\<T\> | no null references; absence is an Option |
| checked exceptions | Result\<T, E\> + `?` | errors are values |
| RuntimeException / Error | panic! | for bugs only |
| final | (default) | `let mut` to allow mutation |
| try-with-resources / close() | Drop (automatic) | runs at end of scope |
| garbage collector | ownership + borrowing | Rc/Arc when sharing is required |
| synchronized / Lock | Mutex\<T\> (data inside) | + Send/Sync compile checks |
| ArrayList / HashMap | Vec / HashMap | in `std::collections` |
| String / StringBuilder | String (owned) / &str (borrowed) | String is growable |
| Streams | iterators | lazy, zero-cost |
| Lombok / annotation processors | derive / proc macros | compile-time, no reflection |
| JUnit @Test | \#\[test\] | in-file `mod tests` |
| Javadoc | /// doc comments + rustdoc | examples are tested |
| Checkstyle / Spotless | rustfmt | `cargo fmt` |
| SpotBugs / Sonar | clippy | `cargo clippy` |
| Spring & web (chapter 12) |  |  |
| Spring Boot | axum + tokio + crates you choose (or Loco) | wired explicitly in `main` |
| @Autowired / DI container | `Arc<AppState>` + `State` extractor | constructor injection by hand |
| @RestController / @GetMapping | `Router::new().route(.., get(..))` | axum |
| @PathVariable / @RequestBody | `Path<T>` / `Json<T>` | extractors |
| @ControllerAdvice | error enum + `IntoResponse` | thiserror helps |
| Servlet filter / interceptor | tower layer | tower-http has the common ones |
| application.yml + profiles | config / figment crates | files + env vars |
| Data access (chapter 13) |  |  |
| JdbcTemplate | sqlx `query` / `query_as` | `fetch_one/optional/all`, `execute` |
| RowMapper | `#[derive(FromRow)]` | generated at compile time |
| HikariCP DataSource | `PgPool` | built into sqlx |
| JPA / Hibernate / Spring Data | SeaORM (or Diesel) | no lazy loading, no derived queries |
| @Transactional | `pool.begin()` … `tx.commit()` | rollback on drop |
| Flyway | `sqlx::migrate!()` / refinery | or keep the Flyway/Liquibase CLI |
| ojdbc | oracle / sibyl / oracle-rs | weakest area, see ch. 13 |
| Messaging, cloud & operations |  |  |
| @KafkaListener | rdkafka `StreamConsumer` loop | in a `tokio::spawn`ed task |
| AWS SDK for Java | aws-sdk-\* (official) | same credential chain |
| Spring Cloud Vault | vaultrs | read at startup, explicit |
| @Scheduled / @Async | `tokio::time::interval` / `tokio::spawn` | tokio-cron-scheduler for cron |
| Caffeine / @Cacheable | moka | explicit calls |
| Resilience4j | tower layers, backon, failsafe | assemble what you need |
| Micrometer / Actuator | metrics, opentelemetry, /health route |  |
| Testcontainers / WireMock / Mockito | testcontainers / wiremock / mockall |  |
| Running it |  |  |
| GraalVM native-image | (the default) | always native |
| java -jar app.jar | ./app | no runtime to install |

---

Numbers in this guide were measured on real projects built with rustc 1.97 on Linux x86-64: a `cargo new` hello world (binary sizes, startup time) and the chapter 14 payments service (axum 0.8, sqlx 0.9, SeaORM 2.0, rdkafka 0.39, aws-sdk-s3 1.x, vaultrs 0.8, run against PostgreSQL 16; crate count, build time, binary size, memory). Crate versions and maturity statuses were checked in October 2026. Re-check them on crates.io before choosing. Your exact numbers will differ by platform and version. Memory and performance comparisons are typical ranges, not guarantees; always measure your own workload.

Gabriel Voicu

I’m a software engineer. I build AI agents that work inside large systems, and I write open-source tools for coding agents.

[More about me](https://ngvoicu.dev/about/)
