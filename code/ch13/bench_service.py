"""How many concurrent conversations one process holds, and what one blocking
call does to that.

Chapter 3 measured the event loop in-process. This measures a real service: a
FastAPI application under uvicorn, driven over real HTTP. The provider is mocked
-- deliberately -- so that what is measured is the SERVICE rather than the model.
A real provider's variance would swamp the effect entirely.

METHOD NOTE, and it matters. The server runs in its OWN PROCESS. An earlier
version of this script ran uvicorn and the load driver on one event loop, and
the driver's own work inflated the server's latency -- the clean baseline
degraded at high concurrency for reasons that had nothing to do with the server.
If you write a load test against an async service, put the load somewhere else.

Three scenarios at each concurrency level:

  clean     every await is a real await
  blocking  one request in twenty calls a blocking library
  threaded  the same offender, wrapped in asyncio.to_thread

    python bench_service.py
"""

from __future__ import annotations

import asyncio
import multiprocessing as mp
import time

import httpx

# --8<-- [start:params]
MODEL_LATENCY = 0.10  # what the mocked provider costs
BLOCKING_WORK = 0.05  # what the offending call costs
OFFENDER_RATE = 20  # one request in this many is an offender
CONCURRENCY = [1, 5, 10, 20, 40]
REQUESTS_PER_LEVEL = 400
# --8<-- [end:params]

HOST, PORT = "127.0.0.1", 8811
BASE = f"http://{HOST}:{PORT}/chat"


# --------------------------------------------------------------------------
# The service, in its own process.
# --------------------------------------------------------------------------
def serve() -> None:
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.state.calls = 0

    def blocking_call() -> None:
        """Stands in for requests, psycopg2, a large json.loads, a PDF parse."""
        time.sleep(BLOCKING_WORK)

    @app.get("/chat")
    async def chat(mode: str = "clean") -> dict[str, str]:
        n = app.state.calls
        app.state.calls += 1

        await asyncio.sleep(MODEL_LATENCY)  # the mocked provider

        if mode != "clean" and n % OFFENDER_RATE == 0:
            if mode == "blocking":
                blocking_call()  # stalls the whole loop
            elif mode == "threaded":
                await asyncio.to_thread(blocking_call)  # does not

        return {"reply": "ok"}

    @app.get("/noop")
    async def noop() -> dict[str, str]:
        """Returns immediately. Used to calibrate the load driver itself."""
        return {"ok": "true"}

    @app.get("/reset")
    async def reset() -> dict[str, str]:
        app.state.calls = 0
        return {"ok": "true"}

    uvicorn.run(app, host=HOST, port=PORT, log_level="error")


# --------------------------------------------------------------------------
# The load driver.
# --------------------------------------------------------------------------
async def drive(client: httpx.AsyncClient, mode: str, concurrency: int,
                total: int) -> tuple[list[float], float]:
    sem = asyncio.Semaphore(concurrency)
    latencies: list[float] = []

    async def one() -> None:
        async with sem:
            t = time.perf_counter()
            await client.get(BASE, params={"mode": mode})
            latencies.append(time.perf_counter() - t)

    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for _ in range(total):
            tg.create_task(one())
    return latencies, time.perf_counter() - start


async def drive_noop(client: httpx.AsyncClient, concurrency: int,
                     total: int) -> tuple[list[float], float]:
    sem = asyncio.Semaphore(concurrency)

    async def one() -> None:
        async with sem:
            await client.get(f"http://{HOST}:{PORT}/noop")

    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for _ in range(total):
            tg.create_task(one())
    return [], time.perf_counter() - start


def pct(xs: list[float], p: float) -> float:
    return sorted(xs)[min(int(len(xs) * p), len(xs) - 1)]


async def main() -> None:
    limits = httpx.Limits(max_connections=300, max_keepalive_connections=300)
    async with httpx.AsyncClient(limits=limits, timeout=120.0) as client:
        for _ in range(100):  # wait for the server process to come up
            try:
                await client.get(BASE, params={"mode": "clean"})
                break
            except httpx.ConnectError:
                await asyncio.sleep(0.1)

        await drive(client, "clean", 10, 40)  # warm up

        # Calibrate the driver. Against an endpoint that does nothing, whatever
        # throughput we see is the HARNESS's ceiling, not the service's. Any
        # measurement approaching it is measuring the client, and this script
        # refuses to report those rather than quietly presenting them.
        ceilings: dict[int, float] = {}
        for conc in CONCURRENCY:
            _, elapsed = await drive_noop(client, conc, 400)
            ceilings[conc] = 400 / elapsed

        print(f"mocked provider latency {MODEL_LATENCY * 1000:.0f} ms; "
              f"one request in {OFFENDER_RATE} is an offender costing "
              f"{BLOCKING_WORK * 1000:.0f} ms")
        print(f"{REQUESTS_PER_LEVEL} requests per cell; "
              f"server in a separate process")
        print("driver ceiling (no-op endpoint): "
              + ", ".join(f"c{c}={v:.0f}/s" for c, v in ceilings.items()) + "\n")
        header = f"{'conc':>6}{'mode':>10}{'p50':>9}{'p95':>9}{'throughput':>13}"
        print(header)
        print("-" * len(header))

        for conc in CONCURRENCY:
            for mode in ("clean", "blocking", "threaded"):
                await client.get(f"http://{HOST}:{PORT}/reset")
                lat, elapsed = await drive(client, mode, conc,
                                           REQUESTS_PER_LEVEL)
                thr = REQUESTS_PER_LEVEL / elapsed
                # Flag any cell within 50% of the harness ceiling: at that point
                # the number describes the load driver, not the service.
                flag = "  <- driver-bound" if thr > 0.5 * ceilings[conc] else ""
                print(f"{conc:>6}{mode:>10}"
                      f"{pct(lat, 0.50) * 1000:>8.0f}m"
                      f"{pct(lat, 0.95) * 1000:>8.0f}m"
                      f"{thr:>10.0f}/s{flag}")
            print()


if __name__ == "__main__":
    mp.set_start_method("spawn")
    server = mp.Process(target=serve, daemon=True)
    server.start()
    try:
        asyncio.run(main())
    finally:
        server.terminate()
        server.join(timeout=5)
