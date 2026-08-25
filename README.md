# LangChain, LangGraph and Async Python

[![Build](https://github.com/konradcinkusz/llm-book/actions/workflows/build.yml/badge.svg)](https://github.com/konradcinkusz/llm-book/actions/workflows/build.yml)
[![Pages](https://img.shields.io/github/deployments/konradcinkusz/llm-book/github-pages?label=docs)](https://konradcinkusz.github.io/llm-book/)
[![Text: CC BY-NC-SA 4.0](https://img.shields.io/badge/text-CC%20BY--NC--SA%204.0-0E7C7B)](LICENSE-CONTENT)
[![Code: MIT](https://img.shields.io/badge/code-MIT-B26A00)](LICENSE)

A practitioner's guide to **LangChain 1.x**, **LangGraph 1.x** and **async
Python** for building agents that run in production — written for engineers
arriving from a typed, async-first backend ecosystem, most likely .NET.

Not an introduction to large language models, and not a Python tutorial. It
assumes you have shipped services, know why idempotency matters on a retried
request, and are now being asked to put an agent behind an API.

> **A complete draft, indexed and cross-checked.** All seventeen chapters and six
> appendices are written — 244 pages, zero unresolved references, zero overfull
> vboxes. A 411-entry index and a full consistency pass between the chapters and
> the appendices are both done.
>
> **Every listing was executed against the pinned versions**, so nothing carries
> a *run this before you trust it* marker. Where something could not be verified,
> the text says so rather than rounding up. The consistency pass found one place
> where that discipline had slipped — a `recursion_limit` default asserted from
> memory in an appendix, and wrong in exactly the way memory is wrong for this
> ecosystem — and fixed it in both the chapter and the appendix that repeated it.
>
> What remains is finishing rather than drafting: three measurements that need a
> provider budget, the mini-project's stages, and one screenshot. Each is counted
> on every CI build so the debt is visible rather than quietly carried.

---

## Why this book

LangChain 1.0 was published on 17 October 2025 (and announced the following
week). It removed the three abstractions that
almost every tutorial before it was built on — `AgentExecutor`,
`initialize_agent` and `LLMChain` — while inverting the relationship between the
two libraries. `langchain` is now a thin layer over `langgraph`'s runtime, and
`create_agent` returns a compiled LangGraph graph.

The practical consequence is unusually severe: **most LangChain material on the
internet describes an architecture that no longer exists.** Search results, blog
posts and a very large amount of model training data all predate the split.

The 1.0 line carries a commitment to no breaking changes before 2.0, so the
material is finally worth writing down carefully rather than provisionally.

---

## What is covered

| Part | Chapters |
|---|---|
| **I — Foundations** | The Landscape · Python for the .NET Engineer · Asynchronous Python · Cancellation, Timeouts and Resilience |
| **II — LangChain 1.x** | Models, Messages and Runnables · Tools and Structured Output · `create_agent` and Middleware |
| **III — LangGraph** | StateGraph · Persistence, Durability and Resilience · Interrupts, Time Travel and Streaming · Multi-Agent Systems |
| **IV — Production** | Context Engineering · Serving Agents · Observability, Evaluation and Testing · Security, Cost and Deployment |
| **V — Perspective** | The Ecosystem, the Alternatives and the Criticism · The Capstone |
| **Appendices** | Packages and migration · API cheat sheet · Troubleshooting · Interview preparation · Glossary and sources · Figure manifest |

Two chapters on `asyncio` rather than one, because an agent is a workload in
which over ninety per cent of wall-clock time is spent waiting on a network, and
the interesting failure modes — a swallowed cancellation, an unbounded queue, a
blocking call in a coroutine — show up in production rather than in a notebook.

### Five experiments, three and a half run — none needing a provider

The book's differentiator is meant to be original measurement rather than
assertion. Five experiments are fully specified; **three and a half have been
run**, all of them without a provider. Until an experiment runs, every claim it
would support is explicitly labelled as judgement and Appendix B's table for it
stays empty.

**Experiment 1 (Chapter 3)** is done and reproducible in thirty seconds with no
provider — twenty requests against a localhost server with a fixed 100 ms delay,
median of ten trials:

| Strategy | Median | Round trips |
|---|---|---|
| Sequential | 2.039 s | 20.4× |
| `gather` | 0.126 s | 1.3× |
| `TaskGroup` | 0.125 s | 1.2× |
| Capped at 5 | 0.421 s | 4.2× |

A 16× difference from a one-line change — and `gather` and `TaskGroup` are
indistinguishable, so that choice is about failure semantics and never about
speed.

**Experiment 2 (Chapter 13)** is done — a FastAPI service under uvicorn, real
HTTP, mocked provider, 400 requests per cell:

| Concurrency | Mode | p50 | Throughput |
|---|---|---|---|
| 1 | clean | 103 ms | 10/s |
| 40 | clean | 103 ms | 349/s |
| 40 | one-in-twenty blocking | 164 ms | 194/s |
| 40 | same, via `to_thread` | 102 ms | 332/s |

Latency flat, throughput linear — and **one request in twenty doing something
blocking costs 44% of throughput** and degrades the nineteen that were innocent.

**Experiment 3 (Chapter 12)** measured four context strategies over a ten-turn
conversation:

| Strategy | Billed tokens | vs naive |
|---|---|---|
| naive | 43,510 | 1.00× |
| projected tool results | 6,910 | **0.16×** |
| summarised history | 28,180 | 0.65× |
| both | 6,910 | 0.16× |

**Projecting tool results cut the bill 84%; summarising history cut 35%** — and
with projection the summariser never fires at all. The technique everyone writes
about is worth less than half the one almost nobody applies.

**Experiment 5 (Chapter 11)** split in two, and the free half is done. Structural
cost — model calls and context carried — is a property of the topology rather
than the model, so a counting fake measures it exactly:

| Topology | Model calls | vs baseline |
|---|---|---|
| Single agent | 2 | 1.0× |
| Pipeline / swarm | 3 | 1.4× |
| Orchestrator + 3 workers | 5 | 2.3× |
| Supervisor (2 workers) | 5 | 2.8× |

Three of a supervisor's five model calls are routing rather than work. What that
buys in answer quality is the half that still needs a provider, and until it runs
every comparative quality claim in the book stays labelled as judgement.

---

## The mini-project

The book builds one system across its length, a stage per chapter:
**[Ops Copilot](https://github.com/konradcinkusz/llm-book-mini-project)** — an
internal operations assistant served over FastAPI, backed by Postgres, that can
take exactly one irreversible action and only behind a human approval gate.

Every stage's tests pass **without a single real model call**. A stage that needs
a live provider to demonstrate anything has been designed wrong.

---

## Building it

```bash
git clone https://github.com/konradcinkusz/llm-book.git
cd llm-book
make          # renders diagrams, then compiles
```

Requires a TeX distribution with `listings`, `tcolorbox`, `titlesec`,
`microtype` and `imakeidx`; TeX Live and MiKTeX both have them. Optional font
and language packages (`newtx`, `inconsolata`, `babel`'s Polish and British
data) are used when present and skipped when not, so a minimal installation
still builds.

Diagrams additionally need Node and a Chromium that `mermaid-cli` can drive.

| Command | Does |
|---|---|
| `make` | Render diagrams, then full build |
| `make text-only` | Compile without re-rendering diagrams |
| `make diagrams` | Render `figures/mermaid/*.mmd` to PDF |
| `make debt` | Print every outstanding-work ledger |
| `make watch` | Rebuild on save |
| `make clean` | Remove build artefacts |

### Diagrams are text

Mermaid source in `figures/mermaid/` is committed; rendered PDFs are not. A
diagram change therefore reviews as a readable text diff rather than as a binary
blob, and a build without `mermaid-cli` prints the Mermaid source in place of
the figure instead of failing.

---

## Repository structure

```
main.tex                  chapter wiring and part structure
preamble.tex              styling, macros, environments, pinned version macros
CLAUDE.md                 working notes: conventions, briefs, verification state
frontmatter/              title page, introduction
chapters/                 ch01 – ch17
appendices/               appA – appF
figures/mermaid/          diagram source (committed)
figures/diagrams/         rendered diagrams (build output, gitignored)
figures/screenshots/      drop captures here, named by key
code/                     listings pulled into the book with \pyfile / \pyregion
tools/check_versions.py   compares the preamble's pins against PyPI
.github/workflows/        build (every PR) · release (every tag) · pages
```

---

## Versions

Every listing is written against the versions pinned in `preamble.tex` and
recorded on the title page. A CI job compares those pins against PyPI on every
build, so a stale pin is visible rather than discovered by a reader.

The conceptual material — the execution model, reducers, the replay semantics of
a node, the economics of a supervisor — will outlive many minor versions. The
exact import paths and keyword arguments will not.

---

## Links

- **[Read the two-minute summary](https://konradcinkusz.github.io/llm-book/)** —
  the same status, contents and measurement tables as this README, rendered.
- **[Ops Copilot](https://github.com/konradcinkusz/llm-book-mini-project)** — the
  mini-project this book builds one stage per chapter.
- **[Microsoft Agent Framework for .NET Engineers](https://github.com/konradcinkusz/maf-book)**
  — the companion volume for readers on the other stack.

---

## Contributing

Errata are the most valuable contribution here. Include the package versions you
are running; in this ecosystem most reports are version drift rather than
mistakes.

Bugs in LangChain or LangGraph themselves belong
[upstream](https://github.com/langchain-ai/langchain/issues), not here.

---

## Licence

The **prose** is [CC BY-NC-SA 4.0](LICENSE-CONTENT). The **code samples, LaTeX
macros and build tooling** are [MIT](LICENSE), so you can paste them into
commercial work without thinking about it.

Not affiliated with or endorsed by LangChain Inc.
