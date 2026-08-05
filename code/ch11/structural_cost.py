"""Structural token overhead of five multi-agent topologies, measured.

This measures the half of the multi-agent cost question that does NOT need a
model provider: how many model calls each topology makes, and how much context
each call carries. Those are properties of the topology, not of the model, so a
counting fake gives exactly the same answer a real provider would -- for a
fraction of a penny and in under a second.

What it deliberately does NOT measure is quality: whether a supervisor actually
answers better than a single agent. That needs a real model on a real task and
is Chapter 11's outstanding experiment. Keep the two apart. A topology that
costs 4x is not thereby worse; it is 4x, and the question is what you bought.

    python structural_cost.py
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Any

from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


# --8<-- [start:meter]
@dataclass
class Meter:
    """Counts what a topology asks of the model."""

    calls: int = 0
    context_chars: int = 0
    per_call: list[int] = field(default_factory=list)

    def record(self, messages: list[BaseMessage]) -> None:
        chars = sum(len(str(m.content)) for m in messages)
        self.calls += 1
        self.context_chars += chars
        self.per_call.append(chars)


class MeteredFakeModel(FakeMessagesListChatModel):
    """A fake model that records every call before answering from a script."""

    meter: Any = None

    def bind_tools(self, tools: Any, **kwargs: Any) -> Runnable:
        return self  # no in-box fake implements this; see Chapter 10

    def _generate(self, messages: list[BaseMessage], *args: Any, **kwargs: Any):
        self.meter.record(messages)
        return super()._generate(messages, *args, **kwargs)
# --8<-- [end:meter]


class S(TypedDict):
    messages: Annotated[list, operator.add]
    trail: Annotated[list, operator.add]


ANSWER = "The Madrid region shows 3 open incidents; the oldest is INC-4471."
QUESTION = "Summarise open incidents for the Madrid region and flag the oldest."


def model_with(meter: Meter, replies: list[str]) -> MeteredFakeModel:
    m = MeteredFakeModel(responses=[AIMessage(content=r) for r in replies])
    m.meter = meter
    return m


def agent_node(name: str, model: MeteredFakeModel):
    """A worker: reads the running conversation, appends one reply."""

    def node(state: S) -> dict:
        reply = model.invoke(state["messages"])
        return {"messages": [reply], "trail": [name]}

    return node


# --------------------------------------------------------------------------
# The topologies. Each answers the same question.
# --------------------------------------------------------------------------
def single_agent(meter: Meter):
    """One agent, one tool round trip, then the answer. The baseline."""
    m = model_with(meter, ["(calls incident tool)", ANSWER])
    g = StateGraph(S)
    g.add_node("agent", agent_node("agent", m))
    g.add_node("tools", lambda s: {"messages": [HumanMessage(content="tool: 3 incidents")],
                                   "trail": ["tools"]})
    g.add_edge(START, "agent")
    g.add_edge("agent", "tools")
    g.add_node("agent2", agent_node("agent", m))
    g.add_edge("tools", "agent2")
    g.add_edge("agent2", END)
    return g.compile()


def pipeline(meter: Meter, stages: int = 3):
    """Fixed sequence. No routing model call at all -- the cheapest topology."""
    m = model_with(meter, [f"stage {i} output" for i in range(stages - 1)] + [ANSWER])
    g = StateGraph(S)
    prev = START
    for i in range(stages):
        name = f"stage{i}"
        g.add_node(name, agent_node(name, m))
        g.add_edge(prev, name)
        prev = name
    g.add_edge(prev, END)
    return g.compile()


def supervisor(meter: Meter, workers: int = 2):
    """Router model call before AND after each worker. The expensive one."""
    replies: list[str] = []
    for i in range(workers):
        replies += [f"route to worker{i}", f"worker{i} result"]
    replies.append(ANSWER)
    m = model_with(meter, replies)

    g = StateGraph(S)
    g.add_node("supervisor", agent_node("supervisor", m))
    for i in range(workers):
        g.add_node(f"worker{i}", agent_node(f"worker{i}", m))
    g.add_edge(START, "supervisor")

    order = [f"worker{i}" for i in range(workers)]

    def route(state: S) -> str:
        done = [t for t in state["trail"] if t.startswith("worker")]
        return order[len(done)] if len(done) < len(order) else END

    g.add_conditional_edges("supervisor", route, order + [END])
    for i in range(workers):
        g.add_edge(f"worker{i}", "supervisor")
    return g.compile()


def swarm(meter: Meter, hops: int = 2):
    """Direct handoffs. No router turn between agents -- cheaper than supervisor."""
    m = model_with(meter, [f"handing off {i}" for i in range(hops)] + [ANSWER])
    g = StateGraph(S)
    names = [f"agent{i}" for i in range(hops + 1)]
    for n in names:
        g.add_node(n, agent_node(n, m))
    g.add_edge(START, names[0])
    for a, b in zip(names, names[1:]):
        g.add_edge(a, b)
    g.add_edge(names[-1], END)
    return g.compile()


def orchestrator_worker(meter: Meter, fan: int = 3):
    """Plan, fan out in parallel, synthesise. Parallel work, serial context."""
    m = model_with(meter, ["plan"] + [f"doc {i} analysed" for i in range(fan)] + [ANSWER])
    g = StateGraph(S)
    g.add_node("plan", agent_node("plan", m))
    for i in range(fan):
        g.add_node(f"w{i}", agent_node(f"w{i}", m))
    g.add_node("synth", agent_node("synth", m))
    g.add_edge(START, "plan")
    for i in range(fan):
        g.add_edge("plan", f"w{i}")
        g.add_edge(f"w{i}", "synth")
    g.add_edge("synth", END)
    return g.compile()


def main() -> None:
    topologies = [
        ("single agent", single_agent),
        ("pipeline (3)", pipeline),
        ("swarm (3 hops)", swarm),
        ("orchestrator+3", orchestrator_worker),
        ("supervisor (2)", supervisor),
    ]
    rows = []
    for name, build in topologies:
        meter = Meter()
        graph = build(meter)
        graph.invoke({"messages": [HumanMessage(content=QUESTION)], "trail": []})
        rows.append((name, meter))

    base = rows[0][1]
    print(f"Task: {QUESTION!r}\n")
    print(f"{'topology':<18}{'model calls':>12}{'context chars':>15}{'vs baseline':>13}")
    print("-" * 58)
    for name, m in rows:
        ratio = m.context_chars / base.context_chars if base.context_chars else 1.0
        print(f"{name:<18}{m.calls:>12}{m.context_chars:>15}{ratio:>12.1f}x")
    print(
        "\nContext chars = total characters sent to the model across all calls."
        "\nA proxy for token cost that is exact for a fixed script, and is a"
        "\nproperty of the TOPOLOGY rather than of the model."
    )


if __name__ == "__main__":
    main()
