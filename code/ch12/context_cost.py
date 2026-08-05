"""What four context strategies cost over a ten-turn conversation.

Cost is linear in input tokens, so measuring tokens IS measuring cost up to a
price-per-token multiplier that varies by provider and changes monthly. This
script measures the tokens -- deterministically, with no provider, in under a
second -- and leaves the multiplication to you.

The point it exists to test is Chapter 12's claim that TOOL RESULTS rather than
conversation history dominate a working agent's context. Every agent tutorial
trims history; almost none trims tool output.

Four strategies over the same scripted conversation:

  naive       everything accumulates
  projected   tool results reduced to the fields the model needs
  summarised  history compacted once it crosses a threshold
  both        projection and summarisation together

    python context_cost.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.messages.utils import count_tokens_approximately

# --8<-- [start:params]
TURNS = 10
SUMMARISE_AT = 3000  # tokens of history before compaction
KEEP_RECENT = 4  # messages left untouched by summarisation
# --8<-- [end:params]


def fat_tool_result(incident_id: int) -> str:
    """What an API actually returns: forty fields, three of them useful.

    This is not a strawman. It is the shape of a real incident-management or
    order API response, and returning it verbatim is the default behaviour of
    a tool written the obvious way.
    """
    return json.dumps({
        "id": f"INC-{4400 + incident_id}",
        "title": f"Elevated error rate in service-{incident_id}",
        "status": "open",
        "severity": "sev2",
        "created_at": "2026-08-01T09:14:22.184Z",
        "updated_at": "2026-08-04T11:02:07.551Z",
        "acknowledged_at": "2026-08-01T09:19:03.221Z",
        "region": "eu-west-1",
        "cluster": f"prod-{incident_id}",
        "namespace": "payments",
        "assignee": {"id": "u-8821", "name": "A. Engineer",
                     "email": "a.engineer@example.com", "team": "payments-oncall",
                     "escalation_policy": "ep-primary-payments"},
        "reporter": {"id": "u-1042", "name": "Monitoring",
                     "email": "noreply@example.com", "team": "platform"},
        "tags": ["payments", "latency", "sev2", "customer-visible", "eu"],
        "linked_alerts": [f"alert-{i}" for i in range(12)],
        "runbook_url": "https://internal.example.com/runbooks/payments-latency",
        "dashboard_url": "https://grafana.example.com/d/abc123/payments",
        "timeline": [
            {"at": "2026-08-01T09:14:22Z", "by": "monitoring", "text": "Alert fired"},
            {"at": "2026-08-01T09:19:03Z", "by": "a.engineer", "text": "Acknowledged"},
            {"at": "2026-08-02T14:30:00Z", "by": "a.engineer",
             "text": "Rolled back deploy 8821, error rate partially recovered"},
            {"at": "2026-08-03T08:05:12Z", "by": "b.engineer",
             "text": "Root cause looks like connection pool exhaustion"},
        ],
        "metrics_snapshot": {f"p{p}": 120 + p for p in (50, 75, 90, 95, 99)},
        "related_incidents": [f"INC-{4300 + i}" for i in range(8)],
    })


# --8<-- [start:projection]
def project(raw: str) -> str:
    """Return the three fields the model needs to answer the question.

    Everything else is still available -- the model can ask for it by id. What
    it must not do is carry all of it in context for the rest of the run.
    """
    d = json.loads(raw)
    return json.dumps({"id": d["id"], "status": d["status"],
                       "severity": d["severity"]})
# --8<-- [end:projection]


def summarise(messages: list[BaseMessage], keep: int) -> list[BaseMessage]:
    """Stand in for a summarisation model call.

    The replacement is deliberately generous at ~60 tokens: a real summary of a
    long conversation is not free, and pretending otherwise flatters the
    strategy.
    """
    head, tail = messages[:-keep], messages[-keep:]
    if not head:
        return messages
    summary = AIMessage(content=(
        "Summary of earlier turns: the user asked about several open incidents "
        "in eu-west-1; the assistant looked each one up and reported status and "
        "severity. No actions were taken and nothing was escalated."
    ))
    return [summary, *tail]


@dataclass
class Run:
    name: str
    cumulative_input_tokens: int
    final_context_tokens: int
    summarisations: int


def simulate(project_results: bool, summarise_history: bool) -> Run:
    messages: list[BaseMessage] = []
    cumulative = 0
    summarisations = 0

    for turn in range(TURNS):
        messages.append(HumanMessage(content=f"What is the status of incident {turn}?"))

        # Every turn is billed for the WHOLE context, not just the new message.
        cumulative += count_tokens_approximately(messages)

        messages.append(AIMessage(content="", tool_calls=[
            {"name": "get_incident", "args": {"id": turn}, "id": f"c{turn}"}]))

        raw = fat_tool_result(turn)
        content = project(raw) if project_results else raw
        messages.append(ToolMessage(content=content, tool_call_id=f"c{turn}"))

        # ...and billed again when the tool result goes back for the answer.
        cumulative += count_tokens_approximately(messages)
        messages.append(AIMessage(content=f"Incident {turn} is open, sev2."))

        if summarise_history and count_tokens_approximately(messages) > SUMMARISE_AT:
            messages = summarise(messages, KEEP_RECENT)
            summarisations += 1

    return Run("", cumulative, count_tokens_approximately(messages), summarisations)


def main() -> None:
    strategies = [
        ("naive", False, False),
        ("projected", True, False),
        ("summarised", False, True),
        ("both", True, True),
    ]
    runs = []
    for name, proj, summ in strategies:
        r = simulate(proj, summ)
        r.name = name
        runs.append(r)

    base = runs[0].cumulative_input_tokens
    print(f"{TURNS} turns, one tool call each, summarisation at "
          f"{SUMMARISE_AT} tokens\n")
    header = (f"{'strategy':<13}{'billed tokens':>15}{'vs naive':>11}"
              f"{'final ctx':>11}{'summaries':>11}")
    print(header)
    print("-" * len(header))
    for r in runs:
        print(f"{r.name:<13}{r.cumulative_input_tokens:>15,}"
              f"{r.cumulative_input_tokens / base:>10.2f}x"
              f"{r.final_context_tokens:>11,}{r.summarisations:>11}")

    print("\n'Billed tokens' is the sum of context sent to the model across all")
    print("calls -- what you actually pay for, since every turn re-sends the")
    print("whole conversation. Summarisation calls are NOT counted, so the")
    print("summarised rows are flattered slightly.")


if __name__ == "__main__":
    main()
