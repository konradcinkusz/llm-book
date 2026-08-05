"""Sequential vs gather vs TaskGroup vs capped fan-out, over real sockets.

The claim this measures is the one Chapter 3 rests on: an I/O-bound workload
interleaves almost perfectly under asyncio, and the ceiling on how much it
interleaves is whatever cap you impose rather than the number of cores.

Deliberately NOT measured with asyncio.sleep on the client side. Sleeping proves
the scheduler can schedule; it proves nothing about sockets, and it would make
the result look better than it is. This starts a real HTTP server on localhost,
with a fixed server-side delay, and drives it over real connections.

    python bench_concurrency.py

Reports medians over repeated trials. Absolute numbers depend on the machine;
the ratios do not.
"""

from __future__ import annotations

import asyncio
import statistics
import time
from collections.abc import Awaitable, Callable

import httpx

# --8<-- [start:params]
N_REQUESTS = 20  # calls per trial
TRIALS = 10  # trials per strategy; report the median
SERVER_DELAY = 0.10  # seconds the server waits before replying
CAP = 5  # concurrency limit for the capped strategy
# --8<-- [end:params]

HOST, PORT = "127.0.0.1", 8765
URL = f"http://{HOST}:{PORT}/delay"


# --------------------------------------------------------------------------
# A minimal HTTP/1.1 server, hand-rolled rather than pulled from a framework so
# that what is being measured is unambiguous: read a request, wait, reply.
# --------------------------------------------------------------------------
async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    body = b"ok"
    response = (
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
        b"Content-Length: %d\r\nConnection: keep-alive\r\n\r\n%s" % (len(body), body)
    )
    try:
        while True:
            await reader.readuntil(b"\r\n\r\n")
            await asyncio.sleep(SERVER_DELAY)
            writer.write(response)
            await writer.drain()
    except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
        pass
    finally:
        writer.close()


# --------------------------------------------------------------------------
# Strategies. Each issues N_REQUESTS calls through one shared client.
# --------------------------------------------------------------------------
# --8<-- [start:strategies]
async def sequential(client: httpx.AsyncClient) -> None:
    """The shape almost everyone writes first. `await` in a loop is a queue."""
    for _ in range(N_REQUESTS):
        await client.get(URL)


async def with_gather(client: httpx.AsyncClient) -> None:
    await asyncio.gather(*(client.get(URL) for _ in range(N_REQUESTS)))


async def with_taskgroup(client: httpx.AsyncClient) -> None:
    async with asyncio.TaskGroup() as tg:
        for _ in range(N_REQUESTS):
            tg.create_task(client.get(URL))


async def capped(client: httpx.AsyncClient) -> None:
    """What you actually ship: unbounded fan-out at a provider earns 429s."""
    sem = asyncio.Semaphore(CAP)

    async def one() -> None:
        async with sem:
            await client.get(URL)

    async with asyncio.TaskGroup() as tg:
        for _ in range(N_REQUESTS):
            tg.create_task(one())
# --8<-- [end:strategies]


async def time_strategy(
    strategy: Callable[[httpx.AsyncClient], Awaitable[None]],
) -> float:
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=100)
    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
        await client.get(URL)  # warm the pool; not counted
        start = time.perf_counter()
        await strategy(client)
        return time.perf_counter() - start


async def main() -> None:
    server = await asyncio.start_server(handle, HOST, PORT)
    async with server:
        strategies: list[tuple[str, Callable[[httpx.AsyncClient], Awaitable[None]]]] = [
            ("sequential", sequential),
            ("gather", with_gather),
            ("TaskGroup", with_taskgroup),
            (f"capped at {CAP}", capped),
        ]
        results: dict[str, list[float]] = {}
        for name, fn in strategies:
            await time_strategy(fn)  # discard one warm-up trial
            results[name] = [await time_strategy(fn) for _ in range(TRIALS)]

    floor = SERVER_DELAY
    print(
        f"{N_REQUESTS} requests, server delay {SERVER_DELAY * 1000:.0f} ms, "
        f"median of {TRIALS} trials\n"
    )
    print(f"{'strategy':<16}{'median':>10}{'min':>10}{'max':>10}{'round trips':>13}")
    print("-" * 59)
    for name, xs in results.items():
        med = statistics.median(xs)
        print(
            f"{name:<16}{med:>9.3f}s{min(xs):>9.3f}s{max(xs):>9.3f}s"
            f"{med / floor:>12.1f}x"
        )
    print(
        f"\none round trip = {floor:.3f}s   "
        f"sequential lower bound = {N_REQUESTS * floor:.3f}s   "
        f"capped lower bound = {-(-N_REQUESTS // CAP) * floor:.3f}s"
    )


if __name__ == "__main__":
    asyncio.run(main())
