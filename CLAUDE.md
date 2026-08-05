# CLAUDE.md — working on this book

Context for continuing *LangChain, LangGraph and Async Python*.
Read this before touching a chapter.

---

## Status

| | Done | Remaining |
|---|---|---|
| Structure | main.tex, preamble, build, CI, mermaid pipeline | — |
| Front matter | Title page, Introduction | — |
| Chapters | **1–17, all drafted** | — |
| Appendices | **A–F, all drafted** | — |

Build is clean: `latexmk -pdf main.tex` returns 0, **241 pages**, **zero
unresolved references**, **21 overfull hboxes, none above 15 pt**, **zero
overfull vboxes**.

**A full draft exists.** Every chapter and appendix is written. What remains is
finishing, not drafting — see *What is left* at the bottom.

**Debt ledgers, reported by CI on every build:**
- 0 chapters and appendices outstanding — `make stubs` prints nothing
- 1 screenshot outstanding: `studio-multi-agent`
- **0 `verifybox` blocks.** Every listing in the written chapters was executed
  against the pinned versions, so none needed one. Keep it that way.
- 45 Mermaid sources; all render

**Measurement: 3½ of 5 experiments run**, all without a provider. Experiments 1
(Ch. 3), 2 (Ch. 13) and the token half of 3 (Ch. 12), plus the structural half of
5 (Ch. 11). The three outstanding pieces all need a provider budget. See
*Measurement debt* below.

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

Five experiments are specified in the chapters. **One has been run.** Each is
the original data that distinguishes this book from the documentation. Until an
experiment runs, every claim it would support stays explicitly labelled as
judgement, and Appendix B's tables stay empty.

**Do not fill them with plausible numbers.**

| # | Chapter | Experiment | Cost | State |
|---|---|---|---|---|
| 1 | 3 §3.5 | Sequential vs `gather` vs `TaskGroup` vs capped, 20 calls over real sockets; median of 10 | Free | **DONE** |
| 2 | 13 | Concurrent conversations per process against p50/p95, with and without one blocking call | Free — mocked provider | **DONE** |
| 3 | 12 | Cost per conversation across four context strategies, plus cache hit rate | Cheap | **token half DONE**; cache hit rate needs a provider |
| 4 | 6 | Tool-selection accuracy: 5 vs 20 tools × terse vs descriptive docstrings, 30 queries × 20 runs | Moderate | not run |
| 5 | 11 | **The headline.** Single agent vs five topologies on one fixed task; turn count, token cost, latency, success rate; ≥20 runs each | Highest | **structural half DONE**, quality half not run |

Do the rest in that order — 2 is free and produces the most persuasive graph in
the book. For 4 and 5, **keep the raw event streams, not just the summary
rows**: Chapter 14 re-scores the same runs under an evaluation harness, and
re-running to recover traces is expensive.

### Experiment 3, token half — run, August 2026

Script: `code/ch12/context_cost.py`. Ten turns, one tool call each, a realistic
~40-field incident payload, tokens counted with `count_tokens_approximately`.
No provider; under a second.

| Strategy | Billed tokens | vs naive | Final context | Summaries |
|---|---|---|---|---|
| naive | 43,510 | 1.00× | 4,350 | 0 |
| projected | 6,910 | **0.16×** | 690 | 0 |
| summarised | 28,180 | 0.65× | 1,795 | 1 |
| both | 6,910 | 0.16× | 690 | 0 |

**Projecting tool results cut the bill 84%; summarising history cut 35%.** The
technique everyone writes about is worth less than half the one almost nobody
applies — which is the chapter's whole thesis, and it is now measured rather
than asserted.

**"Both" is identical to "projected", to the token**, because with projection
the conversation never reaches the summarisation threshold at all. Fix the
dominant consumer and the second technique becomes unnecessary.

Two honest caveats, both in the chapter: the ratio depends on the tool returning
a fat payload (a lean tool has nothing to project), and the summarised rows are
flattered because the script does not charge for the summarisation call.

**Not measured: cache hit rate.** That needs a real provider's usage reporting.
The §12.5 material on prefix matching is therefore mechanism and judgement, not
measurement.

Corroborating detail worth keeping: the in-box context-editing middleware's only
built-in edit type is `ClearToolUsesEdit` — the library's own default remedy
targets tool output rather than history.

### Experiment 2 — run, August 2026

Script: `code/ch13/bench_service.py`. FastAPI under uvicorn **in a separate
process**, driven over real HTTP, provider mocked at 100 ms. 400 requests per
cell.

| Conc. | Mode | p50 | p95 | Throughput |
|---|---|---|---|---|
| 1 | clean | 103 ms | 104 ms | 10/s |
| 10 | clean | 102 ms | 108 ms | 97/s |
| 20 | clean | 103 ms | 110 ms | 190/s |
| 40 | clean | 103 ms | 159 ms | 349/s |
| 40 | blocking | 164 ms | 329 ms | 194/s |
| 40 | threaded | 102 ms | 197 ms | 332/s |

**Latency flat, throughput linear** — 1 → 40 concurrent, p50 unmoved at ~103 ms,
throughput 10 → 349/s in one process. **One request in twenty blocking cost 44%
of throughput**, raised p50 60%, and degraded the nineteen innocent requests.
`to_thread` recovered nearly all of it.

**Two methodological errors, both instructive and both written into the chapter.**
The first version ran uvicorn and the load driver on one event loop, so the
driver inflated the server's latency and the clean baseline degraded for no
reason. The second put the server in its own process but pushed concurrency to
100, where the *client* saturated — producing the tell-tale absurdity of the
blocking scenario out-throughputting the clean one. The script now calibrates
against a no-op endpoint and flags any cell within half its own ceiling. Do this
for any future load test in this book.

### Experiment 1 — run, August 2026

Script: `code/ch03/bench_concurrency.py`. Reproducible in about thirty seconds
on any machine, no provider needed. Twenty requests against a hand-rolled
localhost HTTP server with a fixed 100 ms delay, one warm-up trial discarded,
median of ten timed trials.

| Strategy | Median | Min | Max | Round trips |
|---|---|---|---|---|
| Sequential | 2.039 s | 2.037 | 2.041 | 20.4× |
| `gather` | 0.126 s | 0.124 | 0.132 | 1.3× |
| `TaskGroup` | 0.125 s | 0.124 | 0.128 | 1.2× |
| Capped at 5 | 0.421 s | 0.420 | 0.424 | 4.2× |

**16× from sequential to concurrent.** `gather` and `TaskGroup` are
indistinguishable on speed (0.126 vs 0.125 s), so that choice is always about
failure semantics and never about performance — worth repeating wherever it
comes up. The capped run landed at 4.2 round trips against a theoretical floor
of 4, i.e. the cap sets the ceiling almost exactly.

Two supporting measurements were taken in the same pass and are also in
Chapter 3:

- **GIL.** Four CPU-bound units, one unit alone = 0.29 s. Four threads: 1.09 s
  (3.7×, essentially serialised). Four processes: 0.29 s (1.0×, parallel) on
  four cores.
- **One blocking call.** Ten healthy coroutines awaiting 50 ms each. Worst
  healthy request: 50.3 ms clean, **500.4 ms** with one blocking offender,
  50.9 ms with the offender wrapped in `to_thread`. A 10× degradation with no
  error and no log line.

Note the measurement is on `localhost`, so the spread is unrealistically tight.
The ratios are structural and transferable; the absolute numbers are not.

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

Thirty diagrams exist. Chapter 1 uses `lc-lg-layering`, `lc-timeline`,
`lc-package-map`; Chapter 3 uses `async-event-loop`, `async-cold-coroutine`,
`async-gather-vs-taskgroup`, `async-blocking-call`; Chapter 8 uses
`lg-superstep`, `lg-reducer-merge`, `lg-send-fanout`, `lg-state-context-config`;
Chapter 9 uses `lg-replay-boundary`, `lg-checkpointer-vs-store`,
`lg-durability-modes`; Chapter 10 uses `hitl-interrupt-resume`, `lg-time-travel`,
`stream-projections`, `double-texting-policies`; Chapter 7 uses `agent-loop`,
`middleware-order`, `middleware-aspnet`; Chapter 11 uses `ma-topologies`,
`ma-supervisor-turns`, `ma-handoff-loop`; Chapter 13 uses `svc-architecture`,
`svc-thread-lock`, `svc-sse-flow`; Chapter 12 uses `ctx-window-budget`,
`ctx-compaction`, `ctx-cache-points`.

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

### Chapter 3 pass, August 2026

Everything in the chapter was measured or executed rather than asserted. **The
brief was wrong about one thing and imprecise about another.**

**1. `create_task` does not start the coroutine.** The brief, following the
source document, described it as "start immediately, in the background". It
schedules. The body does not execute until the current coroutine yields, which
is observable: after `create_task` and before any `await`, a side effect on the
first line of the body has not happened. §3.3.1 measures it and states the
distinction, because it changes how you reason about ordering.

**2. `TaskGroup` and `gather` are identical on speed.** The brief implied
`TaskGroup` was the modern-and-therefore-better option. Measured at 0.125 vs
0.126 s over twenty requests, the difference does not exist. The case for
`TaskGroup` is entirely about failure semantics, and the chapter was rewritten
to make that the *only* argument. Anyone recommending it for performance is
recommending it on a difference that is not there.

**Confirmed by execution, reusable later:**

- `gather` genuinely orphans siblings — the slow sibling logs `finished` *after*
  the caller's `except` block has run. `TaskGroup` cancels it. Demonstrated with
  a log-ordering test, which is the clearest way to show it.
- `as_completed` yields in completion order (`fast`, `mid`, `slow` for
  0.05/0.15/0.3 s).
- `Queue(maxsize=n)` blocks the producer when full — verified with
  `wait_for(q.put(...), timeout=...)` raising `TimeoutError`.
- The blocking-call demonstration is cheap and extremely persuasive; a version
  of it belongs in Chapter 13's service-level experiment too, at which point the
  two should cross-reference rather than duplicate.

**Method note.** The benchmark uses a real localhost HTTP server rather than
`asyncio.sleep` on the client side. That was a deliberate choice and it is worth
keeping: sleeping demonstrates the scheduler can schedule and says nothing about
sockets, and a reviewer will notice.

### Chapter 8 pass, August 2026

Verified by running every listing against `langgraph` 1.2.10. **Two findings that
were not in the brief, and both are chapter-grade material.**

**1. A `Command`-returning node without a return annotation draws the wrong
graph.** `def router(s) -> Command:` yields edges `(__start__, router)`,
`(router, __end__)` — the edge to the actual destination is **missing**.
`def router(s) -> Command[Literal["billing"]]:` yields the correct three edges.
Both execute identically; only the visualisation differs. §8.6.1 has this as a
warning. Rule: always annotate the return type of a node returning a `Command`.

**2. An append-only reducer shared across a subgraph boundary duplicates the
parent's content.** Parent writes `['parent']`, child appends `['sub']`, result
is `['parent', 'parent', 'sub']`. Mechanism: the subgraph is invoked with the
parent's state, so its accumulator already contains the parent's entries; its
*final* value is then merged back through `operator.add`, which appends the lot.
`add_messages` is immune because it merges by id. §8.8.1 has this, and it
retroactively explains why `add_messages` is id-keyed rather than a plain append
— worth reusing in Chapter 9 when replay comes up.

**Confirmed, and reusable:**

- **Supersteps, demonstrated.** Two nodes from `START` both read `counter=0`; a
  third node one step later reads `2`. `stream_mode="updates"` emits one dict per
  node with clear step grouping. This is the clearest superstep demo available
  and costs nothing to run.
- **The exact error text:** `InvalidUpdateError: At key 'value': Can receive only
  one value per step. Use an Annotated key to handle multiple values.` A reduced
  key in the same graph merges fine — the error names the offending key.
- **`add_messages` does three things:** appends; **replaces** when the id matches;
  deletes on `RemoveMessage`. Messages without an id get one assigned.
- **`StateGraph.__init__` is `(state_schema, context_schema, input_schema,
  output_schema)`.** Note `input_schema`/`output_schema`, not the older
  `input=`/`output=`. `compile()` takes `checkpointer, cache, store,
  interrupt_before, interrupt_after, debug, name, transformers`.
- **Output schema filters the returned dict; input schema does not validate.**
  Passing an unknown input key is accepted without error.
- **`Runtime[Ctx]` as a second node parameter**, with `context=` on invoke.
  `Runtime` also carries `store`, `stream_writer`, `previous`, `control`.
  This supersedes the source document's config-based context entirely.
- **`stream(..., subgraphs=True)`** yields `(namespace_tuple, update)` and is the
  first tool to reach for when a composed graph misbehaves.

### Chapter 9 pass, August 2026

**The source document was right about every one of Chapter 9's flagged gaps.**
`RetryPolicy`, `CachePolicy`, `NodeTimeoutError`, `GraphRecursionError` and
`RemainingSteps` all exist at the pinned version. Import paths:
`langgraph.types` for the policies, `langgraph.errors` for the exceptions,
`langgraph.managed` for `RemainingSteps`. Those items are now struck from the
not-yet-verified list above. This is the first pass where the brief was not
wrong about anything — worth noting, because it was wrong on the previous three.

**One constraint that is chapter-grade and is documented nowhere else.** Node
`timeout=` **only works on async nodes.** A sync node raises at run time:

> `ValueError: Node timeouts are only supported for async nodes because sync
> Python execution cannot be safely cancelled in-process. Node 'slow' is sync.`

Async gives the expected `NodeTimeoutError: Node 'slow' exceeded its run timeout
of 0.100s (elapsed: 0.101s).` This is the best error message in the library — it
explains its own reasoning — and it is a concrete, enforced justification for the
book's "async all the way down" convention. Reuse it in Chapter 13.

**The replay demonstration works and is the chapter's centrepiece.** Crash a node
after its side effect, resume, and the email is sent twice while the state log
shows one send — the checkpoint protected the state, nothing protected the world.
`nodes run: ['draft', 'send_email', 'send_email']` proves only the failed node
replays. Both halves (broken and fixed) run in-process with `InMemorySaver` and
no provider, so they are cheap to re-run and reusable in Chapter 14's testing
material.

**Confirmed, and reusable:**

- `add_node` takes more than the brief listed: `defer`, `error_handler`,
  `destinations`, `input_schema`, `metadata`, alongside `retry_policy`,
  `cache_policy` and `timeout`. `destinations=` is a second way to declare a
  `Command` node's targets — an alternative to Chapter 8's return annotation,
  worth mentioning if that section is ever revised.
- `Durability = Literal['sync','async','exit']`, and it is a per-invocation
  argument on both `invoke` and `stream`.
- `RetryPolicy` defaults: `max_attempts=3`, `initial_interval=0.5`,
  `backoff_factor=2.0`, `max_interval=128.0`, `jitter=True`.
- `CachePolicy(key_func, ttl)` needs a cache passed to `compile()` as well; a
  policy with no cache configured does nothing, silently.
- Missing `thread_id` raises `ValueError: Checkpointer requires one or more of
  the following 'configurable' keys: thread_id, checkpoint_ns, checkpoint_id`.
- `StateSnapshot` fields are `values, next, config, metadata, created_at,
  parent_config, tasks, interrupts` — **Chapter 10 needs this** for time travel.
- Store API is `get/put/search/delete/list_namespaces` plus async twins.
  Namespace tuples isolate correctly; a different second element sees nothing.
- `AsyncPostgresSaver` is in `langgraph.checkpoint.postgres.aio`. SQLite is a
  separate distribution and is not installed in the mini-project.

### Chapter 10 pass, August 2026

**The v3 streaming question is settled, and the source document was right but
incomplete.** All seven projections it named exist — `messages`, `tool_calls`,
`values`, `output`, `subagents`, `subgraphs`, `extensions` — plus four it did
not: **`lifecycle`, `interrupted`, `interrupts`, `abort`**. The interrupt
projections matter: an approval prompt arrives on the same stream as the tokens,
which is what ties this chapter together. Struck from the not-yet-verified list.

**v3 is opt-in and experimental.** `version` still defaults to `"v2"`. Passing
`"v3"` returns an `AsyncGraphRunStream` (`langgraph.stream.run_stream`) and
raises `LangChainBetaWarning: The v3 streaming protocol on Pregel is
experimental`. `stream_mode` and `subgraphs` are rejected with `TypeError` under
v3 — v3 owns them. §10.6 has a versionbox.

**`ToolCallStream` attributes are mutating, not awaitables.** From
`langgraph.prebuilt._tool_call_stream`. `tool_name`, `tool_call_id` and `input`
are available immediately; `output` is `None` and `completed` is `False` until
you iterate `output_deltas` to exhaustion, after which `output` becomes a
`ToolMessage`. `await call.output` raises `TypeError: object NoneType can't be
used in 'await' expression` and `await call.completed` the same about `bool` —
both are the natural first guess and both are wrong. Written up as a warning
because a reader will hit it.

**The interrupt re-execution trap is real and now measured.** Code before
`interrupt()` **in the same node** ran twice; code after it ran once. A node
*before* the gate ran once — its checkpoint held. So the hazard is confined to
the node containing the call, which makes the fix precise: prepare, gate and act
in three separate nodes.

**`update_state` forks, but the fork becomes the thread head.** History grows
(5 → 6 snapshots), the original tip stays readable by `checkpoint_id`, but
`get_state({"thread_id": ...})` afterwards returns the branch. Capture the
original checkpoint id before forking if you want it back.

**Blocking finding for the mini-project: no in-box fake chat model implements
`bind_tools`.** `GenericFakeChatModel`, `FakeListChatModel`,
`FakeMessagesListChatModel`, `ParrotFakeChatModel` — none of them. So none can be
used inside a `create_agent` that has tools; it raises `NotImplementedError` at
the model node. The fix is a five-line subclass of `FakeMessagesListChatModel`
overriding `bind_tools` to return `self`. **Stage 03's harness must do this**, and
every streaming test depends on it. Also note `GenericFakeChatModel` streams from
`content`, so a tool-call message with empty content raises `RuntimeError: v2
stream finished without producing a message` — base the harness on
`FakeMessagesListChatModel` instead.

**Confirmed:** `StreamMode = Literal['values','updates','checkpoints','tasks',
'debug','messages','custom']` — the seven the source document listed.
`__interrupt__` is the reserved key in the returned dict, carrying
`Interrupt(value=..., id=...)`. `runtime.stream_writer(...)` emits custom events.

### Chapter 7 pass, August 2026

**The last scaffolding-time unknown is resolved.** Every middleware class the
source document named exists in `langchain.agents.middleware`, and there are
**sixteen** in total — seven more than it listed: `ModelRetryMiddleware`,
`ToolRetryMiddleware`, `ToolErrorMiddleware`, `TodoListMiddleware`,
`ShellToolMiddleware`, `FilesystemFileSearchMiddleware`,
`ProviderToolSearchMiddleware`. All six hook names confirmed on
`AgentMiddleware`, each with an `a`-prefixed async twin the source document did
not mention. There is also a lowercase decorator for each hook plus
`dynamic_prompt` and `hook_config`.

**Hook ordering, measured — this is the chapter's centrepiece.** With
`middleware=[A, B]`:

| Hook family | Order |
|---|---|
| `before_*` | declaration order — A, then B |
| `wrap_*` | nested, first-declared outermost — A wraps B wraps the call |
| `after_*` | **reverse** declaration order — B, then A |

Agent-level hooks run once per run; model-level hooks run once per iteration.
Exactly ASP.NET Core pipeline semantics, and the `after_*` reversal is the part
people get wrong. Reuse this table in Appendix B.

**Three signature corrections — the source document was wrong on two.**

- `ModelCallLimitMiddleware` has **no `limit=` parameter**. It is
  `(thread_limit=None, run_limit=None, exit_behavior='end')`, at least one limit
  required, and `exit_behavior` is `'end'` or `'error'`. The source document's
  `ModelCallLimitMiddleware(limit=15)` does not work.
- `SummarizationMiddleware` has **no `max_tokens_before_summary`**. It is
  `(model, trigger=None, keep=('messages', 20), ...)` where `trigger` takes
  `("tokens", N)`, `("messages", N)` or `("fraction", 0.8)`; a list is OR, a
  dict is AND. Far more expressive than a single number, and `("fraction", ...)`
  survives a model change.
- `PIIMiddleware(pii_type, strategy='redact', detector=None, apply_to_input=True,
  apply_to_output=False, apply_to_tool_results=False)`. The source document's
  call form is right, but note the defaults: **input only**. Data flowing out of
  a tool into the provider's context is not covered unless you ask.

**Composition confirmed, twice.** An agent with a middleware stack still has
exactly four nodes — `['__start__','model','tools','__end__']` — so middleware
adds none; hooks run inside the existing nodes. And a compiled agent drops into a
larger `StateGraph` as a single node and runs. That is Chapter 11's foundation:
topologies built out of agents rather than bespoke plumbing.

### Chapter 11 pass, August 2026

**Experiment 5 was split in two, and half of it is now done.** The brief treated
the multi-agent comparison as one expensive experiment. It is really two, and
only one needs a provider:

- **Structural cost** — model calls per run and context carried per call — is a
  property of the topology, not the model. A counting fake gives exactly the
  answer a real provider would, in under a second, for nothing. **Run**;
  `code/ch11/structural_cost.py`.
- **Quality** — whether a supervisor answers better — needs a real model on a
  real task. **Still outstanding.**

Keeping them apart is worth more than either alone, because it lets the chapter
state the cost as fact while labelling the benefit as judgement.

| Topology | Model calls | Context chars | vs baseline |
|---|---|---|---|
| Single agent | 2 | 172 | 1.0× |
| Pipeline (3) | 3 | 243 | 1.4× |
| Swarm (3 hops) | 3 | 240 | 1.4× |
| Orchestrator + 3 | 5 | 393 | 2.3× |
| Supervisor (2) | 5 | 487 | 2.8× |

**Model calls is a hard number** (topology-determined; a real provider makes the
same count). **Context chars is indicative** — it depends on scripted reply
lengths. Say so wherever it is quoted; do not let the 2.8× become folklore.

The explainable finding: supervisor and orchestrator make the same five calls,
but the supervisor carries more context, because every router turn re-reads the
whole accumulating conversation while an orchestrator's workers each see only
their slice. And **three of a supervisor's five calls are routing rather than
work** — the sentence worth remembering from this chapter.

**Confirmed:**

- `langgraph-supervisor` and `langgraph-swarm` are **separate distributions and
  are not installed**. Topologies here are hand-built from `StateGraph` +
  `Command`, which suits the book — it shows the mechanism rather than a wrapper.
- `Command.PARENT` handoff from inside a subgraph to a sibling of the parent
  works as documented.
- `@entrypoint` / `@task` return a `Pregel`, so `get_state` works and
  checkpointing/interrupts/streaming all apply. `@task` takes the same
  `retry_policy`, `cache_policy` and `timeout` as a node.

**Reusable:** the `MeteredFakeModel` in the harness — a fake that records call
count and context size before answering from a script — is the seed of the
mini-project's stage 08 comparison harness and belongs in CI, since it needs no
provider.

### Chapter 13 pass, August 2026

**Experiment 2 is done** — see *Measurement debt* above for the numbers and for
the two methodological errors that produced them, which are worth re-reading
before running experiments 3 or 4.

**The concurrent-thread hazard is sharper than the brief said.** The brief
described "interleaved state, corrupted thread". Measured with two concurrent
`ainvoke` calls on one `thread_id`, what actually happens is that **one request
vanishes entirely**:

```
UNLOCKED:  req-2, A saw 1 messages, B saw 2 messages      <- req-1 is gone
LOCKED:    req-1, A saw 1, B saw 2, req-2, A saw 4, B saw 5
```

Both runs load the same checkpoint, both run, last writer wins. No error, no log
line. "One user's message and the entire response to it disappeared" is both more
accurate and more alarming than "interleaved", and §13.5 says it that way.

**Reusable:** the demonstration is free (`InMemorySaver`, two `ainvoke` calls
under `gather`) and belongs in the mini-project's CI. It is the test most
implementations lack.

### Chapter 12 pass, August 2026

The brief was right that this was the source document's largest gap and right
about the thesis. What it could not supply was the number, and the number turned
out to be larger than expected: **84% against 35%**. See *Measurement debt*.

**Verified:** `ContextEditingMiddleware(edits=..., token_count_method=...)` with
`ClearToolUsesEdit(trigger=100000, clear_at_least=0, keep=3,
clear_tool_inputs=False, exclude_tools=(), placeholder='[cleared]')`.
`count_tokens_approximately` is in `langchain_core.messages.utils` and takes
`chars_per_token`, `extra_tokens_per_message` and a `tools=` argument — so tool
definitions can be priced too, which §12.7 uses.

**§12.6 (degradation over long context) carries no measurement and says so.**
Measuring positional attention properly needs a provider, a checkable task and
enough runs to beat variance, and the answer would be specific to one model
version. The structural advice holds regardless; the numbers commonly quoted for
this do not.

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


---

## What is left

**All seventeen chapters and six appendices are drafted.** There are no stubs.
The remaining work is finishing, in rough priority order:

1. **The three provider-dependent measurements.** Multi-agent answer quality
   (Ch. 11), tool-selection accuracy against tool count (Ch. 6), and cache hit
   rate (Ch. 12). All are specified; all need a budget and a few hours. Until
   they run, Appendix B's tables for them stay empty and every claim resting on
   them stays labelled as judgement.
2. **The mini-project.** Seventeen chapters of contracts and zero implemented
   stages. Stage 00's tests pass; everything else is a README stating what must
   be built. This is now the largest single body of outstanding work.
3. **One screenshot**: `studio-multi-agent`.
4. **An index pass.** The book has `\index{}` entries throughout but no
   dedicated pass; maf-book's experience was that this roughly quintuples the
   entry count and is worth a session of its own. Note its two hard limits:
   verbatim entries must stay under about 29 characters or they overflow the
   two-column index, and package names never fit.
5. **A consistency pass.** Written chapter-by-chapter over several sessions, so
   the appendices were drafted last and may disagree with chapters in places.
   maf-book found two outright errors this way.
6. Optional: a further-reading section; a glossary of the English terms alone,
   for readers who do not need the Polish column.

**Do not fill Appendix B's empty tables with plausible numbers.** They are empty
on purpose and the emptiness is load-bearing.
