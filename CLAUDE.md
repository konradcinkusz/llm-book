# CLAUDE.md — working on this book

Context for continuing *LangChain, LangGraph and Async Python*.
Read this before touching a chapter.

---

## Status

| | Done | Remaining |
|---|---|---|
| Structure | main.tex, preamble, build, CI, mermaid pipeline | — |
| Front matter | Title page, Introduction | — |
| Chapters | **1** | 2–17, stubbed |
| Appendices | 0 written | A–F, all stubbed |

Build is clean: `latexmk -pdf main.tex` returns 0, **87 pages**, **zero
unresolved references**, **3 overfull hboxes (9.9 / 9.1 / 0.3 pt)**, **zero
overfull vboxes**. Chapter 1 is 17 of those pages; the rest is scaffolding.

**Debt ledgers, reported by CI on every build:**
- 22 chapters and appendices not yet written (`make stubs`)
- 0 screenshots requested so far
- **0 `verifybox` blocks.** Every listing in Chapter 1 was executed against the
  pinned versions, so none needed one. Keep it that way.
- 4 Mermaid sources; all render

**Five experiments are specified across the chapters and none has been run.**
See *Measurement debt* below. Appendix B's results tables stay empty until they
have been.

---

## Non-negotiable conventions

**Verify before writing.** Do not write API surface from memory. The LangChain
ecosystem was restructured in October 2025, and a very large fraction of what a
model has absorbed about it describes the pre-1.0 architecture. Anything you
"remember" about `AgentExecutor`, `LLMChain`, `initialize_agent` or
`langgraph.prebuilt.create_react_agent` is a description of a library that no
longer exists.

Sources, in order of authority:

1. **The installed package.** `uv pip install langchain==$(pin)` into a scratch
   venv and read the source. This is the only source that cannot be stale.
2. `github.com/langchain-ai/langchain` and `.../langgraph` at the tag matching
   the pin — `examples/` and the tests are more informative than the prose docs.
3. `docs.langchain.com/oss/python/` — current, but written for the happy path.
4. `reference.langchain.com/python/` — generated API reference.
5. `blog.langchain.com` — rationale and announcements.

> **Network note.** In the Claude Code web sandbox `pypi.org` and
> `files.pythonhosted.org` are reachable, so packages install and their source
> can be read directly. That is the authoritative route and it should be the
> default. `api.github.com` needs `add_repo`. Check
> `tools/check_versions.py` output before starting a chapter — if a pin has
> drifted a long way, resolve that first rather than writing against a version
> nobody will install.

**Run listings, or mark them.** Anything not executed against the pinned
versions goes inside `\begin{verifybox}`. Removing a verifybox means you ran the
code — not that you reread it and it felt right. Nothing ships to a reader with
one attached.

**Versions live in `preamble.tex` only** (`\lcver`, `\lgver`, and the rest).
Never write a version number into a chapter. `tools/check_versions.py` compares
every pin against PyPI on each build.

**ASCII inside listings.** No em-dashes or smart quotes inside `python`,
`csharp`, `shellcmd`, `yamlcode`, `jsoncode`, `console`. `listings` cannot
handle multi-byte UTF-8 in verbatim mode. The preamble maps the common offenders
and the Polish diacritics, but ASCII is safer.

**Underscores.** Python is full of them and `_` is a maths subscript in LaTeX.
Inside `\code{}`, `\api{}` and `\pkg{}` it must be written `\_`. This is the
single most common way to break the build. In a chapter title it additionally
needs `\texorpdfstring` for the PDF bookmark — see `ch07`.

**Voice.** British English, second person, senior audience. The book is allowed
to say the framework is the wrong tool, that the documentation is stale, that a
popular pattern is not worth its cost, and that the author has not verified
something. No marketing register. No "simply", no "just", no "powerful".

**Prefer measurements to assertions.** This is the book's differentiator. A
claim about what is faster, cheaper or more reliable needs a method and a number,
or an explicit label as judgement. Five experiments are specified; until each is
run, the claims it would support stay labelled as judgement.

**Two to four figures per chapter**, each teaching something. Prefer a Mermaid
diagram to a screenshot: it is text, it reviews as a diff, and it does not go
stale when a UI changes. Reserve `\needscreenshot` for things that genuinely
cannot be drawn — a trace waterfall, a Studio session, an evaluation report.

**Watch the margin.** The page is 17 cm wide and `\code{}` / `\api{}` /
`\pkg{}` do not hyphenate, so a long identifier at a line break runs into the
margin. `create_agent` is fine; `RemainingSteps` is fine;
`AsyncPostgresSaver.from_conn_string` is not — move lists of long names into a
displayed `itemize` or a table. Check with the counter in *After each pass*
below. Aim for nothing over ~15 pt.

**Count vboxes as well as hboxes.** `grep -c 'Overfull' main.log` lumps them
together. An overfull **vbox** means a `center`+`tabularx` block grew past a
page; those cannot break, so a long table next to an admonition overflows by
hundreds of points. The fix is to split the table, not to shrink the text.

---

## Structure

Five parts, seventeen chapters, six appendices.

| Part | Chapters |
|---|---|
| I — Foundations | 1 Landscape · 2 Python for the .NET Engineer · 3 Asynchronous Python · 4 Cancellation, Timeouts and Resilience |
| II — LangChain 1.x | 5 Models, Messages, Runnables · 6 Tools and Structured Output · 7 `create_agent` and Middleware |
| III — LangGraph | 8 StateGraph · 9 Persistence and Durability · 10 Interrupts, Time Travel, Streaming · 11 Multi-Agent Systems |
| IV — Production | 12 Context Engineering · 13 Serving Agents · 14 Observability, Evaluation, Testing · 15 Security, Cost, Deployment |
| V — Perspective | 16 Ecosystem and Criticism · 17 Capstone |
| Appendices | A Packages and Migration · B Cheat Sheet · C Troubleshooting · D Interview Prep · E Glossary and Sources · F Manifest |

**Each chapter's full brief lives in its own `.tex` file**, inside the
`\chapterstub{...}` block: the argument it must make, its sections, its planned
listings and diagrams, its mini-project stage, and which topics of the source
document it discharges. That is deliberate — the brief sits next to the work,
prints in the draft PDF so nobody mistakes a stub for a chapter, and disappears
the moment the chapter is written.

**Writing a chapter means: delete the `\chapterstub{}` block and replace it with
the chapter.** If a section in the brief turns out to be wrong once you have read
the source, change it and say so here under *Resolved questions*.

### Reading order constraints

- Chapter 4 assumes Chapter 3.
- Chapter 9 assumes Chapter 8.
- Chapter 17 assumes everything and introduces no new API.
- Everything else is independent enough to write out of order.

### Suggested writing order

Not chapter order. Write **1, 3, 8** first: they carry the three ideas the rest
of the book leans on (the inversion, the cold coroutine, the reducer), and every
later chapter cross-references them. Then **7 and 9**, which are the two most
substantial. Chapter 2 is easy to write and low-risk, so it is a good one to slot
in when the appetite for reading source is low. Chapter 17 must be last.

---

## The mini-project

`konradcinkusz/llm-book-mini-project` — **Ops Copilot**, an internal operations
assistant. FastAPI, LangGraph, Postgres. Built one stage per chapter.

| Stage | Chapter | Adds |
|---|---|---|
| 00 | 2 | Repository skeleton, `uv`, ruff/mypy/pytest, CI |
| 01 | 3, 4 | Concurrency playground; bounded queue; graceful shutdown |
| 02 | 5 | Streaming CLI chat, token and cost accounting |
| 03 | 6 | Five async tools with schemas; fake-model harness |
| 04 | 7 | `create_agent` with audit, PII, limits, approval middleware |
| 05 | 8 | Rebuilt as an explicit `StateGraph` with `Send` fan-out |
| 06 | 9 | `AsyncPostgresSaver`, store, idempotency key, retry/timeout |
| 07 | 10 | Approval gate, resume endpoint, time-travel endpoint, streaming |
| 08 | 11 | Supervisor variant and the comparison harness |
| 09 | 12 | Tool-result projection, summarisation, cache points, cost report |
| 10 | 13 | The FastAPI service: SSE, disconnects, rate limiting, per-thread lock |
| 11 | 14 | Tracing, twenty-case eval in CI, full test suite with no real model calls |
| 12 | 15 | Injection tests, tool authz, retention, budget cap, Docker, manifests |
| 13 | 16 | MCP adapter; the comparison write-ups |
| final | 17 | The complete service plus `DECISIONS.md` |

**The rule that keeps them honest:** every stage's tests pass without a single
real model call. A stage that needs a live provider to demonstrate anything has
been designed wrong.

Chapters reference stages through `\begin{projectbox}`. Listings that also exist
in the project should be pulled in with `\pyregion{}` against a `# --8<--`
delimited region rather than retyped, so the book and the running code cannot
drift.

---

## Measurement debt

Five experiments are specified in the chapters and **none has been run.** Each
one is the original data that distinguishes this book from the documentation.
Until an experiment runs, every claim it would support stays explicitly labelled
as judgement, and Appendix B's tables stay empty.

**Do not fill them with plausible numbers.**

| # | Chapter | Experiment | Cost |
|---|---|---|---|
| 1 | 3 §3.x | Sequential vs `gather` vs `TaskGroup` over 20 calls with fixed latency; median of 10 | Free — no provider needed |
| 2 | 13 | Concurrent conversations per process against p50/p95, with and without one blocking call | Free — mocked provider |
| 3 | 12 | Cost per conversation across four context strategies, plus cache hit rate; 10 conversations × 10 turns | Cheap |
| 4 | 6 | Tool-selection accuracy: 5 vs 20 tools × terse vs descriptive docstrings, 30 queries × 20 runs | Moderate |
| 5 | 11 | **The headline.** Single agent vs five topologies on one fixed task; turn count, token cost, latency, success rate; ≥20 runs each | Highest |

Do them in that order — 1 and 2 are free and 2 produces the most persuasive
graph in the book. For 4 and 5, **keep the raw event streams, not just the
summary rows**: Chapter 14 re-scores the same runs under an evaluation harness,
and re-running to recover traces is expensive.

---

## Diagrams

Mermaid. Source of truth is `figures/mermaid/<key>.mmd`, **committed**. Rendered
output is `figures/diagrams/<key>.pdf`, **gitignored** — it is build output, and
keeping it out means a diagram change reviews as a text diff.

```
make diagrams      # renders every .mmd
\mermaidfig{key}{caption}{one-line description for the manifest}
```

If the PDF is absent the macro prints a placeholder **and typesets the Mermaid
source**, so an unrendered build still shows the reader the structure. That is
why `make` (text-only) is safe to use while drafting.

**Verified working:** `mermaid-cli` v11 renders against the sandbox's
pre-installed Chromium. `make diagrams` writes `figures/mermaid/.puppeteer.json`
pointing at whatever browser it finds; override with `make diagrams BROWSER=...`.
`--pdfFit` crops the page to the diagram — without it you get a US-Letter page
with a small graph in the corner.

Four diagrams exist: `lc-lg-layering`, `lc-timeline`, `lc-package-map`,
`async-event-loop`. Chapter 1 references the first three.

**Theme.** `figures/mermaid/config.json` matches the book's palette. Use it
rather than styling inside each `.mmd`, so the diagrams stay a set.

---

## Build

```bash
make              # diagrams, then latexmk
make text-only    # skip diagram rendering while drafting
make debt         # all four debt ledgers
make watch        # rebuild on save
```

CI runs the diagram render and the LaTeX build as separate jobs, fails on any
unresolved cross-reference, and publishes the debt ledgers to the step summary.
A third job compares the pins against PyPI and is advisory only.

### Three build traps already hit and fixed

Each cost time; none is obvious from its error message.

- **A `literate` mapping for U+00A0 (non-breaking space) makes `listings` abort
  the run.** `Improper alphabetic constant`, fatal, no PDF, and the message names
  neither the character nor the line. It is the obvious next entry to add to the
  literate list and it must not be added. Every other mapping in that list —
  Polish diacritics, dashes, smart quotes, the degree sign — is fine; only the
  non-breaking space is poison. Note that **maf-book's preamble carries this
  mapping**, so it is presumably latent there too.

- **`babel` with a missing language is fatal, not a warning.** Loading
  `[polish]` on a TeX installation without `texlive-lang-polish` aborts the run
  with no PDF. The preamble now probes for `polish.ldf` and then `british.ldf`
  before requesting either. Do not simplify this back to a bare `\usepackage`.
- **`fancyhdr` overwrites `\chaptermark` at `\pagestyle{fancy}`.** Any
  redefinition must come *after* that line or it is silently discarded. The
  symptom is a running-head change that appears to do nothing.

And one layout fix worth keeping in mind when adding a chapter: chapter titles
are set `\raggedright`. Several titles here exceed 35 characters, and at `\Huge`
on a 13 cm block a justified title cannot break and overflows by 30 pt or more.
Adding a long-titled chapter without ragged-right will reintroduce that.

---

## Resolved questions

### Chapter 1 pass, August 2026

Verified against the installed packages at the pinned versions, plus PyPI
release metadata. **The brief was wrong about two things**, exactly as the
maf-book experience predicted.

**1. The 1.0 release date is 17 October 2025, not the 22nd.** PyPI upload times
put `langchain` 1.0.0, `langgraph` 1.0.0 and `langchain-classic` 1.0.0 all on
2025-10-17 — the same day, a coordinated release. The 22nd is the announcement.
The book uses upload dates throughout, because that is the date the installable
thing changed. **Corrected in `frontmatter/introduction.tex`, `README.md` and
`docs/index.html` as well as in the chapter.**

**2. `create_react_agent` is deprecated, not removed.** The brief listed it with
`AgentExecutor` and `LLMChain` as retired. It imports fine from
`langgraph.prebuilt`, still works, and carries a deprecation decorator against a
warning category named `LangGraphDeprecatedSinceV10`. Chapter 1 §1.2.4 now says
so and uses it as the chapter's worked example of why the package beats the
documentation.

**Confirmed, and now usable by later chapters:**

- **The dependency direction, from packaging metadata.** `langchain` requires
  `langchain-core<2.0.0,>=1.4.9` and `langgraph<1.3.0,>=1.2.5`. `langgraph`
  requires `langchain-core` and never mentions `langchain`. That is the
  inversion, stated by the build system.
- **`create_agent` returns `CompiledStateGraph`** — it is the declared return
  annotation, and at runtime the MRO is `CompiledStateGraph → Pregel →
  PregelProtocol → Runnable → ABC`. Nodes are `__start__`, `model`, `tools`,
  `__end__`. **This demo runs with a `GenericFakeChatModel` and needs no API
  key**, which makes it reusable anywhere in the book.
- **Node count is invariant** under adding tools or a system prompt, and under
  passing a checkpointer. A checkpointer changes `agent.checkpointer` and
  nothing in `get_graph()`. Both are Chapter 1 exercises and both were run.
- **`langchain` has 6 submodules; `langchain-classic` has 43.** `langchain.chains`,
  `.memory`, `.retrievers` and `.hub` do not exist — plain `ModuleNotFoundError`
  with no hint that `langchain-classic` is where they went. Worth remembering for
  Appendix A's migration section.
- **`langchain-classic` 1.0.8 really does carry the whole retired surface**
  working: `AgentExecutor`, `initialize_agent`, `create_react_agent`,
  `LLMChain`, `ConversationChain`, `RetrievalQA` all present.
- **Release cadence, Jan–Jul 2026:** `langchain-core` 49 stable releases,
  `langchain` 36, `langgraph` 27. None breaking. `deepagents` is still pre-1.0
  with 52 releases this year — it published one *while Chapter 1 was being
  written*, making the preamble pin one behind the same day. Chapter 1 uses that
  as an honest illustration; do not quietly fix the pin without also fixing the
  anecdote.

**Method note.** The scratch-venv route works well and should be the default:
`uv venv scratch && VIRTUAL_ENV=scratch uv pip install <pkg>==<pin>`, then read
or introspect. That is how `langchain-classic` was checked without adding it to
the mini-project's dependencies.

*(As each further chapter is written against the source, record here anything
that contradicted the brief — including contradictions of notes written during
an earlier pass.)*

### Verified at scaffolding time, August 2026

Pins in `preamble.tex`, all confirmed as the current release on PyPI:

| Package | Version |
|---|---|
| `langchain` | 1.3.14 |
| `langchain-core` | 1.5.3 |
| `langgraph` | 1.2.10 |
| `langgraph-checkpoint-postgres` | 3.1.1 |
| `langchain-classic` | 1.0.8 |
| `langchain-anthropic` | 1.5.3 |
| `langsmith` | 0.10.15 |
| `langchain-mcp-adapters` | 0.3.1 |
| `deepagents` | 0.7.3 |

`langchain` and `langchain-core` both declare `>=3.10,<4.0`; `langgraph`
declares `>=3.10`; `deepagents` declares `>=3.11`. So `\pymin` is correct at
3.10 for LangChain itself, but the book targets 3.13 and uses `TaskGroup` and
`asyncio.timeout` freely, both of which need 3.11.

**Not yet verified — do this before writing the chapter that needs it:**

- Whether event streaming `version="v3"` and the projection names in the source
  document (`stream.messages`, `.tool_calls`, `.subagents`, `.subgraphs`,
  `.extensions`) match the installed `langchain` 1.3.x. **Chapter 10 depends on
  this and the source document is the only evidence for it.** Check first.
- The exact middleware class names and their import path. The source document
  lists nine; confirm each exists and confirm the hook names.
- Whether `RetryPolicy`, node-level `timeout=`, `NodeTimeoutError`,
  `CachePolicy` and `RemainingSteps` are all present in `langgraph` 1.2.x and
  where they import from. These are Chapter 9's flagged gaps and none of them is
  attested anywhere except the source document.
- `ConversationSplitters`-equivalent and the evaluation surface for Chapter 14.
  The source is thin here.

---

## After each pass

1. `make diagrams && latexmk -pdf main.tex` — zero errors, zero unresolved refs
2. `make debt` — confirm the ledgers moved in the direction you expected
3. Update the Status table and the ledgers at the top of this file
4. Check the overfull count with the snippet below, comparing the *multiset of
   sizes* against a build with the change reverted. Line numbers shift, so a
   plain `diff` of the log is noise. Attributing boxes by reading `main.log`
   nesting does not work.

```bash
python3 - <<'PY'
import re
log = open('main.log', encoding='utf8', errors='replace').read()
h = [float(x) for x in re.findall(r'Overfull \\hbox \(([\d.]+)pt', log)]
v = [float(x) for x in re.findall(r'Overfull \\vbox \(([\d.]+)pt', log)]
print('pages:', re.search(r'Output written on main.pdf \((\d+) pages', log).group(1))
print('hbox:', len(h), sorted((round(x, 1) for x in h), reverse=True))
print('vbox:', len(v))
PY
```

5. Tag if it is a meaningful milestone: `git tag -a v0.1.0 -m "Chapter 1"`

**Note on tagging:** `git push --tags` returns HTTP 403 through the sandbox's
git proxy, so tags created in a Claude Code web session exist locally only and
are lost when the container is reclaimed. Tag from a local clone instead.
