# LangChain, LangGraph and Async Python

[![Build](https://github.com/konradcinkusz/llm-book/actions/workflows/build.yml/badge.svg)](https://github.com/konradcinkusz/llm-book/actions/workflows/build.yml)
[![Text: CC BY-NC-SA 4.0](https://img.shields.io/badge/text-CC%20BY--NC--SA%204.0-0E7C7B)](LICENSE-CONTENT)
[![Code: MIT](https://img.shields.io/badge/code-MIT-B26A00)](LICENSE)

A practitioner's guide to **LangChain 1.x**, **LangGraph 1.x** and **async
Python** for building agents that run in production — written for engineers
arriving from a typed, async-first backend ecosystem, most likely .NET.

Not an introduction to large language models, and not a Python tutorial. It
assumes you have shipped services, know why idempotency matters on a retried
request, and are now being asked to put an agent behind an API.

> **Chapters 1, 3, 7, 8, 9 and 10 are written. The rest are not.** The
> structure, build and diagram pipeline are in place and the book compiles clean
> at 150 pages. Every unwritten chapter prints a visible *NOT YET WRITTEN* box carrying
> its own brief, and CI reports the count on every build, so the page count never
> flatters the state of the work.
>
> Every listing in every written chapter was executed against the pinned
> versions, so none carries a *run this before you trust it* marker. That is the
> standard the rest of the book is held to.

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

### Five experiments, one run

The book's differentiator is meant to be original measurement rather than
assertion. Five experiments are fully specified in the chapters; **one has been
run.** Until an experiment runs, every claim it would support is explicitly
labelled as judgement and Appendix B's table for it stays empty.

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

The largest experiment still outstanding compares a single agent against all
five multi-agent topologies on one fixed task — turn count, token cost, latency
and success rate, twenty runs each, medians and spreads rather than best runs.

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
